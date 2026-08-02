"""Single-worker runtime locks and boot-scoped final-challenge state.

The challenge registry supplies anti-replay and explicit-confirmation evidence
for the trusted local MVP. It is not authentication, an identity proof, a
session, or a credential. Project-local owner configuration remains the sole
authoritative owner identity source.
"""

from __future__ import annotations

import base64
import copy
import fcntl
import hashlib
import os
import re
import secrets
import stat
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

from backend.story_knowledge.apply_contract import (
    ApplyContractError,
    canonical_json_bytes,
    canonical_sha256,
    require_closed_object,
    require_integer,
    require_string,
    validate_owner_identity,
    validate_safe_id,
    validate_sha256,
    validate_uuid_v4,
)


CHALLENGE_LIFETIME_SECONDS = 120.0
CHALLENGE_TOMBSTONE_SECONDS = 600.0
CHALLENGE_REGISTRY_CAPACITY = 1_024
CHALLENGE_RESPONSE_ALGORITHM = "sha256-canonical-final-confirmation-v1"
CHALLENGE_SECURITY_CLASSIFICATION = {
    "purpose": "anti-replay_explicit_confirmation_evidence",
    "authentication": False,
    "identity_proof": False,
    "session": False,
    "credential": False,
}

_BOOT_ID_RE = re.compile(r"^[a-f0-9]{16}$")
_CHALLENGE_ID_RE = re.compile(r"^challenge_([a-f0-9]{16})_([a-f0-9]{64})$")
_LOCK_NAME_RE = re.compile(r"^approved-store-[a-f0-9]{64}\.lock$")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _rfc3339(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ApplyContractError("FINAL_CHALLENGE_CLOCK_INVALID")
    normalized = value.astimezone(timezone.utc)
    rendered = normalized.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return rendered.replace(".000000Z", "Z")


def _has_symlink_component(path: Path) -> bool:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current = current / component
        try:
            if stat.S_ISLNK(os.lstat(current).st_mode):
                return True
        except FileNotFoundError:
            return False
    return False


def _require_owned_directory(path: Path, *, exact_mode: int | None, code: str) -> os.stat_result:
    try:
        metadata = os.lstat(path)
    except OSError as exc:
        raise ApplyContractError(code) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ApplyContractError(code)
    if metadata.st_uid != os.geteuid():
        raise ApplyContractError(code)
    mode = stat.S_IMODE(metadata.st_mode)
    if mode & 0o077 or (exact_mode is not None and mode != exact_mode):
        raise ApplyContractError(code)
    return metadata


def _require_plain_directory(path: Path, *, code: str) -> os.stat_result:
    try:
        metadata = os.lstat(path)
    except OSError as exc:
        raise ApplyContractError(code) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ApplyContractError(code)
    return metadata


def _require_owned_empty_lock_fd(descriptor: int, *, code: str) -> os.stat_result:
    metadata = os.fstat(descriptor)
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_uid != os.geteuid()
        or metadata.st_nlink != 1
        or stat.S_IMODE(metadata.st_mode) != 0o600
        or metadata.st_size != 0
    ):
        raise ApplyContractError(code)
    return metadata


@dataclass
class _ProjectResource:
    project_root: Path
    lock_path: Path
    descriptor: int
    device: int
    inode: int
    guard: threading.Lock
    readers: int = 0
    writer: bool = False


class ApplyPromotionRuntimeManager:
    """Process lease plus retained per-project nonblocking lock resources."""

    def __init__(
        self,
        *,
        runtime_dir: str | Path,
        projects_dir: str | Path,
        worker_count: int = 1,
    ) -> None:
        self.runtime_dir = Path(runtime_dir)
        self.projects_dir = Path(projects_dir)
        self.worker_count = worker_count
        self._runtime_root: Path | None = None
        self._projects_root: Path | None = None
        self._locks_dir: Path | None = None
        self._lease_fd: int | None = None
        self._lease_device: int | None = None
        self._lease_inode: int | None = None
        self._resources: dict[Path, _ProjectResource] = {}
        self._manager_guard = threading.Lock()
        self._started = False

    @classmethod
    def from_environment(
        cls,
        *,
        projects_dir: str | Path,
        environ: Mapping[str, str] | None = None,
    ) -> "ApplyPromotionRuntimeManager":
        values = os.environ if environ is None else environ
        runtime_value = values.get("WRITING_ASSISTANT_RUNTIME_DIR")
        if not runtime_value:
            raise ApplyContractError("RUNTIME_DIRECTORY_REQUIRED")
        worker_count = 1
        for name in ("WRITING_ASSISTANT_WORKER_COUNT", "WEB_CONCURRENCY", "UVICORN_WORKERS"):
            value = values.get(name)
            if value is None:
                continue
            try:
                configured = int(value)
            except ValueError as exc:
                raise ApplyContractError("UNSUPPORTED_MULTI_WORKER_DEPLOYMENT") from exc
            if configured != 1:
                raise ApplyContractError("UNSUPPORTED_MULTI_WORKER_DEPLOYMENT")
        return cls(runtime_dir=runtime_value, projects_dir=projects_dir, worker_count=worker_count)

    def start(self) -> "ApplyPromotionRuntimeManager":
        if self._started:
            return self
        if isinstance(self.worker_count, bool) or self.worker_count != 1:
            raise ApplyContractError("UNSUPPORTED_MULTI_WORKER_DEPLOYMENT")
        if not self.runtime_dir.is_absolute():
            raise ApplyContractError("RUNTIME_DIRECTORY_REQUIRED")
        try:
            runtime_root = self.runtime_dir.resolve(strict=True)
            projects_root = self.projects_dir.resolve(strict=True)
        except OSError as exc:
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE") from exc
        if _has_symlink_component(self.runtime_dir):
            raise ApplyContractError("RUNTIME_DIRECTORY_UNSAFE")
        _require_owned_directory(runtime_root, exact_mode=None, code="RUNTIME_DIRECTORY_UNSAFE")
        if _has_symlink_component(self.projects_dir):
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")
        _require_plain_directory(projects_root, code="RUNTIME_LOCK_UNAVAILABLE")
        try:
            runtime_root.relative_to(projects_root)
        except ValueError:
            pass
        else:
            raise ApplyContractError("RUNTIME_DIRECTORY_UNSAFE")
        try:
            projects_root.relative_to(runtime_root)
        except ValueError:
            pass
        else:
            raise ApplyContractError("RUNTIME_DIRECTORY_UNSAFE")

        try:
            root_fd = os.open(
                runtime_root,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            )
        except OSError as exc:
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE") from exc
        try:
            locks_name = "approved-store-locks"
            locks_path = runtime_root / locks_name
            try:
                os.mkdir(locks_name, 0o700, dir_fd=root_fd)
            except FileExistsError:
                pass
            _require_owned_directory(locks_path, exact_mode=0o700, code="RUNTIME_DIRECTORY_UNSAFE")
            lease_fd = self._open_lock_file(root_fd, "backend-single-worker.lock", conflict_code="RUNTIME_DIRECTORY_UNSAFE")
            try:
                fcntl.flock(lease_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                os.close(lease_fd)
                raise ApplyContractError("UNSUPPORTED_MULTI_WORKER_DEPLOYMENT") from exc
            except OSError as exc:
                os.close(lease_fd)
                raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE") from exc
        finally:
            os.close(root_fd)

        self._runtime_root = runtime_root
        self._projects_root = projects_root
        self._locks_dir = locks_path
        self._lease_fd = lease_fd
        lease_metadata = os.fstat(lease_fd)
        self._lease_device = lease_metadata.st_dev
        self._lease_inode = lease_metadata.st_ino
        self._started = True
        try:
            for entry in sorted(projects_root.iterdir(), key=lambda item: os.fsencode(item.name)):
                if entry.is_symlink() or not entry.is_dir():
                    continue
                try:
                    validate_safe_id(entry.name, "project_id")
                except ApplyContractError:
                    continue
                self.register_project(entry)
        except Exception:
            self.close()
            raise
        return self

    @staticmethod
    def _open_lock_file(directory_fd: int, name: str, *, conflict_code: str) -> int:
        flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(name, flags, 0o600, dir_fd=directory_fd)
            _require_owned_empty_lock_fd(descriptor, code=conflict_code)
            return descriptor
        except ApplyContractError:
            if "descriptor" in locals():
                os.close(descriptor)
            raise
        except OSError as exc:
            if "descriptor" in locals():
                os.close(descriptor)
            raise ApplyContractError(conflict_code) from exc

    def _canonical_project_root(self, project_root: str | Path) -> Path:
        if not self._started or self._projects_root is None:
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")
        supplied = Path(project_root)
        if supplied.is_symlink() or _has_symlink_component(supplied):
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")
        try:
            canonical = supplied.resolve(strict=True)
        except OSError as exc:
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE") from exc
        if not canonical.is_dir() or canonical.parent != self._projects_root:
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")
        validate_safe_id(canonical.name, "project_id")
        return canonical

    def register_project(self, project_root: str | Path) -> Path:
        """Register a completed project mutation; GET paths never call this."""

        canonical = self._canonical_project_root(project_root)
        with self._manager_guard:
            existing = self._resources.get(canonical)
            if existing is not None:
                self._validate_resource(existing)
                return existing.lock_path
            if self._locks_dir is None:
                raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")
            _require_owned_directory(self._locks_dir, exact_mode=0o700, code="RUNTIME_LOCK_UNAVAILABLE")
            key = hashlib.sha256(str(canonical).encode("utf-8", errors="strict")).hexdigest()
            name = f"approved-store-{key}.lock"
            if not _LOCK_NAME_RE.fullmatch(name):
                raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")
            try:
                directory_fd = os.open(
                    self._locks_dir,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                )
            except OSError as exc:
                raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE") from exc
            try:
                descriptor = self._open_lock_file(
                    directory_fd, name, conflict_code="RUNTIME_LOCK_UNAVAILABLE"
                )
            finally:
                os.close(directory_fd)
            metadata = os.fstat(descriptor)
            resource = _ProjectResource(
                project_root=canonical,
                lock_path=self._locks_dir / name,
                descriptor=descriptor,
                device=metadata.st_dev,
                inode=metadata.st_ino,
                guard=threading.Lock(),
            )
            self._resources[canonical] = resource
            return resource.lock_path

    def _existing_resource(self, project_root: str | Path) -> _ProjectResource:
        canonical = self._canonical_project_root(project_root)
        with self._manager_guard:
            resource = self._resources.get(canonical)
        if resource is None:
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")
        self._validate_resource(resource)
        return resource

    def _validate_resource(self, resource: _ProjectResource) -> None:
        if self._runtime_root is None or self._locks_dir is None or self._lease_fd is None:
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")
        try:
            _require_owned_directory(self._runtime_root, exact_mode=None, code="RUNTIME_LOCK_UNAVAILABLE")
            _require_owned_directory(self._locks_dir, exact_mode=0o700, code="RUNTIME_LOCK_UNAVAILABLE")
            lease_path_metadata = os.lstat(self._runtime_root / "backend-single-worker.lock")
            lease_fd_metadata = _require_owned_empty_lock_fd(
                self._lease_fd, code="RUNTIME_LOCK_UNAVAILABLE"
            )
            path_metadata = os.lstat(resource.lock_path)
            fd_metadata = _require_owned_empty_lock_fd(resource.descriptor, code="RUNTIME_LOCK_UNAVAILABLE")
        except OSError as exc:
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE") from exc
        if (
            stat.S_ISLNK(lease_path_metadata.st_mode)
            or not stat.S_ISREG(lease_path_metadata.st_mode)
            or lease_path_metadata.st_uid != os.geteuid()
            or lease_path_metadata.st_nlink != 1
            or stat.S_IMODE(lease_path_metadata.st_mode) != 0o600
            or lease_path_metadata.st_size != 0
            or (lease_path_metadata.st_dev, lease_path_metadata.st_ino)
            != (self._lease_device, self._lease_inode)
            or (lease_fd_metadata.st_dev, lease_fd_metadata.st_ino)
            != (self._lease_device, self._lease_inode)
            or
            stat.S_ISLNK(path_metadata.st_mode)
            or not stat.S_ISREG(path_metadata.st_mode)
            or path_metadata.st_uid != os.geteuid()
            or path_metadata.st_nlink != 1
            or stat.S_IMODE(path_metadata.st_mode) != 0o600
            or path_metadata.st_size != 0
            or (path_metadata.st_dev, path_metadata.st_ino) != (resource.device, resource.inode)
            or (fd_metadata.st_dev, fd_metadata.st_ino) != (resource.device, resource.inode)
        ):
            raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")

    @contextmanager
    def shared(self, project_root: str | Path) -> Iterator[None]:
        """Acquire an existing read resource without registering or writing."""

        resource = self._existing_resource(project_root)
        with resource.guard:
            if resource.writer:
                raise ApplyContractError("APPROVED_STORE_APPLY_LOCKED")
            if resource.readers == 0:
                try:
                    fcntl.flock(resource.descriptor, fcntl.LOCK_SH | fcntl.LOCK_NB)
                except BlockingIOError as exc:
                    raise ApplyContractError("APPROVED_STORE_APPLY_LOCKED") from exc
                except OSError as exc:
                    raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE") from exc
            resource.readers += 1
        try:
            yield
        finally:
            with resource.guard:
                resource.readers -= 1
                if resource.readers == 0:
                    fcntl.flock(resource.descriptor, fcntl.LOCK_UN)

    @contextmanager
    def exclusive(self, project_root: str | Path) -> Iterator[None]:
        resource = self._existing_resource(project_root)
        with resource.guard:
            if resource.writer or resource.readers:
                raise ApplyContractError("APPROVED_STORE_APPLY_LOCKED")
            try:
                fcntl.flock(resource.descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ApplyContractError("APPROVED_STORE_APPLY_LOCKED") from exc
            except OSError as exc:
                raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE") from exc
            resource.writer = True
        try:
            yield
        finally:
            with resource.guard:
                resource.writer = False
                fcntl.flock(resource.descriptor, fcntl.LOCK_UN)

    def close(self) -> None:
        with self._manager_guard:
            resources = tuple(self._resources.values())
            self._resources.clear()
            lease_fd = self._lease_fd
            self._lease_fd = None
            self._lease_device = None
            self._lease_inode = None
            self._started = False
        for resource in resources:
            try:
                fcntl.flock(resource.descriptor, fcntl.LOCK_UN)
            finally:
                os.close(resource.descriptor)
        if lease_fd is not None:
            try:
                fcntl.flock(lease_fd, fcntl.LOCK_UN)
            finally:
                os.close(lease_fd)


def final_challenge_idempotency_scope(
    *,
    project_id: str,
    promotion_id: str,
    revision: int,
    sealed_contract_hash: str,
    before_state_snapshot_token: str,
    authoritative_owner_actor: dict[str, Any],
) -> dict[str, Any]:
    validate_safe_id(project_id, "project_id")
    validate_safe_id(promotion_id, "promotion_id")
    require_integer(revision, label="revision", minimum=1, maximum=256)
    validate_sha256(sealed_contract_hash, "sealed_contract_hash")
    validate_sha256(before_state_snapshot_token, "before_state_snapshot_token")
    validate_owner_identity(authoritative_owner_actor)
    return {
        "operation_kind": "final_challenge",
        "project_id": project_id,
        "promotion_id": promotion_id,
        "revision": revision,
        "sealed_contract_hash": sealed_contract_hash,
        "before_state_snapshot_token": before_state_snapshot_token,
        "authoritative_owner_actor": authoritative_owner_actor,
    }


@dataclass
class _ChallengeEntry:
    challenge_id: str
    nonce_bytes: bytes
    nonce: str
    challenge_scope: dict[str, Any]
    idempotency_key: str
    idempotency_scope_hash: str
    seal_identity: tuple[str, str, int, str]
    deadline: float
    status: str = "outstanding"
    terminal_at: float | None = None


class FinalChallengeRegistry:
    """Bounded process-local challenge state; intentionally lost on restart."""

    def __init__(
        self,
        *,
        capacity: int = CHALLENGE_REGISTRY_CAPACITY,
        boot_id: str | None = None,
        monotonic_clock: Callable[[], float] = time.monotonic,
        wall_clock: Callable[[], datetime] = _utc_now,
        random_bytes: Callable[[int], bytes] = secrets.token_bytes,
    ) -> None:
        if isinstance(capacity, bool) or not 1 <= capacity <= CHALLENGE_REGISTRY_CAPACITY:
            raise ValueError("challenge registry capacity out of range")
        generated_boot = random_bytes(8).hex() if boot_id is None else boot_id
        if not _BOOT_ID_RE.fullmatch(generated_boot):
            raise ValueError("invalid challenge boot ID")
        self.capacity = capacity
        self.boot_id = generated_boot
        self._monotonic = monotonic_clock
        self._wall = wall_clock
        self._random_bytes = random_bytes
        self._entries: dict[str, _ChallengeEntry] = {}
        self._keys: dict[tuple[str, str, str], str] = {}
        self._outstanding_by_seal: dict[tuple[str, str, int, str], str] = {}
        self._guard = threading.Lock()

    def _expire_and_purge(self, now: float) -> None:
        for entry in self._entries.values():
            if entry.status == "outstanding" and now >= entry.deadline:
                entry.status = "expired"
                entry.terminal_at = entry.deadline
                self._outstanding_by_seal.pop(entry.seal_identity, None)
        purge_ids = [
            entry.challenge_id
            for entry in self._entries.values()
            if entry.terminal_at is not None
            and now - entry.terminal_at >= CHALLENGE_TOMBSTONE_SECONDS
        ]
        for challenge_id in purge_ids:
            entry = self._entries.pop(challenge_id)
            key = (
                entry.challenge_scope["project_id"],
                entry.challenge_scope["promotion_id"],
                entry.idempotency_key,
            )
            if self._keys.get(key) == challenge_id:
                self._keys.pop(key, None)

    @staticmethod
    def _response(entry: _ChallengeEntry, *, replayed: bool) -> dict[str, Any]:
        return {
            "challenge_id": entry.challenge_id,
            "challenge_nonce": entry.nonce,
            "response_algorithm": CHALLENGE_RESPONSE_ALGORITHM,
            "challenge_scope": copy.deepcopy(entry.challenge_scope),
            "replayed": replayed,
        }

    def issue(
        self,
        *,
        project_id: str,
        promotion_id: str,
        revision: int,
        sealed_contract_hash: str,
        before_state_snapshot_token: str,
        operation: str,
        destination_path: str,
        authoritative_owner_actor: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        validate_uuid_v4(idempotency_key)
        if operation not in {"create", "update"}:
            raise ApplyContractError("APPLY_OPERATION_INVALID")
        require_string(destination_path, label="destination_path", minimum=1, maximum=320)
        idempotency_scope = final_challenge_idempotency_scope(
            project_id=project_id,
            promotion_id=promotion_id,
            revision=revision,
            sealed_contract_hash=sealed_contract_hash,
            before_state_snapshot_token=before_state_snapshot_token,
            authoritative_owner_actor=authoritative_owner_actor,
        )
        scope_hash = canonical_sha256(idempotency_scope)
        now = self._monotonic()
        wall_now = self._wall()
        key_identity = (project_id, promotion_id, idempotency_key)
        seal_identity = (project_id, promotion_id, revision, sealed_contract_hash)
        with self._guard:
            self._expire_and_purge(now)
            existing_id = self._keys.get(key_identity)
            if existing_id is not None:
                existing = self._entries[existing_id]
                if existing.idempotency_scope_hash != scope_hash:
                    raise ApplyContractError("IDEMPOTENCY_PAYLOAD_CONFLICT")
                self._raise_for_status(existing, now)
                return self._response(existing, replayed=True)
            if len(self._entries) >= self.capacity:
                raise ApplyContractError("CHALLENGE_REGISTRY_CAPACITY")
            random_id = self._random_bytes(32)
            nonce_bytes = self._random_bytes(32)
            if len(random_id) != 32 or len(nonce_bytes) != 32:
                raise ApplyContractError("CHALLENGE_RANDOMNESS_UNAVAILABLE")
            challenge_id = f"challenge_{self.boot_id}_{random_id.hex()}"
            nonce = base64.urlsafe_b64encode(nonce_bytes).decode("ascii").rstrip("=")
            issued_at = _rfc3339(wall_now)
            expires_at = _rfc3339(wall_now + timedelta(seconds=CHALLENGE_LIFETIME_SECONDS))
            challenge_scope = {
                "protocol": "apply-promotion-final-challenge.v1",
                "project_id": project_id,
                "promotion_id": promotion_id,
                "revision": revision,
                "sealed_contract_hash": sealed_contract_hash,
                "before_state_snapshot_token": before_state_snapshot_token,
                "operation": operation,
                "destination_path": destination_path,
                "authoritative_owner_actor": copy.deepcopy(authoritative_owner_actor),
                "challenge_id": challenge_id,
                "issued_at": issued_at,
                "expires_at": expires_at,
            }
            prior_id = self._outstanding_by_seal.get(seal_identity)
            entry = _ChallengeEntry(
                challenge_id=challenge_id,
                nonce_bytes=nonce_bytes,
                nonce=nonce,
                challenge_scope=challenge_scope,
                idempotency_key=idempotency_key,
                idempotency_scope_hash=scope_hash,
                seal_identity=seal_identity,
                deadline=now + CHALLENGE_LIFETIME_SECONDS,
            )
            if prior_id is not None:
                prior = self._entries[prior_id]
                prior.status = "replaced"
                prior.terminal_at = now
            self._entries[challenge_id] = entry
            self._keys[key_identity] = challenge_id
            self._outstanding_by_seal[seal_identity] = challenge_id
            return self._response(entry, replayed=False)

    def _entry(self, challenge_id: str, now: float) -> _ChallengeEntry:
        match = _CHALLENGE_ID_RE.fullmatch(challenge_id) if isinstance(challenge_id, str) else None
        if match is None:
            raise ApplyContractError("FINAL_CHALLENGE_UNKNOWN")
        if match.group(1) != self.boot_id:
            raise ApplyContractError("FINAL_CHALLENGE_REQUIRED_AFTER_RESTART")
        entry = self._entries.get(challenge_id)
        if entry is None:
            raise ApplyContractError("FINAL_CHALLENGE_UNKNOWN")
        self._raise_for_status(entry, now)
        return entry

    def _raise_for_status(self, entry: _ChallengeEntry, now: float) -> None:
        if entry.status == "outstanding" and now >= entry.deadline:
            entry.status = "expired"
            entry.terminal_at = entry.deadline
            self._outstanding_by_seal.pop(entry.seal_identity, None)
        codes = {
            "expired": "FINAL_CHALLENGE_EXPIRED",
            "replaced": "FINAL_CHALLENGE_REPLACED",
            "consumption_pending": "FINAL_CHALLENGE_CONSUMED",
            "consumed": "FINAL_CHALLENGE_CONSUMED",
            "invalidated": "FINAL_CHALLENGE_CONSUMED",
        }
        if entry.status != "outstanding":
            raise ApplyContractError(codes[entry.status])

    @staticmethod
    def expected_response(challenge_nonce: str, challenge_scope: dict[str, Any]) -> str:
        try:
            nonce_bytes = base64.b64decode(
                challenge_nonce + "=" * (-len(challenge_nonce) % 4),
                altchars=b"-_",
                validate=True,
            )
        except (ValueError, TypeError) as exc:
            raise ApplyContractError("FINAL_CHALLENGE_RESPONSE_INVALID") from exc
        confirmation = {
            "challenge_scope": challenge_scope,
            "final_confirmation": {
                "confirmed": True,
                "method": "explicit_final_apply_confirmation",
            },
        }
        preimage = (
            b"apply-promotion-final-confirmation-v1\x00"
            + nonce_bytes
            + b"\x00"
            + canonical_json_bytes(confirmation)
        )
        return hashlib.sha256(preimage).hexdigest()

    def begin_consumption(
        self,
        *,
        challenge_id: str,
        challenge_response: str,
        expected_challenge_scope: dict[str, Any],
    ) -> dict[str, Any]:
        validate_sha256(challenge_response, "challenge_response")
        now = self._monotonic()
        with self._guard:
            self._expire_and_purge(now)
            entry = self._entry(challenge_id, now)
            if entry.challenge_scope != expected_challenge_scope:
                raise ApplyContractError("FINAL_CHALLENGE_SCOPE_MISMATCH")
            expected = self.expected_response(entry.nonce, entry.challenge_scope)
            if not secrets.compare_digest(challenge_response, expected):
                raise ApplyContractError("FINAL_CHALLENGE_RESPONSE_INVALID")
            entry.status = "consumption_pending"
            self._outstanding_by_seal.pop(entry.seal_identity, None)
            return copy.deepcopy(entry.challenge_scope)

    def outstanding_scope(self, challenge_id: str) -> dict[str, Any]:
        """Return the exact outstanding server scope without changing state."""

        now = self._monotonic()
        with self._guard:
            self._expire_and_purge(now)
            entry = self._entry(challenge_id, now)
            return copy.deepcopy(entry.challenge_scope)

    def complete_consumption(self, challenge_id: str) -> None:
        now = self._monotonic()
        with self._guard:
            entry = self._entries.get(challenge_id)
            if entry is None or entry.status != "consumption_pending":
                raise ApplyContractError("FINAL_CHALLENGE_CONSUMED")
            entry.status = "consumed"
            entry.terminal_at = now

    def invalidate_before_intent(self, challenge_id: str) -> None:
        now = self._monotonic()
        with self._guard:
            entry = self._entries.get(challenge_id)
            if entry is None or entry.status not in {"outstanding", "consumption_pending"}:
                raise ApplyContractError("FINAL_CHALLENGE_CONSUMED")
            entry.status = "invalidated"
            entry.terminal_at = now
            self._outstanding_by_seal.pop(entry.seal_identity, None)

    def status(self, challenge_id: str) -> str:
        now = self._monotonic()
        with self._guard:
            self._expire_and_purge(now)
            match = _CHALLENGE_ID_RE.fullmatch(challenge_id) if isinstance(challenge_id, str) else None
            if match is None:
                return "unknown"
            if match.group(1) != self.boot_id:
                return "prior_boot"
            entry = self._entries.get(challenge_id)
            return "unknown" if entry is None else entry.status

    def __len__(self) -> int:
        with self._guard:
            self._expire_and_purge(self._monotonic())
            return len(self._entries)


__all__ = (
    "ApplyPromotionRuntimeManager",
    "CHALLENGE_LIFETIME_SECONDS",
    "CHALLENGE_REGISTRY_CAPACITY",
    "CHALLENGE_RESPONSE_ALGORITHM",
    "CHALLENGE_SECURITY_CLASSIFICATION",
    "CHALLENGE_TOMBSTONE_SECONDS",
    "FinalChallengeRegistry",
    "final_challenge_idempotency_scope",
)

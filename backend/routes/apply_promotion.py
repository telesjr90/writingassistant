"""Apply-promotion contract lifecycle and final-apply route surface."""

from __future__ import annotations

from typing import Any

import os
import stat
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from backend import project_manager
from backend.story_knowledge import apply_promotion
from backend.story_knowledge.apply_contract import (
    ApplyContractError,
    MAX_REQUEST_BYTES,
    preparation_id,
    strict_json_loads,
    validate_safe_id,
)


router = APIRouter(prefix="/api/projects/{project_id}/apply-promotion")
lifecycle_router = APIRouter(
    prefix="/api/projects/{project_id}/omi/promotions/{promotion_id}"
)


def _error_status(code: str) -> int:
    if code in {
        "PROJECT_NOT_FOUND",
        "PROMOTION_NOT_FOUND",
        "CANDIDATE_NOT_FOUND",
        "APPLY_CONTRACT_REVISION_NOT_FOUND",
    }:
        return 404
    if (
        code.startswith("SCHEMA_")
        or code.startswith("JSON_")
        or code in {
            "REQUEST_TOO_LARGE",
            "INVALID_SAFE_ID",
            "INVALID_SHA256",
            "INVALID_UUID_V4",
            "UNKNOWN_QUERY_PARAMETER",
            "APPLY_OPERATION_INVALID",
            "APPROVED_DESTINATION_TYPE_INVALID",
            "APPROVED_MEMORY_INDEX_ORDINARY_WRITE_FORBIDDEN",
        }
    ):
        return 422
    if code in {
        "RUNTIME_LOCK_UNAVAILABLE",
        "APPROVED_STORE_APPLY_LOCKED",
        "UNSUPPORTED_MULTI_WORKER_DEPLOYMENT",
    }:
        return 503
    return 409


def _raise_contract_error(exc: ApplyContractError) -> None:
    raise HTTPException(
        status_code=_error_status(exc.code),
        detail={"code": exc.code, "message": str(exc)},
    ) from exc


async def _strict_body(request: Request) -> Any:
    try:
        return strict_json_loads(await request.body(), max_bytes=MAX_REQUEST_BYTES)
    except ApplyContractError as exc:
        _raise_contract_error(exc)


def _project_context(project_id: str, promotion_id: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    try:
        validate_safe_id(project_id, "project_id")
        validate_safe_id(promotion_id, "promotion_id")
        project_dir = _project_root(project_id)
        promotion = _read_authority_object(
            project_dir,
            Path("omi", "promotions", f"{promotion_id}.json"),
            missing_code="PROMOTION_NOT_FOUND",
        )
        candidate_id = promotion.get("candidate_id")
        validate_safe_id(candidate_id, "candidate_id")
        candidate = _read_authority_object(
            project_dir,
            Path("omi", "candidates", f"{candidate_id}.json"),
            missing_code="CANDIDATE_NOT_FOUND",
        )
        return project_dir, promotion, candidate
    except FileNotFoundError as exc:
        code = "PROJECT_NOT_FOUND" if not (Path(project_manager.PROJECTS_DIR) / project_id).exists() else "PROMOTION_NOT_FOUND"
        raise ApplyContractError(code) from exc
    except ValueError as exc:
        raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID") from exc


def _project_root(project_id: str) -> Path:
    validate_safe_id(project_id, "project_id")
    try:
        projects_root = Path(project_manager.PROJECTS_DIR).resolve(strict=True)
        project_dir = projects_root / project_id
        metadata = os.lstat(project_dir)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ApplyContractError("PROJECT_NOT_FOUND")
        if project_dir.resolve(strict=True).parent != projects_root:
            raise ApplyContractError("PROJECT_NOT_FOUND")
        return project_dir
    except FileNotFoundError as exc:
        raise ApplyContractError("PROJECT_NOT_FOUND") from exc


def _read_authority_object(
    project_dir: Path, relative: Path, *, missing_code: str
) -> dict[str, Any]:
    current = project_dir
    for part in relative.parts[:-1]:
        current = current / part
        try:
            metadata = os.lstat(current)
        except FileNotFoundError as exc:
            raise ApplyContractError(missing_code) from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ApplyContractError("PROMOTION_AUTHORITY_UNSAFE")
    path = project_dir / relative
    try:
        metadata = os.lstat(path)
    except FileNotFoundError as exc:
        raise ApplyContractError(missing_code) from exc
    if (
        stat.S_ISLNK(metadata.st_mode)
        or not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
        or metadata.st_size > MAX_REQUEST_BYTES
    ):
        raise ApplyContractError("PROMOTION_AUTHORITY_UNSAFE")
    value = strict_json_loads(path.read_bytes(), max_bytes=MAX_REQUEST_BYTES)
    if not isinstance(value, dict):
        raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
    return value


def _runtime(request: Request) -> Any:
    manager = getattr(request.app.state, "apply_promotion_runtime_manager", None)
    if manager is None:
        raise ApplyContractError("RUNTIME_LOCK_UNAVAILABLE")
    return manager


def _registry(request: Request) -> Any:
    registry = getattr(request.app.state, "apply_promotion_challenge_registry", None)
    if registry is None:
        raise ApplyContractError("FINAL_CHALLENGE_REQUIRED_AFTER_RESTART")
    return registry


@lifecycle_router.post("/apply-contract/revisions")
async def post_apply_contract_revision(
    project_id: str, promotion_id: str, request: Request
) -> JSONResponse:
    body = await _strict_body(request)
    try:
        project_dir = _project_root(project_id)
        existing_preparation = False
        if isinstance(body, dict) and isinstance(body.get("idempotency_key"), str):
            try:
                prep_id = preparation_id(project_id, promotion_id, body["idempotency_key"])
                existing_preparation = (
                    project_dir
                    / "writer_assistant"
                    / "apply_contracts"
                    / promotion_id
                    / "preparations"
                    / f"{prep_id}.json"
                ).exists()
            except ApplyContractError:
                pass
        if existing_preparation:
            promotion: dict[str, Any] = {}
            candidate: dict[str, Any] = {}
            owner: dict[str, Any] = {}
        else:
            promotion = {}
            candidate = {}
            owner = {}
        with _runtime(request).exclusive(project_dir):
            if not existing_preparation:
                _, promotion, candidate = _project_context(project_id, promotion_id)
            response, status_code = apply_promotion.prepare_apply_contract(
                project_dir=project_dir,
                project_id=project_id,
                promotion_id=promotion_id,
                promotion=promotion,
                candidate=candidate,
                owner=owner,
                body=body,
            )
        return JSONResponse(status_code=status_code, content=response)
    except ApplyContractError as exc:
        _raise_contract_error(exc)


@lifecycle_router.get("/apply-contract")
def get_apply_contract(
    project_id: str, promotion_id: str, request: Request
) -> dict[str, Any]:
    try:
        unknown = set(request.query_params.keys()) - {"revision"}
        if unknown:
            raise ApplyContractError("UNKNOWN_QUERY_PARAMETER")
        values = request.query_params.getlist("revision")
        if len(values) > 1:
            raise ApplyContractError("UNKNOWN_QUERY_PARAMETER")
        selected = None
        if values:
            try:
                selected = int(values[0])
            except ValueError as exc:
                raise ApplyContractError("SCHEMA_INTEGER_INVALID", "revision") from exc
        project_dir = _project_root(project_id)
        with _runtime(request).shared(project_dir):
            _, promotion, candidate = _project_context(project_id, promotion_id)
            owner = apply_promotion.load_local_owner_identity(project_dir, project_id=project_id)
            return apply_promotion.read_apply_contract(
                project_dir=project_dir,
                project_id=project_id,
                promotion_id=promotion_id,
                promotion=promotion,
                candidate=candidate,
                owner=owner,
                selected_revision=selected,
            )
    except ApplyContractError as exc:
        _raise_contract_error(exc)


@lifecycle_router.post("/apply-contract/revisions/{revision}/approval")
async def post_apply_contract_approval(
    project_id: str, promotion_id: str, revision: int, request: Request
) -> JSONResponse:
    body = await _strict_body(request)
    try:
        project_dir = _project_root(project_id)
        with _runtime(request).exclusive(project_dir):
            _, promotion, candidate = _project_context(project_id, promotion_id)
            response, status_code = apply_promotion.approve_apply_contract(
                project_dir=project_dir,
                project_id=project_id,
                promotion_id=promotion_id,
                promotion=promotion,
                candidate=candidate,
                owner={},
                revision_number=revision,
                body=body,
            )
        return JSONResponse(status_code=status_code, content=response)
    except ApplyContractError as exc:
        _raise_contract_error(exc)


@lifecycle_router.post("/apply-contract/revisions/{revision}/revocation")
async def post_apply_contract_revocation(
    project_id: str, promotion_id: str, revision: int, request: Request
) -> JSONResponse:
    body = await _strict_body(request)
    try:
        project_dir = _project_root(project_id)
        with _runtime(request).exclusive(project_dir):
            _, promotion, candidate = _project_context(project_id, promotion_id)
            response, status_code = apply_promotion.revoke_apply_contract(
                project_dir=project_dir,
                project_id=project_id,
                promotion_id=promotion_id,
                promotion=promotion,
                candidate=candidate,
                owner={},
                revision_number=revision,
                body=body,
            )
        return JSONResponse(status_code=status_code, content=response)
    except ApplyContractError as exc:
        _raise_contract_error(exc)


@lifecycle_router.post("/apply-contract/final-challenge")
async def post_apply_contract_final_challenge(
    project_id: str, promotion_id: str, request: Request
) -> JSONResponse:
    body = await _strict_body(request)
    try:
        project_dir = _project_root(project_id)
        with _runtime(request).exclusive(project_dir):
            _, promotion, candidate = _project_context(project_id, promotion_id)
            owner = apply_promotion.load_local_owner_identity(project_dir, project_id=project_id)
            response, status_code = apply_promotion.issue_final_challenge(
                project_dir=project_dir,
                project_id=project_id,
                promotion_id=promotion_id,
                promotion=promotion,
                candidate=candidate,
                owner=owner,
                body=body,
                registry=_registry(request),
            )
        return JSONResponse(status_code=status_code, content=response)
    except ApplyContractError as exc:
        _raise_contract_error(exc)


@lifecycle_router.get("/apply-audit")
def get_apply_audit(
    project_id: str, promotion_id: str, request: Request
) -> dict[str, Any]:
    try:
        if request.query_params:
            raise ApplyContractError("UNKNOWN_QUERY_PARAMETER")
        project_dir = _project_root(project_id)
        with _runtime(request).shared(project_dir):
            _, promotion, candidate = _project_context(project_id, promotion_id)
            return apply_promotion.read_apply_audit(
                project_dir=project_dir,
                project_id=project_id,
                promotion_id=promotion_id,
                promotion=promotion,
                candidate=candidate,
            )
    except ApplyContractError as exc:
        _raise_contract_error(exc)


@router.post("")
async def post_apply_promotion(
    project_id: str, request: Request
) -> JSONResponse:
    body = await _strict_body(request)
    try:
        if not isinstance(body, dict):
            raise ApplyContractError("SCHEMA_TYPE_MISMATCH", "final apply request")
        promotion_id = body.get("promotion_id")
        validate_safe_id(promotion_id, "promotion_id")
        project_dir = _project_root(project_id)
        with _runtime(request).exclusive(project_dir):
            _, promotion, candidate = _project_context(project_id, promotion_id)
            response = apply_promotion.final_apply_promotion(
                project_dir=project_dir,
                project_id=project_id,
                promotion_id=promotion_id,
                promotion=promotion,
                candidate=candidate,
                body=body,
                registry=_registry(request),
            )
        return JSONResponse(status_code=200, content=response)
    except ApplyContractError as exc:
        _raise_contract_error(exc)

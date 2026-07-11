"""T021A production NCP Node-validation opt-in contract tests.

All child-process behavior is mocked. These tests never execute npm or Node,
install packages, access a network, start a server, or persist OMI candidates.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from backend import omi_analysis_orchestrator as oao


def _payload() -> dict[str, Any]:
    return {
        "schema_version": "1.3.0",
        "story": {
            "narratives": [
                {
                    "subtext": {
                        "storypoints": [
                            {
                                "id": "point-1",
                                "name": "Archive pressure",
                                "summary": "Archive pressure remains unresolved.",
                            }
                        ]
                    }
                }
            ]
        },
    }


def _prepare_fake_repo(
    monkeypatch: Any,
    tmp_path: Path,
    *,
    package_root: bool = True,
    package_json: bool = True,
    validator_script: bool = True,
) -> tuple[Path, Path, Path]:
    repo_root = tmp_path / "repo"
    module_path = repo_root / "backend" / "omi_analysis_orchestrator.py"
    module_path.parent.mkdir(parents=True)
    module_path.write_text("# test anchor\n", encoding="utf-8")
    monkeypatch.setattr(oao, "__file__", str(module_path))

    ncp_root = repo_root / ".external_sources" / "narrative-context-protocol"
    if package_root:
        ncp_root.mkdir(parents=True)
        if package_json:
            (ncp_root / "package.json").write_text("{}\n", encoding="utf-8")
        if validator_script:
            (ncp_root / "tests").mkdir(parents=True)
            (ncp_root / "tests" / "validate-file.js").write_text(
                "// test fixture\n", encoding="utf-8"
            )

    input_path = (
        ncp_root / "examples" / "selected.json"
        if package_root
        else tmp_path / "selected.json"
    )
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_text(json.dumps(_payload()), encoding="utf-8")
    return repo_root, ncp_root, input_path.resolve()


def _mock_success(monkeypatch: Any, input_path: Path) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(oao.shutil, "which", lambda name: "/usr/bin/npm")

    def fake_run(command: Any, **kwargs: Any) -> Any:
        calls.append({"command": command, **kwargs})
        return SimpleNamespace(
            returncode=0,
            stdout=f"PASS {input_path}\n",
            stderr="",
        )

    monkeypatch.setattr(oao.subprocess, "run", fake_run)
    return calls


def _run_live_ncp(monkeypatch: Any, input_path: Path, *, node: bool) -> dict[str, Any]:
    monkeypatch.setenv("OMI_LIVE_TOOLS_ENABLED", "1")
    monkeypatch.setenv("OMI_LIVE_NCP_ENABLED", "1")
    monkeypatch.setenv("OMI_LIVE_NCP_INPUT_PATH", str(input_path))
    if node:
        monkeypatch.setenv("OMI_LIVE_NCP_VALIDATE_WITH_NODE", "1")
    else:
        monkeypatch.delenv("OMI_LIVE_NCP_VALIDATE_WITH_NODE", raising=False)
    return oao.analyze_omi_raw_idea_with_tools(
        "example",
        "Owner-authored analysis note for NCP validation.",
        requested_adapters=["ncp"],
        persist_candidates=False,
    )


def _ncp_result(result: dict[str, Any]) -> dict[str, Any]:
    matches = [item for item in result["adapter_results"] if item["adapter"] == "ncp"]
    assert len(matches) == 1
    return matches[0]


def test_exact_bounded_validate_file_command_contract(
    monkeypatch: Any, tmp_path: Path
) -> None:
    _, ncp_root, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    calls = _mock_success(monkeypatch, input_path)

    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=input_path) is True
    assert len(calls) == 1
    call = calls[0]
    assert call["command"] == [
        "/usr/bin/npm",
        "run",
        "validate:file",
        "--",
        str(input_path),
    ]
    assert call["cwd"] == ncp_root.resolve()
    assert call["shell"] is False
    assert call["stdout"] is subprocess.PIPE
    assert call["stderr"] is subprocess.PIPE
    assert call["text"] is True
    assert call["timeout"] == 60.0
    assert call["stdin"] is subprocess.DEVNULL
    assert call["check"] is False
    forbidden = {"install", "ci", "audit", "audit fix", "start", "server"}
    assert forbidden.isdisjoint({str(value).lower() for value in call["command"]})


@pytest.mark.parametrize(
    ("returncode", "stdout", "expected"),
    [
        (0, "PASS {path}\n", True),
        (0, "validation complete\n", False),
        (0, "PASS /tmp/a-different-file.json\n", False),
        (1, "PASS {path}\n", False),
    ],
)
def test_process_result_requires_zero_exit_and_exact_success_line(
    monkeypatch: Any,
    tmp_path: Path,
    returncode: int,
    stdout: str,
    expected: bool,
) -> None:
    _, _, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    monkeypatch.setattr(oao.shutil, "which", lambda name: "/usr/bin/npm")
    monkeypatch.setattr(
        oao.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=returncode,
            stdout=stdout.format(path=input_path),
            stderr="validator detail",
        ),
    )
    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=input_path) is expected


@pytest.mark.parametrize("failure", ["timeout", "oserror", "valueerror"])
def test_process_start_and_completion_failures_return_false(
    monkeypatch: Any, tmp_path: Path, failure: str
) -> None:
    _, _, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    monkeypatch.setattr(oao.shutil, "which", lambda name: "/usr/bin/npm")

    def fail(*args: Any, **kwargs: Any) -> Any:
        if failure == "timeout":
            raise subprocess.TimeoutExpired(args[0], 60.0, output="large output")
        if failure == "oserror":
            raise OSError("unavailable")
        raise ValueError("malformed invocation")

    monkeypatch.setattr(oao.subprocess, "run", fail)
    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=input_path) is False


def test_missing_npm_returns_false_without_starting_process(
    monkeypatch: Any, tmp_path: Path
) -> None:
    _, _, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    monkeypatch.setattr(oao.shutil, "which", lambda name: None)
    monkeypatch.setattr(
        oao.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("subprocess must not start"),
    )
    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=input_path) is False


@pytest.mark.parametrize(
    ("package_root", "package_json", "validator_script"),
    [(False, False, False), (True, False, True), (True, True, False)],
)
def test_missing_ncp_package_surface_returns_false(
    monkeypatch: Any,
    tmp_path: Path,
    package_root: bool,
    package_json: bool,
    validator_script: bool,
) -> None:
    repo_root, _, input_path = _prepare_fake_repo(
        monkeypatch,
        tmp_path,
        package_root=package_root,
        package_json=package_json,
        validator_script=validator_script,
    )
    if not package_root:
        # Keep the input allowlisted through the temp root while leaving the
        # fixed repo-local NCP source root absent.
        assert not (repo_root / ".external_sources" / "narrative-context-protocol").exists()
    monkeypatch.setattr(oao.shutil, "which", lambda name: "/usr/bin/npm")
    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=input_path) is False


@pytest.mark.parametrize("bad_input", ["not-a-path", Path("relative.json")])
def test_non_path_and_relative_input_are_rejected(
    monkeypatch: Any, tmp_path: Path, bad_input: Any
) -> None:
    _prepare_fake_repo(monkeypatch, tmp_path)
    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=bad_input) is False


def test_nonexistent_file_and_directory_are_rejected(
    monkeypatch: Any, tmp_path: Path
) -> None:
    repo_root, _, _ = _prepare_fake_repo(monkeypatch, tmp_path)
    assert oao._ncp_validate_with_node_opt_in(
        absolute_input_path=(repo_root / "tests" / "missing.json").absolute()
    ) is False
    directory = repo_root / "tests"
    directory.mkdir()
    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=directory.resolve()) is False


def test_symlink_and_nonresolved_path_are_rejected(
    monkeypatch: Any, tmp_path: Path
) -> None:
    _, _, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    link = tmp_path / "selected-link.json"
    try:
        link.symlink_to(input_path)
    except OSError:
        pytest.skip("symlinks unavailable")
    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=link.absolute()) is False
    nonresolved = input_path.parent / ".." / "examples" / input_path.name
    assert nonresolved.is_absolute()
    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=nonresolved) is False


def test_unresolvable_input_returns_false(monkeypatch: Any, tmp_path: Path) -> None:
    _, _, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    real_resolve = Path.resolve

    def fake_resolve(path: Path, *args: Any, **kwargs: Any) -> Path:
        if path == input_path:
            raise OSError("unresolvable")
        return real_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", fake_resolve)
    assert oao._ncp_validate_with_node_opt_in(absolute_input_path=input_path) is False


@pytest.mark.parametrize("forbidden_root", ["projects", "artifacts", ".codex-context"])
def test_forbidden_repo_trees_are_rejected(
    monkeypatch: Any, tmp_path: Path, forbidden_root: str
) -> None:
    repo_root, _, _ = _prepare_fake_repo(monkeypatch, tmp_path)
    input_path = repo_root / forbidden_root / "selected.json"
    input_path.parent.mkdir(parents=True)
    input_path.write_text(json.dumps(_payload()), encoding="utf-8")
    assert oao._ncp_validate_with_node_opt_in(
        absolute_input_path=input_path.resolve()
    ) is False


def test_external_sources_tests_and_temp_allowlist_behavior_is_preserved(
    monkeypatch: Any, tmp_path: Path
) -> None:
    repo_root, _, external_input = _prepare_fake_repo(monkeypatch, tmp_path)
    monkeypatch.setattr(oao.shutil, "which", lambda name: "/usr/bin/npm")

    accepted: list[Path] = []

    def fake_run(command: list[str], **kwargs: Any) -> Any:
        selected = Path(command[-1])
        accepted.append(selected)
        return SimpleNamespace(returncode=0, stdout=f"PASS {selected}\n", stderr="")

    monkeypatch.setattr(oao.subprocess, "run", fake_run)
    tests_input = repo_root / "tests" / "ncp" / "selected.json"
    tests_input.parent.mkdir(parents=True)
    tests_input.write_text(json.dumps(_payload()), encoding="utf-8")
    temp_input = tmp_path / "temp-selected.json"
    temp_input.write_text(json.dumps(_payload()), encoding="utf-8")

    for input_path in (external_input, tests_input.resolve(), temp_input.resolve()):
        assert oao._ncp_validate_with_node_opt_in(absolute_input_path=input_path) is True
    assert accepted == [external_input, tests_input.resolve(), temp_input.resolve()]


def test_helper_failure_keeps_adapter_failed_closed_and_hides_child_output(
    monkeypatch: Any, tmp_path: Path
) -> None:
    _, _, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    monkeypatch.setattr(oao.shutil, "which", lambda name: "/usr/bin/npm")
    monkeypatch.setattr(
        oao.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1,
            stdout="SECRET STDOUT",
            stderr="SECRET STDERR",
        ),
    )
    result = _run_live_ncp(monkeypatch, input_path, node=True)
    adapter = _ncp_result(result)
    assert adapter["state"] == "failed_closed"
    assert adapter["candidates"] == []
    assert result["findings"] == []
    assert "SECRET STDOUT" not in repr(result)
    assert "SECRET STDERR" not in repr(result)


def test_helper_success_allows_committed_parsing_and_normalization(
    monkeypatch: Any, tmp_path: Path
) -> None:
    _, _, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    _mock_success(monkeypatch, input_path)
    result = _run_live_ncp(monkeypatch, input_path, node=True)
    adapter = _ncp_result(result)
    assert adapter["state"] == "succeeded"
    assert adapter["candidates"]
    assert result["findings"]
    assert all(item["source_adapter"] == "ncp" for item in result["findings"])
    assert result["persistence_status"] == "not_requested"
    assert result["persisted_candidate_ids"] == []


def test_default_node_free_behavior_remains_unchanged(
    monkeypatch: Any, tmp_path: Path
) -> None:
    _, _, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    monkeypatch.setattr(
        oao.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("Node validation must remain opt-in"),
    )
    result = _run_live_ncp(monkeypatch, input_path, node=False)
    assert _ncp_result(result)["state"] == "succeeded"
    assert result["findings"]


def test_safety_envelope_and_no_persistence_are_preserved(
    monkeypatch: Any, tmp_path: Path
) -> None:
    _, _, input_path = _prepare_fake_repo(monkeypatch, tmp_path)
    _mock_success(monkeypatch, input_path)
    result = _run_live_ncp(monkeypatch, input_path, node=True)
    for key in (
        "no_prose",
        "no_memory_canon_mutation",
        "no_apply_promotion",
        "no_canon_promotion",
        "no_package_installs",
        "no_story_prose_generation",
        "candidate_presence_is_not_canon",
        "queue_presence_is_not_approval",
        "support_is_not_truth",
        "tool_output_is_not_canon",
    ):
        assert result["safety"][key] is True
    assert result["persistence_status"] == "not_requested"
    assert result["new_candidate_ids"] == []
    assert result["reused_candidate_ids"] == []

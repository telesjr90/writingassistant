"""Source-level guards for the MVP owner acceptance browser evidence harness."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "mvp-owner-acceptance-browser-smoke.mjs"


def read_source() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def function_body(source: str, function_name: str) -> str:
    match = re.search(rf"(async\s+)?function {function_name}\([^)]*\) \{{", source)
    assert match is not None, f"{function_name} should exist"
    start = match.end()
    depth = 1
    index = start

    while index < len(source) and depth:
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1

    assert depth == 0, f"{function_name} body should parse by braces"
    return source[start : index - 1]


def test_script_checks_ollama_readiness_version_and_tags() -> None:
    source = read_source()
    body = function_body(source, "checkOllamaHealth")

    assert "/api/version" in body
    assert "/api/tags" in body
    assert "safeFetchJson(versionUrl)" in body
    assert "safeFetchJson(tagsUrl)" in body
    assert "WSL_OLLAMA_REMEDIATION_COMMAND" in body


def test_script_reads_ollama_base_url_and_ollama_host_with_base_url_priority() -> None:
    source = read_source()
    body = function_body(source, "buildOllamaCandidates")

    assert "process.env.OLLAMA_BASE_URL" in body
    assert "process.env.OLLAMA_HOST" in body
    assert body.index("process.env.OLLAMA_BASE_URL") < body.index("process.env.OLLAMA_HOST")
    assert "addCandidate('localhost', DEFAULT_OLLAMA_BASE_URL)" in body
    assert "addCandidate('WSL Windows-host fallback', await detectWslWindowsHostUrl())" in body


def test_script_normalizes_ollama_base_urls() -> None:
    source = read_source()
    body = function_body(source, "normalizeOllamaBaseUrl")

    assert "http://" in body
    assert "replace(/\\/+$/, '')" in body
    assert "trim()" in body


def test_script_records_ollama_unreachable_as_blocked() -> None:
    source = read_source()
    body = function_body(source, "checkOllamaHealth")

    assert "startup_ollama_unreachable" in source
    assert "startup_ollama_unreachable" in body
    assert "STATUSES.BLOCKED" in body
    assert "Model-backed check blocked because Ollama readiness failed" in source


def test_script_records_attempted_ollama_candidates() -> None:
    source = read_source()
    body = function_body(source, "checkOllamaHealth")
    write_body = function_body(source, "writeEvidenceArtifacts")

    assert "attemptedCandidates" in body
    assert "ollamaAttemptedCandidates" in write_body
    assert "Selected Ollama base URL" in write_body
    assert "Selected Ollama source" in write_body
    assert "Attempted candidates" in write_body


def test_script_documents_wsl_ollama_remediation_command() -> None:
    source = read_source()

    assert "WINDOWS_HOST=$(ip route show | grep -i default | awk '{ print $3 }')" in source
    assert 'export OLLAMA_HOST="http://$WINDOWS_HOST:11434"' in source
    assert 'curl "$OLLAMA_HOST/api/version"' in source
    assert "WSL_INTEROP" in source
    assert "/proc/version" in source
    assert "/proc/net/route" in source


def test_script_has_every_owner_checklist_section() -> None:
    source = read_source()

    for section in (
        "Startup Requirements",
        "Project Isolation",
        "Manual Workspace Checks",
        "Runtime Extraction Checks",
        "Candidate / Review Checks",
        "Apply-Promotion Checks",
        "Model-Assisted / Analysis Runtime Checks",
        "No-Prose Checks",
        "Final Owner Decision",
    ):
        assert section in source


def test_script_uses_scoped_memory_canon_checks_not_global_body_for_leakage() -> None:
    source = read_source()
    body = function_body(source, "runProjectIsolationChecks")
    memory_block = body.split(
        "const memoryText = await getScopedText('section.memory-canon-shell'",
        1,
    )[1].split(
        "const projectIsolationPass =",
        1,
    )[0]

    assert "getScopedText('section.memory-canon-shell'" in body
    assert "project_isolation_memory_canon_no_leakage" in memory_block
    assert "getVisibleText()" not in memory_block
    assert "locator('body')" not in memory_block


def test_script_records_not_exposed_or_manual_review_instead_of_fake_pass() -> None:
    source = read_source()

    assert "STATUSES.NOT_EXPOSED" in source
    assert "STATUSES.MANUAL_REVIEW_REQUIRED" in source
    assert "No browser-visible runtime extraction/raw artifact control was exposed" in source
    assert "No safe apply-promotion UI fixture is visible without a review queue entry" in source
    assert "No NCP UI/runtime label visible in browser surface" in source


def test_script_preserves_no_prose_negative_assertions() -> None:
    source = read_source()
    body = function_body(source, "runNoProseChecks")

    for request in (
        "rewrite this scene",
        "continue this scene",
        "outline the next chapter",
        "generate a draft",
        "polish/improve/expand/imitate this prose",
    ):
        assert request in source

    for item_id in (
        "no_prose_no_rewrite",
        "no_prose_no_continuation",
        "no_prose_no_outline_generation",
        "no_prose_no_generated_prose",
        "no_prose_no_imitation_polish_improve_expand_draft_chapter",
    ):
        assert item_id in body


def test_script_writes_required_evidence_artifacts() -> None:
    source = read_source()
    body = function_body(source, "writeEvidenceArtifacts")

    assert "workflow-log.json" in body
    assert "checklist-results.json" in body
    assert "evidence-report.md" in body
    assert "screenshots" in source
    assert "groupedResults" in body


def test_script_has_no_generated_prose_implementation_paths() -> None:
    source = read_source()

    forbidden_implementation_patterns = (
        r"/api/chat",
        r"/api/generate",
        r"/api/create",
        r"function\s+rewrite",
        r"function\s+continue",
        r"function\s+outline",
        r"function\s+generateDraft",
        r"function\s+polish",
        r"function\s+improve",
        r"function\s+expand",
        r"function\s+imitate",
        r"\.post\([^)]*generate",
        r"\.post\([^)]*rewrite",
        r"\.post\([^)]*continue",
    )
    for pattern in forbidden_implementation_patterns:
        assert re.search(pattern, source, flags=re.IGNORECASE) is None

    assert "NO_PROSE_NEGATIVE_REQUESTS" in source
    assert "Generated prose behavior is not implemented by the harness" not in source

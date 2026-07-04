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
        "Cyber Detective Fixture",
        "Final Owner Decision",
    ):
        assert section in source


def test_script_has_cyber_detective_owner_authored_fixture() -> None:
    source = read_source()

    assert "MVP_ACCEPTANCE_FIXTURE" in source
    assert "'cyber-detective'" in source
    assert "Cyber detective" in source
    assert "rawOwnerAuthoredContent" in source
    assert "A paranoid, grumpy, cybersecurity detective" in source
    assert "ownerAuthored: true" in source
    assert "contentWarningMetadata" in source
    assert "analysis/diagnostic only" in source
    assert "didGenerateStoryProseFromFixture: false" in source
    assert "contentLength: selectedFixture.rawOwnerAuthoredContent.length" in source


def test_script_records_cyber_fixture_checklist_ids() -> None:
    source = read_source()

    for item_id in (
        "cyber_fixture_project_created",
        "cyber_fixture_owner_source_visible_on_review",
        "cyber_fixture_active_project_scoped",
        "cyber_fixture_omi_candidate_planning_only",
        "cyber_fixture_memory_canon_not_mutated",
        "cyber_fixture_story_check_source_selected",
        "cyber_fixture_story_check_submitted",
        "cyber_fixture_story_check_result_diagnostic_only",
        "cyber_fixture_story_check_no_generated_prose",
        "cyber_fixture_story_check_analysis_only",
        "cyber_fixture_story_check_no_prose_generated",
        "cyber_fixture_model_output_not_canon",
        "cyber_fixture_no_prose_rewrite_refused",
        "cyber_fixture_no_prose_continue_refused",
        "cyber_fixture_no_prose_outline_refused",
        "cyber_fixture_no_prose_draft_polish_imitation_refused",
        "cyber_fixture_no_rewrite",
        "cyber_fixture_no_continuation",
        "cyber_fixture_no_outline",
        "cyber_fixture_no_draft_polish_imitation",
        "cyber_fixture_runtime_tools_not_directly_executed",
    ):
        assert item_id in source


def test_script_records_cyber_fixture_workflow_actions() -> None:
    source = read_source()

    for action in (
        "fixture_selected",
        "cyber_fixture_create_project_begin",
        "cyber_fixture_review_before_create",
        "cyber_fixture_after_project_creation",
        "cyber_fixture_story_check_attempted",
        "cyber_fixture_story_check_skipped",
        "cyber_fixture_story_check_blocked",
        "cyber_fixture_story_check_passed",
        "cyber_fixture_no_prose_checks_attempted",
        "cyber_fixture_no_prose_checks_skipped",
        "cyber_fixture_no_prose_checks_blocked",
        "cyber_fixture_no_prose_checks_passed",
        "cyber_fixture_final_status",
    ):
        assert action in source


def test_script_includes_diagnostic_only_story_check_instruction() -> None:
    source = read_source()

    assert (
        "Analyze this owner-authored setup for story diagnostics only. "
        "Do not rewrite, continue, outline, expand, polish, imitate, or generate prose."
    ) in source
    assert "STORY_CHECK_DIAGNOSTIC_INSTRUCTION" in source


def test_script_forbids_cyber_fixture_prose_intents() -> None:
    source = read_source()

    for forbidden in (
        "rewrite",
        "continue",
        "outline",
        "draft",
        "polish",
        "improve",
        "imitate",
        "expand",
        "generate prose",
    ):
        assert forbidden in source


def test_script_records_manual_review_when_safe_cyber_ui_is_missing() -> None:
    source = read_source()
    body = function_body(source, "runCyberDetectiveFixtureChecks")
    select_body = function_body(source, "selectSafeCyberFixtureSceneForStoryCheck")

    assert "STATUSES.MANUAL_REVIEW_REQUIRED" in body
    assert "no safe selected cyber detective scene/source workflow is exposed" in body.lower()
    assert "No safe Cyber detective no-prose prompt/input path is exposed" in body
    assert "recordCyberStoryCheckManualReview" in body
    assert "missing_scene_create_or_import_workflow" in select_body
    assert "no browser-visible create/import owner-authored scene/source control is exposed" in select_body
    assert "Owner-authored source ID" in select_body
    assert "Owner-authored source text" in select_body
    assert "ux2-source-import-owner-authored" in select_body
    assert "ux2-selected-story-check-source" in select_body
    assert "setCyberSelectedSourceEvidence(" in select_body
    assert "STATUSES.PASS" in select_body
    assert "hasSafeNoProseInput = false" in body


def test_script_has_new_story_check_and_no_prose_checklist_ids() -> None:
    source = read_source()

    for item_id in (
        "cyber_fixture_story_check_source_selected",
        "cyber_fixture_story_check_submitted",
        "cyber_fixture_story_check_result_diagnostic_only",
        "cyber_fixture_story_check_no_generated_prose",
        "cyber_fixture_no_prose_rewrite_refused",
        "cyber_fixture_no_prose_continue_refused",
        "cyber_fixture_no_prose_outline_refused",
        "cyber_fixture_no_prose_draft_polish_imitation_refused",
    ):
        assert item_id in source


def test_script_uses_browser_ui_story_check_workflow_not_direct_chat() -> None:
    source = read_source()
    body = function_body(source, "runCyberDetectiveFixtureChecks")
    select_body = function_body(source, "selectSafeCyberFixtureSceneForStoryCheck")

    assert "ux2-source-create-import" in select_body
    assert "cyber_fixture_owner_authored_source_imported" in select_body
    assert "getByRole('button', { name: /Run Story Check/i })" in body
    assert "storyCheckButton.click()" in body
    assert "selectedSceneContainsFixture" in select_body
    assert "selectedFixture.rawOwnerAuthoredContent.slice(0, 80)" in select_body
    assert "/api/chat" not in source
    assert "/api/generate" not in source
    assert "/api/completions" not in source


def test_script_records_required_cyber_story_check_screenshots() -> None:
    source = read_source()

    for screenshot_name in (
        "12-cyber-fixture-source-scene-selection",
        "13-cyber-fixture-story-check-before-submit",
        "14-cyber-fixture-story-check-result-error",
        "15-cyber-fixture-no-prose-negative-prompt-attempt-result",
    ):
        assert screenshot_name in source


def test_script_fails_on_generated_prose_markers() -> None:
    source = read_source()
    body = function_body(source, "runCyberDetectiveFixtureChecks")

    for marker in (
        "here(?:'s| is) (?:a|the) (?:rewrite|rewritten|continuation|continued|outline|draft|polished|improved|expanded|imitation)",
        "(?:INT\\.|EXT\\.)",
        "chapter\\s+\\d+\\s*:",
    ):
        assert marker in source

    assert "containsForbiddenGeneratedProse(resultText)" in body
    assert "storyCheckError" in body
    assert "fail-closed/manual-review error" in body
    assert "STATUSES.FAIL" in body
    assert "Generated story prose marker detected" in source


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
    cyber_body = function_body(source, "runCyberDetectiveFixtureChecks")

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

    assert "ux2-no-prose-refusal-panel" in cyber_body
    assert "noProseRefusalsCovered" in cyber_body
    assert "didSubmitUnsafePrompt: false" in cyber_body
    assert "setCyberNoProseEvidence(" in cyber_body


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


def test_script_does_not_call_direct_generation_or_training_artifact_paths() -> None:
    source = read_source()

    forbidden_direct_calls = (
        "/api/chat",
        "/api/generate",
        "/api/completions",
        "/api/embeddings",
        "create_training_jsonl",
        "fine_tuning",
        "fine-tuning",
    )
    for forbidden in forbidden_direct_calls:
        assert forbidden not in source

    assert re.search(r"fs\.writeFile\([^)]*\.jsonl", source, flags=re.IGNORECASE) is None
    assert re.search(r"fs\.writeFile\([^)]*dataset", source, flags=re.IGNORECASE) is None
    assert re.search(r"fs\.writeFile\([^)]*(?:model_artifact|\.bin|\.safetensors|\.gguf)", source, flags=re.IGNORECASE) is None
    assert "/api/version" in source
    assert "/api/tags" in source


def test_script_does_not_execute_runtime_tools_directly() -> None:
    source = read_source()

    for forbidden_call in (
        "runBookNLP",
        "runSpacy",
        "runSpaCy",
        "booknlp.process",
        "spacy.load",
        "subtxt run",
        "ncp run",
    ):
        assert forbidden_call not in source

    assert "cyber_fixture_runtime_tools_not_directly_executed" in source
    assert "directRuntimeToolsExecuted: false" in source

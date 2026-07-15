"""Focused T010 contracts for specialized Plan Integrity reviewers.

All finding inputs and evidence are temporary fixtures. Tests do not invoke an
OpenCode agent, model, network, retrieval system, or external command.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.project_memory.reviewer_findings import (  # noqa: E402
    AUTHORIZED_DOMAINS,
    ReviewerFindingsError,
    deterministic_finding_id,
    normalize_reviewer_findings,
)
from scripts.project_memory.validate_reviewer_guidance import (  # noqa: E402
    ALLOWED_SHELL_GRANTS,
    REQUIRED_FILES,
    REVIEWER_AGENTS,
    validate_reviewer_guidance,
)


COMMIT = "a" * 40
BRANCH = "review-test"


def _copy_guidance(tmp_path: Path) -> Path:
    for relative_path in REQUIRED_FILES:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative_path, target)
    return tmp_path


def _fixture(tmp_path: Path, domain: str = "backend_contracts") -> tuple[Path, dict]:
    root = tmp_path / "repo"
    source = root / "docs" / "source.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Contract\n\nBounded evidence line.\n", encoding="utf-8")
    report = root / ".codex-context" / "project-memory" / "accepted-pi"
    report.mkdir(parents=True)
    (report / "run-metadata.json").write_text(
        json.dumps({
            "authority_class": "generated_evidence",
            "branch": BRANCH,
            "bound_commit": COMMIT,
        }),
        encoding="utf-8",
    )
    (report / "readiness.json").write_text(
        json.dumps({"result": "READY_WITH_ADVISORIES"}),
        encoding="utf-8",
    )
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    document = {
        "request": {
            "repository_root": str(root),
            "expected_branch": BRANCH,
            "expected_full_commit": COMMIT,
            "reviewer_domain": domain,
            "task_or_feature_scope": "TASK-001/component-a",
            "maximum_file_scope": ["docs/"],
            "allowed_source_classes": ["authoritative", "accepted_evidence"],
            "protected_paths": ["projects/", "books/"],
            "accepted_plan_integrity_report_path": ".codex-context/project-memory/accepted-pi",
            "freshness_requirement": "current_clean_head",
            "historical_evidence_permission": False,
            "owner_decision_requirement": False,
        },
        "repository_state": {
            "repository_root": str(root),
            "branch": BRANCH,
            "full_commit": COMMIT,
            "dirty": False,
            "staged": False,
        },
        "findings": [{
            "content_type": "plan_integrity_review_finding",
            "reviewer_domain": domain,
            "rule_or_concern_id": "BC-001",
            "title": "Contract evidence requires a deterministic check",
            "bounded_claim": "The scoped contract has one evidence-backed concern.",
            "result": "CONCERN",
            "status": "proposed",
            "severity": "warning",
            "blocking_recommendation": False,
            "affected_ids": ["TASK-001", "component-a"],
            "evidence_locators": [{
                "path": "docs/source.md",
                "line_start": 1,
                "line_end": 3,
                "sha256": digest,
                "authority_class": "authoritative",
                "freshness": "current",
                "bound_commit": COMMIT,
            }],
            "facts": ["The scoped source contains a bounded contract statement."],
            "inferences": ["A future exact check may be useful."],
            "uncertainty_or_conflicting_evidence": [],
            "owner_decision_status": "not_required",
            "recommended_deterministic_follow_up": "Add an exact fixture assertion.",
            "authority_declaration": "generated_evidence",
        }],
    }
    return root, document


def _normalize(root: Path, document: dict) -> dict:
    return normalize_reviewer_findings(document, root)


def _expect_error(root: Path, document: dict, code: str) -> None:
    with pytest.raises(ReviewerFindingsError) as exc_info:
        _normalize(root, document)
    assert exc_info.value.code == code


def test_exact_six_domains_and_agent_definitions():
    assert AUTHORIZED_DOMAINS == tuple(REVIEWER_AGENTS)
    assert AUTHORIZED_DOMAINS == (
        "backend_contracts",
        "frontend_ui",
        "test_coverage",
        "roadmap_consistency",
        "enrichment_accuracy",
        "decision_coherence",
    )


def test_guidance_validator_passes_complete_temporary_copy(tmp_path):
    fixture = _copy_guidance(tmp_path)
    report = validate_reviewer_guidance(fixture)
    assert report["result"] == "PASS"
    assert report["findings"] == []
    assert report["reviewer_domains"] == list(AUTHORIZED_DOMAINS)


def test_guidance_validator_fails_closed_and_sorts(tmp_path):
    fixture = _copy_guidance(tmp_path)
    agent = fixture / REVIEWER_AGENTS["backend_contracts"]
    agent.write_text("write: true\nwebfetch: true\n", encoding="utf-8")
    report = validate_reviewer_guidance(fixture)
    assert report["result"] == "BLOCKED"
    keys = [(item["code"], item["path"], item["detail"]) for item in report["findings"]]
    assert keys == sorted(keys)
    assert {item["code"] for item in report["findings"]} >= {
        "forbidden_permission_grant",
        "missing_reviewer_control",
        "shell_allowlist_mismatch",
    }


def test_each_agent_has_only_bounded_read_only_git_shell_grants(tmp_path):
    fixture = _copy_guidance(tmp_path)
    for relative_path in REVIEWER_AGENTS.values():
        text = (fixture / relative_path).read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        grants = tuple(
            line.strip()
            for line in frontmatter.splitlines()
            if line.strip().endswith(": allow")
        )
        assert grants == ALLOWED_SHELL_GRANTS
        assert all(token in text for token in (
            "write: false", "edit: false", "patch: false", "webfetch: false",
            "task: false", "external_directory: deny", '"*": deny',
        ))


def test_protocol_and_skill_keep_t009_as_readiness_authority(tmp_path):
    fixture = _copy_guidance(tmp_path)
    protocol = (fixture / "docs/project-memory/reviewer-protocol.md").read_text()
    skill = (fixture / ".agents/skills/project-memory-plan-integrity-review/SKILL.md").read_text()
    assert "T009 remains the sole deterministic readiness authority" in protocol
    assert all(value in protocol for value in ("`READY`", "`READY_WITH_ADVISORIES`", "`BLOCKED`"))
    assert "Never change T009 readiness" in skill
    assert "generated_evidence" in protocol and "generated_evidence" in skill


def test_schema_defines_bounded_reviewer_contracts_in_temporary_copy(tmp_path):
    source = REPO_ROOT / "docs/project-memory/schemas/project-memory.schema.json"
    target = tmp_path / "project-memory.schema.json"
    shutil.copyfile(source, target)
    definitions = json.loads(target.read_text(encoding="utf-8"))["$defs"]
    assert definitions["PlanIntegrityReviewerDomain"]["enum"] == list(AUTHORIZED_DOMAINS)
    request = definitions["PlanIntegrityReviewerRequest"]
    finding = definitions["PlanIntegrityReviewerFinding"]
    package = definitions["PlanIntegrityReviewerFindingsPackage"]
    assert request["additionalProperties"] is False
    assert finding["properties"]["authority_declaration"] == {"const": "generated_evidence"}
    assert package["properties"]["t009_readiness_mutation_performed"] == {"const": False}


@pytest.mark.parametrize("domain", AUTHORIZED_DOMAINS)
def test_all_authorized_domains_normalize(domain, tmp_path):
    root, document = _fixture(tmp_path, domain)
    output = _normalize(root, document)
    assert output["reviewer_domain"] == domain
    assert output["finding_count"] == 1


def test_normalization_generates_stable_id_and_generated_evidence(tmp_path):
    root, document = _fixture(tmp_path)
    output = _normalize(root, document)
    finding = output["findings"][0]
    assert finding["finding_id"] == deterministic_finding_id(finding)
    assert output["authority_class"] == "generated_evidence"
    assert finding["authority_declaration"] == "generated_evidence"


def test_normalization_is_byte_stable(tmp_path):
    root, document = _fixture(tmp_path)
    first = _normalize(root, copy.deepcopy(document))
    second = _normalize(root, copy.deepcopy(document))
    assert json.dumps(first, sort_keys=True).encode() == json.dumps(second, sort_keys=True).encode()


def test_multiple_findings_are_preserved_and_sorted(tmp_path):
    root, document = _fixture(tmp_path)
    second = copy.deepcopy(document["findings"][0])
    second["rule_or_concern_id"] = "AA-002"
    second["title"] = "Second supported concern"
    second["bounded_claim"] = "A second evidence-backed concern remains separate."
    second["severity"] = "critical"
    document["findings"].insert(0, second)
    output = _normalize(root, document)
    assert output["finding_count"] == 2
    assert [item["rule_or_concern_id"] for item in output["findings"]] == ["AA-002", "BC-001"]
    assert output["semantic_truth_selected"] is False


def test_exact_supplied_id_is_accepted_and_mismatch_rejected(tmp_path):
    root, document = _fixture(tmp_path)
    normalized = _normalize(root, copy.deepcopy(document))["findings"][0]
    document["findings"][0]["finding_id"] = normalized["finding_id"]
    assert _normalize(root, copy.deepcopy(document))["finding_count"] == 1
    document["findings"][0]["finding_id"] = "review-finding-" + "0" * 20
    _expect_error(root, document, "finding_id_mismatch")


def test_unsupported_domain_is_rejected(tmp_path):
    root, document = _fixture(tmp_path)
    document["request"]["reviewer_domain"] = "security_oracle"
    document["findings"][0]["reviewer_domain"] = "security_oracle"
    _expect_error(root, document, "unsupported_domain")


@pytest.mark.parametrize("path", ["../outside.md", "/tmp/outside.md", "docs\\source.md"])
def test_unsafe_or_external_locator_syntax_is_rejected(path, tmp_path):
    root, document = _fixture(tmp_path)
    document["findings"][0]["evidence_locators"][0]["path"] = path
    _expect_error(root, document, "unsafe_path")


def test_missing_locator_and_missing_evidence_are_rejected(tmp_path):
    root, document = _fixture(tmp_path)
    missing = copy.deepcopy(document)
    missing["findings"][0]["evidence_locators"][0]["path"] = "docs/missing.md"
    _expect_error(root, missing, "missing_locator")
    document["findings"][0]["evidence_locators"] = []
    _expect_error(root, document, "missing_evidence")


def test_unbound_locator_commit_and_hash_mismatch_are_rejected(tmp_path):
    root, document = _fixture(tmp_path)
    unbound = copy.deepcopy(document)
    unbound["findings"][0]["evidence_locators"][0]["bound_commit"] = "short"
    _expect_error(root, unbound, "unbound_commit")
    document["findings"][0]["evidence_locators"][0]["sha256"] = "0" * 64
    _expect_error(root, document, "locator_hash_mismatch")


def test_scope_and_protected_path_fail_closed(tmp_path):
    root, document = _fixture(tmp_path)
    outside_scope = copy.deepcopy(document)
    outside_scope["request"]["maximum_file_scope"] = ["tests/"]
    _expect_error(root, outside_scope, "unsupported_scope")
    document["request"]["protected_paths"] = ["docs/"]
    _expect_error(root, document, "protected_path")


def test_historical_evidence_requires_permission(tmp_path):
    root, document = _fixture(tmp_path)
    locator = document["findings"][0]["evidence_locators"][0]
    locator["freshness"] = "historical"
    locator["bound_commit"] = "b" * 40
    _expect_error(root, copy.deepcopy(document), "historical_evidence_denied")
    document["request"]["historical_evidence_permission"] = True
    assert _normalize(root, document)["finding_count"] == 1


@pytest.mark.parametrize("field", ["dirty", "staged"])
def test_unclean_repository_state_is_rejected(field, tmp_path):
    root, document = _fixture(tmp_path)
    document["repository_state"][field] = True
    _expect_error(root, document, "unclean_input")


@pytest.mark.parametrize("field,value", [("branch", "other"), ("full_commit", "b" * 40)])
def test_stale_repository_binding_is_rejected(field, value, tmp_path):
    root, document = _fixture(tmp_path)
    document["repository_state"][field] = value
    _expect_error(root, document, "stale_binding")


@pytest.mark.parametrize("metadata_change,readiness,code", [
    ({"authority_class": "authoritative"}, "READY", "authority_violation"),
    ({"bound_commit": "b" * 40}, "READY", "stale_binding"),
    ({}, "BLOCKED", "plan_integrity_blocked"),
])
def test_accepted_plan_integrity_report_gate(metadata_change, readiness, code, tmp_path):
    root, document = _fixture(tmp_path)
    report = root / ".codex-context/project-memory/accepted-pi"
    metadata = json.loads((report / "run-metadata.json").read_text())
    metadata.update(metadata_change)
    (report / "run-metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (report / "readiness.json").write_text(json.dumps({"result": readiness}), encoding="utf-8")
    _expect_error(root, document, code)


def test_facts_and_inferences_must_remain_distinct(tmp_path):
    root, document = _fixture(tmp_path)
    fact = document["findings"][0]["facts"][0]
    document["findings"][0]["inferences"] = [fact]
    _expect_error(root, document, "fact_inference_overlap")


@pytest.mark.parametrize("field", ["confidence", "confidence_score", "probability", "story_prose"])
def test_confidence_as_truth_and_story_prose_fields_are_rejected(field, tmp_path):
    root, document = _fixture(tmp_path)
    document["findings"][0][field] = "unsupported content"
    _expect_error(root, document, "prohibited_content")


@pytest.mark.parametrize("field,value,code", [
    ("authority_declaration", "authoritative", "authority_violation"),
    ("status", "approved", "prohibited_status"),
    ("result", "TASK_CLOSED", "prohibited_status"),
    ("content_type", "story_prose", "story_prose_rejected"),
])
def test_authority_status_canon_and_prose_contracts_fail_closed(field, value, code, tmp_path):
    root, document = _fixture(tmp_path)
    document["findings"][0][field] = value
    _expect_error(root, document, code)


@pytest.mark.parametrize("claim", [
    "This finding is authoritative.",
    "The task should be closed.",
    "Automatically mutate the roadmap.",
    "Run apply-promotion now.",
    "Write the Memory/Canon records.",
])
def test_prohibited_authority_and_automatic_mutation_claims_are_rejected(claim, tmp_path):
    root, document = _fixture(tmp_path)
    document["findings"][0]["bounded_claim"] = claim
    _expect_error(root, document, "prohibited_claim")


def test_owner_pending_fails_when_accepted_owner_decision_is_required(tmp_path):
    root, document = _fixture(tmp_path)
    document["request"]["owner_decision_requirement"] = True
    document["findings"][0]["owner_decision_status"] = "owner_pending"
    _expect_error(root, document, "owner_decision_required")


def test_output_cannot_change_t009_or_create_owner_decision(tmp_path):
    root, document = _fixture(tmp_path)
    output = _normalize(root, document)
    assert output["t009_readiness_mutation_performed"] is False
    assert output["owner_decision_created"] is False
    assert output["semantic_truth_selected"] is False


def test_implementation_has_no_model_network_subprocess_or_write_path():
    source = (REPO_ROOT / "scripts/project_memory/reviewer_findings.py").read_text()
    assert "import subprocess" not in source
    assert "urllib" not in source and "requests" not in source
    assert "ollama" not in source.lower()
    assert "write_text(" not in source and "write_bytes(" not in source

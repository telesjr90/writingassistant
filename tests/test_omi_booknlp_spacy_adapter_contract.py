"""PHASE8-IMPL-023-T007 BookNLP/spaCy fixture adapter contract tests.

These tests use fixture/mock output only. They do not import or run real
BookNLP or spaCy, install dependencies, mutate Memory/Canon, create promotion
records, run apply-promotion, persist AI/tool candidates, or generate story
prose.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend import omi_analysis_orchestrator as oao


RAW_IDEA = (
    "Owner note: Mara Vale meets the Harbor Archive clerk near the west quay. "
    "The brass key is logged after the storm alarm."
)


def _booknlp_finding(**overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "raw_finding_id": "booknlp-person-1",
        "finding_type": "person_entity",
        "label": "Mara Vale",
        "extracted_claim": "Mara Vale appears as a person entity candidate",
        "evidence": [
            {
                "source_excerpt": "Mara Vale meets the Harbor Archive clerk",
                "source_locator": "raw_idea:L1:C12-55",
            }
        ],
        "source_locator": "raw_idea:L1:C12-55",
        "confidence": "medium support",
    }
    finding.update(overrides)
    return finding


def _spacy_finding(**overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "raw_finding_id": "spacy-person-1",
        "spacy_label": "PERSON",
        "text": "Mara Vale",
        "claim": "Mara Vale appears as a PERSON entity candidate",
        "sentence": "Mara Vale meets the Harbor Archive clerk near the west quay.",
        "source_locator": "raw_idea:L1:C12-76",
        "confidence": "spaCy fixture support only",
    }
    finding.update(overrides)
    return finding


def _booknlp_envelope(findings: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "schema_version": oao.OMI_BOOKNLP_SCHEMA_VERSION,
        "adapter": "booknlp",
        "status": "succeeded",
        "explanation": "fixture-only BookNLP local NLP extraction",
        "provenance": {
            "tool_source": "booknlp",
            "adapter": "booknlp",
            "support": "BookNLP fixture support only",
        },
        "findings": findings if findings is not None else [_booknlp_finding()],
    }


def _spacy_envelope(findings: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "schema_version": oao.OMI_SPACY_SCHEMA_VERSION,
        "adapter": "spacy",
        "status": "succeeded",
        "explanation": "fixture-only spaCy local NLP extraction",
        "provenance": {
            "tool_source": "spacy",
            "adapter": "spacy",
            "support": "spaCy fixture support only",
        },
        "findings": findings if findings is not None else [_spacy_finding()],
    }


def _run_adapter(adapter: str, fixture: Any | None = None, **kwargs: Any) -> dict[str, Any]:
    params: dict[str, Any] = {
        "persist_candidates": False,
        "requested_adapters": [adapter],
    }
    if fixture is not None:
        params["adapter_fixture_outputs"] = {adapter: fixture}
    params.update(kwargs)
    return oao.analyze_omi_raw_idea_with_tools("demo", RAW_IDEA, **params)


def _adapter_env(result: dict[str, Any], adapter: str) -> dict[str, Any]:
    envs = [env for env in result["adapter_results"] if env["adapter"] == adapter]
    assert len(envs) == 1
    return envs[0]


def _assert_failed_closed(result: dict[str, Any], adapter: str) -> dict[str, Any]:
    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    env = _adapter_env(result, adapter)
    assert env["state"] in {"failed_closed", "unavailable", "error"}
    assert env["candidates"] == []
    assert env["explanation"]
    return env


def _assert_candidate_only_finding(finding: dict[str, Any], adapter: str) -> None:
    assert finding["source_adapter"] == adapter
    assert finding["provenance"]["tool_source"] == adapter
    assert finding["provenance"]["adapter"] == adapter
    assert "support" in finding["provenance"]["support"].lower()
    assert "support" in finding["support_label"].lower()
    assert finding["owner_decision"]["decision"] == "pending"
    assert finding["owner_decision"]["approved"] is False
    assert finding["review_status"] == "candidate_review_pending"
    assert finding["source_locator"]
    assert finding["evidence"][0]["source_excerpt"]
    assert finding["evidence"][0]["source_locator"]
    assert finding["candidate_fingerprint"].startswith("omi-cand-")
    assert finding["evidence_fingerprint"].startswith("omi-evid-")
    assert finding["normalized_finding_id"].startswith(f"omi-find-{adapter}-")
    for forbidden in ("truth", "canon", "approved", "promoted"):
        assert forbidden not in finding["support_label"].lower()


def test_booknlp_without_fixture_returns_unavailable_and_no_findings() -> None:
    result = _run_adapter("booknlp")
    env = _assert_failed_closed(result, "booknlp")
    assert env["state"] == "unavailable"
    assert "fixture" in env["explanation"].lower()
    assert "live booknlp" in env["explanation"].lower()


def test_spacy_without_fixture_returns_unavailable_and_no_findings() -> None:
    result = _run_adapter("spacy")
    env = _assert_failed_closed(result, "spacy")
    assert env["state"] == "unavailable"
    assert "fixture" in env["explanation"].lower()
    assert "live spacy" in env["explanation"].lower()


def test_valid_booknlp_fixture_normalizes_candidate_only_findings() -> None:
    fixture = _booknlp_envelope(
        [
            _booknlp_finding(),
            _booknlp_finding(
                raw_finding_id="booknlp-location-1",
                finding_type="location",
                label="Harbor Archive",
                extracted_claim="Harbor Archive appears as a location candidate",
                evidence=[
                    {
                        "source_excerpt": "near the west quay at the Harbor Archive",
                        "source_locator": "raw_idea:L1:C50-90",
                    }
                ],
                source_locator="raw_idea:L1:C50-90",
            ),
            _booknlp_finding(
                raw_finding_id="booknlp-event-1",
                finding_type="event_mention",
                label="storm alarm",
                extracted_claim="storm alarm appears as an event mention candidate",
                evidence=[
                    {
                        "source_excerpt": "after the storm alarm",
                        "source_locator": "raw_idea:L1:C108-129",
                    }
                ],
                source_locator="raw_idea:L1:C108-129",
            ),
            _booknlp_finding(
                raw_finding_id="booknlp-coref-1",
                finding_type="coreference_relationship",
                label="Mara Vale / Harbor Archive clerk",
                extracted_claim=(
                    "Mara Vale and Harbor Archive clerk appear in relationship support"
                ),
                evidence=[
                    {
                        "source_excerpt": "Mara Vale meets the Harbor Archive clerk",
                        "source_locator": "raw_idea:L1:C12-55",
                    }
                ],
                source_locator="raw_idea:L1:C12-55",
            ),
            _booknlp_finding(
                raw_finding_id="booknlp-named-entity-1",
                finding_type="named_entity",
                label="Harbor Archive clerk",
                extracted_claim=(
                    "Harbor Archive clerk appears as named entity evidence support"
                ),
                quote_text="Harbor Archive clerk",
                source_locator="raw_idea:L1:C34-55",
            ),
        ]
    )

    result = _run_adapter("booknlp", fixture)

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert _adapter_env(result, "booknlp")["state"] == "succeeded"
    assert [finding["candidate_type"] for finding in result["findings"]] == [
        "character",
        "location",
        "timeline_event",
        "relationship",
        "evidence_note",
    ]
    assert result["findings"][0]["label"] == "Mara Vale"
    assert result["findings"][0]["evidence"][0]["source_excerpt"] == (
        "Mara Vale meets the Harbor Archive clerk"
    )
    assert result["findings"][0]["source_locator"] == "raw_idea:L1:C12-55"
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "booknlp")


def test_valid_spacy_fixture_normalizes_candidate_only_findings() -> None:
    fixture = _spacy_envelope(
        [
            _spacy_finding(),
            _spacy_finding(
                raw_finding_id="spacy-loc-1",
                spacy_label="LOC",
                text="west quay",
                claim="west quay appears as a LOC location candidate",
                sentence="Mara Vale meets the clerk near the west quay.",
                source_locator="raw_idea:L1:C68-76",
            ),
            _spacy_finding(
                raw_finding_id="spacy-org-1",
                spacy_label="ORG",
                text="Harbor Archive",
                claim="Harbor Archive appears as an ORG candidate",
                sentence="Mara Vale meets the Harbor Archive clerk.",
                source_locator="raw_idea:L1:C28-43",
            ),
            _spacy_finding(
                raw_finding_id="spacy-object-1",
                spacy_label="CONCRETE_NOUN",
                text="brass key",
                claim="brass key appears as a concrete object candidate",
                sentence="",
                token_span={
                    "text": "The brass key is logged after the storm alarm.",
                    "source_locator": "raw_idea:L1:C82-129",
                },
                source_locator="raw_idea:L1:C82-91",
            ),
            _spacy_finding(
                raw_finding_id="spacy-event-1",
                spacy_label="EVENT",
                text="storm alarm",
                claim="storm alarm appears as an EVENT mention candidate",
                sentence="The brass key is logged after the storm alarm.",
                source_locator="raw_idea:L1:C108-119",
            ),
        ]
    )

    result = _run_adapter("spacy", fixture)

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert _adapter_env(result, "spacy")["state"] == "succeeded"
    assert [finding["candidate_type"] for finding in result["findings"]] == [
        "character",
        "location",
        "organization",
        "object",
        "timeline_event",
    ]
    assert result["findings"][3]["label"] == "brass key"
    assert result["findings"][3]["evidence"][0]["source_excerpt"] == (
        "The brass key is logged after the storm alarm."
    )
    assert result["findings"][3]["source_locator"] == "raw_idea:L1:C82-91"
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "spacy")


def test_booknlp_fixture_missing_evidence_source_locator_or_provenance_fails_closed() -> None:
    missing_evidence = _booknlp_envelope([_booknlp_finding()])
    del missing_evidence["findings"][0]["evidence"]

    missing_source_locator = _booknlp_envelope([_booknlp_finding()])
    del missing_source_locator["findings"][0]["source_locator"]

    missing_provenance = _booknlp_envelope([_booknlp_finding()])
    del missing_provenance["provenance"]

    for fixture in (missing_evidence, missing_source_locator, missing_provenance):
        result = _run_adapter("booknlp", fixture)
        _assert_failed_closed(result, "booknlp")


def test_spacy_fixture_missing_evidence_source_locator_or_provenance_fails_closed() -> None:
    missing_sentence = _spacy_envelope([_spacy_finding()])
    del missing_sentence["findings"][0]["sentence"]

    missing_source_locator = _spacy_envelope([_spacy_finding()])
    del missing_source_locator["findings"][0]["source_locator"]

    missing_provenance = _spacy_envelope([_spacy_finding()])
    del missing_provenance["provenance"]

    for fixture in (missing_sentence, missing_source_locator, missing_provenance):
        result = _run_adapter("spacy", fixture)
        _assert_failed_closed(result, "spacy")


def test_booknlp_and_spacy_reject_truth_canon_approved_or_promoted_output() -> None:
    fixtures = [
        ("booknlp", _booknlp_envelope([
            _booknlp_finding(support_label="approved canon support")
        ])),
        ("spacy", _spacy_envelope([
            _spacy_finding(owner_decision={"decision": "approve", "approved": True})
        ])),
    ]

    for adapter, fixture in fixtures:
        env = _assert_failed_closed(_run_adapter(adapter, fixture), adapter)
        assert "truth" in env["explanation"].lower() or "approve" in (
            env["explanation"].lower()
        )


def test_booknlp_and_spacy_reject_prose_like_generated_output() -> None:
    fixtures = [
        ("booknlp", _booknlp_envelope([
            _booknlp_finding(extracted_claim="Rewrite: a polished version begins here")
        ])),
        ("spacy", _spacy_envelope([
            _spacy_finding(claim="Chapter 2: Mara stepped into the rain")
        ])),
    ]

    for adapter, fixture in fixtures:
        env = _assert_failed_closed(_run_adapter(adapter, fixture), adapter)
        assert "prose" in env["explanation"].lower()


def test_booknlp_and_spacy_reject_memory_canon_and_promotion_operations() -> None:
    fixtures = [
        ("booknlp", _booknlp_envelope([
            _booknlp_finding(apply_promotion_enabled=True)
        ])),
        ("spacy", _spacy_envelope([
            _spacy_finding(promotion_record={"id": "unsafe"})
        ])),
    ]

    for adapter, fixture in fixtures:
        env = _assert_failed_closed(_run_adapter(adapter, fixture), adapter)
        assert "promotion" in env["explanation"].lower()


def test_booknlp_and_spacy_findings_are_not_persisted_or_mutating(monkeypatch: Any) -> None:
    import backend.project_manager as project_manager

    calls: list[dict[str, Any]] = []

    def spy_extract(*args: Any, **kwargs: Any) -> dict[str, Any]:
        calls.append({"args": args, "kwargs": kwargs})
        return {"candidates": [], "persisted_candidate_ids": []}

    monkeypatch.setattr(
        project_manager,
        "extract_omi_candidates_from_raw_idea",
        spy_extract,
    )

    for adapter, fixture in (
        ("booknlp", _booknlp_envelope()),
        ("spacy", _spacy_envelope()),
    ):
        result = _run_adapter(adapter, fixture, persist_candidates=True)
        assert result["analysis_status"] == "succeeded"
        assert result["persisted_candidate_ids"] == []
        assert result["safety"]["no_memory_canon_mutation"] is True
        assert result["safety"]["no_apply_promotion"] is True

    assert calls == []


# ---------------------------------------------------------------------------
# T014C — Live spaCy adapter behind env flags
# ---------------------------------------------------------------------------


def _mock_live_spacy_env(monkeypatch: Any) -> None:
    monkeypatch.setenv("OMI_LIVE_TOOLS_ENABLED", "true")
    monkeypatch.setenv("OMI_LIVE_SPACY_ENABLED", "true")


def _install_mock_spacy(monkeypatch: Any) -> MagicMock:
    """Install a mock spaCy module so import spacy succeeds."""
    mock_spacy = MagicMock()
    mock_nlp = MagicMock()
    mock_spacy.load.return_value = mock_nlp
    monkeypatch.setitem(sys.modules, "spacy", mock_spacy)
    return mock_nlp


def _make_mock_doc(
    text: str,
    entities: list[tuple[str, str, int, int]] | None = None,
    noun_chunks: list[tuple[str, int, int]] | None = None,
) -> MagicMock:
    """Create a mock spaCy Doc with entities and noun chunks.

    Each entity is a (text, label_, start_char, end_char) tuple.
    Each noun chunk is a (text, start_char, end_char) tuple.
    """
    doc = MagicMock()
    doc.text = text
    doc.ents = []
    doc.noun_chunks = []

    seen_texts: set[str] = set()

    if entities:
        for label_text, ent_type, start, end in entities:
            ent = MagicMock()
            ent.text = label_text
            ent.label_ = ent_type
            ent.start_char = start
            ent.end_char = end
            ent.start = start
            ent.end = end
            sent = MagicMock()
            sent.text = text
            ent.sent = sent
            doc.ents.append(ent)
            seen_texts.add(label_text.lower())

    if noun_chunks:
        for chunk_text, chunk_start, chunk_end in noun_chunks:
            if chunk_text.lower() in seen_texts:
                continue
            chunk = MagicMock()
            chunk.text = chunk_text
            chunk.start_char = chunk_start
            chunk.end_char = chunk_end
            chunk.start = chunk_start
            chunk.end = chunk_end
            sent = MagicMock()
            sent.text = text
            chunk.sent = sent
            doc.noun_chunks.append(chunk)

    return doc


def test_live_spacy_disabled_by_default_returns_unavailable() -> None:
    """No env flags -> live spaCy path not triggered -> unavailable."""
    result = _run_adapter("spacy")
    env = _assert_failed_closed(result, "spacy")
    assert env["state"] == "unavailable"


def test_live_spacy_enabled_with_mocked_model_returns_normalized_candidates(
    monkeypatch: Any,
) -> None:
    """Live spaCy with mocked model returns normalized candidate findings."""
    _mock_live_spacy_env(monkeypatch)
    mock_nlp = _install_mock_spacy(monkeypatch)

    mock_doc = _make_mock_doc(
        RAW_IDEA,
        entities=[
            ("Mara Vale", "PERSON", 12, 21),
            ("the west quay", "LOC", 61, 73),
            ("Harbor Archive", "ORG", 28, 42),
            ("the storm alarm", "EVENT", 104, 119),
        ],
    )
    mock_nlp.return_value = mock_doc

    result = _run_adapter("spacy")

    assert result["analysis_status"] == "succeeded"
    env = _adapter_env(result, "spacy")
    assert env["state"] == "succeeded"
    assert len(env["candidates"]) == 4
    types = [f["candidate_type"] for f in env["candidates"]]
    assert "character" in types
    assert "location" in types
    assert "organization" in types
    assert "timeline_event" in types
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "spacy")


def test_live_spacy_noun_chunks_produce_object_candidates(
    monkeypatch: Any,
) -> None:
    """Non-overlapping noun chunks produce object candidates."""
    _mock_live_spacy_env(monkeypatch)
    mock_nlp = _install_mock_spacy(monkeypatch)

    mock_doc = _make_mock_doc(
        RAW_IDEA,
        entities=[
            ("Mara Vale", "PERSON", 12, 21),
        ],
        noun_chunks=[
            ("the brass key", 82, 96),
        ],
    )
    mock_nlp.return_value = mock_doc

    result = _run_adapter("spacy")

    assert result["analysis_status"] == "succeeded"
    env = _adapter_env(result, "spacy")
    assert env["state"] == "succeeded"
    types = [f["candidate_type"] for f in env["candidates"]]
    assert "object" in types
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "spacy")


def test_live_spacy_missing_package_returns_unavailable(
    monkeypatch: Any,
) -> None:
    """spaCy not installed -> runner returns unavailable."""
    _mock_live_spacy_env(monkeypatch)

    result = _run_adapter("spacy")

    env = _assert_failed_closed(result, "spacy")
    assert env["state"] == "unavailable"
    assert "not installed" in env["explanation"].lower()


def test_live_spacy_model_load_failure_returns_unavailable(
    monkeypatch: Any,
) -> None:
    """Model load failure -> runner returns unavailable."""
    _mock_live_spacy_env(monkeypatch)

    mock_spacy = MagicMock()
    mock_spacy.load.side_effect = OSError("mock model not found")
    monkeypatch.setitem(sys.modules, "spacy", mock_spacy)

    result = _run_adapter("spacy")

    env = _assert_failed_closed(result, "spacy")
    assert env["state"] == "unavailable"
    assert "model" in env["explanation"].lower()
    assert "not" in env["explanation"].lower()


def test_live_spacy_runtime_exception_fails_closed(
    monkeypatch: Any,
) -> None:
    """Processing exception -> runner returns failed_closed."""
    _mock_live_spacy_env(monkeypatch)

    mock_spacy = MagicMock()
    mock_nlp = MagicMock()
    mock_nlp.side_effect = RuntimeError("mock processing error")
    mock_spacy.load.return_value = mock_nlp
    monkeypatch.setitem(sys.modules, "spacy", mock_spacy)

    result = _run_adapter("spacy")

    env = _assert_failed_closed(result, "spacy")
    assert env["state"] in {"unavailable", "failed_closed"}
    assert "processing" in env["explanation"].lower() or "error" in (
        env["explanation"].lower()
    )


def test_live_spacy_safety_boundaries_preserved(
    monkeypatch: Any,
) -> None:
    """Live spaCy findings preserve candidate-only safety boundaries."""
    _mock_live_spacy_env(monkeypatch)
    mock_nlp = _install_mock_spacy(monkeypatch)

    mock_doc = _make_mock_doc(
        RAW_IDEA,
        entities=[
            ("Mara Vale", "PERSON", 12, 21),
        ],
    )
    mock_nlp.return_value = mock_doc

    result = _run_adapter("spacy", persist_candidates=True)

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True

    for finding in result["findings"]:
        for forbidden in ("truth", "canon", "approved", "promoted"):
            assert forbidden not in finding["support_label"].lower()
        assert finding["owner_decision"]["approved"] is False
        assert finding["source_adapter"] == "spacy"
        assert finding["evidence"][0]["source_excerpt"]
        assert finding["evidence"][0]["source_locator"]

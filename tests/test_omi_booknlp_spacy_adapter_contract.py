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


# ---------------------------------------------------------------------------
# T017B — Live BookNLP adapter behind env flags
# ---------------------------------------------------------------------------


def _mock_live_booknlp_env(monkeypatch: Any) -> None:
    """Enable both the global live-tools flag and the per-tool flag."""
    monkeypatch.setenv("OMI_LIVE_TOOLS_ENABLED", "true")
    monkeypatch.setenv("OMI_LIVE_BOOKNLP_ENABLED", "true")


def _install_mock_booknlp(
    monkeypatch: Any,
    *,
    entities: list[dict[str, str]] | None = None,
    quotes: list[dict[str, str]] | None = None,
    tokens: list[dict[str, str]] | None = None,
    raise_on_process: BaseException | None = None,
) -> None:
    """Install a mock ``booknlp.booknlp.BookNLP`` module.

    The mock writes fake ``.entities`` / ``.quotes`` / ``.tokens`` files
    into the temporary output directory so the live runner can parse them
    without invoking real BookNLP processing. Tests may pass empty
    lists to simulate ``empty`` / ``failed_closed`` output, or a
    ``raise_on_process`` exception to simulate a processing failure.
    """
    if entities is None:
        entities = []
    if quotes is None:
        quotes = []
    if tokens is None:
        tokens = []

    booknlp_pkg = MagicMock()
    booknlp_mod = MagicMock()

    class _MockBookNLP:
        def __init__(self, language: str, model_params: dict) -> None:
            self.language = language
            self.model_params = model_params

        def process(self, input_file: str, output_dir: str, book_id: str) -> None:
            if raise_on_process is not None:
                raise raise_on_process
            if entities:
                with open(
                    f"{output_dir}/{book_id}.entities", "w", encoding="utf-8"
                ) as handle:
                    handle.write(
                        "COREF\tstart_token\tend_token\tprop\tcat\ttext\n"
                    )
                    for row in entities:
                        handle.write(
                            "\t".join(
                                [
                                    str(row.get("COREF", "")),
                                    str(row.get("start_token", "")),
                                    str(row.get("end_token", "")),
                                    str(row.get("prop", "")),
                                    str(row.get("cat", "")),
                                    str(row.get("text", "")),
                                ]
                            )
                            + "\n"
                        )
            if quotes:
                with open(
                    f"{output_dir}/{book_id}.quotes", "w", encoding="utf-8"
                ) as handle:
                    handle.write(
                        "\t".join(
                            [
                                "quote_start",
                                "quote_end",
                                "mention_start",
                                "mention_end",
                                "mention_phrase",
                                "char_id",
                                "quote",
                            ]
                        )
                        + "\n"
                    )
                    for row in quotes:
                        handle.write(
                            "\t".join(
                                [
                                    str(row.get("quote_start", "")),
                                    str(row.get("quote_end", "")),
                                    str(row.get("mention_start", "")),
                                    str(row.get("mention_end", "")),
                                    str(row.get("mention_phrase", "")),
                                    str(row.get("char_id", "")),
                                    str(row.get("quote", "")),
                                ]
                            )
                            + "\n"
                        )
            if tokens:
                with open(
                    f"{output_dir}/{book_id}.tokens", "w", encoding="utf-8"
                ) as handle:
                    handle.write(
                        "\t".join(
                            [
                                "paragraph_ID",
                                "sentence_ID",
                                "token_ID_within_sentence",
                                "token_ID_within_document",
                                "word",
                                "lemma",
                                "byte_onset",
                                "byte_offset",
                                "POS_tag",
                                "fine_POS_tag",
                                "dependency_relation",
                                "syntactic_head_ID",
                                "event",
                            ]
                        )
                        + "\n"
                    )
                    for row in tokens:
                        handle.write(
                            "\t".join(
                                [
                                    str(row.get("paragraph_ID", "")),
                                    str(row.get("sentence_ID", "")),
                                    str(row.get("token_ID_within_sentence", "")),
                                    str(row.get("token_ID_within_document", "")),
                                    str(row.get("word", "")),
                                    str(row.get("lemma", "")),
                                    str(row.get("byte_onset", "")),
                                    str(row.get("byte_offset", "")),
                                    str(row.get("POS_tag", "")),
                                    str(row.get("fine_POS_tag", "")),
                                    str(row.get("dependency_relation", "")),
                                    str(row.get("syntactic_head_ID", "")),
                                    str(row.get("event", "")),
                                ]
                            )
                            + "\n"
                        )

    booknlp_mod.BookNLP = _MockBookNLP
    booknlp_pkg.booknlp = booknlp_mod

    monkeypatch.setitem(sys.modules, "booknlp", booknlp_pkg)
    monkeypatch.setitem(sys.modules, "booknlp.booknlp", booknlp_mod)


def test_live_booknlp_disabled_by_default_returns_unavailable() -> None:
    """No env flags -> live BookNLP path not triggered -> unavailable."""
    result = _run_adapter("booknlp")
    env = _assert_failed_closed(result, "booknlp")
    assert env["state"] == "unavailable"


def test_live_booknlp_blocked_overrides_enabled_returns_no_live_call(
    monkeypatch: Any,
) -> None:
    """OMI_LIVE_BOOKNLP_BLOCKED wins over OMI_LIVE_BOOKNLP_ENABLED."""
    monkeypatch.setenv("OMI_LIVE_TOOLS_ENABLED", "true")
    monkeypatch.setenv("OMI_LIVE_BOOKNLP_ENABLED", "true")
    monkeypatch.setenv("OMI_LIVE_BOOKNLP_BLOCKED", "true")
    monkeypatch.setenv(
        "OMI_LIVE_BOOKNLP_BLOCKED_REASON", "Owner decision pending."
    )
    _install_mock_booknlp(
        monkeypatch,
        entities=[
            {
                "COREF": "1",
                "start_token": "0",
                "end_token": "1",
                "prop": "PROP",
                "cat": "PROP_PER",
                "text": "Mara Vale",
            }
        ],
    )

    result = _run_adapter("booknlp")
    env = _assert_failed_closed(result, "booknlp")
    assert env["state"] == "unavailable"
    assert "fixture" in env["explanation"].lower()
    assert "live booknlp" in env["explanation"].lower()


def test_live_booknlp_missing_package_returns_unavailable(
    monkeypatch: Any,
) -> None:
    """BookNLP package not installed -> runner returns unavailable."""
    _mock_live_booknlp_env(monkeypatch)

    # Ensure the lazy import inside the runner raises ImportError.
    booknlp_pkg = MagicMock()
    booknlp_mod = MagicMock()

    def _raise(*_args: Any, **_kwargs: Any) -> None:
        raise ImportError("simulated missing booknlp.booknlp")

    booknlp_mod.BookNLP = _raise
    booknlp_pkg.booknlp = booknlp_mod

    # Force ``from booknlp.booknlp import BookNLP`` to fail with ImportError.
    real_import = __builtins__["__import__"] if isinstance(
        __builtins__, dict
    ) else __builtins__.__import__

    def _fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "booknlp.booknlp" or name.startswith("booknlp.booknlp."):
            raise ImportError("simulated missing booknlp.booknlp")
        return real_import(name, *args, **kwargs)

    if isinstance(__builtins__, dict):
        monkeypatch.setitem(__builtins__, "__import__", _fake_import)
    else:
        monkeypatch.setattr(__builtins__, "__import__", _fake_import)

    result = _run_adapter("booknlp")
    env = _assert_failed_closed(result, "booknlp")
    assert env["state"] == "unavailable"
    assert "not installed" in env["explanation"].lower()


def test_live_booknlp_runtime_exception_fails_closed(
    monkeypatch: Any,
) -> None:
    """BookNLP.process raises -> runner returns failed_closed."""
    _mock_live_booknlp_env(monkeypatch)
    _install_mock_booknlp(
        monkeypatch, raise_on_process=RuntimeError("simulated failure")
    )

    result = _run_adapter("booknlp")
    env = _assert_failed_closed(result, "booknlp")
    assert env["state"] in {"unavailable", "failed_closed"}
    assert "processing" in env["explanation"].lower() or "error" in (
        env["explanation"].lower()
    )


def test_live_booknlp_empty_output_fails_closed(
    monkeypatch: Any,
) -> None:
    """BookNLP produced no .entities/.quotes -> empty state, no findings."""
    _mock_live_booknlp_env(monkeypatch)
    _install_mock_booknlp(monkeypatch)

    result = _run_adapter("booknlp")
    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    env = _adapter_env(result, "booknlp")
    assert env["state"] in {"empty", "failed_closed"}
    assert env["candidates"] == []


def test_live_booknlp_malformed_entities_fails_closed(
    monkeypatch: Any,
) -> None:
    """Malformed BookNLP .entities output -> failed_closed, no findings."""
    _mock_live_booknlp_env(monkeypatch)

    booknlp_pkg = MagicMock()
    booknlp_mod = MagicMock()

    class _MalformedBookNLP:
        def __init__(self, language: str, model_params: dict) -> None:
            pass

        def process(self, input_file: str, output_dir: str, book_id: str) -> None:
            with open(
                f"{output_dir}/{book_id}.entities", "w", encoding="utf-8"
            ) as handle:
                # Header only — no data rows; the live runner treats this
                # as no entities, so the adapter fails closed.
                handle.write("COREF\tstart_token\tend_token\n")
            with open(
                f"{output_dir}/{book_id}.tokens", "w", encoding="utf-8"
            ) as handle:
                handle.write(
                    "paragraph_ID\tsentence_ID\ttoken_ID_within_sentence\t"
                    "token_ID_within_document\tword\tlemma\tbyte_onset\t"
                    "byte_offset\tPOS_tag\tfine_POS_tag\tdependency_relation\t"
                    "syntactic_head_ID\tevent\n"
                )

    booknlp_mod.BookNLP = _MalformedBookNLP
    booknlp_pkg.booknlp = booknlp_mod

    monkeypatch.setitem(sys.modules, "booknlp", booknlp_pkg)
    monkeypatch.setitem(sys.modules, "booknlp.booknlp", booknlp_mod)

    result = _run_adapter("booknlp")
    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    env = _adapter_env(result, "booknlp")
    assert env["state"] in {"empty", "failed_closed"}
    assert env["candidates"] == []


def test_live_booknlp_unsafe_entity_category_skipped_or_failed_closed(
    monkeypatch: Any,
) -> None:
    """Unsafe entity categories (truth/canon/approved/etc.) are skipped.

    Only safe PER/GPE/LOC/FAC/ORG/VEH-style categories survive; everything
    else is dropped at the parser or converter level. When no safe rows
    remain, the adapter returns ``empty`` / ``failed_closed`` with no
    findings and never sanitizes the unsafe text into a safe claim.
    """
    _mock_live_booknlp_env(monkeypatch)
    _install_mock_booknlp(
        monkeypatch,
        entities=[
            {
                "COREF": "1",
                "start_token": "0",
                "end_token": "1",
                "prop": "PROP",
                "cat": "approved_canon_per",  # unsafe category token
                "text": "Mara Vale",
            }
        ],
    )

    result = _run_adapter("booknlp")
    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    env = _adapter_env(result, "booknlp")
    assert env["state"] in {"empty", "failed_closed"}
    assert env["candidates"] == []


def test_live_booknlp_entities_become_candidate_only_findings(
    monkeypatch: Any,
) -> None:
    """Parsed .entities rows become evidence-backed candidate findings."""
    _mock_live_booknlp_env(monkeypatch)
    _install_mock_booknlp(
        monkeypatch,
        entities=[
            {
                "COREF": "1",
                "start_token": "0",
                "end_token": "1",
                "prop": "PROP",
                "cat": "PROP_PER",
                "text": "Mara Vale",
            },
            {
                "COREF": "2",
                "start_token": "4",
                "end_token": "6",
                "prop": "PROP",
                "cat": "PROP_LOC",
                "text": "Harbor Archive",
            },
            {
                "COREF": "3",
                "start_token": "10",
                "end_token": "11",
                "prop": "PROP",
                "cat": "PROP_ORG",
                "text": "Storm Watch",
            },
        ],
        tokens=[
            {
                "paragraph_ID": "0",
                "sentence_ID": "0",
                "token_ID_within_sentence": "0",
                "token_ID_within_document": "0",
                "word": "Mara",
                "lemma": "Mara",
                "byte_onset": "12",
                "byte_offset": "16",
                "POS_tag": "NNP",
                "fine_POS_tag": "NNP",
                "dependency_relation": "nsubj",
                "syntactic_head_ID": "1",
                "event": "O",
            },
            {
                "paragraph_ID": "0",
                "sentence_ID": "0",
                "token_ID_within_sentence": "1",
                "token_ID_within_document": "1",
                "word": "Vale",
                "lemma": "Vale",
                "byte_onset": "17",
                "byte_offset": "21",
                "POS_tag": "NNP",
                "fine_POS_tag": "NNP",
                "dependency_relation": "flat",
                "syntactic_head_ID": "0",
                "event": "O",
            },
            {
                "paragraph_ID": "0",
                "sentence_ID": "0",
                "token_ID_within_sentence": "4",
                "token_ID_within_document": "4",
                "word": "Harbor",
                "lemma": "Harbor",
                "byte_onset": "28",
                "byte_offset": "34",
                "POS_tag": "NNP",
                "fine_POS_tag": "NNP",
                "dependency_relation": "compound",
                "syntactic_head_ID": "5",
                "event": "O",
            },
            {
                "paragraph_ID": "0",
                "sentence_ID": "0",
                "token_ID_within_sentence": "5",
                "token_ID_within_document": "5",
                "word": "Archive",
                "lemma": "Archive",
                "byte_onset": "35",
                "byte_offset": "42",
                "POS_tag": "NNP",
                "fine_POS_tag": "NNP",
                "dependency_relation": "nsubj",
                "syntactic_head_ID": "6",
                "event": "O",
            },
            {
                "paragraph_ID": "0",
                "sentence_ID": "0",
                "token_ID_within_sentence": "6",
                "token_ID_within_document": "6",
                "word": ".",
                "lemma": ".",
                "byte_onset": "42",
                "byte_offset": "43",
                "POS_tag": ".",
                "fine_POS_tag": ".",
                "dependency_relation": "punct",
                "syntactic_head_ID": "5",
                "event": "O",
            },
            {
                "paragraph_ID": "0",
                "sentence_ID": "1",
                "token_ID_within_sentence": "0",
                "token_ID_within_document": "10",
                "word": "Storm",
                "lemma": "Storm",
                "byte_onset": "80",
                "byte_offset": "86",
                "POS_tag": "NNP",
                "fine_POS_tag": "NNP",
                "dependency_relation": "compound",
                "syntactic_head_ID": "11",
                "event": "O",
            },
            {
                "paragraph_ID": "0",
                "sentence_ID": "1",
                "token_ID_within_sentence": "1",
                "token_ID_within_document": "11",
                "word": "Watch",
                "lemma": "Watch",
                "byte_onset": "87",
                "byte_offset": "92",
                "POS_tag": "NNP",
                "fine_POS_tag": "NNP",
                "dependency_relation": "nsubj",
                "syntactic_head_ID": "12",
                "event": "O",
            },
        ],
    )

    result = _run_adapter("booknlp")

    assert result["analysis_status"] == "succeeded"
    env = _adapter_env(result, "booknlp")
    assert env["state"] == "succeeded"
    types = [f["candidate_type"] for f in env["candidates"]]
    assert "character" in types
    assert "location" in types
    assert "organization" in types
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "booknlp")


def test_live_booknlp_quotes_become_dialogue_attribution_candidates(
    monkeypatch: Any,
) -> None:
    """Parsed .quotes rows become dialogue-attribution candidate findings."""
    _mock_live_booknlp_env(monkeypatch)
    _install_mock_booknlp(
        monkeypatch,
        quotes=[
            {
                "quote_start": "0",
                "quote_end": "3",
                "mention_start": "5",
                "mention_end": "5",
                "mention_phrase": "she",
                "char_id": "42",
                "quote": "we wait here",
            }
        ],
    )

    result = _run_adapter("booknlp")
    assert result["analysis_status"] == "succeeded"
    env = _adapter_env(result, "booknlp")
    assert env["state"] == "succeeded"
    types = [f["candidate_type"] for f in env["candidates"]]
    assert "diagnostic_question" in types
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "booknlp")
        assert "dialogue attribution" in finding["label"].lower() or (
            "dialogue attribution" in finding["extracted_claim"].lower()
        )


def test_live_booknlp_unsafe_excerpt_text_does_not_leak_into_findings(
    monkeypatch: Any,
) -> None:
    """Unsafe BookNLP output text must not be smuggled into findings.

    The runner does NOT rewrite unsafe text into a safe claim; it SKIPS
    unsafe rows. A row whose text contains a canon/approved label or
    rewrite/continue/draft language must not produce a finding.
    """
    _mock_live_booknlp_env(monkeypatch)
    _install_mock_booknlp(
        monkeypatch,
        entities=[
            {
                "COREF": "1",
                "start_token": "0",
                "end_token": "1",
                "prop": "PROP",
                "cat": "PROP_PER",
                "text": "approved canon Mara",
            },
            {
                "COREF": "2",
                "start_token": "2",
                "end_token": "3",
                "prop": "PROP",
                "cat": "PROP_LOC",
                "text": "rewrite here Harbor",
            },
        ],
    )

    result = _run_adapter("booknlp")
    env = _assert_failed_closed(result, "booknlp")
    assert env["state"] in {"empty", "failed_closed"}
    assert env["candidates"] == []
    for finding in result["findings"]:
        for forbidden in ("approved canon", "rewrite here", "rewrite:"):
            assert forbidden.lower() not in finding["label"].lower()
            assert forbidden.lower() not in finding["extracted_claim"].lower()
            assert forbidden.lower() not in finding["evidence"][0][
                "source_excerpt"
            ].lower()


def test_live_booknlp_does_not_mutate_or_persist_when_enabled(
    monkeypatch: Any,
) -> None:
    """Live BookNLP never mutates Memory/Canon, never persists, no prose."""
    import backend.project_manager as project_manager

    persist_calls: list[dict[str, Any]] = []

    def _spy_persist(*args: Any, **kwargs: Any) -> dict[str, Any]:
        persist_calls.append({"args": args, "kwargs": kwargs})
        return {
            "persisted_candidate_ids": [],
            "new_candidate_ids": [],
            "reused_candidate_ids": [],
            "persistence_status": "not_persisted",
            "persistence_explanation": "spy",
        }

    monkeypatch.setattr(
        project_manager,
        "persist_omi_tool_assisted_findings_as_candidates",
        _spy_persist,
    )

    _mock_live_booknlp_env(monkeypatch)
    _install_mock_booknlp(
        monkeypatch,
        entities=[
            {
                "COREF": "1",
                "start_token": "0",
                "end_token": "1",
                "prop": "PROP",
                "cat": "PROP_PER",
                "text": "Mara Vale",
            }
        ],
        tokens=[
            {
                "paragraph_ID": "0",
                "sentence_ID": "0",
                "token_ID_within_sentence": "0",
                "token_ID_within_document": "0",
                "word": "Mara",
                "lemma": "Mara",
                "byte_onset": "12",
                "byte_offset": "16",
                "POS_tag": "NNP",
                "fine_POS_tag": "NNP",
                "dependency_relation": "nsubj",
                "syntactic_head_ID": "1",
                "event": "O",
            },
            {
                "paragraph_ID": "0",
                "sentence_ID": "0",
                "token_ID_within_sentence": "1",
                "token_ID_within_document": "1",
                "word": "Vale",
                "lemma": "Vale",
                "byte_onset": "17",
                "byte_offset": "21",
                "POS_tag": "NNP",
                "fine_POS_tag": "NNP",
                "dependency_relation": "flat",
                "syntactic_head_ID": "0",
                "event": "O",
            },
        ],
    )

    result = _run_adapter("booknlp", persist_candidates=True)

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_story_prose_generation"] is True
    assert result["safety"]["no_canon_promotion"] is True

    for finding in result["findings"]:
        assert finding["owner_decision"]["approved"] is False
        assert finding["review_status"] == "candidate_review_pending"
        for forbidden in ("truth", "canon", "approved", "promoted"):
            assert forbidden not in finding["support_label"].lower()
        for forbidden_text in ("rewrite:", "continuation:", "outline:", "draft:"):
            assert forbidden_text not in finding["extracted_claim"].lower()


def test_live_booknlp_uses_env_model_and_pipeline_overrides(
    monkeypatch: Any,
) -> None:
    """Runner honors OMI_LIVE_BOOKNLP_MODEL/PIPELINE when safe and valid."""
    _mock_live_booknlp_env(monkeypatch)
    monkeypatch.setenv("OMI_LIVE_BOOKNLP_MODEL", "small")
    monkeypatch.setenv("OMI_LIVE_BOOKNLP_PIPELINE", "entity,quote,event")

    captured: dict[str, Any] = {}

    booknlp_pkg = MagicMock()
    booknlp_mod = MagicMock()

    class _CaptureBookNLP:
        def __init__(self, language: str, model_params: dict) -> None:
            captured["language"] = language
            captured["model_params"] = model_params

        def process(self, input_file: str, output_dir: str, book_id: str) -> None:
            captured["input_file"] = input_file
            captured["output_dir"] = output_dir
            captured["book_id"] = book_id

    booknlp_mod.BookNLP = _CaptureBookNLP
    booknlp_pkg.booknlp = booknlp_mod

    monkeypatch.setitem(sys.modules, "booknlp", booknlp_pkg)
    monkeypatch.setitem(sys.modules, "booknlp.booknlp", booknlp_mod)

    result = _run_adapter("booknlp")

    assert captured["language"] == "en"
    assert captured["model_params"]["model"] == "small"
    pipe_tokens = captured["model_params"]["pipeline"].split(",")
    assert "entity" in pipe_tokens
    assert "quote" in pipe_tokens
    assert "event" in pipe_tokens
    assert result["findings"] == []
    env = _adapter_env(result, "booknlp")
    assert env["state"] in {"empty", "failed_closed"}


def test_live_booknlp_invalid_model_env_falls_back_to_default(
    monkeypatch: Any,
) -> None:
    """Invalid OMI_LIVE_BOOKNLP_MODEL falls back to ``small`` safely."""
    _mock_live_booknlp_env(monkeypatch)
    monkeypatch.setenv("OMI_LIVE_BOOKNLP_MODEL", "unsafe_model_name")

    captured: dict[str, Any] = {}

    booknlp_pkg = MagicMock()
    booknlp_mod = MagicMock()

    class _CaptureBookNLP:
        def __init__(self, language: str, model_params: dict) -> None:
            captured["model_params"] = model_params

        def process(self, input_file: str, output_dir: str, book_id: str) -> None:
            pass

    booknlp_mod.BookNLP = _CaptureBookNLP
    booknlp_pkg.booknlp = booknlp_mod

    monkeypatch.setitem(sys.modules, "booknlp", booknlp_pkg)
    monkeypatch.setitem(sys.modules, "booknlp.booknlp", booknlp_mod)

    _run_adapter("booknlp")
    assert captured["model_params"]["model"] == "small"


def test_live_booknlp_existing_fixture_tests_still_pass() -> None:
    """Existing fixture tests still produce unavailable when no env flag set."""
    result = _run_adapter("booknlp")
    env = _assert_failed_closed(result, "booknlp")
    assert env["state"] == "unavailable"
    assert "fixture" in env["explanation"].lower()
    assert "live booknlp" in env["explanation"].lower()

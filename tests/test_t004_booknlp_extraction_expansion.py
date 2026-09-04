from __future__ import annotations

import copy
import hashlib
import json

import pytest

from backend import omi_analysis_orchestrator as orchestrator
from backend import project_manager
from backend.story_knowledge import analysis_run_control, booknlp_adapter_contract
from backend.story_knowledge.evidence_ledger import scan_evidence_ledger
from backend.story_knowledge.raw_artifacts import read_immutable_raw_artifact_bundle
from backend.story_knowledge.source_map import build_exact_source_snapshot


SOURCE = 'Éva opened the brass door. “Wait,” she told ACME at Dock Seven. Her Rover waited.'
CREATED_AT = "2026-09-04T19:30:00Z"


def _byte_span(text: str) -> tuple[int, int]:
    char_start = SOURCE.index(text)
    char_end = char_start + len(text)
    return (
        len(SOURCE[:char_start].encode("utf-8")),
        len(SOURCE[:char_end].encode("utf-8")),
    )


def _token(token_id: int, word: str, *, dependency: str = "dep", head: int = 0, event: str = "O") -> dict:
    byte_start, byte_end = _byte_span(word)
    return {
        "paragraph_ID": 0,
        "sentence_ID": 0,
        "token_ID_within_sentence": token_id,
        "token_ID_within_document": token_id,
        "word": word,
        "lemma": word.lower(),
        "byte_onset": byte_start,
        "byte_offset": byte_end,
        "POS_tag": "NNP" if word[:1].isupper() else "NN",
        "fine_POS_tag": "NNP" if word[:1].isupper() else "NN",
        "dependency_relation": dependency,
        "syntactic_head_ID": head,
        "event": event,
    }


def _rows() -> tuple[list[dict], list[dict], list[dict], list[dict], dict]:
    words = ["Éva", "opened", "brass", "door", "Wait", "she", "ACME", "Dock", "Seven", "Rover", "waited"]
    tokens = [
        _token(index, word, dependency=("ROOT" if word == "opened" else "dep"), head=(index if word == "opened" else 1), event=("EVENT" if word in {"opened", "waited"} else "O"))
        for index, word in enumerate(words)
    ]
    entities = [
        {"COREF": 1, "start_token": 0, "end_token": 0, "prop": "PROP", "cat": "PROP_PER", "text": "Éva"},
        {"COREF": 1, "start_token": 5, "end_token": 5, "prop": "PRON", "cat": "PRON_PER", "text": "she"},
        {"COREF": 2, "start_token": 6, "end_token": 6, "prop": "PROP", "cat": "PROP_ORG", "text": "ACME"},
        {"COREF": 3, "start_token": 7, "end_token": 8, "prop": "PROP", "cat": "PROP_FAC", "text": "Dock Seven"},
        {"COREF": 4, "start_token": 9, "end_token": 9, "prop": "PROP", "cat": "PROP_VEH", "text": "Rover"},
    ]
    quotes = [{
        "quote_start": 4,
        "quote_end": 4,
        "mention_start": 5,
        "mention_end": 5,
        "mention_phrase": "she",
        "char_id": 1,
        "quote": "Wait",
    }]
    supersense = [{
        "start_token": 2,
        "end_token": 3,
        "supersense_category": "noun.artifact",
        "text": "brass door",
    }]
    book = {
        "characters": [{
            "agent": ["opened"],
            "patient": [],
            "mod": [],
            "poss": ["Rover"],
            "id": 1,
            "g": {"she/her": 1},
            "count": 2,
            "mentions": {
                "proper": [{"c": "Éva", "n": 1}],
                "common": [],
                "pronoun": [{"c": "she", "n": 1}],
            },
        }]
    }
    return tokens, entities, quotes, supersense, book


def _tsv(header: tuple[str, ...], rows: list[dict]) -> str:
    return "\n".join([
        "\t".join(header),
        *["\t".join(str(row[field]) for field in header) for row in rows],
    ]) + "\n"


def _raw_payloads() -> dict[str, bytes]:
    tokens, entities, quotes, supersense, book = _rows()
    return {
        "tokens": _tsv(("paragraph_ID", "sentence_ID", "token_ID_within_sentence", "token_ID_within_document", "word", "lemma", "byte_onset", "byte_offset", "POS_tag", "fine_POS_tag", "dependency_relation", "syntactic_head_ID", "event"), tokens).encode(),
        "entities": _tsv(("COREF", "start_token", "end_token", "prop", "cat", "text"), entities).encode(),
        "quotes": _tsv(("quote_start", "quote_end", "mention_start", "mention_end", "mention_phrase", "char_id", "quote"), quotes).encode(),
        "supersense": _tsv(("start_token", "end_token", "supersense_category", "text"), supersense).encode(),
        "book": json.dumps(book, ensure_ascii=False, sort_keys=True).encode(),
    }


def _snapshot():
    return build_exact_source_snapshot(
        project_id="example",
        source_document_type="omi",
        source_document_id="idea-t004",
        source_document_version="1",
        source_ownership="owner_authored",
        source_content=SOURCE,
    )


def _adapter_result() -> dict:
    tokens, entities, quotes, supersense, book = _rows()
    envelope = orchestrator._booknlp_t004_result_to_envelope(
        project_name="example",
        source_idea_id="idea-t004",
        source_content=SOURCE,
        tokens=tokens,
        entities=entities,
        quotes=quotes,
        supersense=supersense,
        book_json=book,
    )
    validated = orchestrator.validate_local_nlp_fixture_envelope(envelope, adapter_name="booknlp")
    handoff = booknlp_adapter_contract.build_booknlp_raw_artifact_handoff(
        snapshot=_snapshot(),
        files=_raw_payloads(),
        tool_version="fixture-1.0.8",
        runtime_name="python",
        runtime_version="3.fixture",
        model_name="small",
        pipeline="entity,quote,supersense,event",
        mapping_limitations=envelope.get("diagnostics", []),
    )
    return {
        "adapter": "booknlp",
        "state": "succeeded",
        "explanation": validated["explanation"],
        "candidates": validated["findings"],
        "raw_artifacts": handoff,
    }


def test_exact_multibyte_offsets_and_expanded_support_mappings() -> None:
    result = _adapter_result()
    findings = result["candidates"]
    eva = next(item for item in findings if item["label"] == "Éva")
    evidence = eva["evidence"][0]
    assert (evidence["char_start"], evidence["char_end"]) == (0, 3)
    assert (evidence["byte_start"], evidence["byte_end"]) == (0, 4)
    assert evidence["source_excerpt"] == "Éva"
    assert evidence["artifact_file_id"] == "booknlp-entities"

    types = {item["candidate_type"] for item in findings}
    assert {"character", "organization", "location", "object", "relationship", "timeline_event", "evidence_note"} <= types
    coref = next(item for item in findings if item["support_metadata"].get("signal_kind") == "coreference")
    assert coref["uncertainty_label"] == "booknlp_coreference_ambiguous"
    assert coref["support_metadata"]["candidate_mentions"] == ["she", "Éva"]
    quote = next(item for item in findings if item["support_metadata"].get("signal_kind") == "quote_attribution")
    assert quote["uncertainty_label"] == "booknlp_speaker_attribution_uncertain"
    assert {item["evidence_role"] for item in quote["evidence"]} == {"quote_span", "speaker_mention_span"}
    event = next(item for item in findings if item["candidate_type"] == "timeline_event")
    assert event["support_metadata"]["derivation"] == "app_owned_from_booknlp_token_event_marker"
    assert event["evidence"][0]["artifact_file_id"] == "booknlp-tokens"
    dependency = next(item for item in findings if item["support_metadata"].get("signal_kind") == "token_dependency")
    assert {"dependency_relation", "syntactic_head_ID", "event", "lemma", "POS_tag"} <= dependency["support_metadata"].keys()
    assert any(item["support_metadata"].get("supersense_category") == "noun.artifact" for item in findings)
    assert any(item["support_metadata"].get("booknlp_entity_class") == "FAC" for item in findings)
    assert any(item["support_metadata"].get("booknlp_entity_class") == "VEH" for item in findings)
    assert not any(item["support_metadata"].get("signal_kind") == "possession" for item in findings)
    assert all(item["owner_decision"] == {"decision": "pending", "approved": False} for item in findings)


def test_unsupported_entity_class_is_not_mapped_and_limitation_is_explicit() -> None:
    tokens, entities, quotes, supersense, book = _rows()
    entities = [{**entities[0], "cat": "PROP_MISC"}]
    envelope = orchestrator._booknlp_t004_result_to_envelope(
        project_name="example",
        source_idea_id="idea-t004",
        source_content=SOURCE,
        tokens=tokens,
        entities=entities,
        quotes=quotes,
        supersense=supersense,
        book_json=book,
    )
    assert "unsupported_entity_class:MISC" in envelope["diagnostics"]
    assert not any(
        item["support_metadata"].get("signal_kind") == "entity_mention"
        for item in envelope["findings"]
    )


def test_unresolved_coreference_sentinel_never_creates_an_identity_cluster() -> None:
    tokens, entities, quotes, supersense, book = _rows()
    entities = [
        {**entities[0], "COREF": -1},
        {**entities[1], "COREF": -1},
    ]
    envelope = orchestrator._booknlp_t004_result_to_envelope(
        project_name="example",
        source_idea_id="idea-t004",
        source_content=SOURCE,
        tokens=tokens,
        entities=entities,
        quotes=quotes,
        supersense=supersense,
        book_json=book,
    )
    entity_findings = [
        item
        for item in envelope["findings"]
        if item["support_metadata"].get("signal_kind") == "entity_mention"
    ]
    assert all(
        item["support_metadata"]["identity_resolution"] == "unresolved_by_booknlp"
        for item in entity_findings
    )
    assert not any(
        item["support_metadata"].get("signal_kind") == "coreference"
        for item in envelope["findings"]
    )


@pytest.mark.parametrize(
    "mutator",
    [
        lambda rows: rows[0].update(byte_offset=1),
        lambda rows: rows[0].update(byte_onset=10_000, byte_offset=10_001),
        lambda rows: rows[0].update(char_start=1, char_end=3),
        lambda rows: rows[0].update(word="not-the-source-token"),
    ],
)
def test_unprovable_or_inconsistent_token_offsets_fail_closed(mutator) -> None:
    tokens, entities, quotes, supersense, book = _rows()
    mutator(tokens)
    with pytest.raises(ValueError):
        orchestrator._booknlp_t004_result_to_envelope(
            project_name="example",
            source_idea_id="idea-t004",
            source_content=SOURCE,
            tokens=tokens,
            entities=entities,
            quotes=quotes,
            supersense=supersense,
            book_json=book,
        )


def test_handoff_is_exact_hash_bound_and_never_invents_events_artifact() -> None:
    handoff = _adapter_result()["raw_artifacts"]
    assert handoff["adapter_id"] == "booknlp"
    assert handoff["source_identity"]["content_hash"] == hashlib.sha256(SOURCE.encode()).hexdigest()
    assert {item["artifact_file_id"] for item in handoff["files"]} == {
        "booknlp-tokens", "booknlp-entities", "booknlp-quotes", "booknlp-supersense", "booknlp-book"
    }
    assert not any("event" in item["artifact_file_id"] for item in handoff["files"])
    assert "possession_book_summary_has_no_exact_span_and_is_not_normalized" in handoff["mapping_limitations"]
    tampered = copy.deepcopy(handoff)
    tampered["files"][0]["payload"] += "tampered"
    with pytest.raises(ValueError, match="hash|size"):
        booknlp_adapter_contract.validate_booknlp_raw_artifact_handoff(tampered)


def test_t003_publication_manifest_ledger_replay_and_tamper(monkeypatch, tmp_path) -> None:
    projects = tmp_path / "projects"
    project = projects / "example"
    project.mkdir(parents=True)
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", projects)
    monkeypatch.setattr(project_manager, "REPO_ROOT", tmp_path)
    calls = 0

    def runner(*args, **kwargs):
        nonlocal calls
        calls += 1
        result = _adapter_result()
        return {
            "analysis_status": "succeeded",
            "explanation": "BookNLP fixture evidence completed",
            "source_idea_id": kwargs.get("source_idea_id"),
            "adapter_results": [result],
            "findings": result["candidates"],
            "persisted_candidate_ids": [],
            "safety": {"no_prose": True, "no_memory_canon_mutation": True, "no_apply_promotion": True},
        }

    submitted = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea=SOURCE,
        source_idea_id="idea-t004",
        requested_adapters=["booknlp"],
        idempotency_key="t004-fixture",
        runner=runner,
        created_at=CREATED_AT,
    )
    run_id = submitted["run_id"]
    persisted = read_immutable_raw_artifact_bundle(
        "example", submitted["raw_artifact_ref"]["artifact_id"], project_dir=tmp_path
    )
    raw_ids = {item["artifact_file_id"] for item in persisted["artifact_files"]}
    assert {"source-artifact", "result-artifact", "booknlp-tokens", "booknlp-entities", "booknlp-quotes", "booknlp-supersense", "booknlp-book"} <= raw_ids
    manifest_path = project / "writer_assistant" / "analysis_runs" / run_id / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest_ids = {item["artifact_id"] for item in manifest["artifact_references"]}
    assert {"booknlp-tokens", "booknlp-entities", "booknlp-quotes", "booknlp-supersense", "booknlp-book"} <= manifest_ids
    chain = scan_evidence_ledger(project_dir=project, project_id="example", run_id=run_id)
    output_evidence = [event["payload"] for event in chain if event["event_type"] == "evidence_recorded" and event["payload"]["output_id"]]
    assert any(item["artifact_file_id"].startswith("booknlp-") for item in output_evidence)
    replay = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea=SOURCE,
        source_idea_id="idea-t004",
        requested_adapters=["booknlp"],
        idempotency_key="t004-fixture",
        runner=runner,
    )
    assert replay["idempotent_replay"] is True
    assert calls == 1
    raw_path = tmp_path / "projects" / "example" / "writer_assistant" / "raw_artifacts" / submitted["raw_artifact_ref"]["artifact_id"] / "artifacts" / "booknlp" / "tokens.tsv"
    raw_path.write_bytes(raw_path.read_bytes() + b"tampered")
    with pytest.raises(ValueError):
        read_immutable_raw_artifact_bundle("example", submitted["raw_artifact_ref"]["artifact_id"], project_dir=tmp_path)
    assert submitted["candidate_persistence_performed"] is False
    assert submitted["automatic_approval_or_promotion_performed"] is False
    assert submitted["memory_canon_mutation_performed"] is False
    assert submitted["story_prose_generated"] is False


def test_source_or_artifact_mismatch_fails_before_publication(monkeypatch, tmp_path) -> None:
    projects = tmp_path / "projects"
    (projects / "example").mkdir(parents=True)
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", projects)
    monkeypatch.setattr(project_manager, "REPO_ROOT", tmp_path)
    result = _adapter_result()
    result["raw_artifacts"]["source_identity"]["content_hash"] = "0" * 64

    def runner(*args, **kwargs):
        return {
            "analysis_status": "succeeded",
            "explanation": "mismatched fixture",
            "source_idea_id": kwargs.get("source_idea_id"),
            "adapter_results": [result],
            "findings": result["candidates"],
            "persisted_candidate_ids": [],
            "safety": {"no_prose": True, "no_memory_canon_mutation": True, "no_apply_promotion": True},
        }

    with pytest.raises(ValueError, match="source|hash"):
        analysis_run_control.submit_analysis_run(
            "example",
            raw_idea=SOURCE,
            source_idea_id="idea-t004",
            requested_adapters=["booknlp"],
            runner=runner,
            created_at=CREATED_AT,
        )
    assert not any((projects / "example").rglob("manifest.json"))

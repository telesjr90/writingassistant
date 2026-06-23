"""Contract tests for future raw extraction artifact storage helpers.

PHASE8-IMPL-008-T003 is tests-first only. The future pure storage module is
imported normally so this targeted file is expected red until T004 creates it:
- backend.story_knowledge.raw_extraction_storage

Fixtures are synthetic, in-memory dictionaries and tmp_path paths only. These
tests do not install, import, or run BookNLP/spaCy and do not write real project
raw extraction artifacts.
"""

from copy import deepcopy
from pathlib import Path

import pytest

from backend.story_knowledge import evidence
from backend.story_knowledge import raw_extraction_storage

PROJECT_ID = "example"
TOOL_NAME = "booknlp"
RUN_ID = "run_20260620_001"
SNAPSHOT_HASH = "sha256:snapshot-001"
SOURCE_HASH = "sha256:source-doc-001"

EXPECTED_PUBLIC_API = (
    "validate_extraction_storage_id",
    "extraction_storage_dir",
    "tool_extraction_dir",
    "extraction_run_dir",
    "extraction_manifest_path",
    "raw_artifact_dir",
    "raw_artifact_path",
    "derived_artifact_dir",
    "validate_extraction_storage_path",
    "validate_extraction_run_manifest",
)

SAFE_STORAGE_IDS = (
    "booknlp",
    "run_20260620_001",
    "booknlp-fixture-001",
    "manual_fixture_import",
)

UNSAFE_STORAGE_IDS = (
    "",
    "   ",
    ".",
    "..",
    "safe..unsafe",
    "folder/name",
    "folder\\name",
    "/absolute",
    "C:\\temp",
    "../outside",
    "booknlp/evil",
    "run.json",
    "run.tsv",
    "run.html",
    "run.txt",
)

ACCEPTED_RAW_ARTIFACT_NAMES = (
    "tokens.tsv",
    "entities.tsv",
    "quotes.tsv",
    "supersense.tsv",
    "book.json",
    "book.html",
)

ACCEPTED_RAW_ARTIFACT_KINDS = (
    "booknlp_tokens",
    "booknlp_entities",
    "booknlp_quotes",
    "booknlp_supersense",
    "booknlp_book_json",
    "booknlp_book_html",
)

ACCEPTED_DERIVED_ARTIFACT_KINDS = ("booknlp_events_derived",)

REJECTED_ARTIFACT_NAMES = (
    "../tokens.tsv",
    "/tmp/tokens.tsv",
    "raw/tokens.tsv",
    "candidates.json",
    "index.json",
    "bible.json",
    "storyform.json",
    "project.json",
    "memory.json",
    "canon.json",
    ".env",
    "package.json",
    "dataset_manifest.json",
)

REJECTED_ARTIFACT_KINDS = (
    "booknlp_events",
    "candidate_json",
    "canon_json",
    "memory_json",
    "storyform_truth",
    "generated_prose",
)

FORBIDDEN_LOCATION_PARTS = frozenset(
    {
        "candidates",
        "index.json",
        "memory",
        "canon",
        "bible.json",
        "storyform.json",
        "project.json",
        "scenes",
        "notes",
        "materials",
        "omi",
        "training",
        ".external_sources",
        "package.json",
        "requirements.txt",
        "dataset_manifest.json",
    }
)

FORBIDDEN_MANIFEST_FIELDS = (
    "candidate_records",
    "canon_records",
    "memory_records",
    "candidate_ids_to_create",
    "write_to_canon",
    "mutate_memory",
    "apply_promotion",
    "generated_prose",
    "storyform_truth",
)

FORBIDDEN_PRODUCTION_SOURCE_TERMS = (
    "booknlp import",
    "from booknlp",
    "spacy.load",
    "ollama",
    "openai",
    "requests",
    "httpx",
    "fastapi",
    "uvicorn",
    "subprocess",
    "Path(",
    "open(",
    ".write_text",
    ".mkdir",
    "training",
    "dataset_manifest",
    "jsonl",
    "generated_prose",
    "rewrite",
    "continuation",
    "write_to_canon",
    "mutate_memory",
    "apply_promotion",
    "world_state",
    "storyform_truth",
)


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "my-project"


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def build_valid_source_document_ref(**overrides):
    ref = {
        "project_id": PROJECT_ID,
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "source_document_version": "1",
        "source_label": "Opening scene",
        "source_path_hint": "scenes/scene_001.md",
        "content_hash": SOURCE_HASH,
        "content_hash_algorithm": "sha256",
        "created_at": "2026-06-20T00:00:00Z",
        "updated_at": "2026-06-20T00:00:00Z",
    }
    ref.update(overrides)
    return ref


def build_raw_artifact_ref(
    artifact_name="tokens.tsv",
    artifact_kind="booknlp_tokens",
    **overrides,
):
    ref = {
        "raw_output_id": f"raw_{artifact_kind}",
        "project_id": PROJECT_ID,
        "tool_name": TOOL_NAME,
        "run_id": RUN_ID,
        "artifact_name": artifact_name,
        "artifact_kind": artifact_kind,
        "artifact_path_hint": f"writer_assistant/extractions/booknlp/{RUN_ID}/raw/{artifact_name}",
        "artifact_hash": f"sha256:{artifact_name}",
        "artifact_hash_algorithm": "sha256",
        "created_at": "2026-06-20T00:00:00Z",
        "source_snapshot_hashes": [SNAPSHOT_HASH],
        "is_canon": False,
        "is_candidate": False,
    }
    ref.update(overrides)
    return ref


def build_derived_artifact_ref(**overrides):
    ref = {
        "raw_output_id": "derived_booknlp_events",
        "project_id": PROJECT_ID,
        "tool_name": TOOL_NAME,
        "run_id": RUN_ID,
        "artifact_name": "events.json",
        "artifact_kind": "booknlp_events_derived",
        "artifact_path_hint": f"writer_assistant/extractions/booknlp/{RUN_ID}/derived/events.json",
        "artifact_hash": "sha256:events",
        "artifact_hash_algorithm": "sha256",
        "created_at": "2026-06-20T00:00:00Z",
        "source_snapshot_hashes": [SNAPSHOT_HASH],
        "is_canon": False,
        "is_candidate": False,
    }
    ref.update(overrides)
    return ref


def build_valid_manifest(**overrides):
    manifest = {
        "run_id": RUN_ID,
        "project_id": PROJECT_ID,
        "tool_name": TOOL_NAME,
        "tool_version": "fixture",
        "adapter_name": "writer_assistant_raw_extraction_storage",
        "adapter_version": "contract",
        "run_type": "booknlp_fixture_parse",
        "status": "complete",
        "source_documents": [build_valid_source_document_ref()],
        "source_snapshot_hashes": [SNAPSHOT_HASH],
        "storage_root": "writer_assistant/extractions",
        "run_dir": f"writer_assistant/extractions/booknlp/{RUN_ID}",
        "raw_artifacts": [
            build_raw_artifact_ref("tokens.tsv", "booknlp_tokens"),
            build_raw_artifact_ref("entities.tsv", "booknlp_entities"),
            build_raw_artifact_ref("quotes.tsv", "booknlp_quotes"),
            build_raw_artifact_ref("supersense.tsv", "booknlp_supersense"),
            build_raw_artifact_ref("book.json", "booknlp_book_json"),
            build_raw_artifact_ref("book.html", "booknlp_book_html"),
        ],
        "derived_artifacts": [build_derived_artifact_ref()],
        "artifact_hashes": {
            "raw/tokens.tsv": "sha256:tokens",
            "raw/entities.tsv": "sha256:entities",
            "raw/quotes.tsv": "sha256:quotes",
            "raw/supersense.tsv": "sha256:supersense",
            "raw/book.json": "sha256:book-json",
            "raw/book.html": "sha256:book-html",
            "derived/events.json": "sha256:events",
        },
        "created_at": "2026-06-20T00:00:00Z",
        "updated_at": "2026-06-20T00:00:00Z",
        "parameters": {},
        "environment": {},
        "warnings": [],
        "errors": [],
        "human_review_required": True,
        "candidate_generation_allowed": False,
        "canon_write_allowed": False,
        "prose_generation_allowed": False,
    }
    manifest.update(overrides)
    return manifest


def assert_no_extraction_side_effects(project: Path) -> None:
    writer_assistant = project / "writer_assistant"
    extractions = writer_assistant / "extractions"
    run = extractions / TOOL_NAME / RUN_ID

    assert not project.exists()
    assert not writer_assistant.exists()
    assert not extractions.exists()
    assert not (extractions / TOOL_NAME).exists()
    assert not run.exists()
    assert not (run / "raw").exists()
    assert not (run / "derived").exists()
    assert not (run / "manifest.json").exists()
    assert not (run / "raw" / "tokens.tsv").exists()
    assert not (writer_assistant / "candidates").exists()
    assert not (writer_assistant / "index.json").exists()
    assert not (writer_assistant / "memory").exists()
    assert not (writer_assistant / "canon").exists()


def test_future_public_api_symbols_are_present():
    for name in EXPECTED_PUBLIC_API:
        assert hasattr(raw_extraction_storage, name), name


def test_storage_root_path_helpers_derive_project_local_extraction_paths(tmp_path):
    project = project_dir(tmp_path)

    storage_root = raw_extraction_storage.extraction_storage_dir(project)
    tool_root = raw_extraction_storage.tool_extraction_dir(project, TOOL_NAME)
    run_root = raw_extraction_storage.extraction_run_dir(
        project, TOOL_NAME, RUN_ID
    )

    assert storage_root == project / "writer_assistant" / "extractions"
    assert tool_root == storage_root / "booknlp"
    assert run_root == tool_root / RUN_ID
    assert raw_extraction_storage.extraction_manifest_path(
        project, TOOL_NAME, RUN_ID
    ) == run_root / "manifest.json"
    assert raw_extraction_storage.raw_artifact_dir(
        project, TOOL_NAME, RUN_ID
    ) == run_root / "raw"
    assert raw_extraction_storage.raw_artifact_path(
        project, TOOL_NAME, RUN_ID, "tokens.tsv"
    ) == run_root / "raw" / "tokens.tsv"
    assert raw_extraction_storage.derived_artifact_dir(
        project, TOOL_NAME, RUN_ID
    ) == run_root / "derived"

    assert_no_extraction_side_effects(project)


@pytest.mark.parametrize("safe_id", SAFE_STORAGE_IDS)
def test_validate_extraction_storage_id_accepts_safe_ids(safe_id):
    assert raw_extraction_storage.validate_extraction_storage_id(
        safe_id, field_name="run_id"
    ) == safe_id


@pytest.mark.parametrize("unsafe_id", UNSAFE_STORAGE_IDS)
def test_validate_extraction_storage_id_rejects_unsafe_ids(unsafe_id):
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_storage_id(
            unsafe_id, field_name="run_id"
        )


@pytest.mark.parametrize("unsafe_tool_name", UNSAFE_STORAGE_IDS)
def test_path_helpers_reject_unsafe_tool_names(tmp_path, unsafe_tool_name):
    project = project_dir(tmp_path)
    with pytest.raises(ValueError):
        raw_extraction_storage.tool_extraction_dir(project, unsafe_tool_name)
    with pytest.raises(ValueError):
        raw_extraction_storage.extraction_run_dir(
            project, unsafe_tool_name, RUN_ID
        )
    assert_no_extraction_side_effects(project)


@pytest.mark.parametrize("unsafe_run_id", UNSAFE_STORAGE_IDS)
def test_path_helpers_reject_unsafe_run_ids(tmp_path, unsafe_run_id):
    project = project_dir(tmp_path)
    with pytest.raises(ValueError):
        raw_extraction_storage.extraction_run_dir(
            project, TOOL_NAME, unsafe_run_id
        )
    with pytest.raises(ValueError):
        raw_extraction_storage.extraction_manifest_path(
            project, TOOL_NAME, unsafe_run_id
        )
    assert_no_extraction_side_effects(project)


@pytest.mark.parametrize("artifact_name", ACCEPTED_RAW_ARTIFACT_NAMES)
def test_raw_artifact_path_accepts_booknlp_raw_filenames(tmp_path, artifact_name):
    project = project_dir(tmp_path)
    path = raw_extraction_storage.raw_artifact_path(
        project, TOOL_NAME, RUN_ID, artifact_name
    )
    raw_dir = project / "writer_assistant" / "extractions" / TOOL_NAME / RUN_ID / "raw"
    assert path == raw_dir / artifact_name
    assert is_relative_to(path, raw_dir)
    assert_no_extraction_side_effects(project)


@pytest.mark.parametrize("artifact_name", REJECTED_ARTIFACT_NAMES)
def test_raw_artifact_path_rejects_forbidden_or_nested_artifact_names(
    tmp_path, artifact_name
):
    project = project_dir(tmp_path)
    with pytest.raises(ValueError):
        raw_extraction_storage.raw_artifact_path(
            project, TOOL_NAME, RUN_ID, artifact_name
        )
    assert_no_extraction_side_effects(project)


def test_storage_path_validation_remains_inside_extractions_tree(tmp_path):
    project = project_dir(tmp_path)
    extraction_root = project / "writer_assistant" / "extractions"

    paths = (
        raw_extraction_storage.extraction_storage_dir(project),
        raw_extraction_storage.tool_extraction_dir(project, TOOL_NAME),
        raw_extraction_storage.extraction_run_dir(project, TOOL_NAME, RUN_ID),
        raw_extraction_storage.extraction_manifest_path(
            project, TOOL_NAME, RUN_ID
        ),
        raw_extraction_storage.raw_artifact_dir(project, TOOL_NAME, RUN_ID),
        raw_extraction_storage.raw_artifact_path(
            project, TOOL_NAME, RUN_ID, "tokens.tsv"
        ),
        raw_extraction_storage.derived_artifact_dir(
            project, TOOL_NAME, RUN_ID
        ),
        raw_extraction_storage.validate_extraction_storage_path(
            project, TOOL_NAME, RUN_ID, "tokens.tsv"
        ),
    )

    for path in paths:
        assert is_relative_to(path, extraction_root)
        assert ".external_sources" not in path.parts
        assert "projects" not in path.parts or is_relative_to(path, project)
    assert_no_extraction_side_effects(project)


@pytest.mark.parametrize("artifact_name", REJECTED_ARTIFACT_NAMES)
def test_storage_path_validation_rejects_artifact_traversal_and_forbidden_targets(
    tmp_path, artifact_name
):
    project = project_dir(tmp_path)
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_storage_path(
            project, TOOL_NAME, RUN_ID, artifact_name
        )
    assert_no_extraction_side_effects(project)


def test_storage_helpers_never_target_forbidden_project_locations(tmp_path):
    project = project_dir(tmp_path)
    allowed_paths = (
        raw_extraction_storage.extraction_storage_dir(project),
        raw_extraction_storage.tool_extraction_dir(project, TOOL_NAME),
        raw_extraction_storage.extraction_run_dir(project, TOOL_NAME, RUN_ID),
        raw_extraction_storage.extraction_manifest_path(
            project, TOOL_NAME, RUN_ID
        ),
        raw_extraction_storage.raw_artifact_path(
            project, TOOL_NAME, RUN_ID, "tokens.tsv"
        ),
        raw_extraction_storage.derived_artifact_dir(
            project, TOOL_NAME, RUN_ID
        ),
    )
    for path in allowed_paths:
        assert "writer_assistant" in path.parts
        assert "extractions" in path.parts
        assert not (set(path.parts) & FORBIDDEN_LOCATION_PARTS)

    for forbidden_name in (
        "bible.json",
        "storyform.json",
        "project.json",
        "index.json",
        "memory.json",
        "canon.json",
        "dataset_manifest.json",
        "package.json",
    ):
        with pytest.raises(ValueError):
            raw_extraction_storage.raw_artifact_path(
                project, TOOL_NAME, RUN_ID, forbidden_name
            )
    assert_no_extraction_side_effects(project)


def test_path_helpers_and_validators_have_no_filesystem_side_effects(tmp_path):
    project = project_dir(tmp_path)

    raw_extraction_storage.extraction_storage_dir(project)
    raw_extraction_storage.tool_extraction_dir(project, TOOL_NAME)
    raw_extraction_storage.extraction_run_dir(project, TOOL_NAME, RUN_ID)
    raw_extraction_storage.extraction_manifest_path(project, TOOL_NAME, RUN_ID)
    raw_extraction_storage.raw_artifact_dir(project, TOOL_NAME, RUN_ID)
    raw_extraction_storage.raw_artifact_path(
        project, TOOL_NAME, RUN_ID, "tokens.tsv"
    )
    raw_extraction_storage.derived_artifact_dir(project, TOOL_NAME, RUN_ID)
    raw_extraction_storage.validate_extraction_storage_path(
        project, TOOL_NAME, RUN_ID, "tokens.tsv"
    )
    raw_extraction_storage.validate_extraction_run_manifest(
        build_valid_manifest()
    )

    assert_no_extraction_side_effects(project)


def test_derived_events_filename_is_manifest_only_app_owned_support(tmp_path):
    project = project_dir(tmp_path)
    derived_dir = raw_extraction_storage.derived_artifact_dir(
        project, TOOL_NAME, RUN_ID
    )
    manifest = build_valid_manifest()

    validated = raw_extraction_storage.validate_extraction_run_manifest(manifest)

    assert derived_dir == (
        project / "writer_assistant" / "extractions" / TOOL_NAME / RUN_ID / "derived"
    )
    assert validated["derived_artifacts"][0]["artifact_name"] == "events.json"
    assert validated["derived_artifacts"][0]["artifact_kind"] == "booknlp_events_derived"
    assert "events.tsv" not in str(validated["derived_artifacts"][0])
    assert_no_extraction_side_effects(project)


def test_validate_extraction_run_manifest_accepts_valid_manifest_copy():
    manifest = build_valid_manifest()
    original = deepcopy(manifest)

    result = raw_extraction_storage.validate_extraction_run_manifest(manifest)

    assert result == manifest
    assert result is not manifest
    assert manifest == original
    assert result["human_review_required"] is True
    assert result["candidate_generation_allowed"] is False
    assert result["canon_write_allowed"] is False
    assert result["prose_generation_allowed"] is False


@pytest.mark.parametrize("field", tuple(build_valid_manifest().keys()))
def test_validate_extraction_run_manifest_rejects_missing_required_field(field):
    manifest = build_valid_manifest()
    manifest.pop(field)
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


def test_validate_extraction_run_manifest_rejects_unknown_fields():
    manifest = build_valid_manifest(extra_field=True)
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("human_review_required", False),
        ("candidate_generation_allowed", True),
        ("canon_write_allowed", True),
        ("prose_generation_allowed", True),
    ),
)
def test_validate_extraction_run_manifest_rejects_malformed_policy_flags(
    field, value
):
    manifest = build_valid_manifest(**{field: value})
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


@pytest.mark.parametrize(
    "run_type",
    ("booknlp_fixture_parse", "booknlp_raw_import", "manual_fixture_import"),
)
def test_validate_extraction_run_manifest_accepts_allowed_run_types(run_type):
    manifest = build_valid_manifest(run_type=run_type)
    result = raw_extraction_storage.validate_extraction_run_manifest(manifest)
    assert result["run_type"] == run_type


@pytest.mark.parametrize("run_type", ("manual", "spacy_baseline", "generated_prose"))
def test_validate_extraction_run_manifest_rejects_invalid_run_type(run_type):
    manifest = build_valid_manifest(run_type=run_type)
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


@pytest.mark.parametrize(
    "status", ("planned", "running", "complete", "partial", "failed", "rejected")
)
def test_validate_extraction_run_manifest_accepts_allowed_status_values(status):
    manifest = build_valid_manifest(status=status)
    result = raw_extraction_storage.validate_extraction_run_manifest(manifest)
    assert result["status"] == status


@pytest.mark.parametrize("status", ("draft", "approved", "promoted"))
def test_validate_extraction_run_manifest_rejects_invalid_status(status):
    manifest = build_valid_manifest(status=status)
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


def test_validate_extraction_run_manifest_rejects_invalid_source_document():
    manifest = build_valid_manifest(
        source_documents=[
            build_valid_source_document_ref(source_document_id="../outside")
        ]
    )
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


def test_validate_extraction_run_manifest_rejects_invalid_raw_artifact_reference():
    manifest = build_valid_manifest(
        raw_artifacts=[build_raw_artifact_ref("../tokens.tsv", "booknlp_tokens")]
    )
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


@pytest.mark.parametrize("unsafe_id", UNSAFE_STORAGE_IDS)
def test_validate_extraction_run_manifest_rejects_invalid_tool_and_run_ids(unsafe_id):
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(
            build_valid_manifest(tool_name=unsafe_id)
        )
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(
            build_valid_manifest(run_id=unsafe_id)
        )


@pytest.mark.parametrize("field", FORBIDDEN_MANIFEST_FIELDS)
def test_manifest_rejects_canon_candidate_promotion_or_prose_fields(field):
    manifest = build_valid_manifest(**{field: True})
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


def test_manifest_does_not_imply_candidate_canon_or_promotion_permissions():
    manifest = raw_extraction_storage.validate_extraction_run_manifest(
        build_valid_manifest()
    )
    manifest_text = repr(manifest).lower()

    assert manifest["candidate_generation_allowed"] is False
    assert manifest["canon_write_allowed"] is False
    assert manifest["prose_generation_allowed"] is False
    assert "candidate_records" not in manifest_text
    assert "canon_records" not in manifest_text
    assert "apply_promotion" not in manifest_text
    assert "write_to_canon" not in manifest_text
    assert "mutate_memory" not in manifest_text


@pytest.mark.parametrize(
    ("artifact_name", "artifact_kind"),
    (
        ("tokens.tsv", "booknlp_tokens"),
        ("entities.tsv", "booknlp_entities"),
        ("quotes.tsv", "booknlp_quotes"),
        ("supersense.tsv", "booknlp_supersense"),
        ("book.json", "booknlp_book_json"),
    ),
)
def test_existing_evidence_raw_output_reference_accepts_compatible_raw_refs(
    artifact_name, artifact_kind
):
    ref = build_raw_artifact_ref(artifact_name, artifact_kind)
    result = evidence.validate_raw_output_reference(ref)
    assert result == ref
    assert result is not ref
    assert result["is_canon"] is False
    assert result["is_candidate"] is False
    assert result["source_snapshot_hashes"] == [SNAPSHOT_HASH]
    assert result["artifact_path_hint"].startswith("writer_assistant/extractions/")


@pytest.mark.parametrize("field", ("candidate_id", "canon_id", "memory_id"))
def test_raw_output_reference_rejects_canon_candidate_or_memory_shortcuts(field):
    ref = build_raw_artifact_ref(**{field: "shortcut"})
    with pytest.raises(ValueError):
        evidence.validate_raw_output_reference(ref)


@pytest.mark.parametrize("field", ("write_to_canon", "mutate_memory", "apply_promotion"))
def test_manifest_raw_refs_reject_memory_canon_mutation_fields(field):
    manifest = build_valid_manifest(
        raw_artifacts=[build_raw_artifact_ref(**{field: True})]
    )
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


@pytest.mark.parametrize("artifact_kind", ACCEPTED_RAW_ARTIFACT_KINDS)
def test_validate_extraction_run_manifest_accepts_booknlp_raw_artifact_kinds(
    artifact_kind,
):
    artifact_name_by_kind = {
        "booknlp_tokens": "tokens.tsv",
        "booknlp_entities": "entities.tsv",
        "booknlp_quotes": "quotes.tsv",
        "booknlp_supersense": "supersense.tsv",
        "booknlp_book_json": "book.json",
        "booknlp_book_html": "book.html",
    }
    manifest = build_valid_manifest(
        raw_artifacts=[
            build_raw_artifact_ref(
                artifact_name_by_kind[artifact_kind], artifact_kind
            )
        ],
        derived_artifacts=[],
    )
    result = raw_extraction_storage.validate_extraction_run_manifest(manifest)
    assert result["raw_artifacts"][0]["artifact_kind"] == artifact_kind


def test_validate_extraction_run_manifest_accepts_derived_events_kind_only_as_derived():
    manifest = build_valid_manifest(
        raw_artifacts=[],
        derived_artifacts=[build_derived_artifact_ref()],
    )
    result = raw_extraction_storage.validate_extraction_run_manifest(manifest)
    assert result["derived_artifacts"][0]["artifact_kind"] == "booknlp_events_derived"

    raw_manifest = build_valid_manifest(
        raw_artifacts=[
            build_raw_artifact_ref("events.json", "booknlp_events_derived")
        ],
        derived_artifacts=[],
    )
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(raw_manifest)


@pytest.mark.parametrize("artifact_kind", REJECTED_ARTIFACT_KINDS)
def test_validate_extraction_run_manifest_rejects_forbidden_artifact_kinds(
    artifact_kind,
):
    manifest = build_valid_manifest(
        raw_artifacts=[build_raw_artifact_ref("tokens.tsv", artifact_kind)]
    )
    with pytest.raises(ValueError):
        raw_extraction_storage.validate_extraction_run_manifest(manifest)


def test_future_production_module_source_has_no_runtime_dependency_or_mutation_terms():
    module_path = Path(raw_extraction_storage.__file__)
    if not module_path.exists():
        pytest.fail("raw_extraction_storage module file is missing")

    module_source = module_path.read_text(encoding="utf-8").lower()
    for forbidden_term in FORBIDDEN_PRODUCTION_SOURCE_TERMS:
        assert forbidden_term.lower() not in module_source

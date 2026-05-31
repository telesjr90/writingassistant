import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from training.scripts import validate_dataset


def test_empty_jsonl_is_valid(tmp_path):
    dataset = tmp_path / "empty.jsonl"
    dataset.write_text("", encoding="utf-8")
    schemas = Path(__file__).resolve().parents[1] / "training" / "schemas"

    validators = validate_dataset.load_validators(schemas)
    record_count, findings = validate_dataset.validate_jsonl(
        dataset,
        validators,
        strict=True,
    )

    assert record_count == 0
    assert findings == []


def test_invalid_jsonl_reports_error(tmp_path):
    dataset = tmp_path / "invalid.jsonl"
    dataset.write_text("{not json}\n", encoding="utf-8")
    schemas = Path(__file__).resolve().parents[1] / "training" / "schemas"

    validators = validate_dataset.load_validators(schemas)
    record_count, findings = validate_dataset.validate_jsonl(
        dataset,
        validators,
        strict=True,
    )

    assert record_count == 0
    assert any("Invalid JSON" in finding.message for finding in findings)

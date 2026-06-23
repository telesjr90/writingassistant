import csv
import io


_TOKENS_HEADER = (
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
)

_TOKEN_NUMERIC_FIELDS = frozenset(
    {
        "paragraph_ID",
        "sentence_ID",
        "token_ID_within_sentence",
        "token_ID_within_document",
        "byte_onset",
        "byte_offset",
        "syntactic_head_ID",
    }
)

_ENTITIES_HEADER = ("COREF", "start_token", "end_token", "prop", "cat", "text")
_ENTITY_NUMERIC_FIELDS = frozenset({"COREF", "start_token", "end_token"})

_QUOTES_HEADER = (
    "quote_start",
    "quote_end",
    "mention_start",
    "mention_end",
    "mention_phrase",
    "char_id",
    "quote",
)
_QUOTE_NUMERIC_FIELDS = frozenset(
    {"quote_start", "quote_end", "mention_start", "mention_end", "char_id"}
)

_SUPERSENSE_HEADER = ("start_token", "end_token", "supersense_category", "text")
_SUPERSENSE_NUMERIC_FIELDS = frozenset({"start_token", "end_token"})

_BOOL_STRINGS = frozenset({"true", "false"})


def parse_booknlp_tokens_tsv(text: str) -> list[dict]:
    rows = _parse_tsv(
        text,
        _TOKENS_HEADER,
        _TOKEN_NUMERIC_FIELDS,
        optional_empty_fields=frozenset({"event"}),
    )
    _validate_span(rows, "byte_onset", "byte_offset")
    return rows


def parse_booknlp_entities_tsv(text: str) -> list[dict]:
    rows = _parse_tsv(text, _ENTITIES_HEADER, _ENTITY_NUMERIC_FIELDS)
    _validate_span(rows, "start_token", "end_token")
    return rows


def parse_booknlp_quotes_tsv(text: str) -> list[dict]:
    rows = _parse_tsv(text, _QUOTES_HEADER, _QUOTE_NUMERIC_FIELDS)
    _validate_span(rows, "quote_start", "quote_end")
    _validate_span(rows, "mention_start", "mention_end")
    return rows


def parse_booknlp_supersense_tsv(text: str) -> list[dict]:
    rows = _parse_tsv(text, _SUPERSENSE_HEADER, _SUPERSENSE_NUMERIC_FIELDS)
    _validate_span(rows, "start_token", "end_token")
    return rows


def parse_booknlp_book_json(text: str) -> dict:
    raise NotImplementedError("deferred parser API")


def derive_booknlp_events_from_tokens(tokens: list[dict]) -> list[dict]:
    raise NotImplementedError("deferred parser API")


def build_booknlp_raw_artifact_bundle_from_fixture_texts(
    fixture_texts: dict,
    *,
    run_manifest: dict,
    source_map: dict,
    raw_output_references: list[dict],
) -> dict:
    raise NotImplementedError("deferred parser API")


def _parse_tsv(text, expected_header, numeric_fields, *, optional_empty_fields=frozenset()):
    _require_text(text)
    rows = list(csv.reader(io.StringIO(text), delimiter="\t"))
    if not rows:
        raise ValueError("invalid fixture text")

    header = rows[0]
    _validate_header(header, expected_header)

    parsed_rows = []
    for row in rows[1:]:
        if len(row) != len(header):
            raise ValueError("invalid row")
        parsed_row = {}
        for field, value in zip(header, row):
            if value == "" and field not in optional_empty_fields:
                raise ValueError("invalid row")
            if field in numeric_fields:
                parsed_row[field] = _coerce_non_negative_int(value)
            else:
                parsed_row[field] = value
        parsed_rows.append(parsed_row)
    return parsed_rows


def _require_text(value):
    if not isinstance(value, str):
        raise ValueError("invalid fixture text")
    if value == "":
        raise ValueError("invalid fixture text")


def _validate_header(header, expected_header):
    if len(header) != len(set(header)):
        raise ValueError("invalid header")
    if tuple(header) != expected_header:
        raise ValueError("invalid header")


def _coerce_non_negative_int(value):
    if value.lower() in _BOOL_STRINGS:
        raise ValueError("invalid numeric field")
    if not value.isdecimal():
        raise ValueError("invalid numeric field")
    number = int(value)
    if number < 0:
        raise ValueError("invalid numeric field")
    return number


def _validate_span(rows, start_field, end_field):
    for row in rows:
        if row[end_field] < row[start_field]:
            raise ValueError("invalid span")

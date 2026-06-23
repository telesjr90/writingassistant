import csv
import io
import json
from copy import deepcopy


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
_BOOK_TOP_LEVEL_FIELDS = frozenset({"characters"})
_BOOK_CHARACTER_FIELDS = frozenset(
    {"agent", "patient", "mod", "poss", "id", "g", "count", "mentions"}
)
_BOOK_CHARACTER_LIST_FIELDS = frozenset({"agent", "patient", "mod", "poss"})
_BOOK_CHARACTER_NUMERIC_FIELDS = frozenset({"id", "count"})
_BOOK_MENTION_BUCKETS = frozenset({"proper", "common", "pronoun"})
_BOOK_MENTION_FIELDS = frozenset({"c", "n"})
_EVENT_MARKERS = frozenset({"EVENT"})


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
    _require_text(text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON") from exc

    if not isinstance(payload, dict):
        raise ValueError("invalid object")
    _reject_unknown_fields(payload, _BOOK_TOP_LEVEL_FIELDS)

    characters = payload.get("characters")
    if not isinstance(characters, list):
        raise ValueError("invalid object")

    for character in characters:
        _validate_book_character(character)

    return deepcopy(payload)


def derive_booknlp_events_from_tokens(tokens: list[dict]) -> list[dict]:
    if not isinstance(tokens, list):
        raise ValueError("invalid event data")

    events = []
    for token in tokens:
        if not isinstance(token, dict):
            raise ValueError("invalid event data")

        marker = token.get("event")
        if marker is None or marker == "O":
            continue
        if not isinstance(marker, str) or marker == "":
            raise ValueError("invalid event data")
        if marker not in _EVENT_MARKERS:
            continue

        event_index = len(events)
        event = {
            "event_id": f"booknlp_event_{event_index}",
            "event_text": _require_token_text(token.get("word")),
            "event_type": "booknlp_token_event",
            "event": marker,
            "word": token["word"],
            "confidence": _event_confidence(token),
        }
        if "token_ID_within_document" in token:
            token_id = _require_json_non_negative_int(token["token_ID_within_document"])
            event["token_ID_within_document"] = token_id
            event["token_id"] = token_id
        elif "token_id" in token:
            event["token_id"] = _require_json_non_negative_int(token["token_id"])
        for field in ("byte_onset", "byte_offset"):
            if field in token:
                event[field] = _require_json_non_negative_int(token[field])
        if "source_locator" in token:
            event["source_locator"] = deepcopy(token["source_locator"])
        events.append(event)

    return events


def build_booknlp_raw_artifact_bundle_from_fixture_texts(
    fixture_texts: dict,
    *,
    run_manifest: dict,
    source_map: dict,
    raw_output_references: list[dict],
) -> dict:
    raise ValueError("deferred parser API")


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


def _reject_unknown_fields(payload, fields):
    for field in payload:
        if field not in fields:
            raise ValueError("invalid object")


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


def _validate_book_character(character):
    if not isinstance(character, dict):
        raise ValueError("invalid object")
    _reject_unknown_fields(character, _BOOK_CHARACTER_FIELDS)

    for field in _BOOK_CHARACTER_LIST_FIELDS:
        if field in character and not isinstance(character[field], list):
            raise ValueError("invalid object")
    for field in _BOOK_CHARACTER_NUMERIC_FIELDS:
        if field in character:
            _require_json_non_negative_int(character[field])
    if "mentions" in character:
        _validate_book_mentions(character["mentions"])


def _validate_book_mentions(mentions):
    if not isinstance(mentions, dict):
        raise ValueError("invalid object")
    _reject_unknown_fields(mentions, _BOOK_MENTION_BUCKETS)

    for entries in mentions.values():
        if not isinstance(entries, list):
            raise ValueError("invalid object")
        for entry in entries:
            _validate_book_mention(entry)


def _validate_book_mention(entry):
    if not isinstance(entry, dict):
        raise ValueError("invalid object")
    _reject_unknown_fields(entry, _BOOK_MENTION_FIELDS)
    if set(entry) != _BOOK_MENTION_FIELDS:
        raise ValueError("invalid object")
    if not isinstance(entry["c"], str) or entry["c"] == "":
        raise ValueError("invalid object")
    _require_json_non_negative_int(entry["n"])


def _require_json_non_negative_int(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("invalid numeric field")
    if value < 0:
        raise ValueError("invalid numeric field")
    return value


def _require_token_text(value):
    if not isinstance(value, str) or value == "":
        raise ValueError("invalid event data")
    return value


def _event_confidence(token):
    if "confidence" not in token:
        return 0.0
    confidence = token["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("invalid event data")
    if confidence < 0.0 or confidence > 1.0:
        raise ValueError("invalid event data")
    return confidence

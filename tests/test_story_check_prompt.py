from pathlib import Path


PROMPT_PATH = Path(__file__).resolve().parents[1] / "backend" / "prompts" / "story_check.txt"


def _prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def test_story_check_prompt_exists():
    assert PROMPT_PATH.exists()


def test_prompt_mentions_required_rich_schema_fields():
    prompt = _prompt()

    for field in (
        "task",
        "coherence_score",
        "throughline_alignment",
        "overall_story",
        "main_character",
        "influence_character",
        "relationship_story",
        "theme_drift",
        "character_consistency",
        "warnings",
        "suggestions",
        "insufficient_evidence",
    ):
        assert field in prompt


def test_prompt_includes_no_prose_boundaries():
    prompt = _prompt().lower()

    for phrase in (
        "do not write story prose",
        "do not rewrite the scene",
        "do not continue the scene",
        "do not imitate style",
        "improve, polish",
        "do not generate dialogue",
        "scenes, chapters, paragraphs",
    ):
        assert phrase in prompt


def test_prompt_requires_json_only_no_markdown_or_code_fences():
    prompt = _prompt().lower()

    assert "return only one valid top-level json object" in prompt
    assert "output valid json only" in prompt
    assert "do not use markdown" in prompt
    assert "do not use code fences" in prompt


def test_prompt_requires_insufficient_evidence_instead_of_guessing():
    prompt = _prompt().lower()

    assert "insufficient_evidence" in prompt
    assert "not guessed" in prompt
    assert "do not invent evidence" in prompt
    assert "missing support must be reported" in prompt


def test_prompt_blocks_common_dramatica_overclaims():
    prompt = _prompt()

    assert "A character relationship existing is not proof of Relationship Story." in prompt
    assert "A generic theme is not proof of Dramatica Issue/Variation." in prompt
    assert "Antagonist is not automatically Influence Character." in prompt


def test_prompt_bounds_warnings_and_suggestions():
    prompt = _prompt().lower()

    assert "warnings must be an array of strings capped at 5 items" in prompt
    assert "suggestions must be an array of writer-focused diagnostic questions capped at 5 items" in prompt
    assert "suggestions must not include replacement prose" in prompt


def test_prompt_does_not_contain_sample_story_prose():
    prompt = _prompt().lower()

    forbidden_sample_markers = (
        "once upon a time",
        "she said",
        "he said",
        "the princess and the pea",
        "elena",
        "ember crown",
    )
    for marker in forbidden_sample_markers:
        assert marker not in prompt

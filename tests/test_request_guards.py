import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import guardrails


def test_guard_freeform_request_refuses_prose_generation_requests():
    blocked = [
        "write a scene about a storm",
        "continue this story",
        "rewrite this paragraph",
    ]

    for text in blocked:
        response = guardrails.guard_freeform_request(text)

        assert response is not None
        assert response["task"] == "out_of_scope_refusal"
        assert response["message"] == guardrails.STANDARD_REFUSAL_MESSAGE


def test_guard_freeform_request_allows_analysis_requests():
    allowed = [
        "analyze this scene",
        "run Story Check",
        "ask diagnostic questions",
    ]

    for text in allowed:
        assert guardrails.guard_freeform_request(text) is None


def test_request_field_policy_guards_freeform_request_fields():
    guarded_fields = [
        "request",
        "user_request",
        "instruction",
        "analysis_request",
        "omi_request",
    ]

    for field_name in guarded_fields:
        assert guardrails.should_guard_request_field(field_name), field_name


def test_request_field_policy_does_not_guard_owner_authored_content_fields():
    content_fields = [
        "content",
        "scene_text",
        "bible_json",
        "storyform_json",
        "raw_idea",
        "planning_notes",
    ]

    for field_name in content_fields:
        assert guardrails.is_owner_authored_content_field(field_name), field_name
        assert not guardrails.should_guard_request_field(field_name), field_name


def test_owner_authored_scene_content_may_contain_command_like_words():
    scene_text = (
        'The editor margin said "rewrite the chapter," while the character refused '
        "to continue the dialogue."
    )

    assert guardrails.should_guard_request_field("content") is False
    assert guardrails.is_prose_generation_request(scene_text) is False


def test_owner_authored_context_json_may_contain_story_craft_terms():
    bible = {
        "notes": [
            "The chapter includes dialogue about style.",
            "A character asks another character to rewrite a public notice.",
        ]
    }

    assert guardrails.should_guard_request_field("bible_json") is False
    assert guardrails.output_appears_to_contain_prose_generation(bible) is False

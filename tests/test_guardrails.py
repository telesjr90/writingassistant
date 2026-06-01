import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import guardrails


def test_prose_generation_requests_are_refused():
    blocked = [
        "write a scene",
        "write the next scene",
        "write dialogue",
        "draft a paragraph",
        "compose a chapter",
        "generate an ending",
        "continue this scene",
        "finish this chapter",
        "extend this passage",
        "rewrite this text",
        "revise this prose",
        "polish the writing",
        "improve the writing",
        "make this sound better",
        "imitate an author style",
        "write in the style of an author",
        "create dialogue",
        "create a monologue",
        "give me the actual prose",
    ]

    for text in blocked:
        assert guardrails.is_prose_generation_request(text), text
        assert guardrails.classify_request(text) is not None


def test_analysis_requests_are_allowed():
    allowed = [
        "analyze this scene",
        "identify throughlines",
        "run Story Check",
        "ask diagnostic questions",
        "classify the Main Character throughline",
        "explain what evidence is missing",
        "list structural issues",
        "summarize warnings as diagnostics",
        "tell me if there is insufficient evidence",
        "what would I need to decide before writing",
    ]

    for text in allowed:
        assert not guardrails.is_prose_generation_request(text), text
        assert guardrails.classify_request(text) is None


def test_refusal_response_shape():
    response = guardrails.refusal_response()

    assert response == {
        "task": "out_of_scope_refusal",
        "request_type": "prose_generation",
        "allowed_help": [
            "analysis",
            "diagnostic questions",
            "structural classification",
        ],
        "message": guardrails.STANDARD_REFUSAL_MESSAGE,
    }


def test_scene_like_content_is_not_treated_as_user_command():
    scene_like_text = "A character keeps a notebook and mentions a chapter during an argument."

    assert not guardrails.is_prose_generation_request(scene_like_text)


def test_output_helper_recurses_conservatively():
    assert guardrails.output_appears_to_contain_prose_generation(
        {"suggestions": ["What structural evidence is missing?"]}
    ) is False
    assert guardrails.output_appears_to_contain_prose_generation(
        {"suggestions": ["Rewrite this paragraph?"]}
    ) is True

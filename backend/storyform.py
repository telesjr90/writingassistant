from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=8)
def _load_schema_from_repo_knowledge(schema_doc_path: str) -> dict[str, Any]:
    """Extract the copied NCP JSON schema from docs/repo_knowledge.md."""

    path = Path(schema_doc_path)
    lines: list[str] = []
    in_json_block = False

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not in_json_block:
            if stripped.startswith("```json"):
                in_json_block = True
            continue

        if stripped.startswith("```"):
            break

        lines.append(line)

    if not lines:
        raise ValueError(f"No JSON schema block found in {path}")

    schema = json.loads("\n".join(lines))
    Draft7Validator.check_schema(schema)
    return schema


@dataclass(frozen=True)
class Storyform:
    data: dict[str, Any]

    SCHEMA_DOC_PATH: ClassVar[Path] = REPO_ROOT / "docs" / "repo_knowledge.md"
    PROJECTS_DIR: ClassVar[Path] = REPO_ROOT / "projects"

    @classmethod
    def schema(cls) -> dict[str, Any]:
        return _load_schema_from_repo_knowledge(str(cls.SCHEMA_DOC_PATH))

    @classmethod
    def validate_data(cls, data: dict[str, Any]) -> None:
        Draft7Validator(cls.schema()).validate(data)

    @classmethod
    def from_file(cls, project_name: str) -> "Storyform":
        path = cls.PROJECTS_DIR / project_name / "storyform.json"
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)

        cls.validate_data(data)
        return cls(data)

    @classmethod
    def from_questionnaire(cls, responses: dict[str, Any]) -> "Storyform":
        del responses

        data: dict[str, Any] = {
            "schema_version": "1.3.0",
            "story": {
                "id": "story_ember_crown_quest",
                "title": "Quest for the Ember Crown",
                "genre": "Fantasy Quest",
                "logline": (
                    "A reluctant mapmaker joins a guarded knight to recover a stolen "
                    "relic before their valley loses its last source of winter fire."
                ),
                "created_at": "2026-01-01T00:00:00Z",
                "narratives": [
                    {
                        "id": "narrative_ember_crown",
                        "title": "The Ember Crown Quest",
                        "status": "complete",
                        "subtext": {
                            "perspectives": [
                                {
                                    "id": "persp_objective_story",
                                    "author_structural_pov": "they",
                                    "summary": "The valley must organize a dangerous expedition.",
                                    "storytelling": (
                                        "Villagers, scouts, and rivals argue over who can "
                                        "retrieve the Ember Crown before the passes close."
                                    ),
                                },
                                {
                                    "id": "persp_main_character",
                                    "author_structural_pov": "i",
                                    "summary": "Mara wants to stay invisible and useful.",
                                    "storytelling": (
                                        "Mara maps everyone else's roads while avoiding the "
                                        "choice that would put her own name on the quest."
                                    ),
                                },
                                {
                                    "id": "persp_influence_character",
                                    "author_structural_pov": "you",
                                    "summary": "Sir Calen believes duty must be carried openly.",
                                    "storytelling": (
                                        "Calen keeps pressing Mara to stop hiding behind plans "
                                        "and accept the cost of leadership."
                                    ),
                                },
                                {
                                    "id": "persp_relationship_story",
                                    "author_structural_pov": "we",
                                    "summary": "Mara and Calen learn to trust different strengths.",
                                    "storytelling": (
                                        "Their partnership shifts from command and resistance "
                                        "toward shared judgment under pressure."
                                    ),
                                },
                            ],
                            "players": [
                                {
                                    "id": "player_mara",
                                    "name": "Mara Vell",
                                    "role": "Main Character",
                                    "visual": "Ink-stained cloak, brass compass, weathered satchel.",
                                    "audio": "Quiet, precise speech that sharpens under stress.",
                                    "summary": "A village mapmaker pulled into the quest.",
                                    "bio": (
                                        "Mara knows every trail through the valley but has spent "
                                        "years avoiding decisions that would make others depend on her."
                                    ),
                                    "storytelling": (
                                        "She solves practical route problems while resisting the "
                                        "larger responsibility the quest demands."
                                    ),
                                    "motivations": [
                                        {
                                            "narrative_function": "Avoid",
                                            "illustration": "She tries to keep the quest theoretical.",
                                            "storytelling": (
                                                "Mara prepares maps and contingencies instead of "
                                                "volunteering to guide the expedition."
                                            ),
                                        }
                                    ],
                                    "perspectives": [{"perspective_id": "persp_main_character"}],
                                },
                                {
                                    "id": "player_calen",
                                    "name": "Sir Calen Rook",
                                    "role": "Influence Character",
                                    "visual": "Dented white shield, ash-gray travel coat.",
                                    "audio": "Measured, formal voice with little ornament.",
                                    "summary": "A knight determined to make duty visible.",
                                    "bio": (
                                        "Calen failed a previous defense by waiting for permission, "
                                        "so he now treats open commitment as a moral necessity."
                                    ),
                                    "storytelling": (
                                        "He challenges Mara's habit of staying useful but unseen."
                                    ),
                                    "motivations": [
                                        {
                                            "narrative_function": "Pursuit",
                                            "illustration": "He pushes directly toward the stolen crown.",
                                            "storytelling": (
                                                "Calen keeps the expedition moving even when "
                                                "political bargains would delay it."
                                            ),
                                        }
                                    ],
                                    "perspectives": [{"perspective_id": "persp_influence_character"}],
                                },
                            ],
                            "dynamics": [
                                {
                                    "id": "dynamic_mc_resolve",
                                    "dynamic": "main_character_resolve",
                                    "vector": "change",
                                    "summary": "Mara changes from avoidance to open commitment.",
                                    "storytelling": (
                                        "She stops treating herself as support staff and claims "
                                        "responsibility for the route and the rescue."
                                    ),
                                },
                                {
                                    "id": "dynamic_story_outcome",
                                    "dynamic": "story_outcome",
                                    "vector": "success",
                                    "summary": "The expedition recovers the Ember Crown.",
                                    "storytelling": (
                                        "The valley regains its winter fire because the quest "
                                        "chooses action before the final pass closes."
                                    ),
                                },
                                {
                                    "id": "dynamic_story_judgment",
                                    "dynamic": "story_judgment",
                                    "vector": "good",
                                    "summary": "Mara is personally better for the journey.",
                                    "storytelling": (
                                        "She returns with a public voice and a chosen place in the community."
                                    ),
                                },
                            ],
                            "storypoints": [
                                {
                                    "id": "sp_os_throughline",
                                    "appreciation": "Objective Story Throughline",
                                    "narrative_function": "Physics",
                                    "illustration": "A race to retrieve the stolen Ember Crown.",
                                    "summary": "The external plot is a hazardous recovery quest.",
                                    "storytelling": "Travel, pursuit, traps, and negotiations drive the plot.",
                                    "throughline": "Objective Story",
                                    "perspectives": [{"perspective_id": "persp_objective_story"}],
                                },
                                {
                                    "id": "sp_os_concern",
                                    "appreciation": "Objective Story Concern",
                                    "narrative_function": "Obtaining",
                                    "illustration": "The valley needs the crown back before winter.",
                                    "summary": "Everyone is focused on securing the relic.",
                                    "storytelling": "Every faction measures success by who ends up holding the crown.",
                                    "throughline": "Objective Story",
                                    "perspectives": [{"perspective_id": "persp_objective_story"}],
                                },
                                {
                                    "id": "sp_os_issue",
                                    "appreciation": "Objective Story Issue",
                                    "narrative_function": "Value",
                                    "illustration": "People disagree about what the crown is worth.",
                                    "summary": "The quest tests public value against private cost.",
                                    "storytelling": "Bargains tempt the party to trade safety for the relic.",
                                    "throughline": "Objective Story",
                                    "perspectives": [{"perspective_id": "persp_objective_story"}],
                                },
                                {
                                    "id": "sp_os_problem",
                                    "appreciation": "Objective Story Problem",
                                    "narrative_function": "Pursuit",
                                    "illustration": "Every side charges after the crown at once.",
                                    "summary": "Blind pursuit escalates danger across the valley.",
                                    "storytelling": "The chase creates ambushes, broken truces, and dwindling supplies.",
                                    "throughline": "Objective Story",
                                    "perspectives": [{"perspective_id": "persp_objective_story"}],
                                },
                                {
                                    "id": "sp_mc_throughline",
                                    "appreciation": "Main Character Throughline",
                                    "narrative_function": "Situation",
                                    "illustration": "Mara is the only person who can read the old route maps.",
                                    "summary": "Mara is trapped by being uniquely necessary.",
                                    "storytelling": "Her special knowledge keeps forcing her into visible choices.",
                                    "throughline": "Main Character",
                                    "perspectives": [{"perspective_id": "persp_main_character"}],
                                },
                                {
                                    "id": "sp_mc_concern",
                                    "appreciation": "Main Character Concern",
                                    "narrative_function": "Future",
                                    "illustration": "Mara fears becoming responsible for what happens next.",
                                    "summary": "Her anxiety centers on the future her choices create.",
                                    "storytelling": "She reads every route as a forecast of blame.",
                                    "throughline": "Main Character",
                                    "perspectives": [{"perspective_id": "persp_main_character"}],
                                },
                                {
                                    "id": "sp_mc_issue",
                                    "appreciation": "Main Character Issue",
                                    "narrative_function": "Choice",
                                    "illustration": "Mara must choose whether to lead openly.",
                                    "summary": "Choice is the pressure point in Mara's arc.",
                                    "storytelling": "Each delay narrows her options until neutrality disappears.",
                                    "throughline": "Main Character",
                                    "perspectives": [{"perspective_id": "persp_main_character"}],
                                },
                                {
                                    "id": "sp_ic_throughline",
                                    "appreciation": "Influence Character Throughline",
                                    "narrative_function": "Mind",
                                    "illustration": "Calen is fixed in his belief that duty must be declared.",
                                    "summary": "Calen's certainty pressures Mara's avoidance.",
                                    "storytelling": "He frames every hesitation as a hidden decision.",
                                    "throughline": "Influence Character",
                                    "perspectives": [{"perspective_id": "persp_influence_character"}],
                                },
                                {
                                    "id": "sp_ic_concern",
                                    "appreciation": "Influence Character Concern",
                                    "narrative_function": "Memory",
                                    "illustration": "Calen is shaped by the defense he failed to join in time.",
                                    "summary": "His past failure keeps his present duty severe.",
                                    "storytelling": "Old shame makes him suspicious of caution.",
                                    "throughline": "Influence Character",
                                    "perspectives": [{"perspective_id": "persp_influence_character"}],
                                },
                                {
                                    "id": "sp_ic_issue",
                                    "appreciation": "Influence Character Issue",
                                    "narrative_function": "Truth",
                                    "illustration": "Calen insists that fear must be named before it can be mastered.",
                                    "summary": "Truth is his standard for courage.",
                                    "storytelling": "He keeps asking Mara to say what she really wants.",
                                    "throughline": "Influence Character",
                                    "perspectives": [{"perspective_id": "persp_influence_character"}],
                                },
                                {
                                    "id": "sp_rs_throughline",
                                    "appreciation": "Relationship Story Throughline",
                                    "narrative_function": "Psychology",
                                    "illustration": "Mara and Calen keep trying to define what partnership means.",
                                    "summary": "Their relationship is built through changing assumptions.",
                                    "storytelling": "Strategy talks become arguments about trust and authority.",
                                    "throughline": "Relationship Story",
                                    "perspectives": [{"perspective_id": "persp_relationship_story"}],
                                },
                                {
                                    "id": "sp_rs_concern",
                                    "appreciation": "Relationship Story Concern",
                                    "narrative_function": "Conceptualizing",
                                    "illustration": "They must imagine a partnership neither has practiced.",
                                    "summary": "The bond develops as they redesign how they work together.",
                                    "storytelling": "Plans improve once both stop treating leadership as a single role.",
                                    "throughline": "Relationship Story",
                                    "perspectives": [{"perspective_id": "persp_relationship_story"}],
                                },
                                {
                                    "id": "sp_rs_issue",
                                    "appreciation": "Relationship Story Issue",
                                    "narrative_function": "Commitment",
                                    "illustration": "Trust depends on staying committed after mistakes.",
                                    "summary": "Commitment tests whether their partnership can survive pressure.",
                                    "storytelling": "Each must stay present when the other's method causes a setback.",
                                    "throughline": "Relationship Story",
                                    "perspectives": [{"perspective_id": "persp_relationship_story"}],
                                },
                                {
                                    "id": "sp_story_goal",
                                    "appreciation": "Story Goal",
                                    "narrative_function": "Obtaining",
                                    "illustration": "Recover the Ember Crown.",
                                    "summary": "The quest succeeds only if the crown is restored to the valley.",
                                    "storytelling": "Every major decision is judged against the recovery of the crown.",
                                    "throughline": "Objective Story",
                                    "perspectives": [{"perspective_id": "persp_objective_story"}],
                                },
                            ],
                            "storybeats": [
                                {
                                    "id": "beat_objective_signpost_1",
                                    "appreciation": "Objective Story Signpost 1",
                                    "scope": "signpost",
                                    "sequence": 1,
                                    "throughline": "Objective Story",
                                    "narrative_function": "Learning",
                                    "summary": "The valley learns the crown was stolen for a rival winter rite.",
                                    "storytelling": "Mara deciphers ash marks that reveal the raiders' destination.",
                                    "perspectives": [{"perspective_id": "persp_objective_story"}],
                                }
                            ],
                        },
                        "storytelling": {
                            "overviews": [
                                {
                                    "id": "overview_logline",
                                    "label": "Logline",
                                    "summary": "A reluctant mapmaker must guide a quest for a stolen relic.",
                                    "storytelling": (
                                        "The plot combines wilderness pursuit with a personal arc "
                                        "from avoidance to leadership."
                                    ),
                                },
                                {
                                    "id": "overview_genre",
                                    "label": "Genre",
                                    "summary": "Fantasy Quest",
                                    "storytelling": (
                                        "A relic journey, contested passes, old magic, and moral bargains."
                                    ),
                                },
                                {
                                    "id": "overview_throughlines",
                                    "label": "Blended Throughlines",
                                    "summary": (
                                        "The recovery quest pressures Mara's fear of responsibility, "
                                        "Calen's rigid duty, and their evolving partnership."
                                    ),
                                    "storytelling": "External pursuit and internal commitment escalate together.",
                                },
                            ],
                            "moments": [
                                {
                                    "id": "moment_call_to_quest",
                                    "summary": "The theft forces Mara to reveal a hidden pass.",
                                    "synopsis": (
                                        "When the Ember Crown is stolen, Mara recognizes the raiders' "
                                        "route and realizes no one else can guide the expedition in time."
                                    ),
                                    "setting": "The frost-lit village archive.",
                                    "timing": "Opening movement.",
                                    "imperatives": "Force Mara from private expertise into public action.",
                                    "act": 1,
                                    "order": 1,
                                    "audience_experiential_pov": "third_person_limited",
                                    "storybeats": [
                                        {
                                            "sequence": 1,
                                            "storybeat_id": "beat_objective_signpost_1",
                                        }
                                    ],
                                }
                            ],
                        },
                    }
                ],
            },
        }

        cls.validate_data(data)
        return cls(data)

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self.data)

    def to_prompt_context(self) -> str:
        story = self.data.get("story", {})
        lines = [
            f"Story: {story.get('title', 'Untitled')}",
            f"Logline: {story.get('logline', '')}",
        ]

        for narrative in story.get("narratives", []):
            status = narrative.get("status")
            heading = f"Narrative: {narrative.get('title', 'Untitled Narrative')}"
            if status:
                heading = f"{heading} ({status})"
            lines.extend(["", heading])

            subtext = narrative.get("subtext", {})
            self._append_players(lines, subtext.get("players", []))
            self._append_dynamics(lines, subtext.get("dynamics", []))
            self._append_throughlines(lines, subtext.get("storypoints", []))
            self._append_storybeats(lines, subtext.get("storybeats", []))

            overviews = narrative.get("storytelling", {}).get("overviews", [])
            if overviews:
                lines.append("Overviews:")
                for overview in overviews:
                    label = overview.get("label", "Overview")
                    summary = overview.get("summary") or overview.get("storytelling", "")
                    lines.append(f"- {label}: {summary}")

        return "\n".join(line for line in lines if line is not None).strip()

    @staticmethod
    def _append_players(lines: list[str], players: list[dict[str, Any]]) -> None:
        if not players:
            return

        lines.append("Players:")
        for player in players:
            lines.append(
                f"- {player.get('name', 'Unnamed')} ({player.get('role', 'Role unknown')}): "
                f"{player.get('summary', '')}"
            )

    @staticmethod
    def _append_dynamics(lines: list[str], dynamics: list[dict[str, Any]]) -> None:
        if not dynamics:
            return

        lines.append("Dynamics:")
        for dynamic in dynamics:
            name = dynamic.get("dynamic", "").replace("_", " ")
            vector = dynamic.get("vector", "").replace("_", " ")
            summary = dynamic.get("summary", "")
            lines.append(f"- {name}: {vector}. {summary}")

    @classmethod
    def _append_throughlines(cls, lines: list[str], storypoints: list[dict[str, Any]]) -> None:
        if not storypoints:
            return

        grouped: dict[str, list[dict[str, Any]]] = {}
        for storypoint in storypoints:
            throughline = storypoint.get("throughline") or cls._throughline_from_appreciation(
                storypoint.get("appreciation", "")
            )
            if throughline:
                grouped.setdefault(throughline, []).append(storypoint)

        if grouped:
            lines.append("Throughlines:")
            for throughline in [
                "Objective Story",
                "Main Character",
                "Influence Character",
                "Relationship Story",
            ]:
                points = grouped.get(throughline, [])
                if not points:
                    continue
                summary = cls._summarize_throughline(throughline, points)
                lines.append(f"- {throughline}: {summary}")

        ungrouped = [storypoint for storypoint in storypoints if not storypoint.get("throughline")]
        if ungrouped:
            lines.append("Storypoints:")
            for storypoint in ungrouped:
                lines.append(f"- {cls._storypoint_summary(storypoint)}")

    @staticmethod
    def _append_storybeats(lines: list[str], storybeats: list[dict[str, Any]]) -> None:
        if not storybeats:
            return

        lines.append("Storybeats:")
        for beat in sorted(storybeats, key=lambda item: item.get("sequence", 0)):
            scope = beat.get("scope", "beat")
            sequence = beat.get("sequence", "?")
            throughline = beat.get("throughline", "Unassigned")
            function = beat.get("narrative_function", "")
            summary = beat.get("summary", "")
            label = f"{scope} {sequence}"
            if function:
                label = f"{label} / {function}"
            lines.append(f"- {throughline} {label}: {summary}")

    @staticmethod
    def _throughline_from_appreciation(appreciation: str) -> str | None:
        for throughline in [
            "Objective Story",
            "Main Character",
            "Influence Character",
            "Relationship Story",
        ]:
            if appreciation.startswith(throughline):
                return throughline
        return None

    @classmethod
    def _summarize_throughline(
        cls, throughline: str, storypoints: list[dict[str, Any]]
    ) -> str:
        priority = [
            "Throughline",
            "Domain",
            "Concern",
            "Issue",
            "Problem",
            "Solution",
            "Symptom",
            "Response",
            "Benchmark",
            "Catalyst",
            "Inhibitor",
            "Goal",
        ]
        parts: list[str] = []

        for suffix in priority:
            storypoint = cls._find_storypoint(throughline, storypoints, suffix)
            if storypoint:
                label = "Domain" if suffix == "Throughline" else suffix
                parts.append(f"{label}: {cls._storypoint_focus(storypoint)}")

        if not parts:
            parts = [cls._storypoint_summary(storypoint) for storypoint in storypoints]

        return "; ".join(parts)

    @staticmethod
    def _find_storypoint(
        throughline: str, storypoints: list[dict[str, Any]], suffix: str
    ) -> dict[str, Any] | None:
        expected = f"{throughline} {suffix}"
        for storypoint in storypoints:
            if storypoint.get("appreciation") == expected:
                return storypoint

        for storypoint in storypoints:
            if str(storypoint.get("appreciation", "")).endswith(suffix):
                return storypoint

        return None

    @staticmethod
    def _storypoint_focus(storypoint: dict[str, Any]) -> str:
        function = storypoint.get("narrative_function")
        summary = storypoint.get("summary") or storypoint.get("illustration", "")
        if function and summary:
            return f"{function} - {summary}"
        return function or summary

    @classmethod
    def _storypoint_summary(cls, storypoint: dict[str, Any]) -> str:
        appreciation = storypoint.get("appreciation", "Storypoint")
        return f"{appreciation}: {cls._storypoint_focus(storypoint)}"

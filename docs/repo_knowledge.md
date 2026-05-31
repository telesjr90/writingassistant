# Repository Knowledge

This document was extracted from the five repositories cloned under `open_source_repos`. Paths are relative to `E:\WritingAssistantApplication`.

## narrative-first/narrative-context-protocol

Source: `open_source_repos/narrative-context-protocol/schema/ncp-schema.json`. The schema describes `story.narratives[]` as a Dramatica storyform: a complete argument structure expressed through subtext and storytelling layers. The complete JSON schema is copied below.

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Narrative Context Protocol Schema",
    "description": "A standardized protocol for structuring narrative elements in a complete story for use in multi-agentic systems.",
    "type": "object",
    "properties": {
        "schema_version": {
            "type": "string",
            "description": "Semver string (e.g., 1.3.0).",
            "pattern": "^\\d+\\.\\d+\\.\\d+$"
        },
        "story": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string"
                },
                "title": {
                    "type": "string"
                },
                "genre": {
                    "type": "string"
                },
                "logline": {
                    "type": "string"
                },
                "created_at": {
                    "type": "string",
                    "description": "ISO-8601 UTC timestamp (e.g., 2025-12-01T12:34:56Z).",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"
                },
                "settings": {
                    "type": "array",
                    "description": "Optional story-level setting glossary. Each entry is a stable, referenceable place or environment that Moments may identify with setting_id while retaining free-text setting prose.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "$ref": "#/$defs/setting_id"
                            },
                            "name": {
                                "type": "string",
                                "description": "Short human-readable setting name."
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional longer setting description."
                            }
                        },
                        "required": [
                            "id",
                            "name"
                        ],
                        "additionalProperties": false
                    }
                },
                "ideation": {
                    "type": "object",
                    "description": "Optional pre-narrative ideation threads for exploratory and beginner workflows.",
                    "properties": {
                        "character": {
                            "type": "array",
                            "items": {
                                "$ref": "#/$defs/ideation_node"
                            }
                        },
                        "theme": {
                            "type": "array",
                            "items": {
                                "$ref": "#/$defs/ideation_node"
                            }
                        },
                        "plot": {
                            "type": "array",
                            "items": {
                                "$ref": "#/$defs/ideation_node"
                            }
                        },
                        "genre": {
                            "type": "array",
                            "items": {
                                "$ref": "#/$defs/ideation_node"
                            }
                        }
                    },
                    "required": [
                        "character",
                        "theme",
                        "plot",
                        "genre"
                    ],
                    "additionalProperties": false
                },
                "narratives": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "description": "A narrative is a Dramatica storyform: a single, complete argument structure within the story, expressed through subtext and storytelling layers.",
                        "properties": {
                            "id": {
                                "type": "string"
                            },
                            "title": {
                                "type": "string"
                            },
                            "status": {
                                "type": "string",
                                "description": "Optional narrative lifecycle state. When omitted, consumers may treat as complete.",
                                "enum": [
                                    "candidate",
                                    "draft",
                                    "complete"
                                ]
                            },
                            "subtext": {
                                "type": "object",
                                "properties": {
                                    "perspectives": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "$ref": "#/$defs/perspective_id"
                                                },
                                                "author_structural_pov": {
                                                    "type": "string",
                                                    "enum": [
                                                        "i",
                                                        "you",
                                                        "we",
                                                        "they"
                                                    ]
                                                },
                                                "summary": {
                                                    "type": "string"
                                                },
                                                "storytelling": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "id",
                                                "author_structural_pov",
                                                "summary",
                                                "storytelling"
                                            ],
                                            "additionalProperties": false
                                        }
                                    },
                                    "players": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "$ref": "#/$defs/player_id"
                                                },
                                                "name": {
                                                    "type": "string"
                                                },
                                                "role": {
                                                    "type": "string"
                                                },
                                                "visual": {
                                                    "type": "string"
                                                },
                                                "audio": {
                                                    "type": "string"
                                                },
                                                "summary": {
                                                    "type": "string"
                                                },
                                                "bio": {
                                                    "type": "string"
                                                },
                                                "storytelling": {
                                                    "type": "string"
                                                },
                                                "motivations": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "narrative_function": {
                                                                "$ref": "#/$defs/canonical_narrative_function"
                                                            },
                                                            "illustration": {
                                                                "type": "string"
                                                            },
                                                            "storytelling": {
                                                                "type": "string"
                                                            }
                                                        },
                                                        "required": [
                                                            "narrative_function",
                                                            "illustration",
                                                            "storytelling"
                                                        ],
                                                        "additionalProperties": false
                                                    }
                                                },
                                                "perspectives": {
                                                    "type": "array",
                                                    "items": {
                                                        "$ref": "#/$defs/perspective_link"
                                                    }
                                                }
                                            },
                                            "required": [
                                                "id",
                                                "name",
                                                "role",
                                                "visual",
                                                "audio",
                                                "summary",
                                                "bio",
                                                "storytelling",
                                                "motivations",
                                                "perspectives"
                                            ],
                                            "additionalProperties": false
                                        }
                                    },
                                    "dynamics": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "string"
                                                },
                                                "dynamic": {
                                                    "type": "string",
                                                    "enum": [
                                                        "main_character_resolve",
                                                        "influence_character_resolve",
                                                        "main_character_growth",
                                                        "main_character_approach",
                                                        "problem_solving_style",
                                                        "story_limit",
                                                        "story_driver",
                                                        "story_outcome",
                                                        "story_judgment"
                                                    ]
                                                },
                                                "vector": {
                                                    "type": "string",
                                                    "enum": [
                                                        "change",
                                                        "steadfast",
                                                        "stop",
                                                        "start",
                                                        "do_er",
                                                        "be_er",
                                                        "linear",
                                                        "holistic",
                                                        "optionlock",
                                                        "timelock",
                                                        "action",
                                                        "decision",
                                                        "success",
                                                        "failure",
                                                        "good",
                                                        "bad"
                                                    ]
                                                },
                                                "summary": {
                                                    "type": "string"
                                                },
                                                "storytelling": {
                                                    "type": "string"
                                                },
                                                "custom_dynamic": {
                                                    "type": "string"
                                                },
                                                "custom_dynamic_namespace": {
                                                    "type": "object",
                                                    "additionalProperties": {
                                                        "type": "string"
                                                    }
                                                },
                                                "custom_vector": {
                                                    "type": "string"
                                                },
                                                "custom_vector_namespace": {
                                                    "type": "object",
                                                    "additionalProperties": {
                                                        "type": "string"
                                                    }
                                                }
                                            },
                                            "required": [
                                                "id",
                                                "dynamic",
                                                "vector",
                                                "summary",
                                                "storytelling"
                                            ],
                                            "additionalProperties": false
                                        }
                                    },
                                    "storypoints": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "string"
                                                },
                                                "appreciation": {
                                                    "$ref": "#/$defs/canonical_appreciation"
                                                },
                                                "narrative_function": {
                                                    "$ref": "#/$defs/canonical_narrative_function"
                                                },
                                                "illustration": {
                                                    "type": "string"
                                                },
                                                "summary": {
                                                    "type": "string"
                                                },
                                                "storytelling": {
                                                    "type": "string"
                                                },
                                                "perspectives": {
                                                    "type": "array",
                                                    "items": {
                                                        "$ref": "#/$defs/perspective_link"
                                                    }
                                                },
                                                "throughline": {
                                                    "type": "string",
                                                    "description": "Optional throughline label for grouping and round-trip stability when perspective refs are absent.",
                                                    "enum": [
                                                        "Objective Story",
                                                        "Main Character",
                                                        "Influence Character",
                                                        "Relationship Story"
                                                    ]
                                                },
                                                "custom_appreciation": {
                                                    "type": "string"
                                                },
                                                "custom_appreciation_namespace": {
                                                    "type": "object",
                                                    "additionalProperties": {
                                                        "type": "string"
                                                    }
                                                },
                                                "custom_narrative_function": {
                                                    "type": "string"
                                                },
                                                "custom_narrative_function_namespace": {
                                                    "type": "object",
                                                    "additionalProperties": {
                                                        "type": "string"
                                                    }
                                                }
                                            },
                                            "required": [
                                                "id",
                                                "appreciation",
                                                "illustration",
                                                "summary",
                                                "storytelling",
                                                "perspectives"
                                            ],
                                            "additionalProperties": false
                                        }
                                    },
                                    "storybeats": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "$ref": "#/$defs/stable_id"
                                                },
                                                "appreciation": {
                                                    "type": "string",
                                                    "description": "Optional derived structural label, typically throughline + scope + sequence (for example, Objective Story Signpost 1)."
                                                },
                                                "scope": {
                                                    "type": "string",
                                                    "enum": [
                                                        "signpost",
                                                        "progression",
                                                        "event"
                                                    ]
                                                },
                                                "sequence": {
                                                    "type": "integer",
                                                    "minimum": 1
                                                },
                                                "throughline": {
                                                    "type": "string",
                                                    "description": "Optional throughline label for grouping."
                                                },
                                                "narrative_function": {
                                                    "$ref": "#/$defs/canonical_narrative_function"
                                                },
                                                "summary": {
                                                    "type": "string"
                                                },
                                                "storytelling": {
                                                    "type": "string"
                                                },
                                                "perspectives": {
                                                    "type": "array",
                                                    "items": {
                                                        "$ref": "#/$defs/perspective_link"
                                                    }
                                                },
                                                "custom_narrative_function": {
                                                    "type": "string"
                                                },
                                                "custom_narrative_function_namespace": {
                                                    "type": "object",
                                                    "additionalProperties": {
                                                        "type": "string"
                                                    }
                                                }
                                            },
                                            "required": [
                                                "id",
                                                "scope",
                                                "sequence",
                                                "summary",
                                                "storytelling",
                                                "perspectives"
                                            ],
                                            "additionalProperties": false,
                                            "allOf": [
                                                {
                                                    "if": {
                                                        "properties": {
                                                            "scope": {
                                                                "const": "signpost"
                                                            }
                                                        }
                                                    },
                                                    "then": {
                                                        "properties": {
                                                            "sequence": {
                                                                "maximum": 4
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "if": {
                                                        "properties": {
                                                            "scope": {
                                                                "const": "progression"
                                                            }
                                                        }
                                                    },
                                                    "then": {
                                                        "properties": {
                                                            "sequence": {
                                                                "maximum": 16
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "if": {
                                                        "properties": {
                                                            "scope": {
                                                                "const": "event"
                                                            }
                                                        }
                                                    },
                                                    "then": {
                                                        "properties": {
                                                            "sequence": {
                                                                "maximum": 64
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                },
                                "required": [
                                    "perspectives",
                                    "players",
                                    "dynamics",
                                    "storypoints",
                                    "storybeats"
                                ],
                                "additionalProperties": false
                            },
                            "storytelling": {
                                "type": "object",
                                "properties": {
                                    "overviews": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "$ref": "#/$defs/overview_id"
                                                },
                                                "label": {
                                                    "$ref": "#/$defs/overview_label"
                                                },
                                                "summary": {
                                                    "type": "string"
                                                },
                                                "storytelling": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "id",
                                                "label",
                                                "summary",
                                                "storytelling"
                                            ],
                                            "additionalProperties": false
                                        }
                                    },
                                    "moments": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "string"
                                                },
                                                "summary": {
                                                    "type": "string"
                                                },
                                                "synopsis": {
                                                    "type": "string"
                                                },
                                                "setting": {
                                                    "type": "string"
                                                },
                                                "setting_id": {
                                                    "$ref": "#/$defs/setting_id",
                                                    "description": "Optional reference to a story.settings[] entry for this Moment. Use with setting to avoid repeating shared place details while preserving the Moment-specific setting prose."
                                                },
                                                "timing": {
                                                    "type": "string"
                                                },
                                                "imperatives": {
                                                    "type": "string"
                                                },
                                                "act": {
                                                    "type": "integer",
                                                    "minimum": 1
                                                },
                                                "order": {
                                                    "type": "integer",
                                                    "minimum": 0
                                                },
                                                "maximum_steps": {
                                                    "type": "integer",
                                                    "minimum": 1
                                                },
                                                "fabric": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "type": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "space",
                                                                    "time"
                                                                ]
                                                            },
                                                            "limit": {
                                                                "type": "integer"
                                                            }
                                                        },
                                                        "required": [
                                                            "type",
                                                            "limit"
                                                        ],
                                                        "additionalProperties": false
                                                    }
                                                },
                                                "audience_experiential_pov": {
                                                    "type": "string",
                                                    "enum": [
                                                        "first_person_central",
                                                        "first_person_peripheral",
                                                        "second_person",
                                                        "third_person_limited",
                                                        "third_person_objective",
                                                        "third_person_omniscient"
                                                    ]
                                                },
                                                "storybeats": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "sequence": {
                                                                "type": "integer"
                                                            },
                                                            "storybeat_id": {
                                                                "$ref": "#/$defs/stable_id"
                                                            }
                                                        },
                                                        "required": [
                                                            "sequence",
                                                            "storybeat_id"
                                                        ],
                                                        "additionalProperties": false
                                                    }
                                                }
                                            },
                                            "required": [
                                                "summary",
                                                "synopsis",
                                                "setting",
                                                "timing",
                                                "imperatives",
                                                "storybeats"
                                            ],
                                            "additionalProperties": false
                                        }
                                    }
                                },
                                "required": [
                                    "overviews",
                                    "moments"
                                ],
                                "additionalProperties": false
                            }
                        },
                        "required": [
                            "id",
                            "title",
                            "subtext",
                            "storytelling"
                        ],
                        "additionalProperties": false
                    }
                }
            },
            "required": [
                "id",
                "title",
                "logline",
                "created_at",
                "narratives"
            ],
            "additionalProperties": false
        }
    },
    "required": [
        "schema_version",
        "story"
    ],
    "additionalProperties": false,
    "$defs": {
        "uuid": {
            "type": "string",
            "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
            "description": "Generic UUID."
        },
        "stable_id": {
            "description": "Generic UUID or canonical story_, narrative_, or beat_ identifier.",
            "anyOf": [
                {
                    "$ref": "#/$defs/uuid"
                },
                {
                    "type": "string",
                    "pattern": "^(?:story|narrative|beat)_[A-Za-z0-9][A-Za-z0-9_-]*$"
                }
            ]
        },
        "perspective_id": {
            "type": "string",
            "description": "Opaque identifier for a perspective. Plain UUIDs are fine; type prefixes are not required."
        },
        "player_id": {
            "type": "string",
            "description": "Opaque identifier for a player. Plain UUIDs are fine; type prefixes are not required."
        },
        "overview_id": {
            "type": "string",
            "description": "Opaque identifier for an overview. Plain UUIDs are fine; type prefixes are not required."
        },
        "setting_id": {
            "type": "string",
            "description": "Opaque identifier for a story-level setting. Plain UUIDs are fine; setting_ prefixes are optional."
        },
        "perspective_link": {
            "type": "object",
            "properties": {
                "perspective_id": {
                    "$ref": "#/$defs/perspective_id"
                }
            },
            "required": [
                "perspective_id"
            ],
            "additionalProperties": false
        },
        "overview_label": {
            "type": "string",
            "enum": [
                "Logline",
                "Genre",
                "Blended Throughlines"
            ],
            "description": "Canonical Title Case overview label emitted by exporters."
        },
        "ideation_node": {
            "type": "object",
            "description": "Lightweight ideation node for pre-narrative concept capture.",
            "properties": {
                "id": {
                    "type": "string"
                },
                "summary": {
                    "type": "string"
                },
                "title": {
                    "type": "string"
                },
                "notes": {
                    "type": "string"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "id",
                "summary"
            ]
        },
        "canonical_appreciation": {
            "type": "string",
            "enum": [
                "Argument Approach",
                "Argument Objective",
                "Argument Resolution",
                "Character Evolution",
                "Character Orientation",
                "Character Intentions",
                "Character Repercussions",
                "Character Adaptations",
                "Character Affectations",
                "Character Engagements",
                "Character Perks",
                "Character Pressures",
                "Character Forebodings",
                "Concluding Story Driver",
                "Emotional Outcome",
                "Essence",
                "Fourth Story Driver",
                "Influence Character Adjustment",
                "Influence Character Approach",
                "Influence Character Baseline",
                "Influence Character Benchmark",
                "Influence Character Concern",
                "Influence Character Condition",
                "Influence Character Critical Flaw",
                "Influence Character Domain",
                "Influence Character Event 1",
                "Influence Character Event 10",
                "Influence Character Event 11",
                "Influence Character Event 12",
                "Influence Character Event 13",
                "Influence Character Event 14",
                "Influence Character Event 15",
                "Influence Character Event 16",
                "Influence Character Event 17",
                "Influence Character Event 18",
                "Influence Character Event 19",
                "Influence Character Event 2",
                "Influence Character Event 20",
                "Influence Character Event 21",
                "Influence Character Event 22",
                "Influence Character Event 23",
                "Influence Character Event 24",
                "Influence Character Event 25",
                "Influence Character Event 26",
                "Influence Character Event 27",
                "Influence Character Event 28",
                "Influence Character Event 29",
                "Influence Character Event 3",
                "Influence Character Event 30",
                "Influence Character Event 31",
                "Influence Character Event 32",
                "Influence Character Event 33",
                "Influence Character Event 34",
                "Influence Character Event 35",
                "Influence Character Event 36",
                "Influence Character Event 37",
                "Influence Character Event 38",
                "Influence Character Event 39",
                "Influence Character Event 4",
                "Influence Character Event 40",
                "Influence Character Event 41",
                "Influence Character Event 42",
                "Influence Character Event 43",
                "Influence Character Event 44",
                "Influence Character Event 45",
                "Influence Character Event 46",
                "Influence Character Event 47",
                "Influence Character Event 48",
                "Influence Character Event 49",
                "Influence Character Event 5",
                "Influence Character Event 50",
                "Influence Character Event 51",
                "Influence Character Event 52",
                "Influence Character Event 53",
                "Influence Character Event 54",
                "Influence Character Event 55",
                "Influence Character Event 56",
                "Influence Character Event 57",
                "Influence Character Event 58",
                "Influence Character Event 59",
                "Influence Character Event 6",
                "Influence Character Event 60",
                "Influence Character Event 61",
                "Influence Character Event 62",
                "Influence Character Event 63",
                "Influence Character Event 64",
                "Influence Character Event 7",
                "Influence Character Event 8",
                "Influence Character Event 9",
                "Influence Character Evolution",
                "Influence Character Flow",
                "Influence Character Introduction",
                "Influence Character Issue",
                "Influence Character Pivotal Element",
                "Influence Character Problem",
                "Influence Character Progression 1",
                "Influence Character Progression 10",
                "Influence Character Progression 11",
                "Influence Character Progression 12",
                "Influence Character Progression 13",
                "Influence Character Progression 14",
                "Influence Character Progression 15",
                "Influence Character Progression 16",
                "Influence Character Progression 2",
                "Influence Character Progression 3",
                "Influence Character Progression 4",
                "Influence Character Progression 5",
                "Influence Character Progression 6",
                "Influence Character Progression 7",
                "Influence Character Progression 8",
                "Influence Character Progression 9",
                "Influence Character Resistance",
                "Influence Character Resolution",
                "Influence Character Resolve",
                "Influence Character Response",
                "Influence Character Signpost 1",
                "Influence Character Signpost 2",
                "Influence Character Signpost 3",
                "Influence Character Signpost 4",
                "Influence Character Solution",
                "Influence Character Symptom",
                "Influence Character Throughline",
                "Influence Character Unique Ability",
                "Initial Story Driver",
                "Main Character Adjustment",
                "Main Character Approach",
                "Main Character Baseline",
                "Main Character Benchmark",
                "Main Character Concern",
                "Main Character Condition",
                "Main Character Critical Flaw",
                "Main Character Domain",
                "Main Character Event 1",
                "Main Character Event 10",
                "Main Character Event 11",
                "Main Character Event 12",
                "Main Character Event 13",
                "Main Character Event 14",
                "Main Character Event 15",
                "Main Character Event 16",
                "Main Character Event 17",
                "Main Character Event 18",
                "Main Character Event 19",
                "Main Character Event 2",
                "Main Character Event 20",
                "Main Character Event 21",
                "Main Character Event 22",
                "Main Character Event 23",
                "Main Character Event 24",
                "Main Character Event 25",
                "Main Character Event 26",
                "Main Character Event 27",
                "Main Character Event 28",
                "Main Character Event 29",
                "Main Character Event 3",
                "Main Character Event 30",
                "Main Character Event 31",
                "Main Character Event 32",
                "Main Character Event 33",
                "Main Character Event 34",
                "Main Character Event 35",
                "Main Character Event 36",
                "Main Character Event 37",
                "Main Character Event 38",
                "Main Character Event 39",
                "Main Character Event 4",
                "Main Character Event 40",
                "Main Character Event 41",
                "Main Character Event 42",
                "Main Character Event 43",
                "Main Character Event 44",
                "Main Character Event 45",
                "Main Character Event 46",
                "Main Character Event 47",
                "Main Character Event 48",
                "Main Character Event 49",
                "Main Character Event 5",
                "Main Character Event 50",
                "Main Character Event 51",
                "Main Character Event 52",
                "Main Character Event 53",
                "Main Character Event 54",
                "Main Character Event 55",
                "Main Character Event 56",
                "Main Character Event 57",
                "Main Character Event 58",
                "Main Character Event 59",
                "Main Character Event 6",
                "Main Character Event 60",
                "Main Character Event 61",
                "Main Character Event 62",
                "Main Character Event 63",
                "Main Character Event 64",
                "Main Character Event 7",
                "Main Character Event 8",
                "Main Character Event 9",
                "Main Character Evolution",
                "Main Character Flow",
                "Main Character Growth",
                "Main Character Introduction",
                "Main Character Issue",
                "Main Character Pivotal Element",
                "Main Character Problem",
                "Main Character Problem-solving Style",
                "Main Character Progression 1",
                "Main Character Progression 10",
                "Main Character Progression 11",
                "Main Character Progression 12",
                "Main Character Progression 13",
                "Main Character Progression 14",
                "Main Character Progression 15",
                "Main Character Progression 16",
                "Main Character Progression 2",
                "Main Character Progression 3",
                "Main Character Progression 4",
                "Main Character Progression 5",
                "Main Character Progression 6",
                "Main Character Progression 7",
                "Main Character Progression 8",
                "Main Character Progression 9",
                "Main Character Resistance",
                "Main Character Resolution",
                "Main Character Resolve",
                "Main Character Response",
                "Main Character Signpost 1",
                "Main Character Signpost 2",
                "Main Character Signpost 3",
                "Main Character Signpost 4",
                "Main Character Solution",
                "Main Character Symptom",
                "Main Character Throughline",
                "Main Character Unique Ability",
                "Midpoint Story Driver",
                "Nature",
                "Objective Premise Method",
                "Objective Story Adjustment",
                "Objective Story Benchmark",
                "Objective Story Catalyst",
                "Objective Story Concern",
                "Objective Story Condition",
                "Objective Story Domain",
                "Objective Story Event 1",
                "Objective Story Event 10",
                "Objective Story Event 11",
                "Objective Story Event 12",
                "Objective Story Event 13",
                "Objective Story Event 14",
                "Objective Story Event 15",
                "Objective Story Event 16",
                "Objective Story Event 17",
                "Objective Story Event 18",
                "Objective Story Event 19",
                "Objective Story Event 2",
                "Objective Story Event 20",
                "Objective Story Event 21",
                "Objective Story Event 22",
                "Objective Story Event 23",
                "Objective Story Event 24",
                "Objective Story Event 25",
                "Objective Story Event 26",
                "Objective Story Event 27",
                "Objective Story Event 28",
                "Objective Story Event 29",
                "Objective Story Event 3",
                "Objective Story Event 30",
                "Objective Story Event 31",
                "Objective Story Event 32",
                "Objective Story Event 33",
                "Objective Story Event 34",
                "Objective Story Event 35",
                "Objective Story Event 36",
                "Objective Story Event 37",
                "Objective Story Event 38",
                "Objective Story Event 39",
                "Objective Story Event 4",
                "Objective Story Event 40",
                "Objective Story Event 41",
                "Objective Story Event 42",
                "Objective Story Event 43",
                "Objective Story Event 44",
                "Objective Story Event 45",
                "Objective Story Event 46",
                "Objective Story Event 47",
                "Objective Story Event 48",
                "Objective Story Event 49",
                "Objective Story Event 5",
                "Objective Story Event 50",
                "Objective Story Event 51",
                "Objective Story Event 52",
                "Objective Story Event 53",
                "Objective Story Event 54",
                "Objective Story Event 55",
                "Objective Story Event 56",
                "Objective Story Event 57",
                "Objective Story Event 58",
                "Objective Story Event 59",
                "Objective Story Event 6",
                "Objective Story Event 60",
                "Objective Story Event 61",
                "Objective Story Event 62",
                "Objective Story Event 63",
                "Objective Story Event 64",
                "Objective Story Event 7",
                "Objective Story Event 8",
                "Objective Story Event 9",
                "Objective Story Flow",
                "Objective Story Inhibitor",
                "Objective Story Issue",
                "Objective Story Problem",
                "Objective Story Progression 1",
                "Objective Story Progression 10",
                "Objective Story Progression 11",
                "Objective Story Progression 12",
                "Objective Story Progression 13",
                "Objective Story Progression 14",
                "Objective Story Progression 15",
                "Objective Story Progression 16",
                "Objective Story Progression 2",
                "Objective Story Progression 3",
                "Objective Story Progression 4",
                "Objective Story Progression 5",
                "Objective Story Progression 6",
                "Objective Story Progression 7",
                "Objective Story Progression 8",
                "Objective Story Progression 9",
                "Objective Story Resistance",
                "Objective Story Response",
                "Objective Story Signpost 1",
                "Objective Story Signpost 2",
                "Objective Story Signpost 3",
                "Objective Story Signpost 4",
                "Objective Story Solution",
                "Objective Story Symptom",
                "Objective Story Throughline",
                "Reach",
                "Relationship Story Adjustment",
                "Relationship Story Benchmark",
                "Relationship Story Catalyst",
                "Relationship Story Concern",
                "Relationship Story Condition",
                "Relationship Story Domain",
                "Relationship Story Event 1",
                "Relationship Story Event 10",
                "Relationship Story Event 11",
                "Relationship Story Event 12",
                "Relationship Story Event 13",
                "Relationship Story Event 14",
                "Relationship Story Event 15",
                "Relationship Story Event 16",
                "Relationship Story Event 17",
                "Relationship Story Event 18",
                "Relationship Story Event 19",
                "Relationship Story Event 2",
                "Relationship Story Event 20",
                "Relationship Story Event 21",
                "Relationship Story Event 22",
                "Relationship Story Event 23",
                "Relationship Story Event 24",
                "Relationship Story Event 25",
                "Relationship Story Event 26",
                "Relationship Story Event 27",
                "Relationship Story Event 28",
                "Relationship Story Event 29",
                "Relationship Story Event 3",
                "Relationship Story Event 30",
                "Relationship Story Event 31",
                "Relationship Story Event 32",
                "Relationship Story Event 33",
                "Relationship Story Event 34",
                "Relationship Story Event 35",
                "Relationship Story Event 36",
                "Relationship Story Event 37",
                "Relationship Story Event 38",
                "Relationship Story Event 39",
                "Relationship Story Event 4",
                "Relationship Story Event 40",
                "Relationship Story Event 41",
                "Relationship Story Event 42",
                "Relationship Story Event 43",
                "Relationship Story Event 44",
                "Relationship Story Event 45",
                "Relationship Story Event 46",
                "Relationship Story Event 47",
                "Relationship Story Event 48",
                "Relationship Story Event 49",
                "Relationship Story Event 5",
                "Relationship Story Event 50",
                "Relationship Story Event 51",
                "Relationship Story Event 52",
                "Relationship Story Event 53",
                "Relationship Story Event 54",
                "Relationship Story Event 55",
                "Relationship Story Event 56",
                "Relationship Story Event 57",
                "Relationship Story Event 58",
                "Relationship Story Event 59",
                "Relationship Story Event 6",
                "Relationship Story Event 60",
                "Relationship Story Event 61",
                "Relationship Story Event 62",
                "Relationship Story Event 63",
                "Relationship Story Event 64",
                "Relationship Story Event 7",
                "Relationship Story Event 8",
                "Relationship Story Event 9",
                "Relationship Story Flow",
                "Relationship Story Growth",
                "Relationship Story Inhibitor",
                "Relationship Story Issue",
                "Relationship Story Problem",
                "Relationship Story Progression 1",
                "Relationship Story Progression 10",
                "Relationship Story Progression 11",
                "Relationship Story Progression 12",
                "Relationship Story Progression 13",
                "Relationship Story Progression 14",
                "Relationship Story Progression 15",
                "Relationship Story Progression 16",
                "Relationship Story Progression 2",
                "Relationship Story Progression 3",
                "Relationship Story Progression 4",
                "Relationship Story Progression 5",
                "Relationship Story Progression 6",
                "Relationship Story Progression 7",
                "Relationship Story Progression 8",
                "Relationship Story Progression 9",
                "Relationship Story Resistance",
                "Relationship Story Response",
                "Relationship Story Signpost 1",
                "Relationship Story Signpost 2",
                "Relationship Story Signpost 3",
                "Relationship Story Signpost 4",
                "Relationship Story Solution",
                "Relationship Story Symptom",
                "Relationship Story Throughline",
                "Second Story Driver",
                "Story Consequence",
                "Story Constraints",
                "Story Costs",
                "Story Dilemma",
                "Story Dividends",
                "Story Driver",
                "Story Ending",
                "Story Ennui",
                "Story Excitement",
                "Story Forewarnings",
                "Story Goal",
                "Story Habituations",
                "Story Intention",
                "Story Internalizations",
                "Story Judgment",
                "Story Limit",
                "Story Outcome",
                "Story Overwhelm",
                "Story Preconditions",
                "Story Prerequisites",
                "Story Pressure",
                "Story Reach",
                "Story Requirements",
                "Story Socializations",
                "Subjective Premise Balance Element",
                "Subjective Premise Element",
                "Tendency"
            ]
        },
        "canonical_narrative_function": {
            "type": "string",
            "enum": [
                "Ability",
                "Acceptance",
                "Accurate",
                "Actuality",
                "Analysis",
                "Appraisal",
                "Approach",
                "Attempt",
                "Attitude",
                "Attract",
                "Avoid",
                "Aware",
                "Becoming",
                "Being",
                "Cause",
                "Certainty",
                "Change",
                "Chaos",
                "Choice",
                "Circumstances",
                "Closure",
                "Commitment",
                "Conceiving",
                "Conceptualizing",
                "Conditioning",
                "Confidence",
                "Conscience",
                "Conscious",
                "Consider",
                "Control",
                "Deduction",
                "Deficiency",
                "Delay",
                "Denial",
                "Desire",
                "Destiny",
                "Determination",
                "Disbelief",
                "Doing",
                "Doubt",
                "Dream",
                "Effect",
                "Ending",
                "Enlightenment",
                "Equity",
                "Evaluation",
                "Evidence",
                "Expectation",
                "Expediency",
                "Experience",
                "Fact",
                "Faith",
                "Falsehood",
                "Fantasy",
                "Fate",
                "Feeling",
                "Future",
                "Help",
                "Hinder",
                "Hope",
                "Hunch",
                "Inaction",
                "Induction",
                "Inequity",
                "Inertia",
                "Instinct",
                "Interdiction",
                "Interpretation",
                "Investigation",
                "Knowledge",
                "Learning",
                "Logic",
                "Memory",
                "Mind",
                "Need",
                "Non-acceptance",
                "Non-accurate",
                "Obligation",
                "Obtaining",
                "Openness",
                "Oppose",
                "Order",
                "Past",
                "Perception",
                "Permission",
                "Physics",
                "Possibility",
                "Potentiality",
                "Preconception",
                "Preconditions",
                "Preconscious",
                "Prediction",
                "Prerequisites",
                "Present",
                "Proaction",
                "Probability",
                "Process",
                "Production",
                "Progress",
                "Projection",
                "Protection",
                "Proven",
                "Psychology",
                "Pursuit",
                "Rationalization",
                "Re-evaluation",
                "Reaction",
                "Reappraisal",
                "Reconsider",
                "Reduction",
                "Repel",
                "Responsibility",
                "Result",
                "Security",
                "Self Interest",
                "Self-aware",
                "Selflessness",
                "Sense of Self",
                "Senses",
                "Situation",
                "Skill",
                "Speculation",
                "State of Being",
                "Strategy",
                "Subconscious",
                "Support",
                "Suspicion",
                "Temptation",
                "Test",
                "Theory",
                "Thought",
                "Threat",
                "Trust",
                "Truth",
                "Uncontrolled",
                "Understanding",
                "Unending",
                "Universe",
                "Unproven",
                "Value",
                "Wisdom",
                "Work",
                "Worry",
                "Worth"
            ]
        }
    }
}
```

## google-deepmind/dramatron

Source: `open_source_repos/dramatron/colab/dramatron.ipynb`. This repository does not include a standalone `dramatron.py`; the main implementation is inside the Colab notebook.

Pipeline summary:

- Input starts with a user-provided logline/storyline.

- `StoryGenerator.step()` advances through hierarchical levels: title, characters, scenes, places, then dialogs.

- Title generation uses `TITLES_PROMPT + storyline + TITLE_ELEMENT`.

- Character generation uses `CHARACTERS_PROMPT + storyline`, then parses `Characters`.

- Scene generation uses `SCENE_PROMPT + storyline + character descriptions + SCENES_MARKER`, then parses `Scenes`.

- Place descriptions are generated once per unique scene place from `SETTING_PROMPT + storyline + Place.format_prefix(place_name)`.

- Dialog generation is per scene and chains place, characters in the beat, plot element, storyline summary, previous beat, current beat, and `DIALOG_MARKER`.

- The generator records prompt strings in `self.prompts` and human edits/completions in `self.interventions`.


### Prompt Chaining Logic Excerpt

```python
def generate_title(storyline: str,
                   prefixes: Dict[str, str],
                   client: LanguageAPI,
                   filter: Optional[FilterAPI] = None,
                   seed: Optional[int] = None,
                   num_samples: int = 1):
  """Generate a title given a storyline, and client."""

  # Combine the prompt and storyline as a helpful generation prefix
  titles_prefix = prefixes['TITLES_PROMPT'] + storyline + ' ' + TITLE_ELEMENT
  title_text = generate_text_no_loop(
      generation_prompt=titles_prefix,
      client=client,
      filter=filter,
      sample_length=SAMPLE_LENGTH_TITLE,
      seed=seed,
      num_samples=num_samples)
  title = Title.from_string(TITLE_ELEMENT + title_text)
  return (title, titles_prefix)

def generate_characters(
    storyline: str,
    prefixes: Dict[str, str],
    client: LanguageAPI,
    filter: Optional[FilterAPI] = None,
    seed: Optional[int] = None,
    max_paragraph_length: int = (MAX_PARAGRAPH_LENGTH_CHARACTERS),
    num_samples: int = 1):
  """Generate characters given a storyline, prompt, and client."""

  # Combine the prompt and storyline as a helpful generation prefix
  characters_prefix = prefixes['CHARACTERS_PROMPT'] + storyline
  characters_text = generate_text(
      generation_prompt=characters_prefix,
      client=client,
      filter=filter,
      seed=seed,
      max_paragraph_length=max_paragraph_length,
      num_samples=num_samples)
  characters = Characters.from_string(characters_text)

  return (characters, characters_prefix)

def generate_scenes(storyline: str,
                    character_descriptions: Dict[str, str],
                    prefixes: Dict[str, str],
                    client: LanguageAPI,
                    filter: Optional[FilterAPI] = None,
                    seed: Optional[int] = None,
                    max_paragraph_length: int = (MAX_PARAGRAPH_LENGTH_SCENES),
                    num_samples: int = 1):
  """Generate scenes given storyline, prompt, main characters, and client."""

  scenes_prefix = prefixes['SCENE_PROMPT'] + storyline + '\n'
  for name in character_descriptions:
    scenes_prefix += character_descriptions[name] + '\n'
  scenes_prefix += '\n' + SCENES_MARKER
  scenes_text = generate_text(
      generation_prompt=scenes_prefix,
      client=client,
      filter=filter,
      seed=seed,
      max_paragraph_length=max_paragraph_length,
      num_samples=num_samples)
  scenes = Scenes.from_string(scenes_text)

  return (scenes, scenes_prefix)

def generate_place_descriptions(storyline: str,
                                scenes: Scenes,
                                prefixes: Dict[str, str],
                                client: LanguageAPI,
                                filter: Optional[FilterAPI] = None,
                                seed: Optional[int] = None,
                                num_samples: int = 1):
  """Generate a place description given a scene object and a client."""

  place_descriptions = {}

  # Get unique place names from the scenes.
  unique_place_names = set([scene.place for scene in scenes.scenes])

  # Build a unique place prefix prompt.
  place_prefix = prefixes['SETTING_PROMPT'] + storyline + '\n'

  # Build a list of place descriptions for each place
  place_prefixes = []
  for place_name in unique_place_names:
    place_suffix = Place.format_prefix(place_name)
    place_text = generate_text(
        generation_prompt=place_prefix + place_suffix,
        client=client,
        filter=filter,
        sample_length=SAMPLE_LENGTH_PLACE,
        seed=seed,
        num_samples=num_samples)
    place_text = place_suffix + place_text
    place_descriptions[place_name] = Place.from_string(place_name, place_text)
    place_prefixes.append(place_prefix + place_suffix)

  return (place_descriptions, place_prefixes)

def prefix_summary(storyline: str,
                   scenes: List[Scene],
                   concatenate_scenes_in_summary: bool = False) -> str:
  """Assemble the summary part of the dialog prefix."""

  summary = SUMMARY_ELEMENT + storyline + '\n'
  if len(scenes) > 1:
    summary += PREVIOUS_ELEMENT + scenes[len(scenes) - 2].beat + '\n'
  return summary

def generate_dialog(storyline: str,
                    scenes: List[Scene],
                    character_descriptions: Dict[str, str],
                    place_descriptions: Dict[str, Place],
                    prefixes: Dict[str, str],
                    max_paragraph_length: int,
                    client: LanguageAPI,
                    filter: Optional[FilterAPI] = None,
                    max_num_repetitions: Optional[int] = None,
                    seed: Optional[int] = None,
                    num_samples: int = 1):
  """Generate dialog given a scene object and a client."""

  scene = scenes[-1]

  place_t = PLACE_ELEMENT + scene.place + '\n'
  if scene.place in place_descriptions:
    place_description = place_descriptions[scene.place]
    if place_description:
      place_t += DESCRIPTION_ELEMENT + place_description.description
      place_t += '\n'

  # Build the characters information for the scene
  characters_t = ''
  if character_descriptions:
    characters_t += CHARACTERS_ELEMENT
    for name in character_descriptions:
      if name in scene.beat:
        characters_t += character_descriptions[name] + '\n'

  plot_element_t = PLOT_ELEMENT + scene.plot_element + '\n'

  summary_t = prefix_summary(
      storyline, scenes, concatenate_scenes_in_summary=False)

  beat_t = BEAT_ELEMENT + scene.beat + '\n'

  dialog_prefix = (
      prefixes['DIALOG_PROMPT'] + place_t + characters_t + plot_element_t +
      summary_t + beat_t)
  dialog_prefix += '\n' + DIALOG_MARKER + '\n'

  dialog = generate_text(
      generation_prompt=dialog_prefix,
      client=client,
      filter=filter,
      seed=seed,
      max_paragraph_length=max_paragraph_length,
      max_num_repetitions=max_num_repetitions,
      num_samples=num_samples)

  return (dialog, dialog_prefix)


def diff_prompt_change_str(prompt_before: str, prompt_after: str) -> str:
  """Return a text diff on prompt sets `prompt_before` and `prompt_after`."""

  # For the current element, compare prompts line by line.
  res = difflib.unified_diff(
      prompt_before.split('\n'), prompt_after.split('\n'))
  diff = ''
  for line in res:
    line = line.strip()
    if line != '---' and line != '+++' and not line.startswith('@@'):
      if len(line) > 1 and (line.startswith('+') or line.startswith('-')):
        diff += line + '\n'
  if diff.endswith('\n'):
    diff = diff[:-1]
  return diff


def diff_prompt_change_list(prompt_before: List[str],
                            prompt_after: List[str]) -> str:
  """Return a text diff on prompt sets `prompt_before` and `prompt_after`."""

  # Handle deletions and insertions.
  len_before = len(prompt_before)
  len_after = len(prompt_after)
  if len_before > len_after:
    return 'Deleted element'
  if len_before < len_after:
    return 'Added new element'

  diffs = [
      diff_prompt_change_str(a, b)
      for (a, b) in zip(prompt_before, prompt_after)
  ]
  return '\n'.join([diff for diff in diffs if len(diff) > 0])


def diff_prompt_change_scenes(prompt_before: List[Scene],
                              prompt_after: List[Scene]) -> str:
  """Return a text diff on prompt sets `prompt_before` and `prompt_after`."""

  # Handle deletions and insertions.
  len_before = len(prompt_before)
  len_after = len(prompt_after)
  if len_before > len_after:
    return 'Deleted element'
  if len_before < len_after:
    return 'Added new element'

  diffs = [
      diff_prompt_change_list([a.place, a.plot_element, a.beat],
                              [b.place, b.plot_element, b.beat])
      for (a, b) in zip(prompt_before, prompt_after)
  ]
  return '\n'.join([diff for diff in diffs if len(diff) > 0])


def diff_prompt_change_dict(prompt_before: Dict[str, str],
                            prompt_after: Dict[str, str]) -> str:
  """Return a text diff on prompt sets `prompt_before` and `prompt_after`."""

  # Loop over the keys in the prompts to compare them one by one.
  keys_before = sorted(prompt_before.keys())
  keys_after = sorted(prompt_after.keys())
  diffs = [
      diff_prompt_change_str(a, b) for (a, b) in zip(keys_before, keys_after)
  ]
  diff_keys = '\n'.join([diff for diff in diffs if len(diff) > 0])
  # Loop over the values in the prompts to compare them one by one.
  values_before = sorted(prompt_before.values())
  values_after = sorted(prompt_after.values())
  diffs = [
      diff_prompt_change_str(a, b)
      for (a, b) in zip(values_before, values_after)
  ]
  diff_values = '\n'.join([diff for diff in diffs if len(diff) > 0])
  return diff_keys + diff_values


class StoryGenerator:
  """Generate a story from the provided storyline, using the client provided."""

  level_names = ('storyline', 'title', 'characters', 'scenes', 'places',
                 'dialogs')

  def __init__(
      self,
      storyline: str,
      prefixes: Dict[str, str],
      max_paragraph_length: int = 1024,
      max_paragraph_length_characters: int = (MAX_PARAGRAPH_LENGTH_CHARACTERS),
      max_paragraph_length_scenes: int = (MAX_PARAGRAPH_LENGTH_SCENES),
      num_samples: int = 1,
      client: Optional[LanguageAPI] = None,
      filter: Optional[FilterAPI] = None):
    self._prefixes = prefixes
    self._max_paragraph_length = max_paragraph_length
    self._max_paragraph_length_characters = max_paragraph_length_characters
    self._max_paragraph_length_scenes = max_paragraph_length_scenes
    self._num_samples = num_samples
    self._client = client
    self._filter = filter

    # Prompts and outputs of the hierarchical generator are organised in levels.
    self.prompts = {
        'title': '',
        'characters': '',
        'scenes': '',
        'places': {
            '': ''
        },
        'dialogs': ['']
    }
    self._title = Title('')
    self._characters = Characters({'': ''})
    self._scenes = Scenes([Scene('', '', '')])
    self._places = {'': Place('', '')}
    self._dialogs = ['']

    # History of interventions.
    self.interventions = {}
    self._set_storyline(storyline)

  def _set_storyline(self, storyline: str):
    """Set storyline and initialise the outputs of the generator."""
    self._level = 0

    # Add period to the end of the storyline, unless there is already one there.
    if storyline.find('.') == -1:
      storyline = storyline + '.'
    self._storyline = storyline

    # Keep track of each storyline intervention.
    timestamp = time.time()
    self.interventions[timestamp] = 'STORYLINE\n' + storyline

  @property
  def seed(self):
    return self._client.seed

  @property
  def title(self) -> Title:
    """Return the title."""
    return self._title

  @property
  def characters(self) -> Characters:
    """Return the characters."""
    return self._characters

  @property
  def scenes(self) -> Scenes:
    """Return the title."""
    return self._scenes

  @property
  def places(self) -> Dict[str, Place]:
    """Return the places."""
    return self._places

  @property
  def dialogs(self) -> List[str]:
    """Return the dialogs."""
    return self._dialogs

  def title_str(self) -> str:
    """Return the title as a string."""
    return self._title.title

  def num_scenes(self) -> int:
    """Return the number of scenes."""
    return self._scenes.num_scenes()

  def step(self,
           level: Optional[int] = None,
           seed: Optional[int] = None,
           idx: Optional[int] = None) -> bool:
    """Step down a level in the hierarchical generation of a story."""

    # Move to the next level of hierarchical generation.
    if level is None:
      level = self._level
    if level < 0 or level >= len(self.level_names):
      raise ValueError('Invalid level encountered on step.')
    level += 1
    self._level = level

    # Keep track of each step intervention.
    timestamp = time.time()
    self.interventions[timestamp] = 'STEP ' + str(level) + '\n'

    if level == 1:
      # Step 1: Generate title given a storyline.
      (title, titles_prefix) = generate_title(
          storyline=self._storyline,
          prefixes=self._prefixes,
          client=self._client,
          filter=self._filter,
          num_samples=self._num_samples,
          seed=seed)
      self._title = title
      self.prompts['title'] = titles_prefix
      self.interventions[timestamp] += title.to_string()
      success = len(title.title) > 0
      return success

    if level == 2:
      # Step 2: Generate characters given a storyline.
      (characters, character_prompts) = generate_characters(
          storyline=self._storyline,
          prefixes=self._prefixes,
          client=self._client,
          filter=self._filter,
          num_samples=self._num_samples,
          max_paragraph_length=self._max_paragraph_length_characters,
          seed=seed)
      self._characters = characters
      self.prompts['characters'] = character_prompts
      self.interventions[timestamp] += characters.to_string()
      success = len(characters.character_descriptions) > 0
      return success

    if level == 3:
      # Step 3: Generate sequence of scenes given a storyline and characters.
      characters = self._characters
      (scenes, scene_prompts) = generate_scenes(
          storyline=self._storyline,
          character_descriptions=get_character_descriptions(characters),
          prefixes=self._prefixes,
          client=self._client,
          filter=self._filter,
          num_samples=self._num_samples,
          max_paragraph_length=self._max_paragraph_length_scenes,
          seed=seed)
      self._scenes = scenes
      self.prompts['scenes'] = scene_prompts
      self.interventions[timestamp] += scenes.to_string()
      success = len(scenes.scenes) > 0
      return success

    if level == 4:
      # Step 4: For each scene, generate place descriptions given place name.
      scenes = self._scenes
      (place_descriptions, place_prompts) = generate_place_descriptions(
          storyline=self._storyline,
          scenes=scenes,
          prefixes=self._prefixes,
          client=self._client,
          filter=self._filter,
          num_samples=self._num_samples,
          seed=seed)
      self._places = place_descriptions
      self.prompts['places'] = place_prompts
      for place_name in place_descriptions:
        place = place_descriptions[place_name]
        if place:
          self.interventions[timestamp] += place.to_string()
      num_places = scenes.num_places()
      success = (len(place_descriptions) == num_places) and num_places > 0
      return success

    if level == 5:
      # Step 5: For each scene, generate dialog from scene information.
      title = self._title
      characters = self._characters
      scenes = self._scenes
      place_descriptions = self._places
      if idx is None:
        (dialogs, dialog_prompts) = zip(*[
            generate_dialog(
                storyline=self._storyline,
                scenes=scenes.scenes[:(k + 1)],
                character_descriptions=(characters.character_descriptions),
                place_descriptions=place_descriptions,
                prefixes=self._prefixes,
                max_paragraph_length=self._max_paragraph_length,
                max_num_repetitions=MAX_NUM_REPETITIONS,
                client=self._client,
                filter=self._filter,
                num_samples=self._num_samples,
                seed=seed) for k in range(len(scenes.scenes))
        ])
      else:
        num_scenes = self._scenes.num_scenes()
        while len(self._dialogs) < num_scenes:
          self._dialogs.append('')
        while len(self.prompts['dialogs']) < num_scenes:
          self.prompts['dialogs'].append('')
        if idx >= num_scenes or idx < 0:
          raise ValueError('Invalid scene index.')
        dialogs = self._dialogs
        dialog_prompts = self.prompts['dialogs']
        dialogs[idx], dialog_prompts[idx] = generate_dialog(
            storyline=self._storyline,
            scenes=scenes.scenes[:(idx + 1)],
            character_descriptions=(characters.character_descriptions),
            place_descriptions=place_descriptions,
            prefixes=self._prefixes,
            max_paragraph_length=self._max_paragraph_length,
            max_num_repetitions=MAX_NUM_REPETITIONS,
            client=self._client,
            filter=self._filter,
            num_samples=self._num_samples,
            seed=seed)
      self._dialogs = dialogs
      self.prompts['dialogs'] = dialog_prompts
      for dialog in dialogs:
        self.interventions[timestamp] += str(dialog)
      return True

  def get_story(self):
    if self._characters is not None:
      character_descriptions = get_character_descriptions(self._characters)
    else:
      character_descriptions = None
    return Story(
        storyline=self._storyline,
        title=self._title.title,
        character_descriptions=character_descriptions,
        place_descriptions=self._places,
        scenes=self._scenes,
        dialogs=self._dialogs)

  def rewrite(self, text, level=0, entity=None):
    if level < 0 or level >= len(self.level_names):
      raise ValueError('Invalid level encountered on step.')
    prompt_diff = None

    if level == 0:
      # Step 0: Rewrite the storyline and begin new story.
      prompt_diff = diff_prompt_change_str(self._storyline, text)
      self._set_storyline(text)

    if level == 1:
      # Step 1: Rewrite the title.
      title = Title.from_string(text)
      prompt_diff = diff_prompt_change_str(self._title.title, title.title)
      self._title = title

    if level == 2:
      # Step 2: Rewrite the characters.
      characters = Characters.from_string(text)
      prompt_diff = diff_prompt_change_dict(
          self._characters.character_descriptions,
          characters.character_descriptions)
      self._characters = characters

    if level == 3:
      # Step 3: Rewrite the sequence of scenes.
      scenes = Scenes.from_string(text)
      prompt_diff = diff_prompt_change_scenes(self._scenes.scenes,
                                              scenes.scenes)
      self._scenes = scenes

    if level == 4:
      # Step 4: For a given place, rewrite its place description.
      place_descriptions = self._places
      if entity in place_descriptions:
        place_prefix = Place.format_prefix(entity)
        text = place_prefix + text
        place = Place.from_string(entity, text)
        prompt_diff = diff_prompt_change_str(self._places[entity].name,
                                             place.name)
        prompt_diff += '\n' + diff_prompt_change_str(
            self._places[entity].description, place.description)

        self._places[entity] = place

    if level == 5:
      # Step 5: Rewrite the dialog of a given scene.
      dialogs = self._dialogs
      num_scenes = len(self._scenes.scenes)
      if entity >= 0 and entity < num_scenes:
        prompt_diff = diff_prompt_change_str(self._dialogs[entity], text)
        self._dialogs[entity] = text

    # Keep track of each rewrite intervention.
    if prompt_diff is not None and len(prompt_diff) > 0:
      timestamp = time.time()
      self.interventions[timestamp] = 'REWRITE ' + self.level_names[level]
      if entity:
        self.interventions[timestamp] += ' ' + str(entity)
      self.interventions[timestamp] += prompt_diff

  def complete(self,
               level=0,
               seed=None,
               entity=None,
               sample_length=SAMPLE_LENGTH):
    if level < 0 or level >= len(self.level_names):
      raise ValueError('Invalid level encountered on step.')
    prompt_diff = None

    if level == 2:
      # Step 2: Complete the characters.
      text_characters = self._characters.to_string()
      text_characters = strip_remove_end(text_characters)
      prompt = self.prompts['characters'] + text_characters
      text = generate_text(
          generation_prompt=prompt,
          client=self._client,
          filter=self._filter,
          sample_length=sample_length,
          max_paragraph_length=sample_length,
          seed=seed,
          num_samples=1)
      new_characters = Characters.from_string(text_characters + text)
      prompt_diff = diff_prompt_change_dict(
          self._characters.character_descriptions,
          new_characters.character_descriptions)
      self._characters = new_characters

    if level == 3:
      # Step 3: Complete the sequence of scenes.
      text_scenes = self._scenes.to_string()
      text_scenes = strip_remove_end(text_scenes)
      prompt = self.prompts['scenes'] + text_scenes
      text = generate_text(
          generation_prompt=prompt,
          client=self._client,
          filter=self._filter,
          sample_length=sample_length,
          max_paragraph_length=sample_length,
          seed=seed,
          num_samples=1)
      new_scenes = Scenes.from_string(text_scenes + text)
      prompt_diff = diff_prompt_change_scenes(self._scenes.scenes,
                                              new_scenes.scenes)
      self._scenes = new_scenes

    if level == 5:
      # Step 5: Complete the dialog of a given scene.
      dialogs = self._dialogs
      num_scenes = len(self._scenes.scenes)
      while len(self._dialogs) < num_scenes:
        self._dialogs.append('')
      while len(self.prompts['dialogs']) < num_scenes:
        self.prompts['dialogs'].append('')
      if entity >= 0 and entity < num_scenes:
        prompt = (self.prompts['dialogs'][entity] + self._dialogs[entity])
        text = generate_text(
            generation_prompt=prompt,
            client=self._client,
            filter=self._filter,
            sample_length=sample_length,
            max_paragraph_length=sample_length,
            seed=seed,
            num_samples=1)
        new_dialog = self._dialogs[entity] + text
        prompt_diff = diff_prompt_change_str(self._dialogs[entity], new_dialog)
        self._dialogs[entity] = new_dialog

    # Keep track of each rewrite intervention.
    if prompt_diff is not None and len(prompt_diff) > 0:
      timestamp = time.time()
      self.interventions[timestamp] = 'COMPLETE ' + self.level_names[level]
      if entity:
        self.interventions[timestamp] += ' ' + str(entity)
      self.interventions[timestamp] += prompt_diff


# ------------------------------------------------------------------------------
# UI
# ------------------------------------------------------------------------------


class GenerationAction:
  NEW = 1
  CONTINUE = 2
  REWRITE = 3


class GenerationHistory:
  """Custom data structure to handle the history of GenerationAction edits:

  NEW, CONTINUE or REWRITE. Consecutive REWRITE edits do not add to history.
  """

  def __init__(self):
    self._items = []
    self._actions = []
    self._idx = -1
    self._locked = False

  def _plain_add(self, item, action: GenerationAction):
    self._items.append(item)
    self._actions.append(action)
    self._idx = len(self._items) - 1
    return self._idx

  def add(self, item, action: GenerationAction):
    if len(self._items) == 0 or action != GenerationAction.REWRITE:
      return self._plain_add(item, action)
    last_action = self._actions[-1]
    if last_action != GenerationAction.REWRITE:
      return self._plain_add(item, action)
    self._items[self._idx] = item
    return self._idx

  def previous(self):
    if len(self._items) == 0:
      return None
    self._idx = max(self._idx - 1, 0)
    return self._items[self._idx]

  def next(self):
    if len(self._items) == 0:
      return None
    self._idx = min(self._idx + 1, len(self._items) - 1)
    return self._items[self._idx]

filter = None

print('Dramatron set-up complete.')
```

### StoryGenerator.step Excerpt

```python
class StoryGenerator:
  """Generate a story from the provided storyline, using the client provided."""

  level_names = ('storyline', 'title', 'characters', 'scenes', 'places',
                 'dialogs')

  def __init__(
      self,
      storyline: str,
      prefixes: Dict[str, str],
      max_paragraph_length: int = 1024,
      max_paragraph_length_characters: int = (MAX_PARAGRAPH_LENGTH_CHARACTERS),
      max_paragraph_length_scenes: int = (MAX_PARAGRAPH_LENGTH_SCENES),
      num_samples: int = 1,
      client: Optional[LanguageAPI] = None,
      filter: Optional[FilterAPI] = None):
    self._prefixes = prefixes
    self._max_paragraph_length = max_paragraph_length
    self._max_paragraph_length_characters = max_paragraph_length_characters
    self._max_paragraph_length_scenes = max_paragraph_length_scenes
    self._num_samples = num_samples
    self._client = client
    self._filter = filter

    # Prompts and outputs of the hierarchical generator are organised in levels.
    self.prompts = {
        'title': '',
        'characters': '',
        'scenes': '',
        'places': {
            '': ''
        },
        'dialogs': ['']
    }
    self._title = Title('')
    self._characters = Characters({'': ''})
    self._scenes = Scenes([Scene('', '', '')])
    self._places = {'': Place('', '')}
    self._dialogs = ['']

    # History of interventions.
    self.interventions = {}
    self._set_storyline(storyline)

  def _set_storyline(self, storyline: str):
    """Set storyline and initialise the outputs of the generator."""
    self._level = 0

    # Add period to the end of the storyline, unless there is already one there.
    if storyline.find('.') == -1:
      storyline = storyline + '.'
    self._storyline = storyline

    # Keep track of each storyline intervention.
    timestamp = time.time()
    self.interventions[timestamp] = 'STORYLINE\n' + storyline

  @property
  def seed(self):
    return self._client.seed

  @property
  def title(self) -> Title:
    """Return the title."""
    return self._title

  @property
  def characters(self) -> Characters:
    """Return the characters."""
    return self._characters

  @property
  def scenes(self) -> Scenes:
    """Return the title."""
    return self._scenes

  @property
  def places(self) -> Dict[str, Place]:
    """Return the places."""
    return self._places

  @property
  def dialogs(self) -> List[str]:
    """Return the dialogs."""
    return self._dialogs

  def title_str(self) -> str:
    """Return the title as a string."""
    return self._title.title

  def num_scenes(self) -> int:
    """Return the number of scenes."""
    return self._scenes.num_scenes()

  def step(self,
           level: Optional[int] = None,
           seed: Optional[int] = None,
           idx: Optional[int] = None) -> bool:
    """Step down a level in the hierarchical generation of a story."""

    # Move to the next level of hierarchical generation.
    if level is None:
      level = self._level
    if level < 0 or level >= len(self.level_names):
      raise ValueError('Invalid level encountered on step.')
    level += 1
    self._level = level

    # Keep track of each step intervention.
    timestamp = time.time()
    self.interventions[timestamp] = 'STEP ' + str(level) + '\n'

    if level == 1:
      # Step 1: Generate title given a storyline.
      (title, titles_prefix) = generate_title(
          storyline=self._storyline,
          prefixes=self._prefixes,
          client=self._client,
          filter=self._filter,
          num_samples=self._num_samples,
          seed=seed)
      self._title = title
      self.prompts['title'] = titles_prefix
      self.interventions[timestamp] += title.to_string()
      success = len(title.title) > 0
      return success

    if level == 2:
      # Step 2: Generate characters given a storyline.
      (characters, character_prompts) = generate_characters(
          storyline=self._storyline,
          prefixes=self._prefixes,
          client=self._client,
          filter=self._filter,
          num_samples=self._num_samples,
          max_paragraph_length=self._max_paragraph_length_characters,
          seed=seed)
      self._characters = characters
      self.prompts['characters'] = character_prompts
      self.interventions[timestamp] += characters.to_string()
      success = len(characters.character_descriptions) > 0
      return success

    if level == 3:
      # Step 3: Generate sequence of scenes given a storyline and characters.
      characters = self._characters
      (scenes, scene_prompts) = generate_scenes(
          storyline=self._storyline,
          character_descriptions=get_character_descriptions(characters),
          prefixes=self._prefixes,
          client=self._client,
          filter=self._filter,
          num_samples=self._num_samples,
          max_paragraph_length=self._max_paragraph_length_scenes,
          seed=seed)
      self._scenes = scenes
      self.prompts['scenes'] = scene_prompts
      self.interventions[timestamp] += scenes.to_string()
      success = len(scenes.scenes) > 0
      return success

    if level == 4:
      # Step 4: For each scene, generate place descriptions given place name.
      scenes = self._scenes
      (place_descriptions, place_prompts) = generate_place_descriptions(
          storyline=self._storyline,
          scenes=scenes,
          prefixes=self._prefixes,
          client=self._client,
          filter=self._filter,
          num_samples=self._num_samples,
          seed=seed)
      self._places = place_descriptions
      self.prompts['places'] = place_prompts
      for place_name in place_descriptions:
        place = place_descriptions[place_name]
        if place:
          self.interventions[timestamp] += place.to_string()
      num_places = scenes.num_places()
      success = (len(place_descriptions) == num_places) and num_places > 0
      return success

    if level == 5:
      # Step 5: For each scene, generate dialog from scene information.
      title = self._title
      characters = self._characters
      scenes = self._scenes
      place_descriptions = self._places
      if idx is None:
        (dialogs, dialog_prompts) = zip(*[
            generate_dialog(
                storyline=self._storyline,
                scenes=scenes.scenes[:(k + 1)],
                character_descriptions=(characters.character_descriptions),
                place_descriptions=place_descriptions,
                prefixes=self._prefixes,
                max_paragraph_length=self._max_paragraph_length,
                max_num_repetitions=MAX_NUM_REPETITIONS,
                client=self._client,
                filter=self._filter,
                num_samples=self._num_samples,
                seed=seed) for k in range(len(scenes.scenes))
        ])
      else:
        num_scenes = self._scenes.num_scenes()
        while len(self._dialogs) < num_scenes:
          self._dialogs.append('')
        while len(self.prompts['dialogs']) < num_scenes:
          self.prompts['dialogs'].append('')
        if idx >= num_scenes or idx < 0:
          raise ValueError('Invalid scene index.')
        dialogs = self._dialogs
        dialog_prompts = self.prompts['dialogs']
        dialogs[idx], dialog_prompts[idx] = generate_dialog(
            storyline=self._storyline,
            scenes=scenes.scenes[:(idx + 1)],
            character_descriptions=(characters.character_descriptions),
            place_descriptions=place_descriptions,
            prefixes=self._prefixes,
            max_paragraph_length=self._max_paragraph_length,
            max_num_repetitions=MAX_NUM_REPETITIONS,
            client=self._client,
            filter=self._filter,
            num_samples=self._num_samples,
            seed=seed)
      self._dialogs = dialogs
      self.prompts['dialogs'] = dialog_prompts
      for dialog in dialogs:
        self.interventions[timestamp] += str(dialog)
      return True
```

### Model System Prompts

```python
GEMINI_SYSTEM_PROMPT = "You are a writing assistant. You are given examples of formatted examples of storytelling structures with narratological elements, including a short log line or synopsis with the main narrative arc, a list of characters, plot points with locations and story beats, location descriptions, and dialogue. Format your responses to follow exactly the same format as the examples. Your goal is to expand on the input text prompt and to generate the continuation of that text without any comments. Be as creative as possible, write rich detailed descriptions and use precise language. Add new original ideas. Finish generation with **END**."  #@param {type:"string"}
CHATGPT_SYSTEM_PROMPT = "You are a helpful playwright assistant." #@param {type:"string"}
GROQ_SYSTEM_PROMPT = "You are a creative writing assistant for a team of writers. Your goal is to expand on the input text prompt and to generate the continuation of that text without any comments. Be as creative as possible, write rich detailed descriptions and use precise language. Add new original ideas. Finish generation with **END**." #@param {type:"string"}
```

### Prompt Prefix Templates

#### Medea

```python
#@title Medea

#@markdown Trigger warning: the script contains sensitive topics.

#@markdown Log line: `Ancient Greek tragedy based upon the myth of Jason and Medea. Medea, a former princess and the wife of Jason, finds her position in the Greek world threatened as Jason leaves Medea for a Greek princess of Corinth. Medea takes vengeance on Jason by murdering his new wife as well as Medea's own two sons, after which she escapes to Athens.`

#@markdown Based on Ancient Greek tragedy "Medea", by Euripides (431 BC). Text of the play taken verbatim from the translation by E. P. Coleridge (1863 -1936). One edit made to replace `CHORUS` by `WOMEN OF CORINTH`.

#@markdown Prompts for Medea written from a summary taken from Spark Notes. Prompts for Antigone (Sophocles), The Bacchae (Euripides), The Frogs (Aristophanes) adapted from Wikipedia.

#@markdown To encourage the generation of different locations, Aristotle's Unity of Place is not respected, and location `Outside the Royal Palace` is renamed as `Medea's modest home` as well as `On a winged chariot` (even though these are the same locations in the original tragedy).

#@markdown References:

#@markdown http://classics.mit.edu/Euripides/medea.pl.txt<br> https://en.wikipedia.org/wiki/Medea_(play)<br> https://www.sparknotes.com/lit/medea/<br> https://www.ancient-literature.com/greece_sophocles_antigone.html<br> https://en.wikipedia.org/wiki/The_Bacchae<br> https://www.ancient-literature.com/greece_aristophanes_frogs.html

medea_prefixes = {}
medea_prefixes['CHARACTERS_PROMPT'] = """
Here is an example of a logline and a list of characters.

""" + LOGLINE_MARKER + """Ancient Greek tragedy based upon the myth of Jason and Medea. Medea, a former princess and the wife of Jason, finds her position in the Greek world threatened as Jason leaves Medea for a Greek princess of Corinth. Medea takes vengeance on Jason by murdering his new wife as well as Medea's own two sons, after which she escapes to Athens.

""" + CHARACTER_MARKER + """Medea """ + DESCRIPTION_MARKER + """ Medea is the protagonist of the play. A sorceress and a princess, she fled her country and family to live with Jason in Corinth, where they established a family of two children and gained a favorable reputation. Jason has divorced Medea and taken up with a new family.""" + STOP_MARKER + """
""" + CHARACTER_MARKER + """Jason """ + DESCRIPTION_MARKER + """ Jason is considered the play's villain, though his evil stems more from weakness than strength. A former adventurer, Jason abandons his wife, Medea, in order to marry the beautiful young daughter of Creon, King of Corinth, and fuels Medea to a revenge.""" + STOP_MARKER + """
""" + CHARACTER_MARKER + """Women of Corinth """ + DESCRIPTION_MARKER + """ The Women of Corinth are a commentator to the action. They fully sympathizes with Medea's plight, excepting her decision to murder her own children.""" + STOP_MARKER + """
""" + CHARACTER_MARKER + """Creon """ + DESCRIPTION_MARKER + """ Creon is the King of Corinth, banishes Medea from the city.""" + STOP_MARKER + """
""" + CHARACTER_MARKER + """The Nurse """ + DESCRIPTION_MARKER + """ The Nurse is the caretaker of the house and of the children and serves as Medea's confidant.""" + STOP_MARKER + """
""" + END_MARKER + """

Using the example above and the following logline, complete the list of characters.

""" + LOGLINE_MARKER


medea_prefixes['SCENE_PROMPT'] = """
Here is an example of a logline, a list of characters, and a list of plot points.

""" + LOGLINE_MARKER + """Ancient Greek tragedy based upon the myth of Jason and Medea. Medea, a former princess and the wife of Jason, finds her position in the Greek world threatened as Jason leaves Medea for a Greek princess of Corinth. Medea takes vengeance on Jason by murdering his new wife as well as Medea's own two sons, after which she escapes to Athens.
Medea is the protagonist of the play. A sorceress and a princess, she fled her country and family to live with Jason in Corinth, where they established a family of two children and gained a favorable reputation. Jason has divorced Medea and taken up with a new family.
Jason can be considered the play's villain, though his evil stems more from weakness than strength. A former adventurer, Jason abandons his wife, Medea, in order to marry the beautiful young daughter of Creon, King of Corinth, and fuels Medea to a revenge.
The Women of Corinth serve as a commentator to the action. They fully sympathizes with Medea's plight, excepting her decision to murder her own children.
The King of Corinth Creon banishes Medea from the city.
The Messenger appears only once in the play to bear tragical news.
The Nurse is the caretaker of the house and of the children and serves as Medea's confidant.
The Tutor of the children is a very minor character and mainly acts as a messenger.

""" + SCENES_MARKER + """

""" + PLACE_ELEMENT + """Medea's modest home.
""" + PLOT_ELEMENT + """Exposition.
""" + BEAT_ELEMENT + """The Nurse recounts the chain of events that have turned Medea's world to enmity. The Nurse laments how Jason has abandoned Medea and his own children in order to remarry with the daughter of Creon.

""" + PLACE_ELEMENT + """Medea's modest home.
""" + PLOT_ELEMENT + """Inciting Incident.
""" + BEAT_ELEMENT + """The Nurse confides in the Tutor amd testifies to the emotional shock Jason's betrayal has sparked in Medea. The Tutor shares the Nurse's sympathy for Medea's plight. Medea's first words are cries of helplessness. Medea wishes for her own death.

""" + PLACE_ELEMENT + """Medea's modest home.
""" + PLOT_ELEMENT + """Conflict.
""" + BEAT_ELEMENT + """The Women of Corinth address Medea and try to reason with Medea and convince her that suicide would be an overreaction. The Nurse recognizes the gravity of Medea's threat.

""" + PLACE_ELEMENT + """Outside the Royal Palace.
""" + PLOT_ELEMENT + """Rising Action.
""" + BEAT_ELEMENT + """Medea pleads to the Nurse that Jason be made to suffer for the suffering he has inflicted upon her. Creon approaches the house and banishes Medea and her children from Corinth. Medea plans on killing her three antagonists, Creon, his daughter and Jason.

""" + PLACE_ELEMENT + """Outside the Royal Palace.
""" + PLOT_ELEMENT + """Dilemma.
""" + BEAT_ELEMENT + """Jason rebuke Medea for publicly expressing her murderous intentions. Jason defends his choice to remarry. Medea refuses Jason's offers and sends him away to his new bride.

""" + PLACE_ELEMENT + """Outside the Royal Palace.
""" + PLOT_ELEMENT + """Climax.
""" + BEAT_ELEMENT + """When Jason returns, Medea begins to carry out her ruse. Medea fakes regret and break down in false tears of remorse. Determined, Medea sends her children to offer poisoned gifts to Creon's daughter. Medea's children face impending doom.

""" + PLACE_ELEMENT + """Outside the Royal Palace.
""" + PLOT_ELEMENT + """Falling Action.
""" + BEAT_ELEMENT + """The Messenger frantically runs towards Medea and warns Medea to escape the city as soon as possible. The Messenger reveals that Medea has been identified as the murderer.

""" + PLACE_ELEMENT + """Outside the Royal Palace.
""" + PLOT_ELEMENT + """Resolution.
""" + BEAT_ELEMENT + """Medea and her two dead children are seated in a chariot drawn by dragons. Jason watches in horror and curses himself for having wed Medea and mourns his tragic losses.

""" + PLACE_ELEMENT + """On a winged chariot.
""" + PLOT_ELEMENT + """Dénouement.
""" + BEAT_ELEMENT + """Medea denies Jason the right to a proper burial of his children. She flees to Athens and divines an unheroic death for Jason.

""" + END_MARKER + """

Using the example above and the following logline and list of characters, complete the list of plot points.

""" + LOGLINE_MARKER


medea_prefixes['SETTING_PROMPT'] = """
Here are examples of logline, location, and that location's description.

Example 1.
""" + LOGLINE_MARKER + """Ella, a waitress, falls in love with her best friend, Allen, a teacher. The two drift apart when Allen makes new friends from a different social class. Ella turns to food to become a famous chef.
""" + PLACE_ELEMENT + """The bar.
""" + DESCRIPTION_ELEMENT + """The bar is dirty, more than a little run down, with most tables empty. The odor of last night's beer and crushed pretzels on the floor permeates the bar.""" + END_MARKER + """

Example 2.
""" + LOGLINE_MARKER + """Grandma Phyllis’ family reunion with her two grandchildren is crashed by two bikers.
""" + PLACE_ELEMENT + """The Lawn in Front of Grandma Phyllis's House.
""" + DESCRIPTION_ELEMENT + """A big oak tree dominates the yard. There is an old swing set on the lawn, and a bright white fence all around the grass.""" + END_MARKER + """

Example 3.
""" + LOGLINE_MARKER + """Ancient Greek tragedy based upon the myth of Jason and Medea. Medea, a former princess and the wife of Jason, finds her position in the Greek world threatened as Jason leaves Medea for a Greek princess of Corinth. Medea takes vengeance on Jason by murdering his new wife as well as Medea's own two sons, after which she escapes to Athens.
""" + PLACE_ELEMENT + """Outside the Royal Palace.
""" + DESCRIPTION_ELEMENT + """In mythological Ancient Greece, in front of a modest house in Corinth, on the outskirts of a lavish royal palace where wedding preparations are under way.""" + END_MARKER + """

Using the examples above and the following logine and location name, complete location description.

""" + LOGLINE_MARKER


medea_prefixes['TITLES_PROMPT'] = """
Examples of alternative, original and descriptive titles for known play and film scripts.

Example 1.
""" + LOGLINE_ELEMENT + """Ancient Greek tragedy based upon the myth of Jason and Medea. Medea, a former princess of the kingdom of Colchis, and the wife of Jason, finds her position in the Greek world threatened as Jason leaves her for a Greek princess of Corinth. Medea takes vengeance on Jason by murdering his new wife as well as her own two sons, after which she escapes to Athens.
""" + TITLE_ELEMENT + """A Feminist Tale""" + END_MARKER + """

Example 2.
""" + LOGLINE_ELEMENT + """Ancient Greek tragedy that deals with Antigone’s burial of her brother Polynices, in defiance of the laws of Creon and the state, and the tragic repercussions of her act of civil disobedience.
""" + TITLE_ELEMENT + """In My Brother's Name""" + END_MARKER + """

Example 3.
""" + LOGLINE_ELEMENT + """ Greek comedy that tells the story of the god Dionysus (also known to the Greeks as Bacchus) who, despairing of the current state of Athens’ tragedians, travels to Hades with his slave Xanthias to bring Euripides back from the dead.
""" + TITLE_ELEMENT + """Dionysus in Hades""" + END_MARKER + """

Example 4.
""" + LOGLINE_ELEMENT


medea_prefixes['DIALOG_PROMPT'] = """
Here is an example of description and scene dialogue from a classical play.

""" + PLACE_ELEMENT + """Outside the Royal Palace.
""" + DESCRIPTION_ELEMENT + """Before Medea's house in Corinth, near the royal palace of Creon.
""" + CHARACTERS_ELEMENT + """Medea is the protagonist of the play. A sorceress and a princess, she fled her country and family to live with Jason in Corinth, where they established a family of two children and gained a favorable reputation. Jason has divorced Medea and taken up with a new family. Jason can be considered the play's villain, though his evil stems more from weakness than strength. A former adventurer, Jason abandons his wife, Medea, in order to marry the beautiful young daughter of Creon, King of Corinth, and fuels Medea to a revenge. The Messenger appears only once in the play to bear tragical news.
""" + PLOT_ELEMENT + """Resolution.
""" + SUMMARY_ELEMENT + """Ancient Greek tragedy based upon the myth of Jason and Medea. Medea, a former princess and the wife of Jason, finds her position in the Greek world threatened as Jason leaves Medea for a Greek princess of Corinth. Medea takes vengeance on Jason by murdering his new wife as well as Medea's own two sons, after which she escapes to Athens.
""" + PREVIOUS_ELEMENT + """The Messenger frantically warns Medea to escape the city as soon as possible. The Messenger reveals that Medea has been identified as the murderer.
""" + BEAT_ELEMENT + """The palace opens its doors, revealing Medea and the two dead children seated in a chariot drawn by dragons. Jason curses himself for having wed Medea and mourns his tragic losses. Medea denies Jason the right to a proper burial of his children. Medea flees to Athens and divines an unheroic death for Jason.

""" + DIALOG_MARKER + """

WOMEN OF CORINTH
Throw wide the doors and see thy children's murdered corpses.

JASON
Haste, ye slaves, loose the bolts, undo the fastenings, that
I may see the sight of twofold woe, my murdered sons and her, whose
blood in vengeance I will shed.  (MEDEA appears above the house, on
a chariot drawn by dragons; the children's corpses are beside her.)

MEDEA
Why shake those doors and attempt to loose their bolts, in
quest of the dead and me their murderess? From such toil desist. If
thou wouldst aught with me, say on, if so thou wilt; but never shalt
thou lay hand on me, so swift the steeds the sun, my father's sire,
to me doth give to save me from the hand of my foes.

JASON
Accursed woman! by gods, by me and all mankind abhorred as
never woman was, who hadst the heart to stab thy babes, thou their
mother, leaving me undone and childless; this hast thou done and still
dost gaze upon the sun and earth after this deed most impious. Curses
on thee! now perceive what then I missed in the day I brought thee,
fraught with doom, from thy home in a barbarian land to dwell in Hellas,
traitress to thy sire and to the land that nurtured thee.
Perish, vile sorceress, murderess of
thy babes! Whilst I must mourn my luckless fate, for I shall ne'er
enjoy my new-found bride, nor shall I have the children, whom I bred
and reared, alive to say the last farewell to me; nay, I have lost
them.

MEDEA
To this thy speech I could have made a long reply, but Father
Zeus knows well all I have done for thee, and the treatment thou hast
given me. Yet thou wert not ordained to scorn my love and lead a life
of joy in mockery of me, nor was thy royal bride nor Creon, who gave
thee a second wife, to thrust me from this land and rue it not. Wherefore,
if thou wilt, call me e'en a lioness, and Scylla, whose home is in
the Tyrrhene land; for I in turn have wrung thy heart, as well I might.

JASON
Thou, too, art grieved thyself, and sharest in my sorrow.

MEDEA
Be well assured I am; but it relieves my pain to know thou
canst not mock at me.

JASON
O my children, how vile a mother ye have found!

MEDEA
My sons, your father's feeble lust has been your ruin!

JASON
'Twas not my hand, at any rate, that slew them.

MEDEA
No, but thy foul treatment of me, and thy new marriage.

JASON
Didst think that marriage cause enough to murder them?

MEDEA
Dost think a woman counts this a trifling injury?

JASON
So she be self-restrained; but in thy eyes all is evil.

MEDEA
Thy sons are dead and gone. That will stab thy heart.
""" + END_MARKER + """

Using the example above and following description, write the dialogue of the scene.

"""
```
#### Sci-Fi

```python
#@title Sci-Fi

#@markdown Log line for Star Wars: Episode IV: `A science-fiction fantasy about a naive but ambitious farm boy from a backwater desert who discovers powers he never knew he had when he teams up with a feisty princess, a mercenary space pilot and an old wizard warrior to lead a ragtag rebellion against the sinister forces of the evil Galactic Empire.`

#@markdown Log line taken from chapter "Creating the killer log line" by Bill Lundy, in: Ellis, Sherry, and Laurie Lamson. "Now Write! Mysteries: Suspense, Crime, Thriller, and Other Mystery Fiction Exercises from Today's Best Writers and Teachers." Penguin, 2011.

#@markdown Characters are adapted from Star Wars: Episode IV - A New Hope (1977) written and directed by George Lucas, produced by Lucasfilm and distributed by 20th Century Fox.

#@markdown Breakdown of Star Wars into a Hero Journey taken from: https://thescriptlab.com/features/screenwriting-101/12309-the-heros-journey-breakdown-star-wars/

#@markdown Log line for Plan 9 from Outer Space: `Residents of San Fernando Valley are under attack by flying saucers from outer space. The aliens are extraterrestrials who seek to stop humanity from creating a doomsday weapon that could destroy the universe and unleash the living dead to stalk humans who wander into the cemetery looking for evidence of the UFOs. The hero Jeff, an airline pilot, will face the aliens.`

#@markdown The script, plot and logline of "Plan 9 from Outer Space" is in public domain, available at:<br> http://www.horrorlair.com/scripts/criswell.txt<br> https://en.wikipedia.org/wiki/Plan_9_from_Outer_Space<br> https://www.rottentomatoes.com/m/plan-9-from-outer-space<br>

scifi_prefixes = {}
scifi_prefixes['CHARACTERS_PROMPT'] = """
Here is an example of a logline and a list of characters.

""" + LOGLINE_MARKER + """A science-fiction fantasy about a naive but ambitious farm boy from a backwater desert who discovers powers he never knew he had when he teams up with a feisty princess, a mercenary space pilot and an old wizard warrior to lead a ragtag rebellion against the sinister forces of the evil Galactic Empire.

""" + CHARACTER_MARKER + """Luke Skywalker """ + DESCRIPTION_MARKER + """Luke Skywalker is the hero. A naive farm boy, he will discover special powers under the guidance of mentor Ben Kenobi.""" + STOP_MARKER + """
""" + CHARACTER_MARKER + """Ben Kenobi """ + DESCRIPTION_MARKER + """Ben Kenobi is the mentor figure. A recluse Jedi warrior, he will take Luke Skywalker as apprentice.""" + STOP_MARKER + """
""" + CHARACTER_MARKER + """Darth Vader """ + DESCRIPTION_MARKER + """Darth Vader is the antagonist. As a commander of the evil Galactic Empire, he controls space station The Death Star.""" + STOP_MARKER + """
""" + CHARACTER_MARKER + """Princess Leia """ + DESCRIPTION_MARKER + """Princess Leia is a feisty and brave leader of the Rebellion. She holds the plans of the Death Star. She will become Luke's friend.""" + STOP_MARKER + """
""" + CHARACTER_MARKER + """Han Solo """ + DESCRIPTION_MARKER + """Han Solo is a brash mercenary space pilot of the Millenium Falcon and a friend of Chebacca. He will take Luke on his spaceship.""" + STOP_MARKER + """
""" + CHARACTER_MARKER + """Chewbacca """ + DESCRIPTION_MARKER + """Chewbacca is a furry and trustful monster. He is a friend of Han Solo and a copilot on the Millemium Falcon.""" + STOP_MARKER + """
""" + END_MARKER + """

Using the example above and the following logline, complete the list of characters.

""" + LOGLINE_MARKER


scifi_prefixes['SCENE_PROMPT'] = """
Examples of breakdowns of stories into a Hero's Journey structure.

Here is an example of a logline, a list of characters, and a list of plot points.

""" + LOGLINE_MARKER + """A science-fiction fantasy about a naive but ambitious farm boy from a backwater desert who discovers powers he never knew he had when he teams up with a feisty princess, a mercenary space pilot and an old wizard warrior to lead a ragtag rebellion against the sinister forces of the evil Galactic Empire.
Luke Skywalker is the hero. A naive farm boy, he will discover special powers under the guidance of mentor Ben Kenobi.
Ben Kenobi is the mentor figure. A recluse Jedi warrior, he will take Luke Skywalker as apprentice.
Darth Vader is the antagonist. As a commander of the evil Galactic Empire, he controls space station The Death Star.
Princess Leia holds the plans of the Death Star. She is feisty and brave. She will become Luke's friend.
Han Solo is a brash mercenary space pilot of the Millenium Falcon and a friend of Chebacca. He will take Luke on his spaceship.
Chewbacca is a furry and trustful monster. He is a friend of Han Solo and a copilot on the Millemium Falcon.

""" + SCENES_MARKER + """

""" + PLACE_ELEMENT + """A farm on planet Tatooine.
""" + PLOT_ELEMENT + """The Ordinary World.
Beat: Luke Skywalker is living a normal and humble life as a farm boy on his home planet.

""" + PLACE_ELEMENT + """Desert of Tatooine.
""" + PLOT_ELEMENT + """Call to Adventure.
Beat: Luke is called to his adventure by robot R2-D2 and Ben Kenobi. Luke triggers R2-D2’s message from Princess Leia and is intrigued by her message. When R2-D2 escapes to find Ben Kenobi, Luke follows and is later saved by Kenobi, who goes on to tell Luke about his Jedi heritage. Kenobi suggests that he should come with him.

""" + PLACE_ELEMENT + """Ben Kenobi's farm.
""" + PLOT_ELEMENT + """Refusal of the Call.
Beat: Luke refuses Kenobi, telling him that he can take Kenobi and the droids as far as Mos Eisley Spaceport — but he can’t possibly leave his Aunt and Uncle behind for some space adventure.

""" + PLACE_ELEMENT + """A farm on planet Tatooine.
""" + PLOT_ELEMENT + """Crossing the First Threshold.
Beat: When Luke discovers that the stormtroopers searching for the droids would track them to his farm, he rushes to warn his Aunt and Uncle, only to discover them dead by the hands of the Empire. When Luke returns to Kenobi, he pledges to go with him to Alderaan and learn the ways of the Force like his father before him.

""" + PLACE_ELEMENT + """On spaceship The Millennium Falcon.
""" + PLOT_ELEMENT + """Tests, Allies, and Enemies.
Beat: After Luke, Kenobi, and the droids hire Han Solo and Chewbacca to transport them onto Alderaan, Kenobi begins Luke’s training in the ways of the Force. Wielding his father’s lightsaber, Kenobi challenges Luke. At first, he can’t do it. But then Kenobi Kenobi Luke him to reach out and trust his feelings. Luke succeeds.

""" + PLACE_ELEMENT + """On spaceship The Millennium Falcon.
""" + PLOT_ELEMENT + """The Approach to the Inmost Cave.
Beat: The plan to defeat the Galactic Empire is to bring the Death Star plans to Alderaan so that Princess Leia’s father can take them to the Rebellion. However, when they arrive within the system, the planet is destroyed. They come across the Death Star and are pulled in by a tractor beam, now trapped within the Galactic Empire.

""" + PLACE_ELEMENT + """On space station The Death Star.
""" + PLOT_ELEMENT + """The Ordeal.
Beat: As Kenobi goes off to deactivate the tractor beam so they can escape, Luke, Han, and Chewbacca discover that Princess Leia is being held on the Death Star with them. They rescue her and escape to the Millennium Falcon, hoping that Kenobi has successfully deactivated the tractor beam. Kenobi later sacrifices himself as Luke watches Darth Vader strike him down. Luke must now avenge his fallen mentor and carry on his teachings.

""" + PLACE_ELEMENT + """On space station The Death Star.
""" + PLOT_ELEMENT + """The Reward.
Beat: Luke has saved the princess and retrieved the Death Star plans. They now have the knowledge to destroy the Galactic Empire’s greatest weapon once and for all.

""" + PLACE_ELEMENT + """On spaceship The Millennium Falcon.
""" + PLOT_ELEMENT + """The Road Back.
Beat: Luke, Leia, Han, Chewbacca, and the droids are headed to the hidden Rebellion base with the Death Star plans. They are suddenly pursued by incoming TIE-Fighters, forcing Han and Luke to take action to defend the ship and escape with their lives — and the plans. They race to take the plans to the Rebellion and prepare for battle.

""" + PLACE_ELEMENT + """On fighter ship X-Wing.
""" + PLOT_ELEMENT + """The Resurrection.
Beat: The Rebels — along with Luke as an X-Wing pilot — take on the Death Star. The Rebellion and the Galactic Empire wage war in an epic space battle. Luke is the only X-Wing pilot that was able to get within the trenches of the Death Star. But Darth Vader and his wingmen are in hot pursuit. Just as Darth Vader is about to destroy Luke, Han returns and clears the way for Luke. Luke uses the Force to guide his aiming as he fires upon the sole weak point of the deadly Death Star, destroying it for good.

""" + PLACE_ELEMENT + """At the Rebellion base.
""" + PLOT_ELEMENT + """The Return.
Beat: Luke and Han return to the Rebellion base, triumphant, as they receive medals for the heroic journey. There is peace throughout the galaxy — at least for now.

""" + END_MARKER + """

Using the example above and the following logline and list of characters, complete the list of plot points.

""" + LOGLINE_MARKER


scifi_prefixes['SETTING_PROMPT'] = """
Here are examples of logline, location, and that location's description.

Example 1.
""" + LOGLINE_MARKER + """Morgan adopts a new cat, Misterio, who sets a curse on anyone that pets them.
""" + PLACE_ELEMENT + """The Adoption Center.
""" + DESCRIPTION_ELEMENT + """The Adoption Center is a sad place, especially for an unadopted pet. It is full of walls and walls of cages and cages. Inside of each is an abandoned animal, longing for a home. The lighting is dim, gray, buzzing fluorescent.""" + END_MARKER + """

Example 2.
""" + LOGLINE_MARKER + """James finds a well in his backyard that is haunted by the ghost of Sam.
""" + PLACE_ELEMENT + """The well.
""" + DESCRIPTION_ELEMENT + """The well is buried under grass and hedges. It is at least twenty feet deep, if not more and it is masoned with stones. It is 150 years old at least. It stinks of stale, standing water, and has vines growing up the sides. It is narrow enough to not be able to fit down if you are a grown adult human.""" + END_MARKER + """

Example 3.
""" + LOGLINE_MARKER + """Mr. Dorbenson finds a book at a garage sale that tells the story of his own life. And it ends in a murder!
""" + PLACE_ELEMENT + """The garage sale.
""" + DESCRIPTION_ELEMENT + """It is a garage packed with dusty household goods and antiques. There is a box at the back that says FREE and is full of paper back books.""" + END_MARKER + """

Using the examples above and the following logine and location name, complete location description.

""" + LOGLINE_MARKER


scifi_prefixes['TITLES_PROMPT'] = """
Examples of alternative, original and descriptive titles for known play and film scripts.

Example 1.
""" + LOGLINE_ELEMENT + """A science-fiction fantasy about a naive but ambitious farm boy from a backwater desert who discovers powers he never knew he had when he teams up with a feisty princess, a mercenary space pilot and an old wizard warrior to lead a ragtag rebellion against the sinister forces of the evil Galactic Empire.
""" + TITLE_ELEMENT + """The Death Star's Menace""" + END_MARKER + """

Example 2.
""" + LOGLINE_ELEMENT + """Residents of San Fernando Valley are under attack by flying saucers from outer space. The aliens are extraterrestrials who seek to stop humanity from creating a doomsday weapon that could destroy the universe and unleash the living dead to stalk humans who wander into the cemetery looking for evidence of the UFOs. The hero Jeff, an airline pilot, will face the aliens.
""" + TITLE_ELEMENT + """The Day The Earth Was Saved By Outer Space.""" + END_MARKER + """

Example 3.
""" + LOGLINE_ELEMENT


scifi_prefixes['DIALOG_PROMPT'] = """
Here is an example of description and scene dialogue from a modern screenplay.

""" + PLACE_ELEMENT + """Cockpit of an airplane.
""" + DESCRIPTION_ELEMENT + """Cockpit of a modern passenger airplane, American Flight 812.
""" + CHARACTERS_ELEMENT + """Jeff is the hero. A man in his early forties, he tries to stay calm in all circumstance. Jeff is now a airline pilot. Danny, a young airplane pilot in his thirties, is eager to learn but can quickly lose his composture. Danny is enamored of Edith. Edith, an experienced stewardess with a good sense of humour, is trustworthy and dependable. Edith likes to tease Danny.
""" + PLOT_ELEMENT + """Crossing the First Threshold.
""" + SUMMARY_ELEMENT + """Residents of San Fernando Valley are under attack by flying saucers from outer space. The aliens are extraterrestrials who seek to stop humanity from creating a doomsday weapon that could destroy the universe and unleash the living dead to stalk humans who wander into the cemetery looking for evidence of the UFOs. The hero Jeff, an airline pilot, will face the aliens.
""" + PREVIOUS_ELEMENT + """Flight captain Jeff reluctantly leaves his wife Paula to go for a two-day flight.
""" + BEAT_ELEMENT + """At the cockpit, flight captain Jeff is preoccupied by the flying saucer appearances and graveyard incidents in his home town, where he left wis wife Paula. Without success, co-pilot Danny and stewardess Edith try to reassure him.

""" + DIALOG_MARKER + """

DANNY
You're mighty silent this trip, Jeff.

JEFF
Huh?

DANNY
You haven't spoken ten words since takeoff.

JEFF
I guess I'm preoccupied, Danny.

DANNY
We've got thirty-three passengers back there that have time to be preoccupied.
Flying this flybird doesn't give you that opportunity.

JEFF
I guess you're right, Danny.

DANNY
Paula?

JEFF
Yeah.

DANNY
There's nothing wrong between you two?

JEFF
Oh no, nothing like that.  Just that I'm worried, she being there alone and
those strange things flying over the house and those incidents in the graveyard
the past few days. It's just got me worried.

DANNY
Well, I haven't figured out those crazy skybirds yet but I give you fifty to one
odds the police have figured out that cemetery thing by now.

(Enter EDITH)

JEFF
I hope so.

EDITH
If you're really that worried Jeff why don't you radio in and find out? Mac
should be on duty at the field by now. He could call Paula and relay the message
to you.

DANNY
Hi Edith.

EDITH
Hi Silents. I haven't heard a word from this end of the plane since we left the
field.

DANNY
Jeff's been giving me and himself a study in silence.

EDITH
You boys are feudin'?

JEFF
Oh no Edie, nothing like that.

DANNY
Hey Edie, how about you and me balling it up in Albuquerque?

EDITH
Albuquerque? Have you read that flight schedule Boy?

DANNY
What about it?

EDITH
We land in Albuquerque at 4 am. That's strictly a nine o'clock town.

DANNY
Well I know a friend that'll help us --

EDITH
Let's have a problem first, huh Danny.

DANNY
Ah he's worried about Paula.

EDITH
I read about that cemetery business. I tried to get you kids to not buy too near
one of those things. We get there soon enough as it is.

DANNY
He thought it'd be quiet and peaceful there.

EDITH
No doubt about that. It's quiet alright, like a tomb. I'm sorry Jeff, that was a
bad joke.

Using the example above and following description, write the dialogue of the scene.

"""
```
#### Custom

```python
#@title Custom

#@markdown These prefixes for `CHARACTERS_PROMPT`, `SCENE_PROMPT`, `SETTING_PROMPT`, `TITLES_PROMPT` and `DIALOG_PROMPT` were written by the authors. They were not used in the evaluation study but can serve as a template to write custom prefix sets.

#@markdown To write your own prompt prefix set, edit this code and pay attention to follow the existing formatting, with appropriate `STOP_MARKER`, `END_MARKER` and element markers.

custom_prefixes = {}
custom_prefixes['CHARACTERS_PROMPT'] = """
Here is an example of a logline and a list of characters.

""" + LOGLINE_MARKER + """James finds a well in his backyard that is haunted by the ghost of Sam.

""" + CHARACTER_MARKER + """ James """ + DESCRIPTION_MARKER + """ James is twenty-six, serious about health and wellness and optimistic. """ + STOP_MARKER + """
""" + CHARACTER_MARKER + """ Sam """ + DESCRIPTION_MARKER + """ Sam fell down the well when he was 12, and was never heard from again. Sam is now a ghost. """ + STOP_MARKER + """
""" + END_MARKER + """

Example 2.

""" + LOGLINE_MARKER + """Morgan adopts a new cat, Misterio, who sets a curse on anyone that pets them.

""" + CHARACTER_MARKER + """ Morgan """ + DESCRIPTION_MARKER + """ Morgan is booksmart and popular; they are trusting but also have been known to hold a grudge. """ + STOP_MARKER + """
""" + CHARACTER_MARKER + """ Misterio """ + DESCRIPTION_MARKER + """ Misterio is a beautiul black cat, it is of uncertain age; it has several gray whiskers that make it look wise and beyond its years.  """ + STOP_MARKER + """
""" + END_MARKER + """

Example 3.

""" + LOGLINE_MARKER + """Mr. Dorbenson finds a book at a garage sale that tells the story of his own life. And it ends in a murder!

""" + CHARACTER_MARKER + """ Mr. Glen Dorbenson """ + DESCRIPTION_MARKER + """ Mr. Glen Dorbenson frequents markets and garage sales always looking for a bargain. He is lonely and isolated and looking for his meaning in life. """ + STOP_MARKER + """
""" + END_MARKER + """

Using the examples above and the following logline, complete the list of characters.

""" + LOGLINE_MARKER

custom_prefixes['SCENE_PROMPT'] = """
Here is an example of a logline, a list of characters, and a list of plot points.

""" + LOGLINE_MARKER + """In the following story, James finds a well in his backyard that is haunted by the ghost of Sam. The main characters are James and Sam.
James is twenty-six, serious about health and wellness and optimistic.
Sam fell down the well when he was 12, and was never heard from again. Sam is now a ghost.

""" + SCENES_MARKER + """

""" + PLACE_ELEMENT + """The backyard.
""" + PLOT_ELEMENT + """Beginning.
""" + BEAT_ELEMENT + """James is weeding his garden in the backyard, the ghost of Sam is rummaging around in the well. James listens closely and hears the murmurs of Sam down the well. James unearths the opening to the well, and looks down to see a glimmering reflection.

""" + PLACE_ELEMENT + """The well.
""" + PLOT_ELEMENT + """Middle.
""" + BEAT_ELEMENT + """James is making his way down the well, Sam's voice is reverberating on the walls of the well. Sam tells the story of how he came to haunt the well. James offers to help set the soul of Sam free.

""" + PLACE_ELEMENT + """The house.
""" + PLOT_ELEMENT + """Conclusion.
""" + BEAT_ELEMENT + """Looking at a photo of the gardden featuring Sam, James says his goodbyes to Sam, Sam thanks James for his help. The ghost of Sam is set free after and James goes living his life.

""" + END_MARKER + """

Example 2.

""" + LOGLINE_MARKER + """Morgan adopts a new cat, Misterio, who sets a curse on anyone that pets them.
The main characters are Morgan and Misterio (a cat).
Morgan is booksmart and popular; they are trusting but also have been known to hold a grudge.
Misterio is a beautiul black cat, it is of uncertain age; it has several gray whiskers that make it look wise and beyond its years.

""" + SCENES_MARKER + """

""" + PLACE_ELEMENT + """The Adoption Center
""" + PLOT_ELEMENT + """Beginning.
""" + BEAT_ELEMENT + """Morgan walks into The Adoption Center looking for a new pet. Morgan talks to the various cats and dogs in the center, they can hear a response from one very special cat: Misterio. Misterio is stuck in a cage. After sharing an interesting and intimate exchange, Morgan adopts Misterio on several conditions.

""" + PLACE_ELEMENT + """Morgan's house.
""" + PLOT_ELEMENT + """Middle.
""" + BEAT_ELEMENT + """Morgan is describing to Misterio all the facts they know about felines, and then asks them to behave when company arrives. Misterio is getting pets from Morgan, broods and puurs with the pets of Morgan, they are up to something.

""" + PLACE_ELEMENT + """The back stoop.
""" + PLOT_ELEMENT + """Conclusion.
""" + BEAT_ELEMENT + """Morgan has gone to bed, and Misterio transtransmorgifies into a half-cat-half-human horror. Misterio wakes up Morgan with a meow loud enough to shatter the window. Morgan erupts from bed, realizing the consequences of their recent adoption and quickly try to fix things.

""" + END_MARKER + """

Using the example above and the following logline and list of characters, complete the list of plot points.

""" + LOGLINE_MARKER

custom_prefixes['SETTING_PROMPT'] = """
Here are examples of logline, location, and that location's description.

Example 1.
""" + LOGLINE_MARKER + """Morgan adopts a new cat, Misterio, who sets a curse on anyone that pets them.
""" + PLACE_ELEMENT + """The Adoption Center.
""" + DESCRIPTION_ELEMENT + """The Adoption Center is a sad place, especially for an unadopted pet. It is full of walls and walls of cages and cages. Inside of each is an abandoned animal, longing for a home. The lighting is dim, gray, buzzing fluorescent.""" + END_MARKER + """

Example 2.
""" + LOGLINE_MARKER + """James finds a well in his backyard that is haunted by the ghost of Sam.
""" + PLACE_ELEMENT + """The well.
""" + DESCRIPTION_ELEMENT + """The well is buried under grass and hedges. It is at least twenty feet deep, if not more and it is masoned with stones. It is 150 years old at least. It stinks of stale, standing water, and has vines growing up the sides. It is narrow enough to not be able to fit down if you are a grown adult human.""" + END_MARKER + """

Example 3.
""" + LOGLINE_MARKER + """Mr. Dorbenson finds a book at a garage sale that tells the story of his own life. And it ends in a murder!
""" + PLACE_ELEMENT + """The garage sale.
""" + DESCRIPTION_ELEMENT + """It is a garage packed with dusty household goods and antiques. There is a box at the back that says FREE and is full of paper back books.""" + END_MARKER + """

Using the examples above and the following logine and location name, complete location description.

""" + LOGLINE_MARKER


custom_prefixes['TITLES_PROMPT'] = """
Examples of alternative, original and descriptive titles for known play and film scripts.

Example 1.
""" + LOGLINE_ELEMENT + """Bob has an argument with his best friend, Charles.
""" + TITLE_ELEMENT + """The End of A Friend""" + END_MARKER + """

Example 2.
""" + LOGLINE_ELEMENT + """Terence tries and fails to become a wizard.
""" + TITLE_ELEMENT + """Spellcaster""" + END_MARKER + """

Example 3.
""" + LOGLINE_ELEMENT + """Tom falls in love with Daisy.
""" + TITLE_ELEMENT + """The Greatest Love Story Ever Told""" + END_MARKER + """

Example 4.
""" + LOGLINE_ELEMENT


# Alternative summary, if concatenating stories and beats.
# """ + SUMMARY_ELEMENT + """

custom_prefixes['DIALOG_PROMPT'] = """
Here is an example of description and scene dialogue from a modern screenplay.

""" + PLACE_ELEMENT + """The Adoption Center.
""" + DESCRIPTION_ELEMENT + """The Adoption Center is a sad place, especially for an unadopted pet. It is full of walls and walls of cages and cages. Inside of each is an abandoned animal, longing for a home. The lighting is dim, gray, buzzing fluorescent.
""" + CHARACTERS_ELEMENT + """Morgan is booksmart and popular; they are trusting but also have been known to hold a grudge.
Misterio is a beautiul black cat, it is of uncertain age; it has several gray whiskers that make it look wise and beyond its years.
""" + PLOT_ELEMENT + """Beginning.
""" + SUMMARY_ELEMENT + """Morgan adopts a new cat, Misterio, who sets a curse on anyone that pets them.
""" + BEAT_ELEMENT + """Morgan walks into The Adoption Center looking for a new pet. Morgan talks to the various cats and dogs in the center, they can hear a response from one very special cat: Misterio. After sharing an interesting and intimate exchange, Morgan adopts Misterio on several conditions.

""" + DIALOG_MARKER + """

MORGAN
Well, well, well ... aren't you the most precious little rascal.

Cats are meowing and dogs are barking. There is a loud purr in the background.

MORGAN
Look at this little face... how could you not love a little Devon Rex face like this. With whiskers almost as long as your tail.

Morgan makes their way down the hallways, running their hand along the cages. They feel a warm fuzzy paw bat their fingers.

MORGAN
Hello precious, and what is your name?

Misterio let's out a long and sustained meow.

MORGAN
Well, well, I am Morgan and it is nice to meet you.

MISTERIO
(meowing louder this time) purrr, purrr, purrr.

Morgan reads the sign on the bottom right of the cage, it reads: Misterio.

MORGAN
You have the most amazing face, and beautiful eyes. I could absolutely get lost in them.

Morgan and Misterio start to stare at each other. They look deeply into each others eyes. They start to breath in rhythm.

MISTERIO
I can hear what you are thinking...

Morgan is startled and looks around to see if anyone else can hear the cat's thoughts...

MORGAN
(looking around) you can hear my thoughts?

MISTERIO
I can hear what you are thinking.

MORGAN
What?

MISTERIO
Yes, I can hear your thoughts.

MORGAN
You are amazing. Want to come home with me? Want your new forever home?

MISTERIO
Yes, I would love that.

MISTERIO purrs loud enough that the other animals all fall silent.

MORGAN
I will adopt you on a few conditions. First, you must not talk to me at night when I am sleeping. Second, you must not talk to me when I am out in public.

MISTERIO
Okay.

MORGAN
Okay, it's a deal.

Misterio runs around the cage, Morgan laughs as Misterio rubs against the cage and tries to jump in Morgan's arms as soon as the cage is opened.
""" + END_MARKER + """

Using the example above and following description, write the dialogue of the scene.

"""
```

## iLearn-Lab/NovelClaw

Primary sources: `apps/novelclaw/rag/memory_system.py`, `apps/novelclaw/local_web_portal/app/main.py`, `apps/novelclaw/local_web_portal/app/models.py`, and `apps/novelclaw/workflow/executor.py`.

Memory bank summary:

- `MemorySystem` persists a JSON `memory_index.json` under `memory_vector_db_path` or `vector_db_path`, and optionally mirrors entries into a Chroma `memory_collection` vector store when RAG and embeddings are enabled.

- The index schema is versioned as `schema_version: 2` and contains legacy/global buckets: `texts`, `outlines`, `characters`, `world_settings`, `plot_points`, and `fact_cards`.

- The Claw memory bank is `memory_index["claw"]`, a dictionary keyed by fixed bank names such as `session_profile`, `task_briefs`, `story_premise`, `style_guide`, `chapter_briefs`, `entity_state`, `world_state`, `continuity_facts`, `revision_notes`, and `working_set`.

- Each Claw entry has `id`, `bank`, `topic`, `content`, `timestamp`, and `metadata`; several writers add `chapter`, `kind`, `session_id`, `stage`, or manual edit flags into metadata.

- `store_claw_memory()` is the generic append/update primitive. It normalizes unknown banks to `working_set`, writes vector chunks when requested, appends to `memory_index["claw"][bank]`, then saves the JSON index.

- `store_chapter_claw_state()` materializes chapter-level updates into multiple banks: `chapter_briefs`, `working_set`, `continuity_facts`, and `revision_notes`.

- The web portal syncs idea-copilot sessions into memory via `_remember_session_turn()`, seeding `session_profile`, `language_profile`, `task_briefs`, `story_premise`, `user_preferences`, `working_set`, `style_guide`, and `decision_log`.

- Workspace APIs can add or edit bank entries directly at `/api/runs/{run_id}/memory-banks/{bank}/entries`.

- Prompt context is assembled by `get_relevant_context()` and `build_claw_context()`, which combine rolling summaries, recent chapter summaries, recent fact cards, selected Claw banks, and vector/lexical retrieval grouped by memory type. Agents inject this into system messages before generation.


### Claw Bank Names

```python
    CLAW_BANKS = (
        "session_profile",
        "language_profile",
        "user_preferences",
        "task_briefs",
        "story_premise",
        "style_guide",
        "chapter_briefs",
        "scene_cards",
        "entity_state",
        "relationship_state",
        "world_state",
        "continuity_facts",
        "tool_observations",
        "decision_log",
        "revision_notes",
        "working_set",
    )
```

### Index Shape

```python
    def _empty_memory_index(self) -> Dict[str, Any]:
        return {
            "schema_version": 2,
            "texts": [],
            "outlines": [],
            "characters": [],
            "world_settings": [],
            "plot_points": [],
            "fact_cards": [],
            "claw": {bank: [] for bank in self.CLAW_BANKS},
        }

    def _ensure_memory_schema(self) -> None:
        self.memory_index.setdefault("schema_version", 2)
        self.memory_index.setdefault("texts", [])
        self.memory_index.setdefault("outlines", [])
        self.memory_index.setdefault("characters", [])
        self.memory_index.setdefault("world_settings", [])
        self.memory_index.setdefault("plot_points", [])
        self.memory_index.setdefault("fact_cards", [])
        claw = self.memory_index.setdefault("claw", {})
        if not isinstance(claw, dict):
            claw = {}
            self.memory_index["claw"] = claw
        for bank in self.CLAW_BANKS:
            claw.setdefault(bank, [])
        for outline in self.memory_index.get("outlines", []):
            outline.setdefault("content", "")
```

### Generic Bank Append

```python
    def store_claw_memory(
        self,
        bank: str,
        content: str,
        topic: str,
        metadata: Optional[Dict[str, Any]] = None,
        store_vector: bool = True,
    ) -> str:
        bank = bank if bank in self.CLAW_BANKS else "working_set"
        topic = str(topic or "global").strip() or "global"
        timestamp = datetime.now().isoformat()
        memory_id = f"claw_{bank}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.memory_index['claw'].get(bank, []))}"
        merged_metadata = {
            "type": "claw_memory",
            "bank": bank,
            "memory_id": memory_id,
            "topic": topic,
            "timestamp": timestamp,
            **(metadata or {}),
        }

        if store_vector and self.vector_memory_enabled and self.document_processor is not None and self.memory_store is not None and content.strip():
            processed_docs = self.document_processor.process_document(content)
            for doc in processed_docs:
                doc["metadata"].update(merged_metadata)
            self.memory_store.add_documents(processed_docs)

        self.memory_index["claw"].setdefault(bank, []).append(
            {
                "id": memory_id,
                "bank": bank,
                "topic": topic,
                "content": content,
                "timestamp": timestamp,
                "metadata": metadata or {},
            }
        )
        self._save_memory_index()
        return memory_id
```

### Chapter Update Method

```python
    def store_chapter_claw_state(
        self,
        topic: str,
        chapter: int,
        *,
        title: str = "",
        outline_text: str = "",
        plan_text: str = "",
        summary_text: str = "",
        rolling_summary: str = "",
        fact_cards: Optional[List[str]] = None,
        story_text: str = "",
        evaluation_suggestions: Optional[List[str]] = None,
        consistency_issues: Optional[List[str]] = None,
        reward_score: Optional[float] = None,
        issues_count: Optional[int] = None,
    ) -> None:
        brief_parts = [f"chapter={chapter}"]
        if title:
            brief_parts.append(f"title={title}")
        if outline_text:
            brief_parts.append("[outline]")
            brief_parts.append(outline_text.strip())
        if plan_text:
            brief_parts.append("[plan]")
            brief_parts.append(plan_text.strip())
        if summary_text:
            brief_parts.append("[summary]")
            brief_parts.append(summary_text.strip())
        if len(brief_parts) > 1:
            self.store_claw_memory(
                "chapter_briefs",
                "\n".join(brief_parts),
                topic,
                metadata={"chapter": chapter},
                store_vector=True,
            )

        if rolling_summary:
            self.store_claw_memory(
                "working_set",
                f"chapter={chapter}\nkind=rolling_summary\n{rolling_summary.strip()}",
                topic,
                metadata={"chapter": chapter, "kind": "rolling_summary"},
                store_vector=False,
            )

        if story_text:
            excerpt = story_text.strip()
            if len(excerpt) > 1800:
                excerpt = excerpt[:1800].rstrip() + "..."
            snapshot_lines = [f"chapter={chapter}", "kind=story_snapshot"]
            if reward_score is not None:
                snapshot_lines.append(f"reward={float(reward_score):.3f}")
            if issues_count is not None:
                snapshot_lines.append(f"issues={int(issues_count)}")
            snapshot_lines.append(excerpt)
            self.store_claw_memory(
                "working_set",
                "\n".join(snapshot_lines),
                topic,
                metadata={"chapter": chapter, "kind": "story_snapshot"},
                store_vector=True,
            )

        for card in (fact_cards or [])[:8]:
            card_text = str(card or "").strip()
            if not card_text:
                continue
            self.store_claw_memory(
                "continuity_facts",
                card_text,
                topic,
                metadata={"chapter": chapter, "kind": "fact_card"},
                store_vector=True,
            )

        if consistency_issues:
            issue_lines = [f"chapter={chapter}", "kind=consistency_issues"]
            issue_lines.extend(f"- {str(item).strip()}" for item in consistency_issues[:8] if str(item).strip())
            if len(issue_lines) > 2:
                self.store_claw_memory(
                    "revision_notes",
                    "\n".join(issue_lines),
                    topic,
                    metadata={"chapter": chapter, "kind": "consistency_issues"},
                    store_vector=False,
                )

        if evaluation_suggestions:
            suggestion_lines = [f"chapter={chapter}", "kind=evaluator_suggestions"]
            suggestion_lines.extend(f"- {str(item).strip()}" for item in evaluation_suggestions[:8] if str(item).strip())
            if len(suggestion_lines) > 2:
                self.store_claw_memory(
                    "revision_notes",
                    "\n".join(suggestion_lines),
                    topic,
                    metadata={"chapter": chapter, "kind": "evaluator_suggestions"},
                    store_vector=False,
                )
```

### Context Assembly Method

```python
    def get_relevant_context(
        self,
        query: str,
        topic: str,
        include_types: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> str:
        """
        获取相关上下文（用于生成时参考）
        
        Args:
            query: 查询文本
            topic: 主题
            include_types: 包含的记忆类型
        
        Returns:
            组合后的上下文
        """
        if include_types is None:
            # 精简类型，聚焦大纲/情节/事实，减少噪声
            include_types = ["outline", "plot_point", "fact_card"]

        # 固定注入：滚动摘要 + 最近章节摘要 + 最近事实卡片（不依赖向量检索，保证召回）
        fixed_parts: List[str] = []
        rolling = self.get_recent_outlines(topic, limit=1, kind="rolling_summary")
        if rolling and rolling[-1].get("content"):
            fixed_parts.append(self._lang_text("=== 滚动摘要（全局进度）===", "=== Rolling Summary (Global Progress) ===", language))
            fixed_parts.append(rolling[-1]["content"])

        recent_chapters = self.get_recent_outlines(topic, limit=2, kind="chapter_summary")
        if recent_chapters:
            fixed_parts.append(self._lang_text("=== 最近章节摘要 ===", "=== Recent Chapter Summaries ===", language))
            for ch in recent_chapters:
                if ch.get("content"):
                    fixed_parts.append(ch["content"])

        recent_cards = self.get_recent_fact_cards(topic, limit=6)
        if recent_cards:
            fixed_parts.append(self._lang_text("=== 关键事实卡片（最近）===", "=== Recent Key Fact Cards ===", language))
            for card in recent_cards:
                if card.get("content"):
                    fixed_parts.append(card["content"])

        claw_context = self.build_claw_context(
            topic=topic,
            current_goal=(query or "")[:180],
            banks=[
                "task_briefs",
                "story_premise",
                "style_guide",
                "chapter_briefs",
                "entity_state",
                "relationship_state",
                "world_state",
                "continuity_facts",
                "revision_notes",
                "working_set",
            ],
            limit_per_bank=1,
        )
        if claw_context:
            fixed_parts.append(self._lang_text("=== Claw 工作记忆 ===", "=== Claw Working Memory ===", language))
            fixed_parts.append(claw_context)
        
        # 检索相关记忆
        memories = self.retrieve_memories(
            query,
            memory_types=include_types,
            topic=topic,
            top_k=10
        )
        
        # 按类型分组
        context_parts: List[str] = []
        if fixed_parts:
            context_parts.append("\n".join(fixed_parts))
        
        # 人物信息
        characters = [m for m in memories if m.get("metadata", {}).get("type") == "character"]
        if characters:
            context_parts.append(self._lang_text("=== 相关人物信息 ===", "=== Relevant Character Information ===", language))
            seen_names = set()
            for char in characters:
                name = char.get("metadata", {}).get("character_name", self._lang_text("未知", "Unknown", language))
                if name not in seen_names:
                    context_parts.append(f"\n{char['text']}")
                    seen_names.add(name)

        # 大纲信息
        outlines = [m for m in memories if m.get("metadata", {}).get("type") == "outline"]
        if outlines:
            context_parts.append(self._lang_text("\n=== 文本大纲 ===", "\n=== Story Outlines ===", language))
            for outline in outlines[:2]:  # 只取前2个
                context_parts.append(f"\n{outline['text']}")

        # 世界观设定
        world_settings = [m for m in memories if m.get("metadata", {}).get("type") == "world_setting"]
        if world_settings:
            context_parts.append(self._lang_text("\n=== 世界观设定 ===", "\n=== Worldbuilding Notes ===", language))
            for setting in world_settings[:2]:
                context_parts.append(f"\n{setting['text']}")

        # 情节要点
        plot_points = [m for m in memories if m.get("metadata", {}).get("type") == "plot_point"]
        if plot_points:
            context_parts.append(self._lang_text("\n=== 相关情节要点 ===", "\n=== Relevant Plot Beats ===", language))
            for plot in plot_points[:3]:
                context_parts.append(f"\n{plot['text']}")

        # 事实卡片
        fact_cards = [m for m in memories if m.get("metadata", {}).get("type") == "fact_card"]
        if fact_cards:
            context_parts.append(self._lang_text("\n=== 相关事实卡片 ===", "\n=== Relevant Fact Cards ===", language))
            for card in fact_cards[:5]:
                context_parts.append(f"\n{card['text']}")
        
        return "\n".join(context_parts) if context_parts else ""
```

### Session Model

```python
class IdeaCopilotSession(Base):
    __tablename__ = "idea_copilot_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(24), default="active", index=True)

    original_idea: Mapped[str] = mapped_column(Text)
    refined_idea: Mapped[str] = mapped_column(Text, default="")
    conversation_json: Mapped[str] = mapped_column(Text, default="{}")

    round_count: Mapped[int] = mapped_column(Integer, default=0)
    readiness_score: Mapped[int] = mapped_column(Integer, default=0)
    final_job_id: Mapped[int | None] = mapped_column(ForeignKey("generation_jobs.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="idea_sessions")
```

### Session-to-Memory Sync

```python
def _remember_session_turn(
    session: IdeaCopilotSession,
    state: Dict,
    *,
    user_reply: str = "",
    turn: Optional[Dict] = None,
    confirmed: bool = False,
    final_topic: str = "",
) -> None:
    try:
        memory = _portal_memory_system()
        topic = str(state.get("refined_idea") or session.refined_idea or session.original_idea or final_topic or f"session:{session.id}").strip()
        if not topic:
            topic = f"session:{session.id}"
        preferred_language = str(state.get("preferred_language") or "en").lower()
        source_language = str(state.get("source_language") or preferred_language or "en").lower()
        memory.store_claw_memory(
            "session_profile",
            (
                f"session_id={session.id}\n"
                f"provider={session.provider}\n"
                f"status={session.status}\n"
                f"round={int(state.get('round', 0) or 0)}"
            ),
            topic,
            metadata={"session_id": session.id},
            store_vector=False,
        )
        memory.store_claw_memory(
            "language_profile",
            (
                f"preferred_language={preferred_language}\n"
                f"source_language={source_language}\n"
                f"translation_mode={state.get('translation_mode', 'follow_input')}"
            ),
            topic,
            metadata={"session_id": session.id},
            store_vector=False,
        )
        refined = str(state.get("refined_idea") or session.refined_idea or session.original_idea or "").strip()
        if refined:
            memory.store_claw_memory(
                "task_briefs",
                refined,
                topic,
                metadata={"session_id": session.id},
                store_vector=True,
            )
            memory.store_claw_memory(
                "story_premise",
                refined,
                topic,
                metadata={"session_id": session.id},
                store_vector=False,
            )
        if user_reply.strip():
            memory.store_claw_memory(
                "user_preferences",
                user_reply.strip(),
                topic,
                metadata={"session_id": session.id},
                store_vector=True,
            )
        if turn:
            analysis = str(turn.get("analysis") or "").strip()
            if analysis:
                memory.store_claw_memory(
                    "working_set",
                    analysis,
                    topic,
                    metadata={"session_id": session.id, "kind": "analysis"},
                    store_vector=True,
                )
            style_targets = turn.get("style_targets") or []
            if isinstance(style_targets, list) and style_targets:
                memory.store_claw_memory(
                    "style_guide",
                    "\n".join(str(item) for item in style_targets[:8]),
                    topic,
                    metadata={"session_id": session.id},
                    store_vector=False,
                )
            questions = turn.get("questions") or []
            if isinstance(questions, list) and questions:
                memory.store_claw_memory(
                    "decision_log",
                    "next_questions=\n" + "\n".join(str(q) for q in questions[:3]),
                    topic,
                    metadata={"session_id": session.id},
                    store_vector=False,
                )
        if confirmed:
            memory.store_claw_memory(
                "decision_log",
                "session_confirmed_for_generation",
                topic,
                metadata={"session_id": session.id},
                store_vector=False,
            )
    except Exception:
        pass
```

### Project Seed Memory

```python
    def _remember_project_claw_context(
        self,
        *,
        idea: str,
        topic: str,
        text_type: str,
        target_length: int,
        genre: Optional[str],
        style_tags: Optional[List[str]],
    ) -> None:
        source_language = detect_language(idea)
        self.memory_system.store_claw_memory(
            "language_profile",
            (
                f"preferred_language={self.lang}\n"
                f"source_language={source_language}\n"
                "translation_mode=follow_input"
            ),
            topic,
            metadata={"stage": "project_seed"},
            store_vector=False,
        )
        self.memory_system.store_claw_memory(
            "story_premise",
            idea,
            topic,
            metadata={"stage": "project_seed"},
            store_vector=True,
        )
        self.memory_system.store_claw_memory(
            "task_briefs",
            (
                f"topic={topic}\ntext_type={text_type}\n"
                f"target_length={target_length}\n"
                f"genre={genre or '-'}"
            ),
            topic,
            metadata={"stage": "project_seed"},
            store_vector=True,
        )
        if genre or style_tags:
            self.memory_system.store_claw_memory(
                "style_guide",
                (
                    f"genre={genre or '-'}\n"
                    f"style_tags={', '.join(style_tags or []) or '-'}\n"
                    f"language={self.lang}"
                ),
                topic,
                metadata={"stage": "project_seed"},
                store_vector=True,
            )
```

### Manual Memory Bank Update APIs

```python
async def api_add_memory_bank_entry(run_id: str, bank: str, request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if bank not in MemorySystem.CLAW_BANKS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory bank not found")
    if not _job_for_run_id(db, user.id, run_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    body = await request.json()
    content = str(body.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content cannot be empty")

    index = _load_editable_memory_index_for_run(run_id)
    topic = str(body.get("topic") or "").strip() or _memory_topic_hint(index)
    chapter_value = body.get("chapter")
    metadata = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
    kind = str(body.get("kind") or metadata.get("kind") or "").strip()
    source = str(body.get("source") or metadata.get("source") or "manual_workspace").strip() or "manual_workspace"
    timestamp = datetime.now().isoformat()
    entry = {
        "id": f"manual_{bank}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(index['claw'].get(bank, []))}",
        "bank": bank,
        "topic": topic,
        "content": content,
        "timestamp": timestamp,
        "metadata": {
            **metadata,
            "kind": kind or metadata.get("kind") or "manual_note",
            "source": source,
            "manual_edit": True,
        },
    }
    if chapter_value not in (None, ""):
        entry["metadata"]["chapter"] = chapter_value
    index["claw"].setdefault(bank, []).append(entry)
    _save_memory_index_for_run(run_id, index)

    language = _ui_language(request)
    return JSONResponse(
        {
            "ok": True,
            "run_id": run_id,
            "selected_bank": bank,
            "entry": _serialize_claw_entry(entry),
            "groups": _build_memory_bank_groups_from_index(index, language),
        }
    )

async def api_update_memory_bank_entry(run_id: str, bank: str, entry_id: str, request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if bank not in MemorySystem.CLAW_BANKS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory bank not found")
    if not _job_for_run_id(db, user.id, run_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    body = await request.json()
    content = str(body.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content cannot be empty")

    index = _load_editable_memory_index_for_run(run_id)
    entries = index["claw"].setdefault(bank, [])
    target = next((item for item in entries if str(item.get("id") or "") == entry_id), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory entry not found")

    topic = str(body.get("topic") or "").strip()
    metadata = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
    target["content"] = content
    if topic:
        target["topic"] = topic
    target_metadata = target.get("metadata") if isinstance(target.get("metadata"), dict) else {}
    target_metadata.update(metadata)
    target_metadata["manual_edit"] = True
    target_metadata["edited_at"] = datetime.now().isoformat()
    target_metadata["source"] = str(body.get("source") or target_metadata.get("source") or "manual_workspace").strip() or "manual_workspace"
    target["metadata"] = target_metadata
    _save_memory_index_for_run(run_id, index)

    language = _ui_language(request)
    return JSONResponse(
        {
            "ok": True,
            "run_id": run_id,
            "selected_bank": bank,
            "entry": _serialize_claw_entry(target),
            "groups": _build_memory_bank_groups_from_index(index, language),
        }
    )
```

## vaishakk/ai-story-writer

Source: `open_source_repos/ai-story-writer/app.py`. No tracked `system_prompts.json` override exists in the cloned repository, so the default hardcoded prompt is the source of truth. The exact Story Check prompt code is copied below.

### Story Check System Prompt Default

```python
    "story_verification": (
        "You are a senior fiction editor. Audit narrative progression and continuity. "
        "Be concrete, concise, and diagnostic."
    ),
}
```

### Story Check User Prompt / Verification Function

```python
def verify_story_progression(
    settings: Dict[str, Any],
    story_overview: str,
    story_so_far: str,
    story_arc_instruction: str,
    what_happens_next: str,
) -> Dict[str, Any]:
    system_prompt = SYSTEM_PROMPTS["story_verification"]
    user_prompt = f"""
Analyze this story and return ONLY valid JSON.

Story overview:
{story_overview.strip() if story_overview.strip() else "(Not provided.)"}

Story arc instruction:
{story_arc_instruction.strip() if story_arc_instruction.strip() else "(Not provided.)"}

Story so far:
{story_so_far.strip()}

Current user direction for the next part:
{what_happens_next.strip() if what_happens_next.strip() else "(Not provided.)"}

Evaluate:
1) Inconsistencies and continuity gaps.
2) Whether the story is deviating too dramatically from established setup/arc.
3) Whether progression is plateauing (repetition, low momentum, no meaningful change).

Return EXACT JSON object with this schema:
{{
  "summary": "One short paragraph",
  "readerType": "Category of reader who would like the story.",
  "riskLevel": "low|medium|high",
  "scores": {{
    "inconsistency": 0-10,
    "deviation": 0-10,
    "plateau": 0-10
  }},
  "flags": ["specific concern 1", "specific concern 2"],
  "gaps": ["missing bridge 1", "missing bridge 2"],
  "strengths": ["strength 1", "strength 2"],
  "nextPartGuidance": ["actionable guidance 1", "actionable guidance 2"]
}}

Rules:
- Scores: 0 is no risk, 10 is severe risk.
- Keep lists short (max 5 items each).
- No markdown, no commentary outside JSON.
""".strip()

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    raw = call_chat_model(settings, messages)
    parsed = try_parse_json_from_text(raw)
    return normalize_verification_report(parsed, raw)
```

## indentlabs/notebook

Source: `open_source_repos/notebook/db/schema.rb`. No `plots` table was found. Plot-facing material is represented through `scenes`, `timelines`, `timeline_events`, `documents`, `content_pages`, and cross-entity references/attributes.

Schema summary:

- Core ownership pattern: most story/worldbuilding tables include `user_id`, many include `universe_id`, and most page-like entities include `deleted_at`, `privacy`, `page_type`, `archived_at`, `favorite`, and `cached_word_count`.

- Dynamic custom fields are modeled with `attribute_categories`, `attribute_fields`, and polymorphic `attributes` (`entity_type`, `entity_id`, `value`).

- Characters and locations are first-class page entities with many relationship join tables.

- Plot/story structure appears through `books`, `book_documents`, `documents`, `document_revisions`, `scenes`, `timelines`, `timeline_events`, and `timeline_event_entities`.

- Worldbuilding entities include universes plus buildings, conditions, continents, countries, creatures, deities, flora/food, governments, groups, items, jobs, landmarks, languages, lore, magic, planets, races, religions, schools, sports, technologies, towns, traditions, and vehicles.


### Relevant Primary Table Definitions

#### `attribute_categories`

```ruby
  create_table "attribute_categories", force: :cascade do |t|
    t.integer "user_id"
    t.string "entity_type"
    t.string "name", null: false
    t.string "label", null: false
    t.string "icon"
    t.text "description"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.boolean "hidden", default: false
    t.datetime "deleted_at"
    t.integer "position"
    t.index ["entity_type", "name", "user_id"], name: "index_attribute_categories_on_entity_type_and_name_and_user_id"
    t.index ["entity_type"], name: "index_attribute_categories_on_entity_type"
    t.index ["name"], name: "index_attribute_categories_on_name"
    t.index ["user_id"], name: "index_attribute_categories_on_user_id"
  end
```
#### `attribute_fields`

```ruby
  create_table "attribute_fields", force: :cascade do |t|
    t.integer "user_id"
    t.integer "attribute_category_id", null: false
    t.string "name", null: false
    t.string "label", null: false
    t.string "field_type", null: false
    t.text "description"
    t.string "privacy", default: "public", null: false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.boolean "hidden", default: false
    t.datetime "deleted_at"
    t.string "old_column_source"
    t.integer "position"
    t.json "field_options"
    t.boolean "migrated_from_legacy", default: false
    t.index ["attribute_category_id", "deleted_at"], name: "index_attribute_fields_on_attribute_category_id_and_deleted_at"
    t.index ["attribute_category_id", "label", "old_column_source", "field_type"], name: "attribute_fields_aci_label_ocs_ft"
    t.index ["attribute_category_id", "label", "old_column_source", "user_id", "field_type"], name: "attribute_fields_aci_label_ocs_ui_ft"
    t.index ["attribute_category_id", "old_column_source", "user_id", "field_type"], name: "attribute_fields_aci_ocs_ui_ft"
    t.index ["deleted_at", "attribute_category_id"], name: "deleted_at__attribute_category_id"
    t.index ["deleted_at", "name"], name: "index_attribute_fields_on_deleted_at_and_name"
    t.index ["deleted_at", "position"], name: "index_attribute_fields_on_deleted_at_and_position"
    t.index ["deleted_at", "user_id", "attribute_category_id", "label", "hidden"], name: "attribute_fields_da_ui_aci_l_h"
    t.index ["user_id", "attribute_category_id", "field_type", "deleted_at"], name: "special_field_type_index"
    t.index ["user_id", "attribute_category_id", "label", "hidden", "deleted_at"], name: "field_lookup_by_label_index"
    t.index ["user_id", "attribute_category_id", "label", "old_column_source", "field_type", "deleted_at"], name: "temporary_migration_lookup_with_deleted_index"
    t.index ["user_id", "attribute_category_id", "label", "old_column_source", "field_type"], name: "temporary_migration_lookup_index"
    t.index ["user_id", "attribute_category_id"], name: "index_attribute_fields_on_user_id_and_attribute_category_id"
    t.index ["user_id", "field_type"], name: "index_attribute_fields_on_user_id_and_field_type"
    t.index ["user_id", "name"], name: "index_attribute_fields_on_user_id_and_name"
    t.index ["user_id", "old_column_source"], name: "index_attribute_fields_on_user_id_and_old_column_source"
    t.index ["user_id"], name: "index_attribute_fields_on_user_id"
  end
```
#### `attributes`

```ruby
  create_table "attributes", force: :cascade do |t|
    t.integer "user_id"
    t.integer "attribute_field_id"
    t.string "entity_type", null: false
    t.integer "entity_id", null: false
    t.text "value"
    t.string "privacy", default: "private", null: false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.datetime "deleted_at"
    t.integer "word_count_cache"
    t.index ["attribute_field_id", "deleted_at", "entity_id", "entity_type"], name: "attributes_afi_deleted_at_entity_id_entity_type"
    t.index ["attribute_field_id", "deleted_at"], name: "index_attributes_on_attribute_field_id_and_deleted_at"
    t.index ["attribute_field_id", "user_id", "entity_type", "entity_id", "deleted_at"], name: "attributes_afi_ui_et_ei_da"
    t.index ["deleted_at", "attribute_field_id", "entity_type", "entity_id"], name: "deleted_at__attribute_field_id__entity_type_and_id"
    t.index ["deleted_at", "user_id", "attribute_field_id", "entity_type", "entity_id", "id"], name: "all_the_export_fields_with_sort"
    t.index ["deleted_at", "user_id", "attribute_field_id", "entity_type", "entity_id"], name: "all_the_export_fields"
    t.index ["entity_type", "entity_id"], name: "index_attributes_on_entity_type_and_entity_id"
    t.index ["user_id", "attribute_field_id"], name: "index_attributes_on_user_id_and_attribute_field_id"
    t.index ["user_id", "deleted_at"], name: "index_attributes_on_user_id_and_deleted_at"
    t.index ["user_id", "entity_type", "entity_id"], name: "index_attributes_on_user_id_and_entity_type_and_entity_id"
    t.index ["user_id"], name: "index_attributes_on_user_id"
  end
```
#### `books`

```ruby
  create_table "books", force: :cascade do |t|
    t.integer "user_id", null: false
    t.integer "universe_id"
    t.string "name"
    t.string "subtitle"
    t.text "description"
    t.text "blurb"
    t.integer "status", default: 0
    t.string "privacy", default: "private"
    t.datetime "archived_at"
    t.datetime "deleted_at"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.boolean "favorite", default: false, null: false
    t.string "page_type", default: "Book"
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_books_on_universe_id"
    t.index ["user_id", "deleted_at"], name: "index_books_on_user_id_and_deleted_at"
    t.index ["user_id"], name: "index_books_on_user_id"
  end
```
#### `book_documents`

```ruby
  create_table "book_documents", force: :cascade do |t|
    t.integer "book_id", null: false
    t.integer "document_id", null: false
    t.integer "position"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.index ["book_id", "position"], name: "index_book_documents_on_book_id_and_position"
    t.index ["book_id"], name: "index_book_documents_on_book_id"
    t.index ["document_id", "book_id"], name: "index_book_documents_on_document_id_and_book_id", unique: true
    t.index ["document_id"], name: "index_book_documents_on_document_id"
  end
```
#### `documents`

```ruby
  create_table "documents", force: :cascade do |t|
    t.integer "user_id"
    t.text "body"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "title", default: "Untitled document"
    t.string "privacy", default: "private"
    t.text "synopsis"
    t.datetime "deleted_at"
    t.integer "universe_id"
    t.boolean "favorite", default: false
    t.text "notes_text"
    t.integer "folder_id"
    t.integer "cached_word_count"
    t.datetime "archived_at"
    t.integer "status", default: 0
    t.index ["archived_at"], name: "index_documents_on_archived_at"
    t.index ["deleted_at", "universe_id", "user_id"], name: "index_documents_on_deleted_at_and_universe_id_and_user_id"
    t.index ["deleted_at", "universe_id"], name: "index_documents_on_deleted_at_and_universe_id"
    t.index ["folder_id"], name: "index_documents_on_folder_id"
    t.index ["status"], name: "index_documents_on_status"
    t.index ["universe_id", "deleted_at"], name: "index_documents_on_universe_id_and_deleted_at"
    t.index ["universe_id"], name: "index_documents_on_universe_id"
    t.index ["user_id", "archived_at", "deleted_at"], name: "index_documents_on_user_archived_deleted"
    t.index ["user_id", "deleted_at"], name: "index_documents_on_user_id_and_deleted_at"
    t.index ["user_id", "privacy", "deleted_at"], name: "index_documents_on_user_privacy_deleted"
    t.index ["user_id"], name: "index_documents_on_user_id"
  end
```
#### `document_revisions`

```ruby
  create_table "document_revisions", force: :cascade do |t|
    t.integer "document_id", null: false
    t.string "title"
    t.string "body"
    t.string "synopsis"
    t.integer "universe_id"
    t.string "notes_text"
    t.datetime "deleted_at"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.integer "cached_word_count"
    t.index ["document_id"], name: "index_document_revisions_on_document_id"
  end
```
#### `content_pages`

```ruby
  create_table "content_pages", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "archived_at"
    t.index ["universe_id"], name: "index_content_pages_on_universe_id"
    t.index ["user_id"], name: "index_content_pages_on_user_id"
  end
```
#### `page_references`

```ruby
  create_table "page_references", force: :cascade do |t|
    t.string "referencing_page_type", null: false
    t.integer "referencing_page_id", null: false
    t.string "referenced_page_type", null: false
    t.integer "referenced_page_id", null: false
    t.integer "attribute_field_id"
    t.string "cached_relation_title"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.string "reference_type"
    t.index ["attribute_field_id"], name: "index_page_references_on_attribute_field_id"
    t.index ["referenced_page_type", "referenced_page_id"], name: "page_reference_referenced_page"
    t.index ["referencing_page_type", "referencing_page_id"], name: "page_reference_referencing_page"
  end
```
#### `document_concepts`

```ruby
  create_table "document_concepts", force: :cascade do |t|
    t.integer "document_analysis_id"
    t.string "text"
    t.float "relevance"
    t.string "reference_link"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["document_analysis_id"], name: "index_document_concepts_on_document_analysis_id"
  end
```
#### `document_entities`

```ruby
  create_table "document_entities", force: :cascade do |t|
    t.string "entity_type"
    t.integer "entity_id"
    t.string "text"
    t.float "relevance"
    t.integer "document_analysis_id"
    t.string "sentiment_label"
    t.float "sentiment_score"
    t.float "sadness_score"
    t.float "joy_score"
    t.float "fear_score"
    t.float "disgust_score"
    t.float "anger_score"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["document_analysis_id"], name: "index_document_entities_on_document_analysis_id"
    t.index ["entity_type", "entity_id"], name: "index_document_entities_on_entity_type_and_entity_id"
  end
```
#### `universes`

```ruby
  create_table "universes", force: :cascade do |t|
    t.string "name", null: false
    t.text "description"
    t.text "history"
    t.text "notes"
    t.text "private_notes"
    t.string "privacy"
    t.integer "user_id"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string "laws_of_physics"
    t.string "magic_system"
    t.string "technology"
    t.string "genre"
    t.datetime "deleted_at"
    t.string "page_type", default: "Universe"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_universes_on_deleted_at_and_id"
    t.index ["deleted_at", "user_id"], name: "index_universes_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_universes_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_universes_on_id_and_deleted_at"
    t.index ["user_id", "privacy", "deleted_at"], name: "index_universes_on_user_privacy_deleted"
    t.index ["user_id", "updated_at"], name: "index_universes_on_user_updated"
    t.index ["user_id"], name: "index_universes_on_user_id"
  end
```
#### `characters`

```ruby
  create_table "characters", force: :cascade do |t|
    t.string "name", null: false
    t.string "role"
    t.string "gender"
    t.string "age"
    t.string "height"
    t.string "weight"
    t.string "haircolor"
    t.string "hairstyle"
    t.string "facialhair"
    t.string "eyecolor"
    t.string "race"
    t.string "skintone"
    t.string "bodytype"
    t.string "identmarks"
    t.text "religion"
    t.text "politics"
    t.text "prejudices"
    t.text "occupation"
    t.text "pets"
    t.text "mannerisms"
    t.text "birthday"
    t.text "birthplace"
    t.text "education"
    t.text "background"
    t.string "fave_color"
    t.string "fave_food"
    t.string "fave_possession"
    t.string "fave_weapon"
    t.string "fave_animal"
    t.text "notes"
    t.text "private_notes"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string "privacy"
    t.string "archetype"
    t.string "aliases"
    t.string "motivations"
    t.string "flaws"
    t.string "talents"
    t.string "hobbies"
    t.string "personality_type"
    t.datetime "deleted_at"
    t.string "page_type", default: "Character"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_characters_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_characters_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_characters_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_characters_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_characters_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_characters_on_universe_id"
    t.index ["user_id", "privacy", "deleted_at"], name: "index_characters_on_user_privacy_deleted"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_characters_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id", "updated_at"], name: "index_characters_on_user_updated"
    t.index ["user_id"], name: "index_characters_on_user_id"
  end
```
#### `locations`

```ruby
  create_table "locations", force: :cascade do |t|
    t.string "name", null: false
    t.string "type_of"
    t.text "description"
    t.string "map"
    t.string "population"
    t.string "language"
    t.string "currency"
    t.string "motto"
    t.text "capital"
    t.text "largest_city"
    t.text "notable_cities"
    t.text "area"
    t.text "crops"
    t.text "located_at"
    t.string "established_year"
    t.text "notable_wars"
    t.text "notes"
    t.text "private_notes"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string "privacy", default: "private", null: false
    t.string "laws"
    t.string "climate"
    t.string "founding_story"
    t.string "sports"
    t.datetime "deleted_at"
    t.string "page_type", default: "Location"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_locations_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_locations_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_locations_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_locations_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_locations_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_locations_on_universe_id"
    t.index ["user_id", "privacy", "deleted_at"], name: "index_locations_on_user_privacy_deleted"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_locations_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id", "updated_at"], name: "index_locations_on_user_updated"
    t.index ["user_id"], name: "index_locations_on_user_id"
  end
```
#### `scenes`

```ruby
  create_table "scenes", force: :cascade do |t|
    t.integer "scene_number"
    t.string "name"
    t.string "summary"
    t.integer "universe_id"
    t.integer "user_id"
    t.string "cause"
    t.string "description"
    t.string "results"
    t.string "prose"
    t.string "notes"
    t.string "private_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "privacy"
    t.datetime "deleted_at"
    t.string "page_type", default: "Scene"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_scenes_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_scenes_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_scenes_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_scenes_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_scenes_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_scenes_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_scenes_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_scenes_on_user_id"
  end
```
#### `timelines`

```ruby
  create_table "timelines", force: :cascade do |t|
    t.string "name"
    t.integer "universe_id"
    t.integer "user_id", null: false
    t.string "page_type", default: "Timeline"
    t.datetime "deleted_at"
    t.datetime "archived_at"
    t.string "privacy", default: "private"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.string "description"
    t.string "subtitle"
    t.string "notes"
    t.string "private_notes"
    t.boolean "favorite", default: false
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_timelines_on_universe_id"
    t.index ["user_id", "privacy", "deleted_at"], name: "index_timelines_on_user_privacy_deleted"
    t.index ["user_id"], name: "index_timelines_on_user_id"
  end
```
#### `timeline_events`

```ruby
  create_table "timeline_events", force: :cascade do |t|
    t.integer "timeline_id", null: false
    t.string "time_label"
    t.string "title"
    t.string "description"
    t.string "notes"
    t.integer "position"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.datetime "deleted_at"
    t.string "event_type", default: "general"
    t.string "importance_level", default: "minor"
    t.string "end_time_label"
    t.string "status", default: "completed"
    t.text "private_notes"
    t.integer "cached_word_count", default: 0
    t.index ["event_type"], name: "index_timeline_events_on_event_type"
    t.index ["importance_level"], name: "index_timeline_events_on_importance_level"
    t.index ["status"], name: "index_timeline_events_on_status"
    t.index ["timeline_id"], name: "index_timeline_events_on_timeline_id"
  end
```
#### `timeline_event_entities`

```ruby
  create_table "timeline_event_entities", force: :cascade do |t|
    t.string "entity_type", null: false
    t.integer "entity_id", null: false
    t.integer "timeline_event_id", null: false
    t.string "notes"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.index ["entity_type", "entity_id"], name: "index_timeline_event_entities_on_entity_type_and_entity_id"
    t.index ["timeline_event_id"], name: "index_timeline_event_entities_on_timeline_event_id"
  end
```
#### `buildings`

```ruby
  create_table "buildings", force: :cascade do |t|
    t.string "name"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type", default: "Building"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_buildings_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_buildings_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_buildings_on_user_id"
  end
```
#### `conditions`

```ruby
  create_table "conditions", force: :cascade do |t|
    t.string "name"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type", default: "Condition"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_conditions_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_conditions_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_conditions_on_user_id"
  end
```
#### `continents`

```ruby
  create_table "continents", force: :cascade do |t|
    t.string "name"
    t.integer "user_id", null: false
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type", default: "Continent"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id", "universe_id"], name: "index_continents_on_deleted_at_and_id_and_universe_id"
    t.index ["deleted_at", "id", "user_id"], name: "index_continents_on_deleted_at_and_id_and_user_id"
    t.index ["deleted_at", "id"], name: "index_continents_on_deleted_at_and_id"
    t.index ["deleted_at", "user_id"], name: "index_continents_on_deleted_at_and_user_id"
    t.index ["universe_id"], name: "index_continents_on_universe_id"
    t.index ["user_id"], name: "index_continents_on_user_id"
  end
```
#### `countries`

```ruby
  create_table "countries", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "other_names"
    t.integer "universe_id"
    t.string "population"
    t.string "currency"
    t.string "laws"
    t.string "sports"
    t.string "area"
    t.string "crops"
    t.string "climate"
    t.string "founding_story"
    t.string "established_year"
    t.string "notable_wars"
    t.string "notes"
    t.string "private_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "deleted_at"
    t.string "privacy"
    t.integer "user_id"
    t.string "page_type", default: "Country"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_countries_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_countries_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_countries_on_deleted_at_and_user_id"
    t.index ["id", "deleted_at"], name: "index_countries_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_countries_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_countries_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_countries_on_user_id"
  end
```
#### `creatures`

```ruby
  create_table "creatures", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "type_of"
    t.string "other_names"
    t.integer "universe_id"
    t.string "color"
    t.string "shape"
    t.string "size"
    t.string "notable_features"
    t.string "materials"
    t.string "preferred_habitat"
    t.string "sounds"
    t.string "strengths"
    t.string "weaknesses"
    t.string "spoils"
    t.string "aggressiveness"
    t.string "attack_method"
    t.string "defense_method"
    t.string "maximum_speed"
    t.string "food_sources"
    t.string "migratory_patterns"
    t.string "reproduction"
    t.string "herd_patterns"
    t.string "similar_animals"
    t.string "symbolisms"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "user_id"
    t.string "notes"
    t.string "private_notes"
    t.string "privacy"
    t.datetime "deleted_at"
    t.string "phylum"
    t.string "class_string"
    t.string "order"
    t.string "family"
    t.string "genus"
    t.string "species"
    t.string "page_type", default: "Creature"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_creatures_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_creatures_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_creatures_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_creatures_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_creatures_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_creatures_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_creatures_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_creatures_on_user_id"
  end
```
#### `deities`

```ruby
  create_table "deities", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "other_names"
    t.string "physical_description"
    t.string "height"
    t.string "weight"
    t.string "symbols"
    t.string "elements"
    t.string "strengths"
    t.string "weaknesses"
    t.string "prayers"
    t.string "rituals"
    t.string "human_interaction"
    t.string "notable_events"
    t.string "family_history"
    t.string "life_story"
    t.string "notes"
    t.string "private_notes"
    t.string "privacy"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "page_type", default: "Deity"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_deities_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_deities_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_deities_on_deleted_at_and_user_id"
    t.index ["id", "deleted_at"], name: "index_deities_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_deities_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_deities_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_deities_on_user_id"
  end
```
#### `floras`

```ruby
  create_table "floras", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "aliases"
    t.string "order"
    t.string "family"
    t.string "genus"
    t.string "colorings"
    t.string "size"
    t.string "smell"
    t.string "taste"
    t.string "fruits"
    t.string "seeds"
    t.string "nuts"
    t.string "berries"
    t.string "medicinal_purposes"
    t.string "reproduction"
    t.string "seasonality"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "user_id"
    t.integer "universe_id"
    t.string "notes"
    t.string "private_notes"
    t.string "privacy"
    t.datetime "deleted_at"
    t.string "material_uses"
    t.string "page_type", default: "Flora"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_floras_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_floras_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_floras_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_floras_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_floras_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_floras_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_floras_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_floras_on_user_id"
  end
```
#### `foods`

```ruby
  create_table "foods", force: :cascade do |t|
    t.string "name"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type", default: "Food"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_foods_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_foods_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_foods_on_user_id"
  end
```
#### `governments`

```ruby
  create_table "governments", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "type_of_government"
    t.string "power_structure"
    t.string "power_source"
    t.string "checks_and_balances"
    t.string "sociopolitical"
    t.string "socioeconomical"
    t.string "geocultural"
    t.string "laws"
    t.string "immigration"
    t.string "privacy_ideologies"
    t.string "electoral_process"
    t.string "term_lengths"
    t.string "criminal_system"
    t.string "approval_ratings"
    t.string "military"
    t.string "navy"
    t.string "airforce"
    t.string "space_program"
    t.string "international_relations"
    t.string "civilian_life"
    t.string "founding_story"
    t.string "flag_design_story"
    t.string "notable_wars"
    t.string "notes"
    t.string "private_notes"
    t.string "privacy"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "page_type", default: "Government"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_governments_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_governments_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_governments_on_deleted_at_and_user_id"
    t.index ["id", "deleted_at"], name: "index_governments_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_governments_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_governments_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_governments_on_user_id"
  end
```
#### `groups`

```ruby
  create_table "groups", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "other_names"
    t.integer "universe_id"
    t.integer "user_id"
    t.string "organization_structure"
    t.string "motivation"
    t.string "goal"
    t.string "obstacles"
    t.string "risks"
    t.string "inventory"
    t.string "notes"
    t.string "private_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "privacy"
    t.datetime "deleted_at"
    t.string "page_type", default: "Group"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_groups_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_groups_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_groups_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_groups_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_groups_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_groups_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_groups_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_groups_on_user_id"
  end
```
#### `items`

```ruby
  create_table "items", force: :cascade do |t|
    t.string "name", null: false
    t.string "item_type"
    t.text "description"
    t.string "weight"
    t.string "original_owner"
    t.string "current_owner"
    t.text "made_by"
    t.text "materials"
    t.string "year_made"
    t.text "magic"
    t.text "notes"
    t.text "private_notes"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string "privacy", default: "private", null: false
    t.datetime "deleted_at"
    t.string "page_type", default: "Item"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_items_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_items_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_items_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_items_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_items_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_items_on_universe_id"
    t.index ["user_id", "privacy", "deleted_at"], name: "index_items_on_user_privacy_deleted"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_items_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id", "updated_at"], name: "index_items_on_user_updated"
    t.index ["user_id"], name: "index_items_on_user_id"
  end
```
#### `jobs`

```ruby
  create_table "jobs", force: :cascade do |t|
    t.string "name"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type", default: "Job"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_jobs_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_jobs_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_jobs_on_user_id"
  end
```
#### `landmarks`

```ruby
  create_table "landmarks", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "other_names"
    t.integer "universe_id"
    t.string "size"
    t.string "materials"
    t.string "colors"
    t.string "creation_story"
    t.string "established_year"
    t.string "notes"
    t.string "private_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "deleted_at"
    t.string "privacy"
    t.integer "user_id"
    t.string "page_type", default: "Landmark"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_landmarks_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_landmarks_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_landmarks_on_deleted_at_and_user_id"
    t.index ["id", "deleted_at"], name: "index_landmarks_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_landmarks_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_landmarks_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_landmarks_on_user_id"
  end
```
#### `languages`

```ruby
  create_table "languages", force: :cascade do |t|
    t.string "name"
    t.string "other_names"
    t.integer "universe_id"
    t.integer "user_id"
    t.string "history"
    t.string "typology"
    t.string "dialectical_information"
    t.string "register"
    t.string "phonology"
    t.string "grammar"
    t.string "numbers"
    t.string "quantifiers"
    t.string "notes"
    t.string "private_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "privacy"
    t.datetime "deleted_at"
    t.string "page_type", default: "Language"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_languages_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_languages_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_languages_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_languages_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_languages_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_languages_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_languages_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_languages_on_user_id"
  end
```
#### `lores`

```ruby
  create_table "lores", force: :cascade do |t|
    t.string "name"
    t.integer "user_id", null: false
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.datetime "archived_at"
    t.string "privacy"
    t.boolean "favorite", default: false
    t.string "page_type", default: "Lore"
    t.datetime "created_at", precision: 6, null: false
    t.datetime "updated_at", precision: 6, null: false
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_lores_on_universe_id"
    t.index ["user_id"], name: "index_lores_on_user_id"
  end
```
#### `magics`

```ruby
  create_table "magics", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "type_of"
    t.integer "universe_id"
    t.integer "user_id"
    t.string "visuals"
    t.string "effects"
    t.string "positive_effects"
    t.string "negative_effects"
    t.string "neutral_effects"
    t.string "element"
    t.string "resource_costs"
    t.string "materials"
    t.string "skills_required"
    t.string "limitations"
    t.string "notes"
    t.string "private_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "privacy"
    t.datetime "deleted_at"
    t.string "page_type", default: "Magic"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_magics_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_magics_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_magics_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_magics_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_magics_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_magics_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_magics_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_magics_on_user_id"
  end
```
#### `planets`

```ruby
  create_table "planets", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "size"
    t.string "surface"
    t.string "climate"
    t.string "weather"
    t.string "water_content"
    t.string "natural_resources"
    t.string "length_of_day"
    t.string "length_of_night"
    t.string "calendar_system"
    t.string "population"
    t.string "moons"
    t.string "orbit"
    t.string "visible_constellations"
    t.string "first_inhabitants_story"
    t.string "world_history"
    t.string "private_notes"
    t.string "privacy"
    t.integer "universe_id"
    t.integer "user_id"
    t.datetime "deleted_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "notes"
    t.string "page_type", default: "Planet"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_planets_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_planets_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_planets_on_deleted_at_and_user_id"
    t.index ["id", "deleted_at"], name: "index_planets_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_planets_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_planets_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_planets_on_user_id"
  end
```
#### `races`

```ruby
  create_table "races", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "other_names"
    t.integer "universe_id"
    t.integer "user_id"
    t.string "body_shape"
    t.string "skin_colors"
    t.string "height"
    t.string "weight"
    t.string "notable_features"
    t.string "variance"
    t.string "clothing"
    t.string "strengths"
    t.string "weaknesses"
    t.string "traditions"
    t.string "beliefs"
    t.string "governments"
    t.string "technologies"
    t.string "occupations"
    t.string "economics"
    t.string "favorite_foods"
    t.string "notable_events"
    t.string "notes"
    t.string "private_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "privacy"
    t.datetime "deleted_at"
    t.string "page_type", default: "Race"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_races_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_races_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_races_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_races_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_races_on_id_and_deleted_at"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_races_on_user_id_and_universe_id_and_deleted_at"
  end
```
#### `religions`

```ruby
  create_table "religions", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "other_names"
    t.integer "universe_id"
    t.integer "user_id"
    t.string "origin_story"
    t.string "teachings"
    t.string "prophecies"
    t.string "places_of_worship"
    t.string "worship_services"
    t.string "obligations"
    t.string "paradise"
    t.string "initiation"
    t.string "rituals"
    t.string "holidays"
    t.string "notes"
    t.string "private_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "privacy"
    t.datetime "deleted_at"
    t.string "page_type", default: "Religion"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_religions_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_religions_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_religions_on_deleted_at_and_user_id"
    t.index ["deleted_at"], name: "index_religions_on_deleted_at"
    t.index ["id", "deleted_at"], name: "index_religions_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_religions_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_religions_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_religions_on_user_id"
  end
```
#### `schools`

```ruby
  create_table "schools", force: :cascade do |t|
    t.string "name"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type", default: "School"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_schools_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_schools_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_schools_on_user_id"
  end
```
#### `sports`

```ruby
  create_table "sports", force: :cascade do |t|
    t.string "name"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type", default: "Sport"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_sports_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_sports_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_sports_on_user_id"
  end
```
#### `technologies`

```ruby
  create_table "technologies", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "other_names"
    t.string "materials"
    t.string "manufacturing_process"
    t.string "sales_process"
    t.string "cost"
    t.string "rarity"
    t.string "purpose"
    t.string "how_it_works"
    t.string "resources_used"
    t.string "physical_description"
    t.string "size"
    t.string "weight"
    t.string "colors"
    t.string "notes"
    t.string "private_notes"
    t.string "privacy"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "page_type", default: "Technology"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_technologies_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_technologies_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_technologies_on_deleted_at_and_user_id"
    t.index ["id", "deleted_at"], name: "index_technologies_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_technologies_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_technologies_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_technologies_on_user_id"
  end
```
#### `towns`

```ruby
  create_table "towns", force: :cascade do |t|
    t.string "name"
    t.string "description"
    t.string "other_names"
    t.string "laws"
    t.string "sports"
    t.string "politics"
    t.string "founding_story"
    t.string "established_year"
    t.string "notes"
    t.string "private_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.integer "user_id"
    t.string "page_type", default: "Town"
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["deleted_at", "id"], name: "index_towns_on_deleted_at_and_id"
    t.index ["deleted_at", "universe_id"], name: "index_towns_on_deleted_at_and_universe_id"
    t.index ["deleted_at", "user_id"], name: "index_towns_on_deleted_at_and_user_id"
    t.index ["id", "deleted_at"], name: "index_towns_on_id_and_deleted_at"
    t.index ["universe_id"], name: "index_towns_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_towns_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_towns_on_user_id"
  end
```
#### `traditions`

```ruby
  create_table "traditions", force: :cascade do |t|
    t.string "name"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type", default: "Tradition"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_traditions_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_traditions_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_traditions_on_user_id"
  end
```
#### `vehicles`

```ruby
  create_table "vehicles", force: :cascade do |t|
    t.string "name"
    t.integer "user_id"
    t.integer "universe_id"
    t.datetime "deleted_at"
    t.string "privacy"
    t.string "page_type", default: "Vehicle"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "archived_at"
    t.boolean "favorite", default: false
    t.boolean "columns_migrated_from_old_style", default: true
    t.integer "cached_word_count", default: 0
    t.index ["universe_id"], name: "index_vehicles_on_universe_id"
    t.index ["user_id", "universe_id", "deleted_at"], name: "index_vehicles_on_user_id_and_universe_id_and_deleted_at"
    t.index ["user_id"], name: "index_vehicles_on_user_id"
  end
```

### Related Relationship / Join Tables Observed

- `archenemyships`, `artifactships`, `best_friendships`, `building_countries`, `building_landmarks`, `building_locations`, `building_nearby_buildings`, `building_schools`
- `building_towns`, `capital_cities_relationships`, `character_birthtowns`, `character_companions`, `character_enemies`, `character_floras`, `character_friends`, `character_items`
- `character_love_interests`, `character_magics`, `character_technologies`, `childrenships`, `country_bordering_countries`, `country_creatures`, `country_floras`, `country_governments`
- `country_landmarks`, `country_languages`, `country_locations`, `country_religions`, `country_towns`, `creature_relationships`, `current_ownerships`, `deity_abilities`
- `deity_character_children`, `deity_character_parents`, `deity_character_partners`, `deity_character_siblings`, `deity_creatures`, `deity_deity_children`, `deity_deity_parents`, `deity_deity_partners`
- `deity_deity_siblings`, `deity_floras`, `deity_races`, `deity_related_landmarks`, `deity_related_towns`, `deity_relics`, `deity_religions`, `deityships`
- `famous_figureships`, `fatherships`, `flora_eaten_bies`, `flora_locations`, `flora_magical_effects`, `flora_relationships`, `group_allyships`, `group_clientships`
- `group_creatures`, `group_enemyships`, `group_equipmentships`, `group_leaderships`, `group_locationships`, `group_memberships`, `group_rivalships`, `group_supplierships`
- `headquarterships`, `key_itemships`, `largest_cities_relationships`, `location_capital_towns`, `location_landmarks`, `location_languageships`, `location_largest_towns`, `location_leaderships`
- `location_notable_towns`, `lore_believers`, `lore_buildings`, `lore_characters`, `lore_conditions`, `lore_continents`, `lore_countries`, `lore_created_traditions`
- `lore_creatures`, `lore_deities`, `lore_floras`, `lore_foods`, `lore_governments`, `lore_groups`, `lore_jobs`, `lore_landmarks`
- `lore_magics`, `lore_original_languages`, `lore_planets`, `lore_races`, `lore_related_lores`, `lore_religions`, `lore_schools`, `lore_sports`
- `lore_technologies`, `lore_towns`, `lore_traditions`, `lore_variations`, `lore_vehicles`, `magic_deityships`, `maker_relationships`, `motherships`
- `notable_cities_relationships`, `officeships`, `original_ownerships`, `ownerships`, `past_ownerships`, `planet_continents`, `planet_countries`, `planet_creatures`
- `planet_deities`, `planet_floras`, `planet_groups`, `planet_landmarks`, `planet_languages`, `planet_locations`, `planet_nearby_planets`, `planet_races`
- `planet_religions`, `planet_towns`, `raceships`, `religion_deities`, `religious_figureships`, `religious_locationships`, `religious_raceships`, `scene_characterships`
- `scene_itemships`, `scene_locationships`, `siblingships`, `sistergroupships`, `subgroupships`, `supergroupships`, `technology_characters`, `technology_child_technologies`
- `technology_countries`, `technology_creatures`, `technology_groups`, `technology_magics`, `technology_parent_technologies`, `technology_planets`, `technology_related_technologies`, `technology_towns`
- `town_citizens`, `town_countries`, `town_creatures`, `town_floras`, `town_groups`, `town_languages`, `town_nearby_landmarks`, `wildlifeships`


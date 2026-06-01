from __future__ import annotations

import os
from typing import Final


MOCK: Final = "mock"
OLLAMA_BASELINE: Final = "ollama_baseline"
VALID_ANALYSIS_MODES: Final = frozenset({MOCK, OLLAMA_BASELINE})
DEFAULT_ANALYSIS_MODE: Final = OLLAMA_BASELINE


def get_analysis_mode() -> str:
    mode = os.getenv("ANALYSIS_MODE", "").strip() or DEFAULT_ANALYSIS_MODE
    if mode not in VALID_ANALYSIS_MODES:
        valid_modes = ", ".join(sorted(VALID_ANALYSIS_MODES))
        raise ValueError(f"Invalid ANALYSIS_MODE '{mode}'. Expected one of: {valid_modes}.")
    return mode

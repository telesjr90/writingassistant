import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import analysis_modes


def test_missing_analysis_mode_defaults_to_ollama_baseline(monkeypatch):
    monkeypatch.delenv("ANALYSIS_MODE", raising=False)

    assert analysis_modes.get_analysis_mode() == analysis_modes.OLLAMA_BASELINE


def test_empty_analysis_mode_defaults_to_ollama_baseline(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "")

    assert analysis_modes.get_analysis_mode() == analysis_modes.OLLAMA_BASELINE


def test_mock_analysis_mode_is_selected(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "mock")

    assert analysis_modes.get_analysis_mode() == analysis_modes.MOCK


def test_ollama_baseline_analysis_mode_is_selected(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "ollama_baseline")

    assert analysis_modes.get_analysis_mode() == analysis_modes.OLLAMA_BASELINE


def test_invalid_analysis_mode_raises_clear_error(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "future_mode")

    with pytest.raises(ValueError, match="Invalid ANALYSIS_MODE 'future_mode'"):
        analysis_modes.get_analysis_mode()

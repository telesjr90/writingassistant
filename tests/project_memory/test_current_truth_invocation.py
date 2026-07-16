"""Direct and module invocation regressions for current-truth validation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_current_truth_validator_direct_script_invocation():
    result = _run("scripts/project_memory/validate_current_truth.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "PASS"
    assert "ModuleNotFoundError" not in result.stderr

def test_current_truth_validator_module_invocation():
    result = _run("-m", "scripts.project_memory.validate_current_truth")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "PASS"
    assert "ModuleNotFoundError" not in result.stderr

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bhsm.interface", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_neutral_action_json_commands_work_offline() -> None:
    for command in (
        "neutral-action-source-search",
        "neutral-action-stiffness",
        "neutral-physical-curvature-map",
        "neutral-action-response-cone",
        "neutral-action-spectral-closure",
    ):
        result = run_cli(command, "--format", "json")
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_neutral_action_markdown_report_names_exact_blockers() -> None:
    result = run_cli("neutral-action-closure-report", "--format", "markdown")
    assert result.returncode == 0, result.stderr
    assert "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION" in result.stdout
    assert "OPEN_MISSING_NUMERIC_STIFFNESS_LENGTH" in result.stdout
    assert "DIMENSIONFUL_MASS_NOT_AVAILABLE" in result.stdout


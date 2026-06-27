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


def test_radius_curvature_json_commands_work_offline() -> None:
    for command in (
        "neutral-propagation-radius",
        "neutral-physical-curvature",
        "neutral-radius-curvature-closure",
        "dimensionful-neutrino-mass-candidate",
    ):
        result = run_cli(command, "--format", "json")
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_radius_curvature_markdown_reports_all_failed_gates() -> None:
    result = run_cli("neutral-radius-curvature-report", "--format", "markdown")
    assert result.returncode == 0, result.stderr
    assert "CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE" in result.stdout
    assert "CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE" in result.stdout
    assert "FAIL: mass_per_length" in result.stdout


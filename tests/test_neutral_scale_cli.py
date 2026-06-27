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


def test_all_neutral_scale_json_commands_work_offline() -> None:
    commands = (
        "neutrino-scale-law",
        "neutral-scale-candidates",
        "neutral-threshold-energy-map",
        "neutral-boundary-measure",
        "neutrino-dimensionful-mass",
    )
    for command in commands:
        result = run_cli(command, "--format", "json")
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_neutral_scale_markdown_report_is_claim_bounded() -> None:
    result = run_cli("neutrino-scale-report", "--format", "markdown")
    assert result.returncode == 0, result.stderr
    assert "OPEN_MISSING_NEUTRAL_SCALE" in result.stdout
    assert "not, by itself, a physical eV/GeV mass" in result.stdout


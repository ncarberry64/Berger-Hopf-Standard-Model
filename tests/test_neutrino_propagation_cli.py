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


def test_all_neutrino_propagation_json_commands_work_offline() -> None:
    commands = (
        ("neutrino-propagation", "--format", "json"),
        ("neutrino-propagation-report", "--format", "json"),
        ("neutrino-effective-mass", "--format", "json"),
        ("neutrino-observable-map", "--format", "json"),
        ("neutrino-scale-law", "--format", "json"),
        ("neutrino-threshold-response", "--format", "json"),
    )
    for command in commands:
        result = run_cli(*command)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_neutrino_markdown_report_is_concise_and_bounded() -> None:
    result = run_cli("neutrino-propagation-report", "--format", "markdown")
    assert result.returncode == 0
    assert "CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE" in result.stdout
    assert "dimensionless" in result.stdout
    assert "static rest-mass matrix" in result.stdout

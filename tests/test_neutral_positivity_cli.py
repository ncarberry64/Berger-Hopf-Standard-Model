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


def test_neutral_positivity_json_commands_work_offline() -> None:
    for command in (
        "neutral-kernel-exact-audit",
        "neutral-admissible-domain",
        "neutral-positivity-proof",
        "neutral-positivity-counterexample",
    ):
        result = run_cli(command, "--format", "json")
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_neutral_positivity_markdown_reports_single_conditional_verdict() -> None:
    result = run_cli("neutral-positivity-report", "--format", "markdown")
    assert result.returncode == 0, result.stderr
    assert "CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE" in result.stdout
    assert "Raw PSD | no" in result.stdout
    assert "Positivity without thresholding | yes" in result.stdout


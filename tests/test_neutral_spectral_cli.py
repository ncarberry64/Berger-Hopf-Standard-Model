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


def test_neutral_spectral_json_commands_work_offline() -> None:
    for command in (
        "neutrino-mass-gap-action",
        "legacy-dimensional-gate",
        "neutral-stiffness-ratio",
        "neutral-spectral-gap",
        "neutral-kernel-positivity",
    ):
        result = run_cli(command, "--format", "json")
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_neutral_spectral_markdown_report_is_claim_safe() -> None:
    result = run_cli("neutral-spectral-report", "--format", "markdown")
    assert result.returncode == 0, result.stderr
    assert "ARTIFACT_BACKED_MASS_GAP_ACTION" in result.stdout
    assert "DIMENSIONFUL_MASS_NOT_AVAILABLE" in result.stdout
    assert "RAW_KERNEL_NOT_POSITIVE_SEMIDEFINITE" in result.stdout


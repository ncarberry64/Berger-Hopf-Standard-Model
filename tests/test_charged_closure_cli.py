from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(command: str, output_format: str = "json") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bhsm.interface", command, "--format", output_format],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_all_charged_json_commands_work_offline() -> None:
    for command in (
        "charged-source-search",
        "charged-action-stiffness",
        "eta-l-source-audit",
        "ckm-exponent-source-audit",
        "charged-mixing-law-audit",
        "charged-dimensional-audit",
    ):
        result = run_cli(command)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_charged_markdown_report_names_open_sources() -> None:
    result = run_cli("charged-closure-report", "markdown")
    assert result.returncode == 0, result.stderr
    assert "CONDITIONAL_CHARGED_ACTION_STIFFNESS_CANDIDATE" in result.stdout
    assert "OPEN_MISSING_CKM_EXPONENT_DERIVATION" in result.stdout
    assert "No frozen charged or CKM value is changed." in result.stdout

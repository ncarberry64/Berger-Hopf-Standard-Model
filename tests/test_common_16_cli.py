from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(command: str, output_format: str = "json") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bhsm.interface", command, "--format", output_format],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_common_16_json_commands_run_offline() -> None:
    for command in (
        "common-16-source-search",
        "common-16-incidence-audit",
        "common-16-bridge-beta-audit",
        "common-16-ckm-transport-audit",
        "common-16-provenance-audit",
        "final-completion-ledger",
    ):
        result = _run(command)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_final_completion_markdown_is_conservative() -> None:
    result = _run("final-completion-status", "markdown")
    assert result.returncode == 0, result.stderr
    assert "OPEN_MISSING_CKM_EXPONENT_DERIVATION" in result.stdout
    assert "Full completion and physical eV/GeV neutrino mass are not claimed" in result.stdout

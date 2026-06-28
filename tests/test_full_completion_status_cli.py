from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(command: str, output_format: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bhsm.interface", command, "--format", output_format],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_full_completion_json_commands_work_offline() -> None:
    for command in (
        "full-completion-ledger",
        "full-completion-priority-map",
        "full-completion-selected-target",
    ):
        result = run_cli(command, "json")
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_full_completion_status_is_conservative_in_both_formats() -> None:
    result = run_cli("full-completion-status", "json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["full_completion_status"] == "INTEGRATED_CONDITIONAL_ARCHITECTURE_WITH_OPEN_BLOCKERS"
    assert payload["completion_claimed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False
    assert payload["empirical_inputs_used"] is False

    markdown = run_cli("full-completion-status", "markdown")
    assert markdown.returncode == 0, markdown.stderr
    assert "No physical eV/GeV neutrino mass is emitted." in markdown.stdout
    assert "PARTIAL_CLOSURE_BOUNDARY_MEASURE_SHAPE_AND_IDENTITY_TRANSPORT" in markdown.stdout

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


def test_json_minimal_action_commands_work_offline() -> None:
    commands = (
        ("minimal-action", "--format", "json"),
        ("minimal-action-status",),
        ("close-minimal-action", "cp_o_int", "--format", "json"),
        ("close-minimal-action", "X_ch", "--format", "json"),
        ("close-minimal-action", "neutrino_basis_scale", "--format", "json"),
    )
    for command in commands:
        result = run_cli(*command)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_markdown_report_command_is_concise() -> None:
    result = run_cli("minimal-action-report", "--format", "markdown")
    assert result.returncode == 0
    assert "# BHSM Minimal Action Closure" in result.stdout
    assert "ARTIFACT_BACKED" in result.stdout
    assert "CONDITIONAL_ACTION_THEOREM" in result.stdout
    assert "CONDITIONAL_PROPAGATION_THEOREM" in result.stdout
    assert len(result.stdout.splitlines()) < 25

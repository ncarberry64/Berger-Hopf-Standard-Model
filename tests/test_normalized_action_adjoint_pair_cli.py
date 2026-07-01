import json
import os
import subprocess
import sys
from pathlib import Path


COMMANDS = (
    "normalized-action-adjoint-pair-search",
    "normalized-action-adjoint-pair-selection",
    "hermitian-charged-current-rule",
    "ckm-transport-space-gate",
    "ckm-alternative-channel-blockers",
    "normalized-action-adjoint-pair-report",
)
ROOT = Path(__file__).resolve().parents[1]


def _env():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return env


def test_normalized_action_adjoint_pair_cli_commands_work_offline_json():
    for command in COMMANDS:
        result = subprocess.run(
            [sys.executable, "-m", "bhsm.interface", command, "--format", "json"],
            cwd=ROOT,
            env=_env(),
            capture_output=True,
            text=True,
            check=True,
        )
        assert json.loads(result.stdout)


def test_normalized_action_adjoint_pair_report_markdown_cli():
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "normalized-action-adjoint-pair-report", "--format", "markdown"],
        cwd=ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "# Normalized Action Adjoint-Pair CKM Audit" in result.stdout
    assert "OPEN_MISSING_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION" in result.stdout

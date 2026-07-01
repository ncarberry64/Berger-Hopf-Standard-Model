import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (
    "charged-current-action-search",
    "normalized-charged-current-action-term",
    "charged-current-transport-space",
    "hermitian-adjoint-pair-transport-gate",
    "ckm-transport-space-application-gate",
    "charged-current-action-report",
)


def _env():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return env


def test_charged_current_action_cli_commands_work_offline_json():
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


def test_charged_current_action_report_markdown_cli():
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "charged-current-action-report", "--format", "markdown"],
        cwd=ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "# Charged-Current Action Transport-Space Audit" in result.stdout
    assert "OPEN_MISSING_NORMALIZED_CHARGED_CURRENT_ACTION_TERM" in result.stdout

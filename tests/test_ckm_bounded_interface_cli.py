import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (
    "ckm-bounded-interface-search",
    "ckm-bounded-interface-term",
    "normalized-projector-sandwich",
    "projector-domain-codomain",
    "paired-term-normalization",
    "ckm-identification-gate",
    "ckm-transport-space-selection",
    "ckm-bounded-interface-report",
)


def _env():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return env


def test_v27_cli_commands_work_offline():
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


def test_v27_report_renders_markdown():
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "ckm-bounded-interface-report", "--format", "markdown"],
        cwd=ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "# CKM Bounded Interface Normalization Audit" in result.stdout
    assert "OPEN_MISSING_CKM_TRANSPORT_SPACE_SELECTION" in result.stdout

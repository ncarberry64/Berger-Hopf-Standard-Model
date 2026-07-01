import json
import subprocess
import sys


COMMANDS = (
    "ckm-bidirectional-source-search",
    "ckm-bidirectional-channel-count",
    "ckm-adjoint-pair-selection",
    "ckm-channel-alternative-resolution",
    "ckm-bidirectional-log-transport-application",
    "ckm-bidirectional-channel-report",
)


def test_bidirectional_ckm_cli_commands_work_offline():
    for command in COMMANDS:
        result = subprocess.run(
            [sys.executable, "-m", "bhsm.interface", command, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert json.loads(result.stdout)


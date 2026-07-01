import json
import subprocess
import sys


COMMANDS = (
    "ckm-channel-source-search",
    "ckm-channel-count-audit",
    "ckm-maximal-sector-selection",
    "ckm-log-transport-application",
    "ckm-channel-equivalence-report",
)


def test_ckm_channel_equivalence_commands_work_offline():
    for command in COMMANDS:
        result = subprocess.run(
            [sys.executable, "-m", "bhsm.interface", command, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert json.loads(result.stdout)


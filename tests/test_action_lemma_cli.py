import json
import subprocess
import sys


COMMANDS = (
    "action-lemma-source-search",
    "primitive-lattice-rule",
    "maximal-overlap-bridge-rule",
    "log-transport-averaging",
    "ckm-log-transport-application",
    "action-lemma-closure-report",
)


def test_all_action_lemma_cli_commands_work_offline():
    for command in COMMANDS:
        result = subprocess.run([sys.executable, "-m", "bhsm.interface", command, "--format", "json"], capture_output=True, text=True, check=True)
        assert json.loads(result.stdout)


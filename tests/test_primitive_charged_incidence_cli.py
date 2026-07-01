import json
import subprocess
import sys


COMMANDS = (
    "primitive-charged-incidence",
    "rho-ch-gcd-selection",
    "overlap-4-over-3-source",
    "bridge-beta-identity",
    "ckm-log-transport-gate",
    "physical-normalization-gate",
    "external-reproduction-status",
)


def test_all_primitive_cli_commands_emit_json_offline():
    for command in COMMANDS:
        result = subprocess.run([sys.executable, "-m", "bhsm.interface", command, "--format", "json"], capture_output=True, text=True, check=True)
        assert json.loads(result.stdout)

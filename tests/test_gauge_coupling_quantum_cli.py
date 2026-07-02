import json

from bhsm.interface.cli import main


COMMANDS = (
    "gauge-coupling-quantum-search",
    "gauge-coupling-registry-pattern",
    "gauge-coupling-volume-denominator",
    "gauge-sector-weight-source",
    "universal-gauge-coupling-quantum",
    "gauge-coupling-action-attachment",
    "alpha-i-action-derivation",
    "g2-action-source-update",
    "ckm-value-source-update",
    "gauge-coupling-quantum-report",
)


def test_v31_cli_commands_work_offline(capsys):
    for command in COMMANDS:
        assert main([command, "--format", "json"]) == 0
        assert json.loads(capsys.readouterr().out)

import json

from bhsm.interface.cli import main


COMMANDS = (
    "weak-gauge-action-source-search",
    "weak-gauge-algebra-source",
    "normalized-weak-gauge-action-skeleton",
    "weak-gauge-trace-normalization",
    "g2-bh-action-source",
    "alpha2-bh-action-source",
    "normalized-weak-gauge-action-coefficient",
    "ckm-value-source-blocker",
    "weak-gauge-action-source-report",
)


def test_v3_cli_commands_emit_json(capsys):
    for command in COMMANDS:
        assert main([command, "--format", "json"]) == 0
        assert json.loads(capsys.readouterr().out)

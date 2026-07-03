import json
from bhsm.interface.berger_hodge_component_map import COMMAND_BUILDERS
from bhsm.interface.cli import main

def test_all_v4_4_commands_emit_json(capsys):
    for command in COMMAND_BUILDERS:
        assert main([command, "--format", "json"]) == 0
        assert isinstance(json.loads(capsys.readouterr().out), dict)

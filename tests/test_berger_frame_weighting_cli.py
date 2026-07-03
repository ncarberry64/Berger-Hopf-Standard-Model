import json
from bhsm.interface.berger_frame_weighting import COMMAND_BUILDERS
from bhsm.interface.cli import main

def test_all_v4_2_commands_work_offline(capsys):
    for command in COMMAND_BUILDERS:
        assert main([command, "--format", "json"]) == 0
        assert isinstance(json.loads(capsys.readouterr().out), dict)

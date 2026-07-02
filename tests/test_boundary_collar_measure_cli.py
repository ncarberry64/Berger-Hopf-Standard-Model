import json

from bhsm.interface.boundary_collar_measure import COMMAND_BUILDERS
from bhsm.interface.cli import main


def test_all_v4_1_commands_work_offline(capsys):
    for command in COMMAND_BUILDERS:
        assert main([command, "--format", "json"]) == 0
        assert isinstance(json.loads(capsys.readouterr().out), dict)

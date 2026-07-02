import json

from bhsm.interface.cli import main
from bhsm.interface.full_action_closure import COMMAND_BUILDERS


def test_every_v4_command_works_offline(capsys):
    for command in COMMAND_BUILDERS:
        assert main([command, "--format", "json"]) == 0
        assert isinstance(json.loads(capsys.readouterr().out), dict)

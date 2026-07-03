import json
from bhsm.interface.gauge_coframe_hodge import COMMAND_BUILDERS
from bhsm.interface.cli import main
def test_cli(capsys):
 for command in COMMAND_BUILDERS: assert main([command,"--format","json"])==0; assert isinstance(json.loads(capsys.readouterr().out),dict)

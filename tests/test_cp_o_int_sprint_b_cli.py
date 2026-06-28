import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable, "-m", "bhsm.interface", *args], cwd=ROOT, text=True, capture_output=True, check=True, timeout=60).stdout


def test_cp_o_int_cli_commands_work_offline_and_parse():
    report = json.loads(run("cp-o-int-report", "--format", "json"))
    stages = json.loads(run("cp-o-int-stages", "--format", "json"))
    gates = json.loads(run("cp-o-int-proof-gates", "--format", "json"))
    candidate = json.loads(run("cp-o-int-candidate", "--format", "json"))
    assert report["status_after"] == "OPEN_MISSING_INTERACTION_ATTACHMENT"
    assert len(stages["stages"]) == 9
    assert len(gates["proof_gates"]) == 21
    assert candidate["template"]["enabled"] is False
    assert "CP O_int Sprint B" in run("cp-o-int-report", "--format", "markdown")

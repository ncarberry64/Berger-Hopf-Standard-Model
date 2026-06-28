import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable, "-m", "bhsm.interface", *args], cwd=ROOT, text=True, capture_output=True, check=True, timeout=60).stdout


def test_sprint_c_cli_commands_work_offline():
    report = json.loads(run("cp-o-int-field-action", "--format", "json"))
    stages = json.loads(run("cp-o-int-field-action-stages", "--format", "json"))
    eligibility = json.loads(run("cp-o-int-production-eligibility", "--format", "json"))
    action = json.loads(run("cp-o-int-action-candidate", "--format", "json"))
    assert report["status_after"] == "OPEN_MISSING_ACTION_SOURCE"
    assert len(stages["stages"]) == 10
    assert eligibility["production_eligible"] is False
    assert eligibility["runtime_export_eligible"] is False
    assert action["candidate_status"] == "AVAILABLE_SYMBOLIC_CANDIDATE"
    assert "Field/Action Construction Sprint C" in run("cp-o-int-field-action", "--format", "markdown")

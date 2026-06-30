import json
import subprocess
import sys


def test_reviewer_invariant_cli_is_offline_and_machine_readable():
    result = subprocess.run([sys.executable, "-m", "bhsm.interface", "engine-invariants", "--format", "json"], capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)["status"] == "ENGINE_INVARIANTS_DETERMINISTIC_OFFLINE_PASS"


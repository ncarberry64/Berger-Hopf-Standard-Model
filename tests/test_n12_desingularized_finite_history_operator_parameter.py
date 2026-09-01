import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/derive_n12_desingularized_finite_history_operator_parameter.py"
)
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_DESINGULARIZED_FINITE_HISTORY_OPERATOR_PARAMETER.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("desingularized_parameter", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_desingularized_operator_parameter_validates() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    duration = payload["duration_parameter_jet"]
    assert duration["D_lambda_T_at_zero"] == 0.0
    assert duration["D_lambda2_T_at_zero_interval"][0] > 0.0
    assert duration["lambda_positive_member_selected"] is False
    assert payload["incoming_selected_line"]["branch"] == 23


def test_desingularized_operator_parameter_replays_identically() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    assert json.loads(first)["validation_passed"] is True

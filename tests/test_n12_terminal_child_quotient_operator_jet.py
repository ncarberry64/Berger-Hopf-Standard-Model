import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_terminal_child_quotient_operator_jet.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_TERMINAL_CHILD_QUOTIENT_OPERATOR_JET.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("terminal_quotient_jet", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_terminal_child_quotient_operator_jet_validates() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["dimensions"] == {
        "reset_tangent": 139,
        "child_projection": 73,
        "reset_lift_kernel": 66,
        "terminal_Cauchy_jet_rank": 2,
    }
    assert payload["total_Weyl_jet_chain_rule"][
        "fixed_duration_promoted_to_total_physical_derivative"
    ] is False


def test_terminal_child_quotient_operator_jet_replays_identically() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    assert json.loads(first)["validation_passed"] is True

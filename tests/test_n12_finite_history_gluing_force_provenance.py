import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_finite_history_gluing_force_provenance.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("gluing_force", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_finite_history_gluing_force_provenance_validates() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"][
        "fixing_C2_state_sets_D_M_C2_to_zero"
    ] is True
    assert payload["adjudication"][
        "fixing_C2_state_removes_M_C2_value_from_force"
    ] is False
    assert payload["claim_boundary"][
        "formation_only_heat_force_localization"
    ] == "INVALIDATED"


def test_finite_history_gluing_force_provenance_replays() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    assert json.loads(first)["validation_passed"] is True

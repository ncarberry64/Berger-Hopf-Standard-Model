import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_c2_birth_coefficient_quotient_jet.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("c2_birth_jet", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_c2_birth_coefficient_quotient_jet_validates() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["physical_forward_order"]["swapped"] == (
        "(E1,C2)=(C_*,E_*)"
    )
    assert payload["physical_forward_order"][
        "full_reset_map_recomputed_after_swap"
    ] is True
    assert payload["swapped_reset"]["rank"] == 57
    assert payload["swapped_reset"]["tangent_dimension"] == 139
    assert payload["swapped_reset"]["C2_projection_rank"] == 73
    assert payload["C2_birth_quotient_jet"]["rank"] == 2
    assert min(payload["C2_birth_quotient_jet"]["singular_values"]) > 0.5
    assert payload["C2_birth_coefficient"][
        "root_lapse_interval"
    ][0] > 0.0
    assert payload["C2_birth_coefficient"][
        "root_D_tau_log_R4_interval"
    ][0] > 0.0


def test_c2_birth_coefficient_quotient_jet_replays() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    assert json.loads(first)["validation_passed"] is True

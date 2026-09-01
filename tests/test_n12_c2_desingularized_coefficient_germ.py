import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_c2_desingularized_coefficient_germ.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_DESINGULARIZED_COEFFICIENT_GERM.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("c2_u_germ", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_c2_desingularized_coefficient_germ_validates() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    intervals = payload["certified_intervals"]
    assert intervals["D_t_u"][0] > 0.0
    assert intervals["D_tau_u"][0] > 0.0
    assert intervals["d_log_R4_du"][0] > 0.0
    assert intervals["D_t_u"] != intervals["D_tau_u"]
    consequence = payload["local_consequence"]
    assert consequence["one_sided_nonzero_outgoing_C2_segment_exists"] is True
    assert consequence["segment_length_selected_or_claimed"] is False
    assert consequence["validation_edge_promoted_to_physical_endpoint"] is False


def test_c2_desingularized_coefficient_germ_replays() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    assert json.loads(first)["validation_passed"] is True

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/derive_n12_finite_history_spectral_realization_provenance.py"
)
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_HISTORY_SPECTRAL_REALIZATION_PROVENANCE.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("spectral_provenance", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_finite_history_spectral_realization_provenance_validates() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["validated"]["chronology"].endswith("C2_CLOSED")
    assert payload["invalidated"][
        "free_two_boundary_M_C_is_the_positive_self_adjoint_heat_operator"
    ] is False
    assert payload["open"][
        "AE2_child_response_M_C2_and_first_two_covariant_jets"
    ] is True
    assert payload["claim_boundary"]["zero_source_force_value"] == "OPEN"


def test_finite_history_spectral_realization_provenance_replays() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    assert json.loads(first)["validation_passed"] is True

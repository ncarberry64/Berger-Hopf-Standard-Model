import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_forward_threshold_source_measure.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_THRESHOLD_SOURCE_MEASURE_AUDIT.json"
)


def test_threshold_source_measure_artifact_rebuilds_and_validates() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["continuous_threshold_regular_class_derived"] is False
    assert payload["adjudication"]["constant_scalar_radius_source_weight"] == "EXACTLY_ZERO"
    assert payload["adjudication"]["product_Dirac_exact_zero_atom_first_weight"] == "EXACTLY_ZERO"
    assert payload["adjudication"]["actual_N12_continuous_threshold_measure_exponent"] == "OPEN"
    assert payload["adjudication"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["adjudication"]["chord_03_authorized"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False

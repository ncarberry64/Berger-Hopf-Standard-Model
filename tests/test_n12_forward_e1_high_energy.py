import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_forward_e1_high_energy.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json"
)


def test_e1_high_energy_artifact_rebuilds_and_validates() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["compact_weak_E1_high_energy_integrability"] == "DERIVED"
    assert payload["adjudication"]["continuous_low_energy_source_measure_exponent"] == "OPEN"
    assert payload["adjudication"]["complete_internal_S3_angular_tail_enclosure"] == "OPEN"
    assert payload["claim_boundary"]["absolute_global_heat_trace_made_finite"] is False
    assert payload["adjudication"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False

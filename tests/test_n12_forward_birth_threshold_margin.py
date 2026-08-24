import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_forward_birth_threshold_margin.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_BIRTH_THRESHOLD_MARGIN_AUDIT.json"
)


def test_birth_threshold_margin_artifact_rebuilds_and_validates() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["core_positivity_plus_operator_nonnegativity_sufficient"] is False
    assert payload["adjudication"]["strict_physical_zero_energy_Wronskian_margin_available"] is False
    assert payload["provenance_adjudication"]["sector_resolved_nonzero_event_flux_and_W_phys_matrix"] == "NOT_ASSEMBLED"
    assert payload["claim_boundary"]["universal_matter_Wentzell_graph_inferred_from_gauge_W"] is False
    assert payload["adjudication"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False

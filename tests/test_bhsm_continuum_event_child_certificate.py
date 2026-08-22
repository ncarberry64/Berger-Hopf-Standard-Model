import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)


def test_continuum_event_child_certificate_closes_existing_gates():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
    assert payload["Q_XI_READOUT_UNLOCKED"] is True
    radius = payload["nonlinear_continuum_radius"]
    assert Decimal(radius["two_K_M2_D1_upper"]) < 1
    assert Decimal(radius["small_radii_root_upper"]) < Decimal(
        radius["existing_physical_neighborhood_radius_lower"]
    )
    assert payload["scientific_result"]["eta_admissible"] is True
    assert payload["scientific_result"]["positive_duration_persistence"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False

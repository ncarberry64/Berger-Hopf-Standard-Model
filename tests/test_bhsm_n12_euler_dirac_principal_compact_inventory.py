import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_EULER_DIRAC_PRINCIPAL_COMPACT_INVENTORY.json"
)


def test_complete_noncompact_inventory_prevents_a_false_compact_bound():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["spatial_principal_block"]["determinant"] == 8
    assert payload["velocity_L2_block"][
        "must_remain_in_principal_ED_operator"
    ] is True
    assert payload["derivative_velocity_mixed_block"][
        "must_remain_in_principal_ED_operator_before_gauge_reduction"
    ] is True
    assert payload["critical_regular_pole_block"]["counted_as_compact"] is False
    assert payload["C_ED_G_evaluable"] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False

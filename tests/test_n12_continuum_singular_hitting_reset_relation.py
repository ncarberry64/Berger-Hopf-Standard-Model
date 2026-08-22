import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
)


def test_continuum_singular_hitting_and_reset_relation_is_certified():
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    assert data["validation_passed"] is True
    assert Decimal(data["one_sided_hitting_theorem"]["continuum_abs_product_lower"]) > 0
    assert Decimal(data["one_sided_hitting_theorem"]["continuum_hard_gap_lower"]) > 0
    assert data["unchanged_jacobian_block_audit"]["fixed_event_child_rank"] == 31
    assert data["reset_correspondence"]["fixed_event_child_fiber_dimension"] == 67
    assert data["reset_correspondence"]["after_existing_whole_system_time_quotient"] == 66
    assert data["reset_correspondence"]["regular_local_continuum_correspondence_proved"] is True
    assert data["reset_correspondence"]["single_valued_physical_reset_map_proved"] is False
    assert data["claim_boundaries"]["current_complete_child_forward_return_proved"] is False
    assert data["FULL_BHSM_COMPLETE"] is False

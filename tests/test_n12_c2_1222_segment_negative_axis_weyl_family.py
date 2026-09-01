import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"


def test_1222_segment_negative_axis_family() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert len(payload["sampled_crosschecks"]) == 6
    assert all(
        Decimal(row["paired_product_Dirac_uniform_log_R4_remainder_decimal"]) != 0
        for row in payload["sampled_crosschecks"]
    )
    assert payload["matching_audit"]["C2_negative_axis_value_and_coefficient_cotangent"].startswith("VALID_MATCH")
    assert payload["claim_boundary"]["heat_minus_zeta_force"] == "OPEN"

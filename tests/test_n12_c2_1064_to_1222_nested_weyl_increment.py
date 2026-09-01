from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_1064_TO_1222_NESTED_WEYL_INCREMENT.json"


def test_nested_weyl_increment_certificate() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "C2_NESTED_CORE_SEMIGROUP_CERTIFIED_CURRENT_WEYL_NET_NOT_CONVERGED"
    )
    assert payload["core_split"]["added_segment_count"] == 158
    assert Decimal(payload["maximum_composition_absolute_residual_decimal"]) <= Decimal("1e-70")
    assert Decimal(
        payload["maximum_cotangent_semigroup_relative_residual_decimal"]
    ) <= Decimal("1e-25")
    assert payload["adjudication"]["physical_projected_heat_minus_zeta_force_tail"] == "OPEN"
    assert payload["hindsight"]["obstruction_physical"] is False
    for row in payload["sampled_crosschecks"]:
        for channel in row["channels"].values():
            zero = Decimal(channel["old_1064_zero_load_Weyl_decimal"])
            full = Decimal(channel["direct_1222_Dirichlet_Weyl_decimal"])
            old = Decimal(channel["old_1064_Dirichlet_Weyl_decimal"])
            assert zero < full < old
            assert Decimal(channel["composition_absolute_residual_decimal"]) <= Decimal("1e-70")
            assert Decimal(
                channel["cotangent_semigroup_maximum_relative_residual_decimal"]
            ) <= Decimal("1e-25")

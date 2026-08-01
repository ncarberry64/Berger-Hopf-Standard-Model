from __future__ import annotations

from bhsm.interface.envelopment.support_constraint_analysis_v10_4 import support_constraint_payload


def test_positive_z_scalar_supplies_one_conditional_physical_pair():
    payload = support_constraint_payload()
    assert payload["validation_passed"] is True
    assert payload["physical_scalar_count"] == 1
    assert payload["physical_scalar_count_status"] == "DERIVED_CONDITIONAL"
    assert payload["constraint_ledger"]["support_primary_constraint"] is None
    assert payload["reduced_kinetic_norm_positive"] == "CONDITIONAL_ON_Z_REDUCED>0"
    assert payload["canonical_depth"]["selected_map"] is None
    assert payload["independence"]["from_q_V"].startswith("q_V has zero")

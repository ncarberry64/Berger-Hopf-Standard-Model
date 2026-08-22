from __future__ import annotations

from bhsm.interface.n12_effective_inverse_localization import (
    effective_inverse_localization,
)


def test_effective_inverse_constant_is_correctly_localized() -> None:
    result = effective_inverse_localization()

    assert result["validation_passed"] is True
    rows = result["counterfamily"]["rows"]
    assert all(row["compact_rank"] == 1 for row in rows)
    assert all(row["normal_kernel_is_zero"] for row in rows)
    assert rows[-1]["normal_inverse_norm"] > 1.0e8
    assert result["BHSM_interpretation"][
        "qualitative_closed_range_invalidated"
    ] is False
    assert result["BHSM_interpretation"][
        "principal_high_tail_bound_4_over_beta_is_the_full_K"
    ] is False
    assert result["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert result["FULL_BHSM_COMPLETE"] is False

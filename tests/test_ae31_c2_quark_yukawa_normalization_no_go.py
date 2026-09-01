import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_quark_yukawa_normalization_no_go import (
    candidate_quark_yukawa_pair,
    claim_boundary,
    normalization_kernel_witness,
    normalization_nonidentifiability_theorem,
    provenance_and_exclusion_ledger,
)
from scripts.materialize_ae31_c2_quark_yukawa_normalization_no_go import (
    TARGET,
    build_payload,
    main,
)


def test_normalized_quark_shapes_have_exact_two_dimensional_normalization_kernel():
    theorem = normalization_nonidentifiability_theorem()
    jacobian = np.asarray(
        theorem[
            "normalized_shape_Jacobian_with_respect_to_log_c_u_log_c_d"
        ]
    )
    assert np.array_equal(jacobian, np.zeros((4, 2)))
    assert theorem["normalized_shape_Jacobian_rank"] == 0
    assert theorem["normalization_nullity"] == 2
    assert not theorem["all_current_within_sector_response_data_select_c_u_or_c_d"]
    assert not theorem["relative_normalization_fixed_by_current_response_shapes"]
    assert not theorem["absolute_normalizations_fixed_by_current_response_shapes"]


def test_distinct_normalizations_leave_shapes_fixed_but_change_cross_sector_scale():
    witness = normalization_kernel_witness()
    assert witness["up_shape_residual"] == 0.0
    assert witness["down_shape_residual"] == 0.0
    assert witness["cross_sector_ratio_changes"]
    assert witness["first_heavy_up_over_down"] == pytest.approx(1.0)
    assert witness["second_heavy_up_over_down"] == pytest.approx(56.0)
    assert witness["continuum_of_indistinguishable_normalizations"]


@pytest.mark.parametrize("c_up,c_down", [(0.2, 5.0), (1.0, 1.0), (9.0, 0.03)])
def test_candidate_pair_preserves_attached_response_ratios(c_up, c_down):
    baseline = candidate_quark_yukawa_pair(
        up_normalization=1.0, down_normalization=1.0
    )
    candidate = candidate_quark_yukawa_pair(
        up_normalization=c_up, down_normalization=c_down
    )
    assert candidate["up_ratios_to_heavy"] == pytest.approx(
        baseline["up_ratios_to_heavy"]
    )
    assert candidate["down_ratios_to_heavy"] == pytest.approx(
        baseline["down_ratios_to_heavy"]
    )
    assert not candidate["normalizations_action_selected"]
    assert not candidate["measured_quark_mass_used"]


def test_invalid_normalizations_fail_closed():
    with pytest.raises(ValueError):
        candidate_quark_yukawa_pair(up_normalization=0.0, down_normalization=1.0)
    with pytest.raises(ValueError):
        candidate_quark_yukawa_pair(up_normalization=1.0, down_normalization=-1.0)


def test_nearby_historical_objects_are_not_relabelled_as_yukawa_sources():
    ledger = provenance_and_exclusion_ledger()
    assert ledger["up_down_gauge_invariant_operator_classes_available"]
    assert ledger["up_down_frozen_family_response_operators_available"]
    assert not ledger["up_down_intrinsic_M4_source_variations_available"]
    assert not ledger["beta_kappa_can_be_relabelled_as_c_u_c_d"]
    assert not ledger["middle_up_virtual_dressing_promoted"]
    assert not ledger["EC_auxiliary_unit_vertex_supplies_global_quark_normalization"]
    assert not ledger["independent_quark_normalization_inserted"]
    assert not ledger["quark_mass_fit_used"]


def test_claim_boundary_names_exact_missing_parent_variation():
    boundary = claim_boundary()
    assert boundary[
        "CURRENT_AE31_QUARK_YUKAWA_NORMALIZATION_NONIDENTIFIABILITY_DERIVED"
    ]
    assert boundary["CURRENT_AE31_QUARK_NORMALIZATION_NULLITY"] == 2
    assert boundary["CURRENT_C2_QUARK_RESPONSE_SHAPES_REUSED"]
    assert not boundary["HISTORICAL_BETA_KAPPA_RELABELLED_AS_QUARK_YUKAWA"]
    assert not boundary["CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED"]
    assert not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
    assert not boundary["CKM_MATRIX_DERIVED"]
    assert "DELTA3S" in boundary["exact_next_operator"]


def test_materialized_normalization_no_go_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second

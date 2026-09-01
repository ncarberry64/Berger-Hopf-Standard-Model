import hashlib

import numpy as np
import pytest

from bhsm.interface.ae3_c2_hopf_semigroup_transport import (
    FROZEN_OVERLAP_WIDTH,
    action_transport_ledger,
    claim_boundary,
    current_c2_birth_overlap_operator,
    family_heat_semigroup,
    frozen_internal_semigroup_attachment,
    symmetric_slice_mass_test,
)
from scripts.materialize_ae3_c2_hopf_semigroup_transport import (
    TARGET,
    build_payload,
    main,
)


def test_current_c2_birth_semigroup_is_noncentral_in_all_charged_sectors():
    result = current_c2_birth_overlap_operator()
    assert result["current_round_geometry_used"]
    assert not result["historical_squashing_reused"]
    assert result["all_sector_shapes_noncentral"]
    assert result["all_frozen_role_orders_recovered"]
    assert result["sectors"]["charged_lepton"][
        "round_reset_dimensionless_generator_costs"
    ] == [0.0, 35.0, 99.0]
    assert result["sectors"]["up"][
        "round_reset_dimensionless_generator_costs"
    ] == [0.0, 48.0, 120.0]
    assert result["sectors"]["down"][
        "round_reset_dimensionless_generator_costs"
    ] == [0.0, 48.0, 80.0]


def test_semigroup_law_and_generator_are_exact_on_family_projectors():
    t1 = 0.31 * FROZEN_OVERLAP_WIDTH
    t2 = 0.69 * FROZEN_OVERLAP_WIDTH
    first = np.asarray(
        family_heat_semigroup(sector="charged_lepton", response_time=t1)[
            "semigroup_operator"
        ]
    )
    second = np.asarray(
        family_heat_semigroup(sector="charged_lepton", response_time=t2)[
            "semigroup_operator"
        ]
    )
    combined = np.asarray(
        family_heat_semigroup(
            sector="charged_lepton", response_time=t1 + t2
        )["semigroup_operator"]
    )
    assert np.allclose(first @ second, combined, atol=2.0e-16, rtol=2.0e-15)


def test_invalid_semigroup_inputs_fail_closed():
    with pytest.raises(ValueError):
        family_heat_semigroup(sector="neutral", response_time=FROZEN_OVERLAP_WIDTH)
    with pytest.raises(ValueError):
        family_heat_semigroup(sector="up", response_time=-1.0)


def test_first_failure_is_the_missing_current_action_coupling():
    result = action_transport_ledger()
    assert result["kinematic_transport_closed_through"] == (
        "UNCHANGED_FROZEN_INTERNAL_MASS_RATIO_OPERATOR_ON_CURRENT_C2_FIBER"
    )
    assert result["first_missing_variational_owner"] == (
        "CURRENT_AE3_INTRINSIC_M4_LR_HIGGS_COUPLING_WITH_T_C2"
    )
    assert not result["first_failure_is_only_a_numeric_scale"]
    assert result["successor_action_required_for_full_transport"]
    assert not result["y0_currently_derived"]


def test_frozen_internal_operator_attaches_without_replacing_its_squashing():
    result = frozen_internal_semigroup_attachment()
    assert not result[
        "current_C2_round_reset_sets_internal_Berger_shape_to_one"
    ]
    assert result["all_attachment_commutators_zero"]
    assert result["all_frozen_ratios_attached_unchanged"]
    assert np.allclose(
        result["sectors"]["charged_lepton"]["frozen_mass_ratio_screen"],
        [1.0, 0.06007447093260976, 0.00029729106456492414],
        atol=2.0e-16,
        rtol=2.0e-15,
    )
    assert np.allclose(
        result["sectors"]["up"]["frozen_mass_ratio_screen"],
        [1.0, 0.008310500554068288, 1.2690463017606151e-05],
        atol=2.0e-16,
        rtol=2.0e-15,
    )
    assert np.allclose(
        result["sectors"]["down"]["frozen_mass_ratio_screen"],
        [1.0, 0.021933971495439474, 0.0011165200546001757],
        atol=2.0e-16,
        rtol=2.0e-15,
    )


def test_zero_symmetric_slice_does_not_promote_a_mass_or_pole():
    result = symmetric_slice_mass_test()
    assert result["all_formal_mass_operators_zero"]
    assert result["response_shapes_remain_noncentral"]
    assert not result["zero_formal_mass_is_a_physical_pole_theorem"]


def test_claim_boundary_advances_shape_only():
    boundary = claim_boundary()
    assert boundary["current_C2_finite_family_Hopf_response_shape_derived"]
    assert boundary["charged_lepton_up_down_response_orderings_derived"]
    assert boundary["frozen_internal_Hopf_response_operator_attached_to_current_C2"]
    assert boundary["frozen_mass_ratio_screens_transported_unchanged"]
    assert not boundary["current_AE3_Yukawa_operator_derived"]
    assert not boundary["current_AE3_family_mass_hierarchy_derived"]
    assert not boundary["historical_dimensionful_numbers_promoted"]


def test_materialized_transport_theorem_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second

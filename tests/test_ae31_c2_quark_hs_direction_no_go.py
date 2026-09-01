import hashlib
import math

import pytest

from bhsm.interface.ae31_c2_quark_hs_direction_no_go import (
    claim_boundary,
    exact_channel_selector,
    family_tensor_pushforward_witness,
    historical_four_channel_trace_reuse,
    kinetic_normalization_nullity_theorem,
    normalized_quark_channel_direction,
)
from scripts.materialize_ae31_c2_quark_hs_direction_no_go import (
    TARGET,
    build_payload,
    main,
)


def test_positive_angle_parameterizes_normalized_kinetic_ellipse():
    for angle in (math.pi / 12.0, math.pi / 4.0, 5.0 * math.pi / 12.0):
        row = normalized_quark_channel_direction(
            angle=angle, up_kinetic=7.0, down_kinetic=13.0
        )
        assert row["kinetic_norm"] == pytest.approx(1.0, abs=2.0e-16)
        assert row["positive_direction"]
        assert not row["direction_action_selected"]


def test_invalid_channel_data_fail_closed():
    with pytest.raises(ValueError):
        normalized_quark_channel_direction(angle=0.0)
    with pytest.raises(ValueError):
        normalized_quark_channel_direction(angle=math.pi / 4.0, up_kinetic=0.0)


def test_kinetic_normalization_has_one_directional_nullity():
    theorem = kinetic_normalization_nullity_theorem()
    assert theorem["constraint_Jacobian_rank"] == 1
    assert theorem["channel_direction_nullity"] == 1
    assert theorem["gradient_dot_tangent"] == pytest.approx(0.0, abs=1.0e-15)
    assert theorem["witness_relative_residues_differ"]
    assert not theorem["kinetic_normalization_selects_relative_up_down_residue"]


def test_equal_historical_multiplicity_is_o2_degeneracy_not_equal_direction():
    trace = historical_four_channel_trace_reuse()
    assert trace["historical_pairing_multiplicity_matrix"] == "diag(9,9,3,3)"
    assert trace["quark_plane_quadratic_symmetry_when_no_other_terms_are_present"] == "O(2)"
    assert not trace["equal_multiplicity_selects_equal_components"]
    assert not trace["historical_numeric_Z_pair_promoted_to_current_C2"]


def test_family_tensor_pushforward_preserves_channel_angle_ambiguity():
    witness = family_tensor_pushforward_witness()
    assert witness["within_sector_shapes_identical"]
    assert witness["cross_sector_ratio_changes"]
    assert witness["all_attachment_commutators_zero"]
    assert not witness["family_tensoring_selects_channel_angle"]
    assert not witness["measured_quark_mass_used"]


def test_next_selector_is_full_channel_hessian_not_equal_component_assumption():
    selector = exact_channel_selector()
    assert selector["minimum_block"] == "[[H_uu,H_ud],[H_du,H_dd]]"
    assert not selector["diagonal_kinetic_trace_alone_sufficient"]
    assert not selector["equal_components_may_be_assumed"]
    assert not selector["quark_mass_fit_allowed"]


def test_claim_boundary_keeps_relative_residue_and_poles_open():
    boundary = claim_boundary()
    assert boundary["CURRENT_C2_QUARK_HS_KINETIC_NORMALIZATION_NULLITY_DERIVED"]
    assert boundary["CURRENT_C2_QUARK_HS_CHANNEL_DIRECTION_NULLITY"] == 1
    assert not boundary["CURRENT_C2_QUARK_CHANNEL_DIRECTION_SELECTED"]
    assert not boundary["CURRENT_C2_UP_DOWN_RELATIVE_YUKAWA_RESIDUE_DERIVED"]
    assert not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]


def test_materialized_hs_direction_no_go_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second

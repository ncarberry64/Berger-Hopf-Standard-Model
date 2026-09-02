import hashlib

import pytest

from bhsm.interface.ae4_current_c2_nonlinear_carrier_authority_adjudication import (
    claim_boundary,
    nonlinear_carrier_authority_contract,
)
from scripts.materialize_ae4_current_c2_nonlinear_carrier_authority_adjudication import (
    TARGET,
    build_payload,
    main,
)


def test_two_negative_transfer_results_do_not_promote_nonlinear_authority():
    result = nonlinear_carrier_authority_contract(
        affine_transfer_allowed=False,
        same_center_contraction_obstructed=True,
        field_descriptor_block_obstructed=True,
        green_image_partition_recovered=True,
        green_directional_seed_derived=True,
        green_directional_endpoints_derived=True,
        green_midpoint_componentwise_route_obstructed=True,
        green_correlated_scalar_interval355_finite=True,
        green_correlated_scalar_all_intervals_derived=True,
        green_correlated_scalar_causal_composition_derived=True,
        root_nonexistence_claim=False,
        physical_instability_claim=False,
        another_center_or_trajectory_authorized=False,
    )
    assert not result["current_affine_operator_jets_have_nonlinear_authority"]
    assert result["same_center_single_radius_contraction_obstructed"]
    assert result["same_center_field_descriptor_block_contraction_obstructed"]
    assert not result["root_nonexistence_inferred"]
    assert "MIXED_GREEN_TRANSVERSE" in result[
        "next_proof_object"
    ]


def test_upstream_physical_overclaims_fail_closed():
    with pytest.raises(ValueError):
        nonlinear_carrier_authority_contract(
            affine_transfer_allowed=False,
            same_center_contraction_obstructed=True,
            field_descriptor_block_obstructed=True,
            green_image_partition_recovered=True,
            green_directional_seed_derived=True,
            green_directional_endpoints_derived=True,
            green_midpoint_componentwise_route_obstructed=True,
            green_correlated_scalar_interval355_finite=True,
            green_correlated_scalar_all_intervals_derived=True,
            green_correlated_scalar_causal_composition_derived=True,
            root_nonexistence_claim=True,
            physical_instability_claim=False,
            another_center_or_trajectory_authorized=False,
        )


def test_claim_boundary_retires_scalar_route_without_restarting_campaign():
    boundary = claim_boundary()
    assert boundary["G7_SAME_CENTER_OUTWARD_74D_OPERANDS_ALREADY_EVALUATED"]
    assert boundary["G7_SINGLE_RADIUS_74D_CONTRACTION_ROUTE_OBSTRUCTED"]
    assert boundary["G7_FIELD_DESCRIPTOR_BLOCK_CONTRACTION_ROUTE_OBSTRUCTED"]
    assert not boundary["NEW_CENTER_OR_TRAJECTORY_AUTHORIZED"]
    assert not boundary[
        "AE4_AFFINE_GAUGE_AND_PARTICLE_JETS_NONLINEAR_AUTHORITY_DERIVED"
    ]


def test_materialized_adjudication_is_valid_and_deterministic():
    payload = build_payload()
    assert payload["validation_passed"]
    assert payload["recovered_same_center_operands"][
        "necessary_discriminant_upper"
    ] < 0.0
    assert payload["validation"]["scalar_route_not_left_as_open_next_calculation"]
    assert payload["validation"]["coarse_field_descriptor_route_not_left_open"]
    assert payload["validation"][
        "BHSM_native_green_longitudinal_correlation_is_reused"
    ]
    assert payload["validation"]["current_green_directional_seed_is_reused"]
    assert payload["validation"][
        "all_post_reset_green_directional_endpoints_are_reused"
    ]
    assert payload["recovered_green_directional_endpoints"][
        "maximum_upper_owner_node"
    ] == 370
    assert payload["validation"][
        "componentwise_green_midpoint_obstruction_is_reused"
    ]
    assert payload["validation"][
        "componentwise_green_midpoint_obstruction_persists_at_512_bit"
    ]
    assert payload["recovered_green_midpoint_obstruction"][
        "first_nonfinite_intrinsic_interval"
    ] == 355
    assert payload["validation"][
        "correlated_green_scalar_interval355_reconciliation_is_reused"
    ]
    assert payload["recovered_green_correlated_scalar_interval355"][
        "midpoint_intrinsic_curvature_upper"
    ] < 0.012207
    assert payload["validation"][
        "all_370_correlated_green_scalar_intervals_are_reused"
    ]
    assert payload["recovered_green_correlated_scalar_all_intervals"][
        "intervals_certified"
    ] == 370
    assert payload["validation"][
        "correlated_green_central_scalar_causal_composition_is_reused"
    ]
    assert payload["recovered_green_correlated_central_scalar_causal_composition"][
        "maximum_causal_curvature_norm_upper"
    ] < 8.406
    assert payload["validation"][
        "current_green_mixed_transverse_decisive_seed_is_integrated"
    ]
    assert payload["recovered_green_mixed_transverse_seed"]["nodes"] == [
        1, 355, 356, 370,
    ]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second

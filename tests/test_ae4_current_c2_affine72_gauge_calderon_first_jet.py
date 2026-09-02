import hashlib

import numpy as np

from bhsm.interface.ae4_current_c2_affine72_gauge_calderon_first_jet import (
    affine72_gauge_brst_first_jet,
    claim_boundary,
    scalar_friedrichs_weyl_first_jet,
)
from scripts.materialize_ae4_current_c2_affine72_gauge_calderon_first_jet import (
    TARGET,
    build_payload,
    main,
)


def test_scalar_weyl_first_jet_separates_radius_and_duration_parts():
    result = scalar_friedrichs_weyl_first_jet(
        log_radii=np.asarray((0.0, 0.01, 0.02)),
        normalized_proper_times=np.asarray((0.0, 0.4, 1.0)),
        proper_duration=0.2,
        log_radius_first_jet=np.asarray(((0.1, 0.0), (0.2, 0.1), (0.3, 0.2))),
        proper_duration_first_jet=np.asarray((0.01, -0.02)),
        unit_potential_coefficient=4.0,
    )
    assert result["parameter_count"] == 2
    assert result["segment_count"] == 2
    assert np.allclose(
        result["D_parameter_Weyl"],
        result["D_parameter_Weyl_radius_part"]
        + result["D_parameter_Weyl_duration_part"],
    )
    assert result["all_first_jet_values_finite"]
    assert not result["explicit_matrix_inverse_formed"]


def test_gauge_brst_first_jet_cancels_unphysical_pair():
    result = affine72_gauge_brst_first_jet(
        log_radii=np.asarray((0.0, 0.01, 0.02)),
        normalized_proper_times=np.asarray((0.0, 0.4, 1.0)),
        proper_duration=0.2,
        log_radius_first_jet=np.ones((3, 3)) * 0.01,
        proper_duration_first_jet=np.asarray((0.01, -0.02, 0.03)),
    )
    assert result["BRST_first_jet_cancellation_residual_norm"] == 0.0
    assert np.array_equal(
        result["surviving_gauge_BRST_first_jet"],
        result["coexact"]["D_parameter_Weyl"],
    )


def test_claim_boundary_keeps_nonlinear_authority_open():
    boundary = claim_boundary()
    assert boundary[
        "AE4_CURRENT_C2_AFFINE72_PROPER_TIME_GAUGE_CALDERON_FIRST_JET_EVALUATED"
    ]
    assert not boundary[
        "AE4_CURRENT_C2_NONLINEAR72_GAUGE_CALDERON_FIRST_JET_DERIVED"
    ]
    assert not boundary["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]


def test_materialized_affine72_gauge_first_jet_is_valid_and_deterministic():
    payload = build_payload()
    assert payload["validation_passed"]
    assert payload["proper_time_pullback"]["parameter_count"] == 72
    assert payload["scientific_result"]["BRST_first_jet_cancellation_residual"] == 0.0
    assert payload["validation"]["moving_duration_contribution_not_dropped"]
    assert payload["scientific_result"][
        "moving_duration_to_log_radius_norm_ratio"
    ] > 1.0e6
    assert not payload["carrier"]["nonlinear_exact_family_authority"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second

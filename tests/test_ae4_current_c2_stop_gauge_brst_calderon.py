import hashlib

import numpy as np
import pytest

from bhsm.interface.ae4_current_c2_stop_gauge_brst_calderon import (
    claim_boundary,
    stop_gauge_brst_calderon,
)
from scripts.materialize_ae4_current_c2_stop_gauge_brst_calderon import (
    TARGET,
    build_payload,
    main,
)


def test_stop_gauge_brst_block_uses_squared_curl_and_exact_quotient():
    result = stop_gauge_brst_calderon(
        log_radii=np.asarray((0.0, 0.01, 0.02)),
        proper_durations=np.asarray((0.1, 0.1)),
        spectral_parameter=-1.0,
        friedrichs_terminal_selected=True,
    )
    assert result["coexact_potential_coefficient"] == 4.0
    assert result["coexact_multiplicity"] == 3
    assert result["coexact_boundary_block"].shape == (3, 3)
    assert result["constraint_two_real_boundary_block"].shape == (2, 2)
    assert result["complex_ghost_graded_two_real_boundary_block"].shape == (2, 2)
    assert result["BRST_cancellation_residual_norm"] == 0.0
    assert result["total_gauge_BRST_supertrace_boundary_value"] == pytest.approx(
        result["coexact_supertrace_boundary_value"]
    )
    assert result["coexact_block_positive"]
    assert not result["Lorentzian_frequency_or_residue_inferred_from_resolvent_probe"]


def test_stop_gauge_block_requires_owned_friedrichs_domain():
    with pytest.raises(ValueError):
        stop_gauge_brst_calderon(
            log_radii=np.asarray((0.0, 0.01)),
            proper_durations=np.asarray((0.1,)),
            friedrichs_terminal_selected=False,
        )


def test_claim_boundary_advances_only_the_center_calderon_block():
    boundary = claim_boundary()
    assert boundary[
        "AE4_CURRENT_C2_CANONICAL_STOP_COEXACT_CALDERON_CENTER_EVALUATED"
    ]
    assert boundary["AE4_CURRENT_C2_CANONICAL_STOP_BRST_QUOTIENT_CENTER_EVALUATED"]
    assert not boundary[
        "AE4_CURRENT_C2_STOP_MATCHED_NONLINEAR_INTERVAL_GAUGE_BRST_BLOCK_DERIVED"
    ]
    assert not boundary["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]


def test_materialized_stop_gauge_brst_calderon_is_valid_and_deterministic():
    payload = build_payload()
    assert payload["validation_passed"]
    assert payload["scientific_result"][
        "BRST_constraint_ghost_pair_cancelled_on_same_Friedrichs_domain"
    ]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second

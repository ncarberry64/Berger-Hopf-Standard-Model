import hashlib

import numpy as np
import pytest

from bhsm.interface.ae4_current_c2_stop_matched_center_diagnostic import (
    refine_piecewise_linear_path,
)
from scripts.materialize_ae4_current_c2_stop_matched_center_diagnostic import (
    TARGET,
    build_payload,
    main,
)


def test_piecewise_linear_refinement_preserves_path_and_duration():
    x = np.asarray((0.0, 0.2, 0.5))
    tau = np.asarray((0.0, 0.3, 1.0))
    refined, durations = refine_piecewise_linear_path(x, tau, 4)
    assert refined.size == 9
    assert durations.size == 8
    assert refined[0] == 0.0
    assert refined[-1] == 0.5
    assert abs(np.sum(durations) - 1.0) < 1e-15
    with pytest.raises(ValueError):
        refine_piecewise_linear_path(x, tau, 0)


def test_stop_matched_center_diagnostic_is_stable_and_fail_closed():
    payload = build_payload()
    boundary = payload["claim_boundary"]
    plus = payload["scientific_result"]["midpoint_finest_chirality_plus"]
    minus = payload["scientific_result"]["midpoint_finest_chirality_minus"]
    assert payload["validation_passed"]
    assert 6700.0 < plus["Weyl_birth_value"] < 6800.0
    assert 6700.0 < minus["Weyl_birth_value"] < 6800.0
    assert abs(plus["D_H_Weyl_birth"] + 1.0) < 2e-4
    assert abs(minus["D_H_Weyl_birth"] + 1.0) < 2e-4
    assert 9e-5 < plus["D2_H_Weyl_birth"] < 1.1e-4
    assert boundary[
        "AE4_CURRENT_C2_STOP_MATCHED_CENTER_HS_CALDERON_DIAGNOSTIC_EVALUATED"
    ]
    assert not boundary[
        "AE4_CURRENT_C2_PHYSICAL_STOP_MATCHED_HS_CALDERON_BLOCK_DERIVED"
    ]
    assert not boundary["AE4_CURRENT_C2_STOP_MOVING_ENDPOINT_HS_JETS_DERIVED"]


def test_materialized_stop_matched_center_diagnostic_is_deterministic():
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second

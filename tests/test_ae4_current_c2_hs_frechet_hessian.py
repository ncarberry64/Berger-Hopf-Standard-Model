import hashlib

import numpy as np
import pytest

from bhsm.interface.ae4_current_c2_hs_frechet_hessian import (
    claim_boundary,
    finite_difference_coordinate_jet,
    generalized_e1_coordinate_jet,
    regulated_kernel_divided_difference,
)
from scripts.materialize_ae4_current_c2_hs_frechet_hessian import (
    TARGET,
    build_payload,
    main,
)


def _forms():
    stiffness = np.asarray(((2.4, -0.3), (-0.3, 1.8)))
    mass = np.asarray(((1.2, 0.1), (0.1, 0.9)))
    vertex = np.asarray(((0.4, -0.12), (-0.12, -0.25)))
    contact = np.asarray(((0.3, 0.04), (0.04, 0.22)))
    return stiffness, mass, vertex, contact


def test_divided_difference_is_symmetric_and_strictly_negative():
    divided = regulated_kernel_divided_difference(np.asarray((0.8, 1.7, 3.2)))
    assert np.allclose(divided, divided.T)
    assert np.all(divided < 0.0)


def test_exact_frechet_jet_matches_owner_finite_difference():
    K, M, V, Q = _forms()
    exact = generalized_e1_coordinate_jet(
        stiffness=K, mass=M, vertex=V, contact=Q
    )
    finite = finite_difference_coordinate_jet(
        stiffness=K, mass=M, vertex=V, contact=Q, step=1.0e-4
    )
    assert abs(exact["HS_source"] - finite["centered_first_derivative"]) < 2e-9
    assert abs(exact["HS_curvature"] - finite["centered_second_derivative"]) < 2e-7
    assert exact["generalized_eigenbasis_M_orthonormality_residual"] < 2e-15


def test_nonpositive_generalized_operator_fails_closed():
    K, M, V, Q = _forms()
    with pytest.raises(ValueError):
        generalized_e1_coordinate_jet(
            stiffness=-K, mass=M, vertex=V, contact=Q
        )


def test_current_c2_full_form_core_payload_is_fail_closed():
    payload = build_payload()
    boundary = payload["claim_boundary"]
    assert payload["validation_passed"]
    assert len(payload["channels"]) == 2
    assert all(row["dimension"] == 128 for row in payload["channels"].values())
    assert boundary[
        "AE4_CURRENT_C2_BIRTH_LOCAL_GALERKIN_HS_FRECHET_HESSIAN_EVALUATED"
    ]
    assert boundary[
        "AE4_CURRENT_C2_BIRTH_LOCAL_CONDITIONED_HS_CURVATURE_POSITIVE"
    ]
    assert boundary["AE4_CURRENT_C2_BIRTH_LOCAL_CHIRAL_HS_JETS_EQUAL"]
    assert not boundary["AE4_PHYSICAL_ELL_STAR_NUMERICALLY_EVALUATED"]
    assert not boundary["AE4_MAXIMAL_HISTORY_HS_CALDERON_BLOCK_EVALUATED"]
    assert not boundary["AE4_BROKEN_LR_HS_SADDLE_DERIVED"]


def test_materialized_hessian_is_deterministic():
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second

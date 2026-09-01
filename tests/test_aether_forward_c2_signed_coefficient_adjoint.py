import numpy as np

from bhsm.interface.aether_forward_c2_signed_coefficient_adjoint import (
    signed_coefficient_history_adjoint,
)


def test_signed_reverse_pullback_matches_forward_jacobi_pairing() -> None:
    rng = np.random.default_rng(7122201)
    segments = 11
    state_dimension = 7
    parameter_dimension = 4
    transitions = np.asarray([
        np.eye(state_dimension) + 0.03 * rng.normal(
            size=(state_dimension, state_dimension)
        )
        for _ in range(segments)
    ])
    x_covectors = rng.normal(size=(segments + 1, state_dimension))
    h_covectors = rng.normal(size=(segments, state_dimension))
    d_x = rng.normal(size=segments + 1)
    d_h = rng.normal(size=segments)
    terminal = rng.normal(size=state_dimension)
    seed_jet = rng.normal(size=(state_dimension, parameter_dimension))

    result = signed_coefficient_history_adjoint(
        transition_jacobians_action=transitions,
        node_log_radius_covectors_action_dual=x_covectors,
        segment_duration_covectors_action_dual=h_covectors,
        D_log_radius_functional=d_x,
        D_proper_duration_functional=d_h,
        terminal_state_covector_action_dual=terminal,
    )
    jacobi = seed_jet.copy()
    forward = d_x[0] * (x_covectors[0] @ jacobi)
    forward += d_h[0] * (h_covectors[0] @ jacobi)
    for index in range(segments):
        jacobi = transitions[index] @ jacobi
        forward += d_x[index + 1] * (x_covectors[index + 1] @ jacobi)
        if index + 1 < segments:
            forward += d_h[index + 1] * (h_covectors[index + 1] @ jacobi)
    forward += terminal @ jacobi
    reverse = result["initial_state_covector_action_dual"] @ seed_jet
    assert np.linalg.norm(forward - reverse) < 2.0e-12
    assert result["explicit_matrix_inverse_formed"] is False
    assert result["forward_Jacobi_columns_formed"] is False


def test_signed_adjoint_rejects_incompatible_shapes() -> None:
    with np.testing.assert_raises(ValueError):
        signed_coefficient_history_adjoint(
            transition_jacobians_action=np.zeros((2, 3, 3)),
            node_log_radius_covectors_action_dual=np.zeros((2, 3)),
            segment_duration_covectors_action_dual=np.zeros((2, 3)),
            D_log_radius_functional=np.zeros(3),
            D_proper_duration_functional=np.zeros(2),
        )

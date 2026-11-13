"""Original D5 response/Green source contacts and unassigned event glue."""
import numpy as np
import pytest

from bhsm.interface.muon_d5_complement_event_return import (
    consume_original_d5_bulk_weak_jacobi, original_d5_green_return,
    consume_event_trace_operand, exact_lagrange_time_pairing,
    original_time_fibre_radial_operator, radial_analytic_left_from_inverse,
)


def test_actual_six_node_mass_retains_time_boundary_and_product_aliasing():
    nodes, _ = np.polynomial.legendre.leggauss(4)
    t = np.r_[-1., nodes, 1.]
    bary = np.array([1/np.prod(t[i]-np.delete(t, i)) for i in range(6)])
    D = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            if i != j:
                D[i, j] = bary[j]/(bary[i]*(t[i]-t[j]))
        D[i, i] = -np.sum(D[i])
    pair = exact_lagrange_time_pairing(t, D)
    assert np.min(np.linalg.eigvalsh(pair['temporal_pairing'])) > .04
    assert np.max(abs(pair['exact_polynomial_SBP_rows'])) < 5e-14
    T = (1+.2*t**2)[None, :, None, None]
    a = original_time_fibre_radial_operator(T, np.ones_like(T), T*.1j,
        time_principal_first=T*.3, radial_principal_first=T*.03,
        body_first=T*.2, time_derivative=D, time_derivative_first=D*0,
        density=np.ones((1, 6)), density_first=np.full((1, 6), .07),
        temporal_pairing=pair['temporal_pairing'],
        temporal_pairing_first=np.zeros((6, 6)))
    assert np.max(abs(a['temporal_discrete_Green_assembly_rows'])) < 1e-13
    assert np.max(abs(a['temporal_discrete_Green_assembly_source_rows'])) < 1e-13
    assert np.linalg.norm(a['variable_coefficient_time_product_aliasing']) > 1.
    assert np.max(abs(a['weak_density'][0]-pair['temporal_pairing'])) < 1e-14


def test_literal_radial_dual_uses_actual_original_current_and_its_source():
    inverse = np.array([[[1, .2j], [.3, .8]], [[.7j, .1], [.2, 1.1]]])
    inversej = inverse * .13
    R = np.repeat(np.array([[1+.1j, .2], [0, .9]])[None], 2, axis=0)
    W = np.repeat(np.array([[.7, .1j], [.03, 1.2]])[None], 2, axis=0)
    a = radial_analytic_left_from_inverse(inverse, inversej, R, R*.2,
                                         W, W*.1j)
    assert np.max(abs(a['original_current_recovery_rows'])) < 1e-14
    assert np.max(abs(a['original_current_source_recovery_rows'])) < 1e-14
    F = np.linalg.inv(inverse)
    Fj = -F @ inversej @ F
    g = original_d5_green_return(R, F, radial_principal_first=R*.2,
        value_first=Fj, independent_left=a['independent_left'],
        independent_left_first=a['independent_left_first'], weak_density=W,
        weak_density_first=W*.1j, orientation=1)
    assert np.max(abs(g['signed_original_Green_return']-np.eye(2))) < 1e-14
    assert np.max(abs(g['signed_original_Green_return_first'])) < 1e-14
    assert a['physical_outer_annihilator_selected'] is False


def test_nonnull_bulk_response_cancels_original_field_vertex_without_conjugation():
    # An exact nonsymmetric complex first-order solution and source tangent.
    q, d, n = 3, 2, 2
    Q = np.repeat(np.array([[.2j, .7], [-.1, .3]])[None], q, axis=0)
    Qj = np.repeat(np.array([[.1, -.2j], [.4j, -.3]])[None], q, axis=0)
    V = np.array([[[1+.1j, .2], [.3j, 1]], [[.7, .1j], [.2, 1.2]],
                  [[1.1, .4], [.1j, .8]]])
    Vj = V * (.13 + .2j)
    R = np.repeat(np.eye(d, dtype=complex)[None], q, axis=0)
    Rj = R * .07
    Vr = -Q @ V
    Vrj = -Qj @ V - Q @ Vj - Rj @ Vr
    L = np.repeat(np.array([[1, .3j], [.2, .7]])[None], q, axis=0)
    W = np.repeat(np.array([[1.2, .1j], [0, .9]])[None], q, axis=0)
    a = consume_original_d5_bulk_weak_jacobi(R, Q, V, Vr,
        radial_principal_first=Rj, zero_time_operator_first=Qj,
        value_first=Vj, radial_derivative_first=Vrj,
        independent_left=L, independent_left_first=L*.2j,
        weak_density=W, weak_density_first=W*.1,
        coordinate_weights=np.array([.2, .3, .5]),
        coordinate_weights_first=np.array([.01, -.02, .01]))
    assert np.max(abs(a['original_full_D5_rows'])) < 1e-14
    assert np.max(abs(a['original_full_D5_source_rows'])) < 1e-14
    assert np.linalg.norm(a['ordered_direct_field_vertex']) > .1
    assert np.linalg.norm(a['ordered_bulk_state_response']) > .1
    assert np.max(abs(a['complete_ordered_weak_source'])) < 1e-14
    assert a['analytic_left_or_source_conjugated'] is False
    assert a['physical_state_contraction_or_formation_load_selected'] is False


def test_original_green_return_retains_every_independent_contact():
    R = np.array([[[1+.2j, .3], [0, .8j]]])
    V = np.array([[[1j], [.3]]])
    L = np.array([[[.2, 1+.1j]]])
    W = np.array([[[1.1, .2j], [0, .8]]])
    Rj, Vj, Lj, Wj = R*.13j, V*.7, L*.11, W*-.2j
    def call(z):
        return original_d5_green_return(R+z*Rj, V+z*Vj,
            radial_principal_first=Rj, value_first=Vj,
            independent_left=L+z*Lj, independent_left_first=Lj,
            weak_density=W+z*Wj, weak_density_first=Wj, orientation=-1)
    a = call(0)
    h = 2e-6
    finite = (call(h)['signed_original_Green_return']-
              call(-h)['signed_original_Green_return'])/(2*h)
    assert np.max(abs(finite-a['signed_original_Green_return_first'])) < 2e-10
    assert np.linalg.norm(a['Green_field_response_contact']) > .1
    assert a['native_temporal_conormal_substituted'] is False
    assert a['physical_outer_equation_satisfied'] is None


def test_bulk_event_operand_does_not_select_reset_or_erase_homogeneous_columns():
    V = np.arange(3*12*5).reshape(3, 12, 5)*(1+.1j)
    a = consume_event_trace_operand(V, V*.3j,
        coordinate_times=[-1., -.4, 0.], event_time_index=2,
        fibre_width=4, branch_identity='incoming_eta_plus_particle')
    expected = V[:, 8:12]
    assert np.array_equal(a['event_incoming_bulk_trace_operand'], expected)
    assert np.array_equal(a['event_row_coefficient_of_reset_lift'], -expected)
    assert np.array_equal(a['event_Jacobi_coefficient_of_reset_lift_first'], -expected)
    assert a['event_incoming_bulk_trace_operand'].shape[-1] == 5
    assert a['held_event_residual'] is None
    assert a['reset_lift_assigned'] is False
    assert a['child_trace_assigned'] is False


def test_missing_source_or_false_chart_fails_closed():
    with pytest.raises(ValueError):
        consume_event_trace_operand(np.ones((2, 11, 3)), np.ones((2, 11, 3)),
            coordinate_times=[-1., -.4, 0.], event_time_index=2,
            fibre_width=4, branch_identity='incoming')
    with pytest.raises(ValueError):
        original_d5_green_return(np.ones((1, 1, 1)), np.ones((1, 1, 1)),
            radial_principal_first=None, value_first=np.ones((1, 1, 1)),
            independent_left=np.ones((1, 1, 1)),
            independent_left_first=np.ones((1, 1, 1)),
            weak_density=np.ones((1, 1, 1)),
            weak_density_first=np.ones((1, 1, 1)), orientation=1)

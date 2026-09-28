from pathlib import Path
import sys
import mpmath as mp
import pytest
from flint import arb, arb_mat, ctx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from bhsm.interface.gate7_current_action import (
    ActionBase, ActionSector, ConstraintSector, ImplicitAction,
    evaluate_gate7_current_action,
)
from bhsm.interface.formation_amplitude import orbit_cut_endpoint, dirichlet_birth_heat_pressure
from bhsm.interface.temporal_action_residual import temporal_source


def constrained_query(shift=0):
    # Synthetic nonlinear implicit model, not BHSM data:
    # F=n-A^2-A*x; Gamma=n^2/2+x*n+A*x; R=n-A*x-4.
    # At A=2,x=3,n=10, mu=-5. R=0 but its moving derivative is not zero.
    base = ActionBase('s', 'c', 't', 'n', 'w', 'r')
    action = ActionSector('Gamma', base, arb_mat([[12-2*shift]]),
                          arb_mat([[13+shift]]), gamma_amplitude=arb_mat([[3-3*shift]]))
    constraint = ConstraintSector('R', 'explicit synthetic constraint', base,
        arb_mat([[-5-shift]]), arb_mat([[0]]), arb_mat([[-2]]), arb_mat([[1]]), arb_mat([[-3]]))
    return ImplicitAction(base, arb_mat([[1]]), arb_mat([[-2]]),
        lambda v: arb_mat(1, 1), (action,), ('Gamma',), 'synthetic', {},
        constraints=(constraint,), F_amplitude=arb_mat([[-7]]), amplitude_owner='synthetic A',
        required_constraints=('R',))


def test_amplitude_and_force_use_same_full_kkt_adjoint():
    q = constrained_query()
    result = evaluate_gate7_current_action(q, {'q66': True, 'amplitude': True})
    a = result['amplitude']
    assert result['adjoint'] == arb_mat([[8]])
    assert result['q66'] == arb_mat([[38]])
    assert a['raw_partial'] == arb_mat([[3]])
    assert a['explicit_constraint_multiplier'] == arb_mat([[15]])
    assert a['internal_adjoint'] == arb_mat([[56]])
    assert a['final_row'] == arb_mat([[74]])
    # Direct differentiation after n=A^2+A*x gives 94-20=74.
    with mp.workdps(70):
        def lagrangian(A, x):
            n = A*A+A*x
            return n*n/2+x*n+A*x-5*(n-A*x-4)
        assert a['final_row'][0, 0].contains(arb(str(mp.diff(lambda A: lagrangian(A, 3), 2))))
    assert a['final_row'] != a['raw_partial']


def test_constraint_gauge_shift_preserves_amplitude_and_physical_force():
    # Gamma -> Gamma+17R, mu -> mu-17 must leave all rows unchanged.
    a = evaluate_gate7_current_action(constrained_query(), {'q66': True, 'amplitude': True})
    b = evaluate_gate7_current_action(constrained_query(17), {'q66': True, 'amplitude': True})
    assert a['amplitude']['final_row'] == b['amplitude']['final_row']
    assert a['adjoint'] == b['adjoint']
    assert a['q66'] == b['q66']


def test_missing_amplitude_forcing_or_partial_is_not_zero():
    q = constrained_query(); q.F_amplitude = None
    with pytest.raises(ValueError, match='F_amplitude'):
        evaluate_gate7_current_action(q, {'amplitude': True})
    q = constrained_query(); q.constraints[0].R_amplitude = None
    with pytest.raises(ValueError, match='R_amplitude'):
        evaluate_gate7_current_action(q, {'amplitude': True})
    q = constrained_query(); q.sectors[0].gamma_amplitude = None
    with pytest.raises(ValueError, match='Gamma_amplitude'):
        evaluate_gate7_current_action(q, {'amplitude': True})


def test_constraint_curvature_is_retained_in_same_action_product():
    # F=n-x^2; Gamma=0; R=n*x; mu=3, so L_red=3*x^3.
    base = ActionBase('s', 'c', 't', 'n', 'w', 'r')
    zero = lambda kind, u, dn: (arb_mat(1, 1), arb_mat(1, 1))
    sector = ActionSector('zero_objective', base, arb_mat(1, 1), arb_mat(1, 1), zero)
    c = ConstraintSector('R', 'synthetic', base, arb_mat([[3]]), arb_mat([[8]]),
        arb_mat([[4]]), arb_mat([[2]]), curvature_product=lambda kind, u, dn, mu:
        (dn*mu[0, 0], u*mu[0, 0]))
    query = ImplicitAction(base, arb_mat([[1]]), arb_mat([[-4]]), lambda v: arb_mat(1, 1),
        (sector,), (sector.name,), 'synthetic curvature', {},
        residual_curvature_product=lambda kind, u, dn, eta: (-2*u*eta[0, 0], arb_mat(1, 1)),
        constraints=(c,), required_constraints=('R',))
    result = evaluate_gate7_current_action(query, {'q66': True, 'H66_u': arb_mat([[1]])})
    assert result['q66'] == arb_mat([[36]])
    assert result['H66_u'] == arb_mat([[36]])
    query.constraints = ()
    with pytest.raises(ValueError, match='omitted'):
        evaluate_gate7_current_action(query, {'q66': True})


def test_orbit_cut_retains_clock_and_cancels_nonzero_temporal_residual():
    # Nonzero Euler and multiplier residuals; cancellation is kinematic.
    ctx.prec = 256
    source = temporal_source(qdim=1, euler_residual=arb_mat([[7], [11]]),
        deuler_residual=arb_mat(2, 1), multiplier_gradient=arb_mat([[13]]),
        multiplier_gradient_first=arb_mat(1, 1), velocity=arb_mat([[3]]),
        velocity_first=arb_mat(1, 1), multiplier_arc_rate=arb_mat([[5]]),
        multiplier_arc_first=arb_mat(1, 1), clock=arb(2), clock_first=arb_mat(1, 1))
    r = orbit_cut_endpoint(density=17, momentum=arb_mat([[19]]), velocity=arb_mat([[3]]),
        state_amplitude=arb_mat([[6], [23], [5]]), coordinate_time_amplitude=2,
        state_source=source['state'], time_source=source['time'][0, 0])
    assert r['endpoint'] == -34
    assert r['configuration'] == -114
    assert r['clock'] == 80
    for key in ('kinematic_replay', 'endpoint_replay', 'temporal_tangential_replay'):
        assert all(v.contains(0) for v in r[key].entries())


def test_heat_birth_pressure_matches_moving_interval_action():
    # Exact first 12 continuum Dirichlet modes on [0,T], constant potential.
    # This tests the shape identity, not a complete graded BHSM realization.
    ctx.prec = 320
    T, V, ell = arb('1.3'), arb('.7'), arb('.4')
    values = [(arb.pi()*k/T)**2+V for k in range(1, 13)]
    norms = [2*(arb.pi()*k)**2/T**3 for k in range(1, 13)]
    result = dirichlet_birth_heat_pressure(eigenvalues=values, squared_conormals=norms,
        signed_weights=[1]*12, heat_length=ell, tail=arb(0))
    with mp.workdps(110):
        def gamma(t):
            return -sum(mp.e1(mp.mpf('.4')**2*((mp.pi*k/t)**2+mp.mpf('.7')))
                        for k in range(1, 13))/2
        truth = arb(mp.nstr(mp.diff(gamma, mp.mpf('1.3')), 95))
        assert result.overlaps(truth)
    with pytest.raises(ValueError, match='tail'):
        dirichlet_birth_heat_pressure(eigenvalues=values, squared_conormals=norms,
            signed_weights=[1]*12, heat_length=ell, tail=None)

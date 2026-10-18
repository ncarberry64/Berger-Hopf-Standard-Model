"""Unadopted incoming-boundary selector: a finite original-action control.

This tests a stationary-past polarization transported through a changing
homogeneous background. It does not realize the adopted Gaussian beams or
solve their constrained background. All zero fields below are declared
manufactured-control inputs, never values assigned to unknown physical fields.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from .muon_native_dirac_hamiltonian import (
    canonical_lepton_hamiltonian_maps, lepton_current_hilbert_representation,
)
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection


def gapped_sign_subspaces(hamiltonian, *, gap_guard=1e-12):
    """Apply an explicitly proposed spectral boundary rule on a finite carrier.

    This rule requires adjudication for physical use. The input is already in
    a fixed action-isometric chart. Zero modes are rejected, not assigned.
    """
    h = np.asarray(hamiltonian, complex)
    if h.ndim != 2 or h.shape[0] != h.shape[1] or not np.isfinite(h).all():
        raise ValueError('finite square fixed-pairing Hamiltonian required')
    if not np.isfinite(gap_guard) or gap_guard <= 0:
        raise ValueError('positive gap guard required')
    if np.linalg.norm(h-h.conj().T, 2) > 1e-12*max(1., np.linalg.norm(h, 2)):
        raise ValueError('self-adjoint fixed-pairing Hamiltonian required')
    values, vectors = np.linalg.eigh(h)
    if np.min(abs(values)) <= gap_guard:
        raise ValueError('zero/gap-closing modes require a separate selection rule')
    plus, minus = vectors[:, values > 0], vectors[:, values < 0]
    return dict(positive=plus, negative=minus, eigenvalues=values,
                projector=plus@plus.conj().T, physical_rule_adopted=False)


def flat_step(t):
    """C-infinity ramp, stationary outside [0,1], and its exact derivative."""
    t = float(t)
    if t <= 0:
        return 0., 0.
    if t >= 1:
        return 1., 0.
    a, b = np.exp(-1/t), np.exp(-1/(1-t))
    value = a/(a+b)
    return value, value*(1-value)*(t**-2+(1-t)**-2)


def original_action_trial():
    """Exact invariant constant-angular electron carrier of a declared trial.

    R4=N=1, Omega=0, H=(0,m/Y_e), m=.75+.75*S(t). Y_e is unchanged.
    This choice gives a readable nonadiabatic control; it is not calibrated
    physical input. Constant-angular sections cannot realize separated beams.
    """
    rep = lepton_current_hilbert_representation()
    y_e = float(rep['family_Y'][2, 2].real)
    injection = charged_dirac_injection(np.array([0., 1.]), family=2)['charged']

    def full(t):
        s, _ = flat_step(t)
        return canonical_lepton_hamiltonian_maps(
            value_map=np.eye(18)[None],
            spatial_derivative_map=np.zeros((1, 3, 18, 18)),
            H=np.array([[0., (.75+.75*s)/y_e]]), R4=1.,
            gauge_connection=np.zeros((1, 4, 18, 18)))['hamiltonian_map'][0]

    h0, h1 = (injection.conj().T@full(t)@injection for t in (0., 1.))

    def reduced(t):
        return h0+flat_step(t)[0]*(h1-h0)

    return dict(injection=injection, full=full, reduced=reduced,
                electron_yukawa=y_e, radius=1., Haar_volume=2*np.pi**2)


def execute_boundary_transport_control():
    """Execute the candidate boundary rule and independent Dirac checks.

    The past is exactly stationary on this manufactured path. Its Moller
    projector cutoff error is therefore zero for every starting time <=0.
    This does not assert a stationary past or a Hadamard completion for BHSM.
    """
    trial = original_action_trial()
    h, full, j = trial['reduced'], trial['full'], trial['injection']
    seed = gapped_sign_subspaces(h(0.))
    frame0 = np.column_stack((seed['positive'], seed['negative']))
    solution = solve_ivp(lambda t, u: (-1j*h(t)@u.reshape(4, 4)).ravel(),
                         (0., 1.), np.eye(4, dtype=complex).ravel(),
                         method='DOP853', rtol=3e-14, atol=3e-16, dense_output=True)
    if not solution.success:
        raise ArithmeticError(solution.message)
    evolution = lambda t: solution.sol(t).reshape(4, 4)
    frame = lambda t: j@evolution(t)@frame0/np.sqrt(trial['Haar_volume'])
    projector = lambda t: evolution(t)@seed['projector']@evolution(t).conj().T
    times = np.linspace(.1, .9, 9)
    epsilon = 1e-4

    def difference(function, t):
        return (function(t-2*epsilon)-8*function(t-epsilon)
                +8*function(t+epsilon)-function(t+2*epsilon))/(12*epsilon)

    dirac, dirac_point, transport, leakage, unitarity = [], [], [], [], []
    for t in times:
        f, p, ht = frame(t), projector(t), h(t)
        # Independent five-point derivative, not a reuse of the ODE RHS.
        point_error = np.linalg.norm(1j*difference(frame, t)-full(t)@f, 2)
        dirac_point.append(point_error)
        dirac.append(np.sqrt(trial['Haar_volume'])*point_error)
        transport.append(np.linalg.norm(1j*difference(projector, t)-(ht@p-p@ht), 2))
        leakage.append(np.linalg.norm(full(t)@j-j@ht, 2))
        u = evolution(t)
        unitarity.append(np.linalg.norm(u.conj().T@u-np.eye(4), 2))
    mid = .5
    instant = gapped_sign_subspaces(h(mid))
    instant_numeric_defect = np.linalg.norm(
        1j*difference(lambda t: gapped_sign_subspaces(h(t))['projector'], mid), 2)
    u = evolution(1.)
    cutoff = []
    for duration in (1., 2.):
        omega = u@expm(-1j*h(0.)*duration)@expm(1j*h(0.)*duration)
        cutoff.append(omega@seed['projector']@omega.conj().T)
    sections = frame(mid)
    instantaneous_sections = j@np.column_stack((instant['positive'], instant['negative']))/np.sqrt(trial['Haar_volume'])
    result = dict(
        classification='UNADOPTED_STATIONARY_PAST_SELECTOR__FINITE_ORIGINAL_ACTION_CONTROL',
        physical_incoming_realization=False, physical_guard=2e-10,
        trial=dict(R4=1., N=1., Omega='all zero by manufactured-control definition only',
                   H='(0,(0.75+0.75*S(t))/Y_e)', family=2,
                   electron_yukawa=trial['electron_yukawa'],
                   carrier='constant-angular full18 charged electron invariant image; 4 coefficients',
                   Haar_volume=trial['Haar_volume'],
                   asymptotic_past='exactly stationary for t<=0 on this trial only',
                   seed_eigenvalues=seed['eigenvalues'].tolist()),
        equations_executed=dict(
            selector='P_plus(0)=1_(0,infinity)(H_trial(0)) on the declared charged invariant carrier',
            transport='i*d_t U=H_trial(t)*U, U(0)=I; P_D=U*P_plus(0)*U_dagger',
            independent_Dirac='i*five_point_d_t F-H_full18(t)*F',
            instantaneous_defect='||i*d_t P_inst-[H,P_inst]||=|a*m_dot-m*a_dot|/(2*(a^2+m^2))'),
        residuals=dict(
            original_full18_Dirac_Cauchy_five_point_max=float(max(dirac)),
            original_full18_Dirac_pointwise_five_point_max=float(max(dirac_point)),
            projector_transport_five_point_max=float(max(transport)),
            full18_invariant_carrier_leakage_max=float(max(leakage)),
            unitary_evolution_max=float(max(unitarity)),
            finite_stationary_past_cutoff_projector_difference=float(np.linalg.norm(cutoff[0]-cutoff[1], 2)),
            past_Cook_tail_bound=0.,
            instantaneous_projector_transport_defect_midpoint=instant_numeric_defect,
            analytic_instantaneous_defect_midpoint=.32,
            instantaneous_defect_formula_check=abs(instant_numeric_defect-.32),
            transported_vs_instantaneous_projector_midpoint=float(np.linalg.norm(projector(mid)-instant['projector'], 2))),
        error_scope='finite DOP853 rtol=3e-14 atol=3e-16; independent five-point epsilon=1e-4; Dirac residual in complete constant-sector canonical Haar norm (point norm times sqrt(2*pi^2)), projector residual in coefficient operator norm; no outward/continuum bound or physical derivative admission',
        adopted_Gaussian_preparation_residuals=dict(
            energy_MeV=None, RMS_width_fm=None, centroid_fm=None, spectral_projection=None,
            reason='Not represented by this homogeneous control; physical X/scale/mass-shell realization remains unsolved. These are unexecuted, never passes.'),
        physical_background_constraints_solved=False,
        calibration='unchanged; manufactured control is not assigned the calibrated GeV/fm unit',
        exact_pair_statistics='retained by the original current consumer; no quasifree substitution',
        physical_derivative_admitted=False, coupled_correction=False,
        NEXT_OPERAND='Adjudicate or derive an action-owned incoming boundary-state prescription, including physical constrained reference history/domain and long-range comparison. Do not adopt this manufactured background.')
    return result, dict(transported=sections, instantaneous=instantaneous_sections,
                        transported_coefficients=evolution(mid)@frame0,
                        instantaneous_coefficients=np.column_stack((instant['positive'], instant['negative'])),
                        value_map=(j/np.sqrt(trial['Haar_volume']))[None],
                        H=np.array([[0., 1.125/trial['electron_yukawa']]]),
                        time=mid, Cauchy_quadrature=np.array([trial['Haar_volume']]))

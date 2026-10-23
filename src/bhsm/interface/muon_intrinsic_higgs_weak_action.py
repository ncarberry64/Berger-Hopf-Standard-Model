"""Executable real weak variations of the retained intrinsic-M4 Higgs action.

The convention here is the action-owned (+---) weak form, with positive
coordinate-time and negative spatial kinetic terms.  It is not inferred
from a UV pole's signature string.  All fields, covariant derivatives,
matter sources, tests and domain quadratures are supplied by the caller.
No function chooses a physical Higgs background, source, state or boundary
condition.  The retained E1+ geometry only evaluates its metric weights.

H is a complex doublet.  With q=H^dagger H-nu_squared,
S=int [ (DH)^dagger G DH-w0*(lambda_H*q^2+2 Re(H^dagger J)) ],
where G=density*g^{-1}.  Its real first variation is 2 Re of the weak
complex dual.  Thus E_H=-D^2 H-2 lambda_H q H-J; the doublet is not
silently rescaled by 1/sqrt(2).  HH is real-linear, not complex-linear.

The derivative form is the full bulk action variation and already contains
its temporal/interface contacts.  A separately displayed conormal term
belongs to its integration-by-parts decomposition, not an extra action.
"""
from __future__ import annotations

import math
from pathlib import Path
from fractions import Fraction

import numpy as np

from .ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator
from .muon_birth_candidate_geometry_action import (
    ROOT, evaluate_retained_candidate_geometry,
)


ACTION_OWNER = 'ae31_c2_intrinsic_m4_lepton_action.action_composition_contract'
EULER_OWNER = 'ae31_c2_intrinsic_m4_lepton_action.first_variation_and_pole_gate'


def retained_higgs_spin_charge_representation():
    """Bind the retained Higgs charges and common lepton LR spin frame.

    This evaluates representations only.  It supplies neither a gauge
    connection/coupling nor a mechanical-to-weak identification, and does
    not choose spinor/Higgs values or a field-state expectation.
    """
    from .completion.foundational_dirac_spin_glue_v14_45 import dirac_gamma_matrices
    from .muon_local_source_jet import source_spin_frame
    from .bhsm_standard_model_gauge_vertices import su2_fundamental_generators
    from .aether_hybrid_standard_model_bundle_v15_53 import (
        chiral_bundle_contract, yukawa_and_anomaly_ledger,
    )

    gamma = np.asarray(dirac_gamma_matrices())
    frame = source_spin_frame(gamma)
    weak = np.asarray(su2_fundamental_generators())
    charge = Fraction(yukawa_and_anomaly_ledger()['charges']['H'])
    left = np.vstack((np.eye(2), np.zeros((2, 2))))
    right = np.vstack((np.zeros((2, 2)), np.eye(2)))
    return dict(
        classification='EVALUATED_RETAINED_HIGGS_CHARGE_AND_LR_SPIN_REPRESENTATIONS',
        higgs_representation=chiral_bundle_contract()['scalar_doublet'],
        higgs_su2_generators=weak,
        higgs_hypercharge_exact=str(charge),
        higgs_hypercharge_generator=float(charge)*np.eye(2),
        higgs_color_dimension=1,
        gamma_Dirac=gamma, gamma_LR=frame['gamma_LR'],
        gamma0_LR=frame['gamma_LR'][0],
        Dirac_to_LR_columns=frame['Dirac_to_LR_columns'],
        left_weyl_embedding_LR=left, right_weyl_embedding_LR=right,
        family_yukawa=np.asarray(charged_lepton_yukawa_operator()['family_operator']),
        source_owners=dict(
            gamma='completion.foundational_dirac_spin_glue_v14_45.dirac_gamma_matrices',
            spin_frame='muon_local_source_jet.source_spin_frame',
            weak_generators='bhsm_standard_model_gauge_vertices.su2_fundamental_generators',
            higgs_charge='aether_hybrid_standard_model_bundle_v15_53.yukawa_and_anomaly_ledger',
            higgs_bundle='aether_hybrid_standard_model_bundle_v15_53.chiral_bundle_contract',
            yukawa='ae31_c2_intrinsic_m4_lepton_action.charged_lepton_yukawa_operator'),
        physical_gauge_connection=None, physical_matter_fields=None,
        mechanical_connection_identified_with_weak=False,
        physical_scalar_primal_selected=False)


def _finite(value, name, *, complex_value=False):
    result = np.asarray(value, dtype=complex if complex_value else float)
    if not np.all(np.isfinite(result)):
        raise ValueError(f'{name} must be finite')
    return result


def _doublet(value, name, count=None):
    result = _finite(value, name, complex_value=True)
    if result.ndim != 2 or result.shape[1] != 2 or result.shape[0] == 0:
        raise ValueError(f'{name} must have shape (points, 2)')
    if count is not None and result.shape[0] != count:
        raise ValueError(f'{name} point count disagrees')
    return result


def _derivative(value, name, count):
    result = _finite(value, name, complex_value=True)
    if result.shape != (count, 4, 2):
        raise ValueError(f'{name} must have shape (points, 4, 2)')
    return result


def _scalar_points(value, name, count):
    result = _finite(value, name)
    try:
        return np.broadcast_to(result, (count,))
    except ValueError as error:
        raise ValueError(f'{name} must be scalar or have shape (points,)') from error


def _kinetic(value, name, count):
    result = _finite(value, name)
    try:
        result = np.broadcast_to(result, (count, 4, 4))
    except ValueError as error:
        raise ValueError(f'{name} must have shape (4,4) or (points,4,4)') from error
    if not np.allclose(result, np.swapaxes(result, -1, -2), rtol=0, atol=1e-13):
        raise ValueError(f'{name} must be symmetric')
    return result


def _couplings(lambda_H, nu_squared):
    lam, nu2 = float(lambda_H), float(nu_squared)
    if not math.isfinite(lam) or lam <= 0 or not math.isfinite(nu2) or nu2 < 0:
        raise ValueError('lambda_H must be positive and nu_squared nonnegative')
    return lam, nu2


def _base(quadrature, kinetic_density, volume_density, H, DH, J, lambda_H, nu_squared):
    H = _doublet(H, 'H')
    count = len(H)
    DH, J = _derivative(DH, 'DH', count), _doublet(J, 'J', count)
    quadrature = _scalar_points(quadrature, 'quadrature', count)
    volume = _scalar_points(volume_density, 'volume_density', count)
    if np.any(quadrature < 0) or np.any(volume <= 0):
        raise ValueError('quadrature must be nonnegative and volume_density positive')
    kinetic = _kinetic(kinetic_density, 'kinetic_density', count)
    lam, nu2 = _couplings(lambda_H, nu_squared)
    return quadrature, kinetic, volume, H, DH, J, lam, nu2


def realify_doublet(H):
    """Return (Re H1, Re H2, Im H1, Im H2), without rescaling."""
    H = _doublet(H, 'H')
    return np.concatenate((H.real, H.imag), axis=1)


def complexify_doublet(real_H):
    """Inverse of :func:`realify_doublet` in the same real chart."""
    value = _finite(real_H, 'real_H')
    if value.ndim != 2 or value.shape[1] != 4 or len(value) == 0:
        raise ValueError('real_H must have shape (points, 4)')
    return value[:, :2] + 1j*value[:, 2:]


def intrinsic_m4_weights(N, R4):
    """Coordinate-time weights per unit S3 measure; no Haar volume added.

    The caller's quadrature supplies time and unit-S3 angular integration.
    A fiber volume or ambient M8 area is not the intrinsic-M4 measure.
    """
    N, R4 = np.broadcast_arrays(_finite(N, 'N'), _finite(R4, 'R4'))
    if np.any(N <= 0) or np.any(R4 <= 0):
        raise ValueError('N and R4 must be positive')
    return dict(time=R4**3/N, spatial=N*R4, potential=N*R4**3)


def diagonal_kinetic_density(weights):
    """Convert intrinsic diagonal weights to the (+---) density tensor."""
    time, spatial = np.broadcast_arrays(_finite(weights['time'], 'time'),
                                        _finite(weights['spatial'], 'spatial'))
    result = np.zeros(time.shape + (4, 4))
    result[..., 0, 0] = time
    for index in range(1, 4):
        result[..., index, index] = -spatial
    return result


def intrinsic_m4_weight_variation(N, R4, *, delta_log_N, delta_log_R4):
    """Partial metric-weight derivative; field/connection jets are separate."""
    weights = intrinsic_m4_weights(N, R4)
    n, r = np.broadcast_arrays(_finite(delta_log_N, 'delta_log_N'),
                               _finite(delta_log_R4, 'delta_log_R4'))
    return dict(time=weights['time']*(3*r-n),
                spatial=weights['spatial']*(r+n),
                potential=weights['potential']*(3*r+n))


def retained_e1_intrinsic_coefficients(repository: Path | str = ROOT):
    """Evaluate only intrinsic weights at the saved actual E1+ geometry.

    These are coefficients for a supplied-data action application, not a
    physical Higgs solution or full stationary interacting base.
    """
    candidate = evaluate_retained_candidate_geometry(repository)
    geometry = candidate['geometry']
    N, R4, C = (geometry[key] for key in ('N', 'R4', 'C'))
    a_v = geometry['chi_first_log']['R4']/C
    weights = intrinsic_m4_weights(N, R4)
    first = intrinsic_m4_weight_variation(N, R4, delta_log_N=0.0,
                                           delta_log_R4=a_v)
    yukawa = charged_lepton_yukawa_operator()
    return dict(classification='EVALUATED_RETAINED_E1_PLUS_INTRINSIC_M4_COEFFICIENTS',
                source=candidate['source'], N=N, R4=R4, C=C,
                lambda_geom=geometry['lambda_geom'],
                normal_first_log_R4_per_unit_amplitude=a_v,
                normal_first_log_intrinsic_measure_per_unit_amplitude=3*a_v,
                weights={key:float(value) for key, value in weights.items()},
                normal_first_weights={key:float(value) for key, value in first.items()},
                polynomial_coefficient_map=dict(
                    kinetic_time=float(weights['time']),
                    kinetic_spatial=-float(weights['spatial']),
                    quartic_factor_times_lambda_H=-float(weights['potential']),
                    quadratic_factor_times_lambda_H_nu_squared=2*float(weights['potential']),
                    constant_factor_times_lambda_H_nu_squared_squared=-float(weights['potential']),
                    source_factor_times_Re_H_dagger_J=-2*float(weights['potential']),
                    family_yukawa=yukawa['family_operator']),
                scalar_primal_evaluated=False, stationary_base_established=False,
                scope='Radial graph first jet at beta_star=0; explicit connection/frame/source/constraint and boundary jets are not replaced by these weights')


def higgs_potential_gradient(H, *, lambda_H, nu_squared):
    """Complex Euler potential 2 lambda q H (before its minus sign)."""
    H = _doublet(H, 'H')
    lam, nu2 = _couplings(lambda_H, nu_squared)
    q = np.sum(np.abs(H)**2, axis=1)-nu2
    return 2*lam*q[:, None]*H


def higgs_potential_hessian_application(H, h, *, lambda_H, nu_squared):
    """Real-linear potential derivative, retaining the conjugate-h term."""
    H = _doublet(H, 'H')
    h = _doublet(h, 'h', len(H))
    lam, nu2 = _couplings(lambda_H, nu_squared)
    q = np.sum(np.abs(H)**2, axis=1)-nu2
    radial = 2*np.real(np.sum(H.conj()*h, axis=1))
    return 2*lam*(q[:, None]*h+radial[:, None]*H)


def higgs_potential_real_hessian(H, *, lambda_H, nu_squared):
    """Jacobian of the complex Euler potential in the unscaled real chart.

    The Hessian of lambda*q^2 as a real action is twice this matrix.
    """
    H = _doublet(H, 'H')
    lam, nu2 = _couplings(lambda_H, nu_squared)
    x = realify_doublet(H)
    q = np.sum(x*x, axis=1)-nu2
    return 2*lam*(q[:, None, None]*np.eye(4)+2*x[:, :, None]*x[:, None, :])


def _kinetic_pair(left, kinetic, right):
    return np.einsum('pmi,pmn,pni->p', left.conj(), kinetic, right)


def higgs_action(*, quadrature, kinetic_density, volume_density, H, DH, J,
                 lambda_H, nu_squared):
    """Literal retained scalar action with explicitly supplied source."""
    quad, G, w0, H, DH, J, lam, nu2 = _base(
        quadrature, kinetic_density, volume_density, H, DH, J, lambda_H, nu_squared)
    q = np.sum(np.abs(H)**2, axis=1)-nu2
    potential = lam*q*q+2*np.real(np.sum(H.conj()*J, axis=1))
    return float(np.sum(quad*(_kinetic_pair(DH, G, DH).real-w0*potential)))


def higgs_weak_residual(*, quadrature, kinetic_density, volume_density, H, DH, J,
                        phi, Dphi, lambda_H, nu_squared):
    """Full derivative-form action variation 2 Re r_H[phi].

    Tests need not satisfy a boundary condition here.  Compact support,
    temporal traces and any constrained-test domain are caller-owned.
    """
    quad, G, w0, H, DH, J, lam, nu2 = _base(
        quadrature, kinetic_density, volume_density, H, DH, J, lambda_H, nu_squared)
    phi, Dphi = _doublet(phi, 'phi', len(H)), _derivative(Dphi, 'Dphi', len(H))
    F = higgs_potential_gradient(H, lambda_H=lam, nu_squared=nu2)+J
    value = _kinetic_pair(Dphi, G, DH)-w0*np.sum(phi.conj()*F, axis=1)
    return float(2*np.real(np.sum(quad*value)))


def higgs_hessian_application(*, quadrature, kinetic_density, volume_density,
                              H, phi, Dphi, h, Dh, lambda_H, nu_squared):
    """Fixed-background HH weak block, with the matter source held fixed."""
    H = _doublet(H, 'H')
    count = len(H)
    phi, h = _doublet(phi, 'phi', count), _doublet(h, 'h', count)
    Dphi, Dh = _derivative(Dphi, 'Dphi', count), _derivative(Dh, 'Dh', count)
    quad = _scalar_points(quadrature, 'quadrature', count)
    w0 = _scalar_points(volume_density, 'volume_density', count)
    if np.any(quad < 0) or np.any(w0 <= 0):
        raise ValueError('quadrature must be nonnegative and volume_density positive')
    G = _kinetic(kinetic_density, 'kinetic_density', count)
    dF = higgs_potential_hessian_application(H, h, lambda_H=lambda_H,
                                            nu_squared=nu_squared)
    value = _kinetic_pair(Dphi, G, Dh)-w0*np.sum(phi.conj()*dF, axis=1)
    return float(2*np.real(np.sum(quad*value)))


def realified_higgs_weak_jacobian(*, quadrature, kinetic_density, volume_density,
                                 H, test_values, test_derivatives, trial_values,
                                 trial_derivatives, lambda_H, nu_squared):
    """Assemble HH on caller-supplied real test/trial directions.

    Complex direction arrays represent real-coordinate vectors: i*h is a
    distinct real direction, not a complex scalar multiple for assembly.
    This imposes neither a physical basis nor a trace/retarded domain.
    """
    H = _doublet(H, 'H')
    count = len(H)
    tests = _finite(test_values, 'test_values', complex_value=True)
    trials = _finite(trial_values, 'trial_values', complex_value=True)
    Dtests = _finite(test_derivatives, 'test_derivatives', complex_value=True)
    Dtrials = _finite(trial_derivatives, 'trial_derivatives', complex_value=True)
    for value, derivative, name in ((tests, Dtests, 'test'), (trials, Dtrials, 'trial')):
        if (value.ndim != 3 or value.shape[1:] != (count, 2)
                or derivative.shape != (len(value), count, 4, 2)):
            raise ValueError(f'{name} basis needs (basis,points,2) and (basis,points,4,2)')
    matrix = np.empty((len(tests), len(trials)))
    for i, (phi, Dphi) in enumerate(zip(tests, Dtests)):
        for j, (h, Dh) in enumerate(zip(trials, Dtrials)):
            matrix[i, j] = higgs_hessian_application(
                quadrature=quadrature, kinetic_density=kinetic_density,
                volume_density=volume_density, H=H, phi=phi, Dphi=Dphi,
                h=h, Dh=Dh, lambda_H=lambda_H, nu_squared=nu_squared)
    return matrix


def _lepton_inputs(L_L, e_R, Y_l, gamma0):
    L = _finite(L_L, 'L_L', complex_value=True)
    e = _finite(e_R, 'e_R', complex_value=True)
    Y = _finite(Y_l, 'Y_l', complex_value=True)
    if L.ndim != 4 or L.shape[1] != 2 or e.ndim != 3 or len(L) == 0:
        raise ValueError('L_L needs (points,2,families_L,spin) and e_R (points,families_R,spin)')
    if len(e) != len(L) or L.shape[3] != e.shape[2] or Y.shape != (L.shape[2], e.shape[1]):
        raise ValueError('lepton point, spin or Yukawa family dimensions disagree')
    spin = e.shape[2]
    gamma = _finite(gamma0, 'gamma0', complex_value=True)
    try:
        gamma = np.broadcast_to(gamma, (len(L), spin, spin))
    except ValueError as error:
        raise ValueError('gamma0 needs (spin,spin) or (points,spin,spin)') from error
    if not np.allclose(gamma, np.swapaxes(gamma.conj(), -1, -2), rtol=0, atol=1e-13):
        raise ValueError('the supplied Dirac-adjoint gamma0 must be Hermitian')
    return L, e, Y, gamma


def lepton_higgs_source(*, L_L, e_R, Y_l, gamma0):
    """J_a=bar(e_R) Y_l^dagger L_L^a in an explicit common spin frame.

    Y_l is the fixed action-owned family operator or its specified basis
    representation.  The supplied gamma0/chiral embeddings are required;
    no spin frame, state expectation or physical matter field is selected.
    """
    L, e, Y, gamma = _lepton_inputs(L_L, e_R, Y_l, gamma0)
    return np.einsum('pfs,pst,gf,pagt->pa', e.conj(), gamma, Y.conj(), L)


def lepton_higgs_source_variation(*, L_L, e_R, Y_l, gamma0,
                                 delta_L_L, delta_e_R, delta_gamma0=None):
    """Matter/frame cross jet of J with the inherited family operator fixed."""
    L, e, Y, gamma = _lepton_inputs(L_L, e_R, Y_l, gamma0)
    dL = _finite(delta_L_L, 'delta_L_L', complex_value=True)
    de = _finite(delta_e_R, 'delta_e_R', complex_value=True)
    if dL.shape != L.shape or de.shape != e.shape:
        raise ValueError('matter variations must have the same shapes as the fields')
    if delta_gamma0 is None:
        dgamma = np.zeros_like(gamma)
    else:
        dgamma = _finite(delta_gamma0, 'delta_gamma0', complex_value=True)
        try:
            dgamma = np.broadcast_to(dgamma, gamma.shape)
        except ValueError as error:
            raise ValueError('delta_gamma0 shape disagrees') from error
        if not np.allclose(dgamma, np.swapaxes(dgamma.conj(), -1, -2), rtol=0, atol=1e-13):
            raise ValueError('Dirac-adjoint frame jet must be Hermitian')
    return (np.einsum('pfs,pst,gf,pagt->pa', de.conj(), gamma, Y.conj(), L)
            +np.einsum('pfs,pst,gf,pagt->pa', e.conj(), dgamma, Y.conj(), L)
            +np.einsum('pfs,pst,gf,pagt->pa', e.conj(), gamma, Y.conj(), dL))


def gauge_covariant_variation(delta_connection, H, phi):
    """Apply a supplied anti-Hermitian Higgs-representation connection jet.

    Returns (delta_DH, delta_Dphi).  The connection is not reconstructed
    from the ambient mechanical connection without a representation map.
    """
    H = _doublet(H, 'H')
    phi = _doublet(phi, 'phi', len(H))
    delta = _finite(delta_connection, 'delta_connection', complex_value=True)
    if delta.shape != (len(H), 4, 2, 2):
        raise ValueError('delta_connection must have shape (points,4,2,2)')
    adjoint = np.swapaxes(delta.conj(), -1, -2)
    if not np.allclose(delta+adjoint, 0, rtol=0, atol=1e-13):
        raise ValueError('unitary-representation connection jet must be anti-Hermitian')
    return (np.einsum('pmij,pj->pmi', delta, H),
            np.einsum('pmij,pj->pmi', delta, phi))


def higgs_explicit_weak_variation(*, quadrature, kinetic_density, volume_density,
                                 H, DH, J, phi, Dphi, lambda_H, nu_squared,
                                 delta_kinetic_density=None, delta_volume_density=None,
                                 delta_J=None, delta_DH=None, delta_Dphi=None,
                                 kinematic_H_lift=None, test_lift=None,
                                 delta_quadrature=None):
    """Differentiate the entire pulled weak residual before stationarity.

    Omitted jets hold that mathematical input fixed.  ``delta_DH`` and
    ``delta_Dphi`` are total explicit covariant-derivative jets (frame,
    connection and any prescribed kinematic lift), not partial derivatives
    of their arrays.  ``kinematic_H_lift`` is a prescribed chart lift only;
    an induced unknown h=D_s H_star belongs to HH, not this partial source.
    Tests transported by the chart supply both test_lift and delta_Dphi.
    Source and geometry remain independent inputs; coupled cross blocks
    are applications with their action-owned delta_J/density jets supplied.
    Quadrature is the reference integration rule.  Independent reference-
    domain motion may supply delta_quadrature; any domain Jacobian belongs
    either there or in the density tensors, once, never in both.
    """
    quad, G, w0, H, DH, J, lam, nu2 = _base(
        quadrature, kinetic_density, volume_density, H, DH, J, lambda_H, nu_squared)
    count = len(H)
    phi, Dphi = _doublet(phi, 'phi', count), _derivative(Dphi, 'Dphi', count)
    dG = np.zeros_like(G) if delta_kinetic_density is None else _kinetic(
        delta_kinetic_density, 'delta_kinetic_density', count)
    dw = np.zeros_like(w0) if delta_volume_density is None else _scalar_points(
        delta_volume_density, 'delta_volume_density', count)
    dJ = np.zeros_like(J) if delta_J is None else _doublet(delta_J, 'delta_J', count)
    dH = np.zeros_like(H) if kinematic_H_lift is None else _doublet(
        kinematic_H_lift, 'kinematic_H_lift', count)
    dphi = np.zeros_like(phi) if test_lift is None else _doublet(test_lift, 'test_lift', count)
    dDH = np.zeros_like(DH) if delta_DH is None else _derivative(delta_DH, 'delta_DH', count)
    dDphi = np.zeros_like(Dphi) if delta_Dphi is None else _derivative(
        delta_Dphi, 'delta_Dphi', count)
    dquad = np.zeros_like(quad) if delta_quadrature is None else _scalar_points(
        delta_quadrature, 'delta_quadrature', count)
    F = higgs_potential_gradient(H, lambda_H=lam, nu_squared=nu2)+J
    dF = higgs_potential_hessian_application(H, dH, lambda_H=lam,
                                            nu_squared=nu2)+dJ
    value = (_kinetic_pair(dDphi, G, DH)+_kinetic_pair(Dphi, dG, DH)
             +_kinetic_pair(Dphi, G, dDH)
             -dw*np.sum(phi.conj()*F, axis=1)
             -w0*np.sum(dphi.conj()*F+phi.conj()*dF, axis=1))
    base = _kinetic_pair(Dphi, G, DH)-w0*np.sum(phi.conj()*F, axis=1)
    return float(2*np.real(np.sum(quad*value+dquad*base)))


def higgs_metric_action_variation(*, quadrature, kinetic_density, volume_density,
                                H, DH, J, lambda_H, nu_squared,
                                delta_kinetic_density, delta_volume_density,
                                delta_J=None, delta_DH=None, delta_quadrature=None):
    """Metric/lapse action cotangent at fixed H, retaining off-shell measure.

    An explicit source/frame/connection metric jet may also be supplied.
    No primal ADM reaction or stationary-base substitution is added here.
    A separate reference/domain quadrature jet is optional.  Assign any
    moving integration Jacobian to quadrature or metric density only once.
    """
    quad, G, w0, H, DH, J, lam, nu2 = _base(
        quadrature, kinetic_density, volume_density, H, DH, J, lambda_H, nu_squared)
    count = len(H)
    dG = _kinetic(delta_kinetic_density, 'delta_kinetic_density', count)
    dw = _scalar_points(delta_volume_density, 'delta_volume_density', count)
    dJ = np.zeros_like(J) if delta_J is None else _doublet(delta_J, 'delta_J', count)
    dDH = np.zeros_like(DH) if delta_DH is None else _derivative(delta_DH, 'delta_DH', count)
    dquad = np.zeros_like(quad) if delta_quadrature is None else _scalar_points(
        delta_quadrature, 'delta_quadrature', count)
    q = np.sum(np.abs(H)**2, axis=1)-nu2
    potential = lam*q*q+2*np.real(np.sum(H.conj()*J, axis=1))
    kinetic = (_kinetic_pair(DH, dG, DH).real
               +2*_kinetic_pair(DH, G, dDH).real)
    base = _kinetic_pair(DH, G, DH).real-w0*potential
    return float(np.sum(quad*(kinetic-dw*potential
                             -2*w0*np.real(np.sum(H.conj()*dJ, axis=1)))+dquad*base))


def higgs_fixed_field_action_two_jet(*, quadrature, kinetic_density, volume_density,
                                   H, DH, J, lambda_H, nu_squared,
                                   kinetic_density_first, kinetic_density_second,
                                   volume_density_first, volume_density_second,
                                   DH_first=None, DH_second=None,
                                   J_first=None, J_second=None,
                                   quadrature_first=None, quadrature_second=None):
    """Partial scalar action (value, first, second) at fixed internal H.

    This retains explicit metric, covariant-derivative, matter-source and
    independent reference-domain product contacts.  DH jets are explicit
    connection/frame lifts compatible with this fixed-H chart, not an
    induced Higgs response.  A chart that moves H's value also needs its
    potential/source value jets and the HH cross applications.  No
    ambient normal derivative of the intrinsic field is introduced.
    Optional absent jets hold the corresponding mathematical input fixed.
    """
    quad, G, w0, H, DH, J, lam, nu2 = _base(
        quadrature, kinetic_density, volume_density, H, DH, J, lambda_H, nu_squared)
    count = len(H)
    G1 = _kinetic(kinetic_density_first, 'kinetic_density_first', count)
    G2 = _kinetic(kinetic_density_second, 'kinetic_density_second', count)
    w1 = _scalar_points(volume_density_first, 'volume_density_first', count)
    w2 = _scalar_points(volume_density_second, 'volume_density_second', count)
    D1 = np.zeros_like(DH) if DH_first is None else _derivative(DH_first, 'DH_first', count)
    D2 = np.zeros_like(DH) if DH_second is None else _derivative(DH_second, 'DH_second', count)
    J1 = np.zeros_like(J) if J_first is None else _doublet(J_first, 'J_first', count)
    J2 = np.zeros_like(J) if J_second is None else _doublet(J_second, 'J_second', count)
    q1 = np.zeros_like(quad) if quadrature_first is None else _scalar_points(
        quadrature_first, 'quadrature_first', count)
    q2 = np.zeros_like(quad) if quadrature_second is None else _scalar_points(
        quadrature_second, 'quadrature_second', count)
    q = np.sum(np.abs(H)**2, axis=1)-nu2
    V = lam*q*q+2*np.real(np.sum(H.conj()*J, axis=1))
    V1 = 2*np.real(np.sum(H.conj()*J1, axis=1))
    V2 = 2*np.real(np.sum(H.conj()*J2, axis=1))
    k0 = _kinetic_pair(DH, G, DH).real
    k1 = (_kinetic_pair(DH, G1, DH).real+2*_kinetic_pair(DH, G, D1).real)
    k2 = (_kinetic_pair(DH, G2, DH).real+2*_kinetic_pair(D1, G, D1).real
          +4*_kinetic_pair(D1, G1, DH).real+2*_kinetic_pair(DH, G, D2).real)
    value = k0-w0*V
    first = k1-w1*V-w0*V1
    second = k2-w2*V-2*w1*V1-w0*V2
    return dict(value=float(np.sum(quad*value)),
                first=float(np.sum(quad*first+q1*value)),
                second=float(np.sum(quad*second+2*q1*first+q2*value)))


def higgs_conormal_flux(DH, oriented_flux_coefficients):
    """Construct the complex canonical flux from supplied Stokes coefficients.

    c^nu includes oriented normal, induced measure and metric contraction
    in the caller's boundary quadrature.  At the final t slice c^t=Wt;
    at the initial slice c^t=-Wt.  No spacelike-normal sign is inferred.
    """
    DH = _finite(DH, 'DH', complex_value=True)
    if DH.ndim != 3 or DH.shape[1:] != (4, 2) or len(DH) == 0:
        raise ValueError('DH must have shape (points,4,2)')
    coefficients = _finite(oriented_flux_coefficients, 'oriented_flux_coefficients')
    if coefficients.shape != (len(DH), 4):
        raise ValueError('oriented_flux_coefficients must have shape (points,4)')
    return np.einsum('pm,pmi->pi', coefficients, DH)


def higgs_boundary_pairing(*, boundary_quadrature, phi, flux):
    """The real boundary/contact term in the bulk variation's IBP identity.

    Reference boundary quadrature and flux density must assign their
    measure factors once; this displayed contact is not appended again
    to the full derivative-form residual.
    """
    phi = _doublet(phi, 'phi')
    flux = _doublet(flux, 'flux', len(phi))
    quad = _scalar_points(boundary_quadrature, 'boundary_quadrature', len(phi))
    if np.any(quad < 0):
        raise ValueError('boundary quadrature must be nonnegative')
    return float(2*np.real(np.sum(quad*np.sum(phi.conj()*flux, axis=1))))


def higgs_boundary_variation(*, boundary_quadrature, phi, flux, delta_flux,
                             test_lift, delta_boundary_quadrature=None):
    """Boundary/conormal and transported-test derivative without double count.

    Flux includes its stated oriented density.  A measure/domain jet is
    assigned to delta_flux or delta_boundary_quadrature, never both.
    """
    phi = _doublet(phi, 'phi')
    count = len(phi)
    flux = _doublet(flux, 'flux', count)
    delta_flux = _doublet(delta_flux, 'delta_flux', count)
    test_lift = _doublet(test_lift, 'test_lift', count)
    quad = _scalar_points(boundary_quadrature, 'boundary_quadrature', count)
    if np.any(quad < 0):
        raise ValueError('boundary quadrature must be nonnegative')
    dquad = np.zeros_like(quad) if delta_boundary_quadrature is None else _scalar_points(
        delta_boundary_quadrature, 'delta_boundary_quadrature', count)
    value = quad*np.sum(test_lift.conj()*flux+phi.conj()*delta_flux, axis=1)
    value += dquad*np.sum(phi.conj()*flux, axis=1)
    return float(2*np.real(np.sum(value)))


def higgs_supplied_constraint_variation(*, constraint_weak_H, delta_constraint_weak_H,
                                       multiplier, multiplier_variation):
    """Preserve a supplied real constraint/multiplier Higgs cotangent.

    These are already action-owned real weak applications, not raw residual
    rows or Euclidean replacements for action covectors.  This computes
    lambda*d(R_H[phi])+delta_lambda*R_H[phi] without selecting lambda.
    """
    base, delta, lam, dlam = np.broadcast_arrays(
        _finite(constraint_weak_H, 'constraint_weak_H'),
        _finite(delta_constraint_weak_H, 'delta_constraint_weak_H'),
        _finite(multiplier, 'multiplier'),
        _finite(multiplier_variation, 'multiplier_variation'))
    return float(np.sum(lam*delta+dlam*base))

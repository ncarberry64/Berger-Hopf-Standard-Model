"""Measured-input matching arithmetic for the retained fixed lepton operator.

This module does not alter the Yukawa operator, insert measured masses into
it, or assign pole residues.  It evaluates the tree electroweak matching and
the total pole corrections which an interacting same-action calculation
would have to reproduce.  The caller owns the measured-input edition,
extraction assumptions and covariance, including the lifetime/mass coupling
in the extraction of G_F.  All dimensionful arguments here are in GeV.
"""
from __future__ import annotations

from collections.abc import Mapping
from math import sqrt

import numpy as np

from .ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator
from .muon_intrinsic_higgs_weak_action import (
    higgs_weak_residual, realified_higgs_weak_jacobian,
)
from .muon_intrinsic_lepton_primal import classical_bosonic_body_source


FAMILIES = ('tau', 'muon', 'electron')
INPUT_ORDER = ('G_F_GeV_inverse_squared', 'm_h_GeV',
               'm_tau_GeV', 'm_muon_GeV', 'm_electron_GeV')
OUTPUT_ORDER = ('v_GeV', 'nu_squared_GeV_squared', 'lambda_H',
                'm_tree_tau_GeV', 'm_tree_muon_GeV', 'm_tree_electron_GeV',
                'pole_minus_tree_tau_GeV', 'pole_minus_tree_muon_GeV',
                'pole_minus_tree_electron_GeV',
                'required_pole_factor_tau', 'required_pole_factor_muon',
                'required_pole_factor_electron',
                'v_from_tau_GeV', 'v_from_muon_GeV', 'v_from_electron_GeV',
                'tau_muon_ratio_factor', 'muon_electron_ratio_factor',
                'tau_electron_ratio_factor')


def _positive(value, name):
    x = float(value)
    if not np.isfinite(x) or x <= 0:
        raise ValueError(f'{name} must be finite and positive')
    return x


def _mass_vector(pole_masses_GeV):
    if isinstance(pole_masses_GeV, Mapping):
        if set(pole_masses_GeV) != set(FAMILIES):
            raise ValueError('pole masses require tau, muon and electron keys')
        values = [pole_masses_GeV[f] for f in FAMILIES]
    else:
        values = pole_masses_GeV
    a = np.asarray(values, dtype=float)
    if a.shape != (3,) or not np.isfinite(a).all() or np.any(a <= 0):
        raise ValueError('three positive pole masses in tau,muon,electron order required')
    return a


def _covariance(value):
    if value is None:
        return None
    c = np.asarray(value, dtype=float)
    if c.shape != (5, 5) or not np.isfinite(c).all():
        raise ValueError('finite five-input covariance required')
    scale = max(float(np.max(np.abs(c))), np.finfo(float).tiny)
    if not np.allclose(c, c.T, atol=scale*1e-13, rtol=1e-13):
        raise ValueError('input covariance must be symmetric')
    if np.min(np.linalg.eigvalsh(c)) < -scale*1e-12:
        raise ValueError('input covariance must be positive semidefinite')
    return (c+c.T)/2


def calibrated_tree_matching(*, fermi_constant_GeV_inverse_squared,
                             higgs_mass_GeV, pole_masses_GeV,
                             input_covariance=None):
    """Evaluate fixed-Y tree matching and required interacting pole shifts.

    ``input_covariance`` uses INPUT_ORDER, in the stated dimensionful units.
    The propagated covariance is a first-order input uncertainty only.  It
    excludes radiative/matching error, model error and a native contribution.
    An omitted covariance never becomes an assertion of zero uncertainty.
    """
    gf = _positive(fermi_constant_GeV_inverse_squared, 'G_F')
    mh = _positive(higgs_mass_GeV, 'm_h')
    masses = _mass_vector(pole_masses_GeV)
    y = np.asarray(charged_lepton_yukawa_operator()['eigenvalues_heavy_middle_light'])
    v = (sqrt(2)*gf)**-.5
    nu2 = v*v/2
    lam = gf*mh*mh/sqrt(2)
    tree = v*y/sqrt(2)
    shift = masses-tree
    factors = masses/tree
    family_v = sqrt(2)*masses/y
    pairs = ((0, 1), (1, 2), (0, 2))
    ratio_factors = np.array([(masses[i]/masses[j])/(y[i]/y[j]) for i, j in pairs])
    outputs = np.concatenate(([v, nu2, lam], tree, shift, factors, family_v, ratio_factors))
    jac = np.zeros((len(OUTPUT_ORDER), len(INPUT_ORDER)))
    jac[0, 0] = -v/(2*gf)
    jac[1, 0] = -nu2/gf
    jac[2, 0], jac[2, 1] = lam/gf, 2*lam/mh
    for i in range(3):
        jac[3+i, 0] = -tree[i]/(2*gf)
        jac[6+i, 0], jac[6+i, 2+i] = tree[i]/(2*gf), 1
        jac[9+i, 0], jac[9+i, 2+i] = factors[i]/(2*gf), 1/tree[i]
        jac[12+i, 2+i] = sqrt(2)/y[i]
    for k, (i, j) in enumerate(pairs):
        jac[15+k, 2+i] = ratio_factors[k]/masses[i]
        jac[15+k, 2+j] = -ratio_factors[k]/masses[j]
    covariance = _covariance(input_covariance)
    propagated = None if covariance is None else jac@covariance@jac.T
    uncertainties = None if propagated is None else np.sqrt(np.maximum(np.diag(propagated), 0))
    rows = []
    for i, family in enumerate(FAMILIES):
        rows.append(dict(family=family, fixed_yukawa=float(y[i]),
            tree_mass_GeV=float(tree[i]), measured_pole_mass_GeV=float(masses[i]),
            pole_minus_tree_GeV=float(shift[i]), required_pole_factor=float(factors[i]),
            required_relative_pole_shift=float(factors[i]-1),
            v_required_with_unmodified_tree_kinetics_GeV=float(family_v[i]),
            # These are two possible algebraic allocations, not fitted inputs.
            mass_only_shift_if_A_left_A_right_equal_one_GeV=float(shift[i]),
            kinetic_product_if_no_masslike_shift=float(factors[i]**-2)))
    ratio_rows = [dict(numerator=FAMILIES[i], denominator=FAMILIES[j],
        fixed_yukawa_ratio=float(y[i]/y[j]), measured_pole_ratio=float(masses[i]/masses[j]),
        required_relative_pole_factor=float(ratio_factors[k]),
        relative_ratio_discrepancy=float(ratio_factors[k]-1))
        for k, (i, j) in enumerate(pairs)]
    return dict(classification='CALIBRATED_TREE_MATCHING_AND_REQUIRED_POLE_CORRECTIONS',
        matching_order='TREE; radiative and BHSM corrections remain to be calculated',
        input_order=list(INPUT_ORDER), input_values=[gf, mh, *masses.tolist()],
        output_order=list(OUTPUT_ORDER), output_values=outputs.tolist(),
        input_covariance=None if covariance is None else covariance.tolist(),
        output_covariance=None if propagated is None else propagated.tolist(),
        output_standard_uncertainties=None if uncertainties is None else uncertainties.tolist(),
        input_jacobian=jac.tolist(),
        input_uncertainty_method='FIRST_ORDER_COVARIANCE' if covariance is not None else 'NOT_SUPPLIED',
        full_prediction_uncertainty_established=False,
        v_GeV=float(v), nu_squared_GeV_squared=float(nu2), lambda_H=float(lam),
        fixed_yukawa_owner='ae31_c2_intrinsic_m4_lepton_action.charged_lepton_yukawa_operator',
        family_rows=rows, ratio_rows=ratio_rows,
        tree_equations=['v^2=1/(sqrt(2)*G_F)', 'nu^2=v^2/2',
                        'lambda_H=m_h^2/(2*v^2)', 'M_l=v*Y_l/sqrt(2)'],
        pole_equation='m_f^2*A_L(m_f^2)*A_R(m_f^2)=B_L(m_f^2)*B_R(m_f^2)',
        cp_real_pole_equation='m_f/M0_f=(1+Sigma_m(m_f^2)/M0_f)/sqrt(A_L*A_R)',
        required_corrections_fitted=False, independent_yukawas_introduced=False,
        mass_input_assigns_residue=False, stationary_base_solved=False,
        common_scale_matches_all_supplied_central_mass_ratios=bool(
            np.allclose(ratio_factors, 1, rtol=1e-13, atol=1e-13)),
        native_cutoff_assigned=False, action_selected=False, Gate7_closed=False,
        muon_anomaly_calibration_used=False, full_native_pauli_evaluated=False)


def chiral_pole_denominator_application(*, pole_mass_GeV, A_left, A_right,
                                      B_left_GeV, B_right_GeV,
                                      dA_left_dp_squared=None,
                                      dA_right_dp_squared=None,
                                      dB_left_dp_squared=None,
                                      dB_right_dp_squared=None):
    """Apply one supplied CP-real chiral inverse-propagator pole condition.

    For Gamma=/p(A_L P_L+A_R P_R)-(B_L P_L+B_R P_R), the scalar squared
    denominator is K(s)=s A_L A_R-B_L B_R.  Its derivative is needed by the
    full matrix pole residue.  ``1/K'`` alone is not a normalized external
    spinor or a Dirac LSZ factor: the adjugate and pairing remain required.
    This routine evaluates supplied same-action coefficients; it fits none.
    """
    mass = _positive(pole_mass_GeV, 'pole mass')
    al, ar = _positive(A_left, 'A_left'), _positive(A_right, 'A_right')
    bl, br = float(B_left_GeV), float(B_right_GeV)
    if not np.isfinite([bl, br]).all():
        raise ValueError('finite CP-real masslike coefficients required')
    s = mass*mass
    residual = s*al*ar-bl*br
    derivatives = (dA_left_dp_squared, dA_right_dp_squared,
                   dB_left_dp_squared, dB_right_dp_squared)
    if any(x is None for x in derivatives) and not all(x is None for x in derivatives):
        raise ValueError('all four pole derivatives required together')
    slope = None
    if all(x is not None for x in derivatives):
        dal, dar, dbl, dbr = map(float, derivatives)
        if not np.isfinite([dal, dar, dbl, dbr]).all():
            raise ValueError('finite pole derivatives required')
        slope = al*ar+s*(dal*ar+al*dar)-dbl*br-bl*dbr
    return dict(pole_mass_GeV=mass, scalar_denominator_GeV_squared=float(residual),
        derivative_with_respect_to_p_squared=None if slope is None else float(slope),
        simple_scalar_pole=None if slope is None else bool(slope != 0),
        inverse_scalar_slope=None if slope is None or slope == 0 else float(1/slope),
        normalized_external_state_evaluated=False, physical_lsz_residue_evaluated=False,
        mass_or_residue_fitted=False)


def higgs_scalar_action_unit_conversion(*, nu_squared_GeV_squared,
                                       energy_unit_GeV):
    """Convert the canonical dimension-one H field using an explicit E_unit.

    If x_phys=x_chart/E_unit and H_phys=E_unit H_chart (hbar=c=1),
    nu_chart^2=nu_phys^2/E_unit^2 and lambda_H is unchanged.  This is a
    dimensional conversion, not an identification of E_unit with a measured
    lepton mass, Planck energy, interface stiffness or the native cutoff.
    Its physical normalization must be supplied by the calibration owner.
    """
    nu2 = _positive(nu_squared_GeV_squared, 'nu_squared_GeV_squared')
    unit = _positive(energy_unit_GeV, 'energy_unit_GeV')
    return dict(nu_squared_chart=float(nu2/unit**2), energy_unit_GeV=unit,
        H_physical_from_chart='H_GeV=energy_unit_GeV*H_chart',
        canonical_momentum_physical_from_chart='p_H_GeV_inverse= p_H_chart/energy_unit_GeV',
        lambda_H_unchanged=True, physical_unit_owner_supplied_by_caller=True,
        native_cutoff_assigned=False)


def local_calibrated_higgs_radial_newton(*, fermi_constant_GeV_inverse_squared,
                                       higgs_mass_GeV, initial_fraction=.8,
                                       relative_residual_tolerance=1e-13,
                                       max_steps=16):
    """Solve the matched local tree broken-phase radial Euler equation.

    The flat local M4 reference cell has volume one in GeV coordinates.
    H=(0,h/sqrt(2)), where h is the unknown canonical real radial amplitude.
    This gauge orientation and positive broken branch belong to the stated
    electroweak matching approximation, not to an E1 scalar Cauchy condition.
    Classical J_body=0 is supplied by the existing odd-fermion body owner;
    quantum induced loads are not deleted or included in this tree solve.

    Each Newton residual and Jacobian comes from the existing literal Higgs
    weak applications.  Since the Lorentzian action contains -V, the weak
    radial Jacobian is -m_h^2 at the root; the potential curvature is +m_h^2.
    """
    gf = _positive(fermi_constant_GeV_inverse_squared, 'G_F')
    mh = _positive(higgs_mass_GeV, 'm_h')
    frac = _positive(initial_fraction, 'initial_fraction')
    tolerance = _positive(relative_residual_tolerance, 'relative_residual_tolerance')
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError('positive integer max_steps required')
    if frac <= 1/sqrt(3):
        raise ValueError('initial iterate must lie on the monotone positive broken-phase radial chart')
    v = (sqrt(2)*gf)**-.5
    nu2, lam = v*v/2, gf*mh*mh/sqrt(2)
    quad = np.ones(1)
    G = np.diag([1., -1., -1., -1.])[None]
    volume = np.ones(1)
    derivatives = np.zeros((1, 4, 2), complex)
    radial = np.array([[0., 1/sqrt(2)]], complex)
    body = classical_bosonic_body_source(1)
    fixed = dict(quadrature=quad, kinetic_density=G, volume_density=volume,
                 lambda_H=lam, nu_squared=nu2)

    def apply(h):
        field = h*radial
        residual = higgs_weak_residual(**fixed, H=field, DH=derivatives,
            J=body['J_H_body'], phi=radial, Dphi=derivatives)
        jacobian = realified_higgs_weak_jacobian(**fixed, H=field,
            test_values=radial[None], test_derivatives=derivatives[None],
            trial_values=radial[None], trial_derivatives=derivatives[None])[0, 0]
        return float(residual), float(jacobian)

    h = frac*v
    scale = mh*mh*v
    initial, _ = apply(h)
    history = []
    for step in range(max_steps):
        residual, jac = apply(h)
        if abs(residual)/scale <= tolerance:
            break
        if jac == 0:
            raise ArithmeticError('radial Newton tangent vanishes at the iterate')
        correction = -residual/jac
        damping = 1.
        # Preserve the declared positive broken branch and residual descent.
        for _ in range(32):
            candidate = h+damping*correction
            updated, _ = apply(candidate)
            if candidate > v/sqrt(3) and abs(updated) < abs(residual):
                break
            damping *= .5
        else:
            raise ArithmeticError('radial Newton correction failed to reduce the residual')
        history.append(dict(iteration=step, radial_h_before_GeV=h,
            initial_residual_GeV_cubed=residual, weak_jacobian_GeV_squared=jac,
            full_newton_correction_GeV=correction,
            accepted_correction_GeV=damping*correction, damping=damping,
            radial_h_after_GeV=candidate, updated_residual_GeV_cubed=updated))
        h = candidate
    final, tangent = apply(h)
    amplitude = h/sqrt(2)
    defect = amplitude*amplitude-nu2
    potential = lam*defect*defect
    converged = bool(abs(final)/scale <= tolerance)
    return dict(classification='CALIBRATED_TREE_LOCAL_BROKEN_VACUUM_ONLY',
        fermi_constant_GeV_inverse_squared=gf, higgs_mass_GeV=mh,
        lambda_H=lam, nu_squared_GeV_squared=nu2,
        represented_domain='FLAT_LOCAL_M4_UNIT_CELL; constant fields; no endpoint is prescribed',
        radial_parameter='canonical real h=sqrt(2)*a in H=(0,a)',
        gauge_orientation='positive neutral component, fixed within matched broken phase',
        initial_fraction=frac, initial_radial_h_GeV=frac*v,
        initial_weak_residual_GeV_cubed=initial, history=history,
        converged=converged, local_radial_h_GeV=h, local_neutral_amplitude_GeV=amplitude,
        final_weak_residual_GeV_cubed=final, normalized_final_weak_residual=abs(final)/scale,
        H_dagger_H_minus_nu_squared_GeV_squared=defect,
        local_potential_density_GeV_fourth=potential,
        final_weak_radial_jacobian_GeV_squared=tangent,
        potential_radial_curvature_GeV_squared=-tangent,
        matched_higgs_mass_squared_GeV_squared=mh*mh,
        classical_body_source_owner='muon_intrinsic_lepton_primal.classical_bosonic_body_source',
        quantum_induced_H_load_evaluated=False, quantum_effects_deleted=False,
        radiative_matching_error_bounded=False, full_prediction_uncertainty_established=False,
        current_E1_stationary_base_solved=False, physical_retarded_boundary_conditions_selected=False,
        mechanical_formation_section_selected=False, native_cutoff_assigned=False,
        full_native_pauli_evaluated=False, action_selected=False, Gate7_closed=False)


__all__ = ['FAMILIES', 'INPUT_ORDER', 'OUTPUT_ORDER', 'calibrated_tree_matching',
           'chiral_pole_denominator_application', 'higgs_scalar_action_unit_conversion',
           'local_calibrated_higgs_radial_newton']

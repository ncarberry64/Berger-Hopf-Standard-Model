"""Common mass/width clock equations on an action-produced unsquared pole.

Measured inputs are matching targets, not action coefficients or mode
selectors. One positive kappa rescales the real pole mass and its width
together. The pole and all parameter responses must already belong to the
same selected retarded domain; this module supplies no pole or exterior.
"""
from __future__ import annotations

import numpy as np


def semisimple_pole_parameter_response(kinetic, left, parameter_rows, right):
    """Return the full spin matrices -Z^-1 L Gamma_parameter R.

    Their traceless part is exported. Taking their trace is a diagnostic
    center derivative, not a proof that a varying spin doublet remains
    semisimple, degenerate or physically at rest.
    """
    Z, L, dG, R = (np.asarray(a, complex) for a in (kinetic, left, parameter_rows, right))
    if (Z.shape != (2, 2) or L.ndim != 2 or R.shape != (L.shape[1], 2)
            or L.shape[0] != 2 or dG.ndim != 3 or dG.shape[1:] != (L.shape[1], L.shape[1])
            or not len(dG) or any(not np.isfinite(a).all() for a in (Z, L, dG, R))):
        raise ValueError("same full action-boundary parameter rows and independent spin-doublet null frames required")
    H = np.array([-np.linalg.solve(Z, L @ a @ R) for a in dG])
    center = np.trace(H, axis1=-2, axis2=-1)/2
    traceless = H-center[:, None, None]*np.eye(2)
    return dict(full_pole_parameter_response=H, pole_center_parameter_response=center,
        pole_parameter_spin_splitting=traceless,
        scalar_center_derivative_is_not_a_spin_doublet_admission=True)


def common_pole_mass_width_clock_equations(pole_energy, *, clock_kappa,
        measured_mass, measured_lifetime, hbar, pole_center_parameter_first):
    """Apply kappa Re(Ep)=m and -2 kappa Im(Ep)=hbar/tau.

    This is the reached shared clock equation. No separate mass/lifetime
    rescaling, square spectral variable, width fit, internal Y retuning or
    anomaly datum is introduced. Parameter first jets are explicit and
    must come from the same Gamma equation; spin splitting admission remains
    the caller's additional original-row test.
    """
    E = complex(pole_energy)
    dE = np.asarray(pole_center_parameter_first, complex)
    k, m, tau, h = map(float, (clock_kappa, measured_mass, measured_lifetime, hbar))
    if (not np.isfinite(E) or E.real <= 0 or dE.ndim != 1 or not len(dE)
            or not np.isfinite(dE).all() or not all(np.isfinite(v) and v > 0 for v in (k, m, tau, h))):
        raise ValueError("positive common clock/mass/lifetime/hbar and finite same-domain pole/parameter jets required")
    observed_width = h/tau
    action_width = -2*E.imag
    residual = np.array((k*E.real-m, k*action_width-observed_width))
    parameter_jacobian = np.array((k*dE.real, -2*k*dE.imag))
    clock_column = np.array((E.real, action_width))
    width_mass_ratio = action_width/E.real
    ratio_first = -2*(dE.imag*E.real-E.imag*dE.real)/E.real**2
    return dict(original_common_mass_width_rows=residual,
        common_mass_width_parameter_jacobian=parameter_jacobian,
        common_mass_width_clock_column=clock_column,
        complete_parameter_and_clock_jacobian=np.column_stack((parameter_jacobian, clock_column)),
        width_mass_ratio_matching_row=np.array(width_mass_ratio-observed_width/m),
        width_mass_ratio_parameter_first=ratio_first,
        action_pole_mass=np.array(E.real), action_pole_width=np.array(action_width),
        matched_mass_clock_candidate=np.array(m/E.real),
        width_at_mass_clock_candidate=np.array((m/E.real)*action_width),
        mass_and_lifetime_share_one_positive_clock=True,
        separate_mass_width_unit_fit_or_Y_refit_used=False,
        interacting_pole_domain_or_parameter_root_selected=False,
        physical_Pauli_or_native_loop_normalization_inferred=False)

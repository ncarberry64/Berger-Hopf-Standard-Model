"""Canonical finite-core fermion body and current actions in geometry units.

This composes existing metric and angular-current data. It supplies a
parameterized free chiral propagation block, not a native quantum Pauli loop.
The mass parameter and Cauchy covariance are explicit calling operands.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm, expm_frechet


def hermitian(value, name):
    value = np.asarray(value, complex)
    if (value.ndim != 2 or value.shape[0] != value.shape[1]
            or not np.isfinite(value).all()
            or np.linalg.norm(value-value.conj().T) > 1e-12*max(1, np.linalg.norm(value))):
        raise ValueError(f"finite Hermitian {name} required")
    return value


def chiral_generators(spatial_dirac_unit):
    """H = R^-1 diag(-D3,+D3) + m sigma1_LR tensor I."""
    d = hermitian(spatial_dirac_unit, "unit spatial Dirac block")
    zeros, identity = np.zeros_like(d), np.eye(len(d))
    kinetic = np.block([[-d, zeros], [zeros, d]])
    mass = np.block([[zeros, identity], [identity, zeros]])
    return kinetic, mass


def photon_source_generators(spatial_currents, charge=-1.):
    """First derivative of B_H=i*d_tau-H for real gauge mode amplitudes.

    J is the Hermitian spatial sigma.A action on the retained spatial block.
    H_a = diag(Q*J,-Q*J), hence B_H,a = -H_a. Multiply by
    1/sqrt(2*pi^2*R^3) for the saved physical-volume mode convention.
    Photon residue/coupling normalization is not supplied here.
    """
    q = float(charge)
    if not np.isfinite(q):
        raise ValueError("finite conserved charge required")
    out = []
    for matrix in spatial_currents:
        j = hermitian(matrix, "real gauge current")
        zero = np.zeros_like(j)
        out.append(np.block([[-q*j, zero], [zero, q*j]]))
    return np.array(out)


def segment_generator(kinetic, mass, *, inverse_radius, duration, compatible_mass):
    """G=h H for one retained midpoint segment; m is in inverse clock units."""
    d, m = hermitian(kinetic, "kinetic generator"), hermitian(mass, "mass generator")
    inv, h, mu = map(float, (inverse_radius, duration, compatible_mass))
    if d.shape != m.shape or not all(np.isfinite([inv, h, mu])) or inv <= 0 or h < 0:
        raise ValueError("compatible generators, positive inverse radius and nonnegative duration required")
    return h*(inv*d+mu*m)


def segment_propagator(generator, generator_jet=None):
    """Exact midpoint-model exponential and optional source/direction jet."""
    g = hermitian(generator, "integrated Hamiltonian")
    if generator_jet is None:
        return expm(-1j*g)
    dg = hermitian(generator_jet, "integrated Hamiltonian jet")
    if dg.shape != g.shape:
        raise ValueError("matching generator jet required")
    return expm_frechet(-1j*g, -1j*dg, compute_expm=True)


def prefix_propagators(generators):
    """Ordered product; no periodic endpoint or frequency diagonalization."""
    generators = np.asarray(generators, complex)
    if generators.ndim != 3 or generators.shape[1] != generators.shape[2] or not len(generators):
        raise ValueError("nonempty square segment generators required")
    values = [np.eye(generators.shape[1], dtype=complex)]
    for generator in generators:
        values.append(segment_propagator(generator) @ values[-1])
    return np.array(values)


def retarded_kernel(u_later, u_source, later):
    """Kernel of i*d_tau-H in the canonical coefficient measure."""
    if not later:
        return np.zeros_like(u_later, dtype=complex)
    return -1j*np.asarray(u_later)@np.asarray(u_source).conj().T


def feynman_kernel(u_at_t, u_at_s, occupation_covariance, later):
    """C_ij=<chi_j^dagger chi_i> at the common initial Cauchy slice.

    No C is selected. For a valid covariance 0<=C<=I, the greater/lesser
    factors are I-C and C. A state change gives delta G_F=i U_t delta C U_s^dagger.
    Equal-time distribution conventions are a caller's concern.
    """
    c = hermitian(occupation_covariance, "Cauchy covariance")
    values = np.linalg.eigvalsh(c)
    if values[0] < -1e-12 or values[-1] > 1+1e-12:
        raise ValueError("fermion covariance must obey 0<=C<=I")
    left, right = np.asarray(u_at_t, complex), np.asarray(u_at_s, complex)
    if left.shape != c.shape or right.shape != c.shape:
        raise ValueError("matching propagation and covariance required")
    middle = -(np.eye(len(c))-c) if later else c
    return 1j*left@middle@right.conj().T


def fermion_body_data(geometry, angular):
    """Reusable coefficients and geometry jets; no mass or state selected.

    Geometry derivatives are inherited parent motions, NOT physical photon
    soft-transfer derivatives. The mass is held as a separate coefficient.
    The n0+n1 spatial truncation does not certify discarded current modes.
    """
    h, x = np.asarray(geometry["proper_durations"]), np.asarray(geometry["log_radius"])
    dx, dh = np.asarray(geometry["log_radius_first_jet"]), np.asarray(geometry["proper_durations_first_jet"])
    if len(x) != len(h)+1 or np.any(h <= 0) or not np.isfinite(x).all():
        raise ValueError("retained positive finite-core geometry required")
    midpoint = .5*(x[:-1]+x[1:])
    dmid = .5*(dx[:-1]+dx[1:])
    inverse = np.exp(-midpoint)
    d1 = np.kron(angular["D_round_n1_times_R_one_right_copy"], np.eye(2))
    d = np.zeros((10, 10), complex)
    d[:2, :2], d[2:, 2:] = 1.5*np.eye(2), d1
    js = []
    for current in angular["reduced_Weyl_angular_currents_real_gauge_basis"]:
        j = np.zeros_like(d)
        j[2:, :2], j[:2, 2:] = current, current.conj().T
        js.append(j)
    kinetic, mass = chiral_generators(d)
    # This factor belongs to physical-volume-normalized spatial test modes.
    volume_factor = np.exp(-1.5*midpoint)/np.sqrt(2*np.pi**2)
    return {
        "spatial_D3_unit": d, "kinetic_generator": kinetic,
        "mass_generator": mass, "spatial_real_current_generators": np.array(js),
        "B_H_photon_source_unit_generators_Q_minus_one": photon_source_generators(js),
        "inverse_radius": inverse, "proper_durations": h,
        "inverse_radius_geometry_jets": -inverse[:, None]*dmid,
        "integrated_kinetic_coefficients": h*inverse,
        "integrated_kinetic_coefficient_geometry_jets": inverse[:, None]*(dh-h[:, None]*dmid),
        "integrated_mass_coefficient_geometry_jets_per_unit_mass": dh,
        "volume_normalized_photon_source_factor": volume_factor,
        "volume_normalized_photon_source_factor_geometry_jets": -1.5*volume_factor[:, None]*dmid,
        "spinor_rescaling_R_three_halves": np.exp(1.5*x),
        "proper_times": np.asarray(geometry["proper_times"]),
        "birth_slice_Q72": np.asarray(geometry["birth_slice_Q72"]),
    }

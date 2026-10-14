"""Keep dispersive and absorptive slopes of a supplied spin-doublet pole.

The original unsquared-boundary module already returns the complex matrix
H_B=-Z^-1 L Gamma_B R. This diagnostic never supplies that matrix, a pole,
external modes, an EM normalization, or a magnetic moment. In particular a
trace-centered approximate root is not admitted as a physical pole here.
"""
from __future__ import annotations

import numpy as np


def pole_slope_invariants(parameter_response):
    """Basis-invariant, unordered first slopes for a supplied 2x2 response.

    For E=M-i*Gamma/2, Re(dE) is an energy slope and -2Im(dE) is a width
    slope. If the parameter is a magnetic probe, identifying a moment still
    requires its physical field units, spin orientation and same-domain
    normalized external modes. No imaginary component is discarded.
    """
    h = np.asarray(parameter_response, complex)
    if h.shape != (2, 2) or not np.isfinite(h).all():
        raise ValueError('one finite supplied spin-doublet response matrix required')
    center = np.trace(h)/2
    determinant = np.linalg.det(h)
    discriminant = center*center-determinant
    half = np.sqrt(complex(discriminant))
    slopes = np.asarray([center+half, center-half])
    traceless = h-center*np.eye(2)
    return dict(complex_response=h.copy(), complex_center=center,
                complex_determinant=determinant,
                half_splitting_squared=discriminant,
                unordered_complex_pole_slopes=slopes,
                unordered_energy_slopes=slopes.real.copy(),
                unordered_width_slopes=-2*slopes.imag,
                traceless_response=traceless,
                characteristic_rows=slopes*slopes-2*center*slopes+determinant,
                imaginary_parts_discarded=False,
                pole_or_analytic_branch_admitted=False,
                physical_magnetic_moment=None)

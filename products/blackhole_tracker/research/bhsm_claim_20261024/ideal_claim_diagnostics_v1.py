"""Ideal invented-input algebra for the BHSM claim dossier.

Not a native-data adapter, likelihood, fit, error model, classifier or package
extension. Positive contrasts do not identify BHs or a microscopic surface.
"""
import math


def _finite(value, name, *, positive=False, nonnegative=False):
    if type(value) not in (int, float):
        raise ValueError(name + ' must be a builtin real number, not bool')
    try:
        result = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(name + ' is not representable') from error
    if not math.isfinite(result):
        raise ValueError(name + ' must be finite')
    if positive and result <= 0:
        raise ValueError(name + ' must be positive')
    if nonnegative and result < 0:
        raise ValueError(name + ' must be nonnegative')
    return result


def annular_contrast(r1, r2, alpha1, alpha2):
    """C=R2*alpha2-R1*alpha1; supplied ideal physical bending magnitudes.

    All radii must share a length unit and both angles a consistent unit.
    No covariance, gravitational-origin validation or significance is added.
    """
    r1 = _finite(r1, 'r1', positive=True)
    r2 = _finite(r2, 'r2', positive=True)
    alpha1 = _finite(alpha1, 'alpha1', positive=True)
    alpha2 = _finite(alpha2, 'alpha2', positive=True)
    if r2 <= r1:
        raise ValueError('Distinct ordered radii r2>r1 required')
    products = (r1 * alpha1, r2 * alpha2)
    if not all(math.isfinite(value) and value > 0 for value in products):
        raise ValueError('Numerical product overflow/underflow unresolved')
    contrast = math.fsum((-products[0], products[1]))
    if not math.isfinite(contrast):
        raise ValueError('Numerical contrast unresolved')
    return {
        'contrast': contrast,
        'gradient_order': ['r1', 'r2', 'alpha1', 'alpha2'],
        'gradient': [-alpha1, alpha2, -r1, r2],
        'uncertainty': None,
        'classification': None,
        'scope': 'IDEAL_MODEL_MOMENT_CONTRAST_ONLY',
    }


def principal_reference_deficit(m, radius):
    """Static dimensionless m=GM/c^2; radius in matching length units.

    Return the one-principal flat-reference deficit of the same exterior.
    A positive result is not a physical junction, spin or BH classification.
    """
    m = _finite(m, 'm', nonnegative=True)
    radius = _finite(radius, 'radius', positive=True)
    twice_m = 2 * m
    if not math.isfinite(twice_m) or radius <= twice_m:
        raise ValueError('Finite static exterior radius>2m required')
    ratio = twice_m / radius
    if m > 0 and ratio == 0:
        raise ValueError('Nonzero compactness underflow unresolved')
    f = 1 - ratio
    if f <= 0:
        raise ValueError('Static branch unresolved in floating arithmetic')
    # Rationalize 1-sqrt(f) to avoid cancellation at low compactness.
    deficit = (ratio / radius) / (1 + math.sqrt(f))
    if not math.isfinite(deficit) or (m > 0 and deficit == 0):
        raise ValueError('Nonzero deficit underflow/overflow unresolved')
    return deficit


def ideal_slip_residual(alpha_radians, speed, c, independently_fixed_slip):
    """Ideal full-line log-potential identity only, never a fitted slip.

    speed and c share velocity units. Real finite-galaxy/LOS/truncation,
    density, inclination and source bridges are outside this algebra.
    """
    alpha = _finite(alpha_radians, 'alpha_radians', nonnegative=True)
    speed = _finite(speed, 'speed', positive=True)
    c = _finite(c, 'c', positive=True)
    slip = _finite(independently_fixed_slip, 'slip')
    beta = speed / c
    squared = beta * beta
    denominator = math.pi * squared
    if not math.isfinite(denominator) or denominator <= 0:
        raise ValueError('Velocity normalization overflow/underflow unresolved')
    residual = alpha / denominator - (1 + slip)
    if not math.isfinite(residual):
        raise ValueError('Ideal closure residual unresolved')
    return residual

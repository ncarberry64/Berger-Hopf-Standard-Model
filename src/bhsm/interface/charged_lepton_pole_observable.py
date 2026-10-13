"""Compose admitted dressed poles with the existing charged-lepton invariant.

The universal pole engine uses z=m_p**2-i*m_p*Gamma_p.  Its output does not
carry family, domain, or scale labels, so those labels are explicit here.
This consumer selects no modes, computes no self-energy, and promotes no
current BHSM prediction.  Covariance is supplied in full, including all
cross-family correlations; it is never inferred from separate error bars.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, pi, sqrt
from typing import Any, Sequence

import numpy as np

from bhsm.interface.ae31_charged_lepton_pole_dressing_invariant import (
    DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT,
    pole_dressing_invariant_theorem,
)
from bhsm.interface.universal_dressed_pole import DressedPole


SPECTRAL_CONVENTION = "z=m_p^2-i*m_p*Gamma_p"
FAMILY_ROLES = tuple(pole_dressing_invariant_theorem()["roles"])
_CONTRAST = np.asarray([[-1.0, 1.0, 0.0], [-1.0, 0.0, 1.0]])
_CONTRAST_COEFFICIENTS = np.asarray([-9.0, 1.0])


@dataclass(frozen=True)
class ChargedLeptonPoleInput:
    """An existing pole bound to an action-selected family and scale map.

    ``domain_id`` identifies the common physical variational domain, not an
    identical family eigenvector. ``scale_map_id`` includes the mass unit
    and its conversion convention. The labels must come from the producer;
    adding them here does not prove that the producer has selected them.
    """

    family_role: str
    pole: DressedPole
    domain_id: str
    scale_map_id: str
    spectral_convention: str = SPECTRAL_CONVENTION


def _label(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"nonempty {name} provenance is required")


def _admit_input(record: ChargedLeptonPoleInput, tolerance: float) -> None:
    if not isinstance(record, ChargedLeptonPoleInput):
        raise TypeError("each family input must be a ChargedLeptonPoleInput")
    if record.family_role not in FAMILY_ROLES:
        raise ValueError("explicit tau_slot, mu_slot, and electron_slot roles required")
    for name in ("domain_id", "scale_map_id", "spectral_convention"):
        _label(getattr(record, name), name)
    if record.spectral_convention != SPECTRAL_CONVENTION:
        raise ValueError("only the existing squared spectral convention is compatible")
    pole = record.pole
    if not isinstance(pole, DressedPole):
        raise TypeError("the consumer requires existing DressedPole outputs")
    _label(pole.action_version, "action_version")
    _label(pole.background_id, "background_id")
    if not pole.provenance or isinstance(pole.provenance, str):
        raise ValueError("nonempty pole producer provenance is required")
    for pin in pole.provenance:
        _label(pin, "pole producer")
    numerical = (
        pole.spectral_parameter, pole.pole_mass, pole.pole_width,
        pole.relative_symbol_residual, pole.descriptor_derivative_normalization,
    )
    if not np.all(np.isfinite(numerical)):
        raise ValueError("finite pole readout, residual, and residue normalization required")
    if pole.pole_mass <= 0.0 or pole.pole_width < 0.0:
        raise ValueError("positive mass and nonnegative width required")
    if pole.relative_symbol_residual < 0.0:
        raise ValueError("pole residual cannot be negative")
    right, left, residue = (
        np.asarray(pole.right_mode), np.asarray(pole.left_mode),
        np.asarray(pole.residue),
    )
    if (right.ndim != 1 or right.size == 0 or left.shape != right.shape
            or residue.shape != (right.size, right.size)
            or any(not np.all(np.isfinite(a)) for a in (right, left, residue))):
        raise ValueError("finite compatible left/right pole modes and residue required")
    if abs(pole.descriptor_derivative_normalization) <= tolerance:
        raise ValueError("nonzero pole derivative normalization required")
    squared_mass = pole.pole_mass * pole.pole_mass
    if not np.isfinite(squared_mass) or not np.isclose(
        pole.spectral_parameter.real, squared_mass, rtol=tolerance, atol=0.0,
    ):
        raise ValueError("pole mass does not match the declared squared spectral convention")
    expected_imaginary = -pole.pole_mass * pole.pole_width
    # The existing solver may clamp a negative width within its tolerance.
    if not np.isclose(
        pole.spectral_parameter.imag, expected_imaginary,
        rtol=tolerance, atol=tolerance * max(1.0, abs(pole.spectral_parameter)),
    ):
        raise ValueError("pole width does not match the declared squared spectral convention")
    pole.require_physical_promotion(tolerance=tolerance)


def _covariance(values: Sequence[Sequence[float]]) -> np.ndarray:
    raw = np.asarray(values)
    if np.iscomplexobj(raw):
        raise ValueError("real covariance required")
    matrix = np.asarray(raw, dtype=float)
    if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
        raise ValueError("finite complete 3 x 3 covariance required")
    if not np.array_equal(matrix, matrix.T):
        raise ValueError("covariance must be explicitly symmetric")
    diagonal = np.diag(matrix)
    if np.any(diagonal < 0.0):
        raise ValueError("covariance must be positive semidefinite")
    zero = diagonal == 0.0
    if np.any(matrix[zero] != 0.0):
        raise ValueError("zero-variance covariance rows must vanish")
    positive = ~zero
    if np.any(positive):
        scales = np.sqrt(diagonal[positive])
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            correlation = matrix[np.ix_(positive, positive)] / np.outer(scales, scales)
        if not np.all(np.isfinite(correlation)):
            raise ValueError("finite covariance correlations required")
        roundoff = 64.0 * np.finfo(float).eps
        if np.linalg.eigvalsh(correlation)[0] < -roundoff:
            raise ValueError("covariance must be positive semidefinite")
    return matrix


def charged_lepton_pole_observable(
    inputs: Sequence[ChargedLeptonPoleInput],
    *,
    covariance: Sequence[Sequence[float]],
    covariance_coordinates: str,
    tolerance: float = 1.0e-10,
) -> dict[str, Any]:
    """Read R and exp(R), propagating the supplied correlated covariance.

    Covariance rows follow ``inputs``; both are reordered together into
    heavy/middle/light family order. In ``log_mass`` coordinates R is affine,
    so its variance is exact for the declared log-mass covariance. In
    ``mass`` coordinates the variance uses the first-order delta method.
    Neither covariance nor the reported standard deviation is an outward
    numerical error bound. All existing pole promotion gates must pass.
    """

    if not np.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("positive finite pole admission tolerance required")
    records = tuple(inputs)
    if len(records) != 3:
        raise ValueError("exactly three explicit charged-lepton family poles required")
    for record in records:
        _admit_input(record, tolerance)
    by_role = {record.family_role: index for index, record in enumerate(records)}
    if set(by_role) != set(FAMILY_ROLES):
        raise ValueError("each charged-lepton family role must occur exactly once")
    if covariance_coordinates not in ("mass", "log_mass"):
        raise ValueError("covariance_coordinates must be mass or log_mass")
    owners = {
        (record.pole.action_version, record.pole.background_id,
         record.domain_id, record.scale_map_id, record.spectral_convention)
        for record in records
    }
    if len(owners) != 1:
        raise ValueError("same action/background/domain/scale/convention required")
    order = [by_role[role] for role in FAMILY_ROLES]
    ordered = [records[index] for index in order]
    matrix = _covariance(covariance)[np.ix_(order, order)]
    masses = np.asarray([record.pole.pole_mass for record in ordered])
    log_masses = np.asarray([log(mass) for mass in masses])
    coefficients = DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT
    mass_gradient = coefficients / masses
    if not np.all(np.isfinite(mass_gradient)):
        raise ValueError("finite mass Jacobian required")
    # Differences remove the common logarithmic scale before contraction.
    residual = float(_CONTRAST_COEFFICIENTS @ (_CONTRAST @ log_masses) - 54.0 / pi)
    try:
        invariant = exp(residual)
    except OverflowError as error:
        raise ValueError("finite multiplicative dressing invariant required") from error
    if invariant == 0.0:
        raise ValueError("multiplicative dressing invariant underflows this numerical readout")
    if covariance_coordinates == "mass":
        log_covariance = matrix / np.outer(masses, masses)
        variance_method = "FIRST_ORDER_DELTA_METHOD_FROM_MASS_COVARIANCE"
    else:
        log_covariance = matrix
        variance_method = "EXACT_AFFINE_RESIDUAL_FROM_LOG_MASS_COVARIANCE"
    if not np.all(np.isfinite(log_covariance)):
        raise ValueError("finite log-mass covariance required after coordinate conversion")
    # Contrasts cancel an exactly shared log-scale covariance before norms.
    contrast_covariance = _CONTRAST @ log_covariance @ _CONTRAST.T
    variance = float(_CONTRAST_COEFFICIENTS @ contrast_covariance @ _CONTRAST_COEFFICIENTS)
    roundoff = 64.0 * np.finfo(float).eps * float(
        np.sum(np.abs(coefficients[:, None] * log_covariance * coefficients[None, :]))
    )
    if not np.isfinite(variance) or not np.isfinite(roundoff) or variance < -roundoff:
        raise ValueError("invalid negative or nonfinite propagated variance")
    roundoff_clamped = variance < 0.0
    variance = max(variance, 0.0)
    invariant_standard_deviation = invariant * sqrt(variance)
    invariant_variance = invariant_standard_deviation * invariant_standard_deviation
    if not np.isfinite(invariant_variance):
        raise ValueError("finite first-order invariant variance required")
    owner = ordered[0]
    return {
        "classification": "CONDITIONAL_ALGEBRAIC_READOUT_FROM_SUPPLIED_DRESSED_POLES",
        "family_roles_heavy_middle_light": list(FAMILY_ROLES),
        "action_version": owner.pole.action_version,
        "background_id": owner.pole.background_id,
        "domain_id": owner.domain_id,
        "scale_map_id": owner.scale_map_id,
        "spectral_convention": owner.spectral_convention,
        "pole_provenance_heavy_middle_light": [list(record.pole.provenance) for record in ordered],
        "pole_masses_heavy_middle_light": masses.tolist(),
        "dressed_sum_rule_residual": residual,
        "multiplicative_dressing_invariant": invariant,
        "mass_jacobian_heavy_middle_light": mass_gradient.tolist(),
        "log_mass_jacobian_heavy_middle_light": coefficients.tolist(),
        "covariance_coordinates": covariance_coordinates,
        "covariance_heavy_middle_light": matrix.tolist(),
        "residual_variance": variance,
        "residual_standard_deviation": sqrt(variance),
        "residual_variance_method": variance_method,
        "invariant_variance_first_order": invariant_variance,
        "variance_roundoff_clamped_to_zero": roundoff_clamped,
        "variance_roundoff_allowance": roundoff,
        "common_log_scale_jacobian": float(np.sum(coefficients)),
        "cross_family_covariances_retained": True,
        "covariance_is_outward_error_bound": False,
        "existing_pole_promotion_gates_passed": True,
        "family_or_mode_selection_performed": False,
        "empirical_reference_used": False,
        "current_bhsm_physical_prediction_promoted": False,
    }


__all__ = [
    "ChargedLeptonPoleInput", "FAMILY_ROLES", "SPECTRAL_CONVENTION",
    "charged_lepton_pole_observable",
]

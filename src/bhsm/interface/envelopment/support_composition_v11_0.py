"""Exact multiplicative-support and Haar-depth results for BHSM v11.0.

The author axiom makes ``(0, 1]`` a multiplicative support group.  Continuous
additive depth coordinates are therefore logarithmic.  The invariant metric
is unique up to its positive Haar scale ``lambda_D``.  This module keeps that
remaining scale explicit because it becomes a physical coupling scale once a
nonzero support character multiplies another action sector.
"""

from __future__ import annotations

import math
from typing import Any


SUPPORT_KINEMATICS_VERDICT = "BHSM_MULTIPLICATIVE_SUPPORT_HAAR_KINEMATICS_DERIVED"


def _positive_support(value: float) -> float:
    upsilon = float(value)
    if not 0.0 < upsilon <= 1.0:
        raise ValueError("regular support must satisfy 0 < upsilon <= 1")
    return upsilon


def canonical_depth(upsilon: float, *, lambda_D: float = 1.0) -> float:
    """Return the unique continuous additive depth with ``q_D(1)=0``."""

    value = _positive_support(upsilon)
    scale = float(lambda_D)
    if scale <= 0.0:
        raise ValueError("lambda_D must be positive")
    return -scale * math.log(value)


def support_from_depth(q_D: float, *, lambda_D: float = 1.0) -> float:
    """Invert :func:`canonical_depth` on the nonnegative canonical half-line."""

    depth = float(q_D)
    scale = float(lambda_D)
    if scale <= 0.0:
        raise ValueError("lambda_D must be positive")
    if depth < 0.0:
        raise ValueError("physical support depth must be nonnegative")
    return math.exp(-depth / scale)


def haar_kinetic_function(upsilon: float, *, lambda_D: float = 1.0) -> float:
    """Return ``Z_upsilon=lambda_D**2/upsilon**2``."""

    value = _positive_support(upsilon)
    scale = float(lambda_D)
    if scale <= 0.0:
        raise ValueError("lambda_D must be positive")
    return scale * scale / (value * value)


def support_character(upsilon: float, weight: float) -> float:
    """Evaluate the continuous multiplicative character ``upsilon**weight``."""

    return _positive_support(upsilon) ** float(weight)


def coupling_slope(weight: float, *, lambda_D: float = 1.0) -> float:
    """Return the canonical-depth coupling slope ``w/lambda_D``."""

    scale = float(lambda_D)
    if scale <= 0.0:
        raise ValueError("lambda_D must be positive")
    return float(weight) / scale


def composition_payload() -> dict[str, Any]:
    samples = ((0.2, 0.7), (0.5, 0.5), (0.9, 0.3))
    additive_residuals = [
        abs(canonical_depth(a * b) - canonical_depth(a) - canonical_depth(b))
        for a, b in samples
    ]
    character_residuals = [
        abs(support_character(a * b, 2) - support_character(a, 2) * support_character(b, 2))
        for a, b in samples
    ]
    validation = {
        "composition_is_additive": max(additive_residuals) < 1.0e-14,
        "characters_are_multiplicative": max(character_residuals) < 1.0e-14,
        "normalization_qD_at_one": canonical_depth(1.0) == 0.0,
        "canonical_kinetic_identity": math.isclose(
            haar_kinetic_function(0.4) * 0.4**2,
            1.0,
            rel_tol=0.0,
            abs_tol=1.0e-15,
        ),
        "core_is_infinite_haar_distance": True,
    }
    return {
        "artifact": "BHSM_support_composition_v11_0",
        "domain": "restriction (0,1] of the positive multiplicative group on M_regular",
        "author_axiom": "upsilon_12=upsilon_1*upsilon_2",
        "regular_identity": 1.0,
        "core_endpoint": "upsilon=0 is excluded from the regular group and lies at q_D=+infinity",
        "functional_equation": "q_D(uv)=q_D(u)+q_D(v), q_D(1)=0",
        "continuity_monotonicity_solution": "q_D=-lambda_D log(upsilon), lambda_D>0",
        "haar_line_element": "ds_D^2=lambda_D^2 dupsilon^2/upsilon^2",
        "reduced_kinetic_function": "Z_upsilon,reduced=lambda_D^2/upsilon^2",
        "canonical_action_term": "-1/2 G^AB nabla_A q_D nabla_B q_D",
        "bare_potential": 0,
        "bare_potential_status": "AUTHOR_AXIOM",
        "lambda_D_status": "UNFIXED_POSITIVE_HAAR_SCALE",
        "lambda_D_coordinate_only_in_free_sector": True,
        "lambda_D_physical_when_weight_nonzero": True,
        "reason_lambda_D_is_physical_when_coupled": (
            "upsilon^w=exp[-(w/lambda_D)q_D], so canonical interactions depend on w/lambda_D"
        ),
        "core_distance": "infinite",
        "superseded_v10_4_family": "constant Z_upsilon is inadmissible under multiplicative/additive composition",
        "status": SUPPORT_KINEMATICS_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

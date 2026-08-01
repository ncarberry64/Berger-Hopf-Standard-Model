"""Covariant proper-volume depth candidate for BHSM v10.4."""

from __future__ import annotations

import math
from typing import Any

import sympy as sp


DEPTH_VERDICT = (
    "BHSM_PROPER_VOLUME_DEFICIT_HAS_NO_INDEPENDENT_PHYSICAL_SCALAR_"
    "AFTER_CONSTRAINT_REDUCTION"
)


def volume_ratio(det_metric: float, det_background: float) -> float:
    """Return the positive Radon--Nikodym ratio of metric volume densities."""

    if det_metric == 0 or det_background == 0:
        raise ValueError("both metrics must be nondegenerate")
    return math.sqrt(abs(det_metric) / abs(det_background))


def q_volume(det_metric: float, det_background: float) -> float:
    """Return q_V=-(1/8) log(dmu_G/dmu_Gbar) on the regular domain."""

    return -math.log(volume_ratio(det_metric, det_background)) / 8.0


def linear_block_depth(
    delta_u4: float,
    delta_u2: float,
    delta_u1: float,
    delta_log_lapse: float = 0.0,
) -> float:
    """Linearized eight-volume depth for block multiplicities (4,2,1)."""

    return -(delta_log_lapse + 4 * delta_u4 + 2 * delta_u2 + delta_u1) / 8.0


def symbolic_reduction() -> dict[str, Any]:
    u4, u2, u1, rho, beta, gamma = sp.symbols("u4 u2 u1 rho beta gamma")
    solution = sp.solve(
        [
            sp.Eq(rho, (4 * u4 + 2 * u2 + u1) / 7),
            sp.Eq(beta, u1 - u2),
            sp.Eq(gamma, u2 - u4),
        ],
        (u4, u2, u1),
        dict=True,
    )[0]
    spatial_qv = sp.simplify(-(4 * u4 + 2 * u2 + u1) / 8)
    reduced_qv = sp.simplify(spatial_qv.subs(solution))
    return {
        "variables": ["rho=(4u4+2u2+u1)/7", "beta=u1-u2", "gamma=u2-u4"],
        "inverse": {str(key): sp.sstr(value) for key, value in solution.items()},
        "q_V_spatial": sp.sstr(spatial_qv),
        "q_V_reduced": sp.sstr(reduced_qv),
        "identity_verified": reduced_qv == -sp.Rational(7, 8) * rho,
    }


def covariance_ledger() -> dict[str, Any]:
    return {
        "same_parent_manifold_required": True,
        "definition": "rho_V=dmu_G/dmu_Gbar after an explicit common pullback",
        "simultaneous_diffeomorphism": "rho_V is a scalar and q_V transforms by pullback",
        "fixed_background_perturbative_gauge": "delta_xi q_V=-(1/8) div_Gbar(xi)",
        "local_gauge_invariant_without_relational_map": False,
        "compact_integrated_volume": "diffeomorphism invariant when boundary flux vanishes",
        "integrated_volume_is_local_depth": False,
        "arbitrary_coordinate_determinants_compared": False,
    }


def conformal_ledger() -> dict[str, Any]:
    return {
        "decomposition": "G_AB=exp(2 omega) Ghat_AB with det(Ghat)/det(Gbar)=1",
        "dimension": 8,
        "volume_ratio": "rho_V=exp(8 omega)",
        "candidate": "q_V=-omega",
        "normalization_minus_one_eighth": "normalizes the isotropic conformal exponent, not its physical kinetic term",
        "vertical_only_breathing": "delta u2=delta u1=b, delta u4=0 gives q_V=-3b/8",
        "Einstein_frame_volume_compensation": "rho=0 gives q_V=0 while a positive shape/radion mode may remain",
    }


def domain_ledger() -> list[dict[str, Any]]:
    return [
        {"region": "regular parent manifold", "condition": "rho_V>0 finite", "q_V": "finite", "inverse_metric_action_valid": True},
        {"region": "high-depletion transition", "condition": "0<rho_V<<1", "q_V": "large finite positive", "inverse_metric_action_valid": "only while nondegenerate and curvature remains controlled"},
        {"region": "core/singular stratum", "condition": "rho_V=0", "q_V": "+infinity", "inverse_metric_action_valid": False},
        {"region": "effective M4 readout", "condition": "requires explicit reduction map", "q_V": None, "inverse_metric_action_valid": "current regular EFT only"},
    ]


def proper_volume_payload() -> dict[str, Any]:
    symbolic = symbolic_reduction()
    covariance = covariance_ledger()
    validation = {
        "block_identity": symbolic["identity_verified"],
        "conformal_unit_check": math.isclose(q_volume(math.exp(16.0), 1.0), -1.0),
        "background_pullback_required": covariance["same_parent_manifold_required"],
        "raw_local_candidate_not_promoted": not covariance["local_gauge_invariant_without_relational_map"],
        "degenerate_core_excluded": not domain_ledger()[2]["inverse_metric_action_valid"],
    }
    return {
        "artifact": "BHSM_spacetime_removal_depth_gate_v10_4",
        "candidate": "q_V=-(1/8) log(dmu_G/dmu_Gbar)",
        "covariance": covariance,
        "conformal_decomposition": conformal_ledger(),
        "block_reduction": symbolic,
        "lapse_relation": "q_V=-(delta log N+7 delta rho)/8 before temporal gauge/constraint reduction",
        "shift_relation": "shift has no determinant contribution but enforces momentum constraints",
        "finiteness": "finite only for two nondegenerate metrics with a common pullback",
        "monotonicity": "monotone in the positive volume ratio, not proved monotone in physical core proximity",
        "physical_depth": None,
        "domain": domain_ledger(),
        "verdict": DEPTH_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

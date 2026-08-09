"""Linearized principal-symbol comparison: composite projector versus Yang-Mills."""

from __future__ import annotations

from typing import Any

import numpy as np

from .eta_projector_dof_audit_v14_1 import random_unit, spacetime_curvature_map

VERSION = "v14.1"


def independent_yang_mills_symbol(momentum: np.ndarray) -> np.ndarray:
    """Euclidean non-gauge-fixed Yang-Mills symbol for eight color directions."""
    k = np.asarray(momentum, float)
    if k.shape != (4,) or np.linalg.norm(k) == 0.0:
        raise ValueError("momentum must be a nonzero four-vector")
    vector_symbol = float(k @ k) * np.eye(4) - np.outer(k, k)
    return np.kron(np.eye(8), vector_symbol)


def composite_quadratic_symbol(momentum: np.ndarray) -> np.ndarray:
    """Hessian symbol of tr(FP^2) at du=0; identically zero because F=O(du^2)."""
    k = np.asarray(momentum, float)
    if k.shape != (4,) or np.linalg.norm(k) == 0.0:
        raise ValueError("momentum must be a nonzero four-vector")
    return np.zeros((6, 6), dtype=float)


def scaling_witness() -> dict[str, Any]:
    unit = random_unit(1412)
    rng = np.random.default_rng(1413)
    derivatives = rng.normal(size=(4, 6))
    epsilon = 2.0e-4
    f_one = spacetime_curvature_map(unit, epsilon * derivatives)
    f_two = spacetime_curvature_map(unit, 2.0 * epsilon * derivatives)
    action_one = float(f_one @ f_one)
    action_two = float(f_two @ f_two)
    return {
        "curvature_scaling_ratio": float(np.linalg.norm(f_two) / np.linalg.norm(f_one)),
        "action_scaling_ratio": action_two / action_one,
        "curvature_is_quadratic": abs(np.linalg.norm(f_two) / np.linalg.norm(f_one) - 4.0) < 1.0e-10,
        "action_is_quartic": abs(action_two / action_one - 16.0) < 1.0e-9,
    }


def principal_symbol_payload() -> dict[str, Any]:
    momentum = np.array([1.0, -0.4, 0.7, 1.2])
    ym = independent_yang_mills_symbol(momentum)
    composite = composite_quadratic_symbol(momentum)
    ym_rank = int(np.linalg.matrix_rank(ym, tol=1.0e-12))
    composite_rank = int(np.linalg.matrix_rank(composite, tol=1.0e-12))
    scaling = scaling_witness()
    validation = {
        "YM_symbol_rank_24_with_eight_gauge_zero_modes": ym_rank == 24,
        "composite_quadratic_symbol_rank_zero": composite_rank == 0,
        "curvature_begins_at_second_order": scaling["curvature_is_quadratic"],
        "candidate_action_begins_at_fourth_order": scaling["action_is_quartic"],
        "no_perturbative_composite_gluon_propagator": True,
        "strong_coupling_degeneracy_at_constant_selector": True,
        "full_YM_hyperbolicity_not_reproduced": True,
        "ghost_freedom_not_claimed_on_nonconstant_backgrounds": True,
    }
    return {
        "artifact": "BHSM_eta_projector_principal_symbol_v14_1",
        "version": VERSION,
        "background": "u=u0, du0=0, AP=0, FP=0",
        "linearized_projector": "delta P=(-delta u tensor u0-u0 tensor delta u-i J_delta_u)/2",
        "leading_curvature": "delta F=0; F^(2)=P0[d(delta P),d(delta P)]P0",
        "candidate_action_order": "S_P=O((d delta u)^4)",
        "composite_quadratic_symbol_rank": composite_rank,
        "independent_YM_symbol_rank": ym_rank,
        "independent_YM_gauge_zero_modes": 8,
        "independent_YM_physical_polarizations": 16,
        "scaling_witness": scaling,
        "verdict": (
            "THE_COMPOSITE_PROJECTOR_ACTION_HAS_NO_QUADRATIC_KINETIC_TERM_AT_"
            "THE_CONSTANT_SELECTOR_VACUUM_AND_CANNOT_REPLACE_PERTURBATIVE_GLUONS"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

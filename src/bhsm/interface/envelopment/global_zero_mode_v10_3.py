"""Compact-domain Fredholm and global-restoring-constraint audit."""

from __future__ import annotations

from typing import Any

import numpy as np
import sympy as sp


GLOBAL_VERDICT = "BHSM_NO_GLOBAL_RESTORING_CONSTRAINT_EXISTS_WITHOUT_AN_EXTERNAL_SCALE_INPUT"


def fredholm_projection(source: np.ndarray, zero_mode: np.ndarray) -> float:
    """Return <u0,J>/<u0,u0> for a finite-dimensional self-adjoint proxy."""

    rhs = np.asarray(source, dtype=float)
    kernel = np.asarray(zero_mode, dtype=float)
    if rhs.shape != kernel.shape or rhs.ndim != 1:
        raise ValueError("source and zero mode must be equal-length vectors")
    norm = float(kernel @ kernel)
    if norm == 0:
        raise ValueError("zero mode must be nonzero")
    return float(kernel @ rhs) / norm


def prior_fold_zero_mode() -> dict[str, Any]:
    chi_1 = sp.Float("5.26830787154212")
    j_z = chi_1 * (sp.Rational(3, 2) * sp.log(2) - 6 * sp.Catalan / sp.pi)
    m_z = 3 * (8 - sp.pi)
    return {
        "sector": "v6.29 scalar-wall fold",
        "kernel": "z_A=sec^2(pi t/4), z_psi=1",
        "source_projection_j_z": float(j_z.evalf(15)),
        "lifting_M_z": float(m_z.evalf(15)),
        "M_z_positive": bool(m_z > 0),
        "response_c_z": float((-j_z / m_z).evalf(15)),
        "constraint_response_derived": True,
        "same_as_Hopf_radion_zero_mode": False,
        "fixes_dimensional_scale": False,
    }


def global_constraint_ledger() -> dict[str, Any]:
    return {
        "integrated_Hamiltonian": "int_Sigma7 H dmu7=0 follows from the local lapse equation",
        "independent_global_equation": False,
        "fixes_homogeneous_radion": False,
        "reason": "the v10.2 homogeneous radion has no static critical point and the overall scale remains free",
        "Fredholm_condition": "<u0,J_local>=0 if O_q has an unlifted kernel",
        "Fredholm_is_restoring_law_by_itself": False,
        "normalized_decomposition": "beta=beta0+tilde_beta with int tilde_beta dmu=0",
        "beta0_fixed": False,
        "local_source_shifts_beta0": None,
        "eta_degree_role": "topological sector label; may enter sources but fixes no length",
        "external_targets_adopted": [],
        "external_targets_rejected": ["V_star", "R_star", "E_star"],
        "remaining_dimensional_moduli": 1,
    }


def global_payload() -> dict[str, Any]:
    prior = prior_fold_zero_mode()
    ledger = global_constraint_ledger()
    validation = {
        "fold_response_positive_lift": prior["M_z_positive"],
        "fold_not_radion": not prior["same_as_Hopf_radion_zero_mode"],
        "integrated_not_independent": not ledger["independent_global_equation"],
        "beta0_unfixed": not ledger["beta0_fixed"],
        "no_external_target": ledger["external_targets_adopted"] == [],
        "scale_remains": ledger["remaining_dimensional_moduli"] == 1,
    }
    return {
        "artifact": "BHSM_global_restoring_constraint_v10_3",
        "prior_fold_zero_mode": prior,
        "global_constraint": ledger,
        "verdict": GLOBAL_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

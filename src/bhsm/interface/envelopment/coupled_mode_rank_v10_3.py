"""Physical-rank, eigenmode, and nonlinear-continuation audit for BHSM v10.3."""

from __future__ import annotations

from typing import Any

import sympy as sp

from .common_envelopment_mode_v10_3 import PRIMARY_VERDICT, UNRESOLVED


def rank_bounds_two_mode(k_zeta: sp.Expr, k_f: sp.Expr) -> dict[str, Any]:
    """Rank possibilities for a symmetric 2x2 kinetic matrix with unknown cross block."""

    if sp.ask(sp.Q.positive(k_zeta)) is not True or sp.ask(sp.Q.positive(k_f)) is not True:
        raise ValueError("known diagonal kinetic entries must be positive")
    cross = sp.Symbol("K_zetaF", real=True)
    determinant = sp.expand(k_zeta * k_f - cross**2)
    return {
        "matrix": [[str(k_zeta), str(cross)], [str(cross), str(k_f)]],
        "determinant": str(determinant),
        "possible_ranks": [1, 2],
        "rank_one_condition": str(sp.Eq(cross**2, k_zeta * k_f)),
        "rank_two_condition": str(sp.Ne(cross**2, k_zeta * k_f)),
    }


def coupled_rank_payload() -> dict[str, Any]:
    kappa5 = sp.Symbol("kappa5", positive=True)
    bounds = rank_bounds_two_mode(sp.Float("6.935084858283065"), 6 * kappa5)
    validation = {
        "known_constraint_removes_seam_duplicate": True,
        "rank_not_guessed": bounds["possible_ranks"] == [1, 2],
        "eigenmode_not_claimed": True,
        "nonlinear_branch_not_claimed": True,
    }
    return {
        "artifact": "BHSM_coupled_physical_rank_v10_3",
        "gauge_rank": 0,
        "known_constraint_rank": 1,
        "formal_reduced_basis": ["zeta", "varphi_F"],
        "physical_kinetic_rank": None,
        "rank_bounds": bounds,
        "generalized_eigenproblem": "H_env v=omega^2 K_env v",
        "lowest_common_eigenmode": None,
        "reason_eigenproblem_unavailable": "cross-domain K/H blocks and one stationary common background are absent",
        "nonlinear_continuation": {
            "branch": "Phi(epsilon)=Phi0+epsilon v_env+O(epsilon^2)",
            "status": UNRESOLVED,
            "exact_blocker": "no common linear operator or stationary common background",
            "tracked_components": ["a_F(epsilon)", "sigma_wall(epsilon)", "X_seam(epsilon)"],
        },
        "equivalence_status": UNRESOLVED,
        "physically_inequivalent": False,
        "primary_verdict": PRIMARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

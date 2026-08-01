"""Exact Schur-complement and historical-reduction audit for BHSM v10.3."""

from __future__ import annotations

from typing import Any

import sympy as sp

from .common_envelopment_mode_v10_3 import PRIMARY_VERDICT, UNRESOLVED


def schur_complement(matrix: sp.Matrix, keep: tuple[int, ...]) -> sp.Matrix:
    """Return the Schur complement onto ``keep`` when the eliminated block is invertible."""

    if matrix.rows != matrix.cols:
        raise ValueError("matrix must be square")
    if not keep or len(set(keep)) != len(keep) or any(i < 0 or i >= matrix.rows for i in keep):
        raise ValueError("keep must contain distinct valid indices")
    rest = tuple(i for i in range(matrix.rows) if i not in keep)
    a = matrix.extract(keep, keep)
    if not rest:
        return a
    b = matrix.extract(keep, rest)
    c = matrix.extract(rest, keep)
    d = matrix.extract(rest, rest)
    if sp.simplify(d.det()) == 0:
        raise ValueError("eliminated block must be invertible")
    return sp.simplify(a - b * d.inv() * c)


def historical_reduction_rows() -> list[dict[str, Any]]:
    return [
        {
            "historical_operator": "support-shift/threading response",
            "recovery": "psi=-(tau*pi*chi_1/16) zeta after the full momentum constraint",
            "status": "DERIVED_CONDITIONAL",
            "is_full_three_sector_Schur_reduction": False,
        },
        {
            "historical_operator": "fold/Fredholm operator",
            "recovery": "exact Schur reduction over lapse/Weyl/constraint complement inside D_fold",
            "status": "DERIVED_CONDITIONAL",
            "is_full_three_sector_Schur_reduction": None,
        },
        {
            "historical_operator": "Hopf-radion operator",
            "recovery": "direct invariant M8 metric reduction",
            "status": "DERIVED_CONDITIONAL",
            "is_full_three_sector_Schur_reduction": None,
        },
    ]


def effective_reduction_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_effective_mode_reductions_v10_3",
        "historical_reductions": historical_reduction_rows(),
        "H_eff_psi": None,
        "H_eff_zeta": None,
        "H_eff_F": None,
        "reason": "H_zetaF, H_Fzeta, and the common domain are undefined",
        "Schur_complement_equivalence": UNRESOLVED,
        "historical_operator_recovery_without_duplicate_derivation": True,
        "physically_inequivalent": False,
        "primary_verdict": PRIMARY_VERDICT,
    }

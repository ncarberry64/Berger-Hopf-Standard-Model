from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import log
from typing import Dict, Iterable, List, Tuple

import charged_kf_generator as kf


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

C_CH = 3
DEPENDENCY_ORDER = "P_ch -> Tr_sector(P_ch) -> C_ch -> K_boundary[C_ch] -> P_f projection"
LOCAL_RHO_CH = 1
B_DIAGNOSTIC_RHO_CH = 3

STATUS_TABLE = {
    "A_local_branch_matrix_export": "EXPORTED",
    "A_background_identity_branch": "IMPLEMENTED_CONDITIONAL",
    "A_background_dependency_order": "VERIFIED",
    "B_diagnostic_branch": "PRESERVED_DIAGNOSTIC",
    "K_collar_response_audit": "RAN",
    "chi_from_boundary_geometry": "OPEN_LOCALIZABLE",
    "chi_from_mass_fit": "FORBIDDEN",
    "charged_precision_closure": "OPEN",
    "official_predictions": "UNCHANGED",
}


@dataclass(frozen=True)
class BranchMatrix:
    branch: str
    sector: str
    matrix: Tuple[Tuple[float, float, float], ...]
    mode_ledger: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]
    claim_status: str
    matrix_status: str
    notes: str


def _to_float_matrix(matrix: Iterable[Iterable[object]]) -> Tuple[Tuple[float, float, float], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)  # type: ignore[return-value]


def _add_identity(matrix: Tuple[Tuple[float, float, float], ...], scale: float) -> Tuple[Tuple[float, float, float], ...]:
    rows = [[value for value in row] for row in matrix]
    for index in range(3):
        rows[index][index] += scale
    return tuple(tuple(row) for row in rows)  # type: ignore[return-value]


def _apply_up_threshold_if_needed(
    sector: str,
    matrix: Tuple[Tuple[float, float, float], ...],
) -> Tuple[Tuple[float, float, float], ...]:
    if sector != "up":
        return matrix
    rows = [[value for value in row] for row in matrix]
    for insertion in kf.threshold_insertions():
        if insertion["sector"] == "up":
            slot = int(insertion["slot"])
            rows[slot][slot] += log(2.0)
    return tuple(tuple(row) for row in rows)  # type: ignore[return-value]


def a_local_matrix(sector: str) -> Tuple[Tuple[float, float, float], ...]:
    """Return the local action-unit branch without charged-background collar insertion."""

    matrix = _to_float_matrix(
        kf.minimal_K_f_for_rule(
            sector,
            LOCAL_RHO_CH,
            kf.RULE_A_SINGLE_OPERATOR_TRACE,
            kf.BRIDGE_RULE_MINIMAL_ANSATZ,
        )
    )
    return _apply_up_threshold_if_needed(sector, matrix)


def a_background_identity_matrix(sector: str) -> Tuple[Tuple[float, float, float], ...]:
    """Return A-background identity-collar branch with C_ch I added before projection."""

    boundary_before_projection = _add_identity(a_local_matrix(sector), float(C_CH))
    return boundary_before_projection


def b_diagnostic_matrix(sector: str) -> Tuple[Tuple[float, float, float], ...]:
    if sector == "up":
        return kf.dressed_K_u_for_rule(
            B_DIAGNOSTIC_RHO_CH,
            kf.RULE_A_SINGLE_OPERATOR_TRACE,
        )
    return _to_float_matrix(
        kf.minimal_K_f_for_rule(
            sector,
            B_DIAGNOSTIC_RHO_CH,
            kf.RULE_A_SINGLE_OPERATOR_TRACE,
            kf.BRIDGE_RULE_MINIMAL_ANSATZ,
        )
    )


def _branch_row(branch: str, sector: str, matrix: Tuple[Tuple[float, float, float], ...]) -> BranchMatrix:
    return BranchMatrix(
        branch=branch,
        sector=sector,
        matrix=matrix,
        mode_ledger=kf.LEDGERS[sector],
        claim_status=(
            "DERIVED_CONDITIONAL_WITH_LOCAL_THRESHOLD"
            if sector == "up"
            else "DERIVED_CONDITIONAL"
        ),
        matrix_status="EXPORTED_FROM_BRANCH_CONSTRUCTOR",
        notes=(
            "Up-sector threshold is restricted to middle mode (q,j)=(6,0)."
            if sector == "up"
            else "No local Z_virt threshold in this sector."
        ),
    )


def build_charged_A_local_branch() -> Tuple[BranchMatrix, ...]:
    return tuple(
        _branch_row("A-local", sector, a_local_matrix(sector))
        for sector in kf.CHARGED_SECTORS
    )


def build_charged_A_background_identity_branch() -> Tuple[BranchMatrix, ...]:
    return tuple(
        _branch_row(
            "A-background-identity",
            sector,
            a_background_identity_matrix(sector),
        )
        for sector in kf.CHARGED_SECTORS
    )


def build_charged_B_diagnostic_branch() -> Tuple[BranchMatrix, ...]:
    return tuple(
        _branch_row("B-diagnostic", sector, b_diagnostic_matrix(sector))
        for sector in kf.CHARGED_SECTORS
    )


def _matrix_to_json(matrix: Tuple[Tuple[float, float, float], ...]) -> List[List[float]]:
    return [[float(value) for value in row] for row in matrix]


def _row_to_json(row: BranchMatrix) -> Dict[str, object]:
    out: Dict[str, object] = {
        "K": _matrix_to_json(row.matrix),
        "mode_ledger": [list(mode) for mode in row.mode_ledger],
        "claim_status": row.claim_status,
        "matrix_status": row.matrix_status,
        "notes": row.notes,
    }
    if row.sector == "up":
        out["Z_virt_middle_up"] = "1/2 if dressed branch active"
        out["Z_virt_scope"] = "up sector, middle mode (q,j)=(6,0) only"
    return out


def branch_artifact(branch: str) -> Dict[str, object]:
    if branch == "A-local":
        rows = build_charged_A_local_branch()
        matrix_status = "EXPORTED"
        source = "A-local branch constructor with local rho_ch=1 action unit"
        extra: Dict[str, object] = {
            "local_rho_ch": LOCAL_RHO_CH,
            "K_collar": "not included",
            "dependency_order": "P_f local action/projector branch",
        }
    elif branch == "A-background-identity":
        rows = build_charged_A_background_identity_branch()
        matrix_status = "EXPORTED"
        source = "A-background identity collar branch constructor"
        extra = {
            "C_ch": C_CH,
            "C_ch_source": "Tr_sector(P_ch)",
            "K_collar": "identity second-jet collar",
            "dependency_order": DEPENDENCY_ORDER,
            "chi_used": False,
            "chi_fit_to_masses": False,
            "direct_projected_Kf_multiplier_by_3": False,
        }
    elif branch == "B-diagnostic":
        rows = build_charged_B_diagnostic_branch()
        matrix_status = "EXPORTED_FROM_REPO_GENERATOR"
        source = "charged_kf_generator with rho_ch=3, Rule-A suppression, up middle ln2 threshold"
        extra = {
            "rho_ch": B_DIAGNOSTIC_RHO_CH,
            "diagnostic_only": True,
            "not_A_background": True,
        }
    else:
        raise ValueError(f"unknown branch: {branch}")

    return {
        "artifact": "charged_branch_matrices_v2",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "branch": branch,
        "frozen_before_comparison": True,
        "used_target_data": False,
        "a": 1.157054135733433,
        "c": [1, 2, 4],
        "generation_order": "by_y_ascending",
        "matrix_status": matrix_status,
        "source": source,
        **extra,
        "sectors": {row.sector: _row_to_json(row) for row in rows},
    }


def status_artifact() -> Dict[str, object]:
    return {
        "artifact": "a_background_collar_dependency_order_v1",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "statuses": STATUS_TABLE,
        "dependency_order": DEPENDENCY_ORDER,
        "A_background_identity_implemented": True,
        "A_background_dependency_order_verified": True,
        "B_diagnostic_preserved": True,
        "chi_from_boundary_geometry": "OPEN_LOCALIZABLE",
        "chi_from_mass_fit": "FORBIDDEN",
        "claim_boundary": (
            "A-background identity is a dependency-order scaffold only; "
            "minimal anisotropic chi remains open and no numerical closure is claimed."
        ),
    }

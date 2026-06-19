from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List

from sector_projector_hessian_fork import (
    CYCLIC_ANISOTROPY_COSTS,
    ISOTROPIC_COSTS,
    all_charged_ledgers_preserved,
    ledger_costs,
)


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"


@dataclass(frozen=True)
class HessianSourceRow:
    object: str
    possible_source: str
    supports_rho_1: bool
    supports_rho_3: bool
    supports_another_rho: bool
    supports_qj_cross_term: bool
    charged_sector_applicable: bool
    neutral_topographic_only: bool
    status: str
    reason: str


def charged_metric_costs(rho_ch: Fraction | int | float) -> Dict[str, List[Fraction | float]]:
    return {
        "lepton": ledger_costs("lepton", rho_ch),
        "up": ledger_costs("up", rho_ch),
        "down": ledger_costs("down", rho_ch),
    }


def down_membership_constraint(rho_ch: Fraction | int | float) -> bool:
    return 0 < rho_ch < 8


def down_ordering_constraint(rho_ch: Fraction | int | float) -> bool:
    return 0 < rho_ch < Fraction(16, 5)


def diagonal_charged_hessian(q: int, j: int, rho_ch: Fraction | int | float) -> Fraction | float:
    return q * q + rho_ch * j * j


def cross_term_status(action_source_present: bool = False) -> str:
    if action_source_present:
        return "OPEN_REQUIRES_ACTION_VALUE"
    return "FORBIDDEN_CONDITIONAL_UNLESS_ACTION_DERIVED"


def eta_l_status(rho_ch_status: str = "OPEN_LOCALIZABLE") -> Dict[str, object]:
    return {
        "eta_l_projection_structure": "VALIDATED_CANDIDATE",
        "eta_l_exact_value": "OPEN",
        "eta_l_depends_on_rho_ch": True,
        "eta_l_fit": "FORBIDDEN_AS_DERIVATION",
        "eta_l_8_over_9_trace_route": "DOWNGRADED_NUMERICAL_COINCIDENCE",
        "alpha_geom_internal_derivation": "OPEN_LOCALIZABLE",
        "Pi_l_value": "OPEN_LOCALIZABLE",
        "self_screening_factor_1_minus_alpha_geom": "STRUCTURALLY_SUPPORTED_CANDIDATE",
        "rho_ch_status": rho_ch_status,
        "eta_l_can_be_derived": rho_ch_status != "OPEN_LOCALIZABLE",
    }


def source_audit_rows() -> List[HessianSourceRow]:
    return [
        HessianSourceRow(
            object="minimal isotropic charged closure",
            possible_source="absence of charged anisotropy, qj cross-term, or charged j-weighting source",
            supports_rho_1=True,
            supports_rho_3=False,
            supports_another_rho=False,
            supports_qj_cross_term=False,
            charged_sector_applicable=True,
            neutral_topographic_only=False,
            status="MINIMAL_ACTION_CLOSURE_CANDIDATE",
            reason="absence of a charged anisotropy source supports rho=1 as a minimal candidate, not a derivation",
        ),
        HessianSourceRow(
            object="base cyclic factor 3",
            possible_source="finite cyclic boundary factor",
            supports_rho_1=False,
            supports_rho_3=True,
            supports_another_rho=False,
            supports_qj_cross_term=False,
            charged_sector_applicable=False,
            neutral_topographic_only=False,
            status="STRUCTURALLY_MOTIVATED_NOT_DERIVED",
            reason="no existing action/Hessian term links the cyclic factor 3 to charged j-direction Hessian weight",
        ),
        HessianSourceRow(
            object="neutral/topographic Berger anisotropy",
            possible_source="neutral/topographic metric, scalar profile, collar, or subsurface mechanism",
            supports_rho_1=False,
            supports_rho_3=False,
            supports_another_rho=True,
            supports_qj_cross_term=True,
            charged_sector_applicable=False,
            neutral_topographic_only=True,
            status="OPEN_ALLOWED_NEUTRAL_ONLY",
            reason="neutral/topographic mixing remains allowed but does not leak into charged Hessian without explicit coupling",
        ),
        HessianSourceRow(
            object="charged qj cross-term",
            possible_source="none found in charged-sector action/Hessian sources",
            supports_rho_1=False,
            supports_rho_3=False,
            supports_another_rho=False,
            supports_qj_cross_term=False,
            charged_sector_applicable=True,
            neutral_topographic_only=False,
            status="FORBIDDEN_CONDITIONAL_UNLESS_ACTION_DERIVED",
            reason="charged q and j remain separate unless a charged action term derives mixing",
        ),
    ]


def audit_statuses() -> Dict[str, str]:
    return {
        "charged_Hessian_source_audit": "COMPLETED",
        "rho_ch_1_minimal_closure": "MINIMAL_ACTION_CLOSURE_CANDIDATE",
        "rho_ch_3_cyclic_weight": "STRUCTURALLY_MOTIVATED_NOT_DERIVED",
        "rho_ch_action_value": "OPEN_LOCALIZABLE",
        "charged_Hessian_anisotropy_rho_ch": "OPEN_LOCALIZABLE",
        "charged_qj_cross_term": "FORBIDDEN_CONDITIONAL_UNLESS_ACTION_DERIVED",
        "neutral_qj_mixing": "OPEN_ALLOWED",
        "topographic_Berger_anisotropy_to_charged_sector": "FORBIDDEN_UNLESS_EXPLICIT_COUPLING_DERIVED",
        "eta_l_projection_structure": "VALIDATED_CANDIDATE",
        "eta_l_exact_value": "OPEN",
        "eta_l_depends_on_rho_ch": "TRUE",
        "eta_l_fit": "FORBIDDEN_AS_DERIVATION",
        "eta_l_8_over_9_trace_route": "DOWNGRADED_NUMERICAL_COINCIDENCE",
        "alpha_geom_internal_derivation": "OPEN_LOCALIZABLE",
        "Pi_l_value": "OPEN_LOCALIZABLE",
        "self_screening_factor_1_minus_alpha_geom": "STRUCTURALLY_SUPPORTED_CANDIDATE",
    }


def no_action_source_decides_rho() -> bool:
    return all(row.status != "DERIVED_CONDITIONAL" for row in source_audit_rows())


def old_costs_are_conditional_on_rho_1() -> bool:
    return charged_metric_costs(1) == ISOTROPIC_COSTS


def cyclic_costs_are_conditional_on_rho_3() -> bool:
    return charged_metric_costs(3) == CYCLIC_ANISOTROPY_COSTS


def rho_candidates_preserve_ledgers() -> bool:
    return all_charged_ledgers_preserved(1) and all_charged_ledgers_preserved(3)

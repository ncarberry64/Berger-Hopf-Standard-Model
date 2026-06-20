from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Tuple

import full_bhsm_closure_dependency_graph as graph


PUBLIC_STATUS = graph.PUBLIC_STATUS

FREEZE_CLASSES = (
    "FROZEN_STRUCTURE_ALLOWED",
    "CANDIDATE_BRANCH_FREEZE_ALLOWED",
    "DIAGNOSTIC_ONLY",
    "BLOCKED_BY_OPEN_SELECTOR",
    "INVALIDATED_DO_NOT_FREEZE",
)

STATUS_TABLE = {
    "full_bhsm_freeze_boundary_v1": "STRUCTURAL_SCAFFOLD",
    "numerical_closure": "OPEN",
}


@dataclass(frozen=True)
class FreezeBoundaryRecord:
    component_id: str
    freeze_class: str
    current_status: str
    reason: str
    allowed_to_freeze_now: bool
    artifact_refs: Tuple[str, ...]


def _record(
    component_id: str,
    freeze_class: str,
    current_status: str,
    reason: str,
    artifact_refs: Tuple[str, ...] = (),
) -> FreezeBoundaryRecord:
    if freeze_class not in FREEZE_CLASSES:
        raise ValueError(f"unknown freeze class: {freeze_class}")
    return FreezeBoundaryRecord(
        component_id=component_id,
        freeze_class=freeze_class,
        current_status=current_status,
        reason=reason,
        allowed_to_freeze_now=freeze_class in {
            "FROZEN_STRUCTURE_ALLOWED",
            "CANDIDATE_BRANCH_FREEZE_ALLOWED",
        },
        artifact_refs=artifact_refs,
    )


def freeze_boundary_records() -> Tuple[FreezeBoundaryRecord, ...]:
    return (
        _record(
            "sector_equations",
            "FROZEN_STRUCTURE_ALLOWED",
            "DERIVED_CONDITIONAL",
            "Sector equations are structural outputs of the sector/projector engine.",
            ("src/charged_kf_generator.py",),
        ),
        _record(
            "mode_ledgers",
            "FROZEN_STRUCTURE_ALLOWED",
            "DERIVED_CONDITIONAL",
            "Mode ledgers are structural architecture, not numerical closure.",
            ("src/charged_kf_generator.py", "src/neutral_sector_operator_kernel.py"),
        ),
        _record(
            "boundary_graded_defect_action_kernel_v1",
            "FROZEN_STRUCTURE_ALLOWED",
            "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
            "Boundary graded defect action kernel can be frozen as structure.",
            ("docs/boundary_graded_defect_action_kernel_v1.md",),
        ),
        _record(
            "Rule_A_single_operator_trace",
            "FROZEN_STRUCTURE_ALLOWED",
            "DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL",
            "Rule A is a direct charged suppression kernel rule.",
            ("docs/charged_kf_rule_a_spectral_sanity_v1.md",),
        ),
        _record(
            "charged_Kf_tridiagonal_bridge_topology",
            "FROZEN_STRUCTURE_ALLOWED",
            "DERIVED_CONDITIONAL_ON_E3_LADDER_AND_TANGENT_ADJACENCY",
            "Bridge topology is structurally freezeable; magnitudes are not.",
            ("docs/charged_kf_bridge_coupling_kernel_v1.md",),
        ),
        _record(
            "up_6_0_Zvirt_threshold",
            "FROZEN_STRUCTURE_ALLOWED",
            "DERIVED_CONDITIONAL",
            "The known up (6,0) eligibility and insertion are conditionally derived.",
            ("docs/full_threshold_operator_eligibility_v1.md",),
        ),
        _record(
            "neutrino_mode_ledger",
            "FROZEN_STRUCTURE_ALLOWED",
            "DERIVED_CONDITIONAL_ON_SECTOR_ENGINE",
            "Neutral ledger can be frozen as structural sector-engine output.",
            ("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _record(
            "PMNS_structural_source",
            "FROZEN_STRUCTURE_ALLOWED",
            "STRUCTURALLY_MOTIVATED_CANDIDATE",
            "Only the structural relation U_PMNS=U_l^dagger U_nu is freezeable.",
            ("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _record(
            "rho_ch_branches_1_2_3",
            "CANDIDATE_BRANCH_FREEZE_ALLOWED",
            "BRANCH_CANDIDATE",
            "rho_ch in {1,2,3} may be frozen as candidate branches only.",
            ("docs/rho_ch_branch_pressure_test_v1.md",),
        ),
        _record(
            "minimal_1_over_21_bridge_seed",
            "CANDIDATE_BRANCH_FREEZE_ALLOWED",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "1/21 bridge seeds may be candidate-frozen, not claimed derived.",
            ("docs/charged_kf_bridge_coupling_kernel_v1.md",),
        ),
        _record(
            "neutral_Hessian_branches_N0_N1_N2",
            "CANDIDATE_BRANCH_FREEZE_ALLOWED",
            "STRUCTURALLY_MOTIVATED_CANDIDATE",
            "Neutral Hessian branches are diagnostic candidates; no winner selected.",
            ("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _record(
            "Rule_B_double_normalized_phase_candidate",
            "CANDIDATE_BRANCH_FREEZE_ALLOWED",
            "CANDIDATE_REQUIRES_INDEPENDENT_PHASE_RESPONSE",
            "Rule B may be candidate-frozen only with its caveat.",
            ("docs/charged_kf_rule_a_spectral_sanity_v1.md",),
        ),
        _record(
            "Rule_A_spectral_sanity_tables",
            "DIAGNOSTIC_ONLY",
            "STRUCTURAL_SCAFFOLD",
            "Spectral sanity tables are internal diagnostics, not empirical closure.",
            ("docs/charged_kf_rule_a_spectral_sanity_v1.md",),
        ),
        _record(
            "rho_branch_pressure_tests",
            "DIAGNOSTIC_ONLY",
            "STRUCTURALLY_INTERESTING_BRANCH",
            "rho branch pressure tests do not select a branch.",
            ("docs/rho_ch_branch_pressure_test_v1.md",),
        ),
        _record(
            "neutral_unit_diagnostic_operator",
            "DIAGNOSTIC_ONLY",
            "STRUCTURALLY_MOTIVATED_CANDIDATE",
            "Unit-normalized neutral readout is not a physical prediction.",
            ("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _record(
            "exact_rho_ch",
            "BLOCKED_BY_OPEN_SELECTOR",
            "OPEN_LOCALIZABLE",
            "Exact rho_ch needs a charged stiffness action source.",
            ("docs/charged_stiffness_action_selector_v1.md",),
        ),
        _record(
            "beta_kappa_bridge_magnitudes",
            "BLOCKED_BY_OPEN_SELECTOR",
            "OPEN_LOCALIZABLE",
            "Bridge magnitudes need beta_0/kappa_0 action source.",
            ("docs/charged_kf_bridge_coupling_kernel_v1.md",),
        ),
        _record(
            "neutral_eta_beta_kappa",
            "BLOCKED_BY_OPEN_SELECTOR",
            "OPEN_LOCALIZABLE",
            "Neutral eta and bridge sources remain open.",
            ("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _record(
            "selected_neutral_Hessian",
            "BLOCKED_BY_OPEN_SELECTOR",
            "OPEN_LOCALIZABLE",
            "Neutral Hessian branch selection has no action selector yet.",
            ("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _record(
            "full_threshold_operator_beyond_up_6_0",
            "BLOCKED_BY_OPEN_SELECTOR",
            "OPEN",
            "No additional virtual-door/projector threshold sources are derived.",
            ("docs/full_threshold_operator_eligibility_v1.md",),
        ),
        _record(
            "RG_transport",
            "BLOCKED_BY_OPEN_SELECTOR",
            "OPEN_LOCALIZABLE",
            "RG/scheme transport interface is scaffolded, rules not derived.",
            ("docs/rg_transport_interface_v1.md",),
        ),
        _record(
            "mass_numerical_closure",
            "BLOCKED_BY_OPEN_SELECTOR",
            "OPEN",
            "Mass numerical closure waits on selectors and transport.",
            ("docs/open_blockers_backlog.md",),
        ),
        _record(
            "CKM_numerical_closure",
            "BLOCKED_BY_OPEN_SELECTOR",
            "OPEN",
            "CKM closure waits on charged operator branch selection and transport.",
            ("docs/open_blockers_backlog.md",),
        ),
        _record(
            "PMNS_numerical_closure",
            "BLOCKED_BY_OPEN_SELECTOR",
            "OPEN",
            "PMNS closure waits on neutral operator derivation.",
            ("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _record(
            "charged_Hessian_from_S_index_trace",
            "INVALIDATED_DO_NOT_FREEZE",
            "INVALIDATED_DO_NOT_CLAIM",
            "S_index_trace is explicitly not the charged Hessian.",
            ("docs/charged_stiffness_action_selector_v1.md",),
        ),
        _record(
            "invented_thresholds_beyond_up_6_0",
            "INVALIDATED_DO_NOT_FREEZE",
            "INVALIDATED_DO_NOT_CLAIM",
            "Threshold factors cannot be invented without virtual-door/projector data.",
            ("docs/full_threshold_operator_eligibility_v1.md",),
        ),
        _record(
            "empirical_input_derived_selector",
            "INVALIDATED_DO_NOT_FREEZE",
            "INVALIDATED_DO_NOT_CLAIM",
            "Selectors must not be derived from post-comparison empirical residuals.",
            ("docs/forbidden_claims.md",),
        ),
        _record(
            "direct_charged_numerical_closure_claim",
            "INVALIDATED_DO_NOT_FREEZE",
            "INVALIDATED_DO_NOT_CLAIM",
            "Charged numerical closure remains open.",
            ("docs/open_blockers_backlog.md",),
        ),
    )


def freeze_class_counts() -> Dict[str, int]:
    counts = {klass: 0 for klass in FREEZE_CLASSES}
    for record in freeze_boundary_records():
        counts[record.freeze_class] += 1
    return counts


def records_by_class(freeze_class: str) -> Tuple[FreezeBoundaryRecord, ...]:
    return tuple(record for record in freeze_boundary_records() if record.freeze_class == freeze_class)


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-full-freeze-boundary-v1",
        "title": "Full BHSM Freeze Boundary v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "statuses": STATUS_TABLE,
        "freeze_class_counts": freeze_class_counts(),
        "records": [asdict(record) for record in freeze_boundary_records()],
        "summary": (
            "BHSM may freeze structural architecture and candidate branches, but not final "
            "numerical predictions from this layer."
        ),
        "claim_boundary": "Freeze boundary does not promote numerical closure.",
    }

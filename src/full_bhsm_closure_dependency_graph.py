from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Tuple


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

ALLOWED_STATUSES = (
    "DERIVED",
    "DERIVED_CONDITIONAL",
    "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL",
    "DERIVED_CONDITIONAL_ON_E3_LADDER_AND_TANGENT_ADJACENCY",
    "DERIVED_CONDITIONAL_ON_SECTOR_ENGINE",
    "STRUCTURAL_SCAFFOLD",
    "STRUCTURALLY_SUPPORTED_CANDIDATE",
    "STRONGLY_SUPPORTED_CANDIDATE",
    "STRUCTURALLY_MOTIVATED_CANDIDATE",
    "STRUCTURALLY_MOTIVATED_NOT_DERIVED",
    "STRUCTURALLY_POSSIBLE_NOT_DERIVED",
    "BRANCH_CANDIDATE",
    "CANDIDATE_REQUIRES_INDEPENDENT_PHASE_RESPONSE",
    "STRUCTURALLY_INTERESTING_BRANCH",
    "OPEN_LOCALIZABLE",
    "OPEN",
    "NO_THRESHOLD_SOURCE_FOUND",
    "REFERENCE_SLOT_NOT_THRESHOLD_TARGET",
    "INVALIDATED_DO_NOT_CLAIM",
)


@dataclass(frozen=True)
class ClosureGraphNode:
    node_id: str
    label: str
    status: str
    dependencies: Tuple[str, ...]
    blocks: Tuple[str, ...]
    evidence_source: str
    repo_artifact_refs: Tuple[str, ...]
    claim_allowed: bool
    claim_text_short: str
    do_not_claim_text: str


def _node(
    node_id: str,
    label: str,
    status: str,
    dependencies: Tuple[str, ...] = (),
    blocks: Tuple[str, ...] = (),
    evidence_source: str = "repo scaffold",
    repo_artifact_refs: Tuple[str, ...] = (),
    claim_allowed: bool = True,
    claim_text_short: str = "",
    do_not_claim_text: str = "",
) -> ClosureGraphNode:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"unknown status for {node_id}: {status}")
    return ClosureGraphNode(
        node_id=node_id,
        label=label,
        status=status,
        dependencies=dependencies,
        blocks=blocks,
        evidence_source=evidence_source,
        repo_artifact_refs=repo_artifact_refs,
        claim_allowed=claim_allowed,
        claim_text_short=claim_text_short or f"{label}: {status}",
        do_not_claim_text=do_not_claim_text,
    )


def closure_graph_nodes() -> Tuple[ClosureGraphNode, ...]:
    nodes = (
        _node(
            "finite_boundary_algebra",
            "Finite boundary algebra",
            "DERIVED_CONDITIONAL",
            blocks=("sector_projectors",),
            repo_artifact_refs=("docs/claim_status_table.md",),
        ),
        _node(
            "sector_projectors",
            "Sector projectors",
            "DERIVED_CONDITIONAL",
            dependencies=("finite_boundary_algebra",),
            blocks=("sector_equations",),
            repo_artifact_refs=("src/charged_kf_generator.py",),
        ),
        _node(
            "sector_equations",
            "Sector equations",
            "DERIVED_CONDITIONAL",
            dependencies=("sector_projectors",),
            blocks=("mode_ledgers",),
            repo_artifact_refs=("src/charged_kf_generator.py",),
        ),
        _node(
            "mode_ledgers",
            "Mode ledgers",
            "DERIVED_CONDITIONAL",
            dependencies=("sector_equations",),
            blocks=("charged_Kf_generator", "neutral_sector_operator_kernel"),
            repo_artifact_refs=("src/charged_kf_generator.py",),
        ),
        _node(
            "boundary_graded_defect_action_kernel",
            "Boundary graded defect action kernel",
            "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
            dependencies=("mode_ledgers",),
            blocks=("boundary_graded_defect_action_kernel_v1",),
            repo_artifact_refs=("docs/boundary_graded_defect_action_kernel_v1.md",),
        ),
        _node(
            "boundary_graded_defect_action_kernel_v1",
            "Boundary graded defect action kernel v1",
            "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
            dependencies=("boundary_graded_defect_action_kernel",),
            blocks=("B_supp_trace_kernel", "charged_Kf_generator"),
            repo_artifact_refs=("docs/boundary_graded_defect_action_kernel_v1.md",),
        ),
        _node(
            "charged_Hessian_from_S_index_trace",
            "Charged Hessian from S_index_trace",
            "INVALIDATED_DO_NOT_CLAIM",
            dependencies=("boundary_graded_defect_action_kernel_v1",),
            evidence_source="charged stiffness selector guardrail",
            repo_artifact_refs=("docs/charged_stiffness_action_selector_v1.md",),
            claim_allowed=False,
            claim_text_short="S_index_trace is not the charged hierarchy Hessian.",
            do_not_claim_text="Do not claim S_index_trace derives rho_ch or the charged Hessian.",
        ),
        _node(
            "charged_stiffness_action_source",
            "Charged stiffness action source",
            "OPEN_LOCALIZABLE",
            dependencies=("boundary_graded_defect_action_kernel_v1",),
            blocks=("rho_ch_exact_value",),
            repo_artifact_refs=("docs/charged_stiffness_action_selector_v1.md",),
            claim_text_short="Charged stiffness source is localized but open.",
        ),
        _node(
            "B_supp_trace_kernel",
            "B_supp trace kernel",
            "DERIVED_CONDITIONAL",
            dependencies=("boundary_graded_defect_action_kernel_v1",),
            blocks=("Rule_A_single_operator_trace",),
            repo_artifact_refs=("docs/charged_suppression_operator_kernel_v1.md",),
        ),
        _node(
            "Rule_A_single_operator_trace",
            "Rule A single-operator trace",
            "DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL",
            dependencies=("B_supp_trace_kernel",),
            blocks=("charged_Kf_generator",),
            repo_artifact_refs=("docs/charged_kf_rule_a_spectral_sanity_v1.md",),
        ),
        _node(
            "Rule_B_double_normalized_phase_candidate",
            "Rule B double-normalized phase candidate",
            "CANDIDATE_REQUIRES_INDEPENDENT_PHASE_RESPONSE",
            dependencies=("B_supp_trace_kernel",),
            repo_artifact_refs=("docs/charged_kf_rule_a_spectral_sanity_v1.md",),
            claim_text_short="Rule B remains a candidate requiring independent phase response.",
        ),
        _node(
            "charged_Kf_generator",
            "Charged Kf generator",
            "STRONGLY_SUPPORTED_CANDIDATE",
            dependencies=("mode_ledgers", "Rule_A_single_operator_trace"),
            blocks=("charged_numerical_closure",),
            repo_artifact_refs=("src/charged_kf_generator.py",),
        ),
        _node(
            "rho_ch_branch_candidates",
            "rho_ch branch candidates",
            "BRANCH_CANDIDATE",
            dependencies=("charged_stiffness_action_source",),
            blocks=("rho_ch_exact_value",),
            repo_artifact_refs=("docs/rho_ch_branch_pressure_test_v1.md",),
        ),
        _node(
            "charged_stiffness_action_selector",
            "Charged stiffness action selector",
            "STRUCTURALLY_MOTIVATED_NOT_DERIVED",
            dependencies=("rho_ch_branch_candidates",),
            blocks=("rho_ch_exact_value",),
            repo_artifact_refs=("docs/charged_stiffness_action_selector_v1.md",),
            claim_text_short="Selector audit found no unique action selector.",
        ),
        _node(
            "rho_ch_exact_value",
            "Exact rho_ch value",
            "OPEN_LOCALIZABLE",
            dependencies=("charged_stiffness_action_selector",),
            blocks=("charged_numerical_closure",),
            repo_artifact_refs=("docs/charged_stiffness_action_selector_v1.md",),
        ),
        _node(
            "charged_Kf_tridiagonal_bridge_topology",
            "Charged Kf tridiagonal bridge topology",
            "DERIVED_CONDITIONAL_ON_E3_LADDER_AND_TANGENT_ADJACENCY",
            dependencies=("charged_Kf_generator",),
            blocks=("charged_numerical_closure",),
            repo_artifact_refs=("docs/charged_kf_bridge_coupling_kernel_v1.md",),
        ),
        _node(
            "beta_f_reference_bridge_magnitude",
            "beta_f reference bridge magnitude",
            "OPEN_LOCALIZABLE",
            dependencies=("charged_Kf_tridiagonal_bridge_topology",),
            blocks=("charged_numerical_closure",),
            repo_artifact_refs=("docs/charged_kf_bridge_coupling_kernel_v1.md",),
        ),
        _node(
            "kappa_f_tangent_bridge_magnitude",
            "kappa_f tangent bridge magnitude",
            "OPEN_LOCALIZABLE",
            dependencies=("charged_Kf_tridiagonal_bridge_topology",),
            blocks=("charged_numerical_closure",),
            repo_artifact_refs=("docs/charged_kf_bridge_coupling_kernel_v1.md",),
        ),
        _node(
            "minimal_1_over_21_bridge_seed",
            "Minimal 1/21 bridge seed",
            "STRONGLY_SUPPORTED_CANDIDATE",
            dependencies=("charged_Kf_tridiagonal_bridge_topology",),
            repo_artifact_refs=("docs/charged_kf_bridge_coupling_kernel_v1.md",),
            claim_text_short="The 1/21 bridge seed is a named candidate, not a derived magnitude.",
        ),
        _node(
            "up_6_0_Zvirt_threshold",
            "up (6,0) Zvirt threshold",
            "DERIVED_CONDITIONAL",
            dependencies=("charged_Kf_generator",),
            blocks=("full_threshold_operator",),
            repo_artifact_refs=("docs/full_threshold_operator_eligibility_v1.md",),
        ),
        _node(
            "full_threshold_operator",
            "Full threshold operator",
            "OPEN",
            dependencies=("up_6_0_Zvirt_threshold",),
            blocks=("charged_numerical_closure",),
            repo_artifact_refs=("docs/full_threshold_operator_eligibility_v1.md",),
        ),
        _node(
            "charged_numerical_closure",
            "Charged numerical closure",
            "OPEN",
            dependencies=(
                "rho_ch_exact_value",
                "beta_f_reference_bridge_magnitude",
                "kappa_f_tangent_bridge_magnitude",
                "full_threshold_operator",
                "RG_transport_interface",
            ),
            blocks=("numerical_closure",),
            repo_artifact_refs=("docs/open_blockers_backlog.md",),
        ),
        _node(
            "neutral_sector_operator_kernel",
            "Neutral sector operator kernel",
            "STRUCTURALLY_MOTIVATED_CANDIDATE",
            dependencies=("mode_ledgers",),
            blocks=("neutral_Hessian_symbolic_form", "neutral_numerical_closure"),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutrino_mode_ledger",
            "Neutrino mode ledger",
            "DERIVED_CONDITIONAL_ON_SECTOR_ENGINE",
            dependencies=("neutral_sector_operator_kernel",),
            blocks=("neutral_Hessian_symbolic_form",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutral_Hessian_symbolic_form",
            "Neutral Hessian symbolic form",
            "OPEN_LOCALIZABLE",
            dependencies=("neutrino_mode_ledger",),
            blocks=("neutral_Hessian_branch_N0", "neutral_Hessian_branch_N1", "neutral_Hessian_branch_N2"),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutral_Hessian_branch_N0",
            "Neutral Hessian branch N0",
            "STRUCTURALLY_MOTIVATED_CANDIDATE",
            dependencies=("neutral_Hessian_symbolic_form",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutral_Hessian_branch_N1",
            "Neutral Hessian branch N1",
            "STRUCTURALLY_POSSIBLE_NOT_DERIVED",
            dependencies=("neutral_Hessian_symbolic_form",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutral_Hessian_branch_N2",
            "Neutral Hessian branch N2",
            "STRUCTURALLY_MOTIVATED_CANDIDATE",
            dependencies=("neutral_Hessian_symbolic_form",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutral_eta_source",
            "Neutral eta source",
            "OPEN_LOCALIZABLE",
            dependencies=("neutral_sector_operator_kernel",),
            blocks=("neutral_numerical_closure",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutral_beta_bridge_source",
            "Neutral beta bridge source",
            "OPEN_LOCALIZABLE",
            dependencies=("neutral_sector_operator_kernel",),
            blocks=("neutral_numerical_closure",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutral_kappa_bridge_source",
            "Neutral kappa bridge source",
            "OPEN_LOCALIZABLE",
            dependencies=("neutral_sector_operator_kernel",),
            blocks=("neutral_numerical_closure",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutral_threshold_operator",
            "Neutral threshold operator",
            "OPEN",
            dependencies=("neutral_sector_operator_kernel",),
            blocks=("neutral_numerical_closure",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "PMNS_structural_source",
            "PMNS structural source",
            "STRUCTURALLY_MOTIVATED_CANDIDATE",
            dependencies=("charged_Kf_generator", "neutral_sector_operator_kernel"),
            blocks=("PMNS_numerical_closure",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "PMNS_numerical_closure",
            "PMNS numerical closure",
            "OPEN",
            dependencies=("PMNS_structural_source", "neutral_numerical_closure", "charged_numerical_closure"),
            blocks=("numerical_closure",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "neutral_numerical_closure",
            "Neutral numerical closure",
            "OPEN",
            dependencies=(
                "neutral_eta_source",
                "neutral_beta_bridge_source",
                "neutral_kappa_bridge_source",
                "neutral_threshold_operator",
                "neutral_Hessian_symbolic_form",
            ),
            blocks=("numerical_closure",),
            repo_artifact_refs=("docs/neutral_sector_operator_kernel_v1.md",),
        ),
        _node(
            "RG_transport_interface",
            "RG transport interface",
            "OPEN",
            dependencies=("charged_Kf_generator", "neutral_sector_operator_kernel"),
            blocks=("scheme_transport", "charged_numerical_closure"),
            repo_artifact_refs=("docs/rg_transport_interface_v1.md",),
        ),
        _node(
            "scheme_transport",
            "Scheme transport",
            "OPEN",
            dependencies=("RG_transport_interface",),
            blocks=("scheme_alignment",),
            repo_artifact_refs=("docs/rg_transport_interface_v1.md",),
        ),
        _node(
            "scheme_alignment",
            "Scheme alignment",
            "OPEN",
            dependencies=("scheme_transport",),
            blocks=("common_scale_comparison",),
            repo_artifact_refs=("docs/rg_transport_interface_v1.md",),
        ),
        _node(
            "common_scale_comparison",
            "Common-scale comparison",
            "OPEN",
            dependencies=("scheme_alignment",),
            blocks=("comparison_ready_predictions",),
            repo_artifact_refs=("docs/rg_transport_interface_v1.md",),
        ),
        _node(
            "comparison_ready_predictions",
            "Comparison-ready predictions",
            "OPEN",
            dependencies=("common_scale_comparison",),
            blocks=("numerical_closure",),
            repo_artifact_refs=("docs/rg_transport_interface_v1.md",),
        ),
        _node(
            "official_frozen_predictions",
            "Official frozen predictions",
            "DERIVED_CONDITIONAL",
            dependencies=("mode_ledgers",),
            repo_artifact_refs=("docs/frozen_predictions.md", "docs/frozen_predictions.json"),
            claim_text_short="Frozen prediction files remain immutable.",
        ),
        _node(
            "numerical_closure",
            "Numerical closure",
            "OPEN",
            dependencies=(
                "charged_numerical_closure",
                "neutral_numerical_closure",
                "PMNS_numerical_closure",
                "comparison_ready_predictions",
            ),
            repo_artifact_refs=("docs/open_blockers_backlog.md",),
            claim_text_short="Numerical closure remains open.",
        ),
    )
    return nodes


def node_map() -> Dict[str, ClosureGraphNode]:
    return {node.node_id: node for node in closure_graph_nodes()}


def missing_dependency_references() -> Tuple[str, ...]:
    ids = set(node_map())
    missing = []
    for node in closure_graph_nodes():
        for dependency in node.dependencies:
            if dependency not in ids:
                missing.append(f"{node.node_id}->{dependency}")
    return tuple(missing)


def graph_status_counts() -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for node in closure_graph_nodes():
        counts[node.status] = counts.get(node.status, 0) + 1
    return counts


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-full-closure-dependency-graph-v1",
        "title": "Full BHSM Closure Dependency Graph v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "nodes": [asdict(node) for node in closure_graph_nodes()],
        "node_count": len(closure_graph_nodes()),
        "status_counts": graph_status_counts(),
        "missing_dependency_references": list(missing_dependency_references()),
        "claim_boundary": "Dependency graph localizes open selectors; it does not claim numerical closure.",
    }

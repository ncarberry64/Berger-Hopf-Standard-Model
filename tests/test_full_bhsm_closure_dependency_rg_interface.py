import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import full_bhsm_closure_dependency_graph as graph
import full_bhsm_freeze_boundary as freeze
import full_bhsm_integrated_status as integrated
import rg_transport_interface as rg
import same_sector_rg_gauge_cancellation as same_sector


DATA_GRAPH = ROOT / "data" / "full_bhsm_closure_dependency_graph_v1.json"
DATA_FREEZE = ROOT / "data" / "full_bhsm_freeze_boundary_v1.json"
DATA_RG = ROOT / "data" / "rg_transport_interface_v1.json"
DATA_STATUS = ROOT / "data" / "full_bhsm_integrated_status_v1.json"
DOCS = (
    ROOT / "docs" / "full_bhsm_closure_dependency_graph_v1.md",
    ROOT / "docs" / "full_bhsm_freeze_boundary_v1.md",
    ROOT / "docs" / "rg_transport_interface_v1.md",
    ROOT / "docs" / "full_bhsm_integrated_status_v1.md",
    ROOT / "docs" / "claim_status_table.md",
    ROOT / "docs" / "open_blockers_backlog.md",
)
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"

EXPECTED_FROZEN_HASHES = {
    FROZEN_MD: "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    FROZEN_JSON: "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_dependency_graph_contains_required_nodes_and_statuses():
    nodes = graph.node_map()
    required = {
        "finite_boundary_algebra",
        "sector_projectors",
        "sector_equations",
        "mode_ledgers",
        "boundary_graded_defect_action_kernel",
        "boundary_graded_defect_action_kernel_v1",
        "charged_Hessian_from_S_index_trace",
        "charged_stiffness_action_source",
        "B_supp_trace_kernel",
        "Rule_A_single_operator_trace",
        "Rule_B_double_normalized_phase_candidate",
        "charged_Kf_generator",
        "rho_ch_exact_value",
        "rho_ch_branch_candidates",
        "charged_stiffness_action_selector",
        "charged_Kf_tridiagonal_bridge_topology",
        "beta_f_reference_bridge_magnitude",
        "kappa_f_tangent_bridge_magnitude",
        "minimal_1_over_21_bridge_seed",
        "up_6_0_Zvirt_threshold",
        "full_threshold_operator",
        "charged_numerical_closure",
        "neutral_sector_operator_kernel",
        "neutrino_mode_ledger",
        "neutral_Hessian_symbolic_form",
        "neutral_Hessian_branch_N0",
        "neutral_Hessian_branch_N1",
        "neutral_Hessian_branch_N2",
        "neutral_eta_source",
        "neutral_beta_bridge_source",
        "neutral_kappa_bridge_source",
        "neutral_threshold_operator",
        "PMNS_structural_source",
        "PMNS_numerical_closure",
        "neutral_numerical_closure",
        "RG_transport_interface",
        "scheme_transport",
        "common_scale_comparison",
        "official_frozen_predictions",
        "numerical_closure",
    }
    assert required.issubset(nodes)
    assert nodes["boundary_graded_defect_action_kernel_v1"].status == (
        "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL"
    )
    assert nodes["B_supp_trace_kernel"].status == "DERIVED_CONDITIONAL"
    assert nodes["Rule_A_single_operator_trace"].status == (
        "DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL"
    )
    assert nodes["rho_ch_exact_value"].status == "OPEN_LOCALIZABLE"
    assert nodes["charged_Hessian_from_S_index_trace"].status == "INVALIDATED_DO_NOT_CLAIM"
    assert nodes["numerical_closure"].status == "OPEN"


def test_dependency_graph_node_integrity_and_no_missing_dependencies():
    for node in graph.closure_graph_nodes():
        assert node.node_id
        assert node.label
        assert node.status
        assert isinstance(node.dependencies, tuple)
        assert isinstance(node.blocks, tuple)
        assert node.evidence_source
        assert isinstance(node.repo_artifact_refs, tuple)
        assert isinstance(node.claim_allowed, bool)
        assert node.claim_text_short
    assert graph.missing_dependency_references() == ()


def test_invalidated_nodes_are_not_freeze_ready():
    invalidated = graph.node_map()["charged_Hessian_from_S_index_trace"]
    assert invalidated.claim_allowed is False
    records = {record.component_id: record for record in freeze.freeze_boundary_records()}
    assert records["charged_Hessian_from_S_index_trace"].freeze_class == (
        "INVALIDATED_DO_NOT_FREEZE"
    )
    assert records["charged_Hessian_from_S_index_trace"].allowed_to_freeze_now is False


def test_freeze_boundary_classifications():
    records = {record.component_id: record for record in freeze.freeze_boundary_records()}
    assert records["sector_equations"].freeze_class == "FROZEN_STRUCTURE_ALLOWED"
    assert records["Rule_A_single_operator_trace"].freeze_class == "FROZEN_STRUCTURE_ALLOWED"
    assert records["rho_ch_branches_1_2_3"].freeze_class == (
        "CANDIDATE_BRANCH_FREEZE_ALLOWED"
    )
    assert records["exact_rho_ch"].freeze_class == "BLOCKED_BY_OPEN_SELECTOR"
    assert records["invented_thresholds_beyond_up_6_0"].freeze_class == (
        "INVALIDATED_DO_NOT_FREEZE"
    )
    assert records["mass_numerical_closure"].freeze_class == "BLOCKED_BY_OPEN_SELECTOR"


def test_rg_transport_stages_and_sector_readiness():
    assert rg.TRANSPORT_STAGES == (
        "BARE_MODE_LEDGER",
        "ACTION_KERNEL_SELECTED",
        "SUPPRESSION_DRESSED",
        "BRIDGE_DRESSED",
        "THRESHOLD_DRESSED",
        "RG_TRANSPORT_PENDING",
        "RG_TRANSPORT_PARTIALLY_LOCALIZED",
        "SCHEME_ALIGNED",
        "COMPARISON_READY",
    )
    assert rg.current_max_stage() == "RG_TRANSPORT_PARTIALLY_LOCALIZED"
    readiness = {record.sector: record for record in rg.comparison_readiness_records()}
    assert readiness["up"].known_thresholds == ("up (6,0): ln 2",)
    assert readiness["up"].current_readiness == "RG_TRANSPORT_PARTIALLY_LOCALIZED"
    assert readiness["up"].gauge_component == "CANCELED_BY_SAME_SECTOR_THEOREM"
    assert readiness["charged_lepton"].comparison_readiness == "NOT_READY"
    assert readiness["down"].known_thresholds == ()
    assert readiness["neutral"].source_operator == "symbolic K_nu"
    assert readiness["neutral"].current_readiness == "RG_TRANSPORT_PENDING"
    assert readiness["neutral"].comparison_readiness == "NOT_READY"
    assert all(record.comparison_readiness != "COMPARISON_READY" for record in readiness.values())
    assert rg.STATUS_TABLE["scheme_alignment"] == "OPEN"


def test_rg_interface_statuses_are_open_scaffold_only():
    report = rg.report_as_dict()
    assert report["statuses"]["RG_transport_interface_v1"] == "STRUCTURAL_SCAFFOLD"
    assert report["statuses"]["same_sector_RG_gauge_cancellation"] == (
        "DERIVED_CONDITIONAL_ON_SHARED_SECTOR_REPRESENTATION"
    )
    assert report["statuses"]["charged_same_sector_RG_gauge_transport"] == (
        "PARTIALLY_LOCALIZED"
    )
    assert report["statuses"]["charged_RG_transport"] == "OPEN_LOCALIZABLE"
    assert report["statuses"]["charged_residual_RG_transport"] == "OPEN_LOCALIZABLE"
    assert report["statuses"]["cross_sector_RG_transport"] == "OPEN"
    assert report["statuses"]["neutral_RG_transport"] == "OPEN_LOCALIZABLE"
    assert report["statuses"]["scheme_transport"] == "OPEN"
    assert report["statuses"]["common_scale_comparison"] == "OPEN"
    assert report["statuses"]["comparison_ready_predictions"] == "OPEN"
    assert report["statuses"]["numerical_closure"] == "OPEN"
    assert report["uses_empirical_derivation_inputs"] is False


def test_integrated_status_counts_and_recommendation():
    report = integrated.report_as_dict()
    assert report["public_status"] == integrated.PUBLIC_STATUS
    assert report["numerical_closure"] == "OPEN"
    assert report["total_node_count"] == len(graph.closure_graph_nodes())
    assert report["derived_or_conditional_count"] > 0
    assert report["candidate_count"] > 0
    assert report["open_localizable_count"] > 0
    assert report["open_count"] > 0
    assert report["invalidated_count"] > 0
    assert report["next_recommended_mathematical_target"] in {
        "RG_TRANSPORT_RULE_DERIVATION",
        "RESIDUAL_YUKAWA_TRANSPORT_RULE",
        "SCHEME_ALIGNMENT_RULE",
        "BRIDGE_MAGNITUDE_ACTION_SOURCE",
        "NEUTRAL_HESSIAN_ACTION_SOURCE",
        "FULL_THRESHOLD_OPERATOR_SOURCE",
    }
    assert report["next_recommended_mathematical_target"] == "RESIDUAL_YUKAWA_TRANSPORT_RULE"


def test_json_artifacts_parse_and_preserve_public_status():
    for path in (DATA_GRAPH, DATA_FREEZE, DATA_RG, DATA_STATUS):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["public_status"] == graph.PUBLIC_STATUS
        assert data["frozen_predictions_changed"] is False
        assert data["official_predictions_changed"] is False
    assert json.loads(DATA_GRAPH.read_text(encoding="utf-8"))[
        "missing_dependency_references"
    ] == []


def test_docs_preserve_expected_status_language():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DOCS)
    required = (
        graph.PUBLIC_STATUS,
        "full_bhsm_closure_dependency_graph_v1=STRUCTURAL_SCAFFOLD",
        "full_bhsm_freeze_boundary_v1=STRUCTURAL_SCAFFOLD",
        "rg_transport_interface_v1=STRUCTURAL_SCAFFOLD",
        "same_sector_RG_gauge_cancellation=DERIVED_CONDITIONAL_ON_SHARED_SECTOR_REPRESENTATION",
        "charged_same_sector_RG_gauge_transport=PARTIALLY_LOCALIZED",
        "charged_RG_transport=OPEN_LOCALIZABLE",
        "charged_residual_RG_transport=OPEN_LOCALIZABLE",
        "cross_sector_RG_transport=OPEN",
        "neutral_RG_transport=OPEN_LOCALIZABLE",
        "scheme_transport=OPEN",
        "common_scale_comparison=OPEN",
        "comparison_ready_predictions=OPEN",
        "numerical_closure=OPEN",
    )
    for phrase in required:
        assert phrase in combined
    forbidden = (
        "comparison-ready predictions achieved",
        "comparison-ready predictions proven",
        "numerical closure achieved",
        "official predictions updated",
        "empirically validated",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_no_empirical_imports_in_new_modules():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            Path(graph.__file__),
            Path(freeze.__file__),
            Path(rg.__file__),
            Path(integrated.__file__),
            Path(same_sector.__file__),
        )
    )
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "gauge_couplings",
        "reference_common_scale",
        "neutrino_mass",
    )
    for item in blocked:
        assert item not in combined


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
    assert integrated.report_as_dict()["frozen_predictions_changed"] is False
    assert integrated.report_as_dict()["official_predictions_changed"] is False

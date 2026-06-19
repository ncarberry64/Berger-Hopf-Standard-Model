import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import boundary_action_source_audit as audit  # noqa: E402


DATA_JSON = ROOT / "data" / "boundary_action_source_audit_kf_v1.json"
DOC = ROOT / "docs" / "boundary_action_source_audit_kf_v1.md"
CLAIM_STATUS = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"

REQUIRED_IDS = {
    "D_C_colored_contact_defect",
    "D_d_color_lower_overlap_contact_defect",
    "Gamma_sigma_weak_orientation_grading",
    "Gamma_T_target_orientation_trace",
    "E3_universal_rank_three_closure",
    "EA_incidence_module_factorization",
    "Delta_IT_index_trace_defect",
    "B_supp_universal_suppression_operator",
    "g_ch_phase_normalized_coupling",
    "R_ch_total_incidence_rank",
    "Pi_f_incidence_projection_fractions",
    "chi_f_incidence_self_screening_counts",
    "S_f_self_screening_factors",
    "eta_f_charged_suppression_constants",
    "N_ch_charged_cost_form",
    "rho_ch_branch_candidates",
    "rho_ch_exact_value",
    "down_sector_admissibility_windows",
    "Kf_tridiagonal_structure",
    "beta_f_reference_bridge",
    "kappa_f_tangent_bridge",
    "tangent_generators",
    "tangent_norms",
    "operator_level_threshold_insertion",
    "Z_virt_u1",
    "mode_identity_branch_tracking",
    "post_diagonal_multiplicative_dressing_prohibition",
    "full_threshold_operator",
    "RG_transport",
    "numerical_closure",
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_audit_table_complete_no_duplicates_and_all_rows_explain_blockers():
    rows = audit.build_audit_table()
    ids = [row.claim_id for row in rows]
    assert REQUIRED_IDS.issubset(set(ids))
    assert len(ids) == len(set(ids))
    for row in rows:
        assert row.status
        assert row.evidence_summary
        assert row.blocking_missing_source
        assert row.forbidden_upgrade_notes


def test_json_artifact_matches_module_and_preserves_global_status():
    data = load_json(DATA_JSON)
    assert data["public_status"] == audit.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert {row["claim_id"] for row in data["rows"]} == {
        row.claim_id for row in audit.build_audit_table()
    }
    assert data["statuses"] == audit.status_by_claim_id()


def test_status_honesty_for_open_and_conditional_claims():
    statuses = audit.status_by_claim_id()
    assert statuses["rho_ch_exact_value"] == "OPEN_LOCALIZABLE"
    assert statuses["full_threshold_operator"] == "OPEN"
    assert statuses["RG_transport"] == "OPEN"
    assert statuses["numerical_closure"] == "OPEN"
    assert statuses["Z_virt_u1"] == "DERIVED_CONDITIONAL"


def test_candidate_not_derived_guardrails_for_key_bridges():
    statuses = audit.status_by_claim_id()
    not_derived_without_direct_action = (
        "g_ch_phase_normalized_coupling",
        "B_supp_universal_suppression_operator",
        "beta_f_reference_bridge",
        "kappa_f_tangent_bridge",
    )
    for claim_id in not_derived_without_direct_action:
        assert statuses[claim_id] != "DERIVED_CONDITIONAL"
        assert statuses[claim_id] != "ACTION_DERIVED"


def test_forbidden_empirical_inputs_are_not_imported():
    combined_source = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "src/boundary_action_source_audit.py",
            "src/charged_kf_generator.py",
        )
    )
    forbidden_imports = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "neutrino",
        "reference_common_scale",
        "fine_structure",
    )
    for name in forbidden_imports:
        assert f"import {name}" not in combined_source
        assert f"from {name}" not in combined_source

    data = load_json(DATA_JSON)
    assert data["uses_empirical_derivation_inputs"] is False
    for phrase in (
        "observed charged-lepton masses",
        "observed quark masses",
        "observed CKM values",
        "observed PMNS values",
        "measured fine-structure alpha",
        "empirical target ratios",
    ):
        assert phrase in data["forbidden_derivation_inputs"]


def test_docs_and_ledgers_contain_required_statuses_and_do_not_overclaim():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC, CLAIM_STATUS, BACKLOG)
    )
    assert audit.PUBLIC_STATUS in combined
    assert "D_C_colored_contact_defect" in combined
    assert "B_supp_universal_suppression_operator" in combined
    assert "g_ch_phase_normalized_coupling" in combined
    assert "rho_ch_exact_value: OPEN_LOCALIZABLE" in combined
    assert "full_threshold_operator: OPEN" in combined
    assert "RG_transport: OPEN" in combined
    assert "numerical_closure: OPEN" in combined
    forbidden = (
        "BHSM is complete.",
        "BHSM is proven.",
        "BHSM is empirically validated",
        "BHSM replaces the Standard Model",
        "BHSM is numerically closed",
        "charged masses are numerically closed by this audit",
        "CKM closure achieved",
        "PMNS closure achieved",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_frozen_prediction_files_remain_unchanged_by_audit():
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()
    data = load_json(DATA_JSON)
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False

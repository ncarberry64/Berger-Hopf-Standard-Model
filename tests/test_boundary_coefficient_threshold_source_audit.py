import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_boundary_coefficient_threshold_source_audit.md"
DOC_PATH = ROOT / "docs" / "bhsm_numerical_input_closure_map.md"
STATUS_PATH = ROOT / "docs" / "current_bhsm_status.md"
CLAIM_TABLE = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_map():
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def entry_by_id(data, entry_id):
    for entry in data["entries"]:
        if entry["id"] == entry_id:
            return entry
    raise AssertionError(f"missing closure-map entry: {entry_id}")


def test_po_bh_63_document_exists_and_names_source_audit_scope():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Boundary-Coefficient and Threshold Selection Source Audit" in text
    assert "coefficient/threshold source audit" in text
    assert "not a profile-solving sprint" in text
    assert "not a numerical prediction sprint" in text


def test_boundary_condition_forms_from_po_bh_62_are_included():
    text = THEORY_PATH.read_text(encoding="utf-8")
    for phrase in (
        "Boundary-Condition Forms From PO-BH-62",
        "T |_{partial B} = T_0",
        "Phi |_{partial B_int} = Phi_0",
        "n^mu partial_mu T |_{partial B} = 0",
        "n^a partial_a Phi |_{partial B_int} = 0",
        "alpha_T T + beta_T n^mu partial_mu T = gamma_T",
        "alpha_Phi Phi + beta_Phi n^a partial_a Phi = gamma_Phi",
        "alpha_T T + beta_T n^mu partial_mu T = J_T",
        "alpha_Phi Phi + beta_Phi n^a partial_a Phi = J_Phi",
    ):
        assert phrase in text


def test_all_eight_audit_routes_are_present():
    text = THEORY_PATH.read_text(encoding="utf-8")
    routes = [
        "Route 1 - Boundary Potential Route",
        "Route 2 - Natural Boundary Condition Route",
        "Route 3 - Dirichlet Level-Set Route",
        "Route 4 - Robin/Mixed Boundary Action Route",
        "Route 5 - Threshold Selection Route",
        "Route 6 - Coefficient Scaling/Equivalence Route",
        "Route 7 - Dimensional Analysis Route",
        "Route 8 - No-Source Result",
    ]
    for route in routes:
        assert route in text


def test_ledgers_and_core_symbols_are_present():
    text = THEORY_PATH.read_text(encoding="utf-8")
    for phrase in (
        "Evidence Table",
        "Coefficient Ledger",
        "Threshold Ledger",
        "alpha_T",
        "beta_T",
        "gamma_T",
        "alpha_Phi",
        "beta_Phi",
        "gamma_Phi",
        "T_0",
        "Phi_0",
        "coefficient_normalization_T",
        "coefficient_ratios_T",
        "coefficient_dimension_family_T",
        "coefficient_dimension_family_Phi",
    ):
        assert phrase in text


def test_required_closure_map_entries_exist_with_expected_statuses():
    data = load_map()
    expected = {
        "coefficient_threshold_source_audit": "COMPLETED",
        "boundary_condition_coefficient_family_T": "DERIVED_CONDITIONAL",
        "boundary_condition_coefficient_family_Phi": "DERIVED_CONDITIONAL",
        "boundary_condition_coefficients_T": "OPEN_LOCALIZABLE",
        "boundary_condition_coefficients_Phi": "OPEN_LOCALIZABLE",
        "coefficient_normalization_T": "OPEN_LOCALIZABLE",
        "coefficient_normalization_Phi": "OPEN_LOCALIZABLE",
        "coefficient_ratios_T": "OPEN_LOCALIZABLE",
        "coefficient_ratios_Phi": "OPEN_LOCALIZABLE",
        "coefficient_dimension_family_T": "DERIVED_CONDITIONAL",
        "coefficient_dimension_family_Phi": "DERIVED_CONDITIONAL",
        "threshold_selection_T_0": "OPEN_LOCALIZABLE",
        "threshold_selection_Phi_0": "OPEN_LOCALIZABLE",
        "T_0_value": "OPEN_LOCALIZABLE",
        "Phi_0_value": "OPEN_LOCALIZABLE",
        "source_terms_J_T": "OPEN_LOCALIZABLE",
        "source_terms_J_Phi": "OPEN_LOCALIZABLE",
        "T_profile_solution": "OPEN_LOCALIZABLE",
        "Phi_profile_solution": "OPEN_LOCALIZABLE",
        "S_nu_topo_value": "OPEN_LOCALIZABLE",
        "epsilon_nu_topo": "OPEN_LOCALIZABLE",
        "neutral_action_evaluation_gate": "OPEN_LOCALIZABLE",
        "profile_solution_gate": "OPEN_LOCALIZABLE",
        "threshold_selection_gate": "OPEN_LOCALIZABLE",
        "coefficient_selection_gate": "OPEN_LOCALIZABLE",
    }
    for key, status in expected.items():
        assert key in data
        assert data[key]["status"] == status
        assert entry_by_id(data, key)["status"] == status
    assert data["coefficient_threshold_source_audit"]["audit_result"] == "COEFFICIENT_FAMILY_PARTIAL_VALUES_OPEN"


def test_values_ratios_sources_thresholds_and_profiles_remain_open_in_document():
    text = THEORY_PATH.read_text(encoding="utf-8")
    required = [
        "boundary_condition_coefficients_T: OPEN_LOCALIZABLE",
        "boundary_condition_coefficients_Phi: OPEN_LOCALIZABLE",
        "coefficient_ratios_T: OPEN_LOCALIZABLE",
        "coefficient_ratios_Phi: OPEN_LOCALIZABLE",
        "source_terms_J_T: OPEN_LOCALIZABLE",
        "source_terms_J_Phi: OPEN_LOCALIZABLE",
        "threshold_selection_T_0: OPEN_LOCALIZABLE",
        "threshold_selection_Phi_0: OPEN_LOCALIZABLE",
        "T_profile_solution: OPEN_LOCALIZABLE",
        "Phi_profile_solution: OPEN_LOCALIZABLE",
        "S_nu_topo_value: OPEN_LOCALIZABLE",
        "epsilon_nu_topo: OPEN_LOCALIZABLE",
        "no coefficient values, coefficient ratios, source terms, T_0, or Phi_0 are derived",
        "T_0 is not derived unless explicit evidence is found",
        "Phi_0 is not derived unless explicit evidence is found",
    ]
    for phrase in required:
        assert phrase in text


def test_docs_preserve_public_status_and_po_bh_63_summary():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG)
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "PO-BH-63 audits existing BHSM structures for sources" in combined
    assert "Coefficient values, coefficient ratios, source terms, thresholds" in combined
    assert "remain open-localizable" in combined


def test_no_affirmative_forbidden_claims_or_closed_values():
    text = THEORY_PATH.read_text(encoding="utf-8")
    forbidden_phrases = [
        "BHSM is proven",
        "BHSM is complete",
        "BHSM replaces the Standard Model",
        "full Standard Model replacement",
        "neutrino masses predicted",
        "PMNS predicted",
        "CKM predicted",
        "local FTL is claimed",
        "experimental FTL is claimed",
        "causality violation is claimed",
        "anomaly validated",
        "propulsion validated",
        "thrust demonstrated",
        "antipode transport demonstrated",
        "S_nu_topo computed",
        "epsilon_nu_topo computed",
        "scalar profile solved",
        "topographic profile solved",
        "T_0 derived",
        "Phi_0 derived",
        "boundary coefficients derived",
        "coefficient values derived",
        "threshold values derived",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in text

    forbidden_assignments = [
        r"T_0\s*=\s*[-+]?\d",
        r"Phi_0\s*=\s*[-+]?\d",
        r"alpha_T\s*=\s*[-+]?\d",
        r"beta_T\s*=\s*[-+]?\d",
        r"gamma_T\s*=\s*[-+]?\d",
        r"alpha_Phi\s*=\s*[-+]?\d",
        r"beta_Phi\s*=\s*[-+]?\d",
        r"gamma_Phi\s*=\s*[-+]?\d",
        r"S_nu_topo\s*=\s*[-+]?\d",
        r"epsilon_nu_topo\s*=\s*[-+]?\d",
    ]
    for pattern in forbidden_assignments:
        assert not re.search(pattern, text)


def test_status_flags_and_prediction_guards_remain_unchanged():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()


def test_forbidden_inputs_and_fit_routes_cover_coefficients_and_thresholds():
    data = load_map()
    entry = data["coefficient_threshold_source_audit"]
    assert entry["derived_numerical_value"] is False
    assert entry["pre_comparison_locked"] is False
    forbidden = set(entry["forbidden_inputs"])
    for item in (
        "observed masses",
        "CKM values",
        "PMNS values",
        "neutrino data",
        "anomaly/FTL data",
        "propulsion/anomaly data",
        "target values",
    ):
        assert item in forbidden
    assert any("fit boundary-condition coefficient values" in route for route in data["forbidden_fit_routes"])


def test_verdict_labels_record_po_bh_63_without_closing_values():
    data = load_map()
    labels = set(data["verdict_labels"])
    for label in (
        "PO_BH_63_COEFFICIENT_THRESHOLD_SOURCE_AUDIT",
        "COEFFICIENT_THRESHOLD_SOURCE_AUDIT_COMPLETED",
        "BOUNDARY_COEFFICIENT_FAMILY_T_DERIVED_CONDITIONAL",
        "BOUNDARY_COEFFICIENT_FAMILY_PHI_DERIVED_CONDITIONAL",
        "BOUNDARY_COEFFICIENT_VALUES_REMAIN_OPEN",
        "COEFFICIENT_RATIOS_REMAIN_OPEN",
        "COEFFICIENT_DIMENSION_FAMILY_DERIVED_CONDITIONAL",
        "THRESHOLD_VALUES_REMAIN_OPEN",
        "SOURCE_TERMS_REMAIN_OPEN",
    ):
        assert label in labels

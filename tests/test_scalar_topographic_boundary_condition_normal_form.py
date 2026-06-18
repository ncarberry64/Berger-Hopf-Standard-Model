import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_scalar_topographic_boundary_condition_normal_form.md"
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


def test_po_bh_62_document_exists_and_names_normal_form_scope():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Scalar/Topographic Boundary Condition Normal Form" in text
    assert "normal-form derivation sprint" in text
    assert "not a numerical prediction sprint" in text
    assert "normal-form closure, not coefficient closure" in text


def test_generic_variational_structure_and_stationarity_are_present():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "delta S = integral_B E[u] delta u + integral_partialB B[u] delta u" in text
    assert "E[u] = 0 in the bulk" in text
    assert "B[u] = 0 on the boundary" in text
    assert "Stationarity requires" in text


def test_boundary_condition_families_are_documented():
    text = THEORY_PATH.read_text(encoding="utf-8")
    for phrase in (
        "Dirichlet Normal Form",
        "Neumann Normal Form",
        "Robin/Mixed Normal Form",
        "Source-Coupled Normal Form",
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


def test_spacetime_and_internal_routes_are_present():
    text = THEORY_PATH.read_text(encoding="utf-8")
    for phrase in (
        "Route A - Spacetime Scalar `T`",
        "F_STF(x,t) = T(x,t) - T_0",
        "normal_derivative_T: DERIVED_CONDITIONAL as form; value OPEN_LOCALIZABLE",
        "Route B - Internal Berger Profile `Phi`",
        "F_int(y) = Phi(y) - Phi_0",
        "n_a = partial_a Phi / sqrt(|g_B^{bc} partial_b Phi partial_c Phi|)",
        "normal_derivative_Phi: DERIVED_CONDITIONAL as form; value OPEN_LOCALIZABLE",
    ):
        assert phrase in text


def test_required_closure_map_entries_exist_with_expected_statuses():
    data = load_map()
    expected = {
        "boundary_condition_normal_form": "DERIVED_CONDITIONAL",
        "spacetime_boundary_condition_form_T": "DERIVED_CONDITIONAL",
        "internal_boundary_condition_form_Phi": "DERIVED_CONDITIONAL",
        "boundary_condition_coefficients_T": "OPEN_LOCALIZABLE",
        "boundary_condition_coefficients_Phi": "OPEN_LOCALIZABLE",
        "threshold_selection_T_0": "OPEN_LOCALIZABLE",
        "threshold_selection_Phi_0": "OPEN_LOCALIZABLE",
        "normal_derivative_T": "DERIVED_CONDITIONAL",
        "normal_derivative_Phi": "DERIVED_CONDITIONAL",
        "T_profile_solution": "OPEN_LOCALIZABLE",
        "Phi_profile_solution": "OPEN_LOCALIZABLE",
        "S_nu_topo_functional": "OPEN_LOCALIZABLE",
        "S_nu_topo_value": "OPEN_LOCALIZABLE",
        "epsilon_nu_topo": "OPEN_LOCALIZABLE",
        "neutral_action_evaluation_gate": "OPEN_LOCALIZABLE",
        "profile_solution_gate": "OPEN_LOCALIZABLE",
        "threshold_selection_gate": "OPEN_LOCALIZABLE",
    }
    for key, status in expected.items():
        assert key in data
        assert data[key]["status"] == status
        assert entry_by_id(data, key)["status"] == status

    assert data["normal_derivative_T"]["status_detail"] == {
        "form": "DERIVED_CONDITIONAL",
        "value": "OPEN_LOCALIZABLE",
    }
    assert data["normal_derivative_Phi"]["status_detail"] == {
        "form": "DERIVED_CONDITIONAL",
        "value": "OPEN_LOCALIZABLE",
    }


def test_coefficients_thresholds_profile_solutions_and_neutral_values_remain_open():
    text = THEORY_PATH.read_text(encoding="utf-8")
    required = [
        "boundary_condition_coefficients_T: OPEN_LOCALIZABLE",
        "boundary_condition_coefficients_Phi: OPEN_LOCALIZABLE",
        "threshold_selection_T_0: OPEN_LOCALIZABLE",
        "threshold_selection_Phi_0: OPEN_LOCALIZABLE",
        "T_profile_solution: OPEN_LOCALIZABLE",
        "Phi_profile_solution: OPEN_LOCALIZABLE",
        "S_nu_topo_value: OPEN_LOCALIZABLE",
        "epsilon_nu_topo: OPEN_LOCALIZABLE",
        "No numerical values for `alpha`, `beta`, `gamma`, or `J` are derived here.",
        "The thresholds `T_0` and `Phi_0` are not derived.",
    ]
    for phrase in required:
        assert phrase in text


def test_docs_preserve_public_status_and_po_bh_62_summary():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG)
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "PO-BH-62 converts the symbolic boundary variation source identified in PO-BH-61" in combined
    assert "Dirichlet, Neumann, Robin/mixed, and conditional source-coupled forms" in combined
    assert "coefficients, thresholds, profile solutions, and neutral suppression values remain open" in combined


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
    ]
    for phrase in forbidden_phrases:
        assert phrase not in text

    forbidden_assignments = [
        r"T_0\s*=\s*[-+]?\d",
        r"Phi_0\s*=\s*[-+]?\d",
        r"alpha_T\s*=\s*[-+]?\d",
        r"beta_T\s*=\s*[-+]?\d",
        r"alpha_Phi\s*=\s*[-+]?\d",
        r"beta_Phi\s*=\s*[-+]?\d",
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


def test_forbidden_inputs_and_fit_routes_cover_boundary_coefficients():
    data = load_map()
    entry = data["boundary_condition_normal_form"]
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
    assert any("fit boundary-condition coefficients" in route for route in data["forbidden_fit_routes"])


def test_verdict_labels_record_po_bh_62_without_closing_numerics():
    data = load_map()
    labels = set(data["verdict_labels"])
    for label in (
        "PO_BH_62_BOUNDARY_CONDITION_NORMAL_FORM",
        "BOUNDARY_CONDITION_NORMAL_FORM_DERIVED_CONDITIONAL",
        "SPACETIME_BOUNDARY_CONDITION_FORM_T_DERIVED_CONDITIONAL",
        "INTERNAL_BOUNDARY_CONDITION_FORM_PHI_DERIVED_CONDITIONAL",
        "BOUNDARY_CONDITION_COEFFICIENTS_T_OPEN_LOCALIZABLE",
        "BOUNDARY_CONDITION_COEFFICIENTS_PHI_OPEN_LOCALIZABLE",
        "PROFILE_SOLUTIONS_REMAIN_OPEN_LOCALIZABLE",
        "NEUTRAL_SUPPRESSION_VALUES_REMAIN_OPEN_LOCALIZABLE",
    ):
        assert label in labels

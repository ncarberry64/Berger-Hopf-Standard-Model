import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_scalar_topographic_profile_eom_source_audit.md"
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


def test_po_bh_61_document_exists_and_names_eom_source_audit_scope():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Scalar/Topographic Profile Equation-of-Motion Source Audit" in text
    assert "derivation-source audit, not a numerical prediction sprint" in text
    assert "partial EOM source found" in text
    assert "does not yet contain a complete explicit spacetime topographic EOM" in text


def test_all_six_candidate_routes_are_audited():
    text = THEORY_PATH.read_text(encoding="utf-8")
    routes = [
        "Route 1 - Existing Scalar/Topographic Action",
        "Route 2 - Collar/Boundary Variation",
        "Route 3 - Level-Set Threshold Selection",
        "Route 4 - Internal Berger Profile Equation",
        "Route 5 - Neutral/Topographic Action Functional",
        "Route 6 - No-Source Result",
    ]
    for route in routes:
        assert route in text


def test_evidence_and_missing_source_tables_are_present():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Evidence Table" in text
    assert "Missing Derivation Source Table" in text
    for phrase in (
        "schematic scalar bulk action",
        "symbolic boundary condition",
        "threshold-selection theorem",
        "complete spacetime EOM",
        "complete internal EOM",
        "derived profile/integration data",
    ):
        assert phrase in text


def test_required_closure_map_entries_exist_with_expected_statuses():
    data = load_map()
    expected = {
        "profile_EOM_source_audit": "COMPLETED",
        "spacetime_topographic_EOM": "OPEN_LOCALIZABLE",
        "internal_Berger_profile_EOM": "OPEN_LOCALIZABLE",
        "profile_boundary_conditions_from_variation": "DERIVED_CONDITIONAL",
        "threshold_selection_T_0": "OPEN_LOCALIZABLE",
        "threshold_selection_Phi_0": "OPEN_LOCALIZABLE",
        "T_profile_solution": "OPEN_LOCALIZABLE",
        "Phi_profile_solution": "OPEN_LOCALIZABLE",
        "S_nu_topo_functional": "OPEN_LOCALIZABLE",
        "S_nu_topo_value": "OPEN_LOCALIZABLE",
        "epsilon_nu_topo": "OPEN_LOCALIZABLE",
        "neutral_action_evaluation_gate": "OPEN_LOCALIZABLE",
        "metric_profile_evaluation_gate": "OPEN_LOCALIZABLE",
        "threshold_selection_gate": "OPEN_LOCALIZABLE",
    }
    for key, status in expected.items():
        assert key in data
        assert data[key]["status"] == status
        assert entry_by_id(data, key)["status"] == status

    assert data["profile_EOM_source_audit"]["audit_result"] == "PARTIAL_EOM_SOURCE_FOUND"
    assert data["profile_boundary_conditions_from_variation"]["status_detail"] == {
        "symbolic_form": "DERIVED_CONDITIONAL",
        "evaluated_values": "OPEN_LOCALIZABLE",
    }


def test_thresholds_profile_solutions_and_neutral_values_remain_open():
    data = load_map()
    text = THEORY_PATH.read_text(encoding="utf-8")
    for key in (
        "threshold_selection_T_0",
        "threshold_selection_Phi_0",
        "T_profile_solution",
        "Phi_profile_solution",
        "S_nu_topo_value",
        "epsilon_nu_topo",
    ):
        assert data[key]["status"] == "OPEN_LOCALIZABLE"

    required = [
        "threshold_selection_T_0: OPEN_LOCALIZABLE",
        "threshold_selection_Phi_0: OPEN_LOCALIZABLE",
        "T_profile_solution: OPEN_LOCALIZABLE",
        "Phi_profile_solution: OPEN_LOCALIZABLE",
        "S_nu_topo_value: OPEN_LOCALIZABLE",
        "epsilon_nu_topo: OPEN_LOCALIZABLE",
        "It does not compute `S_nu_topo` or `epsilon_nu_topo`",
    ]
    for phrase in required:
        assert phrase in text


def test_docs_preserve_public_status_and_po_bh_61_summary():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG)
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "PO-BH-61 audits the scalar/topographic profile equation-of-motion source routes" in combined
    assert "PO-BH-61 completes a derivation-source audit" in combined
    assert "partial source found" in combined
    assert "complete EOM and profile solutions remain `OPEN_LOCALIZABLE`" in combined


def test_forbidden_inputs_are_not_used_as_derivation_sources():
    data = load_map()
    entry = data["profile_EOM_source_audit"]
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
    assert any("fit profile EOM terms" in route for route in data["forbidden_fit_routes"])


def test_no_affirmative_forbidden_claims_or_numeric_assignments():
    text = THEORY_PATH.read_text(encoding="utf-8")
    forbidden_phrases = [
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
        "full Standard Model replacement",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in text

    forbidden_assignments = [
        r"T_0\s*=\s*[-+]?\d",
        r"Phi_0\s*=\s*[-+]?\d",
        r"epsilon_nu_topo\s*=\s*[-+]?\d",
        r"S_nu_topo\s*=\s*[-+]?\d",
    ]
    for pattern in forbidden_assignments:
        assert not re.search(pattern, text)


def test_status_flags_and_frozen_prediction_guards_remain_unchanged():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()


def test_verdict_labels_record_po_bh_61_without_closing_numerics():
    data = load_map()
    labels = set(data["verdict_labels"])
    for label in (
        "PO_BH_61_PROFILE_EOM_SOURCE_AUDIT_COMPLETED",
        "PROFILE_EOM_PARTIAL_SOURCE_FOUND",
        "SPACETIME_TOPOGRAPHIC_EOM_OPEN_LOCALIZABLE",
        "INTERNAL_BERGER_PROFILE_EOM_OPEN_LOCALIZABLE",
        "PROFILE_BOUNDARY_CONDITIONS_FROM_VARIATION_DERIVED_CONDITIONAL",
        "THRESHOLD_SELECTION_T_0_OPEN",
        "THRESHOLD_SELECTION_PHI_0_OPEN",
        "S_NU_TOPO_VALUE_OPEN",
        "EPSILON_NU_TOPO_REMAINS_OPEN_LOCALIZABLE",
    ):
        assert label in labels

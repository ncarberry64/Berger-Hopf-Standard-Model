import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_scalar_topographic_profile_input_classification.md"
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


def test_po_bh_60_document_exists_and_names_input_classification_scope():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Scalar/Topographic Profile Input Classification and Threshold Ledger" in text
    assert "input classification only" in text
    assert "not a numerical prediction" in text
    assert "Localized notation is not a derivation" in text


def test_required_input_ledger_entries_exist_with_expected_statuses():
    data = load_map()
    expected = {
        "T_0": "OPEN_LOCALIZABLE",
        "Phi_0": "OPEN_LOCALIZABLE",
        "topographic_scalar_T_explicit_profile": "LOCALIZED_NOT_NUMERIC",
        "internal_topographic_profile_Phi_explicit_profile": "LOCALIZED_NOT_NUMERIC",
        "T_bg": "LOCALIZED_NOT_NUMERIC",
        "A_T_dip": "LOCALIZED_NOT_NUMERIC",
        "T_loc": "OPEN_LOCALIZABLE",
        "internal_Berger_metric_g_B": "LOCALIZED_NOT_NUMERIC",
        "Berger_radius_r": "OPEN_LOCALIZABLE",
        "Berger_squash_parameter_epsilon": "OPEN_LOCALIZABLE",
        "distinguished_point_y_0": "LOCALIZED_NOT_NUMERIC",
        "profile_equation_of_motion": "OPEN_LOCALIZABLE",
        "profile_boundary_conditions": "OPEN_LOCALIZABLE",
        "gradient_norm_T": "OPEN_LOCALIZABLE",
        "gradient_norm_Phi": "OPEN_LOCALIZABLE",
        "normal_orientation": "OPEN_LOCALIZABLE",
        "K_of_Y": "OPEN_LOCALIZABLE",
        "S_of_Y": "OPEN_LOCALIZABLE",
        "J_of_Y_rho": "DERIVED_CONDITIONAL",
        "S_nu_topo": "OPEN_LOCALIZABLE",
        "epsilon_nu_topo": "OPEN_LOCALIZABLE",
    }
    for key, status in expected.items():
        assert key in data
        assert data[key]["status"] == status
        assert entry_by_id(data, key)["status"] == status

    assert data["J_of_Y_rho"]["status_detail"] == {
        "formula": "DERIVED_CONDITIONAL",
        "value": "OPEN_LOCALIZABLE",
    }


def test_theory_document_includes_routes_and_threshold_ledger():
    text = THEORY_PATH.read_text(encoding="utf-8")
    required = [
        "F_STF(x,t) = T(x,t) - T_0",
        "T(x,t) = T_0",
        "T(x,t) = T_bg(t) + A_T,dip(t)(ihat . uhat) + T_loc(x,t)",
        "F_int(y) = Phi(y) - Phi_0",
        "Phi(y) = Phi_0",
        "Threshold Ledger",
        "`T_0` is not derived",
        "`Phi_0` is not derived",
        "explicit `T(x,t)`",
        "explicit `Phi(y)`",
        "profile equation of motion",
        "profile boundary conditions",
        "gradient norm `|grad T|`",
        "gradient norm `|grad Phi|`",
        "normal orientation",
        "`K(Y)`",
        "`S(Y)`",
        "`J(Y,rho)`",
        "`S_nu_topo`",
        "`epsilon_nu_topo`",
    ]
    for phrase in required:
        assert phrase in text


def test_four_gates_are_documented_and_statused():
    data = load_map()
    text = THEORY_PATH.read_text(encoding="utf-8")
    gates = data["scalar_topographic_profile_input_classification"]["profile_gates"]
    by_id = {gate["id"]: gate for gate in gates}
    assert by_id["gate_1_profile_existence_localization"]["status"] == "PARTIALLY_LOCALIZED"
    assert by_id["gate_2_threshold_selection"]["status"] == "OPEN_LOCALIZABLE"
    assert by_id["gate_3_metric_profile_evaluation"]["status"] == "OPEN_LOCALIZABLE"
    assert by_id["gate_4_neutral_action_evaluation"]["status"] == "OPEN_LOCALIZABLE"

    for phrase in (
        "Gate 1 - profile existence/localization",
        "Gate 2 - threshold selection",
        "Gate 3 - metric/profile evaluation",
        "Gate 4 - neutral action evaluation",
        "Gate 1 is partially localized",
        "Gates 2, 3, and 4 remain open-localizable",
    ):
        assert phrase in text


def test_profile_and_threshold_claims_remain_open_not_computed():
    text = THEORY_PATH.read_text(encoding="utf-8")
    required = [
        "T_0: OPEN_LOCALIZABLE",
        "Phi_0: OPEN_LOCALIZABLE",
        "topographic_scalar_T_explicit_profile: LOCALIZED_NOT_NUMERIC",
        "internal_topographic_profile_Phi_explicit_profile: LOCALIZED_NOT_NUMERIC",
        "J_of_Y_rho: DERIVED_CONDITIONAL formula; OPEN_LOCALIZABLE value",
        "S_nu_topo: OPEN_LOCALIZABLE",
        "epsilon_nu_topo: OPEN_LOCALIZABLE",
        "It does not compute `S_nu_topo` or `epsilon_nu_topo`",
    ]
    for phrase in required:
        assert phrase in text


def test_docs_preserve_public_status_and_po_bh_60_summary():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG)
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "PO-BH-60 classifies the scalar/topographic profile inputs required after PO-BH-59" in combined
    assert "Gate 1 is partially localized; Gates 2, 3, and 4 remain open-localizable" in combined
    assert "`T_0`, `Phi_0`, explicit profile functions, gradient norms, metric/profile values, orientation, `S_nu_topo`, and `epsilon_nu_topo` remain open/localizable" in combined


def test_forbidden_inputs_and_fit_routes_are_explicit():
    data = load_map()
    entry = data["scalar_topographic_profile_input_classification"]
    forbidden = set(entry["forbidden_inputs"])
    for item in (
        "observed masses",
        "CKM values",
        "PMNS values",
        "neutrino data",
        "anomaly/FTL data",
        "propulsion/anomaly data",
        "target values",
        "post-comparison T_0 fit",
        "post-comparison Phi_0 fit",
        "post-comparison S_nu_topo fit",
        "post-comparison epsilon_nu_topo fit",
    ):
        assert item in forbidden

    assert any("fit scalar/topographic profile inputs" in route for route in data["forbidden_fit_routes"])
    assert any("use observed masses" in route and "target values" in route for route in data["forbidden_fit_routes"])


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
        r"K\(Y\)\s*=\s*[-+]?\d",
        r"S\(Y\)\s*=\s*[-+]?\d",
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


def test_verdict_labels_record_po_bh_60_without_closing_numerics():
    data = load_map()
    labels = set(data["verdict_labels"])
    for label in (
        "PO_BH_60_SCALAR_PROFILE_INPUT_CLASSIFICATION",
        "PROFILE_GATE_1_PARTIALLY_LOCALIZED",
        "PROFILE_GATE_2_THRESHOLD_SELECTION_OPEN",
        "PROFILE_GATE_3_METRIC_PROFILE_EVALUATION_OPEN",
        "PROFILE_GATE_4_NEUTRAL_ACTION_EVALUATION_OPEN",
        "T_0_OPEN_LOCALIZABLE",
        "PHI_0_OPEN_LOCALIZABLE",
        "T_EXPLICIT_PROFILE_LOCALIZED_NOT_NUMERIC",
        "PHI_EXPLICIT_PROFILE_LOCALIZED_NOT_NUMERIC",
        "S_NU_TOPO_REMAINS_OPEN_LOCALIZABLE",
        "EPSILON_NU_TOPO_REMAINS_OPEN_LOCALIZABLE",
    ):
        assert label in labels

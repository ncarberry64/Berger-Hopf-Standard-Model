import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_scalar_topographic_level_set_boundary_embedding.md"
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


def test_po_bh_59_objects_and_statuses_exist_in_closure_map():
    data = load_map()
    expected = {
        "boundary_embedding_X": "OPEN_LOCALIZABLE",
        "scalar_topographic_level_set_F": "OPEN_LOCALIZABLE",
        "spacetime_topographic_scalar_T": "LOCALIZED_NOT_NUMERIC",
        "internal_topographic_profile_Phi": "LOCALIZED_NOT_NUMERIC",
        "level_set_unit_normal_n": "DERIVED_CONDITIONAL",
        "level_set_second_fundamental_form_K_AB": "DERIVED_CONDITIONAL",
        "level_set_shape_operator_S": "DERIVED_CONDITIONAL",
        "level_set_boundary_trace_K": "DERIVED_CONDITIONAL",
        "level_set_collar_jacobian_J": "DERIVED_CONDITIONAL",
        "neutral_topographic_action_S_nu_topo": "OPEN_LOCALIZABLE",
        "epsilon_nu_topo": "OPEN_LOCALIZABLE",
    }
    for key, status in expected.items():
        assert key in data
        assert data[key]["status"] == status
        assert entry_by_id(data, key)["status"] == status

    assert data["scalar_topographic_level_set_boundary_embedding"]["status"] == "DERIVED_CONDITIONAL_WITH_OPEN_LEVEL_SET_INPUTS"


def test_theorem_document_exists_and_contains_route_a_and_route_b():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Scalar/Topographic Level-Set Boundary Embedding Theorem" in text
    assert "Route A - Spacetime Scalar/Topographic Route" in text
    assert "F_STF(x,t) = T(x,t) - T_0" in text
    assert "T(x,t) = T_0" in text
    assert "T(x,t) = T_bg(t) + A_T,dip(t)(ihat . uhat) + T_loc(x,t)" in text
    assert "Route B - Internal Berger/Topographic Profile Route" in text
    assert "F_int(y) = Phi(y) - Phi_0" in text
    assert "Phi(y) = Phi_0" in text
    assert "B^3" in text
    assert "radius" in text
    assert "squash parameter" in text
    assert "y_0" in text


def test_level_set_geometry_formulas_and_conditions_are_present():
    text = THEORY_PATH.read_text(encoding="utf-8")
    required = [
        "F(X(Y)) = 0",
        "T(X(Y)) = T_0",
        "Phi(X(Y)) = Phi_0",
        "n_mu = partial_mu F / sqrt(|g^{alpha beta} partial_alpha F partial_beta F|)",
        "n_mu = partial_mu T / sqrt(|g^{alpha beta} partial_alpha T partial_beta T|)",
        "n_a = partial_a Phi / sqrt(|g_B^{bc} partial_b Phi partial_c Phi|)",
        "provided the gradient norm is nonzero",
        "K = nabla_mu n^mu",
        "K_int = nabla_a n^a",
        "K_AB = e_A^mu e_B^nu nabla_mu n_nu",
        "S^A_B = h^{AC} K_CB",
        "K = tr(S) = h^{AB} K_AB",
        "K_AB = P_A^mu P_B^nu nabla_mu nabla_nu F / |grad F|",
        "J(Y,rho)=det(I + rho S(Y))",
        "J(Y,rho)=1 + rho K(Y) + O(rho^2)",
    ]
    for phrase in required:
        assert phrase in text


def test_level_set_profiles_thresholds_and_values_remain_open():
    text = THEORY_PATH.read_text(encoding="utf-8")
    for phrase in (
        "does not derive `T_0`",
        "does not derive `Phi_0`",
        "explicit profile",
        "no numerical/profile closure",
        "Their BHSM numerical/function values are not derived here",
        "does not derive `S_nu_topo`",
        "does not derive the explicit BHSM profile",
    ):
        assert phrase in text


def test_neutral_suppression_remains_open_and_not_numerically_claimed():
    data = load_map()
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert entry_by_id(data, "S_nu_topo")["status"] == "OPEN_LOCALIZABLE"
    assert entry_by_id(data, "epsilon_nu_topo")["status"] == "OPEN_LOCALIZABLE"
    assert data["neutral_topographic_action_S_nu_topo"]["status"] == "OPEN_LOCALIZABLE"
    assert data["epsilon_nu_topo"]["status"] == "OPEN_LOCALIZABLE"
    assert "epsilon_nu_topo = exp(-S_nu_topo)" in text
    assert "M_nu = epsilon_nu_topo M_nu^(0)" in text
    assert "H_nu = epsilon_nu_topo^2 H_nu^(0)" in text


def test_forbidden_inputs_and_fit_routes_cover_level_set_shortcuts():
    data = load_map()
    entry = data["scalar_topographic_level_set_boundary_embedding"]
    forbidden = set(entry["forbidden_inputs"])
    for item in (
        "observed neutrino masses",
        "observed neutrino mass splittings",
        "PMNS angles",
        "PMNS CP phase",
        "CKM values",
        "fitted FTL/anomaly data",
        "propulsion data",
        "post-comparison T_0 fit",
        "post-comparison Phi_0 fit",
        "post-comparison topographic profile fit",
        "post-comparison S_nu_topo fit",
        "post-comparison epsilon_nu_topo fit",
    ):
        assert item in forbidden
    assert any("fit T_0" in route and "propulsion data" in route for route in data["forbidden_fit_routes"])
    assert any("promote point or saddle data" in route for route in data["forbidden_fit_routes"])


def test_no_forbidden_scientific_or_ftl_claims_are_introduced():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (THEORY_PATH, DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG)
    )
    forbidden_phrases = [
        "neutrino masses are predicted",
        "neutrino numerical prediction is achieved",
        "PMNS numerical prediction is achieved",
        "CKM numerical prediction is achieved",
        "anomaly validation is achieved",
        "propulsion validation is achieved",
        "local FTL is claimed",
        "experimental FTL is claimed",
        "local causality violation is claimed",
        "BHSM is proven",
        "BHSM is complete",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in combined

    forbidden_assignments = [
        r"T_0\s*=\s*[-+]?\d",
        r"Phi_0\s*=\s*[-+]?\d",
        r"epsilon_nu_topo\s*=\s*[-+]?\d",
        r"K\(Y\)\s*=\s*[-+]?\d",
        r"S\(Y\)\s*=\s*[-+]?\d",
    ]
    for pattern in forbidden_assignments:
        assert not re.search(pattern, combined)


def test_docs_preserve_public_status_and_po_bh_59_summary():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG)
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "PO-BH-59 localizes two scalar/topographic level-set boundary routes" in combined
    assert "Their thresholds, explicit profiles, metric values, orientation, and numerical/function values remain open" in combined
    assert "No numerical neutrino prediction, PMNS numerical prediction, CKM numerical prediction, local FTL, experimental FTL, anomaly validation, or propulsion validation is claimed" in combined


def test_public_flags_frozen_predictions_and_verdict_labels_remain_guarded():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()

    labels = set(data["verdict_labels"])
    for label in (
        "PO_BH_59_SCALAR_TOPOGRAPHIC_LEVEL_SET_BOUNDARY_CONDITIONAL",
        "SCALAR_TOPOGRAPHIC_LEVEL_SET_F_OPEN",
        "SPACETIME_TOPOGRAPHIC_SCALAR_T_LOCALIZED_NOT_NUMERIC",
        "INTERNAL_TOPOGRAPHIC_PROFILE_PHI_LOCALIZED_NOT_NUMERIC",
        "LEVEL_SET_UNIT_NORMAL_DERIVED_CONDITIONAL",
        "LEVEL_SET_SECOND_FUNDAMENTAL_FORM_DERIVED_CONDITIONAL",
        "LEVEL_SET_SHAPE_OPERATOR_DERIVED_CONDITIONAL",
        "LEVEL_SET_BOUNDARY_TRACE_DERIVED_CONDITIONAL",
        "LEVEL_SET_COLLAR_JACOBIAN_DERIVED_CONDITIONAL",
        "NEUTRAL_TOPOGRAPHIC_ACTION_REMAINS_OPEN_LOCALIZABLE",
        "EPSILON_NU_TOPO_REMAINS_OPEN_LOCALIZABLE",
    ):
        assert label in labels


def test_boundary_saddle_data_are_not_promoted_to_full_embedding():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "y_H" in text
    assert "y_nu" in text
    assert "y_0" in text
    assert "do not by themselves define a full boundary" in text
    assert "promote point or saddle data into a boundary embedding without a profile theorem" in text

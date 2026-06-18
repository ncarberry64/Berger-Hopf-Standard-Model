import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_boundary_embedding_shape_operator.md"
COLLAR_THEORY = ROOT / "theory" / "theorem_discharge_collar_measure_extrinsic_geometry.md"
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


def test_boundary_embedding_shape_operator_objects_exist_in_closure_map():
    data = load_map()
    expected = {
        "boundary_embedding_shape_operator": "DERIVED_CONDITIONAL_WITH_OPEN_EMBEDDING_INPUTS",
        "boundary_embedding_X": "OPEN_LOCALIZABLE",
        "induced_boundary_metric_h_AB": "DERIVED_CONDITIONAL",
        "unit_normal_n": "DERIVED_CONDITIONAL",
        "second_fundamental_form_K_AB": "DERIVED_CONDITIONAL",
        "shape_operator_S": "DERIVED_CONDITIONAL",
        "boundary_trace_K": "DERIVED_CONDITIONAL",
        "collar_jacobian_J": "DERIVED_CONDITIONAL",
    }
    for key, status in expected.items():
        assert key in data
        assert data[key]["status"] == status
        assert entry_by_id(data, key)["status"] == status

    assert entry_by_id(data, "collar_measure")["status"] == "OPEN_LOCALIZABLE"


def test_theorem_includes_required_geometric_formulas_and_routes():
    text = THEORY_PATH.read_text(encoding="utf-8")
    required = [
        "Boundary Embedding / Induced Metric / Shape Operator Theorem",
        "X: partialB -> B",
        "X^mu(Y^A)",
        "e_A^mu = partial_A X^mu",
        "h_AB = g_mu_nu e_A^mu e_B^nu",
        "n_mu e_A^mu = 0",
        "g^{mu nu} n_mu n_nu = 1",
        "K_AB = e_A^mu e_B^nu nabla_mu n_nu",
        "S^A_B = h^{AC} K_CB",
        "K = tr(S) = h^{AB} K_AB",
        "F(x)=0",
        "Phi(x)=Phi_0",
        "n_mu = partial_mu Phi / |grad Phi|",
        "K = nabla_mu n^mu",
        "K_AB ~ P_A^mu P_B^nu nabla_mu nabla_nu Phi / |grad Phi|",
        "J(Y,rho)=det(I + rho S(Y))",
        "J(Y,rho)=1 + rho K(Y) + O(rho^2)",
    ]
    for phrase in required:
        assert phrase in text


def test_theorem_has_six_candidate_routes_and_guarded_statuses():
    text = THEORY_PATH.read_text(encoding="utf-8")
    for route in (
        "Route A - Embedding Pullback Route",
        "Route B - Unit-Normal Route",
        "Route C - Second Fundamental Form Route",
        "Route D - Level-Set / Topographic Boundary Route",
        "Route E - Hessian / Projected Curvature Route",
        "Route F - Collar-Measure Consistency Route",
    ):
        assert route in text

    assert "boundary_embedding_X: OPEN_LOCALIZABLE" in text
    assert "induced_boundary_metric_h_AB: DERIVED_CONDITIONAL" in text
    assert "unit_normal_n: DERIVED_CONDITIONAL" in text
    assert "second_fundamental_form_K_AB: DERIVED_CONDITIONAL" in text
    assert "shape_operator_S: DERIVED_CONDITIONAL" in text
    assert "boundary_trace_K: DERIVED_CONDITIONAL" in text
    assert "collar_jacobian_J: DERIVED_CONDITIONAL" in text
    assert "STRUCTURALLY_MOTIVATED_NOT_DERIVED" in text
    assert "OPEN_LOCALIZABLE" in text


def test_forbidden_inputs_and_fit_routes_are_explicit():
    data = load_map()
    entry = data["boundary_embedding_shape_operator"]
    forbidden = set(entry["forbidden_inputs"])
    for item in (
        "observed neutrino masses",
        "observed neutrino mass splittings",
        "PMNS angles",
        "PMNS CP phase",
        "fitted FTL/anomaly data",
        "post-comparison boundary embedding fit",
        "post-comparison induced metric fit",
        "post-comparison normal fit",
        "post-comparison second fundamental form fit",
        "post-comparison shape-operator fit",
        "post-comparison K(Y) fit",
        "post-comparison J(Y,rho) fit",
    ):
        assert item in forbidden
    assert entry["fit_policy"] == "FORBIDDEN_TO_FIT"
    assert any("boundary embedding" in route and "FTL/anomaly data" in route for route in data["forbidden_fit_routes"])


def test_no_numerical_neutrino_or_ftl_claims_are_introduced():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (THEORY_PATH, DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG)
    )
    forbidden_phrases = [
        "neutrino masses are predicted",
        "neutrino numerical prediction is achieved",
        "PMNS numerical prediction is achieved",
        "experimental FTL is claimed",
        "local FTL is claimed",
        "local causality violation is claimed",
        "full Standard Model replacement is achieved",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in combined

    forbidden_assignments = [
        r"lambda_nu\s*=\s*[-+]?\d",
        r"A_nu\s*=\s*[-+]?\d",
        r"B_nu\s*=\s*[-+]?\d",
        r"K\(Y\)\s*=\s*[-+]?\d",
        r"S\(Y\)\s*=\s*[-+]?\d",
    ]
    for pattern in forbidden_assignments:
        assert not re.search(pattern, combined)


def test_docs_preserve_public_status_and_po_bh_58_language():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG)
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "The boundary embedding, induced metric, unit normal, second fundamental form, shape operator, and trace formulas have been localized or derived conditionally" in combined
    assert "Their numerical/function values remain open unless a BHSM scalar/topographic boundary profile and embedding are derived" in combined
    assert "No numerical neutrino prediction or local FTL claim is made" in combined


def test_public_status_flags_and_frozen_prediction_guards_remain_unchanged():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()


def test_verdict_labels_record_conditional_formula_not_numerical_closure():
    data = load_map()
    labels = set(data["verdict_labels"])
    for label in (
        "PO_BH_58_BOUNDARY_EMBEDDING_SHAPE_OPERATOR_CONDITIONAL",
        "BOUNDARY_EMBEDDING_X_OPEN",
        "INDUCED_BOUNDARY_METRIC_DERIVED_CONDITIONAL",
        "UNIT_NORMAL_DERIVED_CONDITIONAL",
        "SECOND_FUNDAMENTAL_FORM_DERIVED_CONDITIONAL",
        "SHAPE_OPERATOR_FORMULA_DERIVED_CONDITIONAL",
        "BOUNDARY_TRACE_FORMULA_DERIVED_CONDITIONAL",
    ):
        assert label in labels

    assert data["boundary_embedding_shape_operator"]["derived_numerical_value"] is False
    assert data["boundary_embedding_shape_operator"]["pre_comparison_locked"] is False
    assert "numerical/function values remain open" in data["boundary_embedding_shape_operator"]["claim_boundary"]


def test_po_bh_58_links_back_to_po_bh_57_collar_measure():
    po_bh_58 = THEORY_PATH.read_text(encoding="utf-8")
    po_bh_57 = COLLAR_THEORY.read_text(encoding="utf-8")
    assert "J(Y,rho)=det(I + rho S(Y))" in po_bh_58
    assert "J(Y,rho)=det(I + rho S(Y))" in po_bh_57
    assert "K=tr(S)" in po_bh_58
    assert re.search(r"K\(Y\)\s*=\s*tr\(S\)", po_bh_57)

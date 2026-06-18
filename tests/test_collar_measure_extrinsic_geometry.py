import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_collar_measure_extrinsic_geometry.md"
COMPLETE_COLLAR_THEORY = ROOT / "theory" / "theorem_discharge_complete_scalar_topographic_collar_action.md"
COLLAR_THEORY = ROOT / "theory" / "theorem_discharge_collar_geometry_package.md"
DOC_PATH = ROOT / "docs" / "bhsm_numerical_input_closure_map.md"
STATUS_PATH = ROOT / "docs" / "current_bhsm_status.md"
CLAIM_TABLE = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"


def load_map():
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def entry_by_id(data, entry_id):
    for entry in data["entries"]:
        if entry["id"] == entry_id:
            return entry
    raise AssertionError(f"missing closure-map entry: {entry_id}")


def test_collar_measure_extrinsic_geometry_objects_exist_in_closure_map():
    data = load_map()
    for key in (
        "collar_measure_extrinsic_geometry",
        "collar_jacobian_J",
        "boundary_trace_K",
        "shape_operator_S",
    ):
        assert key in data
        assert entry_by_id(data, key)

    assert data["collar_measure_extrinsic_geometry"]["status"] == "DERIVED_CONDITIONAL"
    assert data["collar_jacobian_J"]["status"] == "DERIVED_CONDITIONAL"
    assert data["boundary_trace_K"]["status"] == "OPEN_LOCALIZABLE"
    assert data["shape_operator_S"]["status"] == "OPEN_LOCALIZABLE"
    assert entry_by_id(data, "collar_measure")["status"] == "OPEN_LOCALIZABLE"


def test_theorem_includes_jacobian_and_first_order_expansion():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Collar Measure / Extrinsic Geometry Theorem" in text
    assert "dV_collar = J(Y,rho) dA d rho" in text
    assert "J(Y,0) = 1" in text
    assert "J(Y,rho) = det(I + rho S(Y))" in text
    assert "J(Y,rho) = 1 + rho tr(S)(Y) + O(rho^2)" in text
    assert "J(Y,rho) = 1 + rho K(Y) + O(rho^2)" in text
    assert "K(Y) = tr(S)(Y)" in text


def test_theorem_includes_induced_metric_and_orientation_dependence():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "J(Y,rho) = sqrt(det h(Y,rho) / det h(Y,0))" in text
    assert "h_AB(Y,rho) = h_AB(Y,0) + 2 rho K_AB(Y) + O(rho^2)" in text
    assert "K(Y) = h^{AB}K_AB(Y)" in text
    assert "sign-convention equivalent" in text
    assert "s_n in {+1,-1}" in text
    assert "normal-orientation sign convention" in text


def test_theorem_discusses_divergence_topographic_and_hessian_routes_honestly():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "K(Y) = div_boundary n" in text
    assert "K(Y) = nabla_mu n^mu" in text
    assert "n_mu = partial_mu Phi / sqrt(partial_alpha Phi partial^alpha Phi)" in text
    assert "K ~ Tr_boundary(H_topo)" in text
    assert "STRUCTURALLY_MOTIVATED_NOT_DERIVED" in text
    assert "scalar/topographic profile solution" in text


def test_k_and_shape_operator_are_geometric_not_fitted():
    data = load_map()
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "K(Y) is a geometric trace term, not a fitted parameter" in text
    assert "geometric dependencies, not fitted parameters" in text
    for entry_id in ("collar_measure_extrinsic_geometry", "collar_jacobian_J", "boundary_trace_K", "shape_operator_S"):
        entry = data[entry_id]
        forbidden = set(entry["forbidden_inputs"])
        assert "post-comparison K(Y) fit" in forbidden
        assert "post-comparison shape-operator fit" in forbidden
        assert entry["fit_policy"] == "FORBIDDEN_TO_FIT"


def test_forbidden_inputs_include_neutrino_pmns_and_anomaly_ftl_data():
    data = load_map()
    forbidden = set(data["collar_measure_extrinsic_geometry"]["forbidden_inputs"])
    for item in (
        "observed neutrino masses",
        "observed neutrino mass splittings",
        "PMNS angles",
        "PMNS CP phase",
        "fitted FTL/anomaly data",
        "post-comparison J(Y,rho) fit",
        "post-comparison K(Y) fit",
    ):
        assert item in forbidden
    assert any("K(Y)" in route and "FTL/anomaly data" in route for route in data["forbidden_fit_routes"])


def test_no_numerical_neutrino_or_lambda_robin_values_are_claimed():
    text = "\n".join(
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
    ]
    for phrase in forbidden_phrases:
        assert phrase not in text

    forbidden_assignments = [
        r"lambda_nu\s*=\s*[-+]?\d",
        r"A_nu\s*=\s*[-+]?\d",
        r"B_nu\s*=\s*[-+]?\d",
        r"K\(Y\)\s*=\s*[-+]?\d",
    ]
    for pattern in forbidden_assignments:
        assert not re.search(pattern, text)


def test_docs_preserve_public_status_and_po_bh_57_language():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            THEORY_PATH,
            COMPLETE_COLLAR_THEORY,
            COLLAR_THEORY,
            DOC_PATH,
            STATUS_PATH,
            CLAIM_TABLE,
            BACKLOG,
        )
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "The collar-measure expansion has been derived conditionally from standard collar/extrinsic geometry as a symbolic formula" in combined
    assert "boundary trace/extrinsic curvature data needed to evaluate `K(Y)` remain open" in combined


def test_public_status_flags_and_verdict_labels_remain_guarded():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert "PO_BH_57_COLLAR_MEASURE_EXTRINSIC_GEOMETRY_CONDITIONAL" in data["verdict_labels"]
    assert "COLLAR_JACOBIAN_DERIVED_CONDITIONAL" in data["verdict_labels"]
    assert "BOUNDARY_TRACE_K_OPEN" in data["verdict_labels"]
    assert "SHAPE_OPERATOR_S_OPEN" in data["verdict_labels"]

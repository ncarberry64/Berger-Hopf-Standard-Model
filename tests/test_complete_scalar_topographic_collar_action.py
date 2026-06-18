import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_complete_scalar_topographic_collar_action.md"
COLLAR_THEORY = ROOT / "theory" / "theorem_discharge_collar_geometry_package.md"
NORMAL_THEORY = ROOT / "theory" / "theorem_discharge_normal_coupling_collar_convention.md"
VARIATION_THEORY = ROOT / "theory" / "theorem_discharge_scalar_topographic_boundary_variation.md"
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


def test_complete_collar_action_exists_in_closure_map():
    data = load_map()
    assert "complete_scalar_topographic_collar_action" in data
    action = data["complete_scalar_topographic_collar_action"]
    assert action["id"] == "PO-BH-56"
    assert action["status"] == "OPEN_LOCALIZABLE"
    assert entry_by_id(data, "complete_scalar_topographic_collar_action")["status"] == "OPEN_LOCALIZABLE"
    assert action["derived_numerical_value"] is False
    assert action["pre_comparison_locked"] is False


def test_collar_piece_statuses_remain_honest_open_or_conditional():
    data = load_map()
    expected = {
        "collar_coordinate_rho": "DERIVED_CONDITIONAL",
        "collar_measure": "OPEN_LOCALIZABLE",
        "normal_orientation": "OPEN_LOCALIZABLE",
        "inner_collar_edge_condition": "OPEN_LOCALIZABLE",
        "admissible_collar_variation_data": "OPEN_LOCALIZABLE",
        "robin_coefficients_A_B": "OPEN_LOCALIZABLE",
    }
    for entry_id, status in expected.items():
        assert entry_by_id(data, entry_id)["status"] == status
    assert data["R_nu_normal_coupling"]["status"] == "OPEN_LOCALIZABLE"


def test_theorem_discusses_complete_scalar_topographic_collar_action():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Complete Scalar/Topographic Collar Action Theorem" in text
    assert "S_collar =" in text
    assert "L_collar[Phi, partial_rho Phi, D_A Phi, J, lambda_nu, chi_nu]" in text
    assert "partialB x [0,epsilon]" in text
    assert "not a complete collar action" in text or "not yet define a full `L_collar`" in text


def test_theorem_includes_measure_route_with_curvature_expansion():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "dV_collar = J(Y,rho) dA d rho" in text
    assert "J(Y,0)=1" in text
    assert "J(Y,rho) = 1 + rho K(Y) + O(rho^2)" in text
    assert "extrinsic-curvature" in text or "extrinsic curvature" in text
    assert "collar_measure: OPEN_LOCALIZABLE" in text


def test_theorem_includes_orientation_route():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "n = s_n partial_rho" in text
    assert "s_n in {+1,-1}" in text
    assert "s_n lambda_nu Phi partial_rho Phi" in text
    assert "normal_orientation: OPEN_LOCALIZABLE" in text


def test_theorem_includes_inner_edge_and_variation_data_routes():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "rho=epsilon" in text
    for phrase in ("subsurface neutral channel", "decay/localization", "Neumann", "Dirichlet", "transparent/matching"):
        assert phrase in text
    for phrase in (
        "delta Phi at rho=0",
        "delta partial_rho Phi at rho=0",
        "delta Phi at rho=epsilon",
        "delta partial_rho Phi at rho=epsilon",
    ):
        assert phrase in text
    assert "admissible_collar_variation_data: OPEN_LOCALIZABLE" in text


def test_theorem_includes_robin_coefficient_analysis_without_values():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "R_nu -> A_nu Phi + B_nu n.grad Phi" in text
    assert "A_nu = A_nu[lambda_nu, J, epsilon, edge condition, orientation]" in text
    assert "B_nu = B_nu[lambda_nu, J, epsilon, edge condition, orientation]" in text
    assert "No numerical values for `lambda_nu`, `A_nu`, or `B_nu` are claimed" in text
    forbidden_numeric_assignments = [
        r"lambda_nu\s*=\s*[-+]?\d",
        r"A_nu\s*=\s*[-+]?\d",
        r"B_nu\s*=\s*[-+]?\d",
    ]
    for pattern in forbidden_numeric_assignments:
        assert not re.search(pattern, text)


def test_forbidden_inputs_include_neutrino_pmns_and_anomaly_fit_data():
    data = load_map()
    action_forbidden = set(data["complete_scalar_topographic_collar_action"]["forbidden_inputs"])
    for forbidden in (
        "observed neutrino masses",
        "observed neutrino mass splittings",
        "PMNS angles",
        "PMNS CP phase",
        "fitted FTL/anomaly data",
        "post-comparison L_collar fit",
        "post-comparison Robin coefficient fit",
    ):
        assert forbidden in action_forbidden
    assert any("complete scalar/topographic collar action" in route for route in data["forbidden_fit_routes"])


def test_docs_preserve_public_status_and_no_neutrino_or_ftl_overclaim():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            THEORY_PATH,
            COLLAR_THEORY,
            NORMAL_THEORY,
            VARIATION_THEORY,
            DOC_PATH,
            STATUS_PATH,
            CLAIM_TABLE,
            BACKLOG,
        )
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "The complete scalar/topographic collar action has been audited as the source needed" in combined
    forbidden = [
        "neutrino masses are predicted",
        "neutrino mass prediction is achieved",
        "PMNS numerical prediction is achieved",
        "experimental FTL is claimed",
        "local causality violation is claimed",
        "lambda_nu is derived from observed neutrino masses",
    ]
    for phrase in forbidden:
        assert phrase not in combined


def test_public_status_flags_and_po_bh_56_labels_remain_guarded():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert "PO_BH_56_COMPLETE_SCALAR_TOPOGRAPHIC_COLLAR_ACTION_AUDITED" in data["verdict_labels"]
    assert "COMPLETE_SCALAR_TOPOGRAPHIC_COLLAR_ACTION_OPEN" in data["verdict_labels"]

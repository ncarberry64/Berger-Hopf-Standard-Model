import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
DOC_PATH = ROOT / "docs" / "bhsm_numerical_input_closure_map.md"
STATUS_PATH = ROOT / "docs" / "current_bhsm_status.md"
CLAIM_TABLE = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_neutral_saddle_displacement.md"
S_NU_THEORY_PATH = ROOT / "theory" / "theorem_discharge_neutral_topographic_suppression_action.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_map():
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def entry_by_id(data, entry_id):
    for entry in data["entries"]:
        if entry["id"] == entry_id:
            return entry
    raise AssertionError(f"missing closure-map entry: {entry_id}")


def test_delta_y_nu_exists_in_closure_map():
    data = load_map()
    assert "neutral_saddle_displacement" in data
    displacement = data["neutral_saddle_displacement"]
    assert displacement["id"] == "PO-BH-49"
    assert displacement["symbol"] == "Delta_y_nu"
    assert displacement["status"] == "OPEN_LOCALIZABLE"
    assert entry_by_id(data, "Delta_y_nu")["status"] == "OPEN_LOCALIZABLE"


def test_delta_y_nu_not_derived_with_open_dependencies():
    data = load_map()
    displacement = data["neutral_saddle_displacement"]
    dependency_statuses = {dep["status"] for dep in displacement["depends_on"]}
    assert {"OPEN_LOCALIZABLE", "OPEN_UNRESOLVED"} & dependency_statuses
    assert displacement["status"] != "DERIVED"
    assert displacement["derived_numerical_value"] is False
    assert displacement["pre_comparison_locked"] is False


def test_formula_candidates_include_stationary_or_centroid_displacement():
    data = load_map()
    formulas = data["formulas"]
    displacement = data["neutral_saddle_displacement"]
    stationary = "Delta y_nu = - H_H^{-1} grad_y[delta S_eff^(nu-H)]|_{y_H}"
    centroid = "Delta y_nu = <y>_nu - <y>_H"
    assert formulas["Delta_y_nu"] == "Delta y_nu = y_nu - y_H"
    assert formulas["Delta_y_nu_stationary"] == stationary
    assert formulas["Delta_y_nu_centroid"] == centroid
    assert displacement["formula_candidate"] == stationary
    assert displacement["alternate_formula_candidate"] == centroid


def test_all_four_candidate_routes_are_classified():
    data = load_map()
    routes = data["neutral_saddle_displacement"]["candidate_routes"]
    by_id = {route["id"]: route for route in routes}
    assert by_id["route_A_stationary_point_displacement"]["status"] == "OPEN_LOCALIZABLE"
    assert (
        by_id["route_B_ledger_displacement"]["status"]
        == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    )
    assert (
        by_id["route_C_boundary_operator_displacement"]["status"]
        == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    )
    assert by_id["route_D_finite_width_centroid"]["status"] == "OPEN_LOCALIZABLE"
    assert all(route["forbidden_shortcut"] for route in routes)


def test_forbidden_inputs_include_neutrino_pmns_and_fit_routes():
    data = load_map()
    displacement = data["neutral_saddle_displacement"]
    forbidden = set(displacement["forbidden_inputs"])
    assert "observed neutrino masses" in forbidden
    assert "observed neutrino mass splittings" in forbidden
    assert "PMNS angles" in forbidden
    assert "PMNS CP phase" in forbidden
    assert "post-comparison Delta_y_nu fit" in forbidden
    assert any("Delta_y_nu" in route for route in data["forbidden_fit_routes"])


def test_s_nu_topo_still_depends_on_delta_y_nu_and_remains_open():
    data = load_map()
    action = data["topographic_suppression_action"]
    dependency_ids = {dep["id"] for dep in action["depends_on"]}
    assert "Delta_y_nu" in dependency_ids
    assert action["status"] == "OPEN_LOCALIZABLE"
    assert action["derived_numerical_value"] is False
    assert action["pre_comparison_locked"] is False
    assert entry_by_id(data, "S_nu_topo")["status"] == "OPEN_LOCALIZABLE"


def test_docs_do_not_claim_neutrino_mass_prediction_is_achieved():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG, THEORY_PATH, S_NU_THEORY_PATH)
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "Numerical neutrino closure remains open" in combined
    forbidden = [
        "neutrino mass prediction is achieved",
        "neutrino masses are predicted",
        "PMNS numerical prediction is achieved",
        "Delta y_nu is derived from observed neutrino masses",
        "S_nu_topo is derived",
        "BHSM is proven",
    ]
    for phrase in forbidden:
        assert phrase not in combined


def test_current_public_status_remains_numerical_closure_open():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert "NUMERICAL_CLOSURE_OPEN" in data["verdict_labels"]
    assert "DELTA_Y_NU_NEUTRAL_SADDLE_DISPLACEMENT_OPEN" in data["verdict_labels"]


def test_frozen_prediction_files_remain_unchanged_by_flags():
    data = load_map()
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()


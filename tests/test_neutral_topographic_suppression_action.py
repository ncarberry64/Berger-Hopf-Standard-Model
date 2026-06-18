import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
DOC_PATH = ROOT / "docs" / "bhsm_numerical_input_closure_map.md"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_neutral_topographic_suppression_action.md"
STATUS_PATH = ROOT / "docs" / "current_bhsm_status.md"
CLAIM_TABLE = ROOT / "docs" / "claim_status_table.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_map():
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def entry_by_id(data, entry_id):
    for entry in data["entries"]:
        if entry["id"] == entry_id:
            return entry
    raise AssertionError(f"missing closure-map entry: {entry_id}")


def test_neutral_topographic_relations_exist_in_closure_map():
    data = load_map()
    formulas = data["formulas"]
    assert formulas["epsilon_nu_topo"] == "epsilon_nu_topo = exp(-S_nu_topo)"
    assert formulas["M_nu"] == "M_nu = epsilon_nu_topo M_nu^(0)"
    action = data["topographic_suppression_action"]
    assert action["epsilon_relation"] == "epsilon_nu_topo = exp(-S_nu_topo)"
    assert action["mass_relation"] == "M_nu = epsilon_nu_topo M_nu^(0)"


def test_candidate_gaussian_hessian_formula_is_represented():
    data = load_map()
    action = data["topographic_suppression_action"]
    formula = "S_nu_topo = 1/2 Delta y_nu^T G_nu_topo Delta y_nu + S_barrier"
    assert data["formulas"]["S_nu_topo_gaussian_hessian"] == formula
    assert action["formula_candidate"] == formula
    assert data["formulas"]["G_nu_topo"] == "G_nu_topo = 1/2 E_nu^T H_topo^(nu) E_nu"


def test_s_nu_topo_is_not_marked_derived_with_open_dependencies():
    data = load_map()
    entry = entry_by_id(data, "S_nu_topo")
    action = data["topographic_suppression_action"]
    assert entry["status"] == "OPEN_LOCALIZABLE"
    assert action["status"] == "OPEN_LOCALIZABLE"
    dependency_statuses = {dep["status"] for dep in action["depends_on"]}
    assert {"OPEN_LOCALIZABLE", "OPEN_UNRESOLVED"} & dependency_statuses
    assert action["derived_numerical_value"] is False
    assert action["pre_comparison_locked"] is False


def test_routes_are_classified_and_forbid_fitting():
    data = load_map()
    routes = data["topographic_suppression_action"]["candidate_routes"]
    by_id = {route["id"]: route for route in routes}
    assert by_id["route_A_gaussian_hessian_displacement"]["status"] == "OPEN_LOCALIZABLE"
    assert (
        by_id["route_B_stiffness_mismatch"]["status"]
        == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    )
    assert (
        by_id["route_C_omega_barrier"]["status"]
        == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    )
    assert all("fit" in route["forbidden_shortcut"] for route in routes)


def test_forbidden_inputs_include_neutrino_and_pmns_data():
    data = load_map()
    action = data["topographic_suppression_action"]
    forbidden = set(action["forbidden_inputs"])
    assert "observed neutrino masses" in forbidden
    assert "observed neutrino mass splittings" in forbidden
    assert "PMNS data" in forbidden
    assert "post-comparison epsilon_nu_topo fit" in forbidden
    assert any("S_nu_topo" in route for route in data["forbidden_fit_routes"])


def test_numerical_closure_remains_open_and_public_status_is_conservative():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert "NUMERICAL_CLOSURE_OPEN" in data["verdict_labels"]
    assert "S_NU_TOPO_DERIVATION_OPEN" in data["verdict_labels"]


def test_docs_do_not_claim_neutrino_numerical_prediction_is_achieved():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC_PATH, THEORY_PATH, STATUS_PATH, CLAIM_TABLE)
    )
    assert "Numerical closure remains open" in combined
    assert "numerical neutrino closure remains open" in combined
    forbidden = [
        "neutrino numerical prediction is achieved",
        "numerical neutrino prediction is achieved",
        "PMNS numerical closure is achieved",
        "S_nu_topo is derived from observed neutrino masses",
        "fit S_nu_topo to neutrino scale",
    ]
    for phrase in forbidden[:4]:
        assert phrase not in combined
    assert "S_nu_topo" in combined
    assert "neutrino scale" in combined


def test_topographic_suppression_remains_common_leading_order():
    data = load_map()
    action = data["topographic_suppression_action"]
    assert action["scope"] == "common_leading_order"
    assert action["mode_dependent_correction_theorem_exists"] is False
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "topographic suppression remains common-leading-order" in text


def test_frozen_prediction_files_remain_present_and_map_flags_unchanged():
    data = load_map()
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()

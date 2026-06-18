import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_neutral_effective_action.md"
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


def test_s_eff_nu_exists_in_closure_map():
    data = load_map()
    assert "neutral_effective_action" in data
    action = data["neutral_effective_action"]
    assert action["id"] == "PO-BH-50"
    assert action["symbol"] == "S_eff_nu"
    assert action["status"] == "OPEN_LOCALIZABLE"
    assert entry_by_id(data, "S_eff_nu")["status"] == "OPEN_LOCALIZABLE"


def test_s_eff_nu_not_derived_with_open_dependencies():
    data = load_map()
    action = data["neutral_effective_action"]
    dependency_statuses = {dep["status"] for dep in action["depends_on"]}
    assert {"OPEN_LOCALIZABLE", "OPEN_UNRESOLVED"} & dependency_statuses
    assert action["status"] != "DERIVED"
    assert action["derived_numerical_value"] is False
    assert action["pre_comparison_locked"] is False


def test_theorem_includes_subsurface_neutral_channel_and_causality_guardrail():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "subsurface neutral topographic channel" in text
    assert "exterior-projected anomalous propagation" in text
    assert "apparent FTL from exterior-surface viewpoint" in text
    assert "locally causal in the internal/topographic metric" in text
    assert "experimentally established faster-than-light neutrino propagation" in text
    assert "local dynamical causality claim" in text


def test_theorem_includes_stationary_and_delta_relations():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "grad_y S_eff^(nu)(y_nu) = 0" in text
    assert "delta S_eff^(nu-H) = S_eff^(nu) - S_eff^(H)" in text
    assert "Delta y_nu = - H_H^{-1} grad_y[delta S_eff^(nu-H)]|_{y_H}" in text


def test_all_four_candidate_routes_are_classified():
    data = load_map()
    routes = data["neutral_effective_action"]["candidate_routes"]
    by_id = {route["id"]: route for route in routes}
    assert by_id["route_A_subsurface_neutral_channel_action"]["status"] == "OPEN_LOCALIZABLE"
    assert by_id["route_B_boundary_scalar_topographic_action"]["status"] == "OPEN_LOCALIZABLE"
    assert (
        by_id["route_C_neutral_operator_source"]["status"]
        == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    )
    assert by_id["route_D_finite_width_neutral_profile_action"]["status"] == "OPEN_LOCALIZABLE"
    assert all(route["forbidden_shortcut"] for route in routes)


def test_delta_y_nu_still_depends_on_s_eff_nu():
    data = load_map()
    displacement = data["neutral_saddle_displacement"]
    dependency_ids = {dep["id"] for dep in displacement["depends_on"]}
    assert "S_eff_nu" in dependency_ids
    delta_entry = entry_by_id(data, "Delta_y_nu")
    assert "S_eff_nu" in delta_entry["depends_on"]
    assert delta_entry["status"] == "OPEN_LOCALIZABLE"


def test_s_nu_topo_remains_not_numerically_closed():
    data = load_map()
    action = data["topographic_suppression_action"]
    assert action["status"] == "OPEN_LOCALIZABLE"
    assert action["derived_numerical_value"] is False
    assert action["pre_comparison_locked"] is False
    assert entry_by_id(data, "S_nu_topo")["status"] == "OPEN_LOCALIZABLE"


def test_forbidden_inputs_include_neutrino_masses_pmns_and_fit_routes():
    data = load_map()
    action = data["neutral_effective_action"]
    forbidden = set(action["forbidden_inputs"])
    assert "observed neutrino masses" in forbidden
    assert "observed neutrino mass splittings" in forbidden
    assert "PMNS angles" in forbidden
    assert "PMNS CP phase" in forbidden
    assert "post-comparison S_eff_nu fit" in forbidden
    assert any("S_eff_nu" in route for route in data["forbidden_fit_routes"])


def test_docs_do_not_claim_neutrino_mass_prediction_is_achieved():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (THEORY_PATH, DOC_PATH, STATUS_PATH, CLAIM_TABLE, BACKLOG)
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "Numerical neutrino closure remains open" in combined
    forbidden = [
        "neutrino mass prediction is achieved",
        "neutrino masses are predicted",
        "PMNS numerical prediction is achieved",
        "S_eff^(nu) is derived from observed neutrino masses",
        "locally superluminal dynamics is derived",
    ]
    for phrase in forbidden:
        assert phrase not in combined


def test_current_public_status_remains_exact_and_flags_unchanged():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert "PO_BH_50_NEUTRAL_EFFECTIVE_ACTION_LOCALIZED" in data["verdict_labels"]
    assert "S_EFF_NU_NEUTRAL_ACTION_OPEN" in data["verdict_labels"]

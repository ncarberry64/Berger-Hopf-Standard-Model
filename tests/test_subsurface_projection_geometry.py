import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_subsurface_projection_geometry.md"
EFFECTIVE_ACTION_THEORY = ROOT / "theory" / "theorem_discharge_neutral_effective_action.md"
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


def test_projection_geometry_objects_exist_in_closure_map():
    data = load_map()
    assert "subsurface_projection_geometry" in data
    geometry = data["subsurface_projection_geometry"]
    assert geometry["id"] == "PO-BH-51"
    assert geometry["status"] == "OPEN_LOCALIZABLE"
    for entry_id in ("g_sub", "ellapse_nu", "Pi_sub_to_ext"):
        entry = entry_by_id(data, entry_id)
        assert entry["status"] == "OPEN_LOCALIZABLE"
        assert entry["fit_policy"] == "FORBIDDEN_TO_FIT"


def test_projection_geometry_not_derived_with_open_dependencies():
    data = load_map()
    geometry = data["subsurface_projection_geometry"]
    dependency_statuses = {dep["status"] for dep in geometry["depends_on"]}
    assert {"OPEN_LOCALIZABLE", "OPEN_UNRESOLVED"} & dependency_statuses
    assert geometry["status"] != "DERIVED"
    assert geometry["derived_numerical_value"] is False
    assert geometry["pre_comparison_locked"] is False
    for entry_id in ("g_sub", "ellapse_nu", "Pi_sub_to_ext"):
        assert entry_by_id(data, entry_id)["status"] != "DERIVED"


def test_theorem_contains_subsurface_channel_and_causality_guardrail():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "subsurface neutral topographic channel" in text
    assert "exterior-projected apparent behavior" in text
    assert "BHSM does not claim local causality violation" in text
    assert "locally causal in the internal/topographic metric" in text
    assert "experimental FTL" in text


def test_theorem_uses_apparent_or_exterior_projected_ftl_language():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "apparent FTL" in text
    assert "exterior-projected apparent FTL" in text
    assert "Claim literal local FTL" in text
    assert "does not imply local causality violation" in text


def test_theorem_includes_projection_lapse_and_interval_relations():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "x^a = Pi_sub_to_ext^a(Y)" in text
    assert "ds_ext^2 = g_ext,ab dx^a dx^b" in text
    assert "ds_sub^2 = g_sub,AB dY^A dY^B" in text
    assert "ds_proj^2 = g_ext,ab dPi^a dPi^b" in text
    assert "ellapse_nu^2 = ds_proj^2 / ds_sub^2" in text
    assert "dt_ext = ellapse_nu dt_sub" in text


def test_s_eff_nu_depends_on_projection_geometry():
    data = load_map()
    action = data["neutral_effective_action"]
    dependency_ids = {dep["id"] for dep in action["depends_on"]}
    assert {"g_sub", "ellapse_nu", "Pi_sub_to_ext"} <= dependency_ids
    s_eff_entry = entry_by_id(data, "S_eff_nu")
    assert {"g_sub", "ellapse_nu", "Pi_sub_to_ext"} <= set(s_eff_entry["depends_on"])


def test_delta_y_nu_and_s_nu_topo_remain_not_numerically_closed():
    data = load_map()
    displacement = data["neutral_saddle_displacement"]
    suppression = data["topographic_suppression_action"]
    assert displacement["status"] == "OPEN_LOCALIZABLE"
    assert displacement["derived_numerical_value"] is False
    assert displacement["pre_comparison_locked"] is False
    assert suppression["status"] == "OPEN_LOCALIZABLE"
    assert suppression["derived_numerical_value"] is False
    assert suppression["pre_comparison_locked"] is False


def test_forbidden_inputs_include_neutrino_pmns_and_anomaly_fit_data():
    data = load_map()
    geometry = data["subsurface_projection_geometry"]
    forbidden = set(geometry["forbidden_inputs"])
    assert "observed neutrino masses" in forbidden
    assert "observed neutrino mass splittings" in forbidden
    assert "PMNS angles" in forbidden
    assert "PMNS CP phase" in forbidden
    assert "fitted FTL/anomaly data" in forbidden
    assert "post-comparison ellapse_nu fit" in forbidden
    assert "post-comparison g_sub fit" in forbidden
    assert "post-comparison Pi_sub_to_ext fit" in forbidden
    assert any("g_sub" in route and "ellapse_nu" in route for route in data["forbidden_fit_routes"])


def test_docs_do_not_claim_neutrino_or_ftl_prediction_is_achieved():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            THEORY_PATH,
            EFFECTIVE_ACTION_THEORY,
            DOC_PATH,
            STATUS_PATH,
            CLAIM_TABLE,
            BACKLOG,
        )
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "Numerical neutrino closure remains open" in combined
    forbidden = [
        "neutrino masses are predicted",
        "neutrino mass prediction is achieved",
        "PMNS numerical prediction is achieved",
        "experimental FTL is claimed",
        "local causality violation is claimed",
        "g_sub is derived from observed neutrino masses",
    ]
    for phrase in forbidden:
        assert phrase not in combined


def test_current_public_status_and_prediction_flags_remain_unchanged():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert "PO_BH_51_SUBSURFACE_PROJECTION_GEOMETRY_LOCALIZED" in data["verdict_labels"]
    assert "G_SUB_ELLAPSE_NU_PROJECTION_GEOMETRY_OPEN" in data["verdict_labels"]

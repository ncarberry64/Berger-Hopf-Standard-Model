import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_neutral_boundary_tensors.md"
EFFECTIVE_ACTION_THEORY = ROOT / "theory" / "theorem_discharge_neutral_effective_action.md"
PROJECTION_THEORY = ROOT / "theory" / "theorem_discharge_subsurface_projection_geometry.md"
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


def test_neutral_boundary_objects_exist_in_closure_map():
    data = load_map()
    assert "neutral_boundary_tensors" in data
    tensors = data["neutral_boundary_tensors"]
    assert tensors["id"] == "PO-BH-52"
    assert tensors["status"] == "OPEN_LOCALIZABLE"
    for entry_id in ("chi_nu_AB", "lambda_nu", "neutral_boundary_condition"):
        entry = entry_by_id(data, entry_id)
        assert entry["status"] == "OPEN_LOCALIZABLE"
        assert entry["fit_policy"] == "FORBIDDEN_TO_FIT"


def test_neutral_boundary_objects_not_derived_with_open_dependencies():
    data = load_map()
    tensors = data["neutral_boundary_tensors"]
    dependency_statuses = {dep["status"] for dep in tensors["depends_on"]}
    assert {"OPEN_LOCALIZABLE", "OPEN_UNRESOLVED"} & dependency_statuses
    assert tensors["status"] != "DERIVED"
    assert tensors["derived_numerical_value"] is False
    assert tensors["pre_comparison_locked"] is False
    for entry_id in ("chi_nu_AB", "lambda_nu", "neutral_boundary_condition"):
        assert entry_by_id(data, entry_id)["status"] != "DERIVED"


def test_theorem_includes_neutral_boundary_action_with_chi_and_lambda():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "S_partial^(nu)" in text
    assert "1/2 chi_nu^{AB} partial_A Phi partial_B Phi" in text
    assert "lambda_nu(nhat) Phi nhat.grad Phi" in text
    assert "S_bulk[Phi] + S_partial^(nu)[Phi]" in text


def test_theorem_includes_variational_boundary_condition_candidate():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Varying the bulk and boundary pieces" in text
    assert "n_mu partial^mu Phi + B_nu[chi_nu, lambda_nu, Phi] = 0 on partialB" in text
    assert "boundary integration-by-parts convention" in text


def test_omega_nu_is_not_automatically_tensor_derivation():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Omega_nu = -q - 2j = -k" in text
    assert "not automatically enough to derive tensor values" in text
    assert "operator-to-tensor proof" in text


def test_theorem_relates_tensors_to_s_eff_and_subsurface_channel():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "shared dependencies for `S_eff_nu`" in text
    assert "subsurface neutral topographic channel" in text
    assert "g_sub, ellapse_nu, Pi_sub_to_ext" in text
    assert "chi_nu^{AB} ~ f_nu(y) g_sub^{AB}" in text
    assert "chi_parallel P_parallel" in text


def test_theorem_denies_local_causality_violation_and_experimental_ftl():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (THEORY_PATH, PROJECTION_THEORY)
    )
    assert "No claim of local causality violation is made" in combined
    assert "No claim of experimental FTL is made" in combined
    assert "exterior-projected anomalous propagation remains interpretive" in combined


def test_s_eff_nu_and_projection_geometry_depend_on_boundary_objects():
    data = load_map()
    action_ids = {dep["id"] for dep in data["neutral_effective_action"]["depends_on"]}
    projection_ids = {dep["id"] for dep in data["subsurface_projection_geometry"]["depends_on"]}
    assert {"chi_nu_AB", "lambda_nu", "neutral_boundary_condition"} <= action_ids
    assert {"chi_nu_AB", "lambda_nu", "neutral_boundary_condition"} <= projection_ids
    s_eff_entry = entry_by_id(data, "S_eff_nu")
    assert {"chi_nu_AB", "lambda_nu", "neutral_boundary_condition"} <= set(
        s_eff_entry["depends_on"]
    )


def test_forbidden_inputs_include_neutrino_pmns_and_anomaly_fit_data():
    data = load_map()
    tensors = data["neutral_boundary_tensors"]
    forbidden = set(tensors["forbidden_inputs"])
    assert "observed neutrino masses" in forbidden
    assert "observed neutrino mass splittings" in forbidden
    assert "PMNS angles" in forbidden
    assert "PMNS CP phase" in forbidden
    assert "fitted FTL/anomaly data" in forbidden
    assert "post-comparison chi_nu fit" in forbidden
    assert "post-comparison lambda_nu fit" in forbidden
    assert "post-comparison neutral boundary condition fit" in forbidden
    assert any("chi_nu" in route and "lambda_nu" in route for route in data["forbidden_fit_routes"])


def test_docs_preserve_public_status_and_no_prediction_or_ftl_claims():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            THEORY_PATH,
            EFFECTIVE_ACTION_THEORY,
            PROJECTION_THEORY,
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
        "chi_nu is derived from observed neutrino masses",
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
    assert "PO_BH_52_NEUTRAL_BOUNDARY_TENSORS_LOCALIZED" in data["verdict_labels"]
    assert "NEUTRAL_BOUNDARY_TENSORS_CONDITION_OPEN" in data["verdict_labels"]

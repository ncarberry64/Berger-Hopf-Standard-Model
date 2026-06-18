import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_scalar_topographic_boundary_variation.md"
BOUNDARY_TENSORS_THEORY = ROOT / "theory" / "theorem_discharge_neutral_boundary_tensors.md"
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


def test_explicit_boundary_variation_exists_in_closure_map():
    data = load_map()
    assert "explicit_scalar_topographic_boundary_variation" in data
    variation = data["explicit_scalar_topographic_boundary_variation"]
    assert variation["id"] == "PO-BH-53"
    assert variation["status"] == "DERIVED_CONDITIONAL"
    assert variation["derived_numerical_value"] is False
    assert variation["pre_comparison_locked"] is False
    assert entry_by_id(data, "explicit_scalar_topographic_boundary_variation")["status"] == "DERIVED_CONDITIONAL"


def test_theorem_includes_bulk_boundary_term_and_variation():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "S_bulk =" in text
    assert "1/2 g^{mu nu} partial_mu Phi partial_nu Phi" in text
    assert "delta S_bulk|boundary" in text
    assert "n_mu partial^mu Phi" in text
    assert "bulk Euler-Lagrange term" in text


def test_theorem_varies_chi_tangential_gradient_term():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "1/2 chi_nu^{AB} D_A Phi D_B Phi" in text
    assert "delta S_chi" in text
    assert "D_A(chi_nu^{AB} D_B Phi)" in text
    assert "-D_A(chi_nu^{AB}D_B Phi)" in text
    assert "boundary integration by parts" in text


def test_theorem_treats_lambda_normal_coupling_ambiguity():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "lambda_nu Phi n.grad Phi" in text
    assert "lambda_nu Phi n.grad(delta Phi)" in text
    assert "R_nu[lambda_nu, Phi, n.grad Phi]" in text
    assert "collar/normal-variation convention" in text


def test_theorem_includes_assumptions_block():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "## Assumptions" in text
    assert "boundary has no boundary" in text
    assert "chi_nu^{AB}` is symmetric" in text
    assert "background boundary geometry" in text
    assert "normal-derivative term" in text
    assert "Local causality is not addressed by this theorem" in text


def test_neutral_boundary_condition_symbolic_status_but_tensors_open():
    data = load_map()
    condition = entry_by_id(data, "neutral_boundary_condition")
    chi = entry_by_id(data, "chi_nu_AB")
    lam = entry_by_id(data, "lambda_nu")
    assert condition["status"] == "DERIVED_CONDITIONAL"
    assert "D_A(chi_nu^{AB} D_B Phi)" in condition["formula_candidate"]
    assert "R_nu[lambda_nu, Phi, n.grad Phi]" in condition["formula_candidate"]
    assert chi["status"] == "OPEN_LOCALIZABLE"
    assert lam["status"] == "OPEN_LOCALIZABLE"
    assert "post-comparison chi_nu fit" in chi["forbidden_inputs"]
    assert "post-comparison lambda_nu fit" in lam["forbidden_inputs"]


def test_forbidden_inputs_include_neutrino_pmns_and_anomaly_fit_data():
    data = load_map()
    variation = data["explicit_scalar_topographic_boundary_variation"]
    forbidden = set(variation["forbidden_inputs"])
    assert "observed neutrino masses" in forbidden
    assert "observed neutrino mass splittings" in forbidden
    assert "PMNS angles" in forbidden
    assert "PMNS CP phase" in forbidden
    assert "fitted FTL/anomaly data" in forbidden
    assert "post-comparison neutral boundary condition fit" in forbidden


def test_docs_preserve_public_status_and_no_prediction_or_ftl_claims():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            THEORY_PATH,
            BOUNDARY_TENSORS_THEORY,
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
    assert "PO_BH_53_SCALAR_TOPOGRAPHIC_BOUNDARY_VARIATION_CONDITIONAL" in data["verdict_labels"]
    assert "EXPLICIT_SCALAR_TOPOGRAPHIC_BOUNDARY_VARIATION_DERIVED_CONDITIONAL" in data["verdict_labels"]

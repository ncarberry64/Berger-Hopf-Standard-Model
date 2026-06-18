import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_normal_coupling_collar_convention.md"
BOUNDARY_VARIATION_THEORY = ROOT / "theory" / "theorem_discharge_scalar_topographic_boundary_variation.md"
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


def test_normal_coupling_objects_exist_in_closure_map():
    data = load_map()
    assert "R_nu_normal_coupling" in data
    assert "normal_collar_convention" in data
    assert data["R_nu_normal_coupling"]["id"] == "PO-BH-54"
    assert data["R_nu_normal_coupling"]["status"] == "OPEN_LOCALIZABLE"
    assert data["normal_collar_convention"]["status"] == "OPEN_LOCALIZABLE"
    assert entry_by_id(data, "R_nu_normal_coupling")["status"] == "OPEN_LOCALIZABLE"
    assert entry_by_id(data, "normal_collar_convention")["status"] == "OPEN_LOCALIZABLE"


def test_theorem_includes_lambda_normal_term_and_fixed_normal_route():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "lambda_nu Phi n.grad Phi" in text
    assert "Fixed Normal Derivative Convention" in text
    assert "R_nu = lambda_nu n.grad Phi" in text
    assert "DERIVED_CONDITIONAL" in text
    assert "restricted convention" in text


def test_theorem_includes_symmetrized_and_collar_routes():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Phi n.grad Phi = 1/2 n.grad(Phi^2)" in text
    assert "S_collar =" in text
    assert "partialB x [0,epsilon]" in text
    assert "lambda_nu(rho,Y) Phi partial_rho Phi" in text
    assert "inner collar edge" in text


def test_theorem_includes_robin_candidate_or_rejection():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "Robin Boundary Condition Route" in text
    assert "A_nu Phi + B_nu n.grad Phi - D_A(chi_nu^{AB}D_B Phi) = 0" in text
    assert "A_nu and B_nu" in text
    assert "not derived" in text


def test_theorem_includes_assumptions_block_and_guardrails():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "## Assumptions" in text
    assert "boundary embedding is fixed" in text
    assert "delta(n.grad Phi)" in text
    assert "delta Phi is free on the boundary" in text
    assert "lambda_nu` is treated as a background coefficient" in text
    assert "No claim of local causality violation is made" in text
    assert "No claim of experimental FTL is made" in text


def test_lambda_value_remains_open_and_not_numerically_derived():
    data = load_map()
    lam = entry_by_id(data, "lambda_nu")
    rnu = data["R_nu_normal_coupling"]
    collar = data["normal_collar_convention"]
    assert lam["status"] == "OPEN_LOCALIZABLE"
    assert "R_nu_normal_coupling" in lam["depends_on"]
    assert "normal_collar_convention" in lam["depends_on"]
    assert rnu["derived_numerical_value"] is False
    assert collar["derived_numerical_value"] is False
    assert "post-comparison lambda_nu fit" in rnu["forbidden_inputs"]


def test_neutral_boundary_condition_keeps_symbolic_status_with_open_rnu():
    data = load_map()
    condition = entry_by_id(data, "neutral_boundary_condition")
    assert condition["status"] == "DERIVED_CONDITIONAL"
    assert "R_nu_normal_coupling" in condition["depends_on"]
    assert "normal_collar_convention" in condition["depends_on"]
    assert data["R_nu_normal_coupling"]["status"] == "OPEN_LOCALIZABLE"


def test_forbidden_inputs_include_neutrino_pmns_and_anomaly_fit_data():
    data = load_map()
    rnu_forbidden = set(data["R_nu_normal_coupling"]["forbidden_inputs"])
    collar_forbidden = set(data["normal_collar_convention"]["forbidden_inputs"])
    for forbidden in (rnu_forbidden, collar_forbidden):
        assert "observed neutrino masses" in forbidden
        assert "observed neutrino mass splittings" in forbidden
        assert "PMNS angles" in forbidden
        assert "PMNS CP phase" in forbidden
        assert "fitted FTL/anomaly data" in forbidden
    assert any("R_nu" in route and "collar" in route for route in data["forbidden_fit_routes"])


def test_docs_preserve_public_status_and_no_prediction_or_ftl_claims():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            THEORY_PATH,
            BOUNDARY_VARIATION_THEORY,
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
        "lambda_nu is derived from observed neutrino masses",
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
    assert "PO_BH_54_NORMAL_COUPLING_COLLAR_CONVENTION_LOCALIZED" in data["verdict_labels"]
    assert "R_NU_NORMAL_COUPLING_COLLAR_CONVENTION_OPEN" in data["verdict_labels"]

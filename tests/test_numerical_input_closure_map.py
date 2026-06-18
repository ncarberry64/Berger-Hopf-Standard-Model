import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
DOC_PATH = ROOT / "docs" / "bhsm_numerical_input_closure_map.md"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_numerical_input_closure_map.md"
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


def test_closure_map_exists_and_guardrail_flags():
    data = load_map()
    assert data["id"] == "PO-BH-47"
    assert data["official_predictions_changed"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["standard_model_fully_derived"] is False
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["pre_comparison_lock_required"] is True


def test_all_four_ledgers_are_exact():
    data = load_map()
    assert data["ledgers"]["charged_lepton"] == [[0, 0], [1, 2], [3, 3]]
    assert data["ledgers"]["neutrino"] == [[0, 0], [3, 0], [1, 1]]
    assert data["ledgers"]["up"] == [[0, 0], [6, 0], [8, 1]]
    assert data["ledgers"]["down"] == [[0, 0], [0, 3], [4, 2]]


def test_neutrino_k_values_and_neutral_moment_costs():
    data = load_map()
    assert data["neutral_k_values"] == [0, 3, 3]
    assert data["neutral_off_diagonal_moment_costs"] == {
        "M_nu(1,1)": 2,
        "M_nu(-2,1)": 5,
        "M_nu(3,0)": 9,
    }


def test_neutral_suppression_and_pmns_phase_loop_formulas():
    data = load_map()
    formulas = data["formulas"]
    assert formulas["epsilon_nu_topo"] == "epsilon_nu_topo = exp(-S_nu_topo)"
    assert formulas["pmns_phase_loop"] == "Phi_nu = phiA + varphi - phiB"
    assert "Delta m_+-^2" in formulas["neutral_mass_splitting"]
    assert formulas["neutral_mixing_angle"] == "tan 2 theta_AB = 2 |delta|/(DeltaB-DeltaA)"


def test_ckm_phase_source_is_sector_relative_not_absolute():
    data = load_map()
    assert data["phase_admissibility"]["absolute_alpha0_physical"] is False
    assert data["phase_admissibility"]["absolute_gamma0_physical"] is False
    assert data["phase_admissibility"]["sector_relative_sampling_required"] is True
    assert data["formulas"]["ckm_phase_loop"] == "arg(Theta_12 Theta_23 Theta_13*)"


def test_open_numerical_inputs_are_not_accidentally_derived():
    data = load_map()
    open_ids = [
        "G_f",
        "C_f",
        "P_f",
        "B_f",
        "kappa_f",
        "R_f",
        "D_f",
        "Y_u",
        "Y_d",
        "G_f_mix",
        "M_f_Delta",
        "Gamma_f_ij",
        "Q_f_ij",
        "eigenvalue_gaps",
        "S_nu_topo",
        "lambda0",
        "lambda3",
        "Delta0",
        "DeltaA",
        "DeltaB",
        "etaA",
        "etaB",
        "delta",
        "phiA",
        "phiB",
        "varphi",
        "scalar_topographic_decoupling_proof",
        "stability_proof",
    ]
    for entry_id in open_ids:
        assert entry_by_id(data, entry_id)["status"] != "DERIVED"


def test_ckm_one_sixteenth_exponent_remains_not_derived():
    data = load_map()
    entry = entry_by_id(data, "ckm_1_16_exponent")
    assert entry["status"] == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert "CKM_1_16_EXPONENT_NOT_DERIVED" in data["verdict_labels"]


def test_forbidden_fit_routes_are_explicit():
    data = load_map()
    routes = data["forbidden_fit_routes"]
    assert any("CKM 1/16" in route for route in routes)
    assert any("S_nu_topo" in route for route in routes)
    assert any("PMNS phase" in route for route in routes)
    assert all(entry["fit_policy"] == "FORBIDDEN_TO_FIT" for entry in data["entries"])


def test_claim_status_table_contains_required_safe_labels():
    text = CLAIM_TABLE.read_text(encoding="utf-8")
    required = [
        "Finite algebra",
        "SM-like charges",
        "Gauge normalization scaffold",
        "Charged hierarchy mechanism",
        "CKM source",
        "CKM CP source",
        "Neutral topographic suppression route",
        "PMNS source",
        "PMNS CP source",
        "Full numerical SM prediction",
        "Replacement readiness",
    ]
    for label in required:
        assert label in text


def test_docs_state_numerical_closure_open_and_no_overclaim():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (DOC_PATH, THEORY_PATH, CLAIM_TABLE)
    )
    assert "Numerical closure remains open" in combined
    forbidden_phrases = [
        "BHSM has fully numerically derived the Standard Model",
        "fully numerically derived the Standard Model",
        "full numerical Standard Model derivation is complete",
        "replacement readiness achieved",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in combined


def test_frozen_prediction_files_unchanged_by_closure_map():
    data = load_map()
    assert data["frozen_predictions_changed"] is False
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()

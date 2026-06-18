import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_one_loop_rg as rg  # noqa: E402


def test_one_loop_rg_results_schema_and_labels():
    payload = rg.export_outputs(ROOT)
    parsed = json.loads(
        (ROOT / "theory" / "theorem_discharge_one_loop_rg_results.json").read_text(
            encoding="utf-8"
        )
    )
    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-one-loop-rg-boundary-content-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["one_loop_rg_layer_discharged_conditionally"] is True
    assert parsed["measured_couplings_predicted"] is False
    assert parsed["two_loop_rg_derived"] is False
    assert parsed["beta_coefficients"] == {
        "convention": "dg_i/dlnmu = b_i g_i^3/(16 pi^2)",
        "b1": "41/10",
        "b2": "-19/6",
        "b3": "-7",
    }

    labels = set(parsed["verdict_labels"])
    assert "PO_BH_15_ONE_LOOP_RG_COEFFICIENTS_FROM_BOUNDARY_CONTENT_DERIVED_CONDITIONAL" in labels
    assert "BETA_COEFFICIENTS_41_10_NEG_19_6_NEG_7_DERIVED_CONDITIONAL" in labels
    assert "MEASURED_COUPLINGS_REMAIN_OPEN" in labels
    assert "TWO_LOOP_RG_REMAINS_OPEN" in labels


def test_one_loop_rg_required_files_exist():
    rg.export_outputs(ROOT)
    required = [
        "theorem_discharge_one_loop_rg_boundary_content.md",
        "derived_one_loop_rg_formula_boundary.md",
        "derived_boundary_fermion_trace_sums.md",
        "derived_boundary_scalar_trace_sums.md",
        "derived_boundary_beta_coefficients.md",
        "one_loop_rg_non_tautology_audit.md",
        "theorem_discharge_one_loop_rg_results.json",
    ]
    for name in required:
        assert (ROOT / "theory" / name).exists()

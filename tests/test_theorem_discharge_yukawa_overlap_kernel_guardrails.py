import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_yukawa_overlap_kernel_main_doc_contains_required_language():
    k.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_yukawa_overlap_kernel_selection.md").read_text()
    assert k.MISSION_LANGUAGE in text
    assert k.CONCLUSION_LANGUAGE in text
    assert "No CKM or PMNS values are derived." in text


def test_yukawa_overlap_kernel_proof_ledger_and_downstream_guardrails():
    ledger = k.proof_discharge_ledger()
    assert "PO-BH-20" in ledger
    assert ledger["PO-BH-20"].status == k.DischargeStatus.DERIVED_CONDITIONAL
    payload = k.build_results_payload()
    assert payload["discharged_obligations"]["PO-BH-20"].startswith("DERIVED_CONDITIONAL")
    assert payload["numerical_overlap_values_derived"] is False
    assert payload["fermion_mass_ratios_derived"] is False
    assert payload["ckm_values_derived"] is False
    assert payload["pmns_values_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
    assert "numerical boundary overlap kernel theorem" in payload["still_open_downstream"]


def test_yukawa_overlap_kernel_replacement_claim_remains_false():
    assert k.replacement_claim_ready() is False
    payload = k.build_results_payload()
    assert payload["standard_model_fully_derived"] is False
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False

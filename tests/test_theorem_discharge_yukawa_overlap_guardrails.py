import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap as yo  # noqa: E402


def test_yukawa_overlap_main_doc_contains_required_language():
    yo.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_yukawa_overlap_texture_source.md").read_text()
    assert yo.MISSION_LANGUAGE in text
    assert yo.CONCLUSION_LANGUAGE in text
    assert "No CKM or PMNS numerical values are derived here." in text


def test_yukawa_overlap_proof_ledger_and_downstream_guardrails():
    ledger = yo.proof_discharge_ledger()
    assert "PO-BH-19" in ledger
    assert ledger["PO-BH-19"].status == yo.DischargeStatus.DERIVED_CONDITIONAL
    payload = yo.build_results_payload()
    assert payload["discharged_obligations"]["PO-BH-19"].startswith("DERIVED_CONDITIONAL")
    assert payload["numerical_yukawa_values_derived"] is False
    assert payload["fermion_mass_ratios_derived"] is False
    assert payload["ckm_values_derived"] is False
    assert payload["pmns_values_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
    assert "numerical boundary overlap theorem" in payload["still_open_downstream"]


def test_yukawa_overlap_replacement_claim_remains_false():
    assert yo.replacement_claim_ready() is False
    payload = yo.build_results_payload()
    assert payload["standard_model_fully_derived"] is False
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False

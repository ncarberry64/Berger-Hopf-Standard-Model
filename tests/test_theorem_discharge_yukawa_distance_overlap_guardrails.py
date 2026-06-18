import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_distance_overlap as d  # noqa: E402


def test_distance_overlap_main_doc_contains_required_language_and_safe_conclusion():
    d.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_yukawa_distance_overlap_law.md").read_text()
    assert d.MISSION_LANGUAGE in text
    assert d.SAFE_CONCLUSION in text
    assert "Numerical overlap values are not derived in this branch." in text


def test_distance_overlap_proof_ledger_is_partial():
    ledger = d.proof_discharge_ledger()
    assert "PO-BH-21" in ledger
    assert ledger["PO-BH-21"].status == "PARTIAL"
    payload = d.build_results_payload()
    assert payload["discharged_obligations"]["PO-BH-21"].startswith("PARTIAL")
    assert payload["distance_overlap_law_discharged_conditionally"] is False
    assert payload["bhsm_replacement_claim_ready"] is False


def test_distance_overlap_downstream_claims_remain_false():
    assert d.numerical_overlap_values_derived() is False
    assert d.fermion_mass_ratios_derived() is False
    assert d.ckm_values_derived() is False
    assert d.pmns_values_derived() is False
    assert d.replacement_claim_ready() is False

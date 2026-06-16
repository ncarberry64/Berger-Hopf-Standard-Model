import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_yukawa_main_doc_contains_required_mission_and_conclusion_language():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_yukawa_operator_closure.md").read_text()
    assert y.MISSION_LANGUAGE in text
    assert y.CONCLUSION_LANGUAGE in text
    assert "Numerical Yukawa values, mass ratios, and mixing matrices remain open." in text


def test_yukawa_proof_ledger_discharge_and_downstream_open():
    ledger = y.proof_discharge_ledger()
    assert "PO-BH-18" in ledger
    assert ledger["PO-BH-18"].status == y.DischargeStatus.DERIVED_CONDITIONAL
    payload = y.build_results_payload()
    assert payload["discharged_obligations"]["PO-BH-18"].startswith("DERIVED_CONDITIONAL")
    assert payload["numerical_yukawa_values_derived"] is False
    assert payload["mass_ratios_derived"] is False
    assert payload["ckm_pmns_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
    assert "full replacement-level SM derivation" in payload["still_open_downstream"]


def test_yukawa_docs_preserve_claim_boundaries():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_yukawa_operator_closure.md").read_text()
    forbidden = [
        "full Standard Model derivation is complete",
        "replacement claim is ready",
        "numerical Yukawa values are derived",
        "fermion mass ratios are derived",
        "CKM/PMNS mixing is derived",
        "Higgs VEV is numerically predicted",
    ]
    for phrase in forbidden:
        assert phrase not in text

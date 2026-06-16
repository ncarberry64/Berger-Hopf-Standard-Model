import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_higgs_scalar as hs  # noqa: E402


def test_main_doc_mission_conclusion_and_guardrails():
    hs.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_higgs_scalar_boundary_mechanism.md").read_text()
    assert hs.MISSION_LANGUAGE in text
    assert hs.CONCLUSION_LANGUAGE in text
    for phrase in [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "replacement claim is ready",
        "Higgs mass is predicted",
        "VEV is predicted",
        "quartic coupling is predicted",
        "Yukawa sector is derived",
    ]:
        assert phrase not in text


def test_proof_discharge_and_payload_keep_downstream_open():
    assert hs.proof_discharge_ledger()["PO-BH-16"].status == hs.DischargeStatus.DERIVED_CONDITIONAL
    payload = hs.build_results_payload()
    assert payload["higgs_mass_predicted"] is False
    assert payload["vev_predicted"] is False
    assert payload["quartic_predicted"] is False
    assert payload["yukawa_sector_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
    assert "Yukawa/mass/mixing theorem-level derivation" in payload["still_open_downstream"]

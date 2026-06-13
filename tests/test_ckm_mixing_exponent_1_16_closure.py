import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ckm_1_16_exponent_remains_open_without_derivation():
    payload = json.loads(ROOT.joinpath("audits/ckm_mixing_exponent_1_16_closure_audit.json").read_text())

    assert payload["status"] == "BLOCKS_FULL_COMPLETION"
    assert payload["blocker"] == "CKM_1_16_EXPONENT_NOT_DERIVED"
    assert payload["classification"] == "CANDIDATE_EXPONENT_NOT_DERIVED"
    assert any("Residual improvement alone is not a derivation" in item for item in payload["pass_fail_criteria"])


def test_ckm_candidate_damage_checks_are_reported():
    text = ROOT.joinpath("theory/ckm_mixing_exponent_1_16_derivation.md").read_text()

    assert "Candidate improves Vcb: True" in text
    assert "Candidate improves Vts: True" in text
    assert "Non-2-3 damage flag: False" in text

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_charged_lepton_precision_remains_blocker():
    payload = json.loads(ROOT.joinpath("audits/charged_lepton_precision_closure_audit.json").read_text())

    assert payload["status"] == "BLOCKS_FULL_COMPLETION"
    assert payload["blocker"] == "LEPTON_PRECISION_NOT_SOLVED"
    assert payload["classification"] == "OPEN_LEPTON_PRECISION_WARNING"


def test_lepton_candidate_is_not_adopted():
    text = ROOT.joinpath("candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.md").read_text()

    assert "NOT_OFFICIAL" in text
    assert "OPEN_LEPTON_PRECISION_WARNING" in text

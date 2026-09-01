import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_scalar_higgs_gap_remains_proxy_blocker():
    payload = json.loads(ROOT.joinpath("audits/scalar_higgs_gap_closure_audit.json").read_text())

    assert payload["status"] == "BLOCKS_FULL_COMPLETION"
    assert payload["blocker"] == "FULL_SPECTRUM_GAP_PROOF_MISSING"
    assert payload["classification"] == "STRONG_PROXY_SURVIVAL"
    assert any("Proxy/scaffold pass is not proof-level closure" in item for item in payload["pass_fail_criteria"])

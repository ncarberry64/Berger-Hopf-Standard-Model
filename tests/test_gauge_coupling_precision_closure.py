import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gauge_precision_lock_survives_under_declared_convention():
    payload = json.loads(ROOT.joinpath("audits/gauge_coupling_precision_closure_audit.json").read_text())

    assert payload["status"] == "CLOSED_SOLVED"
    assert payload["blocker"] is None
    assert payload["classification"] == "GAUGE_PRECISION_SURVIVAL"
    assert any("alpha_3 relative error" in item for item in payload["evidence"])
    assert any("electroweak window: True" in item for item in payload["evidence"])

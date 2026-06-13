import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_boundary_operator_not_action_derived():
    payload = json.loads(ROOT.joinpath("audits/boundary_operator_closure_audit.json").read_text())

    assert payload["status"] == "BLOCKS_FULL_COMPLETION"
    assert payload["blocker"] == "BOUNDARY_OPERATORS_NOT_ACTION_DERIVED"
    assert payload["classification"] == "ACTION_LINKED"
    assert any("Recovery of the mode ledger alone is not enough" in item for item in payload["pass_fail_criteria"])


def test_boundary_operator_values_reported_without_upgrade():
    text = ROOT.joinpath("theory/boundary_operator_action_derivation.md").read_text()

    assert "Omega_l=-q+2j=3" in text
    assert "Omega_u=q-2j=6" in text
    assert "Omega_d=q+4j=12" in text

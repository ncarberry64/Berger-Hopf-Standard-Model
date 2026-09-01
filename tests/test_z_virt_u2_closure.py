import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_z_virt_u2_closure_is_not_faked():
    payload = json.loads(ROOT.joinpath("audits/z_virt_u2_closure_audit.json").read_text())

    assert payload["status"] == "BLOCKS_FULL_COMPLETION"
    assert payload["blocker"] == "Z_VIRT_U2_NOT_DERIVED"
    assert payload["classification"] == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert any("without c/t residual input" in item for item in payload["pass_fail_criteria"])


def test_z_virt_u2_theory_file_exists():
    text = ROOT.joinpath("theory/z_virt_u2_derivation.md").read_text()

    assert "Z_VIRT_U2_NOT_DERIVED" in text
    assert "Two-state virtual half-occupation" in text

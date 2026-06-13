import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_common_scale_quark_rg_inputs_missing():
    payload = json.loads(ROOT.joinpath("audits/common_scale_quark_rg_closure_audit.json").read_text())

    assert payload["status"] == "BLOCKS_FULL_COMPLETION"
    assert payload["blocker"] == "COMMON_SCALE_QUARK_RG_INPUTS_MISSING"
    assert payload["classification"] == "EXTERNAL_INPUT_REQUIRED"
    assert any("Mixed-scale PDG-style values cannot be used as a precision verdict" in item for item in payload["pass_fail_criteria"])

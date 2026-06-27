import json
from pathlib import Path
from bhsm.interface.notebook_pack import check_notebook_pack, notebook_pack_manifest
ROOT=Path(__file__).resolve().parents[1]
def test_notebooks_parse_without_execution():
    result=check_notebook_pack(ROOT); assert result["passed"] and result["execution_attempted"] is False
    manifest=notebook_pack_manifest(); assert manifest["execution_required_for_tests"] is False
    assert manifest["requires_internet"] is False and manifest["requires_pdg"] is False
    assert json.loads((ROOT/"artifacts/BHSM_notebook_pack_manifest_v0_2.json").read_text())==manifest
def test_notebooks_include_claim_boundaries():
    combined="\n".join((ROOT/p).read_text() for p in notebook_pack_manifest()["notebooks"])
    assert "not empirical validation claims" in combined
    assert "never BHSM derivation inputs" in combined
    assert "do not promote a blocker" in combined

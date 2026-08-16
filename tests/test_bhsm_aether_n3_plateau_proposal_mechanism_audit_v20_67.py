import json
from pathlib import Path


def test_v20_62_plateau_audit_recomposes_exact_f376_and_selects_one_outcome() -> None:
    payload = json.loads(Path("artifacts/BHSM_N3_V20_62_PLATEAU_PROPOSAL_MECHANISM_AUDIT_V20_67.json").read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    audit = payload["plateau_proposal_mechanism_audit"]
    assert audit["accepted_frontier"]["version"] == "v20.62"
    assert abs(audit["accepted_frontier"]["exact_f376_l2"] - 0.766997331117846) < 5.0e-12
    assert audit["outcome"][0] in "ABCDEF"
    assert not audit["residual_definition"]["equations_changed"]

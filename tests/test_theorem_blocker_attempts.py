import json
from pathlib import Path
from bhsm.interface.theorem_blockers import OPEN, attempt_all_theorem_closures, attempt_theorem_closure
ROOT=Path(__file__).resolve().parents[1]
def test_all_blockers_remain_exactly_open():
    rows=attempt_all_theorem_closures(ROOT); assert len(rows)==3
    statuses={r.blocker_key:r.closure_status for r in rows}
    assert statuses=={
        "X_ch":"OPEN_MISSING_FIELD_REPRESENTATION",
        "neutrino_basis_scale_dirac_majorana":"OPEN_MISSING_PHYSICAL_BASIS",
        "cp_o_int":"OPEN_MISSING_ACTION_SOURCE",
    }
    assert all(not r.empirical_inputs_used for r in rows)
    assert {r.blocker_key for r in rows}=={"X_ch","neutrino_basis_scale_dirac_majorana","cp_o_int"}
def test_author_template_does_not_promote_by_default():
    template=json.loads((ROOT/"data/theorem_inputs/theorem_input_template.json").read_text())
    assert attempt_theorem_closure("X_ch",ROOT,template).closure_status=="OPEN_MISSING_FIELD_REPRESENTATION"
def test_theorem_attempt_artifacts_parse_and_stay_open():
    for name in ("BHSM_x_ch_closure_attempt_v0_2.json","BHSM_neutrino_basis_scale_closure_attempt_v0_2.json","BHSM_cp_o_int_closure_attempt_v0_2.json"):
        data=json.loads((ROOT/"artifacts"/name).read_text()); assert data["closure_status"]==OPEN

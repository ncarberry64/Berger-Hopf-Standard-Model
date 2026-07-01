import json
from pathlib import Path
from bhsm.interface.ckm_coefficient_form_source import build_coefficient_form_report
ROOT=Path(__file__).resolve().parents[1]
def test_artifacts_and_claims():
 for p in (ROOT/"artifacts").glob("*v2_9.json"):
  d=json.loads(p.read_text()); assert d.get("empirical_inputs_used",False) is False
 r=build_coefficient_form_report(); assert r["transport_blocker"]["ckm_exponent_status"]=="not_derived" and len(r["required_statements"])==6

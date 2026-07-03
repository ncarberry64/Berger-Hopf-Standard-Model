import json
from .common import GATES, GUARD, REQUIRED_STATEMENTS, build_gate
from .source_search import search_gauge_coframe_hodge_sources
def build_gauge_coframe_hodge_report():
    return {"status":"GAUGE_COFRAME_BASIS_OPEN_HODGE_FACTORS_CONDITIONAL","candidate_formula":"e^a=lambda_a sigma_a; S_gauge contains Tr(F wedge *F)","claim_boundary":"Conditional metric dependence does not derive equal coefficients, averaging, or couplings.","evidence_for":["Berger metric and schematic Hodge action"],"evidence_against":["basis and component factors unspecified"],"dependencies":list(GATES),"blocking_conditions":[k for k,v in GATES.items() if str(v["status"]).startswith(("OPEN_","FULL_"))],"source_search":search_gauge_coframe_hodge_sources(),"gates":{k:build_gate(k) for k in GATES},"required_statements":list(REQUIRED_STATEMENTS),**GUARD}
def gauge_coframe_hodge_report_to_markdown(payload=None):
    p=payload or build_gauge_coframe_hodge_report(); return "# Gauge Coframe/Hodge v4.3\n\n"+"\n".join(f"- {x}" for x in p["required_statements"])+"\n\n```json\n"+json.dumps(p,indent=2,sort_keys=True,ensure_ascii=False)+"\n```"

import json
from .common import GATES, GUARD, REQUIRED_STATEMENTS, build_gate
from .source_search import search_berger_hodge_component_sources

def build_berger_hodge_component_report():
    return {"status": "BERGER_HODGE_COMPONENT_MAP_CONDITIONAL_COFRAME_SELECTION_OPEN", "candidate_formula": GATES["hodge_component_map"]["candidate_formula"], "claim_boundary": "The component map closes conditionally; gauge-action basis selection and every normalization promotion remain open.", "evidence_for": ["explicit raw and orthonormal Hodge formulas"], "evidence_against": ["gauge action does not select a coframe"], "dependencies": list(GATES), "blocking_conditions": [k for k, v in GATES.items() if str(v["status"]).startswith(("OPEN_", "FULL_"))], "source_search": search_berger_hodge_component_sources(), "gates": {k: build_gate(k) for k in GATES}, "required_statements": list(REQUIRED_STATEMENTS), **GUARD}

def berger_hodge_component_report_to_markdown(payload=None):
    p = payload or build_berger_hodge_component_report()
    return "# Berger Hodge Component Map v4.4\n\n" + "\n".join(f"- {x}" for x in p["required_statements"]) + "\n\n```json\n" + json.dumps(p, indent=2, sort_keys=True, ensure_ascii=False) + "\n```"

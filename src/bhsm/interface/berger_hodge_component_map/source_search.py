from .common import GUARD, ORTHO, RAW

def search_berger_hodge_component_sources():
    return {"status": "SOURCE_SEARCH_COMPLETE_HODGE_MAP_CONDITIONAL_COFRAME_OPEN", "candidate_formula": RAW, "orthonormal_formula": ORTHO, "raw_berger_formula": RAW, "claim_boundary": "The Berger metric supports a conditional component map but does not select the gauge-action coframe.", "evidence_for": ["artifact-backed Berger metric", "normalized gauge action skeleton containing Tr(F wedge *F)"], "evidence_against": ["no action-selected gauge coframe", "no coefficient equality theorem"], "dependencies": ["Berger metric", "orientation"], "blocking_conditions": ["gauge-action coframe selection"], **GUARD}

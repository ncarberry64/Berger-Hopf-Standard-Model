from .common import G2,input_guard
def audit_g2_source():
 return {"symbol":"g2_BH_runtime","source_locations":["artifacts/BHSM_minimal_runtime_parameter_requirements_v1_2.json","artifacts/BHSM_bounded_feynrules_prep_lagrangian_v1_2.json"],"is_runtime_input":True,"is_registered_constant":False,"is_action_derived":False,"normalization_source":None,"evidence_for":["runtime input is explicit"],"evidence_against":["normalized weak gauge action does not fix it"],"status":G2,"claim_boundary":"A runtime g2_BH input is not an action-derived coupling.",**input_guard()}

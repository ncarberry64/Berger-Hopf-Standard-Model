import json
from .common import STATEMENTS,input_guard
from .weak_charged_current_form import audit_weak_charged_current_form
from .g2_source_audit import audit_g2_source
from .alpha2_source_audit import audit_alpha2_source
from .weak_coupling_convention import audit_weak_coupling_convention
from .ckm_coefficient_form import audit_ckm_coefficient_form
from .ckm_coefficient_value_source import audit_ckm_coefficient_value_source
from .measure_coefficient_attachment import audit_measure_coefficient_attachment
from .source_search import search_coefficient_form_sources
def build_coefficient_form_report():
 a=audit_measure_coefficient_attachment(); return {"source_search":search_coefficient_form_sources(),"weak_form":audit_weak_charged_current_form(),"g2":audit_g2_source(),"alpha2":audit_alpha2_source(),"convention":audit_weak_coupling_convention(),"ckm_form":audit_ckm_coefficient_form(),"value":audit_ckm_coefficient_value_source(),"attachment":a,"transport_blocker":{"coefficient_form_status":"ARTIFACT_BACKED_CKM_COEFFICIENT_FORM","coefficient_value_status":"OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE","measure_attachment_status":a["status"],"projector_status":"OPEN_MISSING_PROJECTOR_SANDWICH_REQUIREMENT","paired_normalization_status":"OPEN_MISSING_PAIRED_NORMALIZATION_RULE","ckm_identification_status":"OPEN_MISSING_CKM_IDENTIFICATION_THEOREM","transport_space_selection_status":"OPEN_MISSING_CKM_TRANSPORT_SPACE_SELECTION","ckm_exponent_status":"not_derived","selected_space":None,"selected_dimension":None,"blocking_conditions":["g2 action source","measure attachment","projectors","paired normalization","CKM identification"]},"required_statements":list(STATEMENTS),"artifact_backed_closures":["ARTIFACT_BACKED_WEAK_CHARGED_CURRENT_COEFFICIENT_FORM","ARTIFACT_BACKED_G2_BH_RUNTIME_INPUT","ARTIFACT_BACKED_ALPHA2_BH_REGISTERED_COUPLING","ARTIFACT_BACKED_CKM_COEFFICIENT_FORM"],"conditional_closures":["CONDITIONAL_WEAK_COUPLING_CONVENTION"],"rejected":["REJECTED_RUNTIME_INPUT_AS_ACTION_DERIVATION","REJECTED_ALPHA2_REGISTRY_AS_ACTION_DERIVATION","REJECTED_COEFFICIENT_FORM_AS_VALUE_DERIVATION","REJECTED_BRIDGE_ARITHMETIC_AS_GAUGE_COUPLING"],**input_guard()}
def coefficient_form_report_to_markdown(p=None):
 p=p or build_coefficient_form_report(); return "# CKM Coefficient Form Source Audit\n\n"+"\n".join(f"- {x}" for x in p["required_statements"])+"\n\n```json\n"+json.dumps(p,indent=2,sort_keys=True)+"\n```"

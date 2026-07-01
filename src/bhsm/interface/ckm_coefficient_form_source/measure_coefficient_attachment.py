from .common import ATTACH,CKM_FORM,VALUE,input_guard
def audit_measure_coefficient_attachment():
 return {"measure_status":"CONDITIONAL_BOUNDARY_MEASURE_SOURCE","coefficient_form_status":CKM_FORM,"coefficient_value_status":VALUE,"same_term_attachment":False,"applies_to_L_CKM_bounded":False,"status":ATTACH,"claim_boundary":"Form occurrence in the interface term does not attach a normalized measure or action-derived value.",**input_guard()}

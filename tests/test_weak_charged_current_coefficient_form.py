from bhsm.interface.ckm_coefficient_form_source import audit_weak_charged_current_form
def test_form():
 p=audit_weak_charged_current_form(); assert p["status"]=="ARTIFACT_BACKED_WEAK_CHARGED_CURRENT_COEFFICIENT_FORM" and "sqrt(2)" in p["candidate_form"]

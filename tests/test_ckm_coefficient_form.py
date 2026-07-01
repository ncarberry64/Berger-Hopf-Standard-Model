from bhsm.interface.ckm_coefficient_form_source import audit_ckm_coefficient_form
def test_ckm_form_applies_but_attachment_open():
 p=audit_ckm_coefficient_form(); assert p["applies_to_L_CKM_bounded"] and p["status"]=="ARTIFACT_BACKED_CKM_COEFFICIENT_FORM"

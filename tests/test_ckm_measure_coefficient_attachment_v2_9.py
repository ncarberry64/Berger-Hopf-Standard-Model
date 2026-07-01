from bhsm.interface.ckm_coefficient_form_source import audit_measure_coefficient_attachment
def test_attachment_open():
 p=audit_measure_coefficient_attachment(); assert not p["same_term_attachment"] and p["status"]=="OPEN_MISSING_CKM_MEASURE_COEFFICIENT_ATTACHMENT"

from bhsm.interface.ckm_coefficient_form_source import audit_g2_source
def test_g2_runtime_not_action():
 p=audit_g2_source(); assert p["is_runtime_input"] and not p["is_action_derived"] and p["status"]=="ARTIFACT_BACKED_G2_BH_RUNTIME_INPUT"

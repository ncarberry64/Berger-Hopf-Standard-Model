from bhsm.interface.ckm_coefficient_form_source import audit_alpha2_source
def test_alpha2_registered_not_action():
 p=audit_alpha2_source(); assert p["is_registered_coupling"] and not p["is_action_derived"]

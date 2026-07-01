from bhsm.interface.ckm_coefficient_form_source import audit_weak_coupling_convention
def test_convention_not_derivation():
 p=audit_weak_coupling_convention(); assert p["status"]=="CONDITIONAL_WEAK_COUPLING_CONVENTION" and not p["is_action_derivation"]

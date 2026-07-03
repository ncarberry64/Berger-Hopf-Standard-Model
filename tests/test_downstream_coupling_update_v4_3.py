from bhsm.interface.gauge_coframe_hodge.downstream_update import audit_downstream_update
def test_downstream_open():
 p=audit_downstream_update(); assert p["alpha_i_status"]=="OPEN_MISSING_ALPHA_I_ACTION_DERIVATION"; assert p["g2_status"]=="OPEN_MISSING_G2_BH_ACTION_SOURCE"; assert p["ckm_exponent_status"]=="not_derived"

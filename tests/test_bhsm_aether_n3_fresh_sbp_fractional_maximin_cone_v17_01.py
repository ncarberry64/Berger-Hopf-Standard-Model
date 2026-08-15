from bhsm.interface.aether_n3_fresh_sbp_fractional_maximin_cone_v17_01 import completion_payload,v17_00_selected_raw_vector
def test_v17_00_state_has_complete_dimension():assert v17_00_selected_raw_vector().shape==(376,)
def test_fractional_maximin_cone_validates():assert completion_payload()["validation_passed"]

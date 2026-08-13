from bhsm.interface.aether_n3_fresh_sbp_v0_priority_family_v17_22 import completion_payload,v17_21_selected_raw_vector
def test_v17_21_state_has_complete_dimension():assert v17_21_selected_raw_vector().shape==(376,)
def test_v0_priority_family_validates():assert completion_payload()["validation_passed"]

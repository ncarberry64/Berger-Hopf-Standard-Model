from bhsm.interface.aether_n3_fresh_sbp_pareto_balanced_selection_v16_89 import completion_payload,pareto_balanced_selection,selected_raw_vector
def test_pareto_selection_preserves_complete_state():assert selected_raw_vector().shape==(376,)
def test_stationarity_biased_candidate_not_promoted():assert pareto_balanced_selection()["v16_88_minimum_total_candidate_promoted"] is False
def test_pareto_balanced_selection_validates():assert completion_payload()["validation_passed"]

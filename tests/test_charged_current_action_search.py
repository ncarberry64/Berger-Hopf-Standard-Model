from bhsm.interface.charged_current_action import search_charged_current_action_sources
from bhsm.interface.charged_current_action.common import channel_dimensions


def test_charged_current_action_search_locates_candidates_and_stays_open():
    payload = search_charged_current_action_sources()
    assert payload["files_scanned"] > 0
    assert payload["total_hits"] >= len(payload["hits"])
    assert payload["status"] == "OPEN_MISSING_NORMALIZED_CHARGED_CURRENT_ACTION_TERM"
    term_ids = {row["term_id"] for row in payload["candidate_action_terms"]}
    assert "L_CKM_charged_current_bounded" in term_ids
    assert payload["empirical_inputs_used"] is False


def test_charged_current_action_search_records_all_candidate_counts():
    dims = channel_dimensions()
    assert dims["one_way_up_down"] == 8
    assert dims["bidirectional_adjoint_pair"] == 16
    assert dims["sector_self_response_sum"] == 21
    assert dims["total_charged_endomorphism"] == 49
    assert dims["maximal_self_response"] == 16


import json
from pathlib import Path

from bhsm.interface.aether_n3_lorentzian_child_cauchy_correspondence_v17_88 import (
    completion_payload,
    deterministic_json,
)


def test_lorentzian_child_cauchy_correspondence_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["event_to_complete_child_cauchy_correspondence"]
    assert result["KKT_integration"]["pre_event_unknown_count"] == 376
    assert result["KKT_integration"]["new_unknowns"] == 0
    assert result["KKT_integration"]["new_equations"] == 0
    assert not result["KKT_integration"]["F_child_already_present"]
    assert not result["KKT_integration"]["direct_N3_solve_authorized_next"]
    assert len(result["F_child"]["current_candidate_rows"]) == 7
    assert result["F_child"]["local_constraint_differential_rank"] == 7
    assert not result["F_child"]["current_candidate_closed"]
    assert result["joined_action_derivation"]["W_phys"] is None


def test_materialized_lorentzian_correspondence_matches_runtime():
    stored_text = Path(
        "artifacts/BHSM_aether_n3_lorentzian_child_cauchy_correspondence_v17_88.json"
    ).read_text(encoding="utf-8")
    assert json.loads(stored_text)["validation_passed"]
    assert stored_text == deterministic_json(completion_payload())

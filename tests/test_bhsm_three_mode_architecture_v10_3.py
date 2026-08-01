from bhsm.interface.envelopment import three_mode_architecture_v10_3 as architecture


def test_three_physical_slots_exclude_seam_and_generations():
    payload = architecture.architecture_payload()
    assert payload["three_mode_state"] == ["q_C", "q_W", "q_D"]
    assert len(payload["modes"]) == 3
    assert payload["seam"].startswith("coordinate/observable projection")
    assert payload["ontology"]["THREE_GENERATIONS_ARE_CYCLE_PHASES"] == "AUTHOR_ONTOLOGY"
    assert payload["modes"][2]["current_status"] == "MISSING_ACTION_OWNED_DEGREE"


def test_common_action_is_Hermitian_typed_and_fail_closed():
    blocks = architecture.common_action_blocks()
    for name in ("K", "H"):
        matrix = blocks[name]
        for i in range(3):
            for j in range(3):
                assert matrix[i][j]["status"] == matrix[j][i]["status"]
                assert matrix[i][j]["value"] == matrix[j][i]["value"]
    assert blocks["K"][0][1]["status"] == "UNDEFINED_CROSS_DOMAIN"
    assert blocks["K"][2][2]["status"] == "OPEN"
    assert blocks["complete_common_source"] is None

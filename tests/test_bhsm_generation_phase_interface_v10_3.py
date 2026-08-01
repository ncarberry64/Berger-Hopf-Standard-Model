from bhsm.interface.envelopment import generation_phase_interface_v10_3 as phases


def test_one_cycle_three_phase_slots_are_separate_from_modes():
    payload = phases.generation_phase_payload()
    assert payload["sector_specific_cycles"] == 1
    assert len(payload["phase_slots"]) == 3
    assert payload["three_geometric_modes_are_generations"] is False
    assert payload["monodromy"] is None


def test_mass_mixing_and_quantum_outputs_fail_closed():
    payload = phases.generation_phase_payload()
    assert payload["mass_output"] is None
    assert payload["CKM_output"] is None
    assert payload["PMNS_output"] is None
    assert payload["core_transition_interface"]["probabilities"] is None
    assert payload["core_transition_interface"]["quantum_nonlocality_derived"] is False

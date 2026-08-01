from __future__ import annotations

from bhsm.interface.envelopment.generation_monodromy_v10_4 import FROZEN_LEDGERS, generation_payload
from bhsm.interface.envelopment.particle_cycle_v10_4 import particle_cycle_payload
from bhsm.interface.envelopment.physical_mass_mixing_gate_v10_4 import mass_mixing_payload


def test_particle_cycles_are_not_solved_without_three_mode_action():
    payload = particle_cycle_payload()
    assert payload["physical_particle_cycle_count"] == 0
    assert payload["charged_lepton"]["mass"] is None
    assert payload["quark_hadron"]["color_neutrality"] is None
    assert payload["neutrino"]["measured_delta_m2_used"] is False


def test_generation_phases_preserve_frozen_ledgers_and_are_not_modes():
    payload = generation_payload()
    assert payload["three_modes_identified_with_generations"] is False
    assert payload["frozen_ledgers_changed"] is False
    assert payload["sectors"]["charged_leptons"]["frozen_slots"] == FROZEN_LEDGERS["charged_leptons"]
    assert payload["derived_generation_phase_count"] == 0


def test_masses_mixing_and_m4_readout_remain_null():
    payload = mass_mixing_payload()
    assert payload["mu_global"] is None
    assert payload["physical_mass_values"] is None
    assert payload["G_f"] is None and payload["Q_f"] is None and payload["K_ud"] is None
    assert payload["CKM"] is None and payload["PMNS"] is None
    assert payload["matrices_printed"] is False
    assert payload["measured_particle_inputs_used"] == []
    assert payload["M4_reduction"]["effective_fields_retained"] is True

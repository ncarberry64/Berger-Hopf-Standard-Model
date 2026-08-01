"""Fail-closed relational neutrino identity and observable interface."""

from __future__ import annotations

from typing import Any

from .relational_axioms import DoctrineStatus


NEUTRINO_VERDICT = "BHSM_NEUTRINO_DIRAC_MAJORANA_OBSERVABLE_DISTINCTION_REMAINS_OPEN"


def neutrino_doctrine_gate() -> dict[str, Any]:
    return {
        "definition": "propagation-supported near-null envelopment without a primitive stationary rest enclosure",
        "author_status": DoctrineStatus.AUTHOR_ONTOLOGY.value,
        "physical_equivalence_status": "OPEN_PHYSICAL_EQUIVALENCE",
        "exists_only_when_observed": False,
        "stationary_rest_branch_assigned": False,
        "primitive_static_mass_assigned": False,
        "target_monodromy": "M_nu xi_i=exp(-i theta_i)xi_i, i=1,2,3",
        "interaction_basis": "weak-current relational boundary projectors",
    }


def observable_gate() -> dict[str, Any]:
    return {
        "propagating_orbit": None,
        "three_physical_monodromy_sectors": None,
        "vertex_phase_map": None,
        "neutrino_antineutrino_orientation": None,
        "self_complementary_propagation": None,
        "lepton_number_conservation_or_violation": None,
        "neutrinoless_double_beta_decay": None,
        "helicity_suppression": None,
        "CP_conjugate_transition_probabilities": None,
        "matter_effect_asymmetries": None,
        "PMNS": None,
        "Delta_m2": None,
        "measured_oscillation_inputs_used": False,
        "conventional_observables_remain_expressible": True,
        "classification": DoctrineStatus.OPEN.value,
    }


def neutrino_payload() -> dict[str, Any]:
    doctrine = neutrino_doctrine_gate()
    observables = observable_gate()
    validation = {
        "no_static_rest_output": not doctrine["stationary_rest_branch_assigned"],
        "no_primitive_mass": not doctrine["primitive_static_mass_assigned"],
        "orbit_placeholders_null": observables["propagating_orbit"] is None and observables["three_physical_monodromy_sectors"] is None,
        "Dirac_Majorana_gate_open": observables["vertex_phase_map"] is None,
        "no_measured_values": not observables["measured_oscillation_inputs_used"],
        "PMNS_null": observables["PMNS"] is None,
    }
    return {
        "artifact": "BHSM_neutrino_relational_identity_gate_v10_1",
        "doctrine": doctrine,
        "observables": observables,
        "verdict": NEUTRINO_VERDICT,
        "exact_missing_object": "NEUTRINO_VERTEX_PHASE_OBSERVABLE_MAP",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

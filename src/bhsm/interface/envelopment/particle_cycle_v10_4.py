"""Charged, hadronic, and neutrino cycle gates for BHSM v10.4."""

from __future__ import annotations

from typing import Any


PARTICLE_VERDICT = "BHSM_PHYSICAL_PARTICLE_CYCLES_BLOCKED_UPSTREAM_BY_INCOMPLETE_THREE_MODE_ACTION"


def _cycle(kind: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "three_mode_cycle": None,
        "finite_invariant_energy": None,
        "complete_gauge_dressing": False,
        "stable_Floquet_spectrum": None,
        "asymptotic_physical_state": None,
        "stress_momentum_integral": None,
        "mass": None,
        "numerical_solution_performed": False,
    }


def particle_cycle_payload() -> dict[str, Any]:
    charged = _cycle("charged-lepton timelike self-envelopment")
    hadron = _cycle("color-neutral parent with color-open quark sub-envelopments")
    hadron.update({"color_neutrality": None, "separation_energy_curve": None, "isolated_quark_instability": None, "hadronization_bifurcation": None})
    neutrino = _cycle("near-null propagation-supported envelopment")
    neutrino.update({"primitive_stationary_rest_enclosure_assumed": False, "near_null_dispersion": None, "adiabatic_phase_limit": None, "measured_delta_m2_used": False})
    return {
        "artifact": "BHSM_particle_cycle_gate_v10_4",
        "charged_lepton": charged,
        "quark_hadron": hadron,
        "neutrino": neutrino,
        "physical_particle_cycle_count": 0,
        "verdict": PARTICLE_VERDICT,
        "validation_passed": True,
    }

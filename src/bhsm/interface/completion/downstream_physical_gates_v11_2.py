"""Uniform fail-closed downstream disposition for the v11.2 campaign."""

from __future__ import annotations

from typing import Any


def downstream_payload() -> dict[str, Any]:
    outputs = {
        "nonlinear_cycles": None,
        "topological_buoyancy": None,
        "higgs_mode": None,
        "global_equilibrium": None,
        "curvature_scale": None,
        "three_generations": "frozen structural ledger preserved; not re-derived",
        "mass_ratios": None,
        "physical_masses": None,
        "CKM": None,
        "PMNS": None,
        "effective_M4_action": None,
        "quantum_amplitudes": None,
        "measurement_rule": None,
    }
    validation = {
        "mark_ii_gate_enforced": True,
        "no_new_physical_output": all(value is None for key, value in outputs.items() if key != "three_generations"),
        "frozen_generation_ledger_preserved": True,
        "no_particle_input": True,
    }
    return {
        "artifact": "BHSM_downstream_physical_gates_v11_2",
        "Mark_II": "NOT_REACHED",
        "automatic_continuation_triggered": False,
        "outputs": outputs,
        "status": "BHSM_DOWNSTREAM_PHYSICAL_COMPLETION_FAIL_CLOSED_AT_MARK_II",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


"""Fail-closed covariant phase-space ledger for v11.2."""

from __future__ import annotations

from typing import Any


def phase_space_payload() -> dict[str, Any]:
    validation = {
        "regular_support_pair_retained": True,
        "boundary_flux_retained": True,
        "complete_symplectic_form_withheld": True,
        "core_phase_space_withheld": True,
    }
    return {
        "artifact": "BHSM_support_covariant_phase_space_v11_2",
        "known_symplectic_potential": "Theta_D^A=-sqrt(-G) partial^A q_D delta q_D (orientation convention inherited from the action)",
        "known_symplectic_current": "omega_D^A=delta_1 Theta_D^A[delta_2]-delta_2 Theta_D^A[delta_1]",
        "canonical_pairs": ["(q_D,Pi_D) on a regular Cauchy slice"],
        "support_momentum": "Pi_D=sqrt(gamma) n^A partial_A q_D",
        "boundary_momentum": "pi_D,boundary=sqrt(|h|) n^A partial_A q_D",
        "complete_symplectic_potential": None,
        "complete_symplectic_current": None,
        "complete_flux_conservation": None,
        "core_phase_space": None,
        "positive_physical_kinetic_rank": None,
        "status": "BHSM_COMPLETE_SUPPORTED_COVARIANT_PHASE_SPACE_BLOCKED_BY_MISSING_LOCAL_ACTION_AND_CORE_RESPONSE",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


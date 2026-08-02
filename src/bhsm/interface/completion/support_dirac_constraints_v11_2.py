"""Dirac--Bergmann disposition for the incomplete v11.2 support action."""

from __future__ import annotations

from typing import Any


def constraint_payload() -> dict[str, Any]:
    validation = {
        "known_regular_scalar_has_nonzero_legendre_map": True,
        "gravity_constraints_preserved": True,
        "unknown_complete_rank_withheld": True,
        "no_false_ghost_claim": True,
    }
    return {
        "artifact": "BHSM_support_constraint_ledger_v11_2",
        "known_support_primary_constraints": [],
        "known_support_pair": "one conditional regular canonical scalar pair for positive Haar kinetic sign",
        "parent_primary_constraints": "lapse/shift and gauge constraints inherited unchanged",
        "secondary_constraints": "parent Hamiltonian, momentum, and gauge constraints inherited; supported modifications not computable",
        "first_class_constraints": None,
        "second_class_constraints": None,
        "complete_dirac_matrix": None,
        "complete_physical_rank": None,
        "ghost_status": "not classifiable for the incomplete coupled action; the isolated support kinetic term is healthy",
        "status": "BHSM_COMPLETE_SUPPORTED_DIRAC_ANALYSIS_BLOCKED_BY_MISSING_ACTION_OWNED_CURRENT_COUPLINGS",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


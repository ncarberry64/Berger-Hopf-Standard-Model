"""Claim and comparison guardrails for the neutrino propagation candidate."""

from __future__ import annotations

from typing import Any


def neutrino_validation_policy() -> dict[str, Any]:
    return {
        "upper_limit_comparison_policy": "Electron-neutrino comparisons remain upper-limit comparisons unless a vetted central mass reference is explicitly supplied.",
        "reference_policy": "Reference values are comparison inputs only and are never theorem inputs.",
        "empirical_derivation_inputs_used": False,
        "reference_values_used_as_theorem_inputs": False,
        "electron_neutrino_upper_limit_used_as_derivation_input": False,
        "w_mass_used_as_theorem_input": False,
        "ordering_inferred_from_data": False,
        "dirac_majorana_closure_claimed": False,
        "internet_required": False,
        "pdg_required": False,
        "external_hep_tools_required": False,
    }

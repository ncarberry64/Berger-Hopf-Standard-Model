"""Observable-policy map for propagation-conditioned neutrino mass."""

from __future__ import annotations

from .common import NeutrinoObservableMap


def build_neutrino_observable_map() -> NeutrinoObservableMap:
    return NeutrinoObservableMap(
        effective_propagation_mass="CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE_DIMENSIONLESS",
        oscillation_sensitive_mass_differences="OPEN_MISSING_OBSERVABLE_MAP",
        electron_neutrino_effective_mass_comparison="UPPER_LIMIT_COMPARISON_ONLY",
        cosmological_mass_sum_comparison="OPEN_MISSING_OBSERVABLE_MAP",
        static_rest_mass_interpretation="FORBIDDEN_STATIC_REST_MASS_FRAMING",
        ordering_policy="ordering-free",
        dirac_majorana_policy="DIRAC_MAJORANA_SECONDARY",
        status="CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE",
        claim_boundary="The propagation response is not automatically an ordinary rest mass, oscillation spectrum, or cosmological mass sum.",
    )

from __future__ import annotations

from bhsm.interface.neutrino_propagation.observable_map import build_neutrino_observable_map
from bhsm.interface.neutrino_propagation.validation_policy import neutrino_validation_policy


def test_observable_map_separates_propagation_mass_from_static_mass() -> None:
    observable = build_neutrino_observable_map()
    assert observable.static_rest_mass_interpretation == "FORBIDDEN_STATIC_REST_MASS_FRAMING"
    assert observable.effective_propagation_mass == "CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE_DIMENSIONLESS"
    assert observable.ordering_policy == "ordering-free"
    assert observable.dirac_majorana_policy == "DIRAC_MAJORANA_SECONDARY"
    assert observable.oscillation_sensitive_mass_differences == "OPEN_MISSING_OBSERVABLE_MAP"


def test_comparison_policy_uses_no_reference_as_theorem_input() -> None:
    policy = neutrino_validation_policy()
    assert policy["electron_neutrino_upper_limit_used_as_derivation_input"] is False
    assert policy["reference_values_used_as_theorem_inputs"] is False
    assert policy["w_mass_used_as_theorem_input"] is False
    assert policy["ordering_inferred_from_data"] is False
    assert policy["dirac_majorana_closure_claimed"] is False

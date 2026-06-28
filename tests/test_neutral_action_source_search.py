from __future__ import annotations

from bhsm.interface.neutrino_action import search_neutral_action_sources


def test_neutral_action_source_search_is_offline_and_exact_about_missing_normalization() -> None:
    result = search_neutral_action_sources()
    keys = {term.term_key for term in result.terms}
    assert result.status == "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION"
    assert result.artifact_backed_terms_found is True
    assert result.conditional_variational_structure_found is True
    assert result.complete_normalized_action_found is False
    assert {
        "neutral_propagation_source",
        "neutral_boundary_tangential_kinetic",
        "neutral_boundary_normal_coupling",
        "scalar_mass_gap_analogue",
        "neutral_collar_measure",
        "measurement_interaction_support",
    } <= keys
    assert result.empirical_derivation_inputs_used is False


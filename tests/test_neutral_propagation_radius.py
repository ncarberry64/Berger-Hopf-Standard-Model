from __future__ import annotations

from bhsm.interface.neutrino_scale import search_neutral_propagation_radius


def test_radius_search_defines_symbolic_candidate_without_inventing_metres() -> None:
    result = search_neutral_propagation_radius()
    assert result.status == "CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE"
    assert result.symbolic_candidate_found is True
    assert result.numeric_metres_found is False
    rows = {row.candidate_key: row for row in result.candidates}
    assert rows["author_ontology_r_prop"].unit == "m (symbolic; no value supplied)"
    assert rows["boundary_profile_sigma"].status == "DIMENSIONLESS_LENGTH_PROXY"
    assert rows["boundary_profile_sigma"].numeric_metres_available is False
    assert rows["empirical_or_mass_derived_length"].status == "FORBIDDEN_EMPIRICAL_RADIUS"


def test_radius_search_uses_no_empirical_theorem_inputs() -> None:
    result = search_neutral_propagation_radius()
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_theorem_inputs is False
    assert result.electron_neutrino_limit_used_as_derivation_input is False
    assert result.w_mass_used_as_theorem_input is False
    assert result.legacy_particle_tables_used_as_derivation_inputs is False


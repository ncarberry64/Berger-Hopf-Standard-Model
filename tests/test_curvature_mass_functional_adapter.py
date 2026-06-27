from __future__ import annotations

from bhsm.interface.neutrino_scale import (
    load_curvature_activation_from_legacy_artifacts,
    load_curvature_mass_functional_from_legacy_artifacts,
)


def test_curvature_mass_functional_is_extracted_with_provenance() -> None:
    result = load_curvature_mass_functional_from_legacy_artifacts()
    assert result.mass_formula == "m = (c^2/(2G)) r_c^2 k_loc"
    assert result.energy_formula == "E = (c^4/(2G)) r_c^2 k_loc"
    assert result.candidate_status == "ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL"
    assert result.action_derived is False
    assert result.matching_ansatz_disclosed is True


def test_curvature_operator_activation_and_stability_are_recorded() -> None:
    result = load_curvature_activation_from_legacy_artifacts()
    assert result.curvature_operator == "K[rho] = -nabla^2 ln rho"
    assert result.single_activation_normalization == "N_K = 1"
    assert len(result.stability_conditions) == 3


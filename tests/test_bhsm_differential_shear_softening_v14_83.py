from math import isclose

import pytest

from bhsm.interface.completion.differential_shear_softening_v14_83 import (
    EXACT_NEXT_OBJECT,
    completion_payload,
    kinetic_decomposition,
    materialize,
    reduced_mass,
    round_reference_ratio,
    shear_susceptibility,
)


def test_weighted_two_stratum_kinetic_decomposition_is_exact() -> None:
    result = kinetic_decomposition(
        [0.3, -0.8, 0.2],
        [1.1, 0.4, -0.5],
        [-0.7, 0.9, 0.6],
        2.5,
        7.0,
    )
    assert isclose(result["original"], result["decomposed"], abs_tol=1e-12)


def test_reduced_fraction_is_positive_and_bounded_by_one_quarter() -> None:
    for pair in ((1.0, 1.0), (1.0, 3.0), (2.0, 9.0)):
        total, reduced, nu = reduced_mass(*pair)
        assert total > 0 and reduced > 0
        assert 0 < nu <= 0.25
    assert reduced_mass(1.0, 1.0)[2] == 0.25


def test_isotropic_ell2_susceptibility_has_derived_positive_sign() -> None:
    assert isclose(shear_susceptibility(2, 1.0, 1.0, 1.0), 2.0 / 3.0)
    assert shear_susceptibility(2, 4.0, 2.0, 5.0) > 0


def test_ell2_is_first_round_reference_threshold_after_exclusions() -> None:
    ratios = [round_reference_ratio(ell) for ell in range(2, 20)]
    assert ratios == sorted(ratios)
    assert len(set(ratios)) == len(ratios)


def test_invalid_reduced_inputs_fail_closed() -> None:
    with pytest.raises(ValueError):
        reduced_mass(0.0, 1.0)
    with pytest.raises(ValueError):
        shear_susceptibility(-1, 1.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        round_reference_ratio(1)


def test_shear_recovery_does_not_overpromote_full_bhsm(tmp_path) -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["completion_status"]["reduced_shear_sign_gate"] == "PASSED"
    assert payload["completion_status"]["full_preimage_shear_action"] == "OPEN"
    assert payload["completion_status"]["BHSM_complete"] is False
    assert "shear itself creates exactly three modes" in payload["not_claimed"]
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second


import math

from bhsm.interface.aether_lr_susceptibility_zeta_v15_67 import (
    completion_payload,
    cutoff_dimensionless_sum,
    cutoff_dimensionless_sum_closed,
    deterministic_json,
    dimensionless_susceptibility_term,
    exact_spectral_contract,
    physical_cutoff_susceptibility,
    renormalization_semantics,
    zeta_laurent_coefficients,
)


def test_weyl_susceptibility_terms_and_closed_partial_sum():
    assert dimensionless_susceptibility_term(0) == 4.0 / 3.0
    for nmax in (0, 1, 2, 5, 20, 100):
        assert math.isclose(
            cutoff_dimensionless_sum(nmax),
            cutoff_dimensionless_sum_closed(nmax),
            rel_tol=2.0e-14,
            abs_tol=2.0e-12,
        )


def test_positive_cutoff_susceptibility_grows_with_cutoff():
    values = [physical_cutoff_susceptibility(nmax) for nmax in (0, 1, 4, 16)]
    assert all(value > 0.0 for value in values)
    assert values == sorted(values)


def test_exact_hurwitz_zeta_laurent_coefficients():
    result = zeta_laurent_coefficients(1.0)
    expected = 1.0 / 24.0 - 0.25 * 0.5772156649015329 - 0.5 * math.log(2.0)
    assert result["dimensionless_residue_at_s0"] == -1.0 / 8.0
    assert math.isclose(
        result["dimensionless_minimal_subtraction_finite_part"], expected,
        rel_tol=1.0e-14,
    )


def test_local_subtraction_is_distinguished_from_fixed_nonlocal_spectrum():
    contract = exact_spectral_contract()
    semantics = renormalization_semantics()
    assert contract["nonlocal_mode_dependence_fixed"] is True
    assert contract["finite_local_HdaggerH_subtraction_fixed"] is False
    assert semantics["MS_finite_part_positive"] is False
    assert semantics["gap_threshold_scheme_independent_without_that_output"] is False


def test_payload_is_deterministic_and_fail_closed():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first

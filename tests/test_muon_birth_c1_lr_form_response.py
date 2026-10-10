"""Exact coefficient proofs and conditional form API checks; no E1 states."""

from fractions import Fraction

import pytest
import sympy as sp

from bhsm.interface.muon_birth_c1_lr_form_response import (
    conditional_amplitude_weighted_form_bound,
    conditional_squared_extension_form_bound,
    exact_lr_symbol_identity,
    exact_squared_form_and_conormal_identity,
)


def test_actual_gamma_symbol_distinguishes_partner_and_positive_adjoint():
    result = exact_lr_symbol_identity()
    assert result["residual_validation_passed"] is True
    assert result["zero_residuals"]["gamma_mass_intertwining"] == [True]*4
    assert result["normal_cross_is_identically_zero"] is False
    m, p = sp.symbols("m_real p0", real=True)
    assert sp.sympify(result["real_mass_beta_positive_entry"], locals={"m_real": m, "p0": p}) == -2*m*p
    assert result["algebraic_partner_is_positive_adjoint"] is False
    assert result["positive_carrier_embedding_established"] is False
    assert result["physical_incoming_mass_or_direction_evaluated"] is False


def test_form_identity_keeps_cross_terms_and_conormal():
    result = exact_squared_form_and_conormal_identity()
    assert "2 Re" in result["form_difference"]
    assert "(E^dagger-E)partial_tau" in result["interior_differential_difference"]
    assert "arbitrary terminal" in result["form_domain"]
    assert result["squared_operator_flux_graph_must_use_new_conormal"] is True
    assert result["contact_in_already_polarized_form_counted_again"] is False


@pytest.mark.parametrize("hermitian", [False, True])
def test_independent_exact_polarization_detects_omitted_derivative_and_contact(hermitian):
    """Integrate test fields independently; the terminal trace is nonzero."""
    tau = sp.symbols("tau", real=True)
    w = sp.Matrix([[1, sp.I], [-sp.I, 2]])
    e = (sp.Matrix([[tau, sp.I], [-sp.I, 1+tau]]) if hermitian
         else sp.Matrix([[tau, sp.I], [2*tau, 1]]))
    u, v = sp.Matrix([tau, tau*tau+sp.I*tau]), sp.Matrix([2*tau+tau**3, sp.I*tau*tau])
    a0u, a0v = u.diff(tau)+w*u, v.diff(tau)+w*v
    full_form = ((a0u+e*u).H*(a0v+e*v)-a0u.H*a0v)[0]
    differential_cross = (e.H-e)*v.diff(tau)
    bulk = differential_cross-e.diff(tau)*v+w.H*e*v+e.H*w*v+e.H*e*v
    direct = sp.integrate(sp.expand(full_form), (tau, 0, 1))
    interior = sp.integrate(sp.expand((u.H*bulk)[0]), (tau, 0, 1))
    endpoint = sp.expand((u.H*e*v)[0].subs(tau, 1))
    assert sp.expand(direct-interior-endpoint) == 0
    assert endpoint != 0
    assert sp.expand(direct-interior) != 0  # Dropping the conormal contact fails.
    if not hermitian:
        omitted = sp.integrate(sp.expand((u.H*differential_cross)[0]), (tau, 0, 1))
        assert omitted != 0
        assert sp.expand(direct-(interior-omitted)-endpoint) != 0
    else:
        assert differential_cross == sp.zeros(2, 1)


def test_exact_form_bound_and_strict_rational_threshold():
    # API-only exact fractions; they are not an incoming mass or amplitude.
    result = conditional_squared_extension_form_bound(
        duration_upper=Fraction(1), superpotential_upper=Fraction(0),
        insertion_norm_upper=Fraction(3, 5), seam_inverse_upper=Fraction(2))
    assert result["one_end_L2_over_form_upper"] == Fraction(2, 3)
    assert result["relative_insertion_upper"] == Fraction(2, 5)
    assert result["relative_form_upper"] == Fraction(24, 25)
    assert result["completed_seam_inverse_upper"] == 50
    assert result["rational_sufficient_criterion_satisfied"] is False
    assert result["coercivity_criterion_satisfied"] is True
    assert result["physical_incoming_LR_bound_established"] is False
    assert sp.sqrt(2)-1 > sp.Rational(2, 5)


def test_large_insertion_reports_failed_coercivity_without_inverse():
    result = conditional_squared_extension_form_bound(
        duration_upper=Fraction(1), superpotential_upper=Fraction(0),
        insertion_norm_upper=Fraction(1), seam_inverse_upper=Fraction(2))
    assert result["relative_form_upper"] == Fraction(16, 9)
    assert result["coercivity_criterion_satisfied"] is False
    assert result["completed_seam_inverse_upper"] is None


def test_weighted_family_cancels_lambda_squared_without_member_selection():
    result = conditional_amplitude_weighted_form_bound(
        duration_coefficient_upper=Fraction(2), lambda_upper=Fraction(1, 2),
        superpotential_upper=Fraction(1), lambda_squared_insertion_norm_upper=Fraction(1, 10))
    assert result["relative_insertion_upper"] == Fraction(1, 5)
    assert result["relative_form_upper"] == Fraction(11, 25)
    assert result["lambda_squared_insertion_rational_threshold"] == Fraction(1, 5)
    assert result["amplitude_member_selected"] is False


@pytest.mark.parametrize("name,value,exception", [
    ("duration_upper", None, TypeError),
    ("duration_upper", Fraction(0), ValueError),
    ("duration_upper", 1.0, TypeError),
    ("superpotential_upper", Fraction(-1), ValueError),
    ("insertion_norm_upper", None, TypeError),
    ("insertion_norm_upper", Fraction(-1), ValueError),
    ("seam_inverse_upper", Fraction(0), ValueError),
])
def test_form_guard(name, value, exception):
    inputs = dict(duration_upper=Fraction(1), superpotential_upper=Fraction(0),
                  insertion_norm_upper=Fraction(0), seam_inverse_upper=Fraction(2))
    inputs[name] = value
    with pytest.raises(exception):
        conditional_squared_extension_form_bound(**inputs)


def test_one_end_domain_denominator_guard():
    with pytest.raises(ValueError, match="S.T"):
        conditional_squared_extension_form_bound(
            duration_upper=Fraction(1), superpotential_upper=Fraction(3, 2),
            insertion_norm_upper=Fraction(0))

"""CONTROL_ONLY exact algebra, plus read-only retained theorem/guard checks.

Synthetic amplitudes, matrices and coefficients below are mathematical inputs
to bound/projection APIs. They neither select a physical family member nor
instantiate the E1 KKT solver, a covariance, or an incoming lower-order term.
"""
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface.muon_birth_covariance_sensitivity import (
    charged_nambu_tangent_projection,
    minimal_consumed_moments,
    occupation_sensitivity_kernel,
)
from bhsm.interface.muon_birth_fermion_event_kkt_inputs import (
    physical_input_packet,
    quadratic_noether_commutator_kernel,
)
from bhsm.interface.muon_birth_parametric_carrier_bounds import (
    retained_carrier_bound_inputs,
    uniform_carrier_majorants,
)
from bhsm.interface.muon_birth_parametric_fermion_seam import (
    completion_inverse_upper,
    exact_symbolic_seam_cotangent_identity,
    fraction_record,
    parametric_response_packet,
    seam_cotangent_majorants,
)


ROOT = Path(__file__).resolve().parents[1]


def carrier_inputs():
    """CONTROL_ONLY: delta=3/8 at a visibly finite amplitude bound."""
    return dict(a_lower=Fraction(1), a_upper=Fraction(3, 2),
                lambda_upper=Fraction(1, 4), superpotential_upper=Fraction(1),
                kappa_squared=Fraction(2), returned_load_upper=Fraction(7))


def car_data():
    """CONTROL_ONLY normalized two-particle-mode charged Nambu algebra."""
    return dict(conjugation=sp.BlockMatrix(
                    [[sp.zeros(2), sp.eye(2)], [sp.eye(2), sp.zeros(2)]]).as_explicit(),
                charge_grading=sp.diag(sp.eye(2), -sp.eye(2)),
                particle_family_projector=sp.eye(2))


def ordered_kernel(operator):
    return sp.diag(occupation_sensitivity_kernel(operator), sp.zeros(operator.rows))


def exact_zero(value):
    entries = list(value) if isinstance(value, sp.MatrixBase) else [value]
    return all(sp.expand_complex(sp.expand(entry)) == 0 for entry in entries)


@pytest.mark.parametrize("parameters", [
    carrier_inputs(),
    dict(a_lower=Fraction(2), a_upper=Fraction(3), lambda_upper=Fraction(2, 5),
         superpotential_upper=Fraction(1, 4), kappa_squared=Fraction(3, 2),
         returned_load_upper=Fraction(5, 3)),
])
def test_scaled_bounds_majorize_duration_dependent_envelopes(parameters):
    """Test the retained inequalities at finite exact CONTROL_ONLY durations.

    The alternating cubic is an independent lower bound for exp(-x) for
    0<=x<1. No synthetic trial response is called an evaluated physical Mf.
    """
    bounds = uniform_carrier_majorants(**parameters)
    alo, ahi = parameters["a_lower"], parameters["a_upper"]
    limit, s = parameters["lambda_upper"], parameters["superpotential_upper"]
    k2 = parameters["kappa_squared"]
    assert 0 < bounds["delta"] < 1
    for fraction in (Fraction(1), Fraction(3, 4), Fraction(1, 2), Fraction(1, 7)):
        amplitude = fraction*limit
        x = 4*s*ahi*amplitude**2
        alternating_cubic = 1-x+x*x/2-x*x*x/6
        assert alternating_cubic/ahi >= bounds["scaled_Mf_lower"] > 0
        # exp(x)<=1/(1-x) gives a larger inverse envelope at each amplitude.
        inverse_envelope = ahi*amplitude**2/(1-x)
        assert inverse_envelope <= bounds["seam_inverse_upper"]
        assert inverse_envelope/amplitude**2 <= bounds[
            "seam_inverse_over_lambda_squared_upper"]
        for coefficient in (alo, (alo+ahi)/2, ahi):
            duration = coefficient*amplitude**2
            assert alo*amplitude**2 <= duration <= ahi*amplitude**2
            linear_trial = 1/duration+s+(s*s+k2)*duration/3
            assert amplitude**2*linear_trial <= bounds["scaled_Mf_upper"]
    assert bounds["returned_load_to_Mf_lower_ratio_upper"] == (
        parameters["returned_load_upper"]*bounds["seam_inverse_upper"])


def test_zero_superpotential_is_exact_and_optional_child_load_stays_optional():
    parameters = carrier_inputs() | dict(superpotential_upper=Fraction(0),
                                         returned_load_upper=None)
    bounds = uniform_carrier_majorants(**parameters)
    assert bounds["delta"] == 0
    assert bounds["scaled_Mf_lower"] == 1/parameters["a_upper"]
    assert bounds["seam_inverse_upper"] == (
        parameters["a_upper"]*parameters["lambda_upper"]**2)
    assert "returned_load_to_Mf_lower_ratio_upper" not in bounds
    with_zero = uniform_carrier_majorants(**(parameters | dict(returned_load_upper=Fraction(0))))
    assert with_zero["returned_load_to_Mf_lower_ratio_upper"] == 0


@pytest.mark.parametrize("name", tuple(carrier_inputs()))
@pytest.mark.parametrize("invalid", [1, True, 0.25, sp.Rational(1, 4)])
def test_carrier_domain_requires_exact_fraction_inputs(name, invalid):
    with pytest.raises(TypeError, match="exact Fraction"):
        uniform_carrier_majorants(**(carrier_inputs() | {name: invalid}))


@pytest.mark.parametrize("change", [
    dict(a_lower=Fraction(0)), dict(a_lower=Fraction(-1)),
    dict(a_upper=Fraction(0)), dict(lambda_upper=Fraction(0)),
    dict(kappa_squared=Fraction(0)), dict(superpotential_upper=Fraction(-1)),
    dict(returned_load_upper=Fraction(-1)),
    dict(a_lower=Fraction(2)),
    dict(lambda_upper=Fraction(1, 2), a_upper=Fraction(1)),  # delta=1
    dict(lambda_upper=Fraction(1)),  # delta>1
])
def test_carrier_assumptions_reject_nonpositive_reversed_or_noncoercive_domains(change):
    with pytest.raises(ValueError):
        uniform_carrier_majorants(**(carrier_inputs() | change))


def test_retained_inputs_bind_raw_sources_without_selecting_a_family_member():
    retained = retained_carrier_bound_inputs(ROOT)
    parameters = {name: Fraction(value) for name, value in retained["parameters"].items()}
    decimals = {name: Fraction(value) for name, value in retained["source_decimal_values"].items()}
    # An outward duration reconciliation may conservatively widen raw bounds.
    assert parameters["a_lower"] <= decimals["a_lower"]
    assert parameters["a_upper"] >= decimals["a_upper"]
    for name in ("lambda_upper", "superpotential_upper", "kappa_squared", "returned_load_upper"):
        assert parameters[name] == decimals[name]
    for record in retained["source_records"]:
        raw = (ROOT/record["path"]).read_bytes()
        assert len(raw) == record["bytes"]
        assert sha256(raw).hexdigest() == record["raw_sha256"]
    assert retained["bound_scope"]["uniform_in_lambda"] is True
    for name in ("uniform_over_all_spatial_levels_or_spectral_probes",
                 "neutral_resolvent_probe_identified_as_physical_momentum",
                 "complete_active_E1_fermion_operator_or_CAR_projection"):
        assert retained["bound_scope"][name] is False
    assert retained["unscaled_Mf_uniform_upper_finite"] is False
    for name in ("lambda_or_duration_selected", "covariance_or_reset_representative_selected",
                 "point_KKT_callback_called", "old_producer_recomputed",
                 "lower_order_or_mixed_terms_defaulted_to_zero"):
        assert retained[name] is False
    assert uniform_carrier_majorants(**parameters)["scaled_Mf_lower"] > 0


@pytest.mark.parametrize("value", [Fraction(1, 3), Fraction(2, 7), Fraction(1, 1000)])
def test_fraction_serialization_encloses_the_exact_number(value):
    record = fraction_record(value)
    assert Fraction(record["exact"]) == value
    lo, hi = (Fraction(Decimal(text)) for text in record["decimal_enclosure"])
    assert lo <= value <= hi
    assert record["decimal_precision"] == 80


def test_seam_adjoint_majorants_scale_the_supplied_source_cotangent():
    bounds = uniform_carrier_majorants(**carrier_inputs())
    result = seam_cotangent_majorants(bounds)
    b = bounds["seam_inverse_upper"]
    assert result == dict(dual_solve_norm_upper=b, inverse_cotangent_norm_upper=b*b,
                          signed_seam_derivative_norm_factor=b*b)
    # A nonnegative returned load in an arbitrary unitary frame cannot lower
    # the carrier eigenvalue; this is CONTROL_ONLY, not a chosen E1 reset.
    u = sp.Matrix([[sp.Rational(3, 5), -sp.Rational(4, 5)],
                   [sp.Rational(4, 5), sp.Rational(3, 5)]])
    seam = 10*sp.eye(2)+u.adjoint()*sp.diag(0, 7)*u
    assert seam.eigenvals() == {sp.Integer(10): 1, sp.Integer(17): 1}
    assert max(seam.inv().eigenvals()) == sp.Rational(1, 10)
    assert sp.Rational(1, 10) <= sp.Rational(b.numerator, b.denominator)
    assert result["dual_solve_norm_upper"]*Fraction(3, 2) == b*Fraction(3, 2)


@pytest.mark.parametrize("value", [Fraction(0), Fraction(-1), 1, True, 0.5])
def test_seam_majorants_reject_invalid_inverse_bound(value):
    with pytest.raises(ValueError, match="Positive exact"):
        seam_cotangent_majorants(dict(seam_inverse_upper=value))


def test_noncommuting_implicit_adjoint_has_the_negative_seam_derivative():
    seam = sp.Matrix([[3, 1+sp.I], [1-sp.I, 4]])
    derivative = sp.Matrix([[1, 2-sp.I], [2+sp.I, -2]])
    r, dr = sp.Matrix([1+sp.I, 2]), sp.Matrix([1, -sp.I])
    g = sp.Matrix([2-sp.I, 1+sp.I])
    assert seam*derivative != derivative*seam
    v = seam.inv()*r
    p = seam.adjoint().inv()*g
    dv = seam.inv()*(dr-derivative*v)
    lhs = (g.adjoint()*dv)[0]
    rhs = (p.adjoint()*(dr-derivative*v))[0]
    assert exact_zero(lhs-rhs)
    assert not exact_zero(lhs-(p.adjoint()*(dr+derivative*v))[0])
    symbolic = exact_symbolic_seam_cotangent_identity()
    assert symbolic["residual"] == "0"
    assert symbolic["signed_pullback"] == "<g,Dv>=<p,Dr-(D S)v>"
    assert symbolic["physical_source_or_terminal_covector_selected"] is False
    assert symbolic["force_root_equivalence_rederived"] is False


def test_inverse_readout_cotangent_has_correct_order_and_sign():
    seam = sp.Matrix([[3, 1+sp.I], [1-sp.I, 4]])
    derivative = sp.Matrix([[1, 2-sp.I], [2+sp.I, -2]])
    g = sp.Matrix([[1, 2-sp.I], [sp.I, -3]])
    inverse = seam.inv()
    inverse_derivative = -inverse*derivative*inverse
    cotangent = -inverse.adjoint()*g*inverse.adjoint()
    lhs = sp.re(sp.trace(g.adjoint()*inverse_derivative))
    rhs = sp.re(sp.trace(cotangent.adjoint()*derivative))
    assert exact_zero(lhs-rhs)
    assert not exact_zero(cotangent+inverse.adjoint()*g)  # both inverse factors matter
    # Increasing a positive seam lowers the identity inverse readout.
    identity_derivative = -inverse*inverse
    assert sp.expand_complex(sp.trace(identity_derivative)) < 0
    assert exact_symbolic_seam_cotangent_identity()["inverse_readout_cotangent"] == (
        "W_S=-S^(-dagger) G S^(-dagger)")


def test_unknown_lower_order_correction_is_not_zero_and_can_reduce_coercivity():
    b = Fraction(1, 4)
    assert completion_inverse_upper(b, None) is None
    assert completion_inverse_upper(b, Fraction(0)) == b
    assert completion_inverse_upper(b, Fraction(3, 4)) == 1
    carrier, remainder = sp.diag(4, 9), sp.diag(-3, 0)
    normalized = sp.diag(sp.Rational(1, 2), sp.Rational(1, 3))
    relative = normalized*remainder*normalized
    assert max(abs(value) for value in relative.eigenvals()) == sp.Rational(3, 4)
    completed = carrier+remainder
    assert min(completed.eigenvals()) == 1 > 0
    assert max(completed.inv().eigenvals()) == 1 > sp.Rational(b.numerator, b.denominator)


@pytest.mark.parametrize("b", [Fraction(0), Fraction(-1), 1, True, 0.25])
def test_completion_requires_positive_exact_carrier_bound(b):
    with pytest.raises(ValueError, match="Positive exact"):
        completion_inverse_upper(b, None)


@pytest.mark.parametrize("rho", [Fraction(-1, 10), Fraction(1), Fraction(5, 4)])
def test_completion_rejects_relative_bounds_without_strict_coercivity(rho):
    with pytest.raises(ValueError, match="0 <= relative bound < 1"):
        completion_inverse_upper(Fraction(1), rho)


@pytest.mark.parametrize("rho", [0, False, 0.5, sp.Rational(1, 2)])
def test_completion_relative_bound_must_be_fraction(rho):
    with pytest.raises(TypeError, match="exact Fraction"):
        completion_inverse_upper(Fraction(1), rho)


def test_carrier_noether_commutator_vanishes_without_an_amplitude_selection():
    carrier = sp.Symbol("M_f", real=True, positive=True)*sp.eye(2)
    generator = sp.Matrix([[0, 1+sp.I], [-1+sp.I, 0]])
    assert generator.adjoint() == -generator
    assert carrier*generator-generator*carrier == sp.zeros(2)
    # This channel-preserving contraction does not identify the full birth row.
    assert quadratic_noether_commutator_kernel(7*sp.eye(2), generator) == sp.zeros(2)


def test_gamma_even_scalar_and_ordered_particle_scalar_have_distinct_car_duals():
    gamma_even = charged_nambu_tangent_projection(3*sp.eye(4), **car_data())
    ordered = charged_nambu_tangent_projection(ordered_kernel(3*sp.eye(2)), **car_data())
    assert gamma_even["annihilates_all_admissible_tangents"] is True
    assert gamma_even["projected_kernel"] == sp.zeros(4)
    assert ordered["annihilates_all_admissible_tangents"] is False
    assert ordered["projected_kernel"] == sp.diag(
        -sp.Rational(3, 2), -sp.Rational(3, 2), sp.Rational(3, 2), sp.Rational(3, 2))
    assert ordered["particle_sensitivity_kernel"] == -3*sp.eye(2)
    moments = minimal_consumed_moments([ordered_kernel(3*sp.eye(2))], **car_data())
    assert moments["span_dimension"] == 1  # One row, although its particle rank is two.
    assert ordered["particle_sensitivity_kernel"].rank() == 2
    assert moments["physical_state_moment_values"] is None


def test_arbitrarily_small_lower_order_remainder_survives_exact_car_projection():
    large, tiny = sp.Integer(10)**60, sp.Rational(1, 10**80)
    carrier = large*sp.eye(2)
    generator = sp.Matrix([[0, 1], [-1, 0]])
    full = carrier+tiny*sp.diag(1, -1)
    assert min(full.eigenvals()) > 0
    assert tiny/large == sp.Rational(1, 10**140)
    assert quadratic_noether_commutator_kernel(carrier, generator) == sp.zeros(2)
    consumed = quadratic_noether_commutator_kernel(full, generator)
    assert consumed == 2*tiny*sp.Matrix([[0, 1], [1, 0]])
    projected = charged_nambu_tangent_projection(ordered_kernel(consumed), **car_data())
    assert projected["annihilates_all_admissible_tangents"] is False
    assert projected["particle_sensitivity_kernel"] == -consumed
    moments = minimal_consumed_moments([ordered_kernel(consumed),
                                        2*ordered_kernel(consumed)], **car_data())
    assert moments["span_dimension"] == 1
    assert moments["kernel_coefficients"] == ((1,), (2,))
    assert moments["physical_E1_kernel_evaluated"] is False


def test_minimal_moment_rank_can_change_at_a_coefficient_zero_in_a_family():
    amplitude = sp.Symbol("lambda", real=True, positive=True)
    coefficient = amplitude-sp.Rational(1, 2)
    first = ordered_kernel(sp.eye(2))
    independent = ordered_kernel(sp.diag(1, -1))
    assert independent.rank() == 2
    ranks = []
    for control_amplitude in (sp.Rational(1, 4), sp.Rational(1, 2), sp.Rational(3, 4)):
        value = coefficient.subs(amplitude, control_amplitude)
        ledger = minimal_consumed_moments([first, value*independent], **car_data())
        ranks.append(ledger["span_dimension"])
        assert ledger["physical_state_moment_values"] is None
    assert ranks == [2, 1, 2]
    # A smallness/inverse bound cannot replace the necessary nonzero-minor proof.
    projected = charged_nambu_tangent_projection(independent, **car_data())["projected_kernel"]
    assert (coefficient*projected).subs(amplitude, sp.Rational(1, 2)) == sp.zeros(4)


def test_parametric_progress_preserves_the_point_guard_and_null_full_operator_verdict():
    point = physical_input_packet(ROOT)
    parametric = parametric_response_packet(ROOT)
    assert point["first_unavailable"] == dict(argument="parent_jet", operand="P_F",
                                             derivative_order=0, tuple_index=0)
    assert all(value == [None, None, None] for value in point["solver_inputs"].values())
    assert point["solver_invoked"] is point["noether_invoked"] is False
    assert parametric["preserved_point_input_result"] == dict(
        operand="P_F", derivative_order=0, argument="parent_jet", point_value=None,
        guard_modified=False)
    assert parametric["common_scale_retained_physical"] is True
    assert parametric["first_blocker"]["name"] == "INCOMING_C1_ADDITIVE_LR_BRIDGE_ACTION_COTANGENT"
    assert parametric["first_blocker"]["CAR_projected_response"] is None
    for name in ("completed_seam_inverse_upper", "lower_order_relative_bound",
                 "complete_physical_E1_operator_enclosure", "complete_CAR_projection_enclosure",
                 "uniform_state_independence", "uniform_minimal_moment_rank"):
        assert parametric[name] is None
    assert parametric["parametric_decomposition"]["lower_order_enclosure"] is None
    assert parametric["parametric_decomposition"]["boundary_response_is_not_sum_of_local_bulk_mass_matrices"] is True
    assert all(value is False for value in parametric["selectors"].values())
    for name in ("point_KKT_callback_called", "Green_cancellation_substituted",
                 "current_C2_or_synthetic_lower_terms_transplanted", "old_producers_recomputed",
                 "interval_straddles_decision_boundary", "physical_member_selection_proved_necessary"):
        assert parametric[name] is False

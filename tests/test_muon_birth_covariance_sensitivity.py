"""CONTROL_ONLY exact algebra inputs; no matrix is an actual E1 operator/state.

These tests exercise the entire finite tangent space and guard its scope.
They do not execute histories, choose a BHSM state, or fill a missing birth
kernel. All coefficients lie in exact rational real/imaginary arithmetic.
"""
import pytest
import sympy as sp

from bhsm.interface.muon_birth_covariance_sensitivity import (
    admissible_charged_nambu_tangent_basis,
    charged_nambu_tangent_projection,
    minimal_consumed_moments,
    occupation_sensitivity_kernel,
    pure_state_tangent_projection,
    reset_pullback_kernel,
)


def car_data(particle_projector):
    p = sp.Matrix(particle_projector)
    size = p.rows
    return dict(
        conjugation=sp.BlockMatrix([[sp.zeros(size), sp.eye(size)],
                                  [sp.eye(size), sp.zeros(size)]]).as_explicit(),
        charge_grading=sp.diag(sp.eye(size), -sp.eye(size)),
        particle_family_projector=p,
    )


@pytest.fixture
def muon_car():
    """CONTROL_ONLY: two carrier modes in a two-slot family representation."""
    return car_data(sp.diag(0, 1, 0, 1))


def particle_kernel(operator):
    value = sp.Matrix(operator)
    return sp.diag(value, sp.zeros(value.rows))


def real_pair(left, right):
    return sp.expand(sp.re(sp.trace(left*right)))


def test_entire_family_supported_tangent_basis_has_expected_real_dimension(muon_car):
    basis = admissible_charged_nambu_tangent_basis(**muon_car)
    g = muon_car["conjugation"]
    charge = muon_car["charge_grading"]
    p = muon_car["particle_family_projector"]
    family = sp.diag(p, p.conjugate())
    assert len(basis) == 4  # rank(Pi_mu)^2, not one arbitrary variation.
    for x in basis:
        assert x == x.adjoint()
        assert g*x.conjugate()*g.adjoint() == -x
        assert x*charge == charge*x
        assert family*x*family == x
    # The explicit diagonal, real and imaginary coherences are all present.
    assert {x[1, 1] for x in basis} == {0, 1}
    assert {x[1, 3] for x in basis} == {0, 1, sp.I}


def test_projection_preserves_pairing_for_every_basis_tangent(muon_car):
    pp = sp.Matrix([[4, 1, 2, 3], [1, 5, sp.I, 2-sp.I],
                    [2, -sp.I, 6, 7], [3, 2+sp.I, 7, 8]])
    hh = sp.diag(9, 1, 11, 2)
    cross = sp.Matrix(4, 4, list(range(16)))
    delta = sp.BlockMatrix([[pp, cross], [cross.adjoint(), hh]]).as_explicit()
    result = charged_nambu_tangent_projection(delta, **muon_car)
    expected_k = sp.zeros(4)
    expected_k[1, 1], expected_k[3, 3] = 4, 6
    expected_k[1, 3], expected_k[3, 1] = 2-sp.I, 2+sp.I
    expected_s = sp.diag(expected_k/2, -expected_k.conjugate()/2)
    assert result["particle_sensitivity_kernel"] == expected_k
    assert result["projected_kernel"] == expected_s
    assert result["tangent_dimension"] == 4
    assert result["annihilates_all_admissible_tangents"] is False
    for x in admissible_charged_nambu_tangent_basis(**muon_car):
        assert real_pair(x, delta) == real_pair(x, expected_s)
    # A nonzero projected Hermitian kernel detects itself, hence necessity.
    assert real_pair(expected_s, delta) == real_pair(expected_s, expected_s) > 0
    assert result["physical_E1_kernel_evaluated"] is False
    assert result["physical_covariance_selected"] is False
    assert result["continuum_Hadamard_or_tail_certified"] is False


def test_gamma_even_offcharge_and_outside_family_are_exact_annihilators(muon_car):
    a = sp.Matrix([[1, sp.I, 2, 0], [-sp.I, 3, 0, 1],
                   [2, 0, 4, 0], [0, 1, 0, 5]])
    gamma_even = sp.diag(a, a.conjugate())
    offcharge = sp.BlockMatrix([[sp.zeros(4), a],
                               [a.adjoint(), sp.zeros(4)]]).as_explicit()
    outside = particle_kernel(sp.diag(1, 0, 3, 0))
    antihermitian = sp.I*sp.eye(8)
    for delta in (gamma_even, offcharge, outside, antihermitian):
        result = charged_nambu_tangent_projection(delta, **muon_car)
        assert result["projected_kernel"] == sp.zeros(8)
        assert result["annihilates_all_admissible_tangents"] is True
        assert all(real_pair(x, delta) == 0 for x in
                   admissible_charged_nambu_tangent_basis(**muon_car))


def test_noncanonical_compatible_gamma_phase_is_retained():
    data = car_data(sp.eye(2))
    phase = sp.diag(1, sp.I)
    data["conjugation"] = sp.BlockMatrix([[sp.zeros(2), phase],
                                          [phase, sp.zeros(2)]]).as_explicit()
    delta = particle_kernel(sp.Matrix([[2, 1+sp.I], [1-sp.I, 3]]))
    result = charged_nambu_tangent_projection(delta, **data)
    basis = admissible_charged_nambu_tangent_basis(**data)
    assert len(basis) == 4
    for x in basis:
        assert real_pair(x, delta) == real_pair(x, result["projected_kernel"])


def test_moment_span_dimension_is_not_operator_rank():
    data = car_data(sp.eye(2))
    a = particle_kernel(sp.eye(2))
    gamma_even = sp.eye(4)
    result = minimal_consumed_moments({"row": a, "twice": 2*a,
                                       "annihilator": gamma_even}, **data)
    assert result["span_dimension"] == 1
    assert result["basis_particle_kernels"][0].rank() == 2
    assert result["basis_kernel_indices"] == (0,)
    assert result["kernel_coefficients"] == ((1,), (2,), (0,))
    assert result["physical_state_moment_values"] is None
    assert result["absolute_Wick_subtraction_selected"] is False


def test_multiple_consumed_rows_are_reconstructed_from_exact_real_span():
    data = car_data(sp.eye(2))
    a = particle_kernel(sp.eye(2))
    b = particle_kernel(sp.diag(1, -1))
    result = minimal_consumed_moments([a, b, 3*a+2*b, sp.zeros(4)], **data)
    assert result["span_dimension"] == 2
    assert result["kernel_coefficients"] == ((1, 0), (0, 1), (3, 2), (0, 0))
    for kernel, coefficients in zip((a, b, 3*a+2*b, sp.zeros(4)),
                                     result["kernel_coefficients"]):
        reconstructed = sum((coefficient*basis for coefficient, basis in
                             zip(coefficients, result["basis_projected_kernels"])),
                            sp.zeros(4))
        assert reconstructed == charged_nambu_tangent_projection(kernel, **data)["projected_kernel"]
    zero = minimal_consumed_moments([sp.eye(4)], **data)
    assert zero["span_dimension"] == 0
    assert zero["all_rows_state_independent_in_supplied_scope"] is True


def test_ordered_occupation_convention_has_negative_covariance_sign():
    a = sp.Matrix([[2, 1+sp.I], [1-sp.I, 3]])
    x = sp.Matrix([[sp.Rational(1, 5), sp.I/3], [-sp.I/3, -sp.Rational(2, 7)]])
    delta_n = -x
    assert occupation_sensitivity_kernel(a) == -a
    assert sp.expand(sp.trace(a*delta_n)-sp.trace(occupation_sensitivity_kernel(a)*x)) == 0
    assert sp.expand(sp.trace(a*x)-sp.trace(a*delta_n)) != 0


def reset_data(data):
    return {key+side: value for side in ("_event", "_child")
            for key, value in data.items()}


def test_reset_graph_does_not_restrict_incoming_tangent_to_reset_commutant():
    data = car_data(sp.eye(2))
    particle_u = sp.diag(1, sp.I)
    u = sp.diag(particle_u, particle_u.conjugate())
    a = particle_kernel(sp.Matrix([[2, 1], [1, 3]]))
    child = -u*a*u.adjoint()
    result = reset_pullback_kernel(a, child, u, **reset_data(data))
    assert result["pulled_back_kernel"] == sp.zeros(4)
    assert result["incoming_reset_commutator_required"] is False
    basis = admissible_charged_nambu_tangent_basis(**data)
    assert any(x*u != u*x for x in basis)
    for x in basis:
        child_x = u*x*u.adjoint()
        assert real_pair(x, a)+real_pair(child_x, child) == 0
    wrong_sign = reset_pullback_kernel(a, -child, u, **reset_data(data))
    assert wrong_sign["pulled_back_kernel"] == 2*a


def test_zero_local_pure_gradient_is_not_global_state_independence():
    data = car_data(sp.eye(2))
    p = sp.diag(1, 0)
    c = sp.diag(p, sp.eye(2)-p)
    delta = particle_kernel(sp.diag(1, -1))
    local = pure_state_tangent_projection(delta, c, **data)
    assert local["local_first_derivative_zero"] is True
    assert local["state_independence_over_all_pure_covariances_proved"] is False
    assert charged_nambu_tangent_projection(delta, **data)["annihilates_all_admissible_tangents"] is False
    rotation = sp.Matrix([[sp.Rational(3, 5), -sp.Rational(4, 5)],
                          [sp.Rational(4, 5), sp.Rational(3, 5)]])
    rotated_p = rotation*p*rotation.adjoint()
    rotated_c = sp.diag(rotated_p, sp.eye(2)-rotated_p)
    assert rotated_c**2 == rotated_c
    assert sp.trace((rotated_c-c)*delta) == -sp.Rational(32, 25)


def test_charge_compatibility_does_not_silently_fix_particle_number():
    data = car_data(sp.eye(2))
    result = charged_nambu_tangent_projection(particle_kernel(sp.eye(2)), **data)
    assert result["annihilates_all_admissible_tangents"] is False
    assert result["purity_or_fixed_occupation_imposed"] is False


@pytest.mark.parametrize("bad", [None, [[0.1]], [[sp.pi]], [[sp.sqrt(2)]],
                                [[sp.Symbol("x")]], [[sp.nan]], [[sp.oo]],
                                [], [[1, 2]]])
def test_absent_inexact_or_undecidable_kernels_are_rejected(bad):
    with pytest.raises(ValueError):
        charged_nambu_tangent_projection(bad, **car_data(sp.ones(1)))


def test_invalid_car_family_and_charge_data_are_rejected():
    data = car_data(sp.eye(2))
    for changed in (
        {"conjugation": 2*data["conjugation"]},
        {"conjugation": sp.eye(4)},
        {"charge_grading": sp.eye(4)},
        {"particle_family_projector": sp.diag(1, sp.Rational(1, 2))},
        {"particle_family_projector": sp.Matrix([[1, 1], [0, 0]])},
    ):
        with pytest.raises(ValueError):
            charged_nambu_tangent_projection(sp.eye(4), **(data | changed))
    family_data = car_data(sp.diag(1, 0))
    swap = sp.Matrix([[0, 1], [1, 0]])
    family_data["conjugation"] = sp.BlockMatrix([[sp.zeros(2), swap],
                                                [swap, sp.zeros(2)]]).as_explicit()
    with pytest.raises(ValueError, match="Gamma compatible"):
        charged_nambu_tangent_projection(sp.eye(4), **family_data)


def test_invalid_reset_or_missing_ledger_is_not_a_zero_verdict():
    data = car_data(sp.eye(2))
    with pytest.raises(ValueError, match="unitary"):
        reset_pullback_kernel(sp.eye(4), -sp.eye(4), 2*sp.eye(4), **reset_data(data))
    with pytest.raises(ValueError, match="intertwine CAR"):
        reset_pullback_kernel(sp.eye(4), -sp.eye(4), sp.diag(1, sp.I, 1, 1), **reset_data(data))
    with pytest.raises(ValueError, match="nonempty"):
        minimal_consumed_moments([], **data)
    with pytest.raises(ValueError, match="absent"):
        minimal_consumed_moments([None], **data)
    with pytest.raises(ValueError, match="Hermitian"):
        occupation_sensitivity_kernel([[0, 1], [0, 0]])


def test_invalid_supplied_pure_covariance_is_rejected():
    data = car_data(sp.eye(2))
    with pytest.raises(ValueError, match="pure projector"):
        pure_state_tangent_projection(sp.eye(4), sp.eye(4)/2, **data)
    with pytest.raises(ValueError, match="self-dual CAR"):
        pure_state_tangent_projection(sp.eye(4), sp.zeros(4), **data)


def test_density_variation_keeps_literal_adjoint_measure_and_order():
    from scripts.replay_muon_birth_covariance_sensitivity import density_variation_identity
    derived = density_variation_identity()
    assert derived["residual"] == "0"
    assert derived["actual_E1_coefficients_evaluated"] is False
    assert "P^dagger_mu(b beta+delta_beta)" in derived["compact_test_strong_kernel"]
    assert "delta_Gamma0_child" in derived["required_domain_variation"]
    assert derived["boundary_and_domain_terms_dropped"] is False

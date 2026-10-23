"""CONTROL_ONLY exact scalar/constraint contractions, not physical C1 data.

All fields, matrices and stationary branches below are supplied mathematical
controls. A finite null vector does not establish an actual BHSM ambiguity.
"""
import pytest
import sympy as sp

from bhsm.interface.muon_birth_c1_lr_scalar_contraction import (
    constrained_scalar_contraction,
    mixed_scalar_source_kernel,
    scalar_adjoint_residual_bound,
)


def test_full_boundary_constraint_adjoint_differs_from_bulk_only_contraction():
    operator = sp.Matrix([[1, 0, 0], [2, 3, 1], [-1, 2, 4]])
    forcing = sp.Matrix([sp.Rational(2, 5), sp.Rational(3, 7), -sp.Rational(5, 11)])
    ell = sp.Matrix([sp.Rational(7, 13), -sp.Rational(2, 3), sp.Rational(4, 5)])
    # Independent exact full primal solve versus adjoint contraction.
    h = operator.inv()*forcing
    result = constrained_scalar_contraction(operator, forcing, ell)
    assert result["contraction"] == (ell.T*h)[0]
    p = result["adjoint_family"]
    assert operator.T*p == ell
    assert result["contraction"] != (p[1:, :].T*forcing[1:, :])[0]
    assert result["primal_solution_selected"] is False
    assert result["physical_C1_contraction"] is None


def test_singular_compatible_primal_and_adjoint_families_identify_one_contraction():
    operator = sp.diag(1, 2, 0)
    forcing = sp.Matrix([sp.Rational(1, 5), sp.Rational(7, 11), 0])
    ell = sp.Matrix([3, 4, 0])
    result = constrained_scalar_contraction(operator, forcing, ell)
    assert result["supplied_response_nullity"] == 1
    assert result["contraction"] == sp.Rational(103, 55)
    assert len(result["adjoint_free_parameters"]) == 1
    assert result["adjoint_pairing_invariant"] is True
    for parameter in (-3, 0, 5):
        p = result["adjoint_family"].subs(result["adjoint_free_parameters"][0], parameter)
        h = sp.Matrix([sp.Rational(1, 5), sp.Rational(7, 22), parameter])
        assert operator*h == forcing
        assert (ell.T*h)[0] == (p.T*forcing)[0] == result["contraction"]
    assert result["pseudoinverse_used"] is False
    assert result["homogeneous_witness"] is None


def test_surviving_supplied_null_vector_changes_contraction_and_satisfies_every_row():
    operator = sp.Matrix([[1, 0, 0], [0, 2, 0]])
    forcing, ell = sp.Matrix([2, 4]), sp.Matrix([3, 4, 5])
    result = constrained_scalar_contraction(operator, forcing, ell)
    assert result["contraction_identified"] is False
    assert result["contraction"] is None
    witness = result["homogeneous_witness"]
    assert witness["vector"] != sp.zeros(3, 1)
    assert operator*witness["vector"] == witness["equation_residual"] == sp.zeros(2, 1)
    assert witness["contraction_difference"] == (ell.T*witness["vector"])[0] != 0
    first = sp.Matrix([2, 2, 0])
    second = first+witness["vector"]
    assert operator*first == operator*second == forcing
    assert (ell.T*(second-first))[0] == witness["contraction_difference"]
    assert result["physical_C1_homogeneous_witness_certified"] is False


def test_explicit_gauge_slice_can_remove_a_dangerous_homogeneous_direction():
    bulk_and_boundary = sp.Matrix([[1, 0, 0], [0, 2, 0]])
    ell = sp.Matrix([3, 4, 5])
    before = constrained_scalar_contraction(bulk_and_boundary, sp.Matrix([2, 4]), ell)
    assert before["contraction"] is None
    with_slice = bulk_and_boundary.col_join(sp.Matrix([[0, 0, 1]]))
    after = constrained_scalar_contraction(with_slice, sp.Matrix([2, 4, 0]), ell)
    assert after["contraction"] == 14
    assert after["supplied_response_nullity"] == 0
    # This proves the need to test actual constraints, not that this is a BHSM slice.
    assert after["physical_C1_homogeneous_witness_certified"] is False


def test_gauge_blind_covector_can_be_identified_without_a_gauge_slice():
    operator = sp.Matrix([[1, 0, 0], [0, 2, 0]])
    result = constrained_scalar_contraction(operator, sp.Matrix([2, 4]), sp.Matrix([3, 4, 0]))
    assert result["supplied_response_nullity"] == 1
    assert result["contraction_identified"] is True
    assert result["contraction"] == 14


@pytest.mark.parametrize("forcing", [sp.Matrix([1, 2, 1]), sp.Matrix([[1, 0], [2, 1], [0, 1]])])
def test_inconsistent_equation_or_source_direction_is_rejected(forcing):
    operator, ell = sp.diag(1, 2, 0), sp.Matrix([3, 4, 0])
    with pytest.raises(ValueError, match="inconsistent"):
        if forcing.cols == 1:
            constrained_scalar_contraction(operator, forcing, ell)
        else:
            mixed_scalar_source_kernel(operator, forcing, ell, sp.zeros(1, forcing.cols))


def test_multiple_source_directions_preserve_direct_and_induced_contacts():
    operator = sp.Matrix([[2, 1], [0, 3], [2, 1]])
    forcing = sp.Matrix([[1, 2, 0], [3, -1, 4], [1, 2, 0]])
    ell, direct = sp.Matrix([5, -2]), sp.Matrix([[7, -3, 2]])
    result = mixed_scalar_source_kernel(operator, forcing, ell, direct)
    h = operator[:2, :].inv()*forcing[:2, :]
    assert operator*h == forcing
    assert result["induced_source_kernel"] == ell.T*h
    assert result["complete_source_kernel"] == direct+ell.T*h
    assert result["complete_source_kernel"] != direct
    assert result["complete_source_kernel"] != ell.T*h
    assert result["adjoint_pairing_invariant"] is True
    assert result["source_forcing_action_sign_inferred"] is False
    assert result["physical_complete_E1_kernel"] is None
    assert result["physical_CAR_verdict"] is None


def test_singular_response_does_not_zero_fill_induced_mixed_kernel():
    result = mixed_scalar_source_kernel(sp.diag(1, 0), sp.Matrix([[2, 3], [0, 0]]),
                                        sp.Matrix([0, 1]), sp.Matrix([[5, 7]]))
    assert result["explicit_source_kernel"] == sp.Matrix([[5, 7]])
    assert result["induced_source_kernel"] is None
    assert result["complete_source_kernel"] is None
    assert result["homogeneous_witness"]["contraction_difference"] != 0


def test_constrained_stationary_mixed_derivative_keeps_multiplier_curvature_and_rows():
    x, c, h, multiplier = sp.symbols("x C h multiplier", real=True)
    action = sp.Rational(3, 2)*h*h+2*x*h+5*c*h+7*x*c
    constraint = h*h-1-x-2*c-3*x*c
    lagrangian = action+multiplier*constraint
    base = {x: 0, c: 0, h: 1, multiplier: -sp.Rational(3, 2)}
    assert sp.diff(lagrangian, h).subs(base) == constraint.subs(base) == 0
    assert base[multiplier] != 0
    unknowns = (h, multiplier)
    residual = sp.Matrix([sp.diff(lagrangian, h), constraint])
    operator = residual.jacobian(unknowns).subs(base)
    forcing = -residual.diff(c).subs(base)
    row = sp.diff(lagrangian, x)
    ell = sp.Matrix([sp.diff(row, value).subs(base) for value in unknowns])
    direct = sp.Matrix([[sp.diff(row, c).subs(base)]])
    result = mixed_scalar_source_kernel(operator, forcing, ell, direct)
    # Independently eliminate the declared CONTROL_ONLY positive scalar branch.
    stationary_h = sp.sqrt(1+x+2*c+3*x*c)
    reduced_action = action.subs(h, stationary_h)
    actual_mixed = sp.diff(reduced_action, x, c).subs({x: 0, c: 0})
    assert result["complete_source_kernel"][0] == actual_mixed == 16
    assert operator == sp.Matrix([[0, 2], [2, 0]])
    assert ell == sp.Matrix([2, -1])  # R_x participates in the consumed row.
    assert forcing == sp.Matrix([-5, 2])  # Nonzero R_C forcing participates.
    assert direct[0] == sp.Rational(23, 2)  # Includes multiplier*R_xC.
    # Omitting constraint curvature yields a different mixed response.
    wrong_operator = sp.Matrix([[sp.diff(action, h, h), 2], [2, 0]])
    wrong = mixed_scalar_source_kernel(wrong_operator, forcing, ell, direct)
    assert wrong["complete_source_kernel"][0] != actual_mixed
    omitted_rx = mixed_scalar_source_kernel(operator, forcing, sp.Matrix([2, 0]), direct)
    omitted_rc = mixed_scalar_source_kernel(operator, sp.Matrix([-5, 0]), ell, direct)
    assert omitted_rx["complete_source_kernel"][0] != actual_mixed
    assert omitted_rc["complete_source_kernel"][0] != actual_mixed


def test_real_linear_higgs_jacobi_keeps_conjugate_variation():
    coordinates = sp.symbols("r0:4", real=True)
    r = sp.Matrix(coordinates)
    kappa, nu2 = sp.Rational(2, 7), sp.Rational(9, 4)
    squared = (r.T*r)[0]
    gradient = -2*kappa*(squared-nu2)*r
    base_values = [sp.Rational(2, 3), -sp.Rational(1, 5), sp.Rational(3, 7), sp.Rational(1, 2)]
    base = dict(zip(coordinates, base_values))
    potential_jacobi = gradient.jacobian(coordinates).subs(base)
    expected = -2*kappa*((squared.subs(base)-nu2)*sp.eye(4)
                         +2*sp.Matrix(base_values)*sp.Matrix(base_values).T)
    assert potential_jacobi == expected
    complex_structure = sp.diag(sp.Matrix([[0, -1], [1, 0]]), sp.Matrix([[0, -1], [1, 0]]))
    assert potential_jacobi*complex_structure != complex_structure*potential_jacobi
    operator = sp.diag(3, 4, 5, 6)+potential_jacobi
    forcing, ell = sp.Matrix([1, 2, -1, 3]), sp.Matrix([4, -2, 5, 1])
    result = constrained_scalar_contraction(operator, forcing, ell)
    assert result["contraction"] == (ell.T*operator.inv()*forcing)[0]
    complex_linear_only = sp.diag(3, 4, 5, 6)-2*kappa*(squared.subs(base)-nu2)*sp.eye(4)
    wrong = constrained_scalar_contraction(complex_linear_only, forcing, ell)
    assert wrong["contraction"] != result["contraction"]


def test_adjoint_residual_enclosure_retains_response_bound_as_an_assumption():
    operator = sp.Matrix([[2, 1], [0, 3]])
    h, ell, candidate = sp.Matrix([3, 4]), sp.Matrix([5, -2]), sp.Matrix([1, 0])
    forcing = operator*h
    result = scalar_adjoint_residual_bound(operator, forcing, ell, candidate, 5)
    error = abs((ell.T*h)[0]-result["candidate_contraction"])
    assert result["adjoint_residual"] == ell-operator.T*candidate
    assert error <= result["absolute_contraction_error_upper"]
    assert result["supplied_response_norm_bound_certified"] is False
    assert result["physical_scalar_error_enclosure"] is None
    assert result["carrier_inverse_substituted_for_scalar_response"] is False
    exact = constrained_scalar_contraction(operator, forcing, ell)["adjoint_family"]
    zero = scalar_adjoint_residual_bound(operator, forcing, ell, exact, 5)
    assert zero["absolute_contraction_error_upper"] == 0
    assert zero["candidate_contraction"] == (ell.T*h)[0]


@pytest.mark.parametrize("slot", range(3))
def test_missing_response_forcing_or_covector_is_not_defaulted_to_zero(slot):
    arguments = [sp.eye(2), sp.Matrix([1, 2]), sp.Matrix([3, 4])]
    arguments[slot] = None
    with pytest.raises(ValueError, match="absent; no zero substitution"):
        constrained_scalar_contraction(*arguments)


def test_missing_direct_source_contact_is_not_defaulted_to_zero():
    with pytest.raises(ValueError, match="explicit_source_kernel is absent"):
        mixed_scalar_source_kernel(sp.eye(2), sp.eye(2), sp.Matrix([3, 4]), None)


@pytest.mark.parametrize("invalid", [sp.Float(0.1), sp.I, sp.Symbol("unbound"), sp.oo])
def test_response_operands_require_bound_exact_real_coordinates(invalid):
    with pytest.raises(ValueError, match="exact real rational"):
        constrained_scalar_contraction(sp.Matrix([[invalid]]), sp.Matrix([1]), sp.Matrix([2]))


@pytest.mark.parametrize("arguments", [
    (sp.zeros(0, 0), sp.Matrix([1]), sp.Matrix([2])),
    (sp.eye(2), sp.Matrix([1]), sp.Matrix([2, 3])),
    (sp.eye(2), sp.Matrix([1, 2]), sp.Matrix([[2, 3]])),
    (sp.eye(2), sp.eye(2), sp.Matrix([2, 3])),
])
def test_contraction_dimensions_are_explicit(arguments):
    with pytest.raises(ValueError):
        constrained_scalar_contraction(*arguments)


@pytest.mark.parametrize("bound", [None, -1, sp.Float(1.0), sp.I])
def test_residual_bound_requires_an_explicit_nonnegative_exact_bound(bound):
    with pytest.raises(ValueError):
        scalar_adjoint_residual_bound(sp.eye(2), sp.Matrix([1, 2]), sp.Matrix([3, 4]),
                                      sp.Matrix([3, 4]), bound)

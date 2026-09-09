import numpy as np
import pytest
from flint import arb, ctx
from bhsm.interface.arb_symmetric_inertia import shifted_inertia, isolate_index


def test_uncertain_symmetric_family_has_verified_inertia():
    matrix = [[arb(-2, '.01'), arb(0, '.01')], [arb(0, '.01'), arb(3, '.01')]]
    result = shifted_inertia(matrix, 0)
    assert (result['negative'], result['positive'], result['zero']) == (1, 1, 0)


def test_nonorthogonal_exact_basis_preserves_inertia():
    result = shifted_inertia(np.diag([-2., 1., 3.]), 0., basis=np.array([[2., 1., 0.], [0., 1., 1.], [0., 0., .5]]))
    assert result['negative'] == 1 and result['positive'] == 2
    assert result['floating_orthogonality_assumed'] is False


def test_index_is_not_inferred_from_floating_label():
    matrix = np.diag([-2., 1., 3.])
    assert isolate_index(matrix, .9, 1.1, 1)['validation_passed']
    assert not isolate_index(matrix, .9, 1.1, 0)['validation_passed']


def test_multiple_eigenvalues_inside_interval_fail_simple_isolation():
    result = isolate_index(np.diag([1., 1., 3.]), .9, 1.1, 0)
    assert result['enclosed_eigenvalue_count'] == 2
    assert not result['validation_passed']


def test_boundary_contact_and_unresolved_pivot_do_not_pass():
    with pytest.raises(ArithmeticError, match='unresolved'):
        shifted_inertia(np.diag([1., 3.]), 1.)
    with pytest.raises(ArithmeticError, match='unresolved'):
        shifted_inertia([[0., 1.], [1., 0.]], 0.)


def test_singular_basis_empty_symmetric_family_and_nonfinite_inputs_fail():
    with pytest.raises(ArithmeticError, match='basis'):
        shifted_inertia(np.eye(2), 0, basis=np.zeros((2, 2)))
    with pytest.raises(ValueError):
        shifted_inertia([[1., 2.], [3., 4.]], 0)
    with pytest.raises(ValueError):
        shifted_inertia([[arb('nan')]], 0)


def test_precision_restored_after_success_and_failure():
    previous = ctx.prec
    shifted_inertia([[2.]], 0., precision=128)
    assert ctx.prec == previous
    with pytest.raises(ArithmeticError):
        shifted_inertia([[0.]], 0., precision=128)
    assert ctx.prec == previous

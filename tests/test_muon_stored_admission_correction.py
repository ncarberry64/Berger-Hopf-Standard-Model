import numpy as np
import pytest
from bhsm.interface.muon_stored_admission_correction import bounded_stored_admission_correction


def test_fixed_complex_saddle_refinement_and_original_rhs_assembly_are_separate():
    rng = np.random.default_rng(732)
    n, nx, nf = 7, 3, 2
    A = rng.normal(size=(n, n))+0.2j*rng.normal(size=(n, n))+4*np.eye(n)
    F = rng.normal(size=(nf, n))+0.1j*rng.normal(size=(nf, n))
    K = np.block([[A, F.T], [F, np.zeros((nf, nf))]])
    z = rng.normal(size=n+nf)+0.3j*rng.normal(size=n+nf)
    rhs = K@z
    Hx = rng.normal(size=(n, nx))+0.2j*rng.normal(size=(n, nx))
    x = rng.normal(size=nx); source = rng.normal(size=n)+0.1j
    target = rhs[:n]+Hx@x+source
    a = bounded_stored_admission_correction(K, rhs, z+1e-5, n,
        action_rows=np.c_[Hx, A], fixed_x=x, source_rows=source,
        target_rows=target, correction_count=2)
    assert a['exact_stored']['bordered_residual_upper'] < 1e-45
    np.testing.assert_allclose(a['arrays']['correction_solution_high'], z, atol=2e-15)
    # Original rows exclude the actual nonzero named frame reaction.
    assert a['exact_stored']['original_action_rows_residual_upper'] > .1
    assert not a['rounded_original_rows_guard_passed']
    np.testing.assert_allclose(a['arrays']['exact_stored_original_action_rows'],
        -F.T@a['arrays']['correction_solution_high'][n:]
        +a['arrays']['stored_rhs_assembly_difference'], atol=2e-15)
    np.testing.assert_array_equal(a['arrays']['stored_saddle'], K)
    np.testing.assert_array_equal(a['arrays']['stored_rhs'], rhs)


def test_guard_applies_to_original_rows_not_only_border_and_budget_is_bounded():
    n=4; F=np.array([[1., 0., 0., 0.]])
    A=np.diag([2., 3., 4., 5.]).astype(complex)
    K=np.block([[A, F.T], [F, np.zeros((1, 1))]])
    z=np.array([1., 2., 3., 4., 0.], complex); rhs=K@z
    a=bounded_stored_admission_correction(K, rhs, z+1e-4, n,
        action_rows=np.c_[np.zeros((n, 1)), A], fixed_x=np.zeros(1),
        source_rows=np.zeros(n), target_rows=rhs[:n])
    assert a['rounded_original_rows_guard_passed']
    assert a['high_low_original_rows_guard_passed']
    assert a['exact_stored']['original_action_rows_residual_upper'] < 1e-45
    with pytest.raises(ValueError, match='bounded'):
        bounded_stored_admission_correction(K, rhs, z, n, correction_count=4)
    with pytest.raises(ValueError, match='original guard'):
        bounded_stored_admission_correction(K, rhs, z, n, tolerance=1e-8)

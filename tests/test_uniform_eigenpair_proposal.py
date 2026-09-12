"""Independent spectral fixtures; these are not BHSM numerical evidence."""
from types import SimpleNamespace
import numpy as np
import pytest
from flint import arb, ctx
from bhsm.interface.uniform_eigenpair_proposal import propose, use_uniform_proposal
from bhsm.interface.physical_hs_value import verified_eigenline
from bhsm.interface.arb_eigenpair_inclusion import verify_eigenpair_box


@pytest.fixture(autouse=True)
def precision():
    previous = ctx.prec
    ctx.prec = 256
    yield
    ctx.prec = previous


def test_complete_matrix_family_is_enclosed_and_index_verified():
    h = np.array([[arb(1, '.001'), arb(0, '.002')],
                  [arb(0, '.002'), arb(3, '.001')]], dtype=object)
    original = lambda *args: (_ for _ in ()).throw(ZeroDivisionError('old interval solve'))
    cert = SimpleNamespace(QDIM=0, _eigenline=original)
    checks = []
    with use_uniform_proposal(cert, selected=0), verified_eigenline(
            cert, checks, expected_index=0, normalize_proposal_center=True):
        p, lam, _, _ = cert._eigenline(h, np.diag([1., 3.]), [1., 0.])
    assert cert._eigenline is original
    assert checks[0]['normalized_eigenpair_enclosed']
    assert checks[0]['selected_zero_based_index_verified'] == 0
    assert verify_eigenpair_box(h, p, lam, precision=256)['validation_passed']
    # Explicit interior family member has an eigenpair displaced from the
    # midpoint; all coordinates must be contained in the published box.
    vals, vecs = np.linalg.eigh(np.array([[1.0005, .001], [.001, 2.9995]]))
    v = vecs[:, 0]
    if v[0] < 0:
        v = -v
    assert all(x.contains(arb(float(y))) for x, y in zip(p, v))
    assert lam.contains(arb(float(vals[0])))


def test_family_containing_multiple_eigenvalue_is_not_certified():
    h = np.array([[arb(1, '1.1'), arb(0)], [arb(0), arb(3, '1.1')]])
    with pytest.raises(ArithmeticError, match='failed independent inclusion'):
        propose(h, [1., 0.], selected=0, max_attempts=6)


def test_restore_on_error_and_repeated_eigenvalue_fail_closed():
    original = lambda *args: None
    cert = SimpleNamespace(QDIM=0, _eigenline=original)
    with pytest.raises((ArithmeticError, ZeroDivisionError)):
        with use_uniform_proposal(cert, selected=0):
            cert._eigenline(np.eye(2), np.eye(2), [1., 0.])
    assert cert._eigenline is original


def test_nonfinite_matrix_rejected():
    with pytest.raises(ValueError, match='finite matrix'):
        propose(np.diag([float('nan'), 3]), [1., 0.], selected=0)


def test_diverging_search_preserves_failed_inclusion_without_singularity_claim():
    h = np.array([[arb(1, '.3'), arb(0, '.3')],
                  [arb(0, '.3'), arb(1.1, '.3')]])
    with pytest.raises(ArithmeticError) as caught:
        propose(h, [1., 0.], selected=0)
    report = caught.value.eigenpair_inclusion
    assert report['proposal_search_exhausted']
    assert not report['matrix_family_singularity_proved']
    assert report['proposal_failure_reason'] == 'proposal_vector_radius_exceeds_search_limit'

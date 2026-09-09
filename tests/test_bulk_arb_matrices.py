from types import SimpleNamespace
from pathlib import Path
import sys
import numpy as np
import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface import bulk_arb_matrices as bulk
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_accepted_replay_center_outward_74d as parent


def identical(a, b):
    assert a.shape == b.shape
    assert all(x.mid() == y.mid() and x.rad() == y.rad()
               for x, y in zip(a.flat, b.flat, strict=True))


@pytest.mark.parametrize('shape', [(13, 99), (74, 297), (99, 1)])
def test_exact_ball_preservation_for_strided_inputs_and_roundtrip(shape):
    previous = ctx.prec
    ctx.prec = 256
    try:
        backing = np.empty((shape[0], shape[1]*2), dtype=object)
        for i in range(backing.size):
            backing.flat[i] = arb(i % 31 - 15, '1e-70') + arb(2)**-180
        values = backing[:, ::2]
        assert not values.flags.c_contiguous
        old, new = parent._mat(values), bulk.to_matrix(values)
        identical(parent._array(old), bulk.to_array(new))
        identical(values, bulk.to_array(new))
    finally:
        ctx.prec = previous


def test_binary64_and_integer_inputs_preserve_original_constructor_semantics():
    for values in (np.array([.1, -1e-300, 2.]), np.array([[2, -3], [4, 0]])):
        identical(parent._array(parent._mat(values)), bulk.to_array(bulk.to_matrix(values)))


def test_context_restores_on_error_and_rejects_changed_parent():
    module = SimpleNamespace(_mat=parent._mat, _array=parent._array)
    with pytest.raises(ArithmeticError):
        with bulk.use_bulk_matrices(module):
            assert module._mat is bulk.to_matrix
            assert module._array is bulk.to_array
            raise ArithmeticError('test exit')
    assert module._mat is parent._mat and module._array is parent._array
    module._mat = bulk.to_matrix
    with pytest.raises(RuntimeError, match='parent'):
        with bulk.use_bulk_matrices(module):
            pass
    assert module._array is parent._array


def test_empty_and_tensor_layouts_fail_closed():
    for value in (np.zeros((0, 2)), np.zeros((2, 2, 2)), 1.):
        with pytest.raises(ValueError):
            bulk.to_matrix(value)
    with pytest.raises(ValueError):
        bulk.to_array(arb_mat(0, 2))

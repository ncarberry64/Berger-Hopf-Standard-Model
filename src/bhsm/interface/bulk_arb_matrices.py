"""Exact bulk transfers between object arrays and Arb matrices."""
from contextlib import contextmanager
import hashlib
import inspect
import numpy as np
from flint import arb_mat

PARENT_SHA256 = {
    '_mat': '580526A2337A872997D8D7E1D655FB86C4257FC7FFD16ABD55DFD5367B5B840B',
    '_array': 'AF8524C762557338E3552A5B5E02108F93219316A9AD32A62489557C75BCC5BF',
}


def to_matrix(values):
    """Preserve row-major order and Arb balls; vectors become column matrices."""
    array = np.asarray(values, dtype=object)
    if array.ndim == 1:
        array = array[:, None]
    if array.ndim != 2 or min(array.shape) < 1:
        raise ValueError('nonempty vector or matrix required')
    return arb_mat(array.shape[0], array.shape[1], array.ravel(order='C').tolist())


def to_array(matrix):
    """Copy every Arb entry without float conversion or interval recomputation."""
    rows, columns = matrix.nrows(), matrix.ncols()
    if min(rows, columns) < 1:
        raise ValueError('nonempty Arb matrix required')
    return np.fromiter(matrix.entries(), dtype=object, count=rows*columns).reshape(rows, columns)


@contextmanager
def use_bulk_matrices(module):
    """Guard the two original converters and restore them on every exit.

    No arithmetic, contraction ordering, or numerical precision is changed.
    Callers must include this adapter in their independent source fingerprint.
    """
    originals = {name: getattr(module, name) for name in PARENT_SHA256}
    for name, function in originals.items():
        digest = hashlib.sha256(inspect.getsource(function).encode()).hexdigest().upper()
        if digest != PARENT_SHA256[name]:
            raise RuntimeError('parent Arb matrix converter changed; reconciliation required')
    module._mat, module._array = to_matrix, to_array
    try:
        yield
    finally:
        module._mat, module._array = originals['_mat'], originals['_array']

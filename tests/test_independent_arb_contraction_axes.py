import numpy as np
import pytest
from bhsm.interface.independent_arb_contraction_axes import independent_legs


def test_independent_axes_preserve_multilinear_entry_order():
    a=np.arange(6,dtype=float).reshape(3,2,1,1)
    b=np.arange(9,dtype=float).reshape(3,1,3,1)+1
    c=np.arange(12,dtype=float).reshape(3,1,1,4)+2
    legs,shape=independent_legs([a,b,c],3)
    expected=np.sum(a*b*c,axis=0)
    actual=np.empty((2,3,4))
    for i,j,k in np.ndindex(actual.shape):
        actual[i,j,k]=sum(legs[0][s,i]*legs[1][s,j]*legs[2][s,k] for s in range(3))
    assert shape==(2,3,4)
    assert np.array_equal(actual.reshape(shape),expected)


@pytest.mark.parametrize('shapes',[
    [(3,2,1),(3,2,1)], # shared index is a diagonal, not an independent product
    [(3,1,2),(3,2,1)], # reordering would silently transpose output entries
    [(3,2,2),(3,1,1)], # one leg varies on two indices
])
def test_coupled_or_reordered_axes_fail(shapes):
    with pytest.raises(ValueError):independent_legs([np.ones(s) for s in shapes],3)

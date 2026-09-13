"""The grouped support keeps Euclidean transverse geometry and all 75 columns."""
import numpy as np
import pytest
from flint import arb,ctx
from scripts.diagnose_n12_gate7_affine_basis_uniform_hessian import support


def test_group_support_contains_attaining_opposite_sign_directions():
    previous=ctx.prec;ctx.prec=256
    try:
        matrix=np.full((2,75),arb(0),dtype=object)
        matrix[0,:3]=[arb(2),arb(3),arb(4)]
        matrix[1,:3]=[-arb(3)/2,arb(-12),arb(5)]
        bound=support(matrix)
        assert abs(bound[0]-7)<arb('1e-60')
        assert abs(bound[1]-arb(29)/2)<arb('1e-60')
        for row,direction in [(0,[arb(1),arb(3)/5,arb(4)/5]),(1,[-arb(1),-arb(12)/13,arb(5)/13])]:
            vector=np.full(75,arb(0),dtype=object);vector[:3]=direction
            assert abs(sum((v*v for v in vector[1:]),arb(0))-1)<arb('1e-60')
            value=matrix[row]@vector
            assert abs(value-bound[row])<arb('1e-60')
    finally:ctx.prec=previous


def test_missing_affine_direction_is_rejected():
    with pytest.raises(ValueError,match='all 75'):
        support(np.full((99,74),arb(0),dtype=object))

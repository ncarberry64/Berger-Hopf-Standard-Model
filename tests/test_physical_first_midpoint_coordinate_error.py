from fractions import Fraction as F
import numpy as np
import pytest
from bhsm.interface.physical_first_midpoint_coordinate_error import combine_coordinate_errors


def exact(a):return np.array([F(float(v)) for v in a.flat],dtype=object).reshape(a.shape)


def test_endpoint_error_balls_propagate_through_ill_conditioned_basis():
    s=np.array([[1.,1.],[1.,1.+2**-20]])
    base=np.array([[1e-16,-2e-16],[3e-16,1e-16]]);br=np.full((2,2),1e-30)
    d=np.array([[[1e-12],[-2e-12]],[[3e-12],[4e-12]]]);dr=np.full(d.shape,1e-24)
    arrays,report=combine_coordinate_errors(s,base,br,d,dr,.1,1)
    se=exact(s);inverse=np.array([[se[1,1],-se[0,1]],[-se[1,0],se[0,0]]],dtype=object)/(se[0,0]*se[1,1]-se[0,1]*se[1,0])
    midpoint=exact(arrays['combined_coordinate_error_mid']);radius=exact(arrays['combined_coordinate_error_radius'])
    for mask in range(16):
        signs=np.array([1 if mask&(1<<i) else -1 for i in range(4)],dtype=object).reshape(d.shape)
        de=exact(d)+signs*exact(dr)
        be=exact(base)+signs.reshape(base.shape)*exact(br)
        delta=np.column_stack((de[0],-de[1]))*F(.1)/8
        target=be+inverse@delta
        assert all(abs(v)<=r for v,r in zip((target-midpoint).flat,radius.flat))
    assert report['physical_frame_error_enclosed'] is False


def test_negative_endpoint_radius_fails():
    with pytest.raises(ValueError):
        combine_coordinate_errors(np.eye(2),np.zeros((2,2)),np.zeros((2,2)),
                                  np.zeros((2,2,1)),-np.ones((2,2,1)),.1,1)

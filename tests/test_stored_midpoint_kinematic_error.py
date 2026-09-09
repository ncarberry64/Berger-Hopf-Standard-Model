from fractions import Fraction as F
import numpy as np
import pytest
from flint import ctx
from bhsm.interface.stored_midpoint_kinematic_error import enclose_midpoint_coordinates, bound_stored_tensor_pullback


def fraction_array(a):
    return np.array([F(float(v)) for v in a.flat],dtype=object).reshape(a.shape)


def operands():
    return dict(basis=np.array([[1.,1.],[1.,1.+2**-20]]),
        frames=np.array([[[1.,3.],[-2.,4.]],[[5.,-1.],[2.,3.]]]),
        axes=np.array([[1.,2.],[2.,-3.]]),
        first_derivatives=np.array([[[.1,.3],[-.7,.4]],[[.2,-.5],[.8,.1]]]),
        step=.03,retained_dimension=1)


def evaluate(p):
    blocks=[]
    for side,sign in enumerate((1,-1)):
        axis=p['axes'][side]/np.linalg.norm(p['axes'][side])
        blocks.append(p['frames'][side]@(np.eye(2)-np.outer(axis,axis))/2
                      + sign*p['step']*p['first_derivatives'][side]/8)
    target=np.column_stack(blocks)
    return dict(p,stored_target=target,approximate_coordinates=np.linalg.solve(p['basis'],target))


def exact_target(p):
    blocks=[]
    for side,sign in enumerate((1,-1)):
        axis=fraction_array(p['axes'][side]);frame=fraction_array(p['frames'][side])
        first=fraction_array(p['first_derivatives'][side])
        proj=np.eye(2,dtype=object)-np.outer(axis,axis)/sum(v*v for v in axis)
        blocks.append(frame@proj/2+sign*F(p['step'])*first/8)
    return np.column_stack(blocks)


def test_ill_conditioned_normalized_construction_contains_exact_rational_target():
    p=evaluate(operands());before=ctx.prec
    arrays,report=enclose_midpoint_coordinates(**p)
    assert ctx.prec==before
    target=exact_target(p);s=fraction_array(p['basis'])
    inverse=np.array([[s[1,1],-s[0,1]],[-s[1,0],s[0,0]]],dtype=object)/(s[0,0]*s[1,1]-s[0,1]*s[1,0])
    target_error=target-fraction_array(p['stored_target'])
    combined=inverse@target-fraction_array(p['approximate_coordinates'])
    for key,exact in [('target_error',target_error),('construction_coordinate_error',inverse@target_error),
                      ('combined_coordinate_error',combined)]:
        mid=fraction_array(arrays[key+'_mid']);rad=fraction_array(arrays[key+'_radius'])
        assert all(abs(v)<=r for v,r in zip((exact-mid).flat,rad.flat))
    bound=F(report['combined_construction_and_solve_error']['combined_operator_norm_upper'])
    for mask in range(16):
        vector=np.array([F(1 if mask&(1<<j) else -1,2) for j in range(4)],dtype=object)
        image=combined@vector
        assert sum(v*v for v in image)<=bound*bound
    assert report['first_derivative_physical_error_enclosed'] is False
    q=np.array([[[2.,-3.],[-3.,5.]],[[7.,1.],[1.,-2.]]])
    output=np.array([[3.,-2.]])
    e=report['combined_construction_and_solve_error']
    pulled=bound_stored_tensor_pullback(output,q,p['approximate_coordinates'],1,
                                      e['retained_operator_norm_upper'],e['complement_operator_norm_upper'])
    mapped=sum((F(float(output[0,i]))*fraction_array(q[i]) for i in range(2)),np.zeros((2,2),dtype=object))
    xs=inverse@target;xh=fraction_array(p['approximate_coordinates'])
    difference=xs.T@mapped@xs-xh.T@mapped@xh
    assert sum(v*v for v in difference.flat)<=F(pulled['pullback_error_frobenius_upper'])**2


def test_fixed_initial_node_has_exact_zero_left_block():
    p=operands();p['frames'][0]=0;p['first_derivatives'][0]=0
    p=evaluate(p);p['axes'][0]=0
    arrays,_=enclose_midpoint_coordinates(**p,fixed_left=True)
    assert np.all(arrays['combined_coordinate_error_mid'][:,:2]==0)


@pytest.mark.parametrize('kind',['zero_axis','nonfinite','negative_step','nonzero_fixed_left','singular'])
def test_invalid_construction_fails(kind):
    p=evaluate(operands())
    if kind=='zero_axis':p['axes'][1]=0
    elif kind=='nonfinite':p['first_derivatives'][1,0,0]=np.nan
    elif kind=='negative_step':p['step']=-1
    elif kind=='nonzero_fixed_left':p['fixed_left']=True
    elif kind=='singular':p['basis'][:]=1
    with pytest.raises((ValueError,RuntimeError,ZeroDivisionError)):
        enclose_midpoint_coordinates(**p)


def test_nonsymmetric_tensor_does_not_use_symmetric_cross_term():
    q=np.array([[[1.,2.],[3.,4.]]])
    with pytest.raises(ValueError):
        bound_stored_tensor_pullback(np.ones((1,1)),q,np.eye(2),1,.01,.02)

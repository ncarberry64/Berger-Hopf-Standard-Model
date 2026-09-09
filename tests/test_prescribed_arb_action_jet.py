import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
import sympy as sp
from flint import arb, ctx
from bhsm.interface.prescribed_arb_action_jet import (
    prescribed_action_jet, batched_scalar_curvature, batched_fixed_contractions,
    batched_first_variation_contractions,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import certify_n12_gate7_accepted_replay_center_outward_74d as cert


def toy_action():
    module = SimpleNamespace(STATE=2, LOCAL=2, POINTS=1,
        HOPF_ORBIT_VOLUME=1., Mixed=cert.Mixed, _mat=cert._mat,
        _array=cert._array, _local_variables=cert._local_variables)

    def integrand(state, node, directions, leg_values):
        x, y = module._local_variables(state, directions, leg_values)
        return SimpleNamespace(bulk=x**5 + 3*x**2*y**2,
                               inertia=module.Mixed.constant(1, directions))

    module._integrand = integrand
    module._boundary = lambda state, directions, raw_legs=None: (
        (((0, arb(1)),), ((1, arb(1)),)), module.Mixed.constant(0, directions))
    return module


def test_curved_scalar_batch_matches_independent_symbolic_chain_rule():
    module = toy_action()
    state=np.array([2,3]); raw_u=np.array([1,-2])
    raw_v=np.array([[2,-1,3],[1,4,-2]])
    p=np.array([1,2]); p_u=np.array([3,-1])
    p_v=np.array([[1,2,4],[2,-1,3]])
    p_uv=np.array([[2,1,-1],[-3,2,1]])
    last=np.array([[1,3],[-2,1]]); last_u=np.array([[2,-1],[1,4]])
    last_v=np.arange(12).reshape(2,3,2)-4
    last_uv=3-np.arange(12).reshape(2,3,2)
    actual=batched_scalar_curvature(module,state,[np.eye(2)],raw_u,raw_v,
                                   p,p_u,p_v,p_uv,last,last_u,
                                   last_v.reshape(2,6),last_uv.reshape(2,6))
    t1,t2,t3,x,y=sp.symbols('t1 t2 t3 x y')
    for j in range(3):
        for k in range(2):
            z=[]
            for i in range(2):
                moving_p=p[i]+p_u[i]*x+p_v[i,j]*y+p_uv[i,j]*x*y
                moving_last=last[i,k]+last_u[i,k]*x+last_v[i,j,k]*y+last_uv[i,j,k]*x*y
                z.append(state[i]+raw_u[i]*x+raw_v[i,j]*y
                         +(t1+t2)*moving_p+t3*moving_last)
            polynomial=sp.Poly(z[0]**5+3*z[0]**2*z[1]**2,t1,t2,t3,x,y)
            for index, powers in enumerate(((0,0),(1,0),(0,1),(1,1))):
                expected=int(polynomial.coeff_monomial((1,1,1,*powers)))
                value=actual[index][k] if index<2 else actual[index][j,k]
                assert value.contains(expected)


def test_affine_path_matches_original_action_and_preserves_shapes(monkeypatch):
    previous=ctx.prec; ctx.prec=192
    try:
        monkeypatch.setattr(cert,'POINTS',1)
        state=np.zeros(cert.STATE)
        term=cert._integrand([arb(0)]*cert.STATE,0,0,None)
        mapping=np.zeros((cert.LOCAL,cert.STATE),dtype=object)
        for i,row in enumerate(term.maps):
            for j,value in row: mapping[i,j]=value
        rng=np.random.default_rng(813)
        shapes=((cert.STATE,2,1,1),(cert.STATE,1,1,1),(cert.STATE,1,1,3))
        legs=[np.array([arb(int(v))/32 for v in rng.integers(-2,3,np.prod(shape))],dtype=object).reshape(shape)
              for shape in shapes]
        expected=cert._contracted_action(state,legs,[mapping])
        actual=prescribed_action_jet(cert,state,[mapping],(2,1,3),
                                    {1:legs[0],2:legs[1],4:legs[2]}).d[7]
        assert np.shape(actual)==(2,1,3)
        assert all(a.overlaps(b) for a,b in zip(actual.flat,expected.flat))
    finally: ctx.prec=previous


@pytest.mark.parametrize('mask,shape',[(0,(2,1)),(2,(2,1)),(1,(2,2))])
def test_invalid_path_mask_or_shape_fails(mask,shape):
    with pytest.raises(ValueError):
        prescribed_action_jet(toy_action(),[1,2],[np.eye(2)],(1,),
                              {mask:np.zeros(shape)})


def test_nonfinite_derivative_fails():
    with pytest.raises(ArithmeticError):
        prescribed_action_jet(toy_action(),[1,2],[np.eye(2)],(1,),
                              {1:np.array([[arb('nan')],[arb(0)]])})


def test_constructor_restored_after_action_failure():
    module=toy_action(); previous=module._local_variables
    def fail(*args): raise RuntimeError('deliberate action failure')
    module._integrand=fail
    with pytest.raises(RuntimeError,match='deliberate'):
        prescribed_action_jet(module,[1,2],[np.eye(2)],(1,),{1:np.ones((2,1))})
    assert module._local_variables is previous


def _toy_affine(module, *legs):
    axes=tuple(1 if np.ndim(v)==1 else np.shape(v)[1] for v in legs)
    values={}
    for i,value in enumerate(legs):
        values[1<<i]=np.asarray(value).reshape(module.STATE,*(
            n if j==i else 1 for j,n in enumerate(axes)))
    return np.asarray(prescribed_action_jet(module,[2,3],[np.eye(2)],axes,values).d[-1])


def test_fixed_batch_returns_the_three_required_contractions():
    module=toy_action(); output=np.eye(2); fixed=np.array([[1,2,3],[2,1,-1]])
    u=np.array([1,3]); v=np.array([[2,3],[-1,4]])
    result=batched_fixed_contractions(module,[2,3],[np.eye(2)],output,fixed,u,v)
    expected=(_toy_affine(module,output,fixed,u),
              _toy_affine(module,output,fixed,v),
              _toy_affine(module,output,fixed,u,v))
    for a,b in zip(result,expected):
        assert all(x.overlaps(y) for x,y in zip(a.flat,b.flat))


def test_first_variation_groups_preserve_each_column_order():
    module=toy_action(); output=np.eye(2); u=np.array([1,3])
    v=np.array([[2,3],[-1,4]])
    pv=np.array([[1,2],[3,-1]]); qv=pv+2; hv=pv-1
    pu=np.array([1,2]); qu=pu+2; hu=pu-1
    actual=batched_first_variation_contractions(module,[2,3],[np.eye(2)],
                                               output,pv,qv,hv,pu,qu,hu,u,v)
    expected=tuple(_toy_affine(module,output,x,u) for x in (pv,qv,hv))+tuple(
        _toy_affine(module,output,x[:,None],v) for x in (pu,qu,hu))
    for a,b in zip(actual,expected):
        assert all(x.overlaps(y) for x,y in zip(a.flat,b.flat))


def test_two_large_axes_lower_and_lift_against_exact_hessian():
    module=toy_action()
    a=np.arange(10).reshape(2,5)-3
    b=np.arange(8).reshape(2,4)-2
    values={1:a.reshape(2,5,1),2:b.reshape(2,1,4)}
    result=prescribed_action_jet(module,[2,3],[np.eye(2)],(5,4),values).d[3]
    expected=a.T@np.array([[214,72],[72,24]])@b
    assert np.shape(result)==(5,4)
    assert all(v.contains(int(e)) for v,e in zip(result.flat,expected.flat))


def test_curved_large_axis_is_not_replaced_by_constant_local_basis():
    module=toy_action()
    a=np.arange(10).reshape(2,5)-3; b=np.array([1,2])
    values={1:a.reshape(2,5,1),2:b.reshape(2,1,1),
            3:(a+2).reshape(2,5,1)}
    lowered=prescribed_action_jet(module,[2,3],[np.eye(2)],(5,1),values).d[3]
    plain=prescribed_action_jet(module,[2,3],[np.eye(2)],(5,1),values,
                                lower_local_axes=False).d[3]
    assert all(a.overlaps(b) for a,b in zip(lowered.flat,plain.flat))


def test_local_lifts_precede_the_global_inertia_reciprocal():
    module=toy_action(); module.POINTS=2
    maps=[np.eye(2),np.diag([2,3])]
    def integrand(state,node,directions,leg_values):
        local=module._array(module._mat(maps[node])*module._mat(state))[:,0]
        x,y=module._local_variables(local,directions,leg_values)
        return SimpleNamespace(bulk=x**5+3*x**2*y**2,inertia=1+x*x+y*y)
    module._integrand=integrand
    a=np.arange(10).reshape(2,5)-3; b=np.arange(8).reshape(2,4)-2
    values={1:a.reshape(2,5,1),2:b.reshape(2,1,4)}
    result=prescribed_action_jet(module,[2,3],maps,(5,4),values).d[3]
    x,y=sp.symbols('x y')
    action=33*x**5+111*x*x*y*y-sp.Rational(1,8)/(2+5*x*x+10*y*y)
    hessian=sp.hessian(action,(x,y)).subs({x:2,y:3})
    expected=sp.Matrix(a.tolist()).T*hessian*sp.Matrix(b.tolist())
    for i,j in np.ndindex(result.shape):
        numerator,denominator=expected[i,j].as_numer_denom()
        assert result[i,j].overlaps(arb(int(numerator))/arb(int(denominator)))

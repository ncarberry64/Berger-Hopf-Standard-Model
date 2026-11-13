"""Finite original-D5 radial solution arithmetic and chart safeguards."""
import numpy as np
import pytest

from bhsm.interface.muon_d5_complement_bulk_response import (
    nodal_derivative,_collocation_rule,_linear_collocation,_generator,
    _extension_cutoff,apply_fundamental_blocks,
)
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


def test_time_polynomial_derivative_keeps_every_nodal_time_contact():
    t=np.array([-1.,-.93,-.67,-.33,-.07,0.])*1e-5
    D=nodal_derivative(t)
    z=t/1e-5
    for k in range(6):
        expected=np.zeros_like(z) if k==0 else k*z**(k-1)/1e-5
        np.testing.assert_allclose(D@(z**k),expected,atol=2e-9,rtol=2e-13)
    assert np.linalg.norm(D)>1e6


def test_original_normal_generator_and_its_complete_source():
    rng=np.random.default_rng(41027);n,d=3,4
    R=np.broadcast_to(np.eye(d),(n,d,d)).copy()+rng.normal(size=(n,d,d))*.02
    T=rng.normal(size=R.shape)+1j*rng.normal(size=R.shape)
    K=rng.normal(size=R.shape)+1j*rng.normal(size=R.shape)
    Rx,Tx,Kx=(rng.normal(size=R.shape)*.03 for _ in range(3))
    D=nodal_derivative(np.array([-1.,-.4,0.]))
    G,Gx=_generator(T,R,K,Tx,Rx,Kx,D)
    V=rng.normal(size=(n*d,2))+1j*rng.normal(size=(n*d,2))
    Vr=(G@V).reshape(n,d,2);Vt=np.einsum('ij,jdk->idk',D,V.reshape(n,d,2))
    np.testing.assert_allclose(R@Vr+T@Vt+K@V.reshape(n,d,2),0,atol=3e-14)
    eps=1e-5
    gp=_generator(T+eps*Tx,R+eps*Rx,K+eps*Kx,Tx,Rx,Kx,D)[0]
    gm=_generator(T-eps*Tx,R-eps*Rx,K-eps*Kx,Tx,Rx,Kx,D)[0]
    np.testing.assert_allclose(Gx,(gp-gm)/(2*eps),atol=2e-10,rtol=2e-9)


def test_collocation_is_actual_bulk_solution_and_source_solve():
    nodes,polys,integral,A=_collocation_rule(3)
    G0=np.array([[.2,.1j],[.03,-.17]],complex)
    Gx=np.array([[.04,.02],[.01j,-.03]],complex)
    gs=np.array([G0+z*.01*np.eye(2) for z in nodes]);gxs=np.broadcast_to(Gx,gs.shape).copy()
    h=-.02;I=np.eye(2);zero=np.zeros((2,2))
    stage,sx,slope,slopex,r,rx=_linear_collocation(gs,gxs,I,zero,h,A)
    assert r<2e-15 and rx<2e-15
    for i,z in enumerate(nodes):
        Y=I+h*np.einsum('j,jab->ab',integral(z),slope)
        Yx=h*np.einsum('j,jab->ab',integral(z),slopex)
        Yr=np.einsum('j,jab->ab',[p(z) for p in polys],slope)
        Yrx=np.einsum('j,jab->ab',[p(z) for p in polys],slopex)
        np.testing.assert_allclose(Y,stage[i],atol=3e-15)
        np.testing.assert_allclose(Yr-gs[i]@Y,0,atol=3e-15)
        np.testing.assert_allclose(Yrx-gxs[i]@Y-gs[i]@Yx,0,atol=3e-15)
    assert np.linalg.norm(stage-I)>.001


def test_extension_is_a_computational_chart_with_wall_and_inner_plateaus():
    w=1e-4;r=WALL-w*np.array([0,.1,.3,.5,.7,.9,1])
    z,zr=_extension_cutoff(r,w)
    np.testing.assert_allclose(z[:2],1,atol=0)
    np.testing.assert_allclose(z[-2:],0,atol=0)
    np.testing.assert_allclose(zr[[0,1,-2,-1]],0,atol=0)
    assert np.max(abs(zr))>1e4


def test_complete_source_solve_with_noncommuting_stages_and_initial_source():
    _,_,_,A=_collocation_rule(3)
    rng=np.random.default_rng(9273)
    gs=(rng.normal(size=(3,3,3))+1j*rng.normal(size=(3,3,3)))*.2
    gxs=(rng.normal(size=(3,3,3))+1j*rng.normal(size=(3,3,3)))*.03
    initial=np.eye(3,dtype=complex)+rng.normal(size=(3,3))*.02
    initialx=rng.normal(size=(3,3))*.04
    out=_linear_collocation(gs,gxs,initial,initialx,-.07,A)
    eps=1e-5
    plus=_linear_collocation(gs+eps*gxs,gxs,initial+eps*initialx,initialx,-.07,A)
    minus=_linear_collocation(gs-eps*gxs,gxs,initial-eps*initialx,initialx,-.07,A)
    np.testing.assert_allclose(out[1],(plus[0]-minus[0])/(2*eps),atol=8e-11,rtol=2e-8)
    np.testing.assert_allclose(out[3],(plus[2]-minus[2])/(2*eps),atol=8e-11,rtol=2e-8)


def test_homogeneous_fields_are_accepted_without_state_or_family_projection():
    n=2;nr=2;k=3;size=n*64
    arrays=dict(times=np.array([-1.,0.]),time_derivative=nodal_derivative(np.array([-1.,0.])),radial_nodes=np.array([1.,.9]))
    for branch in ('particle','conjugate'):
        prefix='plus_'+branch+'_'
        arrays[prefix+'fundamental']=np.broadcast_to(np.eye(size),(nr,size,size)).copy()
        arrays[prefix+'fundamental_source']=np.zeros((nr,size,size))
        arrays[prefix+'fundamental_radial']=np.zeros((nr,size,size))
        arrays[prefix+'fundamental_radial_source']=np.zeros((nr,size,size))
    rng=np.random.default_rng(1227);wall=rng.normal(size=(n,384,k))+1j*rng.normal(size=(n,384,k))
    source=rng.normal(size=wall.shape)*.01
    out=apply_fundamental_blocks(arrays,'plus',wall,source)
    np.testing.assert_allclose(out['value'],np.broadcast_to(wall,(nr,n,384,k)))
    np.testing.assert_allclose(out['source'],np.broadcast_to(source,(nr,n,384,k)))
    assert np.linalg.norm(out['time'])>0
    with pytest.raises(ValueError):apply_fundamental_blocks(arrays,'plus',wall)
    with pytest.raises(ValueError):apply_fundamental_blocks(arrays,'plus',wall[:,:18])

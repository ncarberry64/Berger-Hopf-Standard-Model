"""CONTROL_ONLY literal-action third variations; no chosen physical state."""
import itertools
import numpy as np
import pytest
from bhsm.interface.muon_parent_maxwell_source_mean_forcing import maxwell_mean_cotangents,higgs_mean_cotangents
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_parent_maxwell_full_weak import M,_bracket
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_matched_mechanical_source import epsilon


@pytest.fixture(scope='module')
def angular():return retained_full_q_angular_space()


def _third(action):
    return sum(a*b*c*action(a,b,c) for a,b,c in itertools.product((-1.,1.),repeat=3))/8


def _maxwell_literal(A,At,Ar,angular,d):
    eps=epsilon();X=At[:,1]-Ar[:,0]+_bracket(A[:,0],A[:,1])
    T=At[:,2:]-angular[:,:,0]+_bracket(A[:,0,None],A[:,2:])
    R=Ar[:,2:]-angular[:,:,1]+_bracket(A[:,1,None],A[:,2:])
    B=2*A[:,2:].copy()
    for i,j,k in np.argwhere(eps):B[:,i]+=eps[i,j,k]*(angular[:,j,2+k]+.5*_bracket(A[:,2+j],A[:,2+k]))
    e,r,bmag,k,beta=d
    return .5*(k*np.sum(X*X,axis=1)+e*np.sum((T-beta*R)**2,axis=(1,2))-r*np.sum(R*R,axis=(1,2))-bmag*np.sum(B*B,axis=(1,2)))


@pytest.mark.parametrize('component,key',[(0,'value'),(6,'value'),(15,'value'),(8,'time'),(3,'radial')])
def test_mean_maxwell_rows_equal_independent_literal_cubic_coefficients(angular,component,key):
    rng=np.random.default_rng(714);V=angular['basis_values'];E=angular['derivative_matrices'];hw=angular['Haar_weights']
    A,At,Ar=rng.normal(size=(3,5,4))*.23
    u,ut,ur=rng.normal(size=(3,2,5,4,20))*.04;d=np.array([1.3,.9,.7,.4,.12])
    out=maxwell_mean_cotangents(A,At,Ar,u,ut,ur,E,d)
    values=np.einsum('ph,afch->apfc',V,u);times=np.einsum('ph,afch->apfc',V,ut);radial=np.einsum('ph,afch->apfc',V,ur)
    derivatives=np.einsum('pih,afch->apifc',angular['basis_derivative_values'],u)
    w=np.eye(20)[component].reshape(5,4)
    def action(s,t,b):
        base=A+s*values[0]+t*values[1]+(b*w if key=='value' else 0)
        tau=At+s*times[0]+t*times[1]+(b*w if key=='time' else 0)
        rho=Ar+s*radial[0]+t*radial[1]+(b*w if key=='radial' else 0)
        return hw@_maxwell_literal(base,tau,rho,s*derivatives[0]+t*derivatives[1],d)
    assert out[key][component,0,1]==pytest.approx(_third(action),rel=2e-12,abs=3e-14)
    assert np.max(abs(out[key]-out[key].swapaxes(-1,-2)))<3e-15
    np.testing.assert_array_equal(out['time'][:4],0)  # no partial_t At in F


def test_mechanical_lambda_cotangent_is_actual_paired_hessian_derivative(angular):
    rng=np.random.default_rng(73);A,At,Ar=rng.normal(size=(3,5,4))*.2
    u,ut,ur=rng.normal(size=(3,2,5,4,20))*.03;E=angular['derivative_matrices'];d=np.array([1.,.8,.6,.5,.1])
    base=maxwell_mean_cotangents(A,At,Ar,u,ut,ur,E,d)
    for j in range(3):
        def value(t):
            fields=[x.copy() for x in (A,At,Ar)];fields[j][2:]+=t*M
            return maxwell_mean_cotangents(*fields,u,ut,ur,E,d)['paired_hessian']
        step=.001
        np.testing.assert_allclose((value(step)-value(-step))/(2*step),base['mechanical_lambda_cotangents'][j],rtol=3e-12,atol=3e-13)


@pytest.mark.parametrize('target,component',[('H',1),('Ht',2),('gauge',0),('gauge',14)])
def test_intrinsic_real_scalar_and_gauss_rows_match_literal_action(angular,target,component):
    rng=np.random.default_rng(933);V=angular['basis_values'];EV=angular['basis_derivative_values'];E=angular['derivative_matrices'];hw=angular['Haar_weights']
    H=np.array([.2,.8,-.1,.05]);Ht=np.array([.1,-.07,.02,.01]);A=rng.normal(size=(5,4))*.1
    h,ht=rng.normal(size=(2,2,4,20))*.025;a=rng.normal(size=(2,5,4,20))*.035
    weights=np.array([1.1,.7,.9]);lam=.17;nu=4.
    out=higgs_mean_cotangents(H,Ht,A,h,ht,a,E,weights,lambda_H=lam,nu_squared_action=nu)
    hv=np.einsum('pn,acn->apc',V,h);tv=np.einsum('pn,acn->apc',V,ht);ev=np.einsum('pin,acn->apic',EV,h);av=np.einsum('pn,afcn->apfc',V,a)
    G=higgs_u2_real_representation()['real_generators'];wH=np.eye(4)[component] if target in ('H','Ht') else np.zeros(4)
    wA=np.eye(20)[component].reshape(5,4) if target=='gauge' else np.zeros((5,4))
    def action(s,t,b):
        v=H+s*hv[0]+t*hv[1]+(b*wH if target=='H' else 0)
        vt=Ht+s*tv[0]+t*tv[1]+(b*wH if target=='Ht' else 0)
        connection=A+s*av[0]+t*av[1]+b*wA
        O=np.einsum('pfc,cij->pfij',connection[:,[0,2,3,4]],G)
        cov=np.einsum('pfij,pj->pfi',O,v);cov[:,0]+=vt;cov[:,1:]+=s*ev[0]+t*ev[1]
        density=weights[0]*np.sum(cov[:,0]**2,axis=1)-weights[1]*np.sum(cov[:,1:]**2,axis=(1,2))-weights[2]*lam*(np.sum(v*v,axis=1)-nu)**2
        return 2*np.pi**2*(hw@density)
    key={'H':'scalar_value','Ht':'scalar_time','gauge':'gauge_value'}[target]
    assert out[key][component,0,1]==pytest.approx(_third(action),rel=3e-11,abs=2e-13)
    assert np.linalg.norm(out['gauge_value'][:4])>0  # charged matter Gauss load
    np.testing.assert_array_equal(out['gauge_value'][4:8],0)  # material Ar is absent
    assert out['material_At_advection_count']==1


def test_unknown_nu_or_complex_response_cannot_be_zero_filled(angular):
    args=(np.ones(4),np.zeros(4),np.zeros((5,4)),np.zeros((2,4,20)),np.zeros((2,4,20)),np.zeros((2,5,4,20)),angular['derivative_matrices'],np.ones(3))
    with pytest.raises(ValueError,match='explicit positive'):
        higgs_mean_cotangents(*args,lambda_H=.1,nu_squared_action=None)
    bad=list(args);bad[3]=bad[3].astype(complex)+1j
    with pytest.raises(ValueError,match='explicit real'):
        higgs_mean_cotangents(*bad,lambda_H=.1,nu_squared_action=4.)

"""CONTROL_ONLY independent polynomial and moving-source chain checks."""
import itertools
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_current_source_motion_cubic import (
    current_face_source_jets,maxwell_cross_hessian,higgs_cross_hessian,
)
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_parent_maxwell_full_weak import _bracket
from bhsm.interface.muon_matched_mechanical_source import epsilon
from bhsm.interface.muon_moving_geometric_action import retained_state


@pytest.fixture(scope='module')
def angular():return retained_full_q_angular_space()


def _mixed_second(action,step):
    return sum(s*t*action(step*s,step*t) for s,t in itertools.product((-1.,1.),repeat=2))/(4*step**2)


def _polynomial_second(action):
    return (4*_mixed_second(action,.5)-_mixed_second(action,1.))/3


def _maxwell(A,At,Ar,angular,d):
    eps=epsilon();X=At[:,1]-Ar[:,0]+_bracket(A[:,0],A[:,1])
    T=At[:,2:]-angular[:,:,0]+_bracket(A[:,0,None],A[:,2:])
    R=Ar[:,2:]-angular[:,:,1]+_bracket(A[:,1,None],A[:,2:])
    B=2*A[:,2:].copy()
    for i,j,k in np.argwhere(eps):B[:,i]+=eps[i,j,k]*(angular[:,j,2+k]+.5*_bracket(A[:,2+j],A[:,2+k]))
    e,r,b,k,shift=d
    return .5*(k*np.sum(X*X,axis=1)+e*np.sum((T-shift*R)**2,axis=(1,2))-r*np.sum(R*R,axis=(1,2))-b*np.sum(B*B,axis=(1,2)))


def test_cross_maxwell_hessian_includes_background_curvature_contact(angular):
    rng=np.random.default_rng(812);A,At,Ar=rng.normal(size=(3,5,4))*.2
    U,Ut,Ur=rng.normal(size=(3,2,5,4,20))*.04
    V,Vt,Vr=rng.normal(size=(3,2,5,4,20))*.03
    E=angular['derivative_matrices'];d=np.array([1.3,.9,.7,.4,.12]);B=angular['basis_values'];EV=angular['basis_derivative_values']
    values=np.einsum('ph,afch->apfc',B,np.concatenate((U[:1],V[1:])))
    times=np.einsum('ph,afch->apfc',B,np.concatenate((Ut[:1],Vt[1:])))
    radial=np.einsum('ph,afch->apfc',B,np.concatenate((Ur[:1],Vr[1:])))
    grad=np.einsum('pih,afch->apifc',EV,np.concatenate((U[:1],V[1:])))
    action=lambda s,t:angular['Haar_weights']@_maxwell(A+s*values[0]+t*values[1],At+s*times[0]+t*times[1],Ar+s*radial[0]+t*radial[1],s*grad[0]+t*grad[1],d)
    actual=maxwell_cross_hessian(A,At,Ar,U,Ut,Ur,V,Vt,Vr,E,d)[0,1]
    assert actual==pytest.approx(_polynomial_second(action),rel=2e-11,abs=3e-13)


def test_cross_higgs_hessian_retains_gauge_scalar_and_potential_contacts(angular):
    rng=np.random.default_rng(811);H=np.array([.2,.8,-.1,.05]);Ht=np.array([.1,-.07,.02,.01]);A=rng.normal(size=(5,4))*.1
    h,ht,k,kt=rng.normal(size=(4,2,4,20))*.025;a,b=rng.normal(size=(2,2,5,4,20))*.035
    weights=np.array([1.1,.7,.9]);lam=.17;nu=4.;V=angular['basis_values'];EV=angular['basis_derivative_values'];G=higgs_u2_real_representation()['real_generators']
    hv=np.einsum('pn,acn->apc',V,np.concatenate((h[:1],k[1:])))
    tv=np.einsum('pn,acn->apc',V,np.concatenate((ht[:1],kt[1:])))
    ev=np.einsum('pin,acn->apic',EV,np.concatenate((h[:1],k[1:])))
    av=np.einsum('pn,afcn->apfc',V,np.concatenate((a[:1],b[1:])))
    def action(s,t):
        v=H+s*hv[0]+t*hv[1];vt=Ht+s*tv[0]+t*tv[1];connection=A+s*av[0]+t*av[1]
        O=np.einsum('pfc,cij->pfij',connection[:,[0,2,3,4]],G)
        cov=np.einsum('pfij,pj->pfi',O,v);cov[:,0]+=vt;cov[:,1:]+=s*ev[0]+t*ev[1]
        density=weights[0]*np.sum(cov[:,0]**2,axis=1)-weights[1]*np.sum(cov[:,1:]**2,axis=(1,2))-weights[2]*lam*(np.sum(v*v,axis=1)-nu)**2
        return 2*np.pi**2*(angular['Haar_weights']@density)
    actual=higgs_cross_hessian(H,Ht,A,h,ht,a,k,kt,b,angular['derivative_matrices'],weights,lambda_H=lam,nu_squared_action=nu)[0,1]
    assert actual==pytest.approx(_polynomial_second(action),rel=3e-10,abs=2e-12)


@pytest.mark.parametrize('index',[0,37,98,99])
def test_normalization_and_rate_jets_match_same_geometry_finite_difference(index):
    q,v,m=retained_state(Path(__file__).resolve().parents[1]);raw=np.r_[q,v,m,.0001,.0002]
    base=current_face_source_jets(raw);direction=np.eye(100)[index];step=1e-5
    plus=current_face_source_jets(raw+step*direction);minus=current_face_source_jets(raw-step*direction)
    for name in ('T_b','T_b_dot'):
        fd=(plus[name].value-minus[name].value)/(2*step)
        assert fd==pytest.approx(base[name].gradient[index],rel=3e-7,abs=3e-10)
    assert 2*np.pi**2*base['intrinsic_weights']['R4'].value*base['T_b'].value**2==pytest.approx(1,abs=3e-16)


def test_source_motion_is_both_ordered_hessian_terms(angular):
    q,v,m=retained_state(Path(__file__).resolve().parents[1]);raw=np.r_[q,v,m,.0001,.0002];chart=current_face_source_jets(raw)
    rng=np.random.default_rng(281);A,At,Ar=rng.normal(size=(3,5,4))*.1
    B=angular['source_coefficients'].T.reshape(8,5,4,20)[:2];E=angular['derivative_matrices'];d=np.array([1.,.8,.6,.5,.1]);p=.7;pt=-20.
    def fields(c):return (c['T_b'].value*p*B,(c['T_b_dot'].value*p+c['T_b'].value*pt)*B,c['T_b'].value*p*.6*B)
    u,ut,ur=fields(chart);z=np.zeros_like(B)
    c0=maxwell_cross_hessian(A,At,Ar,u,ut,ur,p*B,pt*B,.6*p*B,E,d)
    c1=maxwell_cross_hessian(A,At,Ar,u,ut,ur,z,p*B,z,E,d)
    index=37;actual=chart['T_b'].gradient[index]*(c0+c0.T)+chart['T_b_dot'].gradient[index]*(c1+c1.T)
    step=1e-5;direction=np.eye(100)[index]
    def value(t):
        f=fields(current_face_source_jets(raw+t*direction))
        return maxwell_cross_hessian(A,At,Ar,*f,*f,E,d)
    np.testing.assert_allclose((value(step)-value(-step))/(2*step),actual,rtol=5e-7,atol=1e-9)
    assert np.linalg.norm(actual)>0


def test_missing_or_complex_geometry_cannot_define_source_normalization():
    with pytest.raises(ValueError,match='explicit real'):current_face_source_jets(None)
    with pytest.raises(ValueError,match='explicit real'):current_face_source_jets(np.ones(100,dtype=complex))


def test_complete_geometry_cubic_matches_derivative_of_the_moving_paired_action(angular):
    from bhsm.interface.muon_current_source_motion_cubic import prescribed_source_cubic_application
    from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation
    from bhsm.interface.muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
    from bhsm.interface.muon_parent_maxwell_full_weak import M,FIELD_ORDER
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP,VOLUME
    from bhsm.interface.muon_parent_retarded_hypercharge import regular_radial_basis,WALL
    q,v,m=retained_state(Path(__file__).resolve().parents[1]);rng=np.random.default_rng(508)
    raw=np.r_[q,v,m,.0001,.0002,rng.normal(size=120)*.02,[.2,.8,-.1,.05],[.1,-.07,.02,.01]]
    rep=correction_representation(radial_points=6,cap_points=6,radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    b=angular['source_coefficients'][:,:2];B=b.T.reshape(2,5,4,20);E=angular['derivative_matrices'];p=.8;pt=-3.
    base=prescribed_source_cubic_application(raw,rep,angular,b,p,pt,nu_squared_action=4.)
    rv,rd=regular_radial_basis(rep['rho'],2);wb,_=regular_radial_basis(np.array([WALL]),2)
    def paired(r):
        chart=current_face_source_jets(r[:100]);T,Td=chart['T_b'].value,chart['T_b_dot'].value;w=chart['intrinsic_weights']
        geo=geometric_connection_coefficient_jets(12,r[:37],r[37:74],r[74:98],rep['rho'],source_value=r[98],source_rate=r[99])
        A=np.einsum('rj...,j->r...',rep['gauge_basis'],r[100:160])[:,0]
        At=np.einsum('rj...,j->r...',rep['gauge_basis'],r[160:220])[:,0]
        Ar=np.einsum('rj...,j->r...',rep['gauge_radial_basis'],r[100:160])[:,0]
        result=np.zeros((2,2))
        for j,row in enumerate(geo['rows']):
            A[j,2:]+=M*(row['connection_lambda'].value-1);At[j,2:]+=M*row['lambda_tau'].value;Ar[j,2:]+=M*row['lambda_rho'].value
            f=(rv[j,-1]*T*p*B,rv[j,-1]*(Td*p+T*pt)*B,rd[j,-1]*T*p*B)
            d=np.array([row[k].value for k in ('electric','radial','angular','electric_radial','shift')])
            result+=MAXWELL_TO_CAP*rep['radial_quadrature'][j]*maxwell_cross_hessian(A[j],At[j],Ar[j],*f,*f,E,d)
        wall=np.zeros((5,4))
        for j,label in enumerate(rep['gauge_labels']):wall[FIELD_ORDER.index(label['field']),label['internal']]+=wb[0,label['radial']]*r[100+j]
        wall[2:]+=M*(w['mechanical_connection_lambda'].value-1);z=np.zeros((2,4,20));a=T*p*B
        result+=higgs_cross_hessian(r[220:224],r[224:228],wall,z,z,a,z,z,a,E,np.array([w[k].value for k in ('wT','wS','wV')]),lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=4.)/VOLUME**2
        return result
    for index in (0,37,98,99):
        step=2e-6;direction=np.eye(228)[index]
        fd=(paired(raw+step*direction)-paired(raw-step*direction))/(2*step)
        np.testing.assert_allclose(fd,base['complete_geometry_cubic_at_fixed_interior_first_coefficients'][index],rtol=2e-6,atol=2e-8)
    assert np.linalg.norm(base['moving_source_geometry_cubic'])>0

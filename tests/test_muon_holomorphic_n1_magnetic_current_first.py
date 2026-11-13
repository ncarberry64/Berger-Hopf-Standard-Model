import numpy as np
from bhsm.interface.muon_holomorphic_n1_magnetic_action import (
    _mixed_H_selected_EM_source,magnetic_unsquared_unit_em_current,original_signed_stage,
)
from bhsm.interface.muon_holomorphic_em_current import holomorphic_unit_em_moments
from test_muon_holomorphic_n1_magnetic_action import fixture


def test_independent_analytic_H_charge_Hessian_and_lapse_product():
    rng=np.random.default_rng(672);draw=lambda s:.03*(rng.normal(size=s)+1j*rng.normal(size=s))
    h=np.array([1.1+.02j,.4-.03j,.08+.01j,-.05+.02j]);dh=draw((4,2));hb=draw((4,12));dhb=draw((2,4,12))
    N=.9+.02j;dN=np.array([.07-.02j,-.03+.01j]);a=_mixed_H_selected_EM_source(h,dh,hb,dhb,N=N,N_first=dN)
    step=2e-5
    for k in range(2):
        values=[holomorphic_unit_em_moments(h+t*dh[:,k],hb+t*dhb[k],N+t*dN[k],np.zeros(12))['literal_right_first']for t in(step,-step)]
        np.testing.assert_allclose(a[k],(values[0]-values[1])/(2*step),rtol=4e-8,atol=4e-12)
    assert np.linalg.norm(a)>.001


def test_full_current_mixed_first_includes_both_endpoints_and_three_slots():
    x,dx,p,dp,refs,dr,rep=fixture()
    binder=lambda a,d,pp,dpp,rr,drr:original_signed_stage(a,d,pp,dpp,rr,drr,rep,side='child',lambda_H=.129,nu_squared_action=4.)
    b=binder(x,dx,p,dp,refs,dr);rng=np.random.default_rng(982)
    field=.02*(rng.normal(size=(336,3))+1j*rng.normal(size=(336,3)))
    df=.01*(rng.normal(size=(2,336,3))+1j*rng.normal(size=(2,336,3)))
    steps=np.array([.004,.004]);z,w=np.polynomial.legendre.leggauss(6)
    points=[dict(cell=j,sigma=(j+(t+1)/2)/2,scale=-1j*steps[j]*wt/2,total_field=field,total_field_first=df)
        for j in range(2)for t,wt in zip(z,w)]
    actual=magnetic_unsquared_unit_em_current([b,b],steps,dict(point_sources=points))
    step=2e-5
    values=[]
    for t in(step,-step):
        moved=binder(x+t*dx[:,0],dx,p+t*dp[:,0],dp,refs+t*dr[:,:,0],dr)
        source=[{k:v for k,v in r.items()if k!='total_field_first'}|dict(total_field=field+t*df[0])for r in points]
        values.append(magnetic_unsquared_unit_em_current([moved,moved],steps,dict(point_sources=source)))
    for key in('operator_insertion','right_current_motion','literal_left_motion','total'):
        expected=(values[0][key]-values[1][key])/(2*step)
        np.testing.assert_allclose(actual[key+'_first'][0],expected,rtol=3e-7,atol=3e-12)
    np.testing.assert_allclose(actual['total_first'],sum(actual[n+'_first']for n in('operator_insertion','right_current_motion','literal_left_motion')),atol=1e-18)

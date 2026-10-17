"""Independent mixed charge/source and complete current controls."""
import numpy as np
from bhsm.interface.muon_holomorphic_em_current import holomorphic_unit_em_moments
from bhsm.interface.muon_holomorphic_magnetic_current_source_jet import (
    mixed_higgs_current, mixed_magnetic_unsquared_current,
)
from bhsm.interface.muon_holomorphic_n1_magnetic_action import magnetic_unsquared_unit_em_current


def test_mixed_charge_hessian_against_actual_nonlinear_current():
    rng=np.random.default_rng(9321)
    draw=lambda shape: .13*(rng.normal(size=shape)+.3j*rng.normal(size=shape))
    h=np.array([1.1,.31,.15,-.21],complex)+1j*draw((4,))
    dh,hb,dhb=draw((4,2)),draw((4,12)),draw((2,4,12))
    N,dN=.91+.04j,draw((2,))
    actual=mixed_higgs_current(h,dh,hb,dhb,N,dN)
    for a in range(2):
        step=2e-5
        def source(e):
            return holomorphic_unit_em_moments(h+e*dh[:,a],hb+e*dhb[a],N+e*dN[a],np.zeros(12))['literal_right_first']
        fd=(source(step)-source(-step))/(2*step)
        np.testing.assert_allclose(actual['right_first'][a],fd,rtol=1e-8,atol=2e-11)
    np.testing.assert_array_equal(actual['left_first'],actual['right_first'].swapaxes(-1,-2))
    assert np.linalg.norm(actual['right_first'].imag)>.01


def test_two_independent_mixed_current_assemblies_and_nonlinear_variation():
    rng=np.random.default_rng(9322)
    draw=lambda shape: .06*(rng.normal(size=shape)+.4j*rng.normal(size=shape))
    bindings=[]
    W=np.zeros((20,84));W[:,:20]=np.eye(20)
    hv=np.zeros((4,84));hv[:,80:]=np.eye(4)
    for j in range(2):
        H,dh=np.array([1.1,.21,.12,-.14],complex)+draw((4,)),draw((4,2))
        stage=dict(R4=np.array(1.2+.02j+.04*j),induced_lapse=np.array(.94-.03j),
            R4_first=draw((2,)),induced_lapse_first=draw((2,)),
            Hcan=draw((18,18)),Hcan_first=draw((2,18,18)),
            canonical_wall_current_vertices=draw((24,18,18)),
            canonical_wall_current_vertices_first=draw((2,24,18,18)))
        bindings.append(dict(stage=stage,row=dict(H=H),row_first=dict(H=dh.T),lifts=dict(W=W,hv=hv)))
    z,w=np.polynomial.legendre.leggauss(3);steps=np.array([.019,.021]);points=[]
    for j in range(2):
        for q,weight in zip(z,w):
            points.append(dict(cell=j,sigma=(j+(q+1)/2)/2,scale=-1j*steps[j]*weight/2,
                total_field=draw((336,3)),total_field_first=draw((2,336,3))))
    response=dict(point_sources=points)
    actual=magnetic_unsquared_unit_em_current(bindings,steps,response)
    independent=mixed_magnetic_unsquared_current(bindings,steps,response)
    names=('operator_insertion','right_current_motion','literal_left_motion','total')
    for name in names:
        np.testing.assert_allclose(actual[name],independent[name],rtol=3e-13,atol=2e-18)
        np.testing.assert_allclose(actual[name+'_first'],independent[name+'_first'],rtol=3e-13,atol=2e-18)
    def moved(a,e):
        bb=[]
        for b in bindings:
            s=b['stage'];sc={**s}
            for key in ('R4','induced_lapse','Hcan','canonical_wall_current_vertices'):
                sc[key]=s[key]+e*s[key+'_first'][a]
            bb.append({**b,'stage':sc,'row':dict(H=b['row']['H']+e*b['row_first']['H'][a])})
        pp=[{k:v for k,v in p.items()if k!='total_field_first'}|dict(total_field=p['total_field']+e*p['total_field_first'][a]) for p in points]
        return magnetic_unsquared_unit_em_current(bb,steps,dict(point_sources=pp))
    for a in range(2):
        step=2e-5;plus,minus=moved(a,step),moved(a,-step)
        for name in names:
            np.testing.assert_allclose(actual[name+'_first'][a],(plus[name]-minus[name])/(2*step),rtol=8e-8,atol=3e-14)
    assert np.linalg.norm(actual['operator_insertion_first'])>1e-7
    assert np.linalg.norm(actual['right_current_motion_first'])>1e-7
    assert np.linalg.norm(actual['literal_left_motion_first'])>1e-7

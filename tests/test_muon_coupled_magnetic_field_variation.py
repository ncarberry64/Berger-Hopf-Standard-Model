import numpy as np
import pytest
from bhsm.interface.muon_coupled_magnetic_field_variation import corrected_magnetic_first_field_interpolation
from bhsm.interface.muon_parent_retarded_hypercharge import regular_radial_basis


def arrays():
    t=np.array([0.,.25,.5,.75,1.]);state=np.zeros((5,800,8));velocity=np.zeros((5,400,8))
    state[:,0,0]=t*t;velocity[:,0,0]=2*t
    state[:,320,0]=3*t*t;velocity[:,320,0]=6*t
    at=np.zeros((5,80,8));at[:,0,0]=4*t*t
    q=np.zeros((5,400,8));qt=q.copy();q[:,160,0]=5*t*t;qt[:,160,0]=10*t
    return ({},{'times':t,'state':state},{'times':t,'velocity':velocity},
        {'times':t,'A_tau':at,'source_trace':q,'source_trace_rate':qt})


def test_saved_future_rates_bind_both_chronological_arms_without_a_sign_flip():
    args=arrays();sample=corrected_magnetic_first_field_interpolation(*args)
    rho=np.array([.4,.7]);r=sample(.3,rho);f,fr=regular_radial_basis(rho,1)
    np.testing.assert_allclose(r['gauge'][:,0,1,0,0],f[:,0]*.09)
    np.testing.assert_allclose(r['gauge_time'][:,0,1,0,0],f[:,0]*.6)
    np.testing.assert_allclose(r['gauge'][:,0,0,0,0],f[:,0]*.36)
    np.testing.assert_allclose(r['gauge_time'][:,0,0,0,0],f[:,0]*2.4)
    np.testing.assert_allclose(r['gauge_radial'][:,0,2,0,0],fr[:,1]*.45)
    assert r['H'][0,0,0]==pytest.approx(.27)
    assert r['Hdot'][0,0,0]==pytest.approx(1.8)
    assert r['wall_gauge'][0,2,0,0]==pytest.approx(.45)


def test_arbitrarily_small_nonzero_n3_rate_requires_the_n6_image():
    p,s,v,c=arrays();v['velocity'][2,324,0]=1e-200
    with pytest.raises(ValueError,match='n3'):corrected_magnetic_first_field_interpolation(p,s,v,c)


def test_contact_clock_must_be_the_same_saved_future_grid():
    p,s,v,c=arrays();c['times']=c['times']+.01
    with pytest.raises(ValueError,match='SAME'):corrected_magnetic_first_field_interpolation(p,s,v,c)

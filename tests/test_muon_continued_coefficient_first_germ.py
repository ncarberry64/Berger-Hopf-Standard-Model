import numpy as np
from numpy.testing import assert_allclose

from bhsm.interface.muon_continued_coefficient_first_germ import geometry_first_germ
from bhsm.interface.muon_continued_action_reality import _geometry


def test_complex_coframe_first_germ_matches_independent_centered_values():
    rng=np.random.default_rng(2271)
    raw=np.zeros(108,dtype=complex)
    raw[:37]=rng.normal(size=37)*.003
    raw[37:74]=rng.normal(size=37)*.0002
    raw[74:98]=rng.normal(size=24)*.002
    raw[98:100]=(.006,.0001)
    raw+=1j*rng.normal(size=len(raw))*1e-6
    dx=(rng.normal(size=len(raw))+1j*rng.normal(size=len(raw)))*.001
    app=geometry_first_germ(raw,dx)
    expected=_geometry(raw)
    for key,value in expected.items():assert_allclose(app['value'][key],value,rtol=5e-15,atol=4e-15)
    h=.002
    plus=_geometry(raw+h*dx);minus=_geometry(raw-h*dx)
    halfplus=_geometry(raw+h/2*dx);halfminus=_geometry(raw-h/2*dx)
    for key,derivative in app['first'].items():
        # Richardson applies only to this independent value comparison;
        # the production derivative is analytic and has no finite step.
        fd=((halfplus[key]-halfminus[key])/(h)-
            (plus[key]-minus[key])/(8*h))*4/3
        assert_allclose(derivative,fd,rtol=5e-7,atol=1e-10)

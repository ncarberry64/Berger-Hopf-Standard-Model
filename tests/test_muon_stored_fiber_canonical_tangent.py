"""Independent original midpoint, endpoint and Ward-batch controls."""
import numpy as np
from numpy.testing import assert_allclose
from bhsm.interface.muon_stored_fiber_canonical_tangent import (
    exact_fiber_ward_lift,stored_original_canonical_tangent,stored_endpoint_constitutive_tangent,
)


def test_full_complex_batch_midpoint_and_true_endpoint_against_original_dense_equations():
    rng=np.random.default_rng(628)
    draw=lambda s:rng.normal(size=s)+.2j*rng.normal(size=s)
    n,m,b=2,1,3;A=draw((2*n+m,2*n+m));H=A+A.T+4*np.eye(2*n+m)
    F=np.array([[.3,.1,1.]],complex);h=.03+.02j;c=draw((2*n,b))
    out=stored_original_canonical_tangent(H,h,F,c,np.zeros_like(c))
    # Independently differentiate x'=v, p'=Lx, Lv=mean(p), Ly=0.
    def equation(z):
        xf,pf,v,y=np.split(z,[n,2*n,3*n]);eta=np.vstack(((c[:n]+xf)/2,v,y))
        cot=H@eta
        return np.vstack((xf-c[:n]-h*v,pf-c[n:]-h*cot[:n],cot[n:2*n]-(c[n:]+pf)/2,cot[2*n:]))
    z=out['solution_high'][:3*n+m]+out['solution_low'][:3*n+m]
    rows=equation(z);reaction=out['reaction_rows']
    assert_allclose(rows,-reaction,atol=5e-15)
    assert_allclose(F@z[2*n:],0,atol=5e-15)
    assert out['framed_rows_upper']<1e-25
    assert out['assembly_difference_upper']<1e-25
    assert out['literal_pairing_difference_upper']<1e-25
    assert np.linalg.norm(reaction)>.01  # framed success is not original admission
    end=stored_endpoint_constitutive_tangent(H,F,out['canonical_final_high'],out['canonical_final_low'])
    eta=end['direction_high']+end['direction_low'];p=out['canonical_final_high'][n:]+out['canonical_final_low'][n:]
    original=H[n:]@eta-np.vstack((p,np.zeros((m,b))))
    assert_allclose(original,-end['reaction_rows'],atol=5e-15)
    assert end['framed_rows_upper']<1e-25
    assert_allclose(eta[:n],out['canonical_final_high'][:n]+out['canonical_final_low'][:n],atol=0)


def test_literal_Ward_repair_preserves_free_canonical_coordinates_and_both_terms():
    rng=np.random.default_rng(238);n=4
    E=rng.normal(size=(2*n,6))+1j*.2*rng.normal(size=(2*n,6));N=rng.normal(size=(6,5))
    C=np.array([[1,.2j,.3,.4],[.1,.9,.2j,.3]],complex);A=rng.normal(size=(2,n))*.1
    out=exact_fiber_ward_lift(E,N,C,A,[0,1]);z=out['canonical_direction_high']+out['canonical_direction_low']
    assert_allclose(C@z[n:]+A@z[:n],0,atol=1e-15)
    assert out['ward_after_upper']<1e-25
    assert_allclose(z[:n],E[:n]@N,atol=8e-16)
    assert_allclose(z[n+2:],E[n+2:]@N,atol=8e-16)
    assert np.linalg.norm(out['canonical_direction_low'])>0

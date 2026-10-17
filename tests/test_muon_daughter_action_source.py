"""Independent moving-current and supplied-domain daughter-source checks."""
import numpy as np
import pytest

from bhsm.interface.muon_daughter_action_source import (
    daughter_tensor, daughter_tensor_first, quotient_trace_return_first,
    owned_daughter_vertices_first, daughter_bilinear_sources,
)
from bhsm.interface.muon_owned_static_charged_current import owned_static_charged_current


def five_point(f, h):
    return (-f(2*h)+8*f(h)-8*f(-h)+f(-2*h))/(12*h)


def test_moving_H_metric_vertices_match_literal_owned_action_and_source_amplitude():
    H=np.array([.2+.1j,.7-.15j]);dH=np.array([-.07+.03j,.02+.04j])
    R,N=.93,.71;dR,dN=.17,-.11
    rng=np.random.default_rng(708);G=rng.normal(size=(24,24))*.03
    a=owned_daughter_vertices_first(H,radius=R,lapse=N,H_first=dH,
                                    radius_first=dR,lapse_first=dN)
    C=daughter_tensor(a['right'],G,a['left'])
    direct=lambda t:owned_static_charged_current(G,H+t*dH,radius=R+t*dR,lapse=N+t*dN)['full_charged_current_tensor']
    np.testing.assert_allclose(C,direct(0),atol=4e-17,rtol=0)
    jet=daughter_tensor_first(a['right'],G,a['left'],a['right_first'],np.zeros_like(G),a['left_first'])
    np.testing.assert_allclose(jet,five_point(direct,.001),atol=2e-10,rtol=0)
    spin=[rng.normal(size=n)+1j*rng.normal(size=n) for n in (4,2,4,2)]
    j=daughter_bilinear_sources(a['right'],a['left'],muon=spin[0],neutrino=spin[1],electron=spin[2],antineutrino=spin[3])
    literal=np.einsum('a,b,abcd,c,d->',spin[1].conj(),spin[0],C,spin[2].conj(),spin[3])
    np.testing.assert_allclose(j['muon_neutrino']@G@j['electron_antineutrino'],literal,atol=1e-15,rtol=1e-14)


def test_quotient_trace_jet_retains_all_moving_maps_and_basis_covariance():
    rng=np.random.default_rng(41);k=np.diag(np.arange(1,7.))+rng.normal(size=(6,6))*.03
    q=rng.normal(size=(6,4));t=rng.normal(size=(3,6))
    dk=rng.normal(size=(6,6))*.07;dq=rng.normal(size=(6,4))*.1;dt=rng.normal(size=(3,6))*.05
    a=quotient_trace_return_first(k,q,t,dk,dq,dt)
    def literal(x):
        Q=q+x*dq;T=t+x*dt;K=k+x*dk
        return T@Q@np.linalg.solve(Q.T@K@Q,Q.T@T.T)
    np.testing.assert_allclose(a['returned_first'],five_point(literal,.001),atol=2e-10,rtol=0)
    b=rng.normal(size=(4,4))*.1
    frame=quotient_trace_return_first(k,q,t,np.zeros_like(k),q@b,np.zeros_like(t))
    np.testing.assert_allclose(frame['returned_first'],0,atol=2e-13,rtol=0)
    # Deleting either of the two moving contacts changes the actual result.
    missing=quotient_trace_return_first(k,q,t,dk,np.zeros_like(q),np.zeros_like(t))
    assert np.linalg.norm(a['returned_first']-missing['returned_first'])>1e-4


@pytest.mark.parametrize('which',[0,1])
def test_open_source_rejects_nonfinite_vertices(which):
    r=np.zeros((2,2,4));l=np.zeros((2,4,2));[r,l][which].flat[0]=np.nan
    with pytest.raises(ValueError):
        daughter_bilinear_sources(r,l,muon=np.ones(4),neutrino=np.ones(2),electron=np.ones(4),antineutrino=np.ones(2))

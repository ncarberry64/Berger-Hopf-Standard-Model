import numpy as np
from bhsm.interface.muon_chronological_current_energy import (
    literal_point_energy_sources,chronological_energy_transfer_chunk,
    clock_origin_energy_contacts)


def test_complete_nonsymmetric_current_energy_matches_two_analytic_source_legs():
    rng=np.random.default_rng(3261)
    K=rng.normal(size=(9,9))+1j*rng.normal(size=(9,9))+12*np.eye(9)
    R=rng.normal(size=(9,5))+1j*rng.normal(size=(9,5))
    L=rng.normal(size=(9,5))+1j*rng.normal(size=(9,5))
    tau=np.linspace(0,.7,9)+.1j*np.arange(9)
    u=np.linalg.solve(K,R);p=np.linalg.solve(K.T,L)
    a=chronological_energy_transfer_chunk(*(x.reshape(3,3,5) for x in
        (L,R,u,p,tau[:,None]*L,-tau[:,None]*R)))
    e=2e-5
    def transfer(E):
        return (np.exp(E*tau)[:,None]*L).T@np.linalg.solve(K,np.exp(-E*tau)[:,None]*R)
    fd=(transfer(e)-transfer(-e))/(2*e)
    np.testing.assert_allclose(a['continued_energy_first'],fd,atol=3e-9,rtol=3e-9)
    np.testing.assert_allclose(a['source_transfer'],a['independent_transpose_transfer'],atol=2e-15)
    # A Hilbert dual would give a different energy/current form here.
    assert np.linalg.norm(a['source_transfer']-L.conj().T@u)>.1


def test_same_clock_shift_cancels_without_source_or_band_deletion():
    rng=np.random.default_rng(98)
    K=rng.normal(size=(6,6))+9*np.eye(6)
    L=rng.normal(size=(6,4))+1j*rng.normal(size=(6,4))
    R=rng.normal(size=(6,4))+1j*rng.normal(size=(6,4))
    tau=.31+.2j
    s=literal_point_energy_sources(dict(literal_right_source=R,
        literal_left_transpose_source=L),tau)
    a=chronological_energy_transfer_chunk(*(x.reshape(2,3,4) for x in
        (L,R,np.linalg.solve(K,R),np.linalg.solve(K.T,L),
         s['literal_left_energy_source'],s['literal_right_energy_source'])))
    np.testing.assert_allclose(a['continued_energy_first'],0,atol=4e-16)
    origin=clock_origin_energy_contacts(a['source_transfer'],a['independent_transpose_transfer'],3.2-.7j)
    np.testing.assert_allclose(origin['clock_origin_cancellation'],0,atol=4e-15)

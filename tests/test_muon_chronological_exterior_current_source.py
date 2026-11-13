import numpy as np
from bhsm.interface.muon_chronological_exterior_current_source import (
    exterior_current_point_sources,exterior_current_transfer)


def test_pointwise_exterior_and_operator_energy_contacts_match_whole_current():
    rng=np.random.default_rng(2681151)
    rnd=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    n,d,nr,nl=3,4,2,3
    R0,L0=rnd((n,d,288)),rnd((n,d,288))
    Br,Bl=rnd((n,288,nr)),rnd((n,288,nl))
    BrE,BlE=rnd(Br.shape)*.2,rnd(Bl.shape)*.2
    tau=np.array([.05+.02j,.13-.01j,.22+.06j]);anchor=.27-.08j
    K=rnd((n*d,n*d))+20*np.eye(n*d);KE=rnd(K.shape)*.04
    def sources(E):
        a=[exterior_current_point_sources(dict(literal_right_source=R0[q],
                 literal_left_transpose_source=L0[q]),tau[q],continued_energy=E,
                 right_trace_map=Br[q]+(E-anchor)*BrE[q],
                 left_trace_map=Bl[q]+(E-anchor)*BlE[q],
                 right_trace_map_energy_first=BrE[q],left_trace_map_energy_first=BlE[q])for q in range(n)]
        return{k:np.array([x[k]for x in a])for k in
               ('exterior_right_source','exterior_left_transpose_source',
                'exterior_right_energy_source','exterior_left_energy_source')}
    a=sources(anchor);R,L=a['exterior_right_source'],a['exterior_left_transpose_source']
    u=np.linalg.solve(K,R.reshape(n*d,nr)).reshape(n,d,nr)
    p=np.linalg.solve(K.T,L.reshape(n*d,nl)).reshape(n,d,nl)
    x=exterior_current_transfer(L,R,u,p,a['exterior_left_energy_source'],
        a['exterior_right_energy_source'],operator_energy_response=(KE@u.reshape(n*d,nr)).reshape(n,d,nr))
    def current(E):
        b=sources(E);return b['exterior_left_transpose_source'].reshape(n*d,nl).T@np.linalg.solve(
            K+(E-anchor)*KE,b['exterior_right_source'].reshape(n*d,nr))
    eps=2e-6;fd=(current(anchor+eps)-current(anchor-eps))/(2*eps)
    np.testing.assert_allclose(x['continued_energy_first'],fd,rtol=2e-8,atol=2e-7)
    np.testing.assert_allclose(x['exterior_source_transfer'],x['independent_transpose_transfer'],rtol=2e-14,atol=2e-13)
    # Literal independent left maps matter for a complex nonsymmetric source.
    assert np.linalg.norm(x['exterior_source_transfer']-L.reshape(n*d,nl).conj().T@u.reshape(n*d,nr))>1
    assert np.linalg.norm(x['operator_energy_contact'])>1e-3


def test_clock_origin_change_keeps_owned_exterior_function_and_jet():
    rng=np.random.default_rng(48)
    rnd=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    point=dict(literal_right_source=rnd((4,288)),literal_left_transpose_source=rnd((4,288)))
    R,L=rnd((288,2)),rnd((288,3));RE,LE=rnd(R.shape),rnd(L.shape)
    E=.41-.23j;tau=.27+.18j;shift=.16-.11j
    a=exterior_current_point_sources(point,tau,continued_energy=E,right_trace_map=R,left_trace_map=L,
        right_trace_map_energy_first=RE,left_trace_map_energy_first=LE)
    # The SAME physical trace is represented at tau+shift by compensating
    # trace functions; differentiating those functions retains both contacts.
    b=exterior_current_point_sources(point,tau+shift,continued_energy=E,
        right_trace_map=np.exp(E*shift)*R,left_trace_map=np.exp(-E*shift)*L,
        right_trace_map_energy_first=np.exp(E*shift)*(RE+shift*R),
        left_trace_map_energy_first=np.exp(-E*shift)*(LE-shift*L))
    for k in ('exterior_right_source','exterior_left_transpose_source',
              'exterior_right_energy_source','exterior_left_energy_source'):
        np.testing.assert_allclose(a[k],b[k],rtol=5e-14,atol=1e-12)
    assert not a['exterior_time_dependence_projected_to_internal_FE2']

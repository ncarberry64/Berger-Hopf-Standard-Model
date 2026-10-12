import numpy as np
from scipy.linalg import solve
from bhsm.interface.muon_chronological_literal_current_source import literal_point_current_sources,add_literal_point_source
from bhsm.interface.muon_chronological_spectral_blocks import homogeneous_scalar_degree_reduction


def test_literal_source_constant_harmonic_change_reproduces_full_complex_transpose_dual():
    rng=np.random.default_rng(10211);c=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    V=c((24,6,6));b=c(2);P=rng.normal(size=(96,336));d=homogeneous_scalar_degree_reduction(1)
    U=np.kron(np.eye(84),d['real_to_complex_coefficient_map'])
    a=literal_point_current_sources(V,b,P.T,P.T)
    r=U@a['literal_right_source'];l=U.conj()@a['literal_left_transpose_source']
    for k in range(2):
        ix=(np.arange(84)[:,None]*4+np.arange(2)[None]*2+k).ravel()
        z=literal_point_current_sources(V,b,(U@P.T)[ix],(U.conj()@P.T)[ix])
        np.testing.assert_allclose(z['literal_right_source'],r[ix],rtol=2e-14,atol=2e-14)
        np.testing.assert_allclose(z['literal_left_transpose_source'],l[ix],rtol=2e-14,atol=2e-14)
    # A complete nonsymmetric inverse proves the literal source ordering,
    # not only equality of two source helper implementations.
    K=c((336,336))+40*np.eye(336);Kc=U@K@U.conj().T
    ur=solve(K,a['literal_right_source'][:,:4]);pr=solve(K.T,a['literal_left_transpose_source'][:,:4])
    uc=solve(Kc,r[:,:4]);pc=solve(Kc.T,l[:,:4])
    np.testing.assert_allclose(pc.T@r[:,:4],pr.T@a['literal_right_source'][:,:4],rtol=2e-12,atol=2e-12)
    np.testing.assert_allclose(l[:,:4].T@uc,a['literal_left_transpose_source'][:,:4].T@ur,rtol=2e-12,atol=2e-12)
    assert np.linalg.norm(pc.conj().T@r[:,:4]-pr.T@a['literal_right_source'][:,:4])>1e-2


def test_original_source_corner_initial_reaction_and_free_final_are_integrated_literally():
    rng=np.random.default_rng(211);S=rng.normal(size=(168,288))+1j*rng.normal(size=(168,288))
    cols=np.array([0,48,287]);rhs=np.zeros((3,176,3),complex);initial=np.zeros((176,3),complex)
    points=[dict(measure=1+.3j,rows=((0,.25,1),(1,.75,-1))),
        dict(measure=-.2+.7j,rows=((1,.4,2),(2,.6,-2))),
        dict(measure=.5-.2j,rows=((2,.1,1),(3,.9,-1)))]
    expected=np.zeros((4,176,3),complex)
    for p in points:
        add_literal_point_source(rhs,initial,p,S,columns=cols)
        for j,v,_ in p['rows']:expected[j,:168]+=p['measure']*v*S[:,cols]
    np.testing.assert_array_equal(initial,expected[0]);np.testing.assert_array_equal(rhs,expected[1:])
    assert np.linalg.norm(rhs[-1])>0 and not np.count_nonzero(rhs[:,168:])

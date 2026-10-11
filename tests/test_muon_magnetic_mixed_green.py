"""Independent derivative and complete image checks for the reached graph."""
import numpy as np
import pytest
from scipy.linalg import eigh
from bhsm.interface.muon_magnetic_mixed_green import (
    mixed_green_spectral_derivative,magnetic_mixed_green_application,family_fiber_indices,
)


def control():
    # CONTROL_ONLY nonnormal factor matrices: no physical coefficient claim.
    rng=np.random.default_rng(27)
    z=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    Ao=z((2,2));Ae=z((3,3));Xi=z((3,3,2));Xa=z((3,3,2))
    Po=1000*np.eye(2)+Ao.conj().T@Ao;Pe=1000*np.eye(3)+Ae.conj().T@Ae
    po,Vo=eigh(Po);pe,Ve=eigh(Pe)
    Ho=1000*np.eye(2)+rng.normal(size=(2,2));Ho=(Ho+Ho.T)/2
    He=1000*np.eye(3)+rng.normal(size=(3,3));He=(He+He.T)/2
    dH=rng.normal(size=(3,3,2))
    B0=z((2,2,1));B1=z((2,3,2));B1H=z((3,2,2))
    data=dict(A_odd=Ao,A_even=Ae,eigenvalues_odd=po,eigenvalues_even=pe,
        eigenvectors_odd=Vo,eigenvectors_even=Ve,Xi_even_odd=Xi,
        Xi_reverse_dagger_even_odd=Xa,delta_P_square_left=Ae.conj().T@Xi,
        delta_P_square_right=Xa@Ao,mixed_vertex_n0_odd=B0,
        mixed_vertex_n1_Hodd=B1,mixed_vertex_n1_Heven=B1H)
    scalar=dict(positive_H_odd=Ho,positive_H_even=He,
        delta_positive_H_even_odd=dH,action_Gram_scalar=1.7)
    return data,scalar


def exact_unregulated_component(d,s,source,epsilon,*,fermion=True,scalar=True):
    # Original odd scalar injection retained; all reached image/output
    # placements included, without adding an unrelated even starting loop.
    A=np.zeros((5,5),complex);A[:2,:2]=d['A_odd'];A[2:,2:]=d['A_even']
    if fermion:
        A[2:,:2]=epsilon*d['Xi_even_odd'][source]
        A[:2,2:]=epsilon*d['Xi_reverse_dagger_even_odd'][source].conj().T
    P=1000*np.eye(5)+A.conj().T@A;GF=np.linalg.solve(P,A.conj().T)
    H=np.zeros((5,5));H[:2,:2]=s['positive_H_odd'];H[2:,2:]=s['positive_H_even']
    if scalar:
        H[2:,:2]=epsilon*s['delta_positive_H_even_odd'][source]
        H[:2,2:]=H[2:,:2].T
    GH=np.linalg.inv(H)/s['action_Gram_scalar']
    B=np.zeros((5,5,3),complex)
    B[:2,:2,:1]=d['mixed_vertex_n0_odd']
    B[:2,2:,1:]=d['mixed_vertex_n1_Hodd']
    B[2:,:2,1:]=d['mixed_vertex_n1_Heven']
    return np.einsum('aiu,ij,bjv,ab->uv',B.conj(),GF,B,GH)


def test_unregulated_derivative_retains_both_propagators_and_nonnormal_numerator():
    d,s=control();r=mixed_green_spectral_derivative(d,s,0.)
    step=2e-5
    for a in range(3):
        p=exact_unregulated_component(d,s,a,step);m=exact_unregulated_component(d,s,a,-step)
        expected=(p-m)/(2*step)
        np.testing.assert_allclose(r['forward']['total'][a],expected[1:,:1],rtol=2e-8,atol=1e-17)
        np.testing.assert_allclose(r['reverse']['total'][a],expected[:1,1:],rtol=2e-8,atol=1e-17)
    assert np.linalg.norm(r['forward']['fermion_numerator_contact'])>0
    assert np.linalg.norm(r['forward']['scalar_propagator_insertion'])>0
    assert not np.allclose(r['reverse']['total'],r['forward']['total'].conj().transpose(0,2,1),rtol=1e-10,atol=0)


def test_scalar_insertion_has_same_action_gram_and_both_open_placements():
    d,s=control();r=mixed_green_spectral_derivative(d,s,0.)
    h=2e-5
    for a in range(3):
        expected=(exact_unregulated_component(d,s,a,h,fermion=False)-exact_unregulated_component(d,s,a,-h,fermion=False))/(2*h)
        np.testing.assert_allclose(r['forward']['scalar_propagator_insertion'][a],expected[1:,:1],rtol=2e-8,atol=1e-17)
        np.testing.assert_allclose(r['reverse']['scalar_propagator_insertion'][a],expected[:1,1:],rtol=2e-8,atol=1e-17)


def test_common_nonzero_cutoff_derivative_has_positive_series_refinement():
    d,s=control();a=mixed_green_spectral_derivative(d,s,1e-3,series_terms=4)
    b=mixed_green_spectral_derivative(d,s,1e-3,series_terms=6)
    for name,bound in a['contracted_series_tail_majorant_estimates'].items():
        # The deliberately wider control spectra expose the series tail;
        # use its analytic bound, not an arbitrary equality tolerance.
        assert np.linalg.norm(a['forward'][name]-b['forward'][name])<=bound+b['contracted_series_tail_majorant_estimates'][name]
        assert b['contracted_series_tail_majorant_estimates'][name]<bound
    assert a['kernel_positive_series_tail_upper']>0
    assert a['bare_fixed_Y_mixed_vertex_first_derivatives_zero']
    assert not a['temporal_source_derivative_removed_by_operator_identity']


def test_missing_negative_or_nonreal_cutoff_cannot_default():
    d,s=control()
    for bad in (None,-1,1+1j):
        with pytest.raises(ValueError):mixed_green_spectral_derivative(d,s,bad)
    with pytest.raises(ValueError):family_fiber_indices(3)


def test_actual_n1_source_reaches_all_even_images_and_preserves_full_fiber():
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
    from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
    from bhsm.interface.muon_intrinsic_higgs_positive_source import intrinsic_higgs_positive_source_application
    from bhsm.interface.muon_primal_cell_reached_source_heat import actual_reached_cell_vertices
    from bhsm.interface.muon_magnetic_mixed_green import _family_operator_data
    b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    fields=magnetic_open_fields_at_node(b,b['source']['times'][2]);rep=dict(b['representation'],native_positive_nu_squared_action=4)
    angular=retained_full_q_angular_space(ROOT);L=b['times'][-1]
    scalar=intrinsic_higgs_positive_source_application(fields['raw_fields'],rep,angular,length=L,
        first_wall_gauge=fields['first_wall_gauge'],first_H=fields['first_H'])
    d=_family_operator_data(actual_reached_cell_vertices(fields,rep),scalar,angular,1,L)
    assert scalar['source_n3_exactly_zero']
    assert {l[0] for l in scalar['even_harmonic_labels']}=={0,2,4}
    assert d['A_even'].shape==(210,210) and d['A_odd'].shape==(120,120)
    assert d['mixed_vertex_n1_Hodd'].shape==(80,210,24)
    assert d['mixed_vertex_n1_Heven'].shape==(140,120,24)
    np.testing.assert_allclose(d['delta_P_even_odd'],d['A_even'].conj().T@d['Xi_even_odd']+
        d['Xi_reverse_dagger_even_odd']@d['A_odd'],rtol=1e-15,atol=1e-15)
    # Scalar real4 Hessian vertices have both Yukawa LR placements and
    # retain neutral leakage; no charged-only replacement is permitted.
    B=d['mixed_vertex_n0_odd'][0,:6]
    assert np.linalg.norm(B[:2,4:])>0 and np.linalg.norm(B[4:,:2])>0

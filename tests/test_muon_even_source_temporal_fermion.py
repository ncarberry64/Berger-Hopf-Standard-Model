"""CONTROL_ONLY independent complete-image and action-pairing checks."""
import numpy as np
import pytest

from bhsm.interface.muon_even_source_temporal_fermion import (
    complete_even_fermion_blocks, integrated_fermion_weak_form)
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_angular_derivative_matrices,scalar_section_labels


def test_complete_even_family_image_and_exact_spectators():
    a=complete_even_fermion_blocks()
    assert [len(b['harmonic_indices'])for b in a['angular_blocks']]==[1,3,3,3,5,5,5,5,5]
    assert sorted(np.concatenate([b['harmonic_indices']for b in a['angular_blocks']]))==list(range(35))
    assert sorted(np.concatenate(a['family_indices']))==list(range(18))
    assert 8*sum(6*len(b['harmonic_indices'])for b in a['angular_blocks'])*3==5040
    # Independently constructed complex irreducible right-coframe action.
    labels=scalar_section_labels(4);ids=[i for i,l in enumerate(labels)if l[0]in(0,2,4)]
    expected=scalar_angular_derivative_matrices(4)[:,ids][:,:,ids]
    np.testing.assert_allclose(a['complex_derivatives'],expected,atol=3e-15,rtol=0)
    assert a['spectator_off_block_max']==0
    assert a['complex_frame_unitary_residual']<2e-15
    assert a['real_to_complex_derivative_residual']<2e-14


def test_changing_nonnormal_weak_action_matches_literal_image_and_measure():
    rng=np.random.default_rng(107);nt=5;d=3;nb=4
    N=np.linspace(.7,1.3,nt);w=np.linspace(.02,.1,nt)
    B=rng.normal(size=(nt,d,d))+1j*rng.normal(size=(nt,d,d))
    p=rng.normal(size=(nt,nb));dp=rng.normal(size=(nt,nb))
    c=rng.normal(size=(nb,d))+1j*rng.normal(size=(nb,d))
    a=integrated_fermion_weak_form(N,B,w,p,dp);v=c.ravel()
    field=p@c;image=(dp@c)/N[:,None]+np.einsum('tij,tj->ti',B,field)
    literal=np.sum(w*N*np.sum(abs(image)**2,axis=1))
    norm=np.sum(w*N*np.sum(abs(field)**2,axis=1))
    np.testing.assert_allclose(v.conj()@a['weak_form']@v,literal,rtol=3e-15,atol=1e-13)
    np.testing.assert_allclose(v.conj()@a['Gram']@v,norm,rtol=3e-15,atol=1e-13)
    # Reversing the non-normal operator's adjoint is a different action.
    wrong=integrated_fermion_weak_form(N,B.conj().transpose(0,2,1),w,p,dp)
    assert abs(v.conj()@(a['weak_form']-wrong['weak_form'])@v)>1


@pytest.mark.parametrize('N,w',[([0,1],[1,1]),([1,1],[0,1]),([np.nan,1],[1,1])])
def test_same_clock_weak_measure_guards(N,w):
    with pytest.raises(ValueError):
        integrated_fermion_weak_form(np.array(N),np.zeros((2,2,2)),np.array(w),np.ones((2,1)),np.ones((2,1)))

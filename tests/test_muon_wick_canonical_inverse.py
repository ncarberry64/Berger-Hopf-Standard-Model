import numpy as np
from bhsm.interface.muon_wick_canonical_inverse import continued_canonical_cell,canonical_cell_adjoint
from bhsm.interface.muon_wick_temporal_action import wick_temporal_forms,analytic_gauss_reduction


def test_continued_original_gauss_then_inverse_matches_action_contour():
    rng=np.random.default_rng(141);M=np.diag([0.,2.,3.,.4]);B=rng.normal(size=(4,4))*.1;B[:,0]=0
    K=rng.normal(size=(4,4));K=(K+K.T)/2;K[0,0]=4
    raw=(M,B,K);R=wick_temporal_forms(raw,1);L=analytic_gauss_reduction(raw,1);E=analytic_gauss_reduction(R['forms'],1)
    state=rng.normal(size=(4,2));b=rng.normal(size=(1,2));bt=rng.normal(size=(1,2));h=.021
    a=continued_canonical_cell(tuple(L[k]for k in('M','B','K')),h,state,b,bt)
    se=state.astype(complex);se[2:]*=-1j
    e=continued_canonical_cell(tuple(E[k]for k in('M','B','K')),1j*h,se,b,-1j*bt)
    expected=a['final_state'].copy();expected[2:]*=-1j
    np.testing.assert_allclose(e['final_state'],expected,atol=1e-14,rtol=1e-14)
    assert np.max(abs(e['original_midpoint_canonical_residual']))<1e-14


def test_recursive_transpose_adjoint_keeps_initial_boundary_and_source():
    rng=np.random.default_rng(28);M=np.diag([2.,3.,.5]);B=rng.normal(size=(3,3))*.1
    K=rng.normal(size=(3,3));K=(K+K.T)/2
    forms=(M,-1j*B,-K);state=rng.normal(size=(4,3))+1j*rng.normal(size=(4,3))
    source=rng.normal(size=(1,3));rate=-1j*rng.normal(size=(1,3));dual=rng.normal(size=(4,2))+1j*rng.normal(size=(4,2))
    c=continued_canonical_cell(forms,.013j,state,source,rate);a=canonical_cell_adjoint(c,dual)
    np.testing.assert_allclose(dual.T@c['final_state'],a['previous_dual'].T@state+a['source_pairing'],rtol=1e-14,atol=1e-14)
    assert np.linalg.norm(a['source_pairing'])>0
    assert np.max(abs(a['inverse_adjoint_residual']))<1e-14

import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_shifted_boundary_source import (
    canonical_reset_chart,shifted_boundary_forms,source_corrected_form_core_return,
    cauchy_external_trace_maps)


def test_density_reset_keeps_independent_dual_and_outward_pairing():
    U=np.array([[0,1j],[1j,0]]);Cp=np.diag([2.,3.]);Cc=np.diag([4.,5.])
    a=canonical_reset_chart(Cp,Cc,U);T=a['canonical_value_reset']
    q=np.array([1+2j,3-1j]);p=np.array([-.3j,2+1j])
    np.testing.assert_allclose(T@Cp@q,Cc@U@q)
    np.testing.assert_allclose((T@q).T@a['analytic_covector_reset']@p,q.T@p)
    np.testing.assert_allclose((T@q).conj().T@a['Hilbert_covector_reset']@p,q.conj().T@p)
    assert np.linalg.norm(a['analytic_covector_reset']-a['Hilbert_covector_reset'])>1


def test_independent_analytic_envelope_and_true_Hilbert_square():
    rng=np.random.default_rng(504);A=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6))
    As=A.conj().T+.2j*np.eye(6);w=1+.2j;ws=1-.3j
    q=dict(H=A,Hsharp=As,R=2.,Rsharp=2.,right_clock=w,reflected_clock=ws,
        measure=.7,original_holomorphic_measure=.4+.1j,rows=((0,.7,-2.),(1,.3,2.)))
    out=shifted_boundary_forms([q],temporal_nodes=2,angular_derivatives=np.zeros((3,1,1)),alpha=np.zeros((3,6,6)))
    E=.31;p=.3;v=2.;right=v*np.eye(6)/w+p*A
    left=v*np.eye(6)/ws+p*As
    actual=(.4+.1j)*(left+E*w/ws*p*np.eye(6))@(right-E*p*np.eye(6))
    K=out['forms']['analytic_envelope'];poly=sum(E**k*a['diagonal'][0]for k,a in enumerate(K))
    np.testing.assert_allclose(poly,actual,rtol=2e-15,atol=3e-15)
    Kh=out['forms']['Hilbert_shift'];polyh=sum(E**k*a['diagonal'][0]for k,a in enumerate(Kh))
    np.testing.assert_allclose(polyh,.7*(right-E*p*np.eye(6)).conj().T@(right-E*p*np.eye(6)),atol=3e-15)
    assert np.linalg.norm(poly-polyh)>1


def test_actual_square_transpose_and_source_corrected_conormal():
    rng=np.random.default_rng(501);n=5;d=3;c=2
    D=5*np.eye(d)[None]+rng.normal(size=(n,d,d))*.08+1j*rng.normal(size=(n,d,d))*.1
    U=rng.normal(size=(n-1,d,d))*.1;L=rng.normal(size=(n-1,d,d))*.2
    B=rng.normal(size=(n,d,c))+1j*rng.normal(size=(n,d,c));left=rng.normal(size=(n,c,d))+1j*rng.normal(size=(n,c,d))
    blocks={f'{kind}_{key}':a for kind in('K','M')for key,a in zip(('diagonal','upper','lower'),(D,U,L))}
    r=source_corrected_form_core_return(blocks,B,left,weak_factor=(D,U,L),source_moments=B)
    np.testing.assert_allclose(r['form_core_literal_current'],r['independent_form_core_transpose_current'],atol=2e-15)
    np.testing.assert_allclose(r['natural_literal_current'],r['independent_natural_transpose_current'],atol=2e-15)
    assert np.linalg.norm(r['source_corrected_final_conormal_omitting_source']-r['source_corrected_final_conormal'])>.1
    np.testing.assert_allclose(r['form_core_original_row_residual'][:-1],0.,atol=1e-15)
    np.testing.assert_allclose(r['form_core_unsquared_source_rows'],r['natural_unsquared_source_rows']-r['unsquared_forced_source_return'],atol=2e-15)


def test_noncommuting_transport_phases_cancel_with_independent_dual():
    H=np.array([[[.1,.2j],[.3,-.1]],[[.2,.4],[-.1j,.3]]]);h=np.array([.03,.05+.01j]);T=np.array([[1,.1j],[0,1]])
    a=cauchy_external_trace_maps(h,H,energy=.27,reset_node=1,reset=T)
    exact=expm(-h[1]*H[1])@T@expm(-h[0]*H[0])
    np.testing.assert_allclose(a['physical_right_trace_map'][-1],exact,atol=4e-16)
    np.testing.assert_allclose(a['analytic_dual_pairing_residual'],0.,atol=5e-16)
    np.testing.assert_allclose(a['physical_right_trace_map_energy_first'],0.,atol=1e-17)
    np.testing.assert_allclose(a['physical_analytic_left_trace_map_energy_first'],0.,atol=1e-17)
    assert a['initial_and_terminal_Dirichlet_boundary_residual'].shape==(4,2)
    assert np.linalg.matrix_rank(a['initial_and_terminal_Dirichlet_boundary_residual'])==2

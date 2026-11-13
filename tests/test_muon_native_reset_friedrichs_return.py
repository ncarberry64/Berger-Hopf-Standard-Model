import numpy as np
from scipy.linalg import block_diag
from bhsm.interface.muon_native_reset_friedrichs_return import (
    terminal_friedrichs_source_return,fixed_form_core_source_two_jet,reset_birth_schur)


def _chain(seed=12):
    rng=np.random.default_rng(seed);n,d=5,2
    A=rng.normal(size=(n*d,n*d))+1j*rng.normal(size=(n*d,n*d))
    D=np.array([A[2*j:2*j+2,2*j:2*j+2]for j in range(n)])+9*np.eye(d)
    U=rng.normal(size=(n-1,d,d))+1j*rng.normal(size=(n-1,d,d))
    L=.3*(rng.normal(size=U.shape)+1j*rng.normal(size=U.shape))
    M=np.array([np.eye(d)*(1+j/5)for j in range(n)])
    mu=.06*np.ones_like(U);ml=.04*np.ones_like(L)
    return dict(K_diagonal=D,K_upper=U,K_lower=L,M_diagonal=M,M_upper=mu,M_lower=ml)


def _dense(D,U,L):
    F=block_diag(*D);d=len(D[0])
    for j in range(len(U)):
        F[j*d:(j+1)*d,(j+1)*d:(j+2)*d]=U[j]
        F[(j+1)*d:(j+2)*d,j*d:(j+1)*d]=L[j]
    return F


def test_forced_terminal_return_matches_independent_original_rows_and_mass_pencil():
    b=_chain();rng=np.random.default_rng(7);rhs=rng.normal(size=(5,2,3))+1j*rng.normal(size=(5,2,3));z=-2.3+.4j
    r=terminal_friedrichs_source_return(b,rhs,spectral_parameter=z)
    D,U,L=[b['K_'+k]-z*b['M_'+k]for k in('diagonal','upper','lower')]
    expected=np.zeros_like(rhs);expected[:-1]=np.linalg.solve(_dense(D,U,L)[:-2,:-2],rhs[:-1].reshape(8,3)).reshape(4,2,3)
    np.testing.assert_allclose(r['form_core_solution'],expected,rtol=1e-12,atol=1e-14)
    np.testing.assert_allclose(r['form_core_original_row_residual'][:-1],0,atol=2e-14)
    np.testing.assert_allclose(r['terminal_Dirichlet_trace'],0,atol=2e-14)
    assert np.linalg.norm(r['final_reaction'])>.1


def test_dirichlet_source_two_jet_keeps_direct_and_both_ordered_contacts():
    b=_chain();P=tuple(b['K_'+k]for k in('diagonal','upper','lower'));rng=np.random.default_rng(31)
    PA=tuple(.05*(rng.normal(size=x.shape)+1j*rng.normal(size=x.shape))for x in P)
    PB=tuple(.07*(rng.normal(size=x.shape)+1j*rng.normal(size=x.shape))for x in P)
    PAB=tuple(.1*rng.normal(size=x.shape)for x in P)
    rhs=rng.normal(size=(5,2,2));ra=.2*rhs;rb=-.3*rhs;rab=.07*rhs
    out=fixed_form_core_source_two_jet(P,rhs,first_pencils=(PA,PB),first_sources=(ra,rb),mixed_pencil=PAB,mixed_source=rab)
    def at(a,c):
        p=tuple(x+a*y+c*z+a*c*t for x,y,z,t in zip(P,PA,PB,PAB))
        return fixed_form_core_source_two_jet(p,rhs+a*ra+c*rb+a*c*rab)['solution']
    errors=[]
    for h in(.003,.0015):
        fd=(at(h,h)-at(h,-h)-at(-h,h)+at(-h,-h))/(4*h*h)
        errors.append(np.linalg.norm(fd-out['mixed_solution']))
    assert errors[1]<errors[0]*.35
    np.testing.assert_allclose(out['mixed_original_row_residual'][:-1],0,atol=1e-14)


def test_nontrivial_reset_pullback_precedes_two_arm_schur_and_no_seam_load():
    b=_chain();birth=3;j=birth-1;z=.21j
    forms=dict(parent_birth_K=.4*b['K_diagonal'][j],child_birth_K=.6*b['K_diagonal'][j],
        parent_birth_M=.3*b['M_diagonal'][j],child_birth_M=.7*b['M_diagonal'][j])
    R=np.array([[0,1j],[1,0]],complex)
    for core in(False,True):
        out=reset_birth_schur(b,forms,birth_trace_node=birth,spectral_parameter=z,reset_lift=R,terminal_form_core=core)
        D,U,L=[b['K_'+k]-z*b['M_'+k]for k in('diagonal','upper','lower')]
        D=D.copy();U=U.copy();L=L.copy()
        D[j]=forms['parent_birth_K']-z*forms['parent_birth_M']+R.conj().T@(forms['child_birth_K']-z*forms['child_birth_M'])@R
        U[j]=R.conj().T@U[j];L[j]=L[j]@R
        F=_dense(D,U,L)
        if core:F=F[:-2,:-2]
        G=np.linalg.inv(F)[2*j:2*j+2,2*j:2*j+2]
        np.testing.assert_allclose(out['birth_Green'],G,rtol=1e-13,atol=1e-14)
        np.testing.assert_allclose(out['sourced_opposite_normal_residual'],0,atol=2e-14)
        assert out['independent_fermion_seam_action_added'] is False

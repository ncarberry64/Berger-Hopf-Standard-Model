import numpy as np
from numpy.testing import assert_allclose

from bhsm.interface.muon_chronological_spectral_blocks import (
    chronological_spectral_factor,chronological_selected_inverse,
    chronological_source_solve,chronological_source_residual,
    chronological_action_trace,homogeneous_scalar_degree_reduction)


def _chain(seed=111):
    rng=np.random.default_rng(seed);sizes=[3,2,4,3]
    make=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    D=[make((d,d))+6*np.eye(d)for d in sizes]
    U=[make((a,b))for a,b in zip(sizes,sizes[1:])]
    L=[make((b,a))for a,b in zip(sizes,sizes[1:])]
    full=np.zeros((sum(sizes),)*2,complex);at=np.r_[0,np.cumsum(sizes)]
    for j,A in enumerate(D):full[at[j]:at[j+1],at[j]:at[j+1]]=A
    for j,(A,B)in enumerate(zip(U,L)):
        full[at[j]:at[j+1],at[j+1]:at[j+2]]=A
        full[at[j+1]:at[j+2],at[j]:at[j+1]]=B
    return D,U,L,full,at


def test_independent_complex_selected_inverse_and_source_rows():
    D,U,L,A,at=_chain();f=chronological_spectral_factor(D,U,L)
    selected=chronological_selected_inverse(f);G=np.linalg.inv(A)
    rhs=np.arange(len(A)*2).reshape(len(A),2)/13+.2j
    blocks=[rhs[at[j]:at[j+1]]for j in range(len(D))]
    x=chronological_source_solve(f,blocks)
    assert_allclose(np.concatenate(x),np.linalg.solve(A,rhs),rtol=8e-14,atol=4e-14)
    assert max(np.max(abs(r))for r in chronological_source_residual(f,x,blocks))<2e-14
    for j in range(len(D)):
        assert_allclose(selected['diagonal'][j],G[at[j]:at[j+1],at[j]:at[j+1]],rtol=2e-14,atol=3e-16)
        if j<len(U):
            assert_allclose(selected['upper'][j],G[at[j]:at[j+1],at[j+1]:at[j+2]],rtol=3e-14,atol=3e-16)
            assert_allclose(selected['lower'][j],G[at[j+1]:at[j+2],at[j]:at[j+1]],rtol=3e-14,atol=3e-16)
    phase,logs=np.linalg.slogdet(A)
    assert_allclose(f['determinant_phase'],phase,atol=8e-15)
    assert_allclose(f['log_absolute_determinant'],logs,atol=8e-15)
    assert np.linalg.norm(U[0]-L[0].conj().T)>1


def test_trace_derivative_matches_whole_pencil_difference():
    D,U,L,A,_=_chain();dD,dU,dL,dA,_=_chain(771)
    f=chronological_spectral_factor(D,U,L);s=chronological_selected_inverse(f)
    derivative=chronological_action_trace(s,dD,dU,dL)
    assert_allclose(derivative,np.trace(np.linalg.solve(A,dA)),rtol=4e-14,atol=8e-14)
    # Independent analytic log determinant derivative through a small
    # circular Cauchy sample; no conjugate-reverse block substitution.
    radius=.02;angles=2*np.pi*np.arange(32)/32;z=radius*np.exp(1j*angles)
    # All samples lie in the same nonsingular determinant/log branch.
    values=np.array([np.log(np.linalg.det(A+t*dA))for t in z])
    actual=np.mean(values*np.exp(-1j*angles))/radius
    assert_allclose(derivative,actual,rtol=2e-12,atol=2e-12)


def test_owned_homogeneous_degree_preserves_whole_trace():
    from scipy.linalg import expm
    rng=np.random.default_rng(65)
    H=rng.normal(size=(6,6))+.3j*rng.normal(size=(6,6))
    K=rng.normal(size=(3,6,6))+.2j*rng.normal(size=(3,6,6))
    for n in range(5):
        r=homogeneous_scalar_degree_reduction(n);E=r['angular_derivatives'];U=r['real_to_complex_coefficient_map']
        reduced=np.kron(H,np.eye(n+1))+sum(np.kron(K[i],E[i])for i in range(3))
        full=np.kron(H,np.eye((n+1)**2))+sum(np.kron(K[i],r['full_real_angular_derivatives'][i])for i in range(3))
        whole=np.kron(np.eye(6),U)@full@np.kron(np.eye(6),U.conj().T)
        expected=np.kron(reduced,np.eye(n+1))
        assert_allclose(whole,expected,rtol=1e-14,atol=2e-14)
        assert_allclose(np.trace(expm(.01*full)),(n+1)*np.trace(expm(.01*reduced)),rtol=2e-14,atol=2e-13)

import numpy as np
from scipy.linalg import solve
from bhsm.interface.muon_chronological_current_factor import factor_literal_current_chain,solve_literal_current_chain


def test_full_nonsymmetric_bordered_chain_and_literal_adjoint_reproduce_original_dense_action():
    rng=np.random.default_rng(11103);c=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    n,d=5,6;D=c((n,d,d))+6*np.eye(d);U=.2*c((n-1,d,d));L=.15*c(U.shape)
    # Retain an algebraic field row and a named frame multiplier in every
    # supplied block rather than deleting their zero kinetic diagonal.
    D[:,-1,:]=0;D[:,:,-1]=0;D[:,-1,1]=1;D[:,1,-1]=1
    U[:,-1]=0;U[:,:,-1]=0;L[:,-1]=0;L[:,:,-1]=0
    K=np.zeros((n*d,n*d),complex)
    for j in range(n):
        s=slice(j*d,(j+1)*d);K[s,s]=D[j]
        if j<n-1:
            t=slice((j+1)*d,(j+2)*d);K[s,t]=U[j];K[t,s]=L[j]
    scales=np.exp(rng.normal(size=(n,d)));Dt=D*scales[:,:,None]*scales[:,None,:]
    Ut=U*scales[:-1,:,None]*scales[1:,None,:];Lt=L*scales[1:,:,None]*scales[:-1,None,:]
    original=Dt.copy();f=factor_literal_current_chain(Dt,Ut,Lt)
    np.testing.assert_array_equal(Dt,original)
    r,l=c((n,d,7)),c((n,d,7));ur=scales[:,:,None]*solve_literal_current_chain(f,scales[:,:,None]*r)
    pl=scales[:,:,None]*solve_literal_current_chain(f,scales[:,:,None]*l,transpose=True)
    np.testing.assert_allclose(ur.reshape(n*d,7),solve(K,r.reshape(n*d,7)),rtol=2e-13,atol=2e-13)
    np.testing.assert_allclose(pl.reshape(n*d,7),solve(K.T,l.reshape(n*d,7)),rtol=2e-13,atol=2e-13)
    np.testing.assert_allclose(pl.reshape(n*d,7).T@r.reshape(n*d,7),l.reshape(n*d,7).T@ur.reshape(n*d,7),rtol=2e-13,atol=2e-13)
    assert np.linalg.norm(pl.reshape(n*d,7).conj().T@r.reshape(n*d,7)-l.reshape(n*d,7).T@ur.reshape(n*d,7))>.1


def test_consume_diagonal_is_explicit_and_free_final_source_stays_in_action():
    D=np.array([[[3.,1.],[0.,2.]],[[5.,-1.],[1.,4.]]],complex)
    U=np.array([[[.2,0.],[0.,.3]]],complex);L=np.array([[[.1,.2],[0.,-.2]]],complex)
    before=D.copy();f=factor_literal_current_chain(D,U,L,consume_diagonal=True)
    assert np.shares_memory(f['LU_diagonal'],D)and not np.array_equal(D,before)
    rhs=np.zeros((2,2,1),complex);rhs[-1,:,0]=[1.,2.]
    x=solve_literal_current_chain(f,rhs)
    K=np.block([[before[0],U[0]],[L[0],before[1]]])
    np.testing.assert_allclose(K@x.reshape(4,1),rhs.reshape(4,1),atol=2e-15)

"""Indexed numerical eigenpair proposal; inclusion and inertia certify it later."""
import numpy as np
from flint import arb,arb_mat


def indexed_proposal(matrix,index,reference):
    """Refine the requested index without a hard-coded outgoing C2 index.

    The returned gap is a floating diagnostic only. Callers must independently
    verify normalized inclusion, reference orientation and spectral inertia.
    """
    H=np.asarray(matrix,dtype=object);n=H.shape[0]
    if H.shape!=(n,n) or not 0<=index<n or np.shape(reference)!=(n,):
        raise ValueError('square matrix, valid index and matching reference required')
    values,vectors=np.linalg.eigh(np.array([float(v.mid()) for v in H.flat]).reshape(n,n))
    p=vectors[:,index]
    if float(p@reference)<0:p=-p
    P=arb_mat(n,1,[arb(float(v)) for v in p]);lam=arb(float(values[index]));M=arb_mat(n,n,list(H.flat))
    for _ in range(5):
        J=arb_mat(n+1,n+1)
        for i in range(n):
            for j in range(n):J[i,j]=M[i,j]-(lam if i==j else 0)
            J[i,n]=-P[i,0];J[n,i]=P[i,0]
        residual=M*P-P*lam
        F=arb_mat(n+1,1,residual.entries()+[(P.transpose()*P)[0,0]/2-arb(1)/2])
        correction=J.solve(-F,algorithm='precond')
        P=arb_mat(n,1,[(P[i,0]+correction[i,0]).mid() for i in range(n)])
        lam=(lam+correction[n,0]).mid()
    residual=M*P-P*lam
    residual_upper=float(sum((abs(v) for v in residual.entries()),arb(0)).upper())
    gap=float(min(abs(values[index]-np.delete(values,index))))
    radius=arb(2)**-400
    return np.array([v+arb(0,radius) for v in P.entries()],dtype=object),lam+arb(0,radius),gap,residual_upper

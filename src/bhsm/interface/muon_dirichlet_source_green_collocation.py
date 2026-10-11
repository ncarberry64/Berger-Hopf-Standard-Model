"""High-order collocation of the same continuous Dirichlet source Green.

The current contains cancellations between a particular source and its
Dirichlet face correction. Gauss collocation integrates their polynomial
source moments before that subtraction. It retains both time halves and
the same complex current orientation; it is an unregulated reference check.
"""
from __future__ import annotations
import numpy as np
from numpy.polynomial.legendre import Legendre
from scipy.linalg import lu_factor,lu_solve


def gauss_collocation_table(stages):
    if type(stages)is not int or stages<2:raise ValueError('explicit Gauss stage count required')
    z,w=np.polynomial.legendre.leggauss(stages);c=(z+1)/2;b=w/2;A=np.empty((stages,stages))
    # Exact Gauss orthogonality expands each cardinal polynomial in the
    # Legendre basis. Integrate there to avoid monomial cancellation.
    A.fill(0.)
    for k in range(stages):
        p=Legendre.basis(k);integ=p.integ()
        A+=(2*k+1)/4*np.outer(integ(z)-integ(-1.),w*p(z))
    return dict(c=c,b=b,A=A,constant_moment_defect=float(np.max(abs(A.sum(axis=1)-c))))


def dirichlet_source_current_collocation(evaluate,*,length,stages,substeps_per_half=1):
    """Apply the unprojected full-time f/g source problem and dual current.

    Same f'=N(S-Bf+g),g'=NB^dagger g and y=length*g0 as the direct RK
    benchmark. All source columns enter the stage solve; none are compressed
    by a numerical rank test. The midpoint is always an integration face.
    The reported stage and endpoint residuals are binary diagnostics.
    """
    T=float(length)
    if not np.isfinite(T)or T<=0 or type(substeps_per_half)is not int or substeps_per_half<1:
        raise ValueError('positive same cell and split refinement required')
    table=gauss_collocation_table(stages);c,b,A=(table[n]for n in('c','b','A'))
    first=evaluate(0.);B=np.asarray(first['B']);S=np.asarray(first['S']);L=np.asarray(first['L']);d=len(B)
    if B.shape!=(d,d)or S.ndim!=3 or S.shape[0]!=d or L.shape!=(S.shape[1],d,S.shape[2]):
        raise ValueError('same complete source/current block axes required')
    e,a=S.shape[1:];p=np.zeros_like(S,dtype=complex);q=np.zeros((d,d),complex);v=np.eye(d,dtype=complex)
    cp=np.zeros((e,e),complex);cq=np.zeros((e,d,a),complex);h=T/(2*substeps_per_half);maxres=0.
    for step in range(2*substeps_per_half):
        pts=[evaluate(float((step+x)*h))for x in c]
        N=np.array([r['N']for r in pts],float);BB=np.array([r['B']for r in pts]);SS=np.array([r['S']for r in pts]);LL=np.array([r['L']for r in pts])
        if np.any(N<=0)or any(not np.isfinite(x).all()for x in(N,BB,SS,LL)):
            raise ValueError('finite same physical-clock point sources required')
        eye=np.eye(stages*d,dtype=complex)
        Kp=eye+(h*A[:,:,None,None]*N[None,:,None,None]*BB[None]).transpose(0,2,1,3).reshape(stages*d,stages*d)
        Kv=eye-(h*A[:,:,None,None]*N[None,:,None,None]*BB.conj().transpose(0,2,1)[None]).transpose(0,2,1,3).reshape(stages*d,stages*d)
        # First solve the homogeneous g transport, then its f source.
        rv=np.broadcast_to(v,(stages,d,d)).reshape(stages*d,d)
        vv=lu_solve(lu_factor(Kv),rv).reshape(stages,d,d)
        rq=q[None]+h*np.einsum('ij,j,jab->iab',A,N,vv)/T
        rp=p[None]+h*np.einsum('ij,j,jdea->idea',A,N,SS)
        rhs=np.concatenate((rq.reshape(stages*d,d),rp.reshape(stages*d,-1)),axis=1)
        factor=lu_factor(Kp);solution=lu_solve(factor,rhs)
        maxres=max(maxres,float(np.linalg.norm(Kp@solution-rhs)/max(np.linalg.norm(rhs),np.finfo(float).tiny)),
            float(np.linalg.norm(Kv@vv.reshape(stages*d,d)-rv)/np.linalg.norm(rv)))
        qq=solution[:,:d].reshape(stages,d,d);pp=solution[:,d:].reshape(stages,d,e,a)
        cp+=h*np.einsum('j,j,jida,jdka->ik',b,N,LL,pp)
        cq+=h*np.einsum('j,j,jida,jdk->ika',b,N,LL,qq)
        p+=h*np.einsum('j,j,jdea->dea',b,N,SS-np.einsum('jdk,jkea->jdea',BB,pp))
        q+=h*np.einsum('j,j,jdk->dk',b,N,vv/T-BB@qq)
        v+=h*np.einsum('j,j,jdk->dk',b,N,BB.conj().transpose(0,2,1)@vv)
    y=-np.linalg.solve(q,p.reshape(d,-1)).reshape(p.shape)
    final=p+(q@y.reshape(d,-1)).reshape(p.shape)
    return dict(signed_source_current=-(cp+np.einsum('ika,kja->ij',cq,y)),selected_scaled_initial_g=y,
        final_Dirichlet_residual=final,endpoint_residual_norm=float(np.linalg.norm(final)),
        endpoint_relative_residual=float(np.linalg.norm(final)/max(np.linalg.norm(p),np.finfo(float).tiny)),
        stage_relative_residual=maxres,fundamental_source_condition=float(np.linalg.cond(q)),
        stages=stages,substeps_per_half=substeps_per_half,table_constant_moment_defect=table['constant_moment_defect'],
        temporal_midpoint_contact_retained=True,unregulated_same_reference=True,
        finite_cutoff_or_native_completion_or_Pauli_equivalence_claimed=False)

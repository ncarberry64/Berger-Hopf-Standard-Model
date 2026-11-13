"""Direct full-time source/dual benchmark for A=partial_t/N+B.

With the same Ndt pairing, A^dagger=-partial_t/N+B^dagger. Setting
g=Af-S gives f'=N(g+S-Bf), g'=NB^dagger g. Dirichlet f at both faces
determines g(initial) internally. A source derivative, temporal covariance
selector, artificial inverse shift and discarded midpoint contact are not
needed. This unregulated problem does not replace a common-cutoff heat kernel.
"""
from __future__ import annotations
import numpy as np


def dirichlet_source_current(evaluate,*,length,steps_per_half):
    """Integrate the literal source Green and its left current on two halves.

    evaluate(u) returns N>0, B[d,d], S[d,e,a], L[e,d,a]. The field inverse
    may already be factored symmetrically into the a source axis. With
    y=length*g(initial), Q(0)=0,V(0)=I, Q'=N(V/length-BQ),
    V'=NB^dagger V. The particular solution p'=N(S-Bp) starts at zero.
    Then y=-Q(length)^-1 p(length), f=p+Qy, and
    current=-int Ndt sum_a L_a f_a. Complex orientations are literal.
    RK4 refinement is a numerical diagnostic; no outward bound is implied.
    """
    T=float(length)
    if not np.isfinite(T) or T<=0 or type(steps_per_half)is not int or steps_per_half<1:
        raise ValueError('positive same-cell length and explicit split refinement required')
    first=evaluate(0.);N,B,S,L=first['N'],np.asarray(first['B']),np.asarray(first['S']),np.asarray(first['L'])
    d=len(B)
    if B.shape!=(d,d)or S.ndim!=3 or S.shape[0]!=d or L.shape!=(S.shape[1],d,S.shape[2]):
        raise ValueError('same complete coefficient/source/readout axes required')
    e=S.shape[1];a=S.shape[2];I=np.eye(d,dtype=complex)
    state=[np.zeros_like(S,dtype=complex),np.zeros((d,d),complex),I.copy(),
        np.zeros((e,e),complex),np.zeros((e,d,a),complex)]
    def rhs(t,z):
        r=evaluate(float(t));n=float(r['N']);b=np.asarray(r['B']);s=np.asarray(r['S']);l=np.asarray(r['L'])
        if (n<=0 or not np.isfinite(n)or b.shape!=(d,d)or s.shape!=S.shape or l.shape!=L.shape or
                any(not np.isfinite(x).all()for x in(b,s,l))):
            raise ValueError('finite same-domain physical-clock point application required')
        p,q,v,cp,cq=z
        return [n*(s-(b@p.reshape(d,-1)).reshape(p.shape)),n*(v/T-b@q),n*b.conj().T@v,
            n*np.einsum('ida,dja->ij',l,p),n*np.einsum('ida,dk->ika',l,q)]
    def add(z,k,h):return [x+h*y for x,y in zip(z,k)]
    h=T/(2*steps_per_half)
    # Every kink is a step face. RHS uses only values, not time derivatives.
    for i in range(2*steps_per_half):
        t=i*h;k1=rhs(t,state);k2=rhs(t+h/2,add(state,k1,h/2))
        k3=rhs(t+h/2,add(state,k2,h/2));k4=rhs(t+h,add(state,k3,h))
        state=[x+h*(a+2*b+2*c+d)/6 for x,a,b,c,d in zip(state,k1,k2,k3,k4)]
    p,q,v,cp,cq=state;y=-np.linalg.solve(q,p.reshape(d,-1)).reshape(p.shape)
    endpoint=p+(q@y.reshape(d,-1)).reshape(p.shape)
    current=-(cp+np.einsum('ika,kja->ij',cq,y))
    return dict(signed_source_current=current,selected_scaled_initial_g=y,
        final_particular=p,final_fundamental_source=q,final_homogeneous_g=v,
        final_Dirichlet_residual=endpoint,endpoint_residual_norm=float(np.linalg.norm(endpoint)),
        endpoint_relative_residual=float(np.linalg.norm(endpoint)/max(np.linalg.norm(p),np.finfo(float).tiny)),
        fundamental_source_condition=float(np.linalg.cond(q)),steps_per_half=steps_per_half,
        temporal_midpoint_contact_retained=True,source_derivative_required=False,
        temporal_complement_discarded=False,unregulated_same_reference=True,
        finite_cutoff_or_native_completion_or_Pauli_equivalence_claimed=False)

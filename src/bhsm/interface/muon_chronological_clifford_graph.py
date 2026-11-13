"""Complete chronological reflected Clifford pencil, without a dense inverse.

The original holomorphic weak measure and independent reflected coframe
remain in every cell and corner leg. Only the initial right trace is
removed. The final weak row and both directions of each corner are kept.
"""
from __future__ import annotations
import numpy as np


def _angular_operators(q, angular_derivatives, alpha):
    E=np.asarray(angular_derivatives,complex);alpha=np.asarray(alpha,complex)
    h=E.shape[-1]
    if E.shape!=(3,h,h) or alpha.shape!=(3,6,6):
        raise ValueError('complete owned angular and Clifford representations required')
    spatial=sum(np.kron(-1j*a,e) for a,e in zip(alpha,E))
    H,Hs=(np.asarray(q[k],complex) for k in ('H','Hsharp'))
    if H.shape!=(6,6) or Hs.shape!=(6,6):raise ValueError('both independent C6 body branches required')
    return np.kron(H,np.eye(h))+spatial/q['R'],np.kron(Hs,np.eye(h))+spatial/q['Rsharp']


def _rows(q, temporal_nodes):
    rows=q['rows']
    if len(rows)!=2 or any(type(j)is not int or not 0<=j<temporal_nodes for j,_,_ in rows):
        raise ValueError('each owned cell has exactly two chronological trace nodes')
    if rows[1][0]!=rows[0][0]+1:raise ValueError('original chronological cell incidence required')
    return [(j-1,complex(p),complex(d)) for j,p,d in rows if j!=0]


def chronological_clifford_blocks(quadrature, *, temporal_nodes, angular_derivatives, alpha):
    """Assemble every K/M diagonal and directed nearest-neighbor block.

    E may be the complete real PW matrix or the exact homogeneous active
    weight reduction. No field/source truncation is made by this function.
    """
    if type(temporal_nodes)is not int or temporal_nodes<2:raise ValueError('complete chronological node count required')
    h=np.asarray(angular_derivatives).shape[-1];d=6*h;n=temporal_nodes-1
    Kd=np.zeros((n,d,d),complex);Ku=np.zeros((n-1,d,d),complex);Kl=np.zeros_like(Ku)
    Md=np.zeros_like(Kd);Mu=np.zeros_like(Ku);Ml=np.zeros_like(Ku);I=np.eye(d)
    for q in quadrature:
        A,As=_angular_operators(q,angular_derivatives,alpha)
        w,ws,m=(complex(q[k])for k in('right_clock','reflected_clock','measure'))
        if 0 in(w,ws,q['R'],q['Rsharp']) or not np.isfinite([w,ws,m]).all():
            raise ValueError('both action clocks and original finite measure required')
        rows=_rows(q,temporal_nodes)
        for j,pj,dj in rows:
            left=dj*I/ws+pj*As
            for k,pk,dk in rows:
                value=m*left@(dk*I/w+pk*A);mass=m*pj*pk*I
                if j==k:Kd[j]+=value;Md[j]+=mass
                elif k==j+1:Ku[j]+=value;Mu[j]+=mass
                elif j==k+1:Kl[k]+=value;Ml[k]+=mass
                else:raise ArithmeticError('nonlocal cell entered a nearest-neighbor action')
    return dict(K_diagonal=Kd,K_upper=Ku,K_lower=Kl,M_diagonal=Md,M_upper=Mu,M_lower=Ml,
        temporal_free_nodes=n,angular_count=h,block_width=d,
        initial_only_right_restriction=True,final_natural_weak_row_retained=True,
        complex_measure_replaced_by_absolute_value=False,
        Hilbert_conjugate_substituted_for_independent_action_branch=False)


def chronological_pencil_blocks(blocks, spectral_parameter):
    z=complex(spectral_parameter)
    if not np.isfinite(z):raise ValueError('finite spectral point required')
    return tuple(blocks['K_'+k]-z*blocks['M_'+k] for k in('diagonal','upper','lower'))


def chronological_clifford_field_trace(quadrature, selected_inverse, *, temporal_nodes,
        angular_derivatives, alpha, trace_multiplicity=1):
    """Tr((K-zM)^-1 delta_field K) in all wall24 n0 coordinates.

    The coefficient tangent is the SAME material At_L/Ar/Ai/H coordinate
    in both analytic action branches. It is not conjugated. Metric/clock
    motion and nonconstant source images are separate variations.
    """
    h=np.asarray(angular_derivatives).shape[-1];d=6*h;n=temporal_nodes-1
    if len(selected_inverse['diagonal'])!=n or type(trace_multiplicity)is not int or trace_multiplicity<1:
        raise ValueError('same chronological inverse and exact spectator multiplicity required')
    result=np.zeros((n,24),complex)
    for q in quadrature:
        A,As=_angular_operators(q,angular_derivatives,alpha)
        X,Xs=(np.asarray(q[k],complex)for k in('vertices','vertices_sharp'))
        if X.shape!=(24,6,6)or Xs.shape!=X.shape:raise ValueError('full gauge and induced-H vertices required')
        w,ws,m=(complex(q[k])for k in('right_clock','reflected_clock','measure'))
        rows=_rows(q,temporal_nodes);local=np.zeros(24,complex);I=np.eye(d)
        for j,pj,dj in rows:
            left=dj*I/ws+pj*As
            for k,pk,dk in rows:
                if k==j:G=selected_inverse['diagonal'][j]
                elif k==j+1:G=selected_inverse['lower'][j]
                elif j==k+1:G=selected_inverse['upper'][k]
                else:raise ArithmeticError('nonlocal coefficient contact')
                right=dk*I/w+pk*A
                # Partial angular trace before the small spin contractions.
                t_left=(G@left).reshape(6,h,6,h).trace(axis1=1,axis2=3)
                t_right=(right@G).reshape(6,h,6,h).trace(axis1=1,axis2=3)
                local+=m*(pk*np.einsum('ab,cba->c',t_left,X)
                    +pj*np.einsum('ab,cba->c',t_right,Xs))
        for l,pl,_ in rows:result[l]+=trace_multiplicity*pl*local
    return result


def chronological_dense_blocks(blocks, *, prefix='K'):
    """Independent small-test reconstruction; production uses block solves."""
    D,U,L=(blocks[prefix+'_'+k]for k in('diagonal','upper','lower'))
    n,d,_=D.shape;out=np.zeros((n*d,n*d),complex)
    for j,A in enumerate(D):out[j*d:(j+1)*d,j*d:(j+1)*d]=A
    for j,(a,b)in enumerate(zip(U,L)):
        out[j*d:(j+1)*d,(j+1)*d:(j+2)*d]=a
        out[(j+1)*d:(j+2)*d,j*d:(j+1)*d]=b
    return out

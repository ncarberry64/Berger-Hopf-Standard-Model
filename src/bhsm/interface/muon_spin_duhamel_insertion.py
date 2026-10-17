"""Noncommuting Lorentz-generator insertions on a supplied boost background.

No physical connection source, initial Spin lift or state is selected.
The base/correction split preserves terms lost by subtracting near-I maps.
"""
from __future__ import annotations
import numpy as np
import math

LORENTZ_PAIRS=tuple((a,b)for a in range(5)for b in range(a+1,5))
FRAME_ORDER=('0','4','1','2','3')

def _gamma(gamma):
    G=np.asarray(gamma,complex)
    if G.ndim!=3 or G.shape[0]!=5 or G.shape[1]!=G.shape[2]or not np.isfinite(G).all():
        raise ValueError('Complete finite existing gamma set in0,4,1,2,3 order required')
    d=G.shape[1];eta=(1,-1,-1,-1,-1)
    defect=max(np.max(abs(G[a]@G[b]+G[b]@G[a]-(2*eta[a]*np.eye(d)if a==b else 0)))for a in range(5)for b in range(5))
    if defect>2e-11:raise ValueError('Cl(1,4) algebra required')
    return G,float(defect)

def _matrix_increment(A):
    term=A.copy();result=A.copy()
    for k in range(2,18):term=term@A/k;result+=term
    return result

def _tail_bound(A):
    norm=float(np.linalg.norm(A,'fro'))
    if norm==0:return 0.
    log_bound=norm+18*math.log(norm)-math.lgamma(19)
    return math.exp(log_bound)if log_bound<math.log(np.finfo(float).max)else float('inf')

def spin_duhamel_insertion_kernels(gamma,*,total_parameter,split_parameter,orientation):
    """Return every -P(t1,s)J_AB P(s,t0), including noncommuting channels.

    alpha(s)=integral(t0,s) omega/2; total=alpha(t1), split=total-2alpha(s).
    orientation is the original eps sheet sign. J_AB=GammaA GammaB/2;
    a general source is deltaOmega=sum_(A<B)deltaomega_AB J_AB.
    No source coefficient or field/domain derivative is assigned zero.
    """
    G,defect=_gamma(gamma)
    if orientation not in(-1,1)or not np.isfinite([total_parameter,split_parameter]).all():
        raise ValueError('Explicit finite real boost parameters and eps orientation required')
    if np.iscomplexobj(total_parameter)or np.iscomplexobj(split_parameter):
        raise ValueError('Real geometric boost background required')
    total,split=float(total_parameter),float(split_parameter);eps=orientation
    K=G[0]@G[1];J=np.array([G[a]@G[b]/2 for a,b in LORENTZ_PAIRS])
    anticommutes=np.array([len(set((a,b))&{0,1})==1 for a,b in LORENTZ_PAIRS])
    parameter=np.where(anticommutes,split,total)
    coefficient_J=-2*np.sinh(parameter/2)**2
    coefficient_KJ=eps*np.sinh(parameter)
    KJ=np.einsum('ij,ajk->aik',K,J)
    correction=coefficient_J[:,None,None]*J+coefficient_KJ[:,None,None]*KJ
    base=-J;kernel=base+correction
    Aleft=-eps*(total+split)*K/2;Aright=-eps*(total-split)*K/2
    left=_matrix_increment(Aleft);right=_matrix_increment(Aright)
    # Literal finite-matrix diagnostic retains all supplied tiny gamma entries.
    literal_correction=-(np.einsum('ij,ajk->aik',left,J)
        +np.einsum('aij,jk->aik',J,right)
        +np.einsum('ij,ajk,kl->ail',left,J,right))
    return dict(frame_order=FRAME_ORDER,generator_pairs=LORENTZ_PAIRS,
        generators=J,background_boost_generator=K,
        generator_anticommutes_with_boost=anticommutes,
        stable_kernel_base=base,stable_kernel_correction=correction,stable_kernel=kernel,
        correction_coefficient_J=coefficient_J,correction_coefficient_KJ=coefficient_KJ,
        literal_finite_gamma_kernel_correction=literal_correction,
        literal_minus_Clifford_identity_correction=literal_correction-correction,
        literal_diagnostic_Taylor_order=17,
        literal_increment_remainder_bounds=(_tail_bound(Aleft),_tail_bound(Aright)),
        source_gamma_Clifford_defect=defect,
        physical_connection_source_selected=False,initial_physical_Spin_lift=None)

def spin_endpoint_and_frame_kernels(gamma,*,parallel,initial_connection,final_connection):
    """Moving times and independent frame variations, without selecting data.

    Frame coordinates are L_i=B_i^-1 delta B_i=sum l_i^AB J_AB.
    For P_ad=B1^-1 P_amb B0 they give -L1 P_ad+P_ad L0.
    The returned P also left-multiplies an arbitrary delta(initial Spin lift).
    """
    G,_=_gamma(gamma);d=G.shape[1]
    P,A0,A1=(np.asarray(a,complex)for a in(parallel,initial_connection,final_connection))
    if any(a.shape!=(d,d)or not np.isfinite(a).all()for a in(P,A0,A1)):
        raise ValueError('Complete finite same-carrier parallel/endpoint connections required')
    J=np.array([G[a]@G[b]/2 for a,b in LORENTZ_PAIRS])
    return dict(generator_pairs=LORENTZ_PAIRS,
        moving_initial_time=P@A0,moving_final_time=-A1@P,
        independent_initial_frame=np.einsum('ij,ajk->aik',P,J),
        independent_final_frame=-np.einsum('aij,jk->aik',J,P),
        initial_physical_lift_variation_left_multiplier=P,
        physical_initial_frame_or_lift_selected=False)

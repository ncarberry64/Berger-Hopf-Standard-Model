"""Signed action response on the reset-admissible canonical tangent.

Algebraic Ly rows enter once through the full Legendre/Gauss elimination.
Position trace rows are constraints; energy and temporal-dual rows remain
natural force readouts. The prescribed normal is a computational trial.
"""
from __future__ import annotations
import numpy as np
from .muon_complex_paired_normal_action import _balanced_solver


def canonical_variation_embedding(hessian,x_indices,v_indices,y_indices,frames,*,
        source_gradient=None,hessian_time_first=None,source_gradient_time_first=None):
    """Map independent (delta x,delta p) into original (delta x,v,y).

    [Lvv Lvy; Lyv Lyy] phase + F.T rho =
    [delta p-Lvx delta x-g_v,s; -Lyx delta x-g_y,s].
    The reaction rho records canonical compatibility instead of deleting
    any Gauss row. Its zero is imposed by the subsequent trial KKT.
    """
    H=np.asarray(hessian,complex);xi=np.asarray(x_indices,int);vi=np.asarray(v_indices,int);yi=np.asarray(y_indices,int)
    n=len(xi);phase=np.r_[vi,yi];F=np.asarray(frames,complex);d=len(phase);dim=len(H)
    if len(vi)!=n or H.shape!=(dim,dim)or F.ndim!=2 or F.shape[1]!=d:
        raise ValueError('complete original coordinates and named phase frames required')
    Gs=np.zeros(dim,complex)if source_gradient is None else np.asarray(source_gradient,complex)
    Ht=np.zeros_like(H)if hessian_time_first is None else np.asarray(hessian_time_first,complex)
    Gst=np.zeros(dim,complex)if source_gradient_time_first is None else np.asarray(source_gradient_time_first,complex)
    D=H[np.ix_(phase,phase)];Dt=Ht[np.ix_(phase,phase)]
    K=np.block([[D,F.T],[F,np.zeros((len(F),len(F)),complex)]]);solve,balance=_balanced_solver(K)
    B=np.zeros((len(K),2*n),complex);B[:d,:n]=-H[np.ix_(phase,xi)];B[:n,n:]=np.eye(n)
    rhs=np.r_[-Gs[phase],np.zeros(len(F))];solutions=solve(B);offset=solve(rhs)
    embed=np.zeros((dim,2*n),complex);embed[np.ix_(xi,np.arange(n))]=np.eye(n);embed[phase]=solutions[:d]
    source=np.zeros(dim,complex);source[phase]=offset[:d]
    Kt=np.zeros_like(K);Kt[:d,:d]=Dt;Bt=np.zeros_like(B);Bt[:d,:n]=-Ht[np.ix_(phase,xi)]
    solution_t=solve(Bt-Kt@solutions);offset_t=solve(np.r_[-Gst[phase],np.zeros(len(F))]-Kt@offset)
    embed_t=np.zeros_like(embed);embed_t[phase]=solution_t[:d];source_t=np.zeros(dim,complex);source_t[phase]=offset_t[:d]
    return dict(original_phase_saddle=K,canonical_rhs_map=B,source_rhs=rhs,
        canonical_phase_solution_map=solutions,canonical_phase_source_solution=offset,
        embedding=embed,source_embedding=source,compatibility_map=solutions[d:],compatibility_source=offset[d:],
        embedding_time_first=embed_t,source_embedding_time_first=source_t,
        compatibility_time_first=solution_t[d:],compatibility_source_time_first=offset_t[d:],
        original_embedding_rows=K@solutions-B,original_source_rows=K@offset-rhs,
        original_embedding_time_rows=K@solution_t+Kt@solutions-Bt,
        original_source_time_rows=K@offset_t+Kt@offset-np.r_[-Gst[phase],np.zeros(len(F))],
        x_indices=xi,v_indices=vi,y_indices=yi,phase_indices=phase,
        source_gradient=Gs,source_gradient_time_first=Gst,hessian_time_first=Ht,
        frames=F,full_Lyy_retained=True,balanced_condition=float(np.linalg.cond(balance)))


def signed_reset_constrained_trial(hessian,embedding,kinematic_trace_rows,normal_row,static_frames,*,normal_amplitude=1,
        kinematic_trace_source=None,normal_trace_source=0):
    """Full signed quadratic action KKT, leaving natural force rows free.

    rho=0 enforces original phase/Gauss compatibility. No duplicate Ly
    borders, Euclidean minimum norm or forced-zero natural traction occur.
    """
    H=np.asarray(hessian,complex);a=embedding;R=a['embedding'];s=a['source_embedding']
    B=np.asarray(kinematic_trace_rows,complex);N=np.asarray(normal_row,complex).reshape(1,-1);C=np.asarray(static_frames,complex)
    bs=np.zeros(len(B),complex)if kinematic_trace_source is None else np.asarray(kinematic_trace_source,complex)
    if bs.shape!=(len(B),):raise ValueError('direct trace source must preserve every original trace row')
    E=np.vstack((B@R,a['compatibility_map'],C@R,N@R))
    rhs=np.r_[-B@s-bs,-a['compatibility_source'],-C@s,normal_amplitude-(N@s)[0]-normal_trace_source]
    Q=R.T@H@R;force=R.T@(H@s+a['source_gradient'])
    K=np.block([[Q,E.T],[E,np.zeros((len(E),len(E)),complex)]]);solve,balance=_balanced_solver(K)
    fullrhs=np.r_[-force,rhs];solution=solve(fullrhs);q=solution[:R.shape[1]];delta=R@q+s
    return dict(canonical_coordinates=q,original_master_direction=delta,
        signed_canonical_action_Hessian=Q,canonical_source_force=force,
        original_KKT=K,original_rhs=fullrhs,solution=solution,original_rows=K@solution-fullrhs,
        constraint_rows=E,constraint_rhs=rhs,constraint_residual=E@q-rhs,
        original_kinematic_trace_rows=B@delta+bs,direct_kinematic_trace_source=bs,
        original_canonical_compatibility=a['compatibility_map']@q+a['compatibility_source'],
        named_static_frame_rows=C@delta,normal_amplitude=(N@delta)[0]+normal_trace_source,
        natural_normal_KKT_reaction=solution[-1],
        signed_action_quadratic=delta@H@delta,
        signed_action_source_pairing=a['source_gradient']@delta,
        balanced_condition=float(np.linalg.cond(balance)),natural_traction_rows_constrained_to_zero=False)


def canonical_variation_evolution(hessian,embedding,trial):
    """Actual canonical variational vector and original DAE audit at a germ."""
    a=embedding;H=np.asarray(hessian,complex);q=trial['canonical_coordinates'];delta=trial['original_master_direction']
    x,v,y=a['x_indices'],a['v_indices'],a['y_indices'];Gs=a['source_gradient']
    qdot=np.r_[delta[v],H[x]@delta+Gs[x]]
    direction_rate=a['embedding']@qdot+a['embedding_time_first']@q+a['source_embedding_time_first']
    Ht=a['hessian_time_first'];Gst=a['source_gradient_time_first'];F=a['frames']
    momentum_dot=H[v]@direction_rate+Ht[v]@delta+Gst[v]
    algebraic_dot=H[y]@direction_rate+Ht[y]@delta+Gst[y]
    compatibility_dot=a['compatibility_map']@qdot+a['compatibility_time_first']@q+a['compatibility_source_time_first']
    return dict(canonical_coordinate_time_first=qdot,original_master_direction_time_first=direction_rate,
        original_position_rate_identity=direction_rate[x]-delta[v],
        original_momentum_rate_identity=momentum_dot-qdot[len(x):],
        original_algebraic_time_first=algebraic_dot,named_frame_time_first=F@direction_rate[a['phase_indices']],
        original_compatibility_time_first=compatibility_dot,
        original_algebraic_source_rows=H[y]@delta+Gs[y],
        source_and_embedding_time_motion_count=1,
        canonical_position_force_not_transformed_or_fitted=True)

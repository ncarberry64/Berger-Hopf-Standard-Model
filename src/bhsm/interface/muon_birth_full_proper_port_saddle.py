"""Full same-action birth phase applications on supplied proper trace rows.

This constructs numerical proper-port paths and an independent analytic
action test. It does not identify the instantaneous action with its
chronological response, select an exterior domain, or replace original
reset equations. Geometry, gauge, scalar and multiplier rows stay intact.
"""
from __future__ import annotations

import numpy as np
from flint import ctx, acb_mat
from .muon_stored_admission_correction import _matrix, _upper
from .muon_stored_fiber_canonical_tangent import _rows, _cat, _split


def full_proper_port_saddle_action(phase_Hessian, proper_trace, named_frames,
        common_ports, temporal_dual, *, precision_bits=192):
    """Solve [D E.T F.T;E 0 0;F 0 0] on all original phase rows.

    E is the COMPLETE supplied proper-coordinate trace, including any
    geometry contact. The right-hand side sets numerical common trial
    amplitudes. It supplies neither environmental data nor physical
    inertia normalization. The independent action adjoint uses transpose.
    """
    D,E,F,C,t=map(lambda x:np.asarray(x,complex),
        (phase_Hessian,proper_trace,named_frames,common_ports,temporal_dual))
    n=len(D);ne=len(E);nf=len(F)
    if (D.shape!=(n,n) or E.shape!=(ne,n) or F.shape!=(nf,n)
            or C.ndim!=2 or C.shape[0]!=ne or t.shape!=(n,)
            or not all(np.isfinite(x).all() for x in (D,E,F,C,t))):
        raise ValueError('full original phase action, complete proper traces, named frames and same temporal target required')
    if precision_bits!=192:
        raise ValueError('reuse the retained 192-bit stored-coefficient application; no precision campaign')
    old=ctx.prec;ctx.prec=precision_bits
    try:
        K=np.block([[D,E.T,F.T],
            [E,np.zeros((ne,ne+nf),complex)],
            [F,np.zeros((nf,ne+nf),complex)]])
        Q=np.vstack((np.zeros((n,C.shape[1]),complex),C,np.zeros((nf,C.shape[1]),complex)))
        target=np.r_[t,np.zeros(ne+nf,complex)]
        KK,QQ,tt=_matrix(K),_matrix(Q),_matrix(target)
        X=KK.solve(QQ);alpha=KK.transpose().solve(tt)
        L=_rows(X,0,n);ports=_rows(X,n,n+ne);frames=_rows(X,n+ne,n+ne+nf)
        a=_rows(alpha,0,n);ap=_rows(alpha,n,n+ne);af=_rows(alpha,n+ne,n+ne+nf)
        phase=_matrix(D)*L+_matrix(E.T)*ports+_matrix(F.T)*frames
        raw=_matrix(D)*L+_matrix(E.T)*ports
        left=_matrix(D.T)*a+_matrix(E.T)*ap+_matrix(F.T)*af-_matrix(t)
        raw_left=_matrix(D.T)*a+_matrix(E.T)*ap-_matrix(t)
        natural=_matrix(t).transpose()*L;dual=alpha.transpose()*QQ
        values=dict(solution=X,phase_lifts=L,proper_port_reactions=ports,named_frame_reactions=frames,
            analytic_adjoint=alpha,analytic_phase_test=a,analytic_proper_port_reactions=ap,
            analytic_named_frame_reactions=af,
            original_phase_rows=phase,original_phase_without_named_reactions=raw,
            original_named_frame_reaction_rows=_matrix(F.T)*frames,
            original_proper_port_rows=_matrix(E)*L-_matrix(C),
            original_named_frame_rows=_matrix(F)*L,
            original_full_saddle_rows=KK*X-QQ,
            original_analytic_adjoint_phase_rows=left,
            original_analytic_adjoint_without_named_reactions=raw_left,
            original_analytic_adjoint_named_frame_reaction_rows=_matrix(F.T)*af,
            original_analytic_adjoint_proper_port_rows=_matrix(E)*a,
            original_analytic_adjoint_named_frame_rows=_matrix(F)*a,
            original_full_transpose_rows=KK.transpose()*alpha-tt,
            natural_cotangent=natural,independent_transpose_natural_cotangent=dual,
            natural_literal_pairing_rows=natural-dual)
        arrays={}
        for name,value in values.items():arrays[name+'_high'],arrays[name+'_low']=_split(value)
        arrays.update(saddle=K,right_hand_side=Q,temporal_target=target,
            phase_Hessian=D,proper_trace=E,named_frames=F,common_port_map=C)
        return dict(arrays=arrays,
            original_phase_rows_upper=_upper(phase),
            original_phase_without_named_reactions_upper=_upper(raw),
            named_frame_reaction_upper=_upper(values['original_named_frame_reaction_rows']),
            proper_port_rows_upper=_upper(values['original_proper_port_rows']),
            named_frame_rows_upper=_upper(values['original_named_frame_rows']),
            independent_transpose_rows_upper=_upper(values['original_full_transpose_rows']),
            natural_pairing_rows_upper=_upper(values['natural_literal_pairing_rows']),
            all_original_action_and_named_frame_rows_retained=True,
            analytic_transpose_not_Hilbert_adjoint=True,
            original_reset_natural_equations_replaced=False,
            physical_mode_environment_or_retarded_domain_selected=False)
    finally:ctx.prec=old

"""Same-action full Legendre/constraint trace and analytic source dual.

The phase coordinates include both velocities and algebraic fields.
No Ly_y block is suppressed. Named frame reactions are exported, rather
than deleting small Hessian eigenvectors or identifying a coefficient
Gram with physical inertia. An off-shell application stays off shell.
"""
from __future__ import annotations
import numpy as np


def _array(value, shape, name):
    a = np.asarray(value, complex)
    if a.shape != shape or not np.isfinite(a).all():
        raise ValueError('complete finite '+name+' required')
    return a


def _solve(matrix, rhs):
    # Independent row/column scales preserve the original signed matrix.
    row = 1/np.maximum(np.max(abs(matrix), axis=1), np.finfo(float).tiny)
    col = 1/np.maximum(np.max(abs(row[:, None]*matrix), axis=0), np.finfo(float).tiny)
    balanced = row[:, None]*matrix*col[None, :]
    if rhs.ndim == 1:
        answer = col*np.linalg.solve(balanced, row*rhs)
    else:
        answer = col[:, None]*np.linalg.solve(balanced, row[:, None]*rhs)
    return answer, row, col


def coupled_phase_trace_projection(D, trace_map, named_frames, temporal_dual,
                                   common_trace_map=None):
    """Apply the full fixed-position action to each prescribed trace.

    With phase=(delta v,delta y), E=[B,0], and named frames F:
        [D E.T F.T; E 0 0; F 0 0] X = [0; I; 0].
    Consequently all original algebraic rows contain Lyv delta v AND
    Lyy delta y, with the named reactions retained. The face is X.T theta,
    where theta=(2 Pi_parent-Pi_graph,0_y), and its adjoint uses transpose.
    This is neither a physical mode selector nor a stationary-base solve.
    """
    D = np.asarray(D, complex)
    if D.ndim != 2 or D.shape[0] != D.shape[1]:
        raise ValueError('full square phase Hessian required')
    n = len(D)
    E, F = np.asarray(trace_map, complex), np.asarray(named_frames, complex)
    if E.ndim != 2 or F.ndim != 2 or E.shape[1] != n or F.shape[1] != n:
        raise ValueError('same-domain trace and named frame maps required')
    nt, nf = len(E), len(F)
    D = _array(D, (n,n), 'phase Hessian')
    E, F = _array(E, (nt,n), 'trace map'), _array(F, (nf,n), 'named frames')
    theta = _array(temporal_dual, (n,), 'analytic temporal dual')
    common = np.eye(nt) if common_trace_map is None else np.asarray(common_trace_map, complex)
    if common.ndim != 2 or common.shape[0] != nt or not np.isfinite(common).all():
        raise ValueError('literal common trace map required')
    Q = np.vstack((E,F))
    K = np.block([[D,Q.T],[Q,np.zeros((nt+nf,nt+nf),complex)]])
    rhs = np.zeros((len(K),nt),complex); rhs[n:n+nt] = np.eye(nt)
    X, row, col = _solve(K,rhs)
    dual_rhs = np.r_[theta,np.zeros(nt+nf,complex)]
    adjoint, _, _ = _solve(K.T,dual_rhs)
    L, port, frame = X[:n], X[n:n+nt], X[n+nt:]
    original = D@L+E.T@port+F.T@frame
    cotangent = common.T@(L.T@theta)
    return dict(saddle=K, saddle_rhs=rhs, solution=X, phase_lift=L,
        port_reactions=port, frame_reactions=frame, adjoint=adjoint,
        analytic_temporal_dual=theta, common_trace_map=common,
        trace_map=E, named_frames=F, phase_Hessian=D,
        phase_count=n, trace_count=nt, named_frame_count=nf,
        original_phase_rows=original, trace_rows=E@L-np.eye(nt),
        named_frame_rows=F@L, saddle_rows=K@X-rhs,
        analytic_adjoint_rows=K.T@adjoint-dual_rhs,
        six_or_general_trace_cotangent=L.T@theta,
        common_trace_cotangent=cotangent, reduced_action=L.T@D@L,
        reduced_action_border_identity=L.T@D@L+port,
        row_scale=row, column_scale=col,
        algebraic_self_Hessian_retained=True,
        raw_action_dual_conjugated=False, numerical_eigenvectors_deleted=0,
        physical_stationarity_or_normalization_claimed=False)


def coupled_phase_trace_parameter(application, D_parameter,
        temporal_dual_parameter, trace_parameter=None, frame_parameter=None):
    """Differentiate the SAME signed saddle, trace, frames and face dual.

    d(X.T theta)=X.T dtheta-adjoint.T dK X. The full dLyy belongs in
    dD. State motion also varies trace/frame maps and must supply dE,dF;
    a held-state tension coefficient has dE=dF=0 by its action provenance.
    """
    a=application; n,nt,nf=(a[k]for k in('phase_count','trace_count','named_frame_count'))
    dD=_array(D_parameter,(n,n),'full phase Hessian parameter')
    dtheta=_array(temporal_dual_parameter,(n,),'temporal dual parameter')
    dE=np.zeros((nt,n),complex)if trace_parameter is None else _array(trace_parameter,(nt,n),'trace parameter')
    dF=np.zeros((nf,n),complex)if frame_parameter is None else _array(frame_parameter,(nf,n),'frame parameter')
    dQ=np.vstack((dE,dF));dK=np.block([[dD,dQ.T],[dQ,np.zeros((nt+nf,nt+nf),complex)]])
    rhs=-dK@a['solution'];dX,_,_=_solve(a['saddle'],rhs)
    dual_rhs=np.r_[dtheta,np.zeros(nt+nf,complex)]-dK.T@a['adjoint']
    dadjoint,_,_=_solve(a['saddle'].T,dual_rhs)
    dual_derivative=a['common_trace_map'].T@(
        a['phase_lift'].T@dtheta-a['adjoint']@dK@a['solution'])
    direct=a['common_trace_map'].T@(
        dX[:n].T@a['analytic_temporal_dual']+a['phase_lift'].T@dtheta)
    return dict(saddle_parameter=dK, solution_parameter=dX,
        phase_lift_parameter=dX[:n], adjoint_parameter=dadjoint,
        common_trace_cotangent_parameter=dual_derivative,
        direct_cotangent_parameter=direct,
        cotangent_dual_identity_rows=dual_derivative-direct,
        parameter_saddle_rows=a['saddle']@dX+dK@a['solution'],
        parameter_adjoint_rows=a['saddle'].T@dadjoint-dual_rhs,
        algebraic_self_Hessian_parameter_retained=True,
        raw_action_dual_conjugated=False,
        held_trace_and_frame_maps=trace_parameter is None and frame_parameter is None,
        physical_mode_or_parameter_value_selected=False)

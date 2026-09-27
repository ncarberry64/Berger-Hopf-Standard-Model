"""Signed fixed-environment seam jets; conditional algebra, not a new law.

All matrices are real Arb matrices in a caller-owned common frame. Parameters
are seam/child directions with external state held fixed. Native reaction jets
must include evaluation-point/normal motion. No missing jet defaults to zero.
The pullback and cotangent conventions are those of
full_field_moving_reset_graph_decision.first_moving_domain_variation and
gauge_connection_reset_bundle_lift_adjudication.weighted_cotangent_momentum_map.
"""
from flint import arb_mat


def _column(a, k):
    return arb_mat([[a[i,k]] for i in range(a.nrows())])


def _columns(items):
    return arb_mat([[a[i,0] for a in items] for i in range(items[0].nrows())])


def pullback_first_jet(value, native_jet, frame, frame_jet):
    """D(P r)=DP r+P Dr, retaining sampling and frame/density terms."""
    if value.ncols()!=1 or native_jet.nrows()!=value.nrows():
        raise ValueError('native value and jet dimensions differ')
    if len(frame_jet)!=native_jet.ncols() or not frame_jet:
        raise ValueError('an explicit frame derivative is required per direction')
    if any((d.nrows(),d.ncols())!=(frame.nrows(),frame.ncols()) for d in frame_jet):
        raise ValueError('frame derivative has wrong shape')
    return frame*value, _columns([frame*_column(native_jet,k)+d*value for k,d in enumerate(frame_jet)])


def cotangent_first_jet(momentum, native_jet, L, dL, We, dWe, Ws, dWs):
    """Differentiate Ws p_seam = L^-T We p_native without discarding weights.

L maps native configuration variations to seam configuration variations.
Native momentum changes include material sampling even though delta e=0.
"""
    n=L.nrows();d=native_jet.ncols()
    if L.ncols()!=n or momentum.nrows()!=n or momentum.ncols()!=1:
        raise ValueError('square common configuration frame and momentum required')
    if any(len(x)!=d for x in (dL,dWe,dWs)) or d==0:
        raise ValueError('all three frame/measure jets must be explicit')
    lifted=L.transpose().solve(We*momentum)
    p=Ws.solve(lifted)
    cols=[]
    for k in range(d):
        rhs=dWe[k]*momentum+We*_column(native_jet,k)-dL[k].transpose()*lifted
        cols.append(Ws.solve(L.transpose().solve(rhs)-dWs[k]*p))
    return p,_columns(cols)


def on_shell_reaction_jet(Hii, Hiq, HiSigma, Hqi, Hqq, HqSigma, dq, dSigma):
    """D(dW/dq) after eliminating only owned interior stationary variables.

All Hessian blocks must come from the SAME action/domain at fixed e0.
This retains the interior response; fixed exterior data do not freeze it.
"""
    if dq.ncols()!=dSigma.ncols():
        raise ValueError('trace and seam jets require the same parameter keys')
    interior=-Hii.solve(Hiq*dq+HiSigma*dSigma)
    return Hqq*dq+HqSigma*dSigma+Hqi*interior,interior


def stack_seven(trace, momentum, flux):
    """Only a typed 3+2+2 response is accepted, in shared parameter columns."""
    if [a.nrows() for a in (trace,momentum,flux)]!=[3,2,2]:
        raise ValueError('required row ownership is 3 trace + 2 momentum + 2 flux')
    if len({a.ncols() for a in (trace,momentum,flux)})!=1:
        raise ValueError('response groups must share parameter keys')
    return arb_mat(trace.tolist()+momentum.tolist()+flux.tolist())


def compose_weak_feedback(affine_value, fixed_rho_state_jet, state_jet, rho_jet):
    """D nu=(D_Y nu)|rho DY + nu_rho D rho for the frozen weak owner.

The caller first evaluates its stored affine-in-rho state derivative at the
owned rho value. rho_jet is a material/seam derivative, not an external input.
"""
    if affine_value.ncols()!=3 or rho_jet.nrows()!=2:
        raise ValueError('expected constant and two held-fixed conormal coefficients')
    if fixed_rho_state_jet.nrows()!=affine_value.nrows():
        raise ValueError('state derivative and affine output dimensions differ')
    if state_jet.ncols()!=rho_jet.ncols():
        raise ValueError('seam and state directions must share keys')
    coupling=arb_mat([[affine_value[i,1],affine_value[i,2]] for i in range(affine_value.nrows())])
    return fixed_rho_state_jet*state_jet+coupling*rho_jet


def solve_seven_balance(child_p, child_q, env_p, env_q, orientation, Tp, Tq):
    """Solve the full signed seven-row balance in a declared p/q frame.

Owner signs are explicit: R=R_child+orientation*R_env. Both env_p and env_q
are required because a slaved q correction also moves the seam. The return
is conditional on those supplied owners; dimensions alone confer no authority.
"""
    if any(a.nrows()!=7 for a in (child_p,child_q,env_p,env_q)):
        raise ValueError('seven owner-bound rows required')
    if any(a.ncols()!=7 for a in (child_q,env_q)):
        raise ValueError('seven reaction coordinates required')
    if child_p.ncols()!=env_p.ncols() or Tp.ncols()!=child_p.ncols():
        raise ValueError('shared p columns required')
    if Tq.ncols()!=7 or Tq.nrows()!=Tp.nrows():
        raise ValueError('state p/q lifts do not agree')
    if (orientation.nrows(),orientation.ncols())!=(7,7):
        raise ValueError('explicit owner orientation required')
    Kp=child_p+orientation*env_p
    Kq=child_q+orientation*env_q
    q=-Kq.solve(Kp)
    tangent=Tp+Tq*q
    return dict(Kp=Kp,Kq=Kq,reactions=q,tangent=tangent,replay=Kp+Kq*q)

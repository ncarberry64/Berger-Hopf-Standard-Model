"""Advanced weak boundary test for the retained central Maxwell probe.

This computes the actual adjoint boundary test on the source support.  It
does not select a physical mode or replace the full interacting action.
Time reversal changes the gyro/shift sign; it does not change the metric,
normal spatial form, radial stiffness or physical charge normalization.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp, simpson
from scipy.linalg import cho_factor, cho_solve

from .muon_parent_retarded_hypercharge import compact_trace_pulse


def boundary_probe_on_support(M,N,K,*,source_duration,time_steps=1024,
                              reversed_time=False,rtol=2e-11,atol=2e-13):
    """Solve the finite action on [0,D] with the actual fixed trace g.

    For the advanced solution u=D-t, N_u=-N_t, so the gyro changes sign.
    The compact sin^4 trace obeys g(D-u)=g(u).  Past-zero data in u are
    final-zero data in t; neither is a statement about the base fields.
    """
    M,N,K=(np.asarray(x,float) for x in (M,N,K))
    if (M.ndim!=2 or M.shape[0]!=M.shape[1] or N.shape!=M.shape or
            K.shape!=M.shape or not all(np.isfinite(x).all() for x in (M,N,K)) or
            source_duration<=0 or type(time_steps)is not int or time_steps<8):
        raise ValueError('finite common square action matrices and resolved positive source interval required')
    n=len(M)-1
    if n<1:raise ValueError('interior and independent wall trace required')
    N_used=-N if reversed_time else N
    gyro=N_used.T-N_used
    factor=cho_factor(M[:n,:n])
    solve=lambda x:cho_solve(factor,x)
    A=np.block([[np.zeros((n,n)),np.eye(n)],
                [-solve(K[:n,:n]),-solve(gyro[:n,:n])]])
    forcing=-solve(np.column_stack((K[:n,n],gyro[:n,n],M[:n,n])))
    def rhs(t,y):
        return A@y+np.r_[np.zeros(n),forcing@np.asarray(compact_trace_pulse(t,source_duration))]
    solution=solve_ivp(rhs,(0,source_duration),np.zeros(2*n),method='DOP853',
        rtol=rtol,atol=atol,max_step=source_duration/time_steps,dense_output=True)
    if not solution.success:raise ArithmeticError(solution.message)
    times=np.linspace(0,source_duration,2*time_steps+1)
    y=solution.sol(times).T
    g,dg,ddg=compact_trace_pulse(times,source_duration)
    state=np.column_stack((y[:,:n],g))
    velocity=np.column_stack((y[:,n:],dg))
    acc=np.column_stack(((y@A.T)[:,n:]+np.column_stack((g,dg,ddg))@forcing.T,ddg))
    residual=acc@M.T+velocity@gyro.T+state@K.T
    reaction=residual[:,-1]
    # Coordinates are saved in the reversed u-time when reversed_time=True.
    # The original-time advanced coefficients are explicitly saved too.
    original_state=state[::-1] if reversed_time else state
    original_velocity=-velocity[::-1] if reversed_time else velocity
    return dict(times=times,state=state,velocity=velocity,acceleration=acc,
        original_time_state=original_state,original_time_velocity=original_velocity,
        original_time_acceleration=acc[::-1] if reversed_time else acc,
        reaction=reaction,trace=g,source_duration=float(source_duration),
        boundary_trace_contraction=float(simpson(g*reaction,x=times)),
        interior_residual_max=float(np.max(abs(residual[:,:n]))),
        M=M,N=N_used,K=K,reversed_time=reversed_time,
        initial_perturbation='zero state and momentum in the integration-time coordinate',
        original_time_condition='zero terminal perturbation' if reversed_time else 'zero initial perturbation',
        source_scope='CONTROL_ONLY same compact fixed wall trace, support interval only',
        numerical_integrator=dict(method='DOP853',rtol=rtol,atol=atol,evaluations=solution.nfev),
        physical_mode_selected=False,physical_Pauli_evaluated=False)

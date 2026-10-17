"""Continue the actual sourced magnetic birth through the reached field graph.

The published fixed-q trace and canonical-dual equations are extended in
this one common numerical angular/body frame.  This is the corresponding
pointwise graph restriction, not a global worldvolume/reset theorem.
Outgoing velocities and At are derived afresh from the outgoing action.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp,simpson
from scipy.linalg import cho_factor,cho_solve
from .muon_parent_maxwell_full_retarded import _reduced_at


def magnetic_birth_continuation_application(form,initial_state,*,time_steps=64,rtol=2e-9,atol=2e-11):
    """Solve the actual reached eight-column Euler/Gauss source problem.

    The outgoing constant plateau starts from the incoming birth canonical
    state.  Its normalization and moving full400 source actions are retained.
    The exported H80 response is newly solved on those actions; an old
    response outside their span is never substituted.
    """
    if type(time_steps) is not int or time_steps<16:
        raise ValueError('resolved source-response mesh required')
    n=400;k=8;T,D=form['final_time'],form['duration']
    def rhs(t,state):
        current_state=np.asarray(state).reshape(2*n,k)
        x,p=current_state[:n],current_state[n:]
        f=_reduced_at(form,t);mass,mixed,stiffness=(f[a] for a in ('M','B','K'))
        g,gd,_=(1.,0.,0.)
        velocity=cho_solve(cho_factor(mass[:n,:n]),
            p-mixed[:n,:n].T@x-g*mixed[n:,:n].T-gd*mass[:n,n:])
        force=mixed[:n,:n]@velocity+g*stiffness[:n,n:]+gd*mixed[:n,n:]+stiffness[:n,:n]@x
        return np.r_[velocity,force].ravel()
    initial=np.asarray(initial_state,float)
    if initial.shape!=(2*n,k) or not np.isfinite(initial).all():raise ValueError("complete actual incoming canonical x/p source state required")
    sol=solve_ivp(rhs,(0,T),initial.ravel(),method='DOP853',
        rtol=rtol,atol=atol,max_step=D/time_steps,dense_output=True)
    if not sol.success:raise ArithmeticError('reached action solve failed: '+sol.message)
    t=np.linspace(0,T,3*time_steps+1)
    states=sol.sol(t).T.reshape(-1,2*n,k)
    velocities=np.array([rhs(a,b.ravel()).reshape(2*n,k)[:n] for a,b in zip(t,states)])
    Ats=[];Gauss=[];Gauss_rel=[];reactions=[];work=[];quadratic=[];scalar_work=[];physical_traces=[];physical_trace_rates=[]
    for a,state,v in zip(t,states,velocities):
        f=_reduced_at(form,a);g,gd,_=(1.,0.,0.)
        z=np.r_[state[:n],g*np.eye(k)];zd=np.r_[v,gd*np.eye(k)]
        y=f['At_value_map']@z+f['At_velocity_map']@zd;Ats.append(y)
        parts=(f['Gauss_matrix']@y,f['Gauss_value_row']@z,f['Gauss_velocity_row']@zd)
        Gauss.append(sum(parts));Gauss_rel.append(float(np.max(abs(sum(parts)))/(1+sum(np.max(abs(a)) for a in parts))))
        full=np.r_[y,z];full_dot=np.r_[np.zeros_like(y),zd]
        G0z,G0v,G1z,G1v=form['gauge_weak_rows'](a)
        reactions.append(g*(G0z@full+G0v@full_dot)+gd*(G1z@full+G1v@full_dot))
        mass,mixed,stiffness=(f[b] for b in ('M','B','K'))
        momentum=mass@zd+mixed.T@z
        work.append(-gd*momentum[n:]-g*(mixed[n:]@zd+stiffness[n:]@z))
        quadratic.append(zd.T@mass@zd+z.T@mixed@zd+zd.T@mixed.T@z+z.T@stiffness@z)
        sm,sb,sk=(form['intrinsic_'+b](a) for b in ('raw_M','raw_B','raw_K'))
        scalar_work.append(-gd*(sm@zd+sb.T@z)[n:]-g*(sb[n:]@zd+sk[n:]@z))
        Q,Qt=form['source_map'](a),form['source_rate_map'](a)
        physical_traces.append(g*Q);physical_trace_rates.append(gd*Q+g*Qt)
    readout=np.zeros((k,2*n));readout[:,:n]=form['intrinsic_raw_K'](T)[n:,:n]
    def adjoint_rhs(a,state):
        state=state.reshape(2*n,k);f=_reduced_at(form,a)
        mass,mixed,stiffness=(f[b][:n,:n] for b in ('M','B','K'))
        v=cho_solve(cho_factor(mass),state[:n]+mixed.T@state[n:])
        return np.r_[mixed@v-stiffness.T@state[n:],-v].ravel()
    adj=solve_ivp(adjoint_rhs,(T,0),readout.T.ravel(),method='DOP853',
        rtol=rtol,atol=atol,max_step=D/time_steps,dense_output=True)
    if not adj.success:raise ArithmeticError('reached adjoint solve failed: '+adj.message)
    adjoints=adj.sol(t).T.reshape(-1,2*n,k)
    contraction=adjoints[0].T@initial+simpson(np.array([a.T@rhs(b,np.zeros(2*n*k)).reshape(2*n,k)
        for a,b in zip(adjoints,t)]),x=t,axis=0)
    output=readout@states[-1]
    endpoint=states[-1,:n].T@states[-1,n:]-states[0,:n].T@states[0,n:]
    ff=_reduced_at(form,T);gz,gdt,_=(1.,0.,0.)
    final_z=np.r_[states[-1,:n],gz*np.eye(k)];final_zd=np.r_[velocities[-1],gdt*np.eye(k)]
    final_source_momentum=(ff['M']@final_zd+ff['B'].T@final_z)[n:]
    work=simpson(np.array(work),x=t,axis=0)
    action_boundary=endpoint-simpson(np.array(quadratic),x=t,axis=0)
    return dict(times=t,state=states,velocity=velocities,A_tau=np.array(Ats),
        Gauss_residual=np.array(Gauss),Gauss_relative_maximum=max(Gauss_rel),
        gauge_Euler_reaction_integrand=np.array(reactions),
        paired_gauge_Euler_reaction=simpson(np.array(reactions),x=t,axis=0),
        source_trace=np.array(physical_traces),source_trace_rate=np.array(physical_trace_rates),
        intrinsic_H_response=states[:,320:400],
        intrinsic_H_canonical_momenta=states[:,n+320:n+400],
        intrinsic_scalar_wall_current_pairing=simpson(np.array(scalar_work),x=t,axis=0),
        wall_trace_reaction_pairing=work,action_temporal_endpoint=endpoint,
        action_boundary_pairing=action_boundary,
        action_boundary_relative_defect=float(np.max(abs(work-action_boundary))/(1+np.max(abs(work)))),
        advanced_adjoint=adjoints,adjoint_readout_map=readout,
        adjoint_output=output,adjoint_source_pairing=contraction,
        adjoint_pairing_maximum_defect=float(np.max(abs(output-contraction))),
        numerical_integrator=dict(method='DOP853',rtol=rtol,atol=atol,evaluations=sol.nfev),
        actual_new_reached_source_response=True,old_source_span_response_substituted=False,
        source_motion_count=1,source_motion_differentiated_before_Gauss=True,
        final_source_canonical_momentum=final_source_momentum,
        source_terminal_endpoint=gz*final_source_momentum,
        temporal_source_scope='same constant magnetic birth trace inherited from incoming plateau; canonical initial state transferred through reached fixed-frame field graph',
        physical_free_wall_inverse=False,physical_native_heat_closed=False,physical_Pauli_value=False)

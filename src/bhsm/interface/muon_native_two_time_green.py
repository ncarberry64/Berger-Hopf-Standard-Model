"""Chronological two-time applications of the reached Maxwell/Higgs action.

These kernels solve the literal classical Euler/Gauss operator.  They are
not a Feynman covariance or a positive BRST/ghost heat inverse.  In
particular a three-axis integrated boundary Hessian is not substituted
for the virtual photon kernel in an open fermion loop.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.linalg import cho_factor,cho_solve
from .muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from .muon_parent_maxwell_full_retarded import _reduced_at


def load_executed_magnetic_green_form(directory,*,repository):
    """Bind the actual full488 forms; reduce the Gauss row at each time."""
    inputs=load_magnetic_reached_mean_inputs(directory,repository=repository)
    folder=inputs['directory'];root=Path(repository)
    data=(folder/'operators.npz').read_bytes();info=inputs['receipt']['array_archives']['operators.npz']
    if len(data)!=info['bytes'] or sha256(data).hexdigest()!=info['sha256']:
        raise ValueError('same-background operator archive changed')
    with np.load(folder/'operators.npz',allow_pickle=False) as f:
        arrays={key:f[key].copy() for key in f.files}
    nodes=inputs['source']['times'];nt=len(nodes)
    form=dict(final_time=float(nodes[-1]),time_nodes=nodes,
        source_map=CubicSpline(nodes,inputs['source']['Q']),
        source_rate_map=CubicSpline(nodes,inputs['source']['Qdot']),
        interior_count=400,Gauss_count=80,active_indices=[0,1,2],
        side=inputs['receipt']['side'],inputs=inputs,input_hashes=dict(inputs['input_hashes']))
    for name in ('M','B','K'):
        value=arrays['raw_'+name]
        if value.shape!=(nt,488,488) or not np.isrealobj(value) or not np.isfinite(value).all():
            raise ValueError('complete real full488 same-action '+name+' required')
        form['raw_'+name]=CubicSpline(nodes,value)
    form['input_hashes'][(folder/'operators.npz').relative_to(root).as_posix()]=info['sha256']
    return form


def _canonical_application(f,phase,n):
    M,B,K=(f[k][:n,:n] for k in ('M','B','K'))
    x,p=phase[:n],phase[n:]
    v=cho_solve(cho_factor(M),p-B.T@x)
    return np.r_[v,B@v+K@x]


def _boundary_impulse(f,n,active,kind):
    M,B,K=(f[k] for k in ('M','B','K'))
    if kind=='value':
        v=-cho_solve(cho_factor(M[:n,:n]),B[n:,:n].T[:,active])
        force=B[:n,:n]@v+K[:n,n:][:,active]
        instant=f['At_value_map'][:,n:][:,active]+f['At_velocity_map'][:,:n]@v
    elif kind=='rate':
        v=-cho_solve(cho_factor(M[:n,:n]),M[:n,n:][:,active])
        force=B[:n,:n]@v+B[:n,n:][:,active]
        instant=f['At_velocity_map'][:,n:][:,active]+f['At_velocity_map'][:,:n]@v
    else:raise ValueError('boundary value or future-rate channel required')
    return np.r_[v,force],instant


def retarded_boundary_green_application(form,source_time,observation_times,*,
        channel='value',rtol=2e-10,atol=2e-12,max_step=None):
    """Apply Phi(t,s)F_b(s) or Phi(t,s)F_bdot(s), including Gauss contacts.

    For L=.5 vMv+xBv+.5 xKx, p=Mv+B^T x, the canonical
    phase obeys xdot=M^-1(p-B^T x), pdot=B xdot+Kx.
    The boundary value and rate columns are different distributions.
    Their sum with b and bdot produces the same action source; they
    must not be identified with two independent quantum field inputs.
    """
    s=float(source_time);t=np.asarray(observation_times)
    if (not np.isrealobj(t) or t.ndim!=1 or not np.isfinite(t).all()
            or not np.isfinite(s) or not 0<=s<form['final_time']
            or np.any(np.diff(t)<=0) or np.any(t<0) or np.any(t>form['final_time'])):
        raise ValueError('actual ordered chronological source/observation times required')
    n=form['interior_count'];active=form['active_indices'];k=len(active)
    initial,instant=_boundary_impulse(_reduced_at(form,s),n,active,channel)
    step=float(max_step) if max_step is not None else form['final_time']/64
    if not np.isfinite(step) or step<=0:raise ValueError('positive numerical integration step required')
    def rhs(a,state):return _canonical_application(_reduced_at(form,a),state.reshape(2*n,k),n).ravel()
    sol=solve_ivp(rhs,(s,form['final_time']),initial.ravel(),method='DOP853',
        rtol=rtol,atol=atol,max_step=step,dense_output=True)
    if not sol.success:raise ArithmeticError('two-time action application failed: '+sol.message)
    phase=np.zeros((len(t),2*n,k));velocity=np.zeros((len(t),n,k));At=np.zeros((len(t),form['Gauss_count'],k))
    for j,a in enumerate(t):
        if a<s:continue
        phase[j]=sol.sol(a).reshape(2*n,k);f=_reduced_at(form,a)
        velocity[j]=_canonical_application(f,phase[j],n)[:n]
        At[j]=f['At_value_map'][:,:n]@phase[j,:n]+f['At_velocity_map'][:,:n]@velocity[j]
    return dict(source_time=s,observation_times=t,phase_kernel=phase,
        side=form['side'],birth_face_reached=bool(form['side']=='incoming' and t[-1]==form['final_time']),
        velocity_kernel=velocity,Gauss_field_kernel=At,
        canonical_jump_columns=initial,instantaneous_Gauss_contact=instant,
        instantaneous_boundary_trace_contact=form['source_map'](s)[:,active] if channel=='value' else np.zeros((400,k)),
        boundary_channel=channel,active_source_indices=active,
        retarded_support_exact_before_source=True,all400_dynamic_and80_Gauss_rows_retained=True,
        differential_rate_contact_not_discarded=True,
        numerical_integrator=dict(method='DOP853',rtol=rtol,atol=atol,evaluations=sol.nfev),
        quantum_Feynman_or_positive_native_covariance_claimed=False,
        static_frequency_or_vacuum_Fourier_pencil_used=False,
        full_native_ghost_or_open_loop_Pauli_completed=False)


def apply_reached_canonical_source(form,profile,*,initial_state=None,observation_times=None,
        rtol=2e-10,atol=2e-12):
    """Execute the same two-channel kernel equation on an actual source law.

    The supplied profile is the owner's reached value/rate application.
    Outgoing initial x/p must come from the incoming canonical birth;
    zero initial data is permitted only for the incoming retarded arm.
    """
    n=form['interior_count'];active=form['active_indices'];k=len(active);T=form['final_time']
    if initial_state is None:
        if form['side']!='incoming':raise ValueError('actual outgoing canonical birth state required')
        initial=np.zeros((2*n,k))
    else:
        initial=np.asarray(initial_state)
        if not np.isrealobj(initial) or initial.shape!=(2*n,k) or not np.isfinite(initial).all():
            raise ValueError('complete real canonical birth columns required')
    def rhs(t,state):
        f=_reduced_at(form,t);p,pt=profile(t)[:2]
        value,_=_boundary_impulse(f,n,active,'value');rate,_=_boundary_impulse(f,n,active,'rate')
        return (_canonical_application(f,state.reshape(2*n,k),n)+p*value+pt*rate).ravel()
    sol=solve_ivp(rhs,(0,T),initial.ravel(),method='DOP853',rtol=rtol,atol=atol,
        max_step=T/256,dense_output=True)
    if not sol.success:raise ArithmeticError('canonical source application failed: '+sol.message)
    t=form['inputs']['times'] if observation_times is None else np.asarray(observation_times)
    if not np.isrealobj(t) or t.ndim!=1 or not np.isfinite(t).all() or np.any(t<0) or np.any(t>T):
        raise ValueError('actual finite chronological observation times required')
    return dict(times=t,phase=sol.sol(t).T.reshape(len(t),2*n,k),
        source_channel_equation='phase=Phi initial+integral Phi(F_b b+F_bdot bdot)dt',
        quantum_covariance_or_Pauli_completed=False)


def continue_canonical_green_across_birth(incoming_application,outgoing_form,observation_times,*,
        rtol=2e-10,atol=2e-12):
    """Execute the reached common-frame trace/canonical graph on a Green column.

    This is the same pointwise fixed-frame graph used by the actual source
    owner.  It does not replace its global worldvolume bundle transport.
    At and the future velocity are rederived from the outgoing action.
    """
    receipt=outgoing_form['inputs']['receipt']
    if outgoing_form['side']!='outgoing' or not receipt['birth_source_matching']['actual_source_initial_state_supplied_from_incoming_birth']:
        raise ValueError('reached common-frame canonical birth graph required')
    n=outgoing_form['interior_count'];k=len(outgoing_form['active_indices'])
    initial=np.asarray(incoming_application['phase_kernel'][-1])
    if initial.shape!=(2*n,k) or not np.isrealobj(initial) or not np.isfinite(initial).all():
        raise ValueError('complete actual incoming Green birth columns required')
    if not incoming_application.get('birth_face_reached',False):
        raise ValueError('incoming application must reach the common birth face')
    t=np.asarray(observation_times)
    if not np.isrealobj(t) or t.ndim!=1 or not np.isfinite(t).all() or np.any(np.diff(t)<=0) or np.any(t<0) or np.any(t>outgoing_form['final_time']):
        raise ValueError('actual increasing outgoing observation times required')
    def rhs(a,state):return _canonical_application(_reduced_at(outgoing_form,a),state.reshape(2*n,k),n).ravel()
    sol=solve_ivp(rhs,(0,outgoing_form['final_time']),initial.ravel(),method='DOP853',
        rtol=rtol,atol=atol,max_step=outgoing_form['final_time']/64,dense_output=True)
    if not sol.success:raise ArithmeticError('common-birth Green continuation failed: '+sol.message)
    phase=sol.sol(t).T.reshape(len(t),2*n,k);velocity=[];At=[]
    for a,p in zip(t,phase):
        f=_reduced_at(outgoing_form,a);v=_canonical_application(f,p,n)[:n]
        velocity.append(v);At.append(f['At_value_map'][:,:n]@p[:n]+f['At_velocity_map'][:,:n]@v)
    return dict(observation_times=t,phase_kernel=phase,velocity_kernel=np.array(velocity),Gauss_field_kernel=np.array(At),
        canonical_birth_jump_norm=float(np.linalg.norm(phase[0]-initial)) if t[0]==0 else None,
        inherited_pointwise_graph_scope='same common angular/radial coefficient trace and canonical-dual graph as executed magnetic source owner',
        outgoing_velocity_or_Gauss_copied_from_incoming=False,
        global_worldvolume_bundle_reset_evaluated=False,quantum_covariance_or_Pauli_completed=False)

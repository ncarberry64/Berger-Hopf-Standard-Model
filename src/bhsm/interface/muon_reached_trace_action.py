"""Same Maxwell/Higgs weak action on moving reached angular traces.

The trace map is differentiated before the algebraic Gauss reduction.
Neither a compression to the original photon span nor a frozen trace
normalization is used.  This is a finite action application; its radial
trial core and time interpolation do not select a physical event or heat
cutoff.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.integrate import solve_ivp, simpson
from scipy.linalg import cho_factor, cho_solve

from .muon_parent_maxwell_corrected_retarded import (
    _lift_tensor, _gauge_rows, full_constant_angular_hessian,
    intrinsic_scalar_trace_hessian,
)
from .muon_parent_maxwell_full_retarded import constrained_gauss_schur
from .muon_parent_maxwell_full_retarded import _reduced_at
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import FIELD_ORDER, M
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_retarded_hypercharge import WALL, regular_radial_basis, compact_trace_pulse


def _real_array(value, shape, name):
    if value is None or not np.isrealobj(value):
        raise ValueError('explicit real '+name+' required')
    a = np.asarray(value, float)
    if a.shape != shape or not np.isfinite(a).all():
        raise ValueError('finite complete '+name+' required')
    return a


def moving_trace_time_forms(local_tensors, weights, radial_values,
                            radial_derivatives, trace, trace_rate,
                            harmonic_products):
    """Pull back all three field jets, including Qdot*b in beta_dot.

    beta=phi*x+lift*Q*b; beta_dot=phi*xdot+lift*(Q*bdot+Qdot*b).
    The returned signed Lagrangian is .5 zdot M zdot+z B zdot+.5 z K z.
    Qdot has its own term, counted once; it is not an Eulerian field
    derivative in addition to that same material motion.
    """
    Q = np.asarray(trace)
    if Q.ndim != 2 or Q.shape[0] != 400 or Q.shape[1] < 1:
        raise ValueError('full inherited real400 trace actions required')
    k = Q.shape[1]
    Q = _real_array(Q, (400,k), 'trace')
    Qt = _real_array(trace_rate, Q.shape, 'trace rate')
    w = np.asarray(weights,float); count = len(w)
    H = _real_array(radial_values, (count,2), 'radial values')
    Hr = _real_array(radial_derivatives, (count,2), 'radial derivatives')
    local = _real_array(local_tensors, (count,3,3,4,4,20,20), 'action tensors')
    products = _real_array(harmonic_products,(4,4,20,20),'harmonic pairings')
    if not np.isfinite(w).all() or np.any(w <= 0):
        raise ValueError('positive inherited radial quadrature required')
    slices = (slice(0,400),slice(400,400+k))
    base = [(0,H[:,0],None),(1,H[:,1],Q)]
    radial = [(0,Hr[:,0],None),(1,Hr[:,1],Q)]
    extra = [(1,H[:,1],Qt)]
    def block(i,j,left,right):
        result = np.zeros((400+k,400+k))
        for l,ls,L in left:
            for r,rs,R in right:
                tensor = np.einsum('r,rpqab->pqab',w*ls*rs,local[:,i,j])
                matrix = _lift_tensor(tensor,products)
                if L is not None: matrix = L.T@matrix
                if R is not None: matrix = matrix@R
                result[slices[l],slices[r]] += matrix
        return result
    mass = block(1,1,base,base)
    mixed = (block(0,1,base,base)+block(2,1,radial,base)
             +block(1,1,extra,base))
    maps = (base,extra,radial)
    stiffness = sum((block(i,j,maps[i],maps[j])
                     for i in range(3) for j in range(3)),
                    np.zeros_like(mass))
    return mass,mixed,(stiffness+stiffness.T)/2


def moving_trace_gauge_rows(local,gauge,weights,H,Hr,trace,trace_rate,E):
    """All D_A eta rows with their actual moving-trace right derivative."""
    Q = _real_array(trace,(400,8),'eight reached traces')
    Qt = _real_array(trace_rate,(400,8),'eight reached trace rates')
    rows = _gauge_rows(local,gauge,weights,H,Hr,Q,E)
    rate_rows = _gauge_rows(local,gauge,weights,H,Hr,Qt,E)
    rows[0,:,400:] += rate_rows[1,:,400:]
    rows[2,:,400:] += rate_rows[3,:,400:]
    return rows


def coupled_reached_sample(raw,representation,angular,trace,trace_rate,*,
                           nu_squared_action):
    """Literal full5 parent plus intrinsic H on one raw228 coefficient jet.

    raw q/qdot, material normal/rate, independent a/adot and H/Hdot are
    bound together.  This accepts no saved old angular response or Gram
    in place of their actual action application.
    """
    raw = _real_array(raw,(228,),'common field jet')
    Q = _real_array(trace,(400,8),'eight reached traces')
    Qt = _real_array(trace_rate,(400,8),'eight reached trace rates')
    if np.any(Q[:160]) or np.any(Qt[:160]):
        raise ValueError('this reached application requires spatial Ai traces; At/Ar stay internal')
    nu2 = float(nu_squared_action)
    if not np.isfinite(nu2) or nu2 < 0:
        raise ValueError('explicit nonnegative action-unit Higgs parameter required')
    rep = representation
    if len(rep['gauge_labels']) != 60:
        raise ValueError('actual complete mean radial representation required')
    rho,w = rep['rho'],rep['radial_quadrature']
    q,v,m,s,sr = raw[:37],raw[37:74],raw[74:98],raw[98],raw[99]
    geo = geometric_connection_coefficient_jets(12,q,v,m,rho,
        source_value=s,source_rate=sr,clock='coordinate_time')
    gb,gbr = rep['gauge_basis'],rep['gauge_radial_basis']
    A = np.einsum('rj...,j->r...',gb,raw[100:160])[:,0]
    At = np.einsum('rj...,j->r...',gb,raw[160:220])[:,0]
    Ar = np.einsum('rj...,j->r...',gbr,raw[100:160])[:,0]
    local=[]
    for j,row in enumerate(geo['rows']):
        A[j,2:] += M*(row['connection_lambda'].value-1)
        At[j,2:] += M*row['lambda_tau'].value
        Ar[j,2:] += M*row['lambda_rho'].value
        density = [row[k].value for k in ('electric','radial','angular','electric_radial','shift')]
        local.append(full_constant_angular_hessian(A[j],At[j],Ar[j],density))
    H,Hr = regular_radial_basis(rho,1)
    E = np.concatenate((np.eye(20)[None],angular['derivative_matrices']))
    products = np.array([[a.T@b for b in E] for a in E])
    maxwell = moving_trace_time_forms(np.array([a['tensor'] for a in local]),
        w,H,Hr,Q,Qt,products)
    matrices=[];idx=np.r_[np.arange(400),np.arange(480,488)]
    for old in maxwell:
        new=np.zeros((488,488));new[np.ix_(idx,idx)]=old;matrices.append(new)
    metric = intrinsic_m4_weight_jet(12,q,v,m,source_value=s,source_rate=sr)
    wall_basis,_ = regular_radial_basis(np.array([WALL]),rep['radial_order'])
    wall = np.zeros((5,4))
    for j,label in enumerate(rep['gauge_labels']):
        wall[FIELD_ORDER.index(label['field']),label['internal']] += wall_basis[0,label['radial']]*raw[100+j]
    wall[2:] += M*(metric['mechanical_connection_lambda'].value-1)
    scalar = intrinsic_scalar_trace_hessian(raw[220:224],raw[224:228],wall,
        np.array([metric[k].value for k in ('wT','wS','wV')]),
        lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu2,angular=angular)['matrix']
    value=np.zeros((560,488));velocity=np.zeros_like(value)
    value[:80,400:480]=np.eye(80);value[80:480,480:]=Q
    velocity[480:,400:480]=np.eye(80)
    scalar_forms=(8*velocity.T@scalar@velocity,
                  8*value.T@scalar@velocity,8*value.T@scalar@value)
    matrices=[a+b for a,b in zip(matrices,scalar_forms)]
    rows=moving_trace_gauge_rows(local,A,w,H,Hr,Q,Qt,E)
    expanded=np.zeros((4,80,488));expanded[:,:,:400]=rows[:,:,:400]
    expanded[:,:,480:]=rows[:,:,400:]
    reduced=constrained_gauss_schur(*matrices,80)
    return dict(raw_forms=tuple(matrices),reduced=reduced,
        scalar_forms=scalar_forms,gauge_weak_rows=expanded,
        source=Q,source_rate=Qt,raw_fields=raw,
        full_background_values=np.array([A,At,Ar]),
        all_moving_trace_contacts_retained=True,
        scalar_Maxwell_relative_normalization=8.,
        physical_free_wall_inverse=False,physical_Pauli_value=False)


def sampled_reached_form(times,samples,*,duration):
    """Interpolate the unreduced action, then eliminate Gauss at each t.

    The samples come from coupled_reached_sample.  Interpolation is a
    numerical action core; it is not an enclosure of a physical history.
    """
    t=np.asarray(times,float)
    if (t.ndim!=1 or len(t)<5 or t[0]!=0 or np.any(np.diff(t)<=0)
        or len(samples)!=len(t) or not 0<duration<t[-1]):
        raise ValueError('resolved oriented local response interval required')
    form=dict(time_nodes=t,duration=float(duration),final_time=float(t[-1]),
        spatial_interior_unknowns=400,intrinsic_scalar_unknowns=80,
        raw_forms=[s['raw_forms'] for s in samples],
        forms=[s['reduced'] for s in samples],
        gauge_weak_rows=CubicSpline(t,np.array([s['gauge_weak_rows'] for s in samples])),
        source_map=CubicSpline(t,np.array([s['source'] for s in samples])),
        source_rate_map=CubicSpline(t,np.array([s['source_rate'] for s in samples])),
        reached_raw_fields=np.array([s['raw_fields'] for s in samples]),
        angular=dict(source_coefficients=samples[0]['source']),
        all_moving_trace_contacts_retained=True,
        source_motion_was_differentiated_before_Gauss=True,
        source_rate_is_derivative_of_supplied_source_interpolation=False,
        physical_free_wall_inverse=False,physical_Pauli_value=False)
    for i,key in enumerate(('raw_M','raw_B','raw_K')):
        form[key]=CubicSpline(t,np.array([s['raw_forms'][i] for s in samples]))
        # Reduced intrinsic rows are needed by the actual terminal readout.
        form['intrinsic_'+key]=CubicSpline(t,np.array([s['scalar_forms'][i][80:,80:] for s in samples]))
    form['minimum_interior_mass_eigenvalue']=min(float(np.linalg.eigvalsh(s['reduced']['M'][:400,:400])[0]) for s in samples)
    if form['minimum_interior_mass_eigenvalue']<=0:
        raise ArithmeticError('the declared finite internal kinetic form is not positive')
    return form


def reached_retarded_application(form,*,time_steps=64,rtol=2e-9,atol=2e-11):
    """Solve the actual reached eight-column Euler/Gauss source problem.

    The compact temporal pulse is a numerical Green application.  Its
    normalization and the moving full400 source actions are retained.
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
        g,gd,_=compact_trace_pulse(t,D)
        velocity=cho_solve(cho_factor(mass[:n,:n]),
            p-mixed[:n,:n].T@x-g*mixed[n:,:n].T-gd*mass[:n,n:])
        force=mixed[:n,:n]@velocity+g*stiffness[:n,n:]+gd*mixed[:n,n:]+stiffness[:n,:n]@x
        return np.r_[velocity,force].ravel()
    sol=solve_ivp(rhs,(0,T),np.zeros(2*n*k),method='DOP853',
        rtol=rtol,atol=atol,max_step=D/time_steps,dense_output=True)
    if not sol.success:raise ArithmeticError('reached action solve failed: '+sol.message)
    t=np.linspace(0,T,3*time_steps+1)
    states=sol.sol(t).T.reshape(-1,2*n,k)
    velocities=np.array([rhs(a,b.ravel()).reshape(2*n,k)[:n] for a,b in zip(t,states)])
    Ats=[];Gauss=[];Gauss_rel=[];reactions=[];work=[];quadratic=[];scalar_work=[];physical_traces=[];physical_trace_rates=[]
    for a,state,v in zip(t,states,velocities):
        f=_reduced_at(form,a);g,gd,_=compact_trace_pulse(a,D)
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
    contraction=simpson(np.array([a.T@rhs(b,np.zeros(2*n*k)).reshape(2*n,k)
        for a,b in zip(adjoints,t)]),x=t,axis=0)
    output=readout@states[-1]
    endpoint=states[-1,:n].T@states[-1,n:]-states[0,:n].T@states[0,n:]
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
        temporal_source_scope='numerical compact Green pulse, not selected physical soft transfer',
        physical_free_wall_inverse=False,physical_native_heat_closed=False,physical_Pauli_value=False)

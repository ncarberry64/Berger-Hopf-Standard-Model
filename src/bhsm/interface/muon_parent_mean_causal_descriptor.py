"""Joint causal mean response and source-paired advanced readout.

The public producer binds the retained instantaneous common action.  It
does not invert a compact two-face Newton matrix, select a scalar state,
or replace the reached gauge/geometry reactions by a Higgs-only inverse.
The current domain is the explicitly numerical outgoing finite core.
"""
from __future__ import annotations

import numpy as np
import json
from hashlib import sha256
from pathlib import Path
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.linalg import lu_factor, lu_solve, matrix_balance

from .muon_birth_candidate_geometry_action import ROOT
from .muon_parent_mean_causal_action import retained_mean_action_family,mean_action_family

ACTION_SAMPLES='artifacts/muon_mean_legendre_certificate_20261010/run_2/action_samples.npz'
ACTION_SAMPLES_SHA='e260a451cba183c94b0d30c29e43b5a06a7503730c68403232c23664b0ff5dbe'


def _real(value, name, shape=None):
    if value is None or not np.isrealobj(value):
        raise ValueError(f'explicit real {name} required')
    result = np.asarray(value, float)
    if not np.isfinite(result).all() or (shape is not None and result.shape != shape):
        raise ValueError(f'finite {name} with shape {shape} required')
    return result


def _saddle_solve(D, rhs):
    """Congruence scaling changes numerical units, not the saddle equation."""
    scale = 1 / np.sqrt(np.max(abs(D), axis=1))
    if not np.isfinite(scale).all():
        raise ValueError('reached saddle has a zero row; no pseudoinverse used')
    balanced = scale[:, None] * D * scale
    factor = lu_factor(balanced)
    result = scale[:, None] * lu_solve(factor, scale[:, None] * rhs)
    if not np.isfinite(result).all():
        raise RuntimeError('nonfinite reached constitutive solve')
    residual = D @ result - rhs
    denominator = np.linalg.norm(D, np.inf)*np.linalg.norm(result, np.inf)+np.linalg.norm(rhs, np.inf)
    return result, float(np.linalg.norm(residual, np.inf)/denominator) if denominator else 0.


def _descriptor_from_samples(samples):
    """Internal equation compiler; physical inputs come from the owner above."""
    times = _real(samples['times'], 'mean action times')
    if times.ndim != 1 or len(times) < 3 or np.any(np.diff(times) <= 0):
        raise ValueError('at least three increasing action sample times required')
    n, m = samples['x_count'], samples['y_count']
    if samples['v_count'] != n:
        raise ValueError('paired mean value/rate counts required')
    h = _real(samples['hessian_samples'], 'same-action Hessians', (len(times), 2*n+m, 2*n+m))
    j = _real(samples['source_samples'], 'same-action mixed source', (len(times), 2*n+m, 8, 8))
    if not np.allclose(h, h.transpose(0, 2, 1), rtol=1e-12, atol=1e-12):
        raise ValueError('one real scalar action requires symmetric Hessians')
    return dict(samples=samples, times=times, n=n, m=m,
        hessian=CubicSpline(times, h), source=CubicSpline(times, j),
        full_hessian=CubicSpline(times, samples['full_hessian_samples']) if 'full_hessian_samples' in samples else None,
        full_source=CubicSpline(times, samples['full_source_samples']) if 'full_source_samples' in samples else None)


def retained_mean_causal_descriptor(repository=ROOT, *, time_nodes=17):
    """Execute the actual common-action sample producer and compile its IVP."""
    return _descriptor_from_samples(retained_mean_action_family(repository, time_nodes=time_nodes))


def certified_sampled_mean_descriptor(repository=ROOT):
    """Reuse exact sampled action operands pinned by the stored Arb receipt.

    Arb certifies the stored instantaneous matrices.  Their sign counts
    change, so this binding explicitly rejects continuous regularity as a
    conclusion.  The finite implicit descriptor remains evaluable.
    """
    root=Path(repository);archive=root/ACTION_SAMPLES;raw=archive.read_bytes()
    if sha256(raw).hexdigest()!=ACTION_SAMPLES_SHA:raise ValueError('frozen same-action sample archive changed')
    receipt=json.loads((archive.parent/'result.json').read_bytes())
    if receipt['action_samples_sha256']!=ACTION_SAMPLES_SHA:raise ValueError('sample receipt hash disagreement')
    for path,digest in receipt['input_hashes'].items():
        if sha256((root/path).read_bytes()).hexdigest()!=digest:raise ValueError(f'consumed action input changed: {path}')
    with np.load(archive) as a:arrays={k:a[k].copy() for k in a.files}
    family=mean_action_family(root);labels=family['coordinates']['raw_gauge_labels']
    Q=arrays['full_to_restricted_lift'];indices=np.argmax(Q,axis=0)
    if Q.shape!=(216,180) or not np.array_equal(Q,np.eye(216)[:,indices]):raise ValueError('retained exact trace restriction changed')
    x=indices[:74];y=indices[148:]-180
    rejected_x=np.array([38+j for j,i in enumerate(family['coordinates']['dynamic_gauge_indices']) if labels[i]['wall_lift']])
    rejected_y=np.array([180+24+j for j,i in enumerate(family['coordinates']['At_indices']) if labels[i]['wall_lift']])
    H=arrays['master_hessians'];J=arrays['master_source_cotangents']
    samples=dict(times=arrays['times'],hessian_samples=np.einsum('ia,tij,jb->tab',Q,H,Q),
        source_samples=np.einsum('ia,tiAB->taAB',Q,J),full_hessian_samples=H,full_source_samples=J,
        full_gradient_samples=arrays['master_gradients'],lift_to_full_mean=Q,
        x_count=74,v_count=74,y_count=32,x_full_indices=x,y_full_indices=y,H_real_indices=np.arange(70,74),
        raw_gauge_labels=labels,rejected_wall_value_rows=np.r_[rejected_x,rejected_y],
        rejected_wall_canonical_rows=90+rejected_x,source_record=receipt['input_hashes'],
        action_samples_path=ACTION_SAMPLES,action_samples_sha256=ACTION_SAMPLES_SHA,
        instantaneous_inertia_changes=True,continuous_interval_regularity_proved=False,
        source_scope=family['source_receipt']['source_profile_scope'],background_scope=family['scope'])
    return _descriptor_from_samples(samples)


def mean_phase_coefficients(time, descriptor, *, derivative=False):
    """Return zdot=Fz+b, z=(x,p), retaining the canonical inhomogeneity Jv.

    D[v;y]=[p-Lvx*x-Jv; -Lyx*x-Jy],
    pdot=Lxx*x+Lxv*v+Lxy*y+Jx.  In particular Jv is not silently
    differentiated away or treated as an independent forcing choice.
    """
    t = float(time)
    if not np.isfinite(t) or t < descriptor['times'][0] or t > descriptor['times'][-1]:
        raise ValueError('descriptor cannot extrapolate its numerical core')
    n, m = descriptor['n'], descriptor['m']
    H = descriptor['hessian'](t); J = descriptor['source'](t).reshape(2*n+m, 64)
    D = H[n:, n:]
    R = np.vstack((np.column_stack((-H[n:2*n, :n], np.eye(n))),
                   np.column_stack((-H[2*n:, :n], np.zeros((m, n))))))
    rhs = np.column_stack((R, -J[n:]))
    solution, residual = _saddle_solve(D, rhs)
    U, f = solution[:, :2*n], solution[:, 2*n:]
    F = np.vstack((U[:n], np.column_stack((H[:n, :n], np.zeros((n, n))))+H[:n, n:]@U))
    b = np.vstack((f[:n], H[:n, n:]@f+J[:n]))
    result = dict(F=F, b=b, U=U, f=f, constitutive_residual_relative=residual)
    if derivative:
        Hd = descriptor['hessian'](t, 1); Jd = descriptor['source'](t, 1).reshape(2*n+m, 64)
        Rd = np.vstack((np.column_stack((-Hd[n:2*n, :n], np.zeros((n, n)))),
                       np.column_stack((-Hd[2*n:, :n], np.zeros((m, n))))))
        ds, dr = _saddle_solve(D, np.column_stack((Rd, -Jd[n:]))-Hd[n:, n:]@solution)
        result.update(Udot=ds[:, :2*n], fdot=ds[:, 2*n:], derivative_solve_residual_relative=dr)
    return result


def mean_descriptor_diagnostics(descriptor):
    n = descriptor['n']; symplectic = np.block([[np.zeros((n,n)), np.eye(n)],[-np.eye(n), np.zeros((n,n))]])
    rows=[]
    for t in descriptor['times']:
        H=descriptor['hessian'](t); D=H[n:,n:]; scale=1/np.sqrt(np.max(abs(D),axis=1))
        eigen=np.linalg.eigvalsh(scale[:,None]*D*scale)
        a=mean_phase_coefficients(t,descriptor); defect=a['F'].T@symplectic+symplectic@a['F']
        rows.append(dict(time=float(t),balanced_saddle_minimum_absolute_eigenvalue=float(min(abs(eigen))),
            balanced_saddle_condition_estimate=float(max(abs(eigen))/min(abs(eigen))),
            saddle_inertia_positive=int(np.count_nonzero(eigen>0)),saddle_inertia_negative=int(np.count_nonzero(eigen<0)),
            constitutive_residual_relative=a['constitutive_residual_relative'],
            Hamiltonian_phase_defect_relative=float(np.linalg.norm(defect)/max(1.,np.linalg.norm(a['F'])))))
    return rows


def _phase_scale(descriptor):
    F=mean_phase_coefficients(np.mean(descriptor['times'][[0,-1]]),descriptor)['F']
    _, transform=matrix_balance(F,permute=False)
    return np.diag(transform)


def solve_retarded_mean_phase(descriptor, *, output_times, rtol, atol):
    """Solve all eight-by-eight actual mixed-source columns on this domain.

    Initial x=p=0 is the differentiated homogeneous initial condition of
    this controlled retarded problem; it is not a physical vacuum choice.
    """
    times=_real(output_times,'retarded output times')
    if times.ndim!=1 or not len(times) or np.any(np.diff(times)<0):raise ValueError('ordered output times required')
    if times[0]<descriptor['times'][0] or times[-1]>descriptor['times'][-1]:raise ValueError('no retarded extrapolation')
    if not all(np.isfinite(v) and v>0 for v in (rtol,atol)):raise ValueError('positive explicit numerical tolerances required')
    scale=_phase_scale(descriptor); size=2*descriptor['n']
    amplitude=max(np.max(abs(mean_phase_coefficients(t,descriptor)['b']/scale[:,None])) for t in descriptor['times'])
    amplitude=max(amplitude,np.finfo(float).tiny)
    def rhs(t,z):
        a=mean_phase_coefficients(t,descriptor); y=z.reshape(size,64)
        return ((a['F']*scale[None,:]/scale[:,None])@y+a['b']/scale[:,None]/amplitude).ravel()
    sol=solve_ivp(rhs,(descriptor['times'][0],descriptor['times'][-1]),np.zeros(size*64),
        t_eval=times,method='DOP853',rtol=rtol,atol=atol,dense_output=True)
    if not sol.success or not np.isfinite(sol.y).all():raise RuntimeError(sol.message)
    phase=sol.y.T.reshape(len(times),size,64)*scale[None,:,None]*amplitude
    return dict(times=times,phase=phase.reshape(len(times),size,8,8),
        solution=lambda t:sol.sol(t).reshape(size,64)*scale[:,None]*amplitude,
        function_evaluations=sol.nfev,rtol=rtol,atol=atol,method='DOP853',
        initial_phase='homogeneous mixed response x=p=0 for the declared retarded numerical core',
        physical_E0_or_vacuum_selected=False)


def mean_phase_reconstruction(time, phase, descriptor):
    """Recover all retained mean variables and the20 prescribed-wall reactions."""
    n=descriptor['n']; z=_real(phase,'actual mean phase',(2*n,64))
    a=mean_phase_coefficients(time,descriptor,derivative=True)
    w=a['U']@z+a['f']; zd=a['F']@z+a['b']; wd=a['Udot']@z+a['U']@zd+a['fdot']
    eta=np.vstack((z[:n],w)); etad=np.vstack((w[:n],wd))
    result=dict(mean_value_rate_algebraic=eta.reshape(2*n+descriptor['m'],8,8))
    samples=descriptor['samples']
    if descriptor['full_hessian'] is not None:
        lift=samples['lift_to_full_mean']; full=lift@eta; fulld=lift@etad
        H=descriptor['full_hessian'](time); Hd=descriptor['full_hessian'](time,1)
        J=descriptor['full_source'](time).reshape(216,64); Jd=descriptor['full_source'](time,1).reshape(216,64)
        force=H@full+J; canonical_rate=Hd@full+H@fulld+Jd
        rows=samples['rejected_wall_value_rows']; reactions=force[rows].copy()
        dynamic=samples['rejected_wall_canonical_rows']; reactions[:len(dynamic)]-=canonical_rate[dynamic]
        result.update(full_mean_value_rate_algebraic=full.reshape(216,8,8),
            wall_reactions=reactions.reshape(len(rows),8,8),
            reaction_equation='dynamic prescribed-wall rows: delta L_x-d_t delta L_v; algebraic prescribed-wall At rows: delta L_y',
            all20_prescribed_wall_reactions_retained=True)
    return result


def advanced_mean_target_contraction(descriptor, *, target_times, target_loads, rtol, atol):
    """Joint advanced readout for weighted x/v/y cotangents at exact samples.

    target_loads have shape(sample,2*x+y,target).  Velocity/algebraic
    readouts use w=Uz+f, so their source-dependent direct term is retained.
    The loads already include heat quadrature density.  Each phase adjoint
    jumps by g=([ell_x,0]+U.T ell_w) at its sample; no density is reapplied.
    """
    times=_real(target_times,'target sample times'); loads=_real(target_loads,'weighted mean readout loads')
    n,m=descriptor['n'],descriptor['m']; size=2*n
    if times.ndim!=1 or len(times)==0 or np.any(np.diff(times)<=0):raise ValueError('strictly increasing target samples required')
    if loads.ndim!=3 or loads.shape[:2]!=(len(times),2*n+m):raise ValueError('complete reduced x/v/y target loads required')
    if times[0]<descriptor['times'][0] or times[-1]>descriptor['times'][-1]:raise ValueError('no target extrapolation')
    if not all(np.isfinite(v) and v>0 for v in (rtol,atol)):raise ValueError('positive explicit numerical tolerances required')
    count=loads.shape[2]; scale=_phase_scale(descriptor); impulses=[]; direct=np.zeros((count,64))
    for t,ell in zip(times,loads):
        a=mean_phase_coefficients(t,descriptor)
        g=np.vstack((ell[:n],np.zeros((n,count))))+a['U'].T@ell[n:]
        impulses.append(scale[:,None]*g);direct+=ell[n:].T@a['f']
    impulses=np.array(impulses);amplitude=np.max(abs(impulses),axis=(0,1))
    amplitude=np.maximum(amplitude,np.finfo(float).tiny)
    impulses/=amplitude[None,None,:]
    current=np.zeros((size,count));work=np.zeros((count,64));nfev=0
    boundaries=np.r_[descriptor['times'][0],times,descriptor['times'][-1]]
    def rhs(t,flat):
        adj=flat[:size*count].reshape(size,count);a=mean_phase_coefficients(t,descriptor)
        F=a['F']*scale[None,:]/scale[:,None];b=a['b']/scale[:,None]
        return np.r_[(-F.T@adj).ravel(),(-adj.T@b).ravel()]
    # The final interval has zero adjoint; then cross each sample backwards.
    for k in range(len(times)-1,-1,-1):
        current+=impulses[k]
        initial=np.r_[current.ravel(),work.ravel()]
        sol=solve_ivp(rhs,(boundaries[k+1],boundaries[k]),initial,method='DOP853',rtol=rtol,atol=atol)
        if not sol.success or not np.isfinite(sol.y).all():raise RuntimeError(sol.message)
        current=sol.y[:size*count,-1].reshape(size,count);work=sol.y[size*count:,-1].reshape(count,64);nfev+=sol.nfev
    work*=amplitude[:,None]
    return dict(contraction=(work+direct).reshape(count,8,8),causal_source_work=work.reshape(count,8,8),
        direct_constitutive_target=direct.reshape(count,8,8),initial_advanced_adjoint=current*amplitude[None,:]/scale[:,None],
        function_evaluations=nfev,rtol=rtol,atol=atol,method='DOP853 with exact weighted target impulses',
        descriptor_phase_count=size,all_geometry_gauge_Gauss_and_H_rows_retained=True,
        scalar_only_inverse_used=False,complete_physical_native_or_Pauli_evaluated=False)


def forward_mean_target_contraction(descriptor, forward, *, target_times, target_loads):
    """Independent forward application of the same weighted readout."""
    n=descriptor['n']; total=np.zeros((target_loads.shape[2],64))
    for t,ell in zip(target_times,target_loads):
        z=forward['solution'](float(t));a=mean_phase_coefficients(t,descriptor)
        eta=np.vstack((z[:n],a['U']@z+a['f']));total+=ell.T@eta
    return total.reshape(target_loads.shape[2],8,8)


def _equilibrated_linear_solve(matrix, rhs):
    """Solve the complete finite descriptor step, never a saddle pseudoinverse."""
    row=1/np.max(abs(matrix),axis=1)
    column=1/np.max(abs(row[:,None]*matrix),axis=0)
    if not np.isfinite(row).all() or not np.isfinite(column).all():
        raise RuntimeError('zero complete descriptor step row/column')
    factor=lu_factor(row[:,None]*matrix*column[None,:])
    solution=column[:,None]*lu_solve(factor,row[:,None]*rhs)
    if not np.isfinite(solution).all():raise RuntimeError('nonfinite full descriptor step solution')
    denominator=np.linalg.norm(matrix,np.inf)*np.linalg.norm(solution,np.inf)+np.linalg.norm(rhs,np.inf)
    residual=float(np.linalg.norm(matrix@solution-rhs,np.inf)/denominator) if denominator else 0.
    return solution,residual


def mean_implicit_descriptor_step(descriptor, start, stop):
    """Compile one full midpoint Euler-Lagrange step without D(t)^-1.

    Unknowns are (x_new,p_new,v_mid,y_mid).  This is a numerical time
    discretization even when the instantaneous Legendre saddle changes
    inertia.  Its finite invertibility does not establish a regular
    continuous IVP through that crossing.
    """
    a,b=float(start),float(stop)
    if not np.isfinite(a+b) or a<descriptor['times'][0] or b>descriptor['times'][-1] or b<=a:
        raise ValueError('positive step inside the sampled action interval required')
    n,m=descriptor['n'],descriptor['m'];h=b-a;t=(a+b)/2
    H=descriptor['hessian'](t);J=descriptor['source'](t).reshape(2*n+m,64)
    size=3*n+m;K=np.zeros((size,size));R=np.zeros((size,2*n));j=np.zeros((size,64))
    K[:n,:n]=np.eye(n);K[:n,2*n:3*n]=-h*np.eye(n);R[:n,:n]=np.eye(n)
    K[n:2*n,:n]=-h/2*H[:n,:n];K[n:2*n,n:2*n]=np.eye(n)
    K[n:2*n,2*n:]=-h*H[:n,n:]
    R[n:2*n,:n]=h/2*H[:n,:n];R[n:2*n,n:]=np.eye(n);j[n:2*n]=h*J[:n]
    G=H[n:,:n];I=np.vstack((np.eye(n),np.zeros((m,n))))
    K[2*n:,:n]=G/2;K[2*n:,n:2*n]=-I/2;K[2*n:,2*n:]=H[n:,n:]
    R[2*n:,:n]=-G/2;R[2*n:,n:]=I/2;j[2*n:]=-J[n:]
    return dict(K=K,R=R,j=j,start=a,stop=b,midpoint=t,
        equation='xdot=v; pdot=Lxx*x+Lxv*v+Lxy*y+Jx; D[v;y]=[p-Lvx*x-Jv;-Lyx*x-Jy]',
        instantaneous_saddle_inverse_used=False)


def implicit_mean_source_target_application(descriptor, *, time_steps, target_times, target_loads, precision_bits=None):
    """Execute the joint finite causal descriptor and its exact discrete adjoint.

    Weighted readouts use linear x interpolation and the full step's
    midpoint v/y.  Forward and adjoint agree for this explicit temporal
    approximation; refinement is required before a continuous claim.
    The prescribed20 wall rows are retained separately as reactions.
    """
    if type(time_steps) is not int or time_steps<2:raise ValueError('explicit descriptor time_steps>=2 required')
    times=_real(target_times,'readout times');loads=_real(target_loads,'weighted joint readout')
    n,m=descriptor['n'],descriptor['m'];phase=2*n;size=3*n+m
    if times.ndim!=1 or len(times)==0 or np.any(np.diff(times)<=0):raise ValueError('ordered readout samples required')
    if loads.ndim!=3 or loads.shape[:2]!=(len(times),2*n+m):raise ValueError('complete reduced target value/rate/algebraic loads required')
    if times[0]<descriptor['times'][0] or times[-1]>descriptor['times'][-1]:raise ValueError('no readout extrapolation')
    grid=np.linspace(descriptor['times'][0],descriptor['times'][-1],time_steps+1)
    count=loads.shape[2];q_load=np.zeros((time_steps,size,count));old_load=np.zeros((time_steps,phase,count))
    for t,ell in zip(times,loads):
        k=min(int(np.searchsorted(grid,t,side='right')-1),time_steps-1);k=max(k,0)
        theta=(t-grid[k])/(grid[k+1]-grid[k]);q_load[k,:n]+=theta*ell[:n]
        q_load[k,phase:]+=ell[n:];old_load[k,:n]+=(1-theta)*ell[:n]
    if precision_bits is not None:
        return _arb_implicit_application(descriptor,grid,q_load,old_load,precision_bits)
    z=np.zeros((phase,64));forward=np.zeros((count,64));phase_values=[z.copy()];midpoint_values=[]
    steps=[];primal_residuals=[]
    for k in range(time_steps):
        step=mean_implicit_descriptor_step(descriptor,grid[k],grid[k+1])
        q,res=_equilibrated_linear_solve(step['K'],step['R']@z+step['j'])
        forward+=q_load[k].T@q+old_load[k].T@z
        z=q[:phase];phase_values.append(z.copy());midpoint_values.append(q[phase:].copy())
        steps.append(step);primal_residuals.append(res)
    adj=np.zeros((phase,count));work=np.zeros((count,64));adjoint_residuals=[]
    for k in range(time_steps-1,-1,-1):
        step=steps[k];rhs=q_load[k].copy();rhs[:phase]+=adj
        lam,res=_equilibrated_linear_solve(step['K'].T,rhs)
        work+=lam.T@step['j'];adj=step['R'].T@lam+old_load[k];adjoint_residuals.append(res)
    discrepancy=float(np.linalg.norm(work-forward));denominator=float(np.linalg.norm(forward))
    # Preserve all prescribed-wall rows, using the same midpoint weak rule.
    reactions=None;samples=descriptor['samples']
    if descriptor['full_hessian'] is not None:
        lift=samples['lift_to_full_mean'];wall=samples['rejected_wall_value_rows'];cv=samples['rejected_wall_canonical_rows']
        wall_value=[];wall_momentum=[]
        for k,wmid in enumerate(midpoint_values):
            xmid=(phase_values[k][:n]+phase_values[k+1][:n])/2;eta=lift@np.vstack((xmid,wmid))
            t=steps[k]['midpoint'];g=descriptor['full_hessian'](t)@eta+descriptor['full_source'](t).reshape(216,64)
            wall_value.append(g[wall]);wall_momentum.append(g[cv])
        wall_value=np.array(wall_value);wall_momentum=np.array(wall_momentum)
        momentum_rate=np.gradient(wall_momentum,(grid[:-1]+grid[1:])/2,axis=0,edge_order=1)
        reactions=wall_value.copy();reactions[:,:len(cv)]-=momentum_rate
    return dict(time_grid=grid,phase_values=np.array(phase_values).reshape(time_steps+1,phase,8,8),
        midpoint_value_rate_algebraic=np.array(midpoint_values).reshape(time_steps,n+m,8,8),
        forward_target=forward.reshape(count,8,8),adjoint_target=work.reshape(count,8,8),
        forward_adjoint_absolute_difference=discrepancy,
        forward_adjoint_relative_difference=discrepancy/denominator if denominator else None,
        maximum_primal_step_backward_error=max(primal_residuals),maximum_adjoint_step_backward_error=max(adjoint_residuals),
        prescribed_wall_reactions=None if reactions is None else reactions.reshape(time_steps,len(samples['rejected_wall_value_rows']),8,8),
        wall_reaction_time_derivative='finite difference of the same midpoint canonical wall cotangent; numerical approximation',
        initial_advanced_adjoint=adj,instantaneous_saddle_inverse_used=False,scalar_only_inverse_used=False,
        zero_initial_phase_scope='homogeneous differentiated retarded numerical core, not a selected physical E0 state',
        continuous_causal_regularity_established=False,physical_two_arm_domain_selected=False,
        complete_native_or_Pauli_evaluated=False)


def _arb_implicit_application(descriptor, grid, q_load, old_load, precision_bits):
    """Validated arithmetic for EXACT STORED finite-step coefficients only."""
    if type(precision_bits) is not int or precision_bits<96:raise ValueError('explicit Arb precision>=96 bits required')
    from flint import arb,arb_mat,ctx
    n,m=descriptor['n'],descriptor['m'];phase=2*n;count=q_load.shape[2];steps=len(grid)-1
    old_precision=ctx.prec;ctx.prec=precision_bits
    def matrix(value):return arb_mat([[arb(float(v)) for v in row] for row in value])
    def numeric(value):return np.array([[float(value[i,j].mid()) for j in range(value.ncols())] for i in range(value.nrows())])
    def upper(value):return float(np.nextafter(float(value.upper()),np.inf))
    def difference_upper(a,b):return max(upper(abs(a[i,j]-b[i,j])) for i in range(a.nrows()) for j in range(a.ncols()))
    def finite(value):return all(value[i,j].is_finite() for i in range(value.nrows()) for j in range(value.ncols()))
    try:
        # Compile the complete step before propagating intervals.  Propagating
        # K^-1*(R*z+j) directly repeatedly destroys its signed cancellations.
        # This is the SAME implicit step, never the instantaneous D inverse.
        mid=steps//2;s=mean_implicit_descriptor_step(descriptor,grid[mid],grid[mid+1])
        Q,_=_equilibrated_linear_solve(s['K'],s['R']);_,balance=matrix_balance(Q[:phase],permute=False)
        scale=np.diag(balance)
        z=arb_mat(phase,64);forward=arb_mat(count,64);states=[numeric(z)];wmid=[];compiled=[]
        for k in range(steps):
            s=mean_implicit_descriptor_step(descriptor,grid[k],grid[k+1]);K,R,j=(matrix(s[name]) for name in ('K','R','j'))
            coefficients=K.solve(matrix(np.column_stack((s['R'],s['j']))))
            if not finite(coefficients):raise RuntimeError('Arb full descriptor step did not certify finite coefficients')
            U=arb_mat([[coefficients[i,jj] for jj in range(phase)] for i in range(3*n+m)])
            f=arb_mat([[coefficients[i,phase+jj] for jj in range(64)] for i in range(3*n+m)])
            g=matrix(q_load[k]).transpose()*U+matrix(old_load[k]).transpose();direct=matrix(q_load[k]).transpose()*f
            T=arb_mat([[U[i,jj]*arb(float(scale[jj]/scale[i])) for jj in range(phase)] for i in range(phase)])
            force=arb_mat([[f[i,jj]/arb(float(scale[i])) for jj in range(64)] for i in range(phase)])
            g=arb_mat([[g[i,jj]*arb(float(scale[jj])) for jj in range(phase)] for i in range(count)])
            physical=arb_mat([[z[i,jj]*arb(float(scale[i])) for jj in range(64)] for i in range(phase)])
            q=U*physical+f;forward+=g*z+direct;z=T*z+force
            state=numeric(z)*scale[:,None];states.append(state);wmid.append(numeric(q)[phase:])
            compiled.append(dict(T=T,force=force,g=g,direct=direct))
        adj=arb_mat(phase,count);work=arb_mat(count,64)
        for k in range(steps-1,-1,-1):
            s=compiled[k];work+=adj.transpose()*s['force']+s['direct'];adj=s['T'].transpose()*adj+s['g'].transpose()
        discrepancy=difference_upper(work,forward)
        radius=max(upper(work[i,j].rad()) for i in range(count) for j in range(64))
        intervals_overlap=all(work[i,j].overlaps(forward[i,j]) for i in range(count) for j in range(64))
        values=numeric(work);denom=float(np.max(abs(values)))
        reactions=None;samples=descriptor['samples']
        if descriptor['full_hessian'] is not None:
            wall=samples['rejected_wall_value_rows'];cv=samples['rejected_wall_canonical_rows'];lift=samples['lift_to_full_mean']
            forces=[];momenta=[]
            for k,w in enumerate(wmid):
                eta=lift@np.vstack(((states[k][:n]+states[k+1][:n])/2,w));t=(grid[k]+grid[k+1])/2
                q=descriptor['full_hessian'](t)@eta+descriptor['full_source'](t).reshape(216,64)
                forces.append(q[wall]);momenta.append(q[cv])
            reactions=np.array(forces);reactions[:,:len(cv)]-=np.gradient(np.array(momenta),(grid[:-1]+grid[1:])/2,axis=0,edge_order=1)
        return dict(time_grid=grid,phase_values=np.array(states).reshape(steps+1,phase,8,8),
            midpoint_value_rate_algebraic=np.array(wmid).reshape(steps,n+m,8,8),
            forward_target=numeric(forward).reshape(count,8,8),adjoint_target=values.reshape(count,8,8),
            forward_adjoint_entrywise_difference_upper=discrepancy,
            forward_adjoint_relative_difference=discrepancy/denom if denom else None,
            exact_stored_forward_adjoint_intervals_overlap=intervals_overlap,
            exact_stored_target_entry_radius_upper=radius,precision_bits=precision_bits,
            prescribed_wall_reactions=None if reactions is None else reactions.reshape(steps,len(samples['rejected_wall_value_rows']),8,8),
            wall_reaction_scope='all20 rows retained; midpoint values and finite-difference canonical time derivative, not an Arb continuum enclosure',
            arithmetic_scope='Arb enclosures of exact stored binary64 K/R/J/readout coefficients; action assembly/interpolation and temporal continuum errors excluded',
            initial_advanced_adjoint=numeric(adj)/scale[:,None],whole_step_phase_balance=scale,
            interval_propagation='complete signed implicit transition compiled before interval application; no instantaneous saddle inverse',
            instantaneous_saddle_inverse_used=False,scalar_only_inverse_used=False,
            zero_initial_phase_scope='homogeneous differentiated retarded numerical core, not a selected physical E0 state',
            continuous_causal_regularity_established=False,physical_two_arm_domain_selected=False,
            complete_native_or_Pauli_evaluated=False)
    finally:ctx.prec=old_precision

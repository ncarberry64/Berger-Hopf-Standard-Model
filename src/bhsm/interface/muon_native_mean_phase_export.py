"""Outward phase export for the retained full implicit mean descriptor.

The fixed-step equations, source and discrete adjoint are identical to the
retained producer. This additive application additionally bounds every
binary64 phase/midpoint export, for a new independently certified target.
No instantaneous saddle inverse or continuous regularity is assumed.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import matrix_balance
from .muon_parent_mean_causal_descriptor import _real, _equilibrated_linear_solve, mean_implicit_descriptor_step

RETAINED_DESCRIPTOR_SOURCE_SHA256='3bdcf63a7c2dc89f47d077a80b50fc6adc9477a46ec2e8a79d2b26d35061de1b'

def implicit_mean_phase_export(descriptor, *, time_steps, target_times, target_loads, precision_bits=512):
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
    return _arb_export_application(descriptor,grid,q_load,old_load,precision_bits)


def _arb_export_application(descriptor, grid, q_load, old_load, precision_bits):
    """Validated arithmetic for EXACT STORED finite-step coefficients only."""
    if type(precision_bits) is not int or precision_bits<96:raise ValueError('explicit Arb precision>=96 bits required')
    from flint import arb,arb_mat,ctx
    n,m=descriptor['n'],descriptor['m'];phase=2*n;count=q_load.shape[2];steps=len(grid)-1
    old_precision=ctx.prec;ctx.prec=precision_bits
    def matrix(value):return arb_mat([[arb(float(v)) for v in row] for row in value])
    def numeric(value):return np.array([[float(value[i,j].mid()) for j in range(value.ncols())] for i in range(value.nrows())])
    def upper(value):return float(np.nextafter(float(value.upper()),np.inf))
    def difference_upper(a,b):return max(upper(abs(a[i,j]-b[i,j])) for i in range(a.nrows()) for j in range(a.ncols()))
    def export_errors(value, stored):
        return np.array([[upper(abs(value[i,j]-arb(float(stored[i,j])))) for j in range(value.ncols())] for i in range(value.nrows())])
    def finite(value):return all(value[i,j].is_finite() for i in range(value.nrows()) for j in range(value.ncols()))
    try:
        # Compile the complete step before propagating intervals.  Propagating
        # K^-1*(R*z+j) directly repeatedly destroys its signed cancellations.
        # This is the SAME implicit step, never the instantaneous D inverse.
        mid=steps//2;s=mean_implicit_descriptor_step(descriptor,grid[mid],grid[mid+1])
        Q,_=_equilibrated_linear_solve(s['K'],s['R']);_,balance=matrix_balance(Q[:phase],permute=False)
        scale=np.diag(balance)
        z=arb_mat(phase,64);forward=arb_mat(count,64);states=[numeric(z)];wmid=[];compiled=[];state_errors=[np.zeros((phase,64))];midpoint_errors=[]
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
            state=numeric(z)*scale[:,None];states.append(state)
            exact_state=arb_mat([[z[i,jj]*arb(float(scale[i])) for jj in range(64)] for i in range(phase)])
            state_errors.append(export_errors(exact_state,state))
            middle=numeric(q)[phase:];wmid.append(middle)
            exact_middle=arb_mat([[q[phase+i,jj] for jj in range(64)] for i in range(n+m)])
            midpoint_errors.append(export_errors(exact_middle,middle))
            compiled.append(dict(T=T,force=force,g=g,direct=direct))
        adj=arb_mat(phase,count);work=arb_mat(count,64)
        for k in range(steps-1,-1,-1):
            s=compiled[k];work+=adj.transpose()*s['force']+s['direct'];adj=s['T'].transpose()*adj+s['g'].transpose()
        discrepancy=difference_upper(work,forward)
        radius=max(upper(work[i,j].rad()) for i in range(count) for j in range(64))
        intervals_overlap=all(work[i,j].overlaps(forward[i,j]) for i in range(count) for j in range(64))
        values=numeric(work);denom=float(np.max(abs(values)))
        exported_adjoint=numeric(adj)/scale[:,None]
        exact_adjoint=arb_mat([[adj[i,jj]/arb(float(scale[i])) for jj in range(count)] for i in range(phase)])
        adjoint_errors=export_errors(exact_adjoint,exported_adjoint)
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
            phase_export_entry_error_bounds=np.array(state_errors).reshape(steps+1,phase,8,8),
            midpoint_export_entry_error_bounds=np.array(midpoint_errors).reshape(steps,n+m,8,8),
            exact_stored_phase_export_entry_error_upper=float(np.max(state_errors)),
            exact_stored_midpoint_export_entry_error_upper=float(np.max(midpoint_errors)),
            initial_advanced_adjoint_export_entry_error_bounds=adjoint_errors,
            exact_stored_initial_adjoint_export_entry_error_upper=float(np.max(adjoint_errors)),
            export_error_scope='abs(exact-stored Arb interval - exact binary64 exported midpoint), including binary64 conversion',
            forward_target=numeric(forward).reshape(count,8,8),adjoint_target=values.reshape(count,8,8),
            forward_adjoint_entrywise_difference_upper=discrepancy,
            forward_adjoint_relative_difference=discrepancy/denom if denom else None,
            exact_stored_forward_adjoint_intervals_overlap=intervals_overlap,
            exact_stored_target_entry_radius_upper=radius,precision_bits=precision_bits,
            prescribed_wall_reactions=None if reactions is None else reactions.reshape(steps,len(samples['rejected_wall_value_rows']),8,8),
            wall_reaction_scope='all20 rows retained; midpoint values and finite-difference canonical time derivative, not an Arb continuum enclosure',
            arithmetic_scope='Arb enclosures of exact stored binary64 K/R/J/readout coefficients; action assembly/interpolation and temporal continuum errors excluded',
            initial_advanced_adjoint=exported_adjoint,whole_step_phase_balance=scale,
            interval_propagation='complete signed implicit transition compiled before interval application; no instantaneous saddle inverse',
            instantaneous_saddle_inverse_used=False,scalar_only_inverse_used=False,
            zero_initial_phase_scope='homogeneous differentiated retarded numerical core, not a selected physical E0 state',
            continuous_causal_regularity_established=False,physical_two_arm_domain_selected=False,
            complete_native_or_Pauli_evaluated=False)
    finally:ctx.prec=old_precision

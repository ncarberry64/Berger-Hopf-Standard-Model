"""Pair the reached heat target with actual certified finite-descriptor phases.

This is a numerical discrete form, not a continuous IVP or native-domain
claim. Interpolation and coordinate lifting are performed with Arb; the
target FE/reference and higher-even allowances are kept visible.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from flint import arb,arb_mat,ctx

from .muon_native_even_y_remainder_certificate import ROOT

TARGET='artifacts/muon_native_even_y_target_certificate_20261010/run_4'
TARGET_HASHES={'target_certificate.json':'6890a7d3ce6985534e100751a97bddb7dedff7ad7a88f2efae9083243c92a934',
    'target_bounds.npz':'82ff89f70a18ce9193c2197899b890e32973cfa5a2d16a62ac14f60b0f40077f'}
TAIL='artifacts/muon_native_even_y_remainder_certificate_20261010/run_4'
TAIL_HASHES={'remainder_certificate.json':'4d853d1f033c3b1e14d58d6fce33051f8f0c742aefb540b251de818d1e161c94',
    'remainder_bounds.npz':'5b4ce92b420b323425294c124952952204ecd3b38c8f69f6d234248b57349f1a'}
CROSSING='artifacts/muon_mean_kinetic_crossing_diagnostic_20261010/run_2/diagnostic.json'
CROSSING_HASH='28003779b537c9cdf16052b45fb3621f8ed1b86a7a9ad9cd2fc27584b5540fe7'
LEGACY='artifacts/muon_native_mean_causal_heat_20261010/run_3'
LEGACY_HASH='d2bc14c47b9705f844832a05b34d08559a313e9dbcb73126b3b6735764609c13'


def _end_float(value,upper):
    if value.is_zero():return 0.
    return float(np.nextafter(float(value.upper() if upper else value.lower()),np.inf if upper else -np.inf))


def _bounds(matrix):
    lower=np.zeros((matrix.nrows(),matrix.ncols()));upper=lower.copy()
    for i in range(matrix.nrows()):
        for j in range(matrix.ncols()):
            lower[i,j]=_end_float(matrix[i,j],False);upper[i,j]=_end_float(matrix[i,j],True)
    return lower.reshape(8,8),upper.reshape(8,8)


def _nonnegative(value,name):
    v=np.asarray(value,float)
    if not np.all(np.isfinite(v)) or np.any(v<0):raise ValueError(name+' must be finite nonnegative bounds')
    return v


def interpolate_phase_interval(grid,phase,phase_error,midpoint,midpoint_error,time):
    """SAME finite convention: linear x, full-step midpoint v/y."""
    grid=np.asarray(grid,float);phase=np.asarray(phase,float);midpoint=np.asarray(midpoint,float)
    if grid.ndim!=1 or len(grid)<3 or not np.all(np.isfinite(grid)) or np.any(np.diff(grid)<=0):
        raise ValueError('increasing finite descriptor grid required')
    if phase.ndim!=3 or phase.shape[0]!=len(grid) or phase.shape[2]!=64 or phase.shape[1]%2:
        raise ValueError('complete x/p phases with64 actual source pairs required')
    if midpoint.ndim!=3 or midpoint.shape[0]!=len(grid)-1 or midpoint.shape[2]!=64:
        raise ValueError('complete step midpoint v/y and64 source pairs required')
    if not np.all(np.isfinite(phase)) or not np.all(np.isfinite(midpoint)):
        raise ValueError('finite actual phase/midpoint entries required')
    pe=np.broadcast_to(_nonnegative(phase_error,'phase export error'),phase.shape)
    me=np.broadcast_to(_nonnegative(midpoint_error,'midpoint export error'),midpoint.shape)
    if not np.isfinite(time) or time<grid[0] or time>grid[-1]:raise ValueError('no descriptor phase extrapolation')
    k=min(max(int(np.searchsorted(grid,time,side='right')-1),0),len(grid)-2)
    theta=(arb(float(time))-arb(float(grid[k])))/(arb(float(grid[k+1]))-arb(float(grid[k])))
    n=phase.shape[1]//2;result=arb_mat(n+midpoint.shape[1],64)
    for i in range(n):
        for j in range(64):
            left=arb(float(phase[k,i,j]),float(pe[k,i,j]));right=arb(float(phase[k+1,i,j]),float(pe[k+1,i,j]))
            result[i,j]=(1-theta)*left+theta*right
    for i in range(midpoint.shape[1]):
        for j in range(64):result[n+i,j]=arb(float(midpoint[k,i,j]),float(me[k,i,j]))
    return result,k,theta


def _lift_interval(lift,value):
    if isinstance(lift,arb_mat):
        if lift.ncols()!=value.nrows():raise ValueError('SAME-action coordinate lift must align')
        return lift*value
    a=np.asarray(lift,float)
    if a.ndim!=2 or a.shape[1]!=value.nrows() or not np.all(np.isfinite(a)):
        raise ValueError('finite SAME-action coordinate lift required')
    result=arb_mat(a.shape[0],value.ncols())
    for i,row in enumerate(a):
        for k in np.flatnonzero(row):
            coefficient=arb(float(row[k]))
            for j in range(value.ncols()):result[i,j]+=coefficient*value[k,j]
    return result


def pair_target_phase_intervals(target_lower,target_upper,FE_error,Y4_error,times,
        grid,phase,phase_error,midpoint,midpoint_error,lift,*,precision_bits=192):
    """Consume actual weighted targets once; no second density insertion."""
    lo=np.asarray(target_lower,float);hi=np.asarray(target_upper,float);times=np.asarray(times,float)
    if lo.ndim!=2 or hi.shape!=lo.shape or times.shape!=(len(lo),) or np.any(hi<lo) or not np.all(np.isfinite(lo)) or not np.all(np.isfinite(hi)):
        raise ValueError('ordered finite target endpoint arrays required')
    fe=_nonnegative(FE_error,'FE target allowance');tail=_nonnegative(Y4_error,'Y4 target allowance')
    lift_rows=lift.nrows() if isinstance(lift,arb_mat) else np.shape(lift)[0]
    if fe.shape!=lo.shape or tail.shape!=lo.shape or lift_rows!=lo.shape[1]:
        raise ValueError('target bounds and raw coordinate lift must align')
    if type(precision_bits) is not int or precision_bits<128:raise ValueError('explicit Arb precision>=128 required')
    previous=ctx.prec
    try:
        ctx.prec=precision_bits;reference=arb_mat(1,64);FE=arb_mat(1,64);Y4=arb_mat(1,64)
        for s,t in enumerate(times):
            reduced,_,_=interpolate_phase_interval(grid,phase,phase_error,midpoint,midpoint_error,float(t))
            raw=_lift_interval(lift,reduced)
            for i in range(lo.shape[1]):
                target=arb(float(lo[s,i])).union(arb(float(hi[s,i])))
                for j in range(64):
                    reference[0,j]+=target*raw[i,j]
                    magnitude=raw[i,j].abs_upper()
                    FE[0,j]+=arb(float(fe[s,i]))*magnitude
                    Y4[0,j]+=arb(float(tail[s,i]))*magnitude
        total=arb_mat(1,64)
        for j in range(64):total[0,j]=reference[0,j]+arb(0,(FE[0,j]+Y4[0,j]).upper())
        rlo,rhi=_bounds(reference);lo_all,hi_all=_bounds(total)
        fe_upper=np.array([_end_float(FE[0,j],True) for j in range(64)]).reshape(8,8)
        y4_upper=np.array([_end_float(Y4[0,j],True) for j in range(64)]).reshape(8,8)
        trace=sum((total[0,9*j] for j in range(8)),arb(0))
        return dict(reference_lower=rlo,reference_upper=rhi,total_lower=lo_all,total_upper=hi_all,
            FE_reference_allowance_upper=fe_upper,Y4_allowance_upper=y4_upper,
            channel_trace_lower=_end_float(trace,False),channel_trace_upper=_end_float(trace,True),
            sample_density_reapplied=False,continuous_temporal_error_enclosed=False,
            interpolation_division_outward=True,complete_native_or_Pauli_evaluated=False)
    finally:ctx.prec=previous


def critical_phase_compatibility(grid,phase,phase_error,critical,*,precision_bits=192):
    """Evaluate the floating-spline crossing row on reached finite phases."""
    p=np.asarray(phase,float);grid=np.asarray(grid,float);pe=np.broadcast_to(_nonnegative(phase_error,'phase error'),p.shape)
    row=np.asarray(critical['phase_row'],float);source=np.asarray(critical['source_row'],float).reshape(64)
    time=float(critical['numerical_root_time'])
    if row.shape!=(p.shape[1],) or source.shape!=(64,) or time<grid[0] or time>grid[-1]:
        raise ValueError('critical phase/source row and reached phase domain must agree')
    previous=ctx.prec
    try:
        ctx.prec=precision_bits;k=min(max(int(np.searchsorted(grid,time,side='right')-1),0),len(grid)-2)
        theta=(arb(time)-arb(float(grid[k])))/(arb(float(grid[k+1]))-arb(float(grid[k])))
        result=arb_mat(1,64);denominator=0.
        for j in range(64):
            result[0,j]=arb(float(source[j]));scale=arb(abs(float(source[j])))
            for i,coefficient in enumerate(row):
                z=(1-theta)*arb(float(p[k,i,j]),float(pe[k,i,j]))+theta*arb(float(p[k+1,i,j]),float(pe[k+1,i,j]))
                result[0,j]+=arb(float(coefficient))*z;scale+=arb(abs(float(coefficient)))*z.abs_upper()
            denominator=max(denominator,_end_float(scale,True))
        lo,hi=_bounds(result)
        return dict(residual_lower=lo,residual_upper=hi,
            residual_absolute_upper=float(max(np.max(abs(lo)),np.max(abs(hi)))),
            absolute_term_scale_upper=denominator,numerical_crossing_time=time,
            floating_crossing_row_and_root_errors_not_enclosed=True,
            finite_interpolated_phase_only=True,continuous_constitutive_compatibility_proved=False,
            source_row_alone_is_not_a_failure_verdict=True)
    finally:ctx.prec=previous


def load_reached_target_bounds(repository=ROOT):
    root=Path(repository);records=[]
    for folder,pins in ((TARGET,TARGET_HASHES),(TAIL,TAIL_HASHES)):
        for name,digest in pins.items():
            raw=(root/folder/name).read_bytes()
            if sha256(raw).hexdigest()!=digest:raise ValueError('pinned reached target/tail changed: '+name)
            records.append(dict(path=folder+'/'+name,bytes=len(raw),sha256=digest))
    raw=(root/CROSSING).read_bytes()
    if sha256(raw).hexdigest()!=CROSSING_HASH:raise ValueError('pinned critical row changed')
    records.append(dict(path=CROSSING,bytes=len(raw),sha256=CROSSING_HASH))
    with np.load(root/TARGET/'target_bounds.npz',allow_pickle=False) as archive:target={k:archive[k] for k in archive.files}
    with np.load(root/TAIL/'remainder_bounds.npz',allow_pickle=False) as archive:tail={k:archive[k] for k in archive.files}
    if not np.array_equal(target['coefficient_time_samples'],tail['coefficient_time_samples']):raise ValueError('target/tail samples differ')
    return target,tail,json.loads(raw)['numerical_crossing_compatibility'],records


def unbounded_export_mesh_diagnostics(meshes,target_lower,target_upper,times,lift,critical):
    """Numerical mesh differences; missing phase errors remain unknown.

    This never calls the interval consumer with a substituted zero error.
    The target midpoint and exported finite phases give diagnostic centers
    only, even though the target itself has a separate certificate.
    """
    target=(np.asarray(target_lower,float)+np.asarray(target_upper,float))/2
    times=np.asarray(times,float);lift=np.asarray(lift,float)
    row=np.asarray(critical['phase_row'],float);source=np.asarray(critical['source_row'],float).reshape(64)
    root_time=float(critical['numerical_root_time']);outputs=[]
    for mesh in meshes:
        grid=np.asarray(mesh['time_grid'],float);phase=np.asarray(mesh['phase_values'],float)
        mid=np.asarray(mesh['midpoint_value_rate_algebraic'],float)
        if phase.ndim!=3 or phase.shape[0]!=len(grid) or phase.shape[2]!=64 or phase.shape[1]%2:
            raise ValueError('complete numerical x/p phases required')
        n=phase.shape[1]//2
        if mid.shape[0]!=len(grid)-1 or mid.shape[2]!=64 or lift.shape!=(target.shape[1],n+mid.shape[1]):
            raise ValueError('numerical midpoint, lift and target dimensions must agree')
        if np.any(np.diff(grid)<=0) or times[0]<grid[0] or times[-1]>grid[-1] or root_time<grid[0] or root_time>grid[-1]:
            raise ValueError('numerical diagnostic must stay in the retained domain')
        if not all(np.all(np.isfinite(v)) for v in (target,times,lift,grid,phase,mid,row,source)):
            raise ValueError('finite numerical diagnostic operands required')
        result=np.zeros(64)
        for ell,t in zip(target,times):
            k=min(max(int(np.searchsorted(grid,t,side='right')-1),0),len(grid)-2)
            theta=(t-grid[k])/(grid[k+1]-grid[k])
            x=(1-theta)*phase[k,:n]+theta*phase[k+1,:n]
            result+=ell@(lift@np.vstack((x,mid[k])))
        k=min(max(int(np.searchsorted(grid,root_time,side='right')-1),0),len(grid)-2)
        theta=(root_time-grid[k])/(grid[k+1]-grid[k]);z=(1-theta)*phase[k]+theta*phase[k+1]
        residual=row@z+source;scale=np.abs(row)@np.abs(z)+np.abs(source)
        outputs.append(dict(time_steps=len(grid)-1,reference_center=result.reshape(8,8),
            reference_channel_trace=float(np.trace(result.reshape(8,8))),
            critical_residual_center=residual.reshape(8,8),critical_residual_absolute_max=float(np.max(abs(residual))),
            critical_absolute_term_scale_max=float(np.max(scale)),phase_export_error_upper=None,
            midpoint_export_error_upper=None,finite_readout_interval_certified=False,
            continuous_constitutive_compatibility_proved=False))
    outputs.sort(key=lambda v:v['time_steps'])
    if len({v['time_steps'] for v in outputs})!=len(outputs):raise ValueError('distinct diagnostic meshes required')
    differences=[]
    for a,b in zip(outputs[:-1],outputs[1:]):
        change=b['reference_center']-a['reference_center']
        differences.append(dict(coarse_steps=a['time_steps'],fine_steps=b['time_steps'],
            reference_center_difference=change,channel_trace_difference=float(np.trace(change)),
            Frobenius_difference=float(np.linalg.norm(change)),continuous_mesh_error_bound_inferred=False))
    return dict(classification='NUMERICAL_LEGACY_MESH_AND_CRITICAL_ROW_DIAGNOSTIC',
        finite_applications=outputs,mesh_differences=differences,
        missing_phase_export_errors_replaced_with_zero=False,
        target_center_only=True,floating_crossing_row_and_root_errors_not_enclosed=True,
        continuous_temporal_error_enclosed=False)


def retained_legacy_mesh_diagnostics(repository=ROOT):
    """Read the unchanged32/64/128 exports without another descriptor solve."""
    from .muon_parent_mean_causal_descriptor import certified_sampled_mean_descriptor
    from .muon_parent_mean_causal_action import mean_coordinate_lift
    root=Path(repository);folder=root/LEGACY;raw=(folder/'mean_causal_heat.json').read_bytes()
    if sha256(raw).hexdigest()!=LEGACY_HASH:raise ValueError('pinned legacy mean application changed')
    receipt=json.loads(raw);records=[dict(path=LEGACY+'/mean_causal_heat.json',bytes=len(raw),sha256=LEGACY_HASH)]
    for entry in receipt['source_records']+receipt['consumed_input_records']:
        data=(root/entry['path']).read_bytes()
        if len(data)!=entry['bytes'] or sha256(data).hexdigest()!=entry['sha256']:
            raise ValueError('legacy diagnostic source/input changed: '+entry['path'])
    values={}
    for entry in receipt['matrix_archives']:
        data=(folder/entry['path']).read_bytes()
        if len(data)!=entry['bytes'] or sha256(data).hexdigest()!=entry['sha256']:
            raise ValueError('legacy diagnostic archive changed')
        records.append(dict(path=LEGACY+'/'+entry['path'],bytes=len(data),sha256=entry['sha256']))
        with np.load(folder/entry['path'],allow_pickle=False) as archive:
            for key in archive.files:
                if key in values:raise ValueError('duplicate legacy diagnostic array')
                values[key]=archive[key]
    for key,entry in receipt['array_records'].items():
        value=np.ascontiguousarray(values[key])
        if list(value.shape)!=entry['shape'] or str(value.dtype)!=entry['dtype'] or sha256(value.tobytes()).hexdigest()!=entry['raw_sha256']:
            raise ValueError('legacy diagnostic array identity changed: '+key)
    target,_,critical,target_records=load_reached_target_bounds(root)
    samples=certified_sampled_mean_descriptor(root)['samples']
    lift=mean_coordinate_lift(samples['raw_gauge_labels'])['lift']@samples['lift_to_full_mean']
    meshes=[]
    for steps in (32,64,128):
        prefix='steps_'+str(steps)+'_'
        phase=values[prefix+'phase_values'];mid=values[prefix+'midpoint_value_rate_algebraic']
        if phase.shape!=(steps+1,148,8,8) or mid.shape!=(steps,106,8,8):raise ValueError('complete legacy finite phase layout required')
        meshes.append(dict(time_grid=values[prefix+'time_grid'],phase_values=phase.reshape(steps+1,148,64),
            midpoint_value_rate_algebraic=mid.reshape(steps,106,64)))
    result=unbounded_export_mesh_diagnostics(meshes,target['reference_paired_Y2_target_lower'],
        target['reference_paired_Y2_target_upper'],target['response_time_samples'],lift,critical)
    result['input_records']=records+target_records
    return result


def retained_paired_readout(phase_directories,*,repository=ROOT,precision_bits=192):
    """Consume actual exported phases; missing export errors cannot be zeroed."""
    from .muon_parent_mean_causal_descriptor import certified_sampled_mean_descriptor
    from .muon_parent_mean_causal_action import mean_coordinate_lift
    root=Path(repository);target,tail,critical,target_records=load_reached_target_bounds(root)
    descriptor=certified_sampled_mean_descriptor(root);samples=descriptor['samples']
    P=mean_coordinate_lift(samples['raw_gauge_labels'])['lift'];Q=samples['lift_to_full_mean']
    previous=ctx.prec;ctx.prec=precision_bits
    try:lift=arb_mat(P.tolist())*arb_mat(Q.tolist())
    finally:ctx.prec=previous
    outputs=[];inputs=list(target_records)
    for directory in phase_directories:
        folder=Path(directory)
        if not folder.is_absolute():folder=root/folder
        raw=(folder/'mean_phase_export.json').read_bytes();receipt=json.loads(raw)
        if receipt['classification']!='EVALUATED_EXACT_STORED_FINITE_DESCRIPTOR_PHASE_EXPORT_WITH_ENTRYWISE_ERRORS':
            raise ValueError('actual finite descriptor export with entrywise error bounds required')
        inputs.append(dict(path=str((folder/'mean_phase_export.json').relative_to(root)).replace('\\','/'),bytes=len(raw),sha256=sha256(raw).hexdigest()))
        for row in receipt['source_records']+receipt['consumed_input_records']:
            data=(root/row['path']).read_bytes()
            if len(data)!=row['bytes'] or sha256(data).hexdigest()!=row['sha256']:
                raise ValueError('phase/action/source provenance changed: '+row['path'])
        values={}
        for row in receipt['matrix_archives']:
            path=folder/row['path'];data=path.read_bytes()
            if len(data)!=row['bytes'] or sha256(data).hexdigest()!=row['sha256']:
                raise ValueError('actual phase archive identity changed')
            inputs.append(dict(path=str(path.relative_to(root)).replace('\\','/'),bytes=len(data),sha256=row['sha256']))
            with np.load(path,allow_pickle=False) as archive:
                for k in archive.files:
                    if k in values:raise ValueError('duplicate phase archive operand')
                    values[k]=archive[k]
        for key,row in receipt['array_records'].items():
            value=np.ascontiguousarray(values[key])
            if list(value.shape)!=row['shape'] or str(value.dtype)!=row['dtype'] or sha256(value.tobytes()).hexdigest()!=row['raw_sha256']:
                raise ValueError('phase array metadata disagreement: '+key)
        required=('phase_export_entry_error_bounds','midpoint_export_entry_error_bounds')
        if any(k not in values for k in required):raise ValueError('actual phase and midpoint export bounds cannot be omitted')
        steps=receipt['time_steps'];grid=values['time_grid'];phase=values['phase_values'];mid=values['midpoint_value_rate_algebraic']
        pe=values[required[0]];me=values[required[1]]
        if phase.shape!=(steps+1,148,8,8) or mid.shape!=(steps,106,8,8) or pe.shape!=phase.shape or me.shape!=mid.shape:
            raise ValueError('actual x74/p74/v74/y32 phase layout required')
        if np.max(pe)!=receipt['exact_stored_phase_export_entry_error_upper'] or np.max(me)!=receipt['exact_stored_midpoint_export_entry_error_upper']:
            raise ValueError('phase export error maxima disagree with receipt')
        if not receipt['exact_stored_forward_adjoint_intervals_overlap']:
            raise ValueError('retained finite forward/adjoint interval identity failed')
        if not np.array_equal(values['target_times'],target['response_time_samples']):raise ValueError('descriptor and certified target sample domains differ')
        result=pair_target_phase_intervals(target['reference_paired_Y2_target_lower'],target['reference_paired_Y2_target_upper'],
            target['actual_FE_Y2_target_reference_difference_upper'],tail['weighted_directional_tail_upper'],target['response_time_samples'],
            grid,phase.reshape(steps+1,148,64),pe.reshape(steps+1,148,64),
            mid.reshape(steps,106,64),me.reshape(steps,106,64),lift,precision_bits=precision_bits)
        compatibility=critical_phase_compatibility(grid,phase.reshape(steps+1,148,64),pe.reshape(steps+1,148,64),critical,precision_bits=precision_bits)
        outputs.append(dict(time_steps=steps,paired_readout=result,critical_spline_compatibility=compatibility,
            original_numeric_target_adjoint=receipt['adjoint_target'],
            original_numeric_target_channel_trace=receipt['paired_channel_trace'],
            actual_phase_export_error_upper=receipt['exact_stored_phase_export_entry_error_upper'],
            actual_midpoint_export_error_upper=receipt['exact_stored_midpoint_export_entry_error_upper']))
    outputs.sort(key=lambda x:x['time_steps'])
    if len({r['time_steps'] for r in outputs})!=len(outputs):raise ValueError('distinct finite meshes required')
    differences=[]
    for coarse,fine in zip(outputs[:-1],outputs[1:]):
        A=coarse['paired_readout'];B=fine['paired_readout']
        lo=B['total_lower']-A['total_upper'];hi=B['total_upper']-A['total_lower']
        lower=np.nextafter(lo,-np.inf);upper=np.nextafter(hi,np.inf)
        centersA=(A['reference_lower']+A['reference_upper'])/2;centersB=(B['reference_lower']+B['reference_upper'])/2
        differences.append(dict(coarse_steps=coarse['time_steps'],fine_steps=fine['time_steps'],
            finite_readout_difference_lower=lower,finite_readout_difference_upper=upper,
            reference_center_Frobenius_difference=float(np.linalg.norm(centersB-centersA)),
            continuous_mesh_error_bound_inferred=False))
    packet=dict(classification='OUTWARD_REACHED_FINITE_DESCRIPTOR_PAIRED_NATIVE_CORE_READOUT',
        input_records=inputs,precision_bits=precision_bits,finite_applications=outputs,finite_mesh_differences=differences,
        source_order='raw betaPhoton source pair8x8',target_sign='middle minus light',
        source_domain_scope='retained outgoing24 backward finite germ; source numerical core, not physical incoming/child history',
        target_scope='positive-Hilbert n0 product core, not full graded supertrace',
        weighted_density_reapplied=False,phase_interpolation_and_basis_product_enclosed=True,
        FE_reference_and_even_Y_tail_errors_propagated=True,
        continuous_temporal_or_quadrature_error_enclosed=False,
        upstream_field_FE_entry_production_errors_enclosed=False,
        physical_two_arm_cutoff_or_primal_selected=False,complete_native_or_Pauli_evaluated=False)
    return packet

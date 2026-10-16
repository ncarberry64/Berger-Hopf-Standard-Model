"""Isolated full original-Maxwell EM-column radial comparison.

No history, profile solve, physical state, or coupled correction is made.
The frozen four-profile coordinate basis is reused at every quadrature rule.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

REPO=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
OFFICIAL='artifacts/electromagnetic_carrier_original_maxwell_20261016/run_2'
EXPECTED_RESULT='79072b58e6cd13f0297a4efbcc65543822a5ef5260187b219e491d96fedae38b'
EXPECTED_ARCHIVE='2eb865ae7b9e73edc236085655954919bd8fc0eed78a15fd034a8774b1384bb0'
sys.path[:0]=[str(REPO/'src'),str(REPO/'scripts')]
from evaluate_em_carrier_original_maxwell_20261016 import PHASES,snapshot,rows,direction,real
from bhsm.interface.electromagnetic_carrier_original_maxwell import even_angular_space
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

def digest(path):return sha256(Path(path).read_bytes()).hexdigest()

def write_json(path,data):
    Path(path).write_bytes((json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())

def row_label(index):
    kind,index=divmod(int(index),800)
    r,f,c,h=np.unravel_index(index,(4,5,4,10))
    return dict(kind=('value','rate')[kind],radial=int(r),field=int(f),internal=int(c),harmonic=int(h))

def column_label(index):
    kind,index=divmod(int(index),16);r,m=divmod(index,4)
    return dict(kind=('amplitude','rate')[kind],radial=r,mode=m)

def metric(old,new,*,operator=False):
    old,new=np.asarray(old),np.asarray(new)
    if old.shape!=new.shape or not np.isfinite(old).all()or not np.isfinite(new).all():
        raise ValueError('same finite coordinate arrays required')
    difference=new-old;absolute=np.abs(difference)
    magnitude=np.maximum(np.abs(old),np.abs(new))
    scaled=absolute/np.maximum(1.,magnitude)
    relative=np.divide(absolute,magnitude,out=np.zeros_like(absolute),where=magnitude!=0)
    def worst(values):
        i=np.unravel_index(int(np.argmax(values)),values.shape)
        item=dict(index=[int(v)for v in i],error=float(values[i]),old=float(old[i]),new=float(new[i]),difference=float(difference[i]))
        if operator:item.update(row=row_label(i[0]),column=column_label(i[1]))
        return item
    return dict(shape=list(old.shape),absolute=worst(absolute),entrywise_scaled=worst(scaled),
        relative_nonzero=worst(relative),relative_Frobenius=float(np.linalg.norm(difference)/max(np.linalg.norm(old),np.linalg.norm(new),np.finfo(float).tiny)),
        absolute_guard_2e10=bool(np.max(absolute)<=2e-10),scaled_guard_2e10=bool(np.max(scaled)<=2e-10))

def evaluate(phase,order,space):
    t=phase['receipt']['span']/2;snap=snapshot(phase,t,order,space)
    base=rows(snap);value=real(base['value_rows']).ravel();rate=real(base['rate_rows']).ravel()
    columns=[]
    for is_rate in(False,True):
        for radial in range(4):
            for mode in range(4):
                delta=direction(snap,radial,mode,rate=is_rate)
                changed=[v.astype(complex)+1e-20j*d for v,d in zip(snap['fields'],delta)]
                applied=rows(snap,changed)
                columns.append(np.r_[applied['value_rows'].imag.ravel(),applied['rate_rows'].imag.ravel()]/1e-20)
    operator=np.column_stack(columns)
    if operator.shape!=(1600,32):raise ValueError('all original rows and32 directions required')
    basis=phase['representation']
    diagnostic=dict(order=order,coordinate_time=t,radial_profile_count=snap['b'].shape[1],
        basis_value_max_by_profile=np.max(abs(snap['b']),axis=0).tolist(),
        basis_radial_max_by_profile=np.max(abs(snap['br']),axis=0).tolist(),
        fixed_source_complement_norm=float(basis['affine_complement_norm']),
        fixed_interior_projection=np.asarray(basis['affine_interior_projection']).tolist(),
        fixed_wall_coefficient=float(basis['affine_wall_coefficient']),
        raw_midpoint_sha256=sha256(np.asarray(phase['arrays'][phase['stage_key']]).tobytes()).hexdigest(),
        positive_density_min_by_slot=np.min(snap['densities'][:,0,:4],axis=0).tolist(),
        all_retained_real=True,source_profiles_renormalized=False)
    return dict(value=value,rate=rate,operator=operator,kinetic=snap['kinetic'],
        charge=snap['charge'],charge_rate=snap['charge_rate'],
        inclusion=snap['s'],inclusion_rate=snap['sd'],rho=snap['rho'],weights=snap['wr'],
        basis=snap['b'],basis_radial=snap['br']),diagnostic

def comparisons(old,new):
    gauss=np.arange(800).reshape(4,5,4,10)[:,0].ravel()
    result={k:metric(old[k],new[k],operator=k=='operator')for k in('value','rate','kinetic','operator')}
    result['Gauss_value_rows']=metric(old['value'][gauss],new['value'][gauss])
    result['Gauss_operator_rows']=metric(old['operator'][gauss],new['operator'][gauss])
    result['Gauss_rate_rows']=metric(old['rate'][gauss],new['rate'][gauss])
    result['Gauss_rate_operator_rows']=metric(old['operator'][800+gauss],new['operator'][800+gauss])
    result['same_inclusion_and_motion_bitwise']=bool(np.array_equal(old['inclusion'],new['inclusion'])and np.array_equal(old['inclusion_rate'],new['inclusion_rate']))
    if not result['same_inclusion_and_motion_bitwise']:raise ValueError('amplitude/rate coordinate inclusion changed across radial rules')
    return result

def main(output):
    out=Path(output)
    if out.exists():raise FileExistsError('preserve independent readouts')
    source_bytes=Path(__file__).read_bytes();out.mkdir(parents=True)
    (out/'executed_source.py').write_bytes(source_bytes)
    reference=REPO/OFFICIAL
    if digest(reference/'result.json')!=EXPECTED_RESULT or digest(reference/'application.npz')!=EXPECTED_ARCHIVE:
        raise ValueError('official same-primal reference changed')
    official=json.loads((reference/'result.json').read_bytes())
    for p,h in official['input_and_source_sha256'].items():
        if digest(REPO/p)!=h:raise ValueError('official source/input changed: '+p)
    if official['coupled_corrections']!=0 or official['full_physical_outgoing_derivative_at_guard']:
        raise ValueError('unexpected promoted reference')
    with np.load(reference/'application.npz',allow_pickle=False)as f:saved={k:f[k].copy()for k in f.files}
    space=even_angular_space();arrays={};records=[]
    for side,path in PHASES.items():
        phase=load_profile_preserving_phase(path,repository=REPO)
        rec=next(r for r in official['records']if r['side']==side)
        if rec['radial_refinement'][-1]['order']!=96:raise ValueError('reference is not radial96')
        old=dict(value=saved[side+'_original_value'],rate=saved[side+'_original_rate'],
            operator=saved[side+'_full1600_by32_local_field_operator'],kinetic=saved[side+'_kinetic_gram'],
            inclusion=saved[side+'_EM_inclusion'],inclusion_rate=saved[side+'_EM_inclusion_rate'])
        fresh48,diag48=evaluate(phase,48,space);cmp48=comparisons(fresh48,old)
        for k,v in fresh48.items():arrays[side+'_q48_'+k]=v
        for k in('value','rate','operator','kinetic'):arrays[side+'_q96_minus_q48_'+k]=old[k]-fresh48[k]
        record=dict(side=side,diagnostics=[diag48],q48_to_saved_q96=cmp48,
            saved96_record=rec,refinement192_required=not cmp48['operator']['absolute_guard_2e10'])
        print(side,'48->96',cmp48['operator']['absolute']['error'],cmp48['operator']['entrywise_scaled']['error'],flush=True)
        if record['refinement192_required']:
            fresh192,diag192=evaluate(phase,192,space);cmp192=comparisons(old,fresh192)
            record.update(q96_to_q192=cmp192);record['diagnostics'].append(diag192)
            for k,v in fresh192.items():arrays[side+'_q192_'+k]=v
            for k in('value','rate','operator','kinetic'):arrays[side+'_q192_minus_q96_'+k]=fresh192[k]-old[k]
            print(side,'96->192',cmp192['operator']['absolute']['error'],cmp192['operator']['entrywise_scaled']['error'],flush=True)
        records.append(record)
        _compressed_npz(out/'application.npz',arrays)
        write_json(out/'partial_result.json',dict(records=records))
    pins=dict(official['input_and_source_sha256'])
    pins[OFFICIAL+'/result.json']=EXPECTED_RESULT;pins[OFFICIAL+'/application.npz']=EXPECTED_ARCHIVE
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(REPO)and(name.startswith('bhsm.')or name.startswith('evaluate_em_')):
            relative=Path(p).relative_to(REPO).as_posix();pins[relative]=digest(p)
    result=dict(classification='ISOLATED_SAME_REAL_PRIMAL_ORIGINAL_MAXWELL_OPERATOR_RADIAL_COMPARISON',
        source_sha256=sha256(source_bytes).hexdigest(),official_result_sha256=EXPECTED_RESULT,
        official_numerical_sha256=EXPECTED_ARCHIVE,input_and_source_sha256=dict(sorted(pins.items())),records=records,
        angular_rule='same24-cell, complete real scalar n0,2; exact degree<=4 at homogeneous primal first derivative',
        row_order='value/rate,radial4,field5,internal4,harmonic10',
        direction_order='amplitude/rate,radial4,EMmode4',all1600_by32_entries_compared=True,
        coordinate_basis='same frozen two interior/source-complement/wall profiles, no node-dependent renormalization',
        matching_guard=2e-10,comparison_precision='binary64, same canonical local80 original weak probes and analytic complexstep1e-20',
        longdouble_mantissa_bits=int(np.finfo(np.longdouble).nmant),
        arithmetic_or_upstream_error_enclosed=False,physical_radial_convergence_admitted=False,
        full_outgoing_derivative_admitted=False,source_or_interface_or_coupled_equations_completed=False,
        coupled_corrections=0,physical_muon_magnetic_moment=None,
        numerical_sha256=digest(out/'application.npz'))
    write_json(out/'result.json',result)
    print('complete',result['numerical_sha256'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    main(p.parse_args().output)

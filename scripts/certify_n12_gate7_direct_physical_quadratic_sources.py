"""Assemble signed local LL/LT/TT sources from three paired physical Hessians."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_direct_physical_hessians as hessian
import certify_n12_gate7_direct_physical_local_defects as local
from bhsm.interface import direct_physical_quadratic_source as quadratic
from bhsm.interface import direct_physical_hs_second_variation as second

WORK=ROOT/'artifacts/flagship_integration/.direct_physical_quadratic_source_work'
THEORY=ROOT/'theory/n12_gate7_direct_physical_quadratic_sources.md'
ALGORITHM='DIRECT_PHYSICAL_HS_FIXED_FRAME_SIGNED_QUADRATIC_SOURCES_ARB512_V1'


def verify_hessian(stage,index,expected):
    directory=hessian.point_directory(stage,index)
    manifest_path=directory/'manifest.json';receipt_path=directory/'reproduction.json'
    manifest=json.loads(manifest_path.read_text());receipt=json.loads(receipt_path.read_text())
    dependencies=hessian.df.point_inputs(stage,index,expected['value_point_binding'])[-1]
    current=hessian.complete_manifest(stage,index,expected,dependencies)
    if (manifest!=current or manifest_path.read_bytes()!=hessian.encoded(current)
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('fresh_spawned_worker_processes') is not True
            or receipt.get('rows')!=list(range(99))
            or receipt.get('manifest_SHA256')!=hessian.df.values.sha(manifest_path)):
        raise RuntimeError('complete independently reproduced physical Hessian required')
    files=dict(manifest['files']);hessian.merge(files,expected['files']);hessian.merge(files,dependencies)
    for path in (manifest_path,receipt_path):files[hessian.df.file_key(path)]=hessian.df.values.sha(path)
    ctx.prec=512
    rows=[hessian.load_row(stage,index,row,expected,dependencies)[0] for row in range(99)]
    return quadratic.UpperHessian(rows),files,dependencies


def load_inputs(index,full_derivatives=False):
    # Capture the Hessian's original value-point binding before switching the
    # DF workspace. The full DF wrapper adds its own algorithm/source binding.
    expected=hessian.binding()
    tensors=[];raw=dict(expected['files']);point_dependencies=[]
    for stage,i in (('endpoint',index),('midpoint',index),('endpoint',index+1)):
        tensor,files,dependencies=verify_hessian(stage,i,expected)
        tensors.append(tensor);hessian.merge(raw,files);point_dependencies.append(dependencies)
    if full_derivatives:
        import derive_n12_gate7_full_direct_physical_jacobians as backend
        backend.install_backend()
    source=local.load_inputs([index])
    if expected['value_point_binding']['value_binding']!=source['binding']['value_binding']:
        raise RuntimeError('Hessian and derivative value campaigns differ')
    derivatives=[]
    for (stage,i),wanted in zip((('endpoint',index),('midpoint',index),('endpoint',index+1)),point_dependencies):
        dependencies=local.df.point_inputs(stage,i,source['binding'])[-1]
        if dependencies!=wanted:raise RuntimeError('Hessian and derivative physical points differ')
        ctx.prec=512
        derivatives.append(local.df.load_cached(stage,i,source['binding'],dependencies)[0])
    axes=local.residual.center.component._load_axes()
    if axes.shape!=(371,74) or local.residual.foundation.maps._array_hash(axes)!=source['axes_SHA256']:
        raise RuntimeError('complete matching frozen axes required')
    for path in (Path(__file__),THEORY,Path(hessian.__file__),Path(quadratic.__file__),Path(second.__file__)):
        hessian.merge(raw,{local.df.file_key(path):local.df.values.sha(path)})
    local.residual.merge_verified_raw_sources(source['inputs'],source['raw_inputs'],raw)
    return source,tensors,derivatives,axes


def direction_families(index,source,axes,family,pair):
    if family not in ('LL','LT','TT') or pair not in ('00','01','10','11'):
        raise ValueError('LL/LT/TT and explicit endpoint pair required')
    cert=local.residual.center.cert
    frames=[quadratic._matrix(cert._frame(source['tangents'][index+i],cert.TRIAL_DESCRIPTOR_SCALE)) for i in (0,1)]
    families=[]
    for kind,endpoint in zip(family,map(int,pair)):
        basis=quadratic._matrix(axes[index+endpoint].reshape(74,1)) if kind=='L' else arb_mat(np.eye(74,dtype=int).tolist())
        direction=frames[endpoint]*basis
        if index+endpoint==0:direction=arb_mat(99,direction.ncols())
        zero=arb_mat(99,direction.ncols())
        families.extend((direction,zero) if endpoint==0 else (zero,direction))
    return families


def build_block(index,family,pair,source,tensors,derivatives,axes):
    ctx.prec=512;cert=local.residual.center.cert
    test=cert._frame(source['tangents'][index+1],cert.TEST_DESCRIPTOR_SCALE).T
    values=quadratic.physical_quadratic_source(tensors,derivatives,float(source['steps'][index]),
        *direction_families(index,source,axes,family,pair),test,source['right'][index])
    array=np.array(values.entries(),dtype=object).reshape(values.nrows(),values.ncols())
    mid,rad=local.df.values.hs.rational_balls(array)
    record=metadata(index,family,pair,source)
    if list(array.shape)!=record['shape']:raise RuntimeError('complete local source shape required')
    return dict(Q_mid_q=mid,Q_rad_q=rad),record


def metadata(index,family,pair,source):
    shape=[74,dict(LL=1,LT=74,TT=5476)[family]]
    return dict(algorithm=ALGORITHM,scope='SELECTED_PHYSICAL_HS_POINT_FIXED_FRAME_LOCAL_QUADRATIC_SOURCE',
        interval=index,family=family,endpoint_pair=pair,precision_bits=512,
        shape=shape,column_order='FIRST_DIRECTION_MAJOR_SECOND_DIRECTION_MINOR',
        transverse_input_domain='FULL_COORDINATE_SPACE_SUPERSET',initial_endpoint_fixed=index==0,
        inputs=source['inputs'],raw_input_SHA256=source['raw_inputs'],
        input_hash_convention='SHA256_CRLF_TO_LF_FOR_JSON_MD_PY',raw_input_hash_convention='SHA256_EXACT_FILE_BYTES',
        axes_SHA256=source['axes_SHA256'],causal_maps_SHA256=source['causal_maps_SHA256'],
        actual_physical_HS_midpoint_used=True,midpoint_second_incidence_included=True,
        taylor_half_included=True,mixed_two_radius_factor=2,
        state_dependent_frame_derivatives_enclosed=False,physical_quotient_identified=False,
        complete_causal_curvature_enclosed=False,neighborhood_remainder_enclosed=False,
        physical_contraction_proved=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def write_block(directory,index,family,pair,source,tensors,derivatives,axes,recompute=False):
    path=directory/f'{family}_{pair}.npz';previous=None
    if path.exists() or path.with_suffix('.json').exists():
        previous=json.loads(path.with_suffix('.json').read_text())
        expected=metadata(index,family,pair,source);expected['data_SHA256']=local.df.values.sha(path)
        if previous!=expected or path.with_suffix('.json').read_bytes()!=hessian.encoded(expected):
            raise RuntimeError('existing quadratic source binding changed')
        with np.load(path,allow_pickle=False) as arrays:
            if set(arrays.files)!={'Q_mid_q','Q_rad_q'} or any(list(arrays[k].shape)!=expected['shape'] for k in arrays.files):
                raise RuntimeError('complete rational local source required')
            local.df.values.hs.restore_balls(arrays['Q_mid_q'],arrays['Q_rad_q'])
        if not recompute:return
    elif recompute:raise RuntimeError('independent repeat requires previous source evidence')
    arrays,record=build_block(index,family,pair,source,tensors,derivatives,axes)
    candidate=directory/f'{family}_{pair}.candidate_{time.time_ns()}.npz'
    np.savez_compressed(candidate,**arrays);record['data_SHA256']=local.df.values.sha(candidate)
    if previous is not None:
        if record!=previous:
            hessian.write_json(candidate.with_suffix('.json'),record)
            raise ArithmeticError('independent quadratic source differs; candidates preserved')
        candidate.unlink()
    else:
        candidate.replace(path);hessian.write_json(path.with_suffix('.json'),record)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--interval',type=int,required=True)
    parser.add_argument('--full-derivatives',action='store_true');parser.add_argument('--recompute',action='store_true')
    args=parser.parse_args()
    if not 0<=args.interval<370:raise ValueError('interval in 0..369 required')
    directory=WORK/f'interval_{args.interval:03d}';directory.mkdir(parents=True,exist_ok=True)
    manifest_path=directory/'manifest.json';receipt_path=directory/'reproduction.json'
    previous=json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    if args.recompute and previous is None:raise RuntimeError('complete prior source manifest required')
    if previous is not None:
        required={local.df.file_key(directory/f'{family}_{pair}.{ext}')
            for family in ('LL','LT','TT') for pair in ('00','01','10','11') for ext in ('json','npz')}
        if (previous.get('algorithm')!=ALGORITHM or previous.get('interval')!=args.interval
                or previous.get('complete_local_source_blocks') is not True
                or set(previous.get('files',{}))!=required):
            raise RuntimeError('complete prior source inventory required')
        local.df.values.verify_binding(dict(files=previous['files']))
    if args.recompute and receipt_path.exists():
        receipt_path.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    source,tensors,derivatives,axes=load_inputs(args.interval,args.full_derivatives)
    for family in ('LL','LT','TT'):
        for pair in ('00','01','10','11'):
            write_block(directory,args.interval,family,pair,source,tensors,derivatives,axes,args.recompute)
            print(json.dumps(dict(interval=args.interval,family=family,pair=pair,reproduced=args.recompute)),flush=True)
    local.residual.foundation.coordinate._verified_inputs(dict(inputs=source['inputs']))
    local.df.values.verify_binding(dict(files=source['raw_inputs']))
    files={local.df.file_key(directory/f'{family}_{pair}.{ext}'):local.df.values.sha(directory/f'{family}_{pair}.{ext}')
        for family in ('LL','LT','TT') for pair in ('00','01','10','11') for ext in ('json','npz')}
    manifest=dict(algorithm=ALGORITHM,interval=args.interval,files=files,complete_local_source_blocks=True,
        complete_causal_curvature_enclosed=False,neighborhood_remainder_enclosed=False,FULL_BHSM_COMPLETE=False)
    if args.recompute:
        if previous!=manifest or manifest_path.read_bytes()!=hessian.encoded(manifest):
            hessian.write_json(directory/f'manifest.mismatch_{time.time_ns()}.json',manifest)
            raise ArithmeticError('independent local source manifest differs')
        hessian.write_json(receipt_path,dict(byte_identical=True,independent_recomputation=True,
            manifest_SHA256=local.df.values.sha(manifest_path),FULL_BHSM_COMPLETE=False))
    else:hessian.write_json(manifest_path,manifest)


if __name__=='__main__':main()

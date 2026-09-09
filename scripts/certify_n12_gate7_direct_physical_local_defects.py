"""Assemble physical-point C/DL/DR blocks for the unchanged frozen inverse."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
from flint import ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_direct_physical_jacobians as df
import certify_n12_gate7_direct_physical_residual as residual
from bhsm.interface import direct_physical_hs_defect as defect
WORK=ROOT/'artifacts/flagship_integration/.direct_physical_local_defect_work'
THEORY=ROOT/'theory/n12_gate7_direct_physical_local_defects.md'
ALGORITHM='DIRECT_PHYSICAL_HS_FROZEN_LOCAL_NEWTON_DEFECT_ARB512_V1'


def verify_pair(manifest,receipt,path,indices):
    endpoints,midpoints=manifest.get('endpoints',[]),manifest.get('midpoints',[])
    if (not endpoints or not midpoints or len(set(endpoints))!=len(endpoints) or len(set(midpoints))!=len(midpoints)
            or any(type(i) is not int or not 0<=i<371 for i in endpoints)
            or any(type(i) is not int or not 0<=i<370 for i in midpoints)
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('points')!=len(endpoints)+len(midpoints)
            or receipt.get('manifest_SHA256')!=df.values.sha(path)):
        raise RuntimeError('independently reproduced derivative point inventory required')
    if any(i not in midpoints or i not in endpoints or i+1 not in endpoints for i in indices):
        raise RuntimeError('each selected interval needs both endpoint DF and physical midpoint DF')
    expected={df.file_key(df.WORK/f'{stage}_{i:03d}.{ext}')
              for stage,points in (('endpoint',endpoints),('midpoint',midpoints)) for i in points for ext in ('json','npz')}
    if set(manifest.get('files',{}))!=expected:
        raise RuntimeError('exact derivative file inventory required')
    df.values.verify_binding(dict(files=manifest['files']))


def load_inputs(indices):
    base,inputs,_,_=residual.load_foundation()
    manifest_path=df.WORK/'manifest.json';receipt_path=df.WORK/'reproduction.json'
    manifest=json.loads(manifest_path.read_text());receipt=json.loads(receipt_path.read_text())
    verify_pair(manifest,receipt,manifest_path,indices)
    expected=df.binding()
    if manifest.get('binding')!=expected:raise RuntimeError('physical DF source binding changed')
    if df.values.cert.ENDPOINT!=residual.center.ENDPOINT:
        raise RuntimeError('physical DF and frozen foundation endpoint sources differ')
    raw={}
    additional=dict(expected['files']);residual.merge(additional,manifest['files'])
    for path in (Path(__file__),THEORY,Path(defect.__file__),Path(defect.hs.__file__),Path(residual.__file__),
                 residual.foundation.RESULT,manifest_path,receipt_path):
        residual.merge(additional,{df.file_key(path):df.values.sha(path)})
    residual.merge_verified_raw_sources(inputs,raw,additional)
    with np.load(residual.center.JACOBIAN.with_suffix('.npz')) as source:
        tangents=source['endpoint_physical_tangent_action'].copy()
    with np.load(residual.center.PRECONDITIONER.with_suffix('.npz')) as source:
        left=source['left_Newton_blocks'].copy();right=source['reduced_right_Newton_blocks'].copy()
    if tangents.shape!=(371,98,73) or left.shape!=(370,99,99) or right.shape!=(370,74,74):
        raise RuntimeError('complete frozen frame and preconditioner operands required')
    steps=df.values.operands()[-1]
    return dict(binding=expected,inputs=inputs,raw_inputs=raw,tangents=tangents,left=left,right=right,steps=steps,
                causal_maps_SHA256=base['causal_maps_SHA256'],axes_SHA256=base['axes_SHA256'])


def build_point(index,source):
    matrices=[]
    for stage,i in (('endpoint',index),('midpoint',index),('endpoint',index+1)):
        dependencies=df.point_inputs(stage,i,source['binding'])[-1]
        matrix,_=df.load_cached(stage,i,source['binding'],dependencies)
        matrices.append(matrix)
    cert=residual.center.cert
    trial_left=cert._frame(source['tangents'][index],cert.TRIAL_DESCRIPTOR_SCALE)
    trial_right=cert._frame(source['tangents'][index+1],cert.TRIAL_DESCRIPTOR_SCALE)
    test=cert._frame(source['tangents'][index+1],cert.TEST_DESCRIPTOR_SCALE).T
    blocks=defect.local_defect_blocks(*matrices,float(source['steps'][index]),trial_left,trial_right,test,
        source['left'][index],source['right'][index],initial_endpoint_fixed=index==0)
    ctx.prec=512
    arrays={}
    for name,matrix in blocks.items():
        array=np.array(matrix.entries(),dtype=object).reshape(74,74)
        arrays[name+'_mid_q'],arrays[name+'_rad_q']=df.values.hs.rational_balls(array)
    record=dict(algorithm=ALGORITHM,scope='FIXED_FRAME_DIRECT_PHYSICAL_HS_LOCAL_NEWTON_DEFECT',interval=index,
        precision_bits=512,initial_endpoint_fixed=index==0,inputs=source['inputs'],
        input_hash_convention='SHA256_CRLF_TO_LF_FOR_JSON_MD_PY',raw_input_SHA256=source['raw_inputs'],
        raw_input_hash_convention='SHA256_EXACT_FILE_BYTES',
        causal_maps_SHA256=source['causal_maps_SHA256'],axes_SHA256=source['axes_SHA256'],
        actual_physical_HS_midpoint_DF_used=True,validation_passed=True,
        physical_branch_continuation_certified=False,physical_quotient_identified=False,
        state_dependent_frame_derivatives_enclosed=False,complete_causal_Z1_enclosed=False,
        physical_Z1_recertified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return arrays,record


def write_point(index,source,recompute=False):
    path=WORK/f'interval_{index:03d}.npz';previous=None
    if path.exists() or path.with_suffix('.json').exists():
        previous=json.loads(path.with_suffix('.json').read_text())
        if (previous.get('data_SHA256')!=df.values.sha(path) or previous.get('inputs')!=source['inputs']
                or previous.get('raw_input_SHA256')!=source['raw_inputs'] or previous.get('algorithm')!=ALGORITHM
                or previous.get('interval')!=index or previous.get('validation_passed') is not True):
            raise RuntimeError('local defect cache binding failed')
        if not recompute:return
    elif recompute:raise RuntimeError('independent local assembly requires prior point evidence')
    arrays,record=build_point(index,source)
    candidate=path.with_suffix('.partial.npz');np.savez_compressed(candidate,**arrays)
    record['data_SHA256']=df.values.sha(candidate)
    if previous is not None:
        if record!=previous:
            df.values.write_json(WORK/f'interval_{index:03d}.repeat_mismatch.json',record)
            raise ArithmeticError('independent local defect assembly differs; both candidates preserved')
        candidate.unlink();return
    candidate.replace(path);df.values.write_json(path.with_suffix('.json'),record)


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--midpoints');group.add_argument('--all-midpoints',action='store_true')
    parser.add_argument('--recompute',action='store_true');args=parser.parse_args()
    indices=list(range(370)) if args.all_midpoints else [int(i) for i in args.midpoints.split(',')]
    if not indices or len(set(indices))!=len(indices) or any(not 0<=i<370 for i in indices):
        raise ValueError('distinct midpoint indices in 0..369 required')
    source=load_inputs(indices);WORK.mkdir(parents=True,exist_ok=True)
    for index in indices:
        write_point(index,source,args.recompute)
        print(json.dumps(dict(interval=index,assembled=True,reproduced=args.recompute)),flush=True)
    # Verify the complete campaign once on entry and once on exit. Rehashing
    # every unrelated DF file at each interval would multiply large-cache I/O.
    residual.foundation.coordinate._verified_inputs(dict(inputs=source['inputs']))
    df.values.verify_binding(dict(files=source['raw_inputs']))
    files={df.file_key(WORK/f'interval_{i:03d}.{ext}'):df.values.sha(WORK/f'interval_{i:03d}.{ext}')
           for i in indices for ext in ('json','npz')}
    record=dict(algorithm=ALGORITHM,intervals=indices,files=files,all_intervals_assembled=len(indices)==370,
                complete_causal_Z1_enclosed=False,physical_Z1_recertified=False,FULL_BHSM_COMPLETE=False)
    df.values.write_json(WORK/'manifest.json',record)
    if args.recompute:
        df.values.write_json(WORK/'reproduction.json',dict(byte_identical=True,independent_recomputation=True,
            manifest_SHA256=df.values.sha(WORK/'manifest.json'),intervals=indices,FULL_BHSM_COMPLETE=False))


if __name__=='__main__':main()

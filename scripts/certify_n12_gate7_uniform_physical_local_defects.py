"""Integrate paired uniform endpoint and actual-midpoint physical derivatives."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_coupled_endpoint_uniform_derivatives as endpoint
import certify_n12_gate7_coupled_midpoint_uniform_derivatives as midpoint
from bhsm.interface import direct_physical_hs_defect as defect

p=endpoint.p
WORK=ROOT/'artifacts/flagship_integration/.uniform_physical_local_defect_work'
THEORY=ROOT/'theory/n12_gate7_uniform_physical_local_defects.md'
ALGORITHM='UNIFORM_PHYSICAL_HS_FROZEN_LOCAL_NEWTON_DEFECT_ARB512_V1'


def read_derivative(producer,index,stage):
    if stage not in ('endpoint','midpoint'):raise ValueError('explicit physical derivative stage required')
    source=producer.load_inputs(index)
    key='endpoint' if stage=='endpoint' else 'interval'
    directory=producer.WORK/f'{key}_{index:03d}'
    path=directory/'record.json';data=directory/'derivative.npz';receipt_path=directory/'reproduction.json'
    record=json.loads(path.read_bytes());receipt=json.loads(receipt_path.read_bytes())
    report=record.get('report',{})
    if (record.get('binding')!=source['binding'] or record.get('algorithm')!=producer.ALGORITHM
            or record.get(key)!=index or report.get('validation_passed') is not True
            or report.get('uniform_physical_first_derivatives_enclosed') is not True
            or report.get('weighted_augmented_basis_columns')!=99
            or report.get('full_descriptor_direction_included') is not True
            or report.get('actual_HS_midpoint_domain_enclosed') is not (stage=='midpoint')
            or path.read_bytes()!=p.geometry.encoded(record) or record.get('data_SHA256')!=p.values.sha(data)
            or receipt.get('record_SHA256')!=p.values.sha(path)
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True):
        raise RuntimeError('paired complete uniform derivative on the matching physical domain required')
    with np.load(data,allow_pickle=False) as a:
        matrix=p.hs.restore_balls(a['derivative_mid_q'],a['derivative_rad_q'])
    if matrix.shape!=(99,99) or not all(v.is_finite() for v in matrix.flat):
        raise ArithmeticError('complete finite 99 by 99 physical derivative required')
    for file in (path,data,receipt_path):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    return source,matrix


def load_inputs(index):
    if type(index) is not int or not 0<=index<370:raise ValueError('HS interval in 0..369 required')
    ctx.prec=512
    left,A=read_derivative(endpoint,index,'endpoint')
    middle,M=read_derivative(midpoint,index,'midpoint')
    right,B=read_derivative(endpoint,index+1,'endpoint')
    binding=dict(left['binding']);binding['files']=dict(binding['files'])
    binding['normalized_inputs']=dict(binding['normalized_inputs'])
    for source in (middle,right):
        if source['binding']['normalized_inputs']!=left['binding']['normalized_inputs']:
            raise RuntimeError('physical derivative domain foundations disagree')
        p.geometry.residual.merge(binding['files'],source['binding']['files'])
    residual=p.geometry.residual
    foundation,inputs,_,_=residual.load_foundation()
    p.geometry.residual.merge(binding['normalized_inputs'],inputs)
    tangent_path=residual.center.JACOBIAN.with_suffix('.npz')
    preconditioner_path=residual.center.PRECONDITIONER.with_suffix('.npz')
    with np.load(tangent_path,allow_pickle=False) as a:tangents=a['endpoint_physical_tangent_action']
    with np.load(preconditioner_path,allow_pickle=False) as a:
        frozen_left=a['left_Newton_blocks'];frozen_right=a['reduced_right_Newton_blocks']
    if (tangents.shape!=(371,98,73) or frozen_left.shape!=(370,99,99)
            or frozen_right.shape!=(370,74,74)
            or not all(np.isfinite(a).all() for a in (tangents,frozen_left,frozen_right))):
        raise ArithmeticError('complete finite frozen physical frame and inverse operands required')
    for file in (Path(__file__),THEORY,Path(defect.__file__),Path(defect.hs.__file__),
                 tangent_path,preconditioner_path,residual.foundation.RESULT):
        p.geometry.residual.merge(binding['files'],{p.df.file_key(file):p.values.sha(file)})
    binding['algorithm']=ALGORITHM
    cert=residual.center.cert
    source=dict(index=index,binding=binding,left_df=A,midpoint_df=M,right_df=B,
        step=float(p.values.operands()[-1][index]),
        trial_left=cert._frame(tangents[index],cert.TRIAL_DESCRIPTOR_SCALE),
        trial_right=cert._frame(tangents[index+1],cert.TRIAL_DESCRIPTOR_SCALE),
        test=cert._frame(tangents[index+1],cert.TEST_DESCRIPTOR_SCALE).T,
        frozen_left=frozen_left[index],frozen_right=frozen_right[index],
        causal_maps_SHA256=foundation['causal_maps_SHA256'],axes_SHA256=foundation['axes_SHA256'])
    p.verify_sources(binding)
    return source


def evaluate(source):
    ctx.prec=512
    blocks=defect.local_defect_blocks(source['left_df'],source['midpoint_df'],source['right_df'],source['step'],
        source['trial_left'],source['trial_right'],source['test'],source['frozen_left'],source['frozen_right'],
        initial_endpoint_fixed=source['index']==0)
    arrays={key:np.array(matrix.entries(),dtype=object).reshape(74,74) for key,matrix in blocks.items()}
    if set(arrays)!={'C','DL','DR'} or not all(v.is_finite() for a in arrays.values() for v in a.flat):
        raise ArithmeticError('complete finite uniform local blocks required')
    p.verify_sources(source['binding'])
    report=dict(validation_passed=True,scope='UNIFORM_FIXED_FRAME_PHYSICAL_HS_LOCAL_NEWTON_DEFECT',
        uniform_local_blocks_enclosed=True,paired_uniform_endpoint_derivatives_used=True,
        paired_uniform_actual_HS_midpoint_derivative_used=True,initial_endpoint_fixed=source['index']==0,
        state_dependent_frame_derivatives_enclosed=False,physical_quotient_identified=False,
        complete_causal_Z1_enclosed=False,physical_Z1_recertified=False,higher_remainder_enclosed=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return arrays,report


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--interval',type=int,default=13)
    parser.add_argument('--preflight',action='store_true');parser.add_argument('--recompute',action='store_true')
    args=parser.parse_args();source=load_inputs(args.interval)
    if args.preflight:print(json.dumps(dict(inputs_verified=True,numerical_evaluation=False)));return
    directory=WORK/f'interval_{args.interval:03d}';directory.mkdir(parents=True,exist_ok=True)
    data=directory/'blocks.npz';path=directory/'record.json';receipt=directory/'reproduction.json'
    previous=json.loads(path.read_bytes()) if path.exists() else None
    if args.recompute!=(previous is not None):raise RuntimeError('first/recompute state differs')
    if previous is not None and (previous['data_SHA256']!=p.values.sha(data) or path.read_bytes()!=p.geometry.encoded(previous)):
        raise RuntimeError('prior uniform local evidence changed')
    if receipt.exists():receipt.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    candidate=directory/f'blocks.candidate_{time.time_ns()}.npz'
    attempted=dict(binding=source['binding'],interval=args.interval,FULL_BHSM_COMPLETE=False)
    candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted))
    try:arrays,report=evaluate(source)
    except Exception as error:
        attempted['error']=repr(error);candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted));raise
    encoded={}
    for name,array in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(array)
    np.savez_compressed(candidate,**encoded)
    record=dict(algorithm=ALGORITHM,binding=source['binding'],interval=args.interval,
        causal_maps_SHA256=source['causal_maps_SHA256'],axes_SHA256=source['axes_SHA256'],
        data_SHA256=p.values.sha(candidate),report=report,FULL_BHSM_COMPLETE=False)
    candidate_record=candidate.with_suffix('.json');candidate_record.write_bytes(p.geometry.encoded(record))
    if previous is not None:
        if path.read_bytes()!=candidate_record.read_bytes():raise ArithmeticError('independent uniform local blocks differ; candidates preserved')
        candidate.unlink();candidate_record.unlink()
        receipt.write_bytes(p.geometry.encoded(dict(independent_recomputation=True,byte_identical=True,
            record_SHA256=p.values.sha(path),complete_causal_Z1_enclosed=False,FULL_BHSM_COMPLETE=False)))
    else:candidate.replace(data);candidate_record.replace(path)
    print(json.dumps(dict(interval=args.interval,reproduced=args.recompute,validation_passed=True,FULL_BHSM_COMPLETE=False)),flush=True)


if __name__=='__main__':main()

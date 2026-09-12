"""Enclose an actual HS midpoint image using paired uniform endpoint fields."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import arb,ctx,fmpq

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_affine_physical_value_pilot as values
from bhsm.interface import affine_hs_midpoint_domain as geometry

p=values.p
WORK=ROOT/'artifacts/flagship_integration/.affine_hs_midpoint_domain_work'
THEORY=ROOT/'theory/n12_gate7_affine_hs_midpoint_domain.md'
ALGORITHM='ACTUAL_HS_MIDPOINT_AFFINE_PRODUCT_DOMAIN_ARB512_V1'


def load_endpoint(index):
    source=values.load_inputs(index)
    directory=values.WORK/f'endpoint_{index:03d}'
    path=directory/'record.json';data=directory/'value.npz';receipt_path=directory/'reproduction.json'
    record=json.loads(path.read_bytes());receipt=json.loads(receipt_path.read_bytes())
    report=record.get('report',{})
    if (record.get('algorithm')!=values.ALGORITHM or record.get('endpoint')!=index
            or record.get('binding')!=source['binding'] or path.read_bytes()!=p.geometry.encoded(record)
            or record.get('data_SHA256')!=p.values.sha(data)
            or receipt.get('record_SHA256')!=p.values.sha(path)
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or report.get('validation_passed') is not True or report.get('uniform_physical_value_enclosed') is not True
            or report.get('scope')!='SELECTED_FROZEN_AFFINE_ENDPOINT_TUBE'
            or report.get('positive_physical_G_norm') is not True
            or not arb(fmpq(report['physical_G_norm_lower_rational']))>0):
        raise RuntimeError('paired uniform physical endpoint field on the bound affine tube required')
    for name in ('longitudinal','transverse'):
        if record.get(f'radius_{name}_rational')!=str(source['tube'][f'radius_{name}'].fmpq()):
            raise RuntimeError('uniform field tube radius changed')
    with np.load(data,allow_pickle=False) as a:
        rate=p.hs.restore_balls(a['rate_candidate_mid_q'],a['rate_candidate_rad_q'])
    if rate.shape!=(99,) or not all(v.is_finite() for v in rate):
        raise ArithmeticError('complete finite uniform field required')
    for file in (path,data,receipt_path):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    return source,rate


def load_inputs(index):
    if type(index) is not int or not 0<=index<370:raise ValueError('HS interval in 0..369 required')
    ctx.prec=512
    left,fL=load_endpoint(index);right,fR=load_endpoint(index+1)
    binding=dict(left['binding'])
    binding['files']=dict(left['binding']['files'])
    p.geometry.residual.merge(binding['files'],right['binding']['files'])
    if left['binding']['normalized_inputs']!=right['binding']['normalized_inputs']:
        raise RuntimeError('endpoint foundations disagree')
    for file in (Path(__file__),THEORY,Path(geometry.__file__)):
        p.geometry.residual.merge(binding['files'],{p.df.file_key(file):p.values.sha(file)})
    binding['algorithm']=ALGORITHM
    p.verify_sources(binding)
    return dict(index=index,left=left,right=right,left_rate=fL,right_rate=fR,binding=binding)


def evaluate(source):
    ctx.prec=512
    index=source['index'];residual=p.geometry.residual
    _,_,_,axes=residual.load_foundation()
    x,w,s,_,steps=p.values.operands()
    with np.load(residual.center.JACOBIAN.with_suffix('.npz'),allow_pickle=False) as a:
        frame=[residual.center.cert._frame(a['endpoint_physical_tangent_action'][i],residual.center.cert.TRIAL_DESCRIPTOR_SCALE)
               for i in (index,index+1)]
    center=[p.hs.weighted_endpoint(x[i],s[i],w) for i in (index,index+1)]
    result=geometry.midpoint_domain(*center,*frame,axes[index],axes[index+1],
        source['left_rate'],source['right_rate'],float(steps[index]),w,
        [source[key]['tube']['radius_longitudinal'] for key in ('left','right')],
        [source[key]['tube']['radius_transverse'] for key in ('left','right')])
    p.verify_sources(source['binding'])
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--interval',type=int,default=13)
    parser.add_argument('--preflight',action='store_true');parser.add_argument('--recompute',action='store_true')
    args=parser.parse_args();source=load_inputs(args.interval)
    if args.preflight:print(json.dumps(dict(inputs_verified=True,numerical_evaluation=False)));return
    directory=WORK/f'interval_{args.interval:03d}';directory.mkdir(parents=True,exist_ok=True)
    data=directory/'domain.npz';path=directory/'record.json';receipt=directory/'reproduction.json'
    previous=json.loads(path.read_bytes()) if path.exists() else None
    if args.recompute!=(previous is not None):raise RuntimeError('first/recompute state differs')
    if previous is not None and (previous['data_SHA256']!=p.values.sha(data) or path.read_bytes()!=p.geometry.encoded(previous)):
        raise RuntimeError('prior midpoint domain changed')
    if receipt.exists():receipt.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    candidate=directory/f'domain.candidate_{time.time_ns()}.npz'
    attempted=dict(binding=source['binding'],interval=args.interval,FULL_BHSM_COMPLETE=False)
    candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted))
    try:result=evaluate(source)
    except Exception as error:
        attempted['error']=repr(error);candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted));raise
    arrays={key:val for key,val in result.items() if isinstance(val,np.ndarray)}
    shapes=dict(raw_center=(99,),raw_directions=(99,249),raw_segment_hull=(99,),raw_rate_remainder_radii=(99,))
    if set(arrays)!=set(shapes) or any(a.shape!=shapes[key] or not all(v.is_finite() for v in a.flat)
                                      for key,a in arrays.items()):
        raise ArithmeticError('complete finite physical midpoint domain required')
    encoded={}
    for name,array in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(array)
    np.savez_compressed(candidate,**encoded)
    groups=[dict(start=g['start'],stop=g['stop'],norm=g['norm'],radius_rational=str(g['radius'].fmpq())) for g in result['groups']]
    record=dict(algorithm=ALGORITHM,binding=source['binding'],interval=args.interval,groups=groups,
        data_SHA256=p.values.sha(candidate),uniform_endpoint_fields_independently_paired=True,
        actual_HS_midpoint_image_enclosed=True,outer_affine_product_domain=True,
        full_uniform_midpoint_eigenpair_enclosed=False,uniform_midpoint_field_enclosed=False,
        axis_normalization_assumed=False,physical_quotient_identified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    candidate_record=candidate.with_suffix('.json');candidate_record.write_bytes(p.geometry.encoded(record))
    if previous is not None:
        if path.read_bytes()!=candidate_record.read_bytes():raise ArithmeticError('independent midpoint domain differs; candidates preserved')
        candidate.unlink();candidate_record.unlink()
        receipt.write_bytes(p.geometry.encoded(dict(independent_recomputation=True,byte_identical=True,
            record_SHA256=p.values.sha(path),uniform_midpoint_field_enclosed=False,FULL_BHSM_COMPLETE=False)))
    else:candidate.replace(data);candidate_record.replace(path)
    print(json.dumps(dict(interval=args.interval,reproduced=args.recompute,actual_midpoint_domain_enclosed=True,FULL_BHSM_COMPLETE=False)),flush=True)


if __name__=='__main__':main()

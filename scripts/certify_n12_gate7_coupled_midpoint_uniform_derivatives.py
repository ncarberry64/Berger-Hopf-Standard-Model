"""Enclose all 99 physical first-variation directions on a paired midpoint domain."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_coupled_midpoint_physical_value as values
from bhsm.interface import coupled_bordered_linear_solve as inverse

p=values.p
WORK=ROOT/'artifacts/flagship_integration/.coupled_midpoint_uniform_df_work'
THEORY=ROOT/'theory/n12_gate7_coupled_midpoint_uniform_derivatives.md'
ALGORITHM='COUPLED_ACTUAL_HS_MIDPOINT_UNIFORM_PHYSICAL_DF_ARB512_V1'
BATCH_SIZE=9


def load_inputs(index):
    ctx.prec=512
    source=values.load_inputs(index)
    directory=values.WORK/f'interval_{index:03d}'
    path=directory/'record.json';data=directory/'value.npz';receipt_path=directory/'reproduction.json'
    record=json.loads(path.read_bytes());receipt=json.loads(receipt_path.read_bytes())
    if (record.get('binding')!=source['binding'] or record.get('algorithm')!=values.ALGORITHM
            or record.get('interval')!=index or record.get('report',{}).get('validation_passed') is not True
            or record['report'].get('uniform_actual_HS_midpoint_field_enclosed') is not True
            or record['report'].get('positive_physical_G_norm') is not True
            or path.read_bytes()!=p.geometry.encoded(record) or record.get('data_SHA256')!=p.values.sha(data)
            or receipt.get('record_SHA256')!=p.values.sha(path)
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True):
        raise RuntimeError('paired actual midpoint physical field required')
    with np.load(data,allow_pickle=False) as a:
        def read(name):return p.hs.restore_balls(a[name+'_mid_q'],a[name+'_rad_q'])
        source['response']=read('response_box')
        source['old_rate']=read('original_rate_candidate')
        source['coupled_rate']=read('rate_candidate')
    for name,shape in (('response',(62,)),('old_rate',(99,)),('coupled_rate',(99,))):
        if source[name].shape!=shape or not all(v.is_finite() for v in source[name]):
            raise ArithmeticError('complete finite paired response and physical value required')
    for file in (path,data,receipt_path,Path(__file__),THEORY,Path(inverse.__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    source['binding']['algorithm']=ALGORITHM
    p.verify_sources(source['binding'])
    return source


def evaluate_batch(source,start,stop):
    if not 0<=start<stop<=99:raise ValueError('nonempty physical basis slice required')
    cert=p.values.cert
    paired=source['paired'];full=paired['full'];eigenbox=paired['eigenbox']
    directions=np.full((99,stop-start),arb(0),dtype=object)
    for k in range(start,stop):directions[k,k-start]=arb(1)
    _,weights,_,reference,_=p.values.operands()
    original_solve=cert._verified_solve;original_eigenline=cert._eigenline
    calls=[];residuals=[];proofs=[]

    def solve(matrix,rhs):
        if matrix.nrows()!=62 or matrix.ncols()!=62 or rhs.nrows()!=62:
            raise ArithmeticError('retained coupled bordered system required')
        if not calls:
            if rhs.ncols()!=1:raise ArithmeticError('physical response must be first')
            calls.append('PAIRED_PHYSICAL_RESPONSE')
            return arb_mat(62,1,list(source['response']))
        if len(calls)>=3 or rhs.ncols()!=stop-start:
            raise ArithmeticError('exactly one eigenline and one response variation required')
        enclosed,residual,proof=inverse.enclose_columns(paired['rm'],
            np.array(rhs.entries(),dtype=object).reshape(62,stop-start),paired['radii'],paired['variation'])
        residuals.append(residual);proofs.append(proof)
        calls.append('EIGENLINE_VARIATION' if len(calls)==1 else 'RESPONSE_VARIATION')
        return arb_mat(62,stop-start,list(enclosed.flat))

    try:
        cert._verified_solve=solve
        cert._eigenline=lambda *args:(eigenbox[:61],eigenbox[-1],arb(0),arb(0))
        with p.df.sparse.use_optimized_mixed(cert),values.eq.engine.affine.factored.use_ball_factored_integrand(cert,full):
            result=cert._rate_enclosure(full,source['raw_domain'][98],weights,reference,directions)
        if len(calls)!=3 or result.derivative.shape!=(99,stop-start):
            raise ArithmeticError('complete physical first variation required')
        if not all(isinstance(v,arb) and v.is_finite() for v in result.derivative.flat):
            raise ArithmeticError('nonfinite uniform physical derivative')
        if not all(a.overlaps(b) for a,b in zip(result.value,source['old_rate'],strict=True)):
            raise ArithmeticError('paired physical value and derivative evaluation disagree')
        return result.derivative,np.stack(residuals),proofs
    finally:
        cert._verified_solve=original_solve;cert._eigenline=original_eigenline


def evaluate(source):
    ctx.prec=512
    derivative=np.empty((99,99),dtype=object)
    residual=np.empty((2,62,99),dtype=object);proofs=[]
    for start in range(0,99,BATCH_SIZE):
        stop=min(start+BATCH_SIZE,99)
        derivative[:,start:stop],residual[:,:,start:stop],proof=evaluate_batch(source,start,stop)
        proofs.append(dict(start=start,stop=stop,solve_bounds=proof))
        print(json.dumps(dict(phase='UNIFORM_PHYSICAL_DF',completed_columns=stop,total_columns=99)),flush=True)
    p.verify_sources(source['binding'])
    report=dict(validation_passed=True,scope='ACTUAL_HS_MIDPOINT_OUTER_DOMAIN',
        uniform_physical_first_derivatives_enclosed=True,actual_HS_midpoint_domain_enclosed=True,
        weighted_augmented_basis_columns=99,full_descriptor_direction_included=True,
        original_complete_first_variation_reused=True,coupled_inverse_bounds=proofs,
        uniform_physical_hessians_enclosed=False,higher_remainder_enclosed=False,
        physical_quotient_identified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return dict(derivative=derivative,preconditioned_variation_rhs=residual,raw_domain=source['raw_domain']),report


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--interval',type=int,default=13)
    parser.add_argument('--preflight',action='store_true');parser.add_argument('--recompute',action='store_true')
    args=parser.parse_args();source=load_inputs(args.interval)
    if args.preflight:print(json.dumps(dict(inputs_verified=True,numerical_evaluation=False)));return
    directory=WORK/f'interval_{args.interval:03d}';directory.mkdir(parents=True,exist_ok=True)
    data=directory/'derivative.npz';path=directory/'record.json';receipt=directory/'reproduction.json'
    previous=json.loads(path.read_bytes()) if path.exists() else None
    if args.recompute!=(previous is not None):raise RuntimeError('first/recompute state differs')
    if previous is not None and (previous['data_SHA256']!=p.values.sha(data) or path.read_bytes()!=p.geometry.encoded(previous)):
        raise RuntimeError('prior uniform derivative evidence changed')
    if receipt.exists():receipt.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    candidate=directory/f'derivative.candidate_{time.time_ns()}.npz'
    attempted=dict(binding=source['binding'],interval=args.interval,FULL_BHSM_COMPLETE=False)
    candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted))
    try:arrays,report=evaluate(source)
    except Exception as error:
        attempted['error']=repr(error);candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted));raise
    encoded={}
    for name,array in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(array)
    np.savez_compressed(candidate,**encoded)
    record=dict(algorithm=ALGORITHM,binding=source['binding'],interval=args.interval,
        data_SHA256=p.values.sha(candidate),report=report,FULL_BHSM_COMPLETE=False)
    candidate_record=candidate.with_suffix('.json');candidate_record.write_bytes(p.geometry.encoded(record))
    if previous is not None:
        if path.read_bytes()!=candidate_record.read_bytes():raise ArithmeticError('independent uniform derivative differs; candidate preserved')
        candidate.unlink();candidate_record.unlink()
        receipt.write_bytes(p.geometry.encoded(dict(independent_recomputation=True,byte_identical=True,
            record_SHA256=p.values.sha(path),Gate7_closed=False,FULL_BHSM_COMPLETE=False)))
    else:candidate.replace(data);candidate_record.replace(path)
    print(json.dumps(dict(interval=args.interval,reproduced=args.recompute,validation_passed=True,FULL_BHSM_COMPLETE=False)),flush=True)


if __name__=='__main__':main()

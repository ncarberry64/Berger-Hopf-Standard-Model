"""Refine paired endpoint fields by canceling their verified common scale."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_affine_hs_midpoint_domain as midpoint
from bhsm.interface import coupled_physical_normalization as normalization

p=midpoint.p
WORK=ROOT/'artifacts/flagship_integration/.coupled_normalized_physical_value_work'
THEORY=ROOT/'theory/n12_gate7_coupled_physical_normalization.md'
ALGORITHM='COUPLED_UNIT_ORTHOGONAL_PHYSICAL_VALUE_ARB512_V1'


def load_inputs(index):
    ctx.prec=512
    source,old=midpoint.load_endpoint(index)
    directory=midpoint.values.WORK/f'endpoint_{index:03d}'
    with np.load(directory/'value.npz',allow_pickle=False) as a:
        response=p.hs.restore_balls(a['response_box_mid_q'],a['response_box_rad_q'])
    if response.shape!=(62,) or not all(v.is_finite() for v in response):
        raise ArithmeticError('complete paired physical response required')
    source['response']=response;source['old_rate']=old
    for file in (Path(__file__),THEORY,Path(normalization.__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    source['binding']['algorithm']=ALGORITHM
    p.verify_sources(source['binding'])
    return source


def evaluate(source):
    ctx.prec=512
    cert=p.values.cert;response=source['response'];old=source['old_rate']
    psi=source['paired']['eigenbox'][:61]
    full=source['tube']['raw_segment_hull'][:98];descriptor=source['tube']['raw_segment_hull'][98]
    _,weights,_,_,_=p.values.operands();qw,rw,_,_=cert.metric_data()
    configuration=np.array([arb(float(qw[i]))*full[37+i] for i in range(37)],dtype=object)
    rw=np.array([arb(float(v)) for v in rw],dtype=object)
    weights=np.array([arb(float(v)) for v in weights],dtype=object)
    pfull=np.concatenate((np.full(37,arb(0)),psi))
    psi_action=np.concatenate((np.full(37,arb(0)),rw*psi))
    hard_action=np.concatenate((configuration,rw*response[:61]))
    da_dh=np.stack((psi_action/weights,hard_action/weights),axis=1)[:,None,:]
    with p.df.sparse.use_optimized_mixed(cert),midpoint.values.eq.affine.factored.use_ball_factored_integrand(cert,full):
        jets=cert._arb_action_jets(full)
        cr=np.asarray(cert._contracted_action(full,[pfull[:,None,None],pfull[:,None,None],da_dh],jets.dense_maps),dtype=object).reshape(2)
    value,proof=normalization.normalized_value(configuration,rw,psi,response[:61],response[-1],descriptor,*cr,normalized_eigenpair=True,bordered_orthogonality=True)
    if not all(a.overlaps(b) for a,b in zip(value,old,strict=True)):
        raise ArithmeticError('factored and original field enclosures disagree')
    p.verify_sources(source['binding'])
    from flint import fmpq
    positive=arb(fmpq(proof['original_norm_lower_rational']))>0
    report=dict(validation_passed=bool(positive),scope='SELECTED_FROZEN_AFFINE_ENDPOINT_TUBE',
        uniform_physical_value_enclosed=bool(positive),positive_physical_G_norm=bool(positive),
        physical_G_norm_lower_rational=proof['original_norm_lower_rational'],normalization_proof=proof,
        normalized_mode_and_response_orthogonality_from_paired_systems=True,
        original_field_overlap=True,paired_response_reused=True,complete_third_action_terms_recomputed=True,
        actual_HS_midpoint_domain_enclosed=False,uniform_physical_derivatives_enclosed=False,
        physical_quotient_identified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return dict(rate_candidate=value,old_rate=old,complete_descriptor_contractions=cr,
        raw_domain=source['tube']['raw_segment_hull']),report


def main():
    import argparse
    import time
    parser=argparse.ArgumentParser();parser.add_argument('--endpoint',type=int,default=13)
    parser.add_argument('--preflight',action='store_true');parser.add_argument('--recompute',action='store_true')
    args=parser.parse_args();source=load_inputs(args.endpoint)
    if args.preflight:print(json.dumps(dict(inputs_verified=True,numerical_evaluation=False)));return
    directory=WORK/f'endpoint_{args.endpoint:03d}';directory.mkdir(parents=True,exist_ok=True)
    data=directory/'value.npz';path=directory/'record.json';receipt=directory/'reproduction.json'
    previous=json.loads(path.read_bytes()) if path.exists() else None
    if args.recompute!=(previous is not None):raise RuntimeError('first/recompute state differs')
    if previous is not None and (previous['data_SHA256']!=p.values.sha(data) or path.read_bytes()!=p.geometry.encoded(previous)):
        raise RuntimeError('prior normalized field changed')
    if receipt.exists():receipt.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    candidate=directory/f'value.candidate_{time.time_ns()}.npz'
    attempted=dict(binding=source['binding'],endpoint=args.endpoint,FULL_BHSM_COMPLETE=False)
    candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted))
    try:
        arrays,report=evaluate(source)
        shapes=dict(rate_candidate=(99,),old_rate=(99,),complete_descriptor_contractions=(2,),raw_domain=(99,))
        if set(arrays)!=set(shapes) or any(a.shape!=shapes[key] or not all(v.is_finite() for v in a.flat)
                                          for key,a in arrays.items()):
            raise ArithmeticError('complete finite normalized physical value arrays required')
    except Exception as error:
        attempted['error']=repr(error);candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted));raise
    encoded={}
    for name,array in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(array)
    np.savez_compressed(candidate,**encoded)
    record=dict(algorithm=ALGORITHM,binding=source['binding'],endpoint=args.endpoint,
        data_SHA256=p.values.sha(candidate),report=report,
        radius_longitudinal_rational=str(source['tube']['radius_longitudinal'].fmpq()),
        radius_transverse_rational=str(source['tube']['radius_transverse'].fmpq()),FULL_BHSM_COMPLETE=False)
    candidate_record=candidate.with_suffix('.json');candidate_record.write_bytes(p.geometry.encoded(record))
    if not report['validation_passed']:raise ArithmeticError('normalized field failed; candidate preserved')
    if previous is not None:
        if path.read_bytes()!=candidate_record.read_bytes():raise ArithmeticError('independent normalized field differs; candidates preserved')
        candidate.unlink();candidate_record.unlink()
        receipt.write_bytes(p.geometry.encoded(dict(independent_recomputation=True,byte_identical=True,
            record_SHA256=p.values.sha(path),uniform_midpoint_field_enclosed=False,FULL_BHSM_COMPLETE=False)))
    else:candidate.replace(data);candidate_record.replace(path)
    print(json.dumps(dict(endpoint=args.endpoint,reproduced=args.recompute,validation_passed=True,FULL_BHSM_COMPLETE=False)),flush=True)


if __name__=='__main__':main()

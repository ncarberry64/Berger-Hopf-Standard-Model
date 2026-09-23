"""Enclose a reduced action Hessian on one correlated affine endpoint tube.

This pilot is not a field-rate or Hermite-Simpson midpoint certificate.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import numpy as np
from flint import arb, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_uniform_physical_value_pilot as pilot
from bhsm.interface import affine_longitudinal_hessian as affine
from bhsm.interface import ball_factored_arb_integrand as factored
from bhsm.interface import factored_arb_integrand as algebra

WORK=ROOT/'artifacts/flagship_integration/.affine_action_hessian_pilot_work'
THEORY=ROOT/'theory/n12_gate7_affine_action_hessian_pilot.md'
ALGORITHM='AFFINE_TUBE_REDUCED_ACTION_HESSIAN_MEAN_VALUE_ARB512_V1'


def load_inputs(index):
    if type(index) is not int or not 0<=index<371:
        raise ValueError('endpoint in 0..370 required')
    source=pilot.load_inputs()
    residual=pilot.geometry.residual
    base,inputs,_,axes=residual.load_foundation()
    frame_path=residual.center.JACOBIAN.with_suffix('.npz')
    with np.load(frame_path,allow_pickle=False) as arrays:
        frames=arrays['endpoint_physical_tangent_action']
        if frames.shape!=(371,98,73) or not np.isfinite(frames).all():
            raise RuntimeError('complete finite bound endpoint frames required')
        frame=residual.center.cert._frame(frames[index],residual.center.cert.TRIAL_DESCRIPTOR_SCALE)
    x,weights,descriptor,reference,_=pilot.values.operands()
    center=pilot.hs.weighted_endpoint(x[index],descriptor[index],weights)
    radii=json.loads(pilot.geometry.TRIAL_RADII.read_text())['stored_polynomial_adjudication']['witness']['radius']
    box,_=pilot.geometry.neighborhood.affine_endpoint_box(center,frame,axes[index],*radii,fixed=index==0)
    if not all(a.contains(b) for a,b in zip(source['boxes'][index],box,strict=True)):
        raise RuntimeError('affine operands differ from paired endpoint geometry')
    tube=affine.endpoint_tube(center,frame,axes[index],*radii,weights,fixed=index==0)
    files=dict(source['binding']['files'])
    for path in (Path(__file__),THEORY,Path(affine.__file__),Path(factored.__file__),
                 Path(algebra.__file__),Path(pilot.df.sparse.__file__),frame_path,residual.foundation.RESULT):
        residual.merge(files,{pilot.df.file_key(path):pilot.values.sha(path)})
    normalized=dict(source['binding']['normalized_inputs'])
    residual.merge(normalized,inputs)
    binding=dict(algorithm=ALGORITHM,precision_bits=512,files=files,normalized_inputs=normalized,
                 runtime=source['binding']['runtime'],axes_SHA256=base['axes_SHA256'])
    pilot.verify_sources(binding)
    return dict(binding=binding,tube=tube,reference=reference,index=index)


def evaluate(source, progress=None):
    ctx.prec=512
    cert=pilot.values.cert
    tube=source['tube']
    base_state=tube['raw_transverse_box'][:98]
    full_state=tube['raw_segment_hull'][:98]
    direction=tube['raw_longitudinal_direction'][:98]
    with pilot.df.sparse.use_optimized_mixed(cert), factored.use_ball_factored_integrand(cert,base_state):
        base_jets=cert._arb_action_jets(base_state)
    base=base_jets.hessian_arb[cert.QDIM:,cert.QDIM:]
    third=np.empty((cert.REDUCED,cert.REDUCED),dtype=object)
    identity=np.array([[arb(int(i==j+cert.QDIM)) for j in range(cert.REDUCED)]
                       for i in range(cert.STATE)],dtype=object)
    # Fixed four-row tiles bound memory while summing every quadrature node,
    # the global inertia reciprocal and boundary in the retained parent action.
    with pilot.df.sparse.use_optimized_mixed(cert), factored.use_ball_factored_integrand(cert,full_state):
        for start in range(0,cert.REDUCED,4):
            stop=min(start+4,cert.REDUCED)
            legs=[identity[:,start:stop,None],identity[:,None,:],direction[:,None,None]]
            tile=np.asarray(cert._contracted_action(full_state,legs,base_jets.dense_maps),dtype=object)
            if tile.shape!=(stop-start,cert.REDUCED) or not all(isinstance(v,arb) and v.is_finite() for v in tile.flat):
                raise ArithmeticError('complete finite signed third-derivative tile required')
            third[start:stop]=tile
            if progress:progress(stop,cert.REDUCED)
    hessian=affine.enclose_hessian(base,third,tube['radius_longitudinal'])
    # The verifier sees the reduced Hessian directly. It does not receive a
    # fabricated full-state matrix or a certificate from a center evaluation.
    stub=SimpleNamespace(QDIM=0,_eigenline=lambda h,m,r:pilot.proposal.propose(h,r,selected=24))
    checks=[]
    try:
        midpoint=np.array([float(v.mid()) for v in hessian.flat]).reshape(hessian.shape)
        with pilot.hs.verified_eigenline(stub,checks,expected_index=24,normalize_proposal_center=True):
            stub._eigenline(hessian,midpoint,source['reference'])
        if len(checks)!=1 or not pilot.proof_valid(checks[0]):
            raise ArithmeticError('one independent affine-tube eigenpair proof required')
        report=dict(validation_passed=True,eigenpair_inclusion=checks[0])
    except ArithmeticError as error:
        report=dict(validation_passed=False,error=repr(error),
                    eigenpair_inclusion=getattr(error,'eigenpair_inclusion',None))
    return dict(transverse_base_hessian=base,signed_longitudinal_third=third,
                affine_tube_hessian=hessian,**{k:v for k,v in tube.items() if isinstance(v,np.ndarray)}),report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--endpoint',type=int,default=13)
    parser.add_argument('--recompute',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    args=parser.parse_args()
    source=load_inputs(args.endpoint)
    if args.preflight:
        print(json.dumps(dict(endpoint=args.endpoint,inputs_verified=True,numerical_evaluation=False)),flush=True)
        return
    directory=WORK/f'endpoint_{args.endpoint:03d}'
    directory.mkdir(parents=True,exist_ok=True)
    path=directory/'matrix.npz';record_path=directory/'record.json';receipt=directory/'reproduction.json'
    previous=json.loads(record_path.read_bytes()) if record_path.exists() else None
    if args.recompute != (previous is not None):
        raise RuntimeError('first run requires no record; repeat requires an existing record')
    if previous is not None and (previous['data_SHA256']!=pilot.values.sha(path)
            or record_path.read_bytes()!=pilot.geometry.encoded(previous)):
        raise RuntimeError('prior affine Hessian evidence changed')
    if receipt.exists():receipt.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    attempt=directory/f'attempt_{time.time_ns()}.npz'
    domain={}
    for key,values in source['tube'].items():
        if isinstance(values,np.ndarray):
            domain[key+'_mid_q'],domain[key+'_rad_q']=pilot.hs.rational_balls(values)
    np.savez_compressed(attempt,**domain)
    attempted=dict(scope='ATTEMPTED_AFFINE_TUBE_DOMAIN_ONLY',endpoint=args.endpoint,
                   binding=source['binding'],data_SHA256=pilot.values.sha(attempt),FULL_BHSM_COMPLETE=False)
    attempt.with_suffix('.json').write_bytes(pilot.geometry.encoded(attempted))
    try:
        arrays,report=evaluate(source,lambda rows,total:print(json.dumps(dict(rows=rows,total=total)),flush=True))
    except Exception as error:
        attempted.update(error=repr(error),eigenpair_inclusion=getattr(error,'eigenpair_inclusion',None),
                         physical_singularity_proved=False)
        attempt.with_suffix('.json').write_bytes(pilot.geometry.encoded(attempted))
        raise
    shapes={key:(61,61) for key in ('transverse_base_hessian','signed_longitudinal_third','affine_tube_hessian')}
    shapes.update({key:(99,) for key in ('raw_transverse_box','raw_longitudinal_direction','raw_segment_hull')})
    if set(arrays)!=set(shapes) or any(values.shape!=shapes[key]
            or not all(isinstance(v,arb) and v.is_finite() for v in values.flat)
            for key,values in arrays.items()):
        raise ArithmeticError('complete finite affine Hessian and domain arrays required')
    pilot.verify_sources(source['binding'])
    encoded={}
    for key,values in arrays.items():
        encoded[key+'_mid_q'],encoded[key+'_rad_q']=pilot.hs.rational_balls(values)
    candidate=directory/f'matrix.candidate_{time.time_ns()}.npz'
    np.savez_compressed(candidate,**encoded)
    record=dict(algorithm=ALGORITHM,binding=source['binding'],endpoint=args.endpoint,
        scope='REDUCED_ACTION_HESSIAN_ON_FROZEN_AFFINE_ENDPOINT_TUBE',
        domain='z0+E*(e*l+t), |l|<=rL, ||t||2<=rT; initial endpoint fixed',
        radius_longitudinal_rational=str(source['tube']['radius_longitudinal'].fmpq()),
        radius_transverse_rational=str(source['tube']['radius_transverse'].fmpq()),
        trial_radii_recertified=False,axis_normalization_assumed=False,
        reduced_action_Hessian_shape=[61,61],signed_longitudinal_contraction_before_hull=True,
        global_inertia_and_boundary_included=True,data_SHA256=pilot.values.sha(candidate),report=report,
        full_coordinate_box_certified=False,uniform_physical_rate_enclosed=False,
        actual_HS_midpoint_neighborhood_enclosed=False,uniform_physical_DF_H_enclosed=False,
        physical_quotient_identified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    candidate_record=candidate.with_suffix('.json')
    candidate_record.write_bytes(pilot.geometry.encoded(record))
    if previous is not None:
        if record_path.read_bytes()!=candidate_record.read_bytes():
            raise ArithmeticError('independent affine Hessian differs; candidates preserved')
        candidate.unlink();candidate_record.unlink()
        receipt.write_bytes(pilot.geometry.encoded(dict(independent_recomputation=True,byte_identical=True,
            record_SHA256=pilot.values.sha(record_path),uniform_physical_rate_enclosed=False,FULL_BHSM_COMPLETE=False)))
    else:
        candidate.replace(path);candidate_record.replace(record_path)
    print(json.dumps(dict(endpoint=args.endpoint,reproduced=args.recompute,
        eigenpair_validation_passed=report['validation_passed'],FULL_BHSM_COMPLETE=False)),flush=True)


if __name__=='__main__':main()

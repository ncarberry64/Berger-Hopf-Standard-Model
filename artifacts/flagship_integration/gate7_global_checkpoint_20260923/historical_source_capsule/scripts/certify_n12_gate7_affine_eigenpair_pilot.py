"""Recompute a selected action eigenpair contraction on its full affine tube.

Every invocation computes its center witness, residual and all proposal trials
from the bound action. Earlier diagnostic arrays are never numerical inputs.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import arb,arb_mat,ctx,fmpq

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_affine_action_hessian_pilot as affine
from bhsm.interface import affine_eigenpair_contraction as bounds

p=affine.pilot
WORK=ROOT/'artifacts/flagship_integration/.affine_eigenpair_pilot_work'
THEORY=ROOT/'theory/n12_gate7_affine_eigenpair_contraction.md'
ALGORITHM='SIGNED_AFFINE_ACTION_EIGENPAIR_BANACH_ARB512_V1'
MAX_PROPOSALS=4


def load_inputs(index):
    source=affine.load_inputs(index)
    files=source['binding']['files']
    for path in (Path(__file__),THEORY,Path(bounds.__file__),
                 Path(bounds.preserve_ball.__code__.co_filename),
                 Path(bounds.exact_radius.__code__.co_filename),
                 Path(bounds._float_upper.__code__.co_filename)):
        p.geometry.residual.merge(files,{p.df.file_key(path):p.values.sha(path)})
    source['binding']['algorithm']=ALGORITHM
    p.verify_sources(source['binding'])
    return source


def contract_rows(state,left,middle,directions,maps,progress,label):
    cert=p.values.cert
    result=np.empty((62,75),dtype=object)
    with p.df.sparse.use_optimized_mixed(cert),affine.factored.use_ball_factored_integrand(cert,state):
        for start in range(0,62,4):
            stop=min(start+4,62)
            legs=[left[:,start:stop,None],middle[:,None,None],directions[:,None,:]]
            tile=np.asarray(cert._contracted_action(state,legs,maps),dtype=object)
            if tile.shape!=(stop-start,75) or not all(isinstance(v,arb) and v.is_finite() for v in tile.flat):
                raise ArithmeticError('complete finite signed action contractions required')
            result[start:stop]=tile
            if progress:progress(label,stop)
    return result


def witness_box(proof):
    if not p.proof_valid(proof):
        raise ArithmeticError('independently verified normalized oriented index-24 point witness required')
    mids,rads=proof['target_midpoints_rational'],proof['target_radii_rational']
    if len(mids)!=62 or len(rads)!=62:
        raise ArithmeticError('complete point witness required')
    result=np.array([arb(arb(fmpq(m)),arb(fmpq(r))) for m,r in zip(mids,rads,strict=True)],dtype=object)
    if not all(v.is_finite() for v in result):
        raise ArithmeticError('finite point witness required')
    return result


def evaluate(source,progress=None):
    ctx.prec=512
    cert=p.values.cert
    if (cert.QDIM,cert.REDUCED,cert.STATE)!=(37,61,98):
        raise RuntimeError('retained action dimensions changed')
    index=source['index'];tube=source['tube']
    states,weights,_,reference,_=p.values.operands()
    center=np.array([arb(float(v)) for v in states[index]],dtype=object)
    full=tube['raw_segment_hull'][:98]
    if not all(a.contains(b) for a,b in zip(full,center,strict=True)):
        raise ArithmeticError('segment hull does not contain exact action anchor')
    residual=p.geometry.residual
    with np.load(residual.center.JACOBIAN.with_suffix('.npz'),allow_pickle=False) as a:
        frame=residual.center.cert._frame(a['endpoint_physical_tangent_action'][index],residual.center.cert.TRIAL_DESCRIPTOR_SCALE)
    directions=np.empty((98,75),dtype=object)
    directions[:,0]=tube['raw_longitudinal_direction'][:98]
    for i in range(98):
        for j in range(74):directions[i,j+1]=arb(float(frame[i,j]))/arb(float(weights[i]))
    with p.df.sparse.use_optimized_mixed(cert),affine.factored.use_ball_factored_integrand(cert,full):
        inertia=sum((cert._integrand(full,node,0).inertia.d[0] for node in range(cert.POINTS)),arb(0))
    if not inertia>0:
        raise ArithmeticError('positive global inertia on entire segment hull required')
    with p.df.sparse.use_optimized_mixed(cert),affine.factored.use_ball_factored_integrand(cert,center):
        jets=cert._arb_action_jets(center)
    checks=[]
    with p.hs.verified_eigenline(cert,checks,expected_index=24,normalize_proposal_center=True):
        vector,value,_,_=cert._eigenline(jets.hessian_arb,jets.hessian_mid,reference)
    if len(checks)!=1:raise ArithmeticError('one point eigenpair proof required')
    witness=witness_box(checks[0])
    vector=np.array([v.mid() for v in vector],dtype=object);value=value.mid()
    centers=np.concatenate((vector,np.array([value],dtype=object)))
    H=arb_mat(61,61,list(jets.hessian_arb[37:,37:].flat))
    pv=arb_mat(61,1,list(vector))
    inverse=p.proposal._bordered(arb_mat(61,61,[v.mid() for v in H.entries()]),pv,value).inv()
    R=arb_mat(62,62,[v.mid() for v in inverse.entries()])
    rm=np.array(R.entries(),dtype=object).reshape(62,62)
    F=arb_mat(62,1,(H*pv-value*pv).entries()+[(pv.transpose()*pv)[0,0]/2-arb(1)/2])
    RF=R*F
    D=arb_mat(np.eye(62,dtype=int).tolist())-R*p.proposal._bordered(H,pv,value)
    defect=np.array(D.entries(),dtype=object).reshape(62,62)
    left=np.full((98,62),arb(0),dtype=object)
    left[37:]=rm[:,:61].T
    psi=np.concatenate((np.full(37,arb(0),dtype=object),vector))
    derivative=contract_rows(full,left,psi,directions,jets.dense_maps,progress,'RESIDUAL')
    rL,rT=tube['radius_longitudinal'],tube['radius_transverse']
    state_residual=bounds.affine_row_bounds(derivative,rL,rT)
    Y=np.array([(abs(RF[i,0]).upper()+state_residual[i]).upper() for i in range(62)],dtype=object)
    radii=np.array([max((2*y).upper(),(2*abs(w-c)).upper(),arb(2)**-128)
                    for y,w,c in zip(Y,witness,centers,strict=True)],dtype=object)
    arrays=dict(center_state=center,raw_segment_hull=full,affine_directions=directions,
        eigenpair_center=centers,preconditioner=rm,center_defect=defect,
        signed_residual_derivatives=derivative,residual_bounds=Y)
    trials=[]
    for attempt in range(MAX_PROPOSALS):
        perturbation=np.array([arb(0)]*37+[arb(0,r) for r in radii[:61]],dtype=object)
        derivative=contract_rows(full,left,perturbation,directions,jets.dense_maps,progress,f'VARIATION_{attempt}')
        S=bounds.affine_row_bounds(derivative,rL,rT)
        V,report=bounds.certify_rows(Y,defect,rm,radii,S)
        arrays.update({f'trial_{attempt}_'+key:val for key,val in dict(
            radii=radii.copy(),signed_variation_derivatives=derivative,variation_bounds=V).items()})
        trials.append(report)
        if report['validation_passed']:break
        radii,changed=bounds.grow_failed_coordinates(Y,V,radii)
        report['next_proposal_grown_coordinates']=changed
    box=np.array([c+arb(0,r) for c,r in zip(centers,arrays[f'trial_{attempt}_radii'],strict=True)],dtype=object)
    contained=all(b.contains(w) for b,w in zip(box,witness,strict=True))
    overlap=sum((v*arb(float(ref)) for v,ref in zip(box[:61],reference,strict=True)),arb(0))
    passed=bool(report['validation_passed'] and contained and overlap>0)
    arrays['eigenpair_box']=box
    result=dict(validation_passed=passed,point_eigenpair_proof=checks[0],trials=trials,
        witness_contained=contained,positive_original_reference_overlap=bool(overlap>0),
        original_reference_overlap_lower_rational=str(overlap.lower().fmpq()),
        segment_inertia_lower_rational=str(inertia.lower().fmpq()),
        uniform_action_eigenpair_enclosed=passed,selected_zero_based_index_verified=24 if passed else None,
        index_argument='CONNECTED_AFFINE_DOMAIN_UNIFORM_CONTRACTION_AND_SIMPLE_SYMMETRIC_EIGENPAIR_CONTINUATION',
        action_domain_bound=True,physical_trial_radii_changed=False,
        uniform_physical_rate_enclosed=False,actual_HS_midpoint_domain_enclosed=False,
        physical_quotient_identified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    p.verify_sources(source['binding'])
    return arrays,result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--endpoint',type=int,default=13)
    parser.add_argument('--recompute',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    args=parser.parse_args();source=load_inputs(args.endpoint)
    if args.preflight:
        print(json.dumps(dict(inputs_verified=True,numerical_evaluation=False)));return
    directory=WORK/f'endpoint_{args.endpoint:03d}';directory.mkdir(parents=True,exist_ok=True)
    data=directory/'eigenpair.npz';record_path=directory/'record.json';receipt=directory/'reproduction.json'
    previous=json.loads(record_path.read_bytes()) if record_path.exists() else None
    if args.recompute!=(previous is not None):
        raise RuntimeError('first run requires no record; repeat requires existing record')
    if previous is not None and (previous['data_SHA256']!=p.values.sha(data)
            or record_path.read_bytes()!=p.geometry.encoded(previous)):
        raise RuntimeError('prior eigenpair evidence changed')
    if receipt.exists():receipt.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    candidate=directory/f'eigenpair.candidate_{time.time_ns()}.npz'
    attempted=dict(binding=source['binding'],endpoint=args.endpoint,FULL_BHSM_COMPLETE=False)
    candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted))
    try:
        arrays,report=evaluate(source,lambda phase,rows:print(json.dumps(dict(phase=phase,rows=rows,total=62)),flush=True))
    except Exception as error:
        attempted['error']=repr(error)
        candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted));raise
    serialized={}
    for key,array in arrays.items():
        serialized[key+'_mid_q'],serialized[key+'_rad_q']=p.hs.rational_balls(array)
    np.savez_compressed(candidate,**serialized)
    record=dict(algorithm=ALGORITHM,binding=source['binding'],endpoint=args.endpoint,
        scope='SELECTED_REDUCED_ACTION_EIGENPAIR_ON_FROZEN_AFFINE_ENDPOINT_TUBE',
        radius_longitudinal_rational=str(source['tube']['radius_longitudinal'].fmpq()),
        radius_transverse_rational=str(source['tube']['radius_transverse'].fmpq()),
        data_SHA256=p.values.sha(candidate),report=report,FULL_BHSM_COMPLETE=False)
    candidate_record=candidate.with_suffix('.json');candidate_record.write_bytes(p.geometry.encoded(record))
    if not report['validation_passed']:
        raise ArithmeticError('affine eigenpair proof failed; candidate and all trial bounds preserved')
    if previous is not None:
        if record_path.read_bytes()!=candidate_record.read_bytes():
            raise ArithmeticError('independent eigenpair recomputation differs; candidates preserved')
        candidate.unlink();candidate_record.unlink()
        receipt.write_bytes(p.geometry.encoded(dict(independent_recomputation=True,byte_identical=True,
            record_SHA256=p.values.sha(record_path),uniform_physical_rate_enclosed=False,FULL_BHSM_COMPLETE=False)))
    else:
        candidate.replace(data);candidate_record.replace(record_path)
    print(json.dumps(dict(endpoint=args.endpoint,reproduced=args.recompute,validation_passed=True,FULL_BHSM_COMPLETE=False)),flush=True)


if __name__=='__main__':main()

"""Diagnostic: signed uniform variation residuals around verified anchor values.

This does not publish a certificate or replace any paired numerical artifact.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface import centered_coupled_variation_residual as signed
from bhsm.interface.weighted_response_enclosure import enclose_response
from bhsm.interface.ball_factored_arb_integrand import use_ball_factored_integrand
import n12_gate7_coupled_normalization_derivative_refinement as refinement
import bhsm_immutable_input_hash_cache as input_cache


def evaluate(engine,source,start,stop):
    p=engine.p;cert=p.values.cert;paired=source['paired'];count=stop-start
    _,weights,descriptors,reference,_=p.values.operands()
    directions=np.full((99,count),arb(0),dtype=object)
    for k in range(start,stop):directions[k,k-start]=arb(1)
    raw=directions[:98]/np.array([arb(float(v)) for v in weights])[:,None]
    center=paired['center'];full=paired['full'];psi=paired['eigenbox'][:61];lam=paired['eigenbox'][-1]
    descriptor=source['raw_center'][98] if 'raw_center' in source else arb(float(descriptors[source['index']]))
    if not source['raw_domain'][98].contains(descriptor):raise ArithmeticError('anchor descriptor outside original domain')
    original_solve=cert._verified_solve;point_solutions=[];checks=[]
    def point_solve(matrix,rhs):
        result=original_solve(matrix,rhs)
        point_solutions.append(np.array([v.mid() for v in result.entries()],dtype=object).reshape(result.nrows(),result.ncols()))
        return result
    try:
        cert._verified_solve=point_solve
        with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,center):
            with p.hs.verified_eigenline(cert,checks,expected_index=24,normalize_proposal_center=True):
                point=cert._rate_enclosure(center,descriptor,weights,reference,directions)
    finally:cert._verified_solve=original_solve
    if (len(checks)!=1 or not p.proof_valid(checks[0]) or len(point_solutions)!=3
            or [a.shape for a in point_solutions]!=[(62,1),(62,count),(62,count)]):
        raise ArithmeticError('verified anchor and all three original physical solves required')
    print(json.dumps(dict(phase='VERIFIED_POINT_VARIATION_CENTERS',columns=[start,stop])),flush=True)
    with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,full):
        maps=cert._arb_action_jets(full).dense_maps
    original_inverse=engine.inverse.enclose_columns;original_action=cert._contracted_action
    qw,rw,_,_=cert.metric_data();calls=[];slopes=None;proofs=[]
    def centered(R,rhs,r,V):
        nonlocal slopes
        which=len(calls)
        if which>=2:raise ArithmeticError('exactly two uniform variations required')
        fixed=point_solutions[which+1]
        if which==0:
            residual,slopes=signed.line_residual(original_action,full,psi,lam,R,fixed,raw,maps)
        else:
            residual=signed.physical_response_residual(original_action,full,psi,lam,
                source['response'][:61],source['response'][-1],calls[0][:61],slopes,
                R,fixed,qw,rw,weights,raw,maps)
        box=np.empty_like(fixed);bounds=[]
        for column in range(count):
            z=fixed[:,column].copy();z[-1]=-z[-1]
            box[:,column],proof=enclose_response(z,residual[:,column],r,V)
            box[-1,column]=-box[-1,column];bounds.append(proof)
        old,_,_=original_inverse(R,rhs,r,V)
        if not all(a.overlaps(b) for a,b in zip(box.flat,old.flat)):
            raise ArithmeticError('centered and zero-center variation enclosures disagree')
        calls.append(box.copy());proofs.append(bounds)
        print(json.dumps(dict(phase='CENTERED_VARIATION',which=which,
            maximum_radius=float(max(v.rad() for v in box.flat)),
            zero_center_maximum_radius=float(max(v.rad() for v in old.flat)))),flush=True)
        return box,residual,bounds
    try:
        engine.inverse.enclose_columns=centered
        arrays,normalization=refinement.refine_batch(engine,source,start,stop)
    finally:engine.inverse.enclose_columns=original_inverse
    if len(calls)!=2:raise ArithmeticError('both centered variations required')
    if not all(a.contains(b) for a,b in zip(arrays['derivative'].flat,point.derivative.flat)):
        raise ArithmeticError('uniform derivative must contain verified point derivative')
    arrays.update(point_derivative=point.derivative,point_line_center=point_solutions[1],
                  point_response_center=point_solutions[2],raw_domain=source['raw_domain'])
    return arrays,dict(point_eigenpair_checks=checks,centered_bounds=proofs,normalization=normalization)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=('endpoint','midpoint'),required=True)
    parser.add_argument('--index',type=int,default=13);parser.add_argument('--start',type=int,default=0)
    parser.add_argument('--stop',type=int,default=1);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if not 0<=args.start<args.stop<=99:raise ValueError('complete nonempty basis slice required')
    if args.stage=='endpoint':import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    else:import certify_n12_gate7_coupled_midpoint_uniform_derivatives as engine
    args.out.mkdir(exist_ok=False,parents=True);ctx.prec=512
    p=engine.p;residual=p.geometry.residual
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with input_cache.cache_hashes(targets,excluded_roots=[args.out]) as stats:
        source=engine.load_inputs(args.index)
        for file in (Path(__file__),Path(signed.__file__),Path(refinement.__file__),
                     Path(refinement.normalization.__file__),Path(input_cache.__file__)):
            residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
        p.verify_sources(source['binding'])
        try:arrays,proof=evaluate(engine,source,args.start,args.stop)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(binding=source['binding'],error=repr(error),FULL_BHSM_COMPLETE=False)))
            raise
        p.verify_sources(source['binding']);encoded={}
        for name,array in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(array)
        data=args.out/'diagnostic.npz';np.savez_compressed(data,**encoded)
        report=dict(binding=source['binding'],stage=args.stage,index=args.index,columns=[args.start,args.stop],
            data_SHA256=p.values.sha(data),proof=proof,maximum_derivative_radius=float(max(v.rad() for v in arrays['derivative'].flat)),
            point_derivative_containment=True,full_basis_enclosed=False,independent_recomputation=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False)
        (args.out/'record.json').write_bytes(p.geometry.encoded(report))
        print(json.dumps(dict(phase='DIAGNOSTIC_FINISHED',maximum_derivative_radius=report['maximum_derivative_radius'],immutable_input_hash_cache=stats)),flush=True)


if __name__=='__main__':main()

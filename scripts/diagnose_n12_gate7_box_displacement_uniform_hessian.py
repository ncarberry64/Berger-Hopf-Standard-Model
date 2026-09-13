"""Feasibility diagnostic: enclose every raw box displacement in one action leg."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
import certify_n12_gate7_ball_physical_hessian_graph as graph
import bhsm_immutable_input_hash_cache as cache
from bhsm.interface import centered_coupled_variation_residual as signed
from bhsm.interface import centered_mixed_coupled_variation_residual as mixed_signed
from bhsm.interface.componentwise_weighted_response import enclose_response_rows
from bhsm.interface.ball_factored_arb_integrand import use_ball_factored_integrand


def evaluate(source,column):
    p=engine.p;cert=p.values.cert
    if cert is not graph.cert:raise ArithmeticError('same retained physical action graph required')
    _,weights,descriptors,reference,_=p.values.operands()
    w=np.array([arb(float(v)) for v in weights],dtype=object)
    paired=source['paired'];center=paired['center'];full=paired['full']
    point_raw_axis=source['tube']['raw_longitudinal_direction']*source['tube']['radius_longitudinal']
    point_axis=point_raw_axis.copy();point_axis[:98]*=w
    raw_center=np.concatenate((center,np.array([arb(float(descriptors[source['index']]))],dtype=object)))
    if not all(a.contains(b) for a,b in zip(source['raw_domain'],raw_center,strict=True)):
        raise ArithmeticError('verified point anchor must lie in the complete domain')
    raw_axis=source['raw_domain']-raw_center
    if not all(a.contains(b) for a,b in zip(raw_axis,point_raw_axis,strict=True)):
        raise ArithmeticError('displacement box must contain the tested longitudinal direction')
    axis=raw_axis.copy();axis[:98]*=w
    transverse=np.full((99,1),arb(0),dtype=object);transverse[column,0]=arb(1)
    raw_v=transverse[:98]/w[:,None]
    original_solve=graph._solve;original_eigen=cert._eigenline;original_scalar=graph._batch_scalar
    point_solves=[];checks=[]
    def point_solve(matrix,rhs):
        result=original_solve(matrix,rhs)
        point_solves.append(np.array([v.mid() for v in result.flat],dtype=object).reshape(result.shape))
        return result
    try:
        graph._solve=point_solve
        with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,center):
            with p.hs.verified_eigenline(cert,checks,expected_index=24,normalize_proposal_center=True):
                point=graph.batched_axis_map(center,arb(float(descriptors[source['index']])),weights,reference,point_axis,transverse)
    finally:graph._solve=original_solve
    if len(checks)!=1 or not p.proof_valid(checks[0]) or len(point_solves)!=7 or any(a.shape!=(62,1) for a in point_solves):
        raise ArithmeticError('verified anchor and all seven original Hessian solves required')
    print(json.dumps(dict(phase='VERIFIED_POINT_HESSIAN',maximum_absolute=float(max(abs(v).upper() for v in point.flat)))),flush=True)
    psi=paired['eigenbox'][:61];lam=paired['eigenbox'][-1];R=paired['rm']
    solved=[];proofs=[];residuals=[];slopes={};scalar=[]
    qw,rw,_,_=cert.metric_data()
    with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,full):
        maps=cert._arb_action_jets(full).dense_maps
    action=cert._contracted_action
    def scalar_capture(*args,**kwargs):
        result=original_scalar(*args,**kwargs)
        scalar.append(tuple(np.asarray(v,dtype=object).copy() for v in result))
        return result
    def solve(matrix,rhs):
        which=len(solved)
        if matrix.nrows()!=62 or matrix.ncols()!=62 or np.shape(rhs)!=(62,1):
            raise ArithmeticError('complete same-family physical Hessian solve required')
        if which==0:
            result=source['response'][:,None].copy();solved.append(result)
            return result
        if which>6:raise ArithmeticError('exactly seven original Hessian solves required')
        fixed=point_solves[which]
        if which in (1,3):
            direction=raw_axis[:98,None] if which==1 else raw_v
            residual,slopes[which]=signed.line_residual(action,full,psi,lam,R,fixed,direction,maps)
        elif which in (2,4):
            direction=raw_axis[:98,None] if which==2 else raw_v
            residual=signed.physical_response_residual(action,full,psi,lam,
                source['response'][:61],source['response'][-1],solved[which-1][:61],slopes[which-1],
                R,fixed,qw,rw,weights,direction,maps)
        else:
            axis_jet=dict(direction=raw_axis[:98,None],psi=solved[1][:61],hard=solved[2][:61],
                border=solved[2][-1],eigenvalue=slopes[1])
            transverse_jet=dict(direction=raw_v,psi=solved[3][:61],hard=solved[4][:61],
                border=solved[4][-1],eigenvalue=slopes[3])
            if which==5:
                residual,slopes[5]=mixed_signed.line_residual(action,full,psi,lam,R,fixed,
                    axis_jet,transverse_jet,maps)
            else:
                residual=mixed_signed.physical_response_residual(action,full,psi,lam,
                    source['response'][:61],source['response'][-1],solved[5][:61],slopes[5],
                    R,fixed,qw,rw,weights,axis_jet,transverse_jet,maps)
        z=fixed[:,0].copy();z[-1]=-z[-1]
        result,proof=enclose_response_rows(z,residual[:,0],paired['radii'],paired['variation'])
        result[-1]=-result[-1];result=result[:,None]
        solved.append(result);proofs.append(proof);residuals.append(residual)
        print(json.dumps(dict(phase='UNIFORM_HESSIAN_SOLVE',solve=which,maximum_radius=float(max(v.rad() for v in result.flat)))),flush=True)
        return result
    try:
        graph._solve=solve;graph._batch_scalar=scalar_capture
        cert._eigenline=lambda *args:(psi,lam,arb(0),arb(0))
        with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,full):
            uniform=graph.batched_axis_map(full,source['raw_domain'][98],weights,reference,axis,transverse)
    finally:
        graph._solve=original_solve;graph._batch_scalar=original_scalar;cert._eigenline=original_eigen
    if len(solved)!=7 or len(scalar)!=1 or uniform.shape!=(99,1) or not all(v.is_finite() for v in uniform.flat):
        raise ArithmeticError('complete finite original uniform physical Hessian graph required')
    if not all(a.contains(b) for a,b in zip(uniform.flat,point.flat)):
        raise ArithmeticError('uniform physical Hessian must contain the verified point result')
    arrays=dict(point_hessian=point,uniform_hessian=uniform,point_solve_centers=np.stack(point_solves),
        uniform_solutions=np.stack(solved),preconditioned_residuals=np.stack(residuals),
        raw_domain=source['raw_domain'],weighted_axis=axis,weighted_transverse=transverse,
        raw_point_anchor=raw_center,weighted_point_test_axis=point_axis)
    for name,value in zip(('descriptor_base','descriptor_first_axis','descriptor_first_transverse','descriptor_mixed'),scalar[0]):arrays[name]=value
    return arrays,dict(point_eigenpair_checks=checks,solve_proofs=proofs,
        complete_original_seven_solve_graph_used=True,complete_original_scalar_contractions_used=True,
        complete_signed_mixed_line_and_response_residuals_used=True,
        maximum_uniform_absolute=float(max(abs(v).upper() for v in uniform.flat)),
        maximum_uniform_radius=float(max(v.rad() for v in uniform.flat)),
        maximum_point_absolute=float(max(abs(v).upper() for v in point.flat)),
        one_scaled_longitudinal_direction_only=False,full_affine_direction_coverage=False,
        complete_raw_box_displacement_direction_enclosed=True,
        point_test_uses_contained_longitudinal_direction=True,
        mean_value_derivative_bound_certified=False,full_transverse_input_basis=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--endpoint',type=int,default=13)
    parser.add_argument('--column',type=int,default=0);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if not 0<=args.column<99:raise ValueError('physical input column in 0..98 required')
    args.out.mkdir(exist_ok=False,parents=True);ctx.prec=512;p=engine.p;residual=p.geometry.residual
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with cache.cache_hashes(targets,excluded_roots=[args.out]):
        source=engine.load_inputs(args.endpoint)
        for file in (Path(__file__),Path(graph.__file__),Path(graph.parent.__file__),Path(graph.parent.original.__file__),
                     Path(graph._batch_scalar.__code__.co_filename),Path(signed.__file__),Path(mixed_signed.__file__),
                     Path(sys.modules[enclose_response_rows.__module__].__file__),Path(cache.__file__)):
            residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
        p.verify_sources(source['binding'])
        try:arrays,proof=evaluate(source,args.column)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(binding=source['binding'],error=repr(error),FULL_BHSM_COMPLETE=False)))
            raise
        encoded={}
        for name,array in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(array)
        data=args.out/'hessian.npz';np.savez_compressed(data,**encoded);p.verify_sources(source['binding'])
        record=dict(binding=source['binding'],endpoint=args.endpoint,column=args.column,data_SHA256=p.values.sha(data),
                    report=proof,independent_recomputation=False,FULL_BHSM_COMPLETE=False)
        (args.out/'record.json').write_bytes(p.geometry.encoded(record))
        print(json.dumps(dict(phase='UNIFORM_HESSIAN_DIAGNOSTIC_FINISHED',
            maximum_uniform_absolute=proof['maximum_uniform_absolute'],
            maximum_uniform_radius=proof['maximum_uniform_radius'],
            maximum_point_absolute=proof['maximum_point_absolute'],
            independent_recomputation=False,FULL_BHSM_COMPLETE=False)),flush=True)


if __name__=='__main__':main()

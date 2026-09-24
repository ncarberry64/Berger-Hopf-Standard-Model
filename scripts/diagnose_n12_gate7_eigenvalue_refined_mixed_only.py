"""Diagnostic affine-state action contractions inside complete mixed residuals."""
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
from bhsm.interface import affine_action_contraction as affine_action
from bhsm.interface.componentwise_weighted_response import enclose_response_rows
from bhsm.interface.ball_factored_arb_integrand import use_ball_factored_integrand


def evaluate(source,column):
    p=engine.p;cert=p.values.cert
    if cert is not graph.cert:raise ArithmeticError('same retained physical action graph required')
    _,weights,descriptors,reference,_=p.values.operands()
    w=np.array([arb(float(v)) for v in weights],dtype=object)
    paired=source['paired'];center=paired['center'];full=paired['full']
    raw_axis=source['tube']['raw_longitudinal_direction']*source['tube']['radius_longitudinal']
    axis=raw_axis.copy();axis[:98]*=w
    transverse=np.full((99,1),arb(0),dtype=object);transverse[column,0]=arb(1)
    raw_v=transverse[:98]/w[:,None]
    original_solve=graph._solve;original_eigen=cert._eigenline;original_scalar=graph._batch_scalar
    point=source['saved_point_hessian']
    point_solves=list(source['saved_point_centers'])
    checks=source['saved_point_checks']
    if point.shape!=(99,1) or len(point_solves)!=7 or any(a.shape!=(62,1) for a in point_solves):
        raise ArithmeticError('complete saved point anchors required')
    print(json.dumps(dict(phase='FROZEN_POINT_ANCHORS_REUSED',new_point_solves=0)),flush=True)
    psi=paired['eigenbox'][:61];lam=paired['eigenbox'][-1];R=paired['rm']
    solved=[];proofs=[];residuals=[];slopes={};scalar=[]
    qw,rw,_,_=cert.metric_data()
    with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,full):
        maps=cert._arb_action_jets(full).dense_maps
    original_action=cert._contracted_action
    base_integrand=cert._integrand
    base_state=source['tube']['raw_transverse_box'][:98]
    raw_long=source['tube']['raw_longitudinal_direction'][:98]
    radius=source['tube']['radius_longitudinal']
    with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,base_state):
        base_maps=cert._arb_action_jets(base_state).dense_maps
    action_counts={2:0,3:0,4:0}
    def at_base(legs):
        active=cert._integrand
        try:
            cert._integrand=base_integrand
            with use_ball_factored_integrand(cert,base_state):
                return original_action(base_state,list(legs),base_maps)
        finally:cert._integrand=active
    def action(state,legs,active_maps):
        if len(legs) not in action_counts:raise ArithmeticError('complete supported next action order required')
        action_counts[len(legs)]+=1
        return affine_action.contract_affine(at_base,
            lambda extended:original_action(full,list(extended),active_maps),legs,raw_long,radius)
    # Only the missing mixed solves are refined. Existing first variations
    # remain valid on this identical original domain. Recover their actual
    # eigenvalue slopes, which the prior artifact did not save.
    from bhsm.interface.selected_eigenvalue_variation import eigenvalue_slopes
    with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,full):
        recovered=eigenvalue_slopes(action,full,psi,np.concatenate((raw_axis[:98,None],raw_v),axis=1),maps)
    slopes[1]=recovered[:1];slopes[3]=recovered[1:]
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
        if which<=4:
            result=source['prior_solutions'][which].copy()
            solved.append(result);proofs.append(source['prior_proofs'][which-1])
            residuals.append(source['prior_residuals'][which-1].copy())
            return result
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
        raw_domain=source['raw_domain'],weighted_axis=axis,weighted_transverse=transverse)
    for name,value in zip(('descriptor_base','descriptor_first_axis','descriptor_first_transverse','descriptor_mixed'),scalar[0]):arrays[name]=value
    return arrays,dict(point_eigenpair_checks=checks,solve_proofs=proofs,
        complete_original_seven_solve_graph_used=True,complete_original_scalar_contractions_used=True,
        complete_signed_mixed_line_and_response_residuals_used=True,
        affine_state_action_contraction_counts=action_counts,
        complete_next_action_orders_through_five_used=True,original_scalar_order_five_unchanged=True,
        maximum_uniform_absolute=float(max(abs(v).upper() for v in uniform.flat)),
        maximum_uniform_radius=float(max(v.rad() for v in uniform.flat)),
        maximum_point_absolute=float(max(abs(v).upper() for v in point.flat)),
        one_scaled_longitudinal_direction_only=True,full_affine_direction_coverage=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--endpoint',type=int,default=13)
    parser.add_argument('--column',type=int,default=0);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--primal-pair',type=Path,required=True)
    parser.add_argument('--saved',type=Path,required=True)
    parser.add_argument('--prior-mixed',type=Path,required=True)
    parser.add_argument('--eigenvalue-pair',type=Path,required=True)
    args=parser.parse_args()
    args.prior_mixed=args.prior_mixed.resolve();args.eigenvalue_pair=args.eigenvalue_pair.resolve()
    args.saved=args.saved.resolve();args.primal_pair=args.primal_pair.resolve()
    if not 0<=args.column<99:raise ValueError('physical input column in 0..98 required')
    args.out.mkdir(exist_ok=False,parents=True);ctx.prec=512;p=engine.p;residual=p.geometry.residual
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with cache.cache_hashes(targets,excluded_roots=[args.out]):
        source=engine.load_inputs(args.endpoint)
        from diagnose_n12_gate7_mean_value_bootstrap_hessian import select_first_variation
        original_binding=dict(source['binding'])
        for folder in (args.saved,args.primal_pair/'first'):
            r=json.loads((folder/'record.json').read_bytes())
            if r['endpoint']!=args.endpoint:raise ValueError('same endpoint required')
            for key,value in original_binding.items():
                if key=='files':
                    if any(r['binding']['files'].get(k)!=v for k,v in value.items()):
                        raise ValueError('same original family inputs required')
                elif r['binding'].get(key)!=value:raise ValueError('same original domain required')
        saved_record=json.loads((args.saved/'record.json').read_bytes())
        if saved_record['column']!=args.column:raise ValueError('same frozen column required')
        if saved_record['data_SHA256']!=p.values.sha(args.saved/'hessian.npz'):
            raise ValueError('saved point anchor data changed')
        with np.load(args.saved/'hessian.npz',allow_pickle=False) as a:
            source['saved_point_hessian']=p.hs.restore_balls(a['point_hessian_mid_q'],a['point_hessian_rad_q'])
            source['saved_point_centers']=p.hs.restore_balls(a['point_solve_centers_mid_q'],a['point_solve_centers_rad_q'])
        source['saved_point_checks']=saved_record['report']['point_eigenpair_checks']
        if len(source['saved_point_checks'])!=1 or not p.proof_valid(source['saved_point_checks'][0]):
            raise ValueError('verified frozen point branch required')
        receipt=json.loads((args.primal_pair/'reproduction.json').read_bytes())
        if not all(receipt.get(k) is True for k in ('independent_recomputation','byte_identical','fresh_process')):
            raise ValueError('paired primal values required')
        for name in ('column.npz','record.json'):
            if receipt['files_SHA256'].get(name)!=p.values.sha(args.primal_pair/'first'/name):
                raise ValueError('paired primal input changed')
        primal=json.loads((args.primal_pair/'first/record.json').read_bytes())
        if not all(primal['report'].get(k) is True for k in
            ('same_family_segment_smoothness_established','uniform_primal_psi_and_response_enclosed','all_75_scaled_directions_verified')):
            raise ValueError('original-domain uniform primal proof required')
        with np.load(args.primal_pair/'first/column.npz',allow_pickle=False) as a:
            psi=p.hs.restore_balls(a['psi_value_mid_q'],a['psi_value_rad_q'])
            response=p.hs.restore_balls(a['response_value_mid_q'],a['response_value_rad_q'])
        source['paired']=dict(source['paired']);source['paired']['eigenbox']=source['paired']['eigenbox'].copy()
        source['response']=source['response'].copy()
        selected=dict(psi=select_first_variation(source['paired']['eigenbox'][:61],psi[:,0]),
            response=select_first_variation(source['response'],response[:,0]))
        print(json.dumps(dict(phase='PAIRED_PRIMAL_VALUES_SELECTED',coordinates=selected)),flush=True)
        eigenrecord=json.loads((args.eigenvalue_pair/'first/record.json').read_bytes())
        eigenreceipt=json.loads((args.eigenvalue_pair/'reproduction.json').read_bytes())
        if not all(eigenreceipt.get(k) is True for k in ('independent_recomputation','byte_identical','fresh_process')):
            raise ValueError('independent eigenvalue repeat required')
        for name in ('record.json','column.npz'):
            if eigenreceipt['files_SHA256'][name]!=p.values.sha(args.eigenvalue_pair/'first'/name):
                raise ValueError('eigenvalue pair changed')
        if eigenrecord['endpoint']!=args.endpoint or eigenrecord['report']['uniform_selected_eigenvalue_enclosed'] is not True:
            raise ValueError('same endpoint eigenvalue family required')
        for key,value in original_binding.items():
            if key=='files':
                if any(eigenrecord['binding']['files'].get(k)!=v for k,v in value.items()):
                    raise ValueError('same original eigenvalue inputs required')
            elif eigenrecord['binding'].get(key)!=value:raise ValueError('same eigenvalue domain required')
        with np.load(args.eigenvalue_pair/'first/column.npz',allow_pickle=False) as a:
            candidate=p.hs.restore_balls(a['eigenvalue_mid_q'],a['eigenvalue_rad_q'])
        select_first_variation(source['paired']['eigenbox'][-1:],candidate)
        prior=json.loads((args.prior_mixed/'record.json').read_bytes())
        if prior['endpoint']!=args.endpoint or prior['column']!=args.column or prior['data_SHA256']!=p.values.sha(args.prior_mixed/'hessian.npz'):
            raise ValueError('same prior mixed jet data required')
        if prior['report'].get('paired_primal_values_used') is not True:raise ValueError('paired primal family required')
        for name in ('record.json','column.npz'):
            key=p.df.file_key(args.primal_pair/'first'/name)
            if prior['binding']['files'].get(key)!=p.values.sha(args.primal_pair/'first'/name):
                raise ValueError('prior jet uses another primal family')
        with np.load(args.prior_mixed/'hessian.npz',allow_pickle=False) as a:
            source['prior_solutions']=p.hs.restore_balls(a['uniform_solutions_mid_q'],a['uniform_solutions_rad_q'])
            source['prior_residuals']=p.hs.restore_balls(a['preconditioned_residuals_mid_q'],a['preconditioned_residuals_rad_q'])
        source['prior_proofs']=prior['report']['solve_proofs']
        for file in (args.prior_mixed/'record.json',args.prior_mixed/'hessian.npz',
            args.eigenvalue_pair/'first/record.json',args.eigenvalue_pair/'first/column.npz',args.eigenvalue_pair/'reproduction.json'):
            residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
        for file in (args.saved/'record.json',args.saved/'hessian.npz',args.primal_pair/'first/record.json',
                     args.primal_pair/'first/column.npz',args.primal_pair/'reproduction.json',
                     Path(sys.modules[select_first_variation.__module__].__file__)):
            residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
        for file in (Path(__file__),Path(graph.__file__),Path(graph.parent.__file__),Path(graph.parent.original.__file__),
                     Path(graph._batch_scalar.__code__.co_filename),Path(signed.__file__),Path(mixed_signed.__file__),Path(affine_action.__file__),
                     Path(sys.modules[enclose_response_rows.__module__].__file__),Path(cache.__file__)):
            residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
        p.verify_sources(source['binding'])
        try:
            arrays,proof=evaluate(source,args.column)
            proof.update(frozen_point_hessian_and_anchors_reused=True,new_point_solves=0,
                paired_primal_values_used=True,primal_coordinates_tightened=selected,
                eigenvalue_refined=True,original_physical_domain_unchanged=True,first_variation_solves_reused=True,new_mixed_solves_only=[5,6])
            arrays['normalization_psi']=source['paired']['eigenbox'][:61]
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

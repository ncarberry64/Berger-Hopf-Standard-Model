"""Complete uniform mixed variations on the paired actual midpoint domain."""
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
import certify_n12_gate7_coupled_midpoint_uniform_derivatives as engine
import certify_n12_gate7_ball_physical_hessian_graph as graph
import bhsm_immutable_input_hash_cache as cache
from bhsm.interface import centered_coupled_variation_residual as signed
from bhsm.interface import centered_mixed_coupled_variation_residual as mixed_signed
from bhsm.interface import coupled_physical_normalization_second as normalization
from bhsm.interface.componentwise_weighted_response import enclose_response_rows
from bhsm.interface.ball_factored_arb_integrand import use_ball_factored_integrand


def evaluate(source,column):
    p=engine.p;cert=p.values.cert
    if cert is not graph.cert:raise ArithmeticError('same retained physical graph required')
    paired=source['paired'];center=paired['center'];full=paired['full']
    _,weights,descriptors,reference,_=p.values.operands()
    w=np.array([arb(float(v)) for v in weights],dtype=object)
    qw,rw,_,_=cert.metric_data();q=np.array([arb(float(v)) for v in qw],dtype=object)
    reduced=np.array([arb(float(v)) for v in rw],dtype=object)
    from bhsm.interface.affine_hs_midpoint_domain import group_row_bounds
    axis=source['_axis'].copy()
    if axis.shape!=(99,) or any(not v.rad().is_zero() for v in axis):
        raise ValueError('complete exact paired midpoint center direction required')
    raw_axis=axis.copy();raw_axis[:98]/=w
    directions=source['_weighted_tube_directions'].copy()
    if directions.shape!=(99,249):raise ValueError('all actual midpoint directions required')
    def support(array):return group_row_bounds(array,source['_unit_groups'])
    raw_v=directions[:98]/w[:,None]
    def product(a,b):
        result=arb_mat(*a.shape,list(a.flat))*arb_mat(*b.shape,list(b.flat))
        return np.array(result.entries(),dtype=object).reshape(result.nrows(),result.ncols())
    seeds={1:source['_axis_seed_line'][:61],2:source['_axis_seed_response'],
           3:product(source['_full_seed_line'][:61],directions),
           4:product(source['_full_seed_response'],directions)}
    seed_selections=[]
    original_solve=graph._solve;original_eigen=cert._eigenline;original_scalar=graph._batch_scalar
    point_full=[];point_centers=[];checks=[]
    def point_solve(matrix,rhs):
        result=original_solve(matrix,rhs);point_full.append(result.copy())
        point_centers.append(np.array([v.mid() for v in result.flat],dtype=object).reshape(result.shape))
        return result
    try:
        graph._solve=point_solve
        with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,center):
            with p.hs.verified_eigenline(cert,checks,expected_index=24,normalize_proposal_center=True):
                point=graph.batched_axis_map(center,source['raw_center'][98],weights,reference,axis,directions)
    finally:graph._solve=original_solve
    shapes=[(62,1)]*3+[(62,249)]*4
    if len(checks)!=1 or not p.proof_valid(checks[0]) or len(point_centers)!=7 or [v.shape for v in point_centers]!=shapes:
        raise ArithmeticError('verified point and complete mixed-column solve graph required')
    df_checks=[]
    with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,center):
        with p.hs.verified_eigenline(cert,df_checks,expected_index=24,normalize_proposal_center=True):
            point_df=cert._rate_enclosure(center,source['raw_center'][98],weights,reference,axis[:,None]).derivative
    if len(df_checks)!=1 or not p.proof_valid(df_checks[0]) or point_df.shape!=(99,1):
        raise ArithmeticError('verified point derivative for the identical input column required')
    print(json.dumps(dict(phase='VERIFIED_POINT_AFFINE_BASIS',columns=249,source_trial_column=column)),flush=True)
    psi=paired['eigenbox'][:61];lam=paired['eigenbox'][-1];R=paired['rm']
    solved=[];proofs=[];residuals=[];slopes={};scalar=[]
    with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,full):
        maps=cert._arb_action_jets(full).dense_maps
    action=cert._contracted_action
    def scalar_capture(*args,**kwargs):
        result=original_scalar(*args,**kwargs)
        scalar.append(tuple(np.asarray(v,dtype=object).copy() for v in result));return result
    def solve(matrix,rhs):
        which=len(solved)
        if which>6 or (matrix.nrows(),matrix.ncols())!=(62,62) or np.shape(rhs)!=shapes[which]:
            raise ArithmeticError('complete expected same-family bordered solve required')
        if which==0:
            result=source['response'][:,None].copy();solved.append(result);return result
        fixed=point_centers[which];count=fixed.shape[1]
        if which in (1,3):
            direction=raw_axis[:98,None] if which==1 else raw_v
            res,slopes[which]=signed.line_residual(action,full,psi,lam,R,fixed,direction,maps)
        elif which in (2,4):
            direction=raw_axis[:98,None] if which==2 else raw_v
            res=signed.physical_response_residual(action,full,psi,lam,source['response'][:61],source['response'][-1],
                solved[which-1][:61],slopes[which-1],R,fixed,qw,rw,weights,direction,maps)
        else:
            u=dict(direction=raw_axis[:98,None],psi=solved[1][:61],hard=solved[2][:61],border=solved[2][-1],eigenvalue=slopes[1])
            v=dict(direction=raw_v,psi=solved[3][:61],hard=solved[4][:61],border=solved[4][-1],eigenvalue=slopes[3])
            if which==5:res,slopes[5]=mixed_signed.line_residual(action,full,psi,lam,R,fixed,u,v,maps)
            else:res=mixed_signed.physical_response_residual(action,full,psi,lam,source['response'][:61],source['response'][-1],
                solved[5][:61],slopes[5],R,fixed,qw,rw,weights,u,v,maps)
        result=np.empty_like(fixed);rows=[]
        for k in range(count):
            z=fixed[:,k].copy();z[-1]=-z[-1]
            result[:,k],proof=enclose_response_rows(z,res[:,k],paired['radii'],paired['variation'])
            result[-1,k]=-result[-1,k];rows.append(proof)
        if which in seeds:
            seed=seeds[which];wanted_rows=61 if which in (1,3) else 62
            if seed.shape!=(wanted_rows,count):raise ArithmeticError('complete same-direction first-variation seed required')
            changed=0
            for i,k in np.ndindex(seed.shape):
                value=seed[i,k]
                if not value.is_finite() or not value.overlaps(result[i,k]):
                    raise ArithmeticError('paired and recomputed first variations disagree')
                if value.rad()<result[i,k].rad():result[i,k]=value;changed+=1
            seed_selections.append(dict(solve=which,coordinates_tightened=changed,
                                        retained_auxiliary_line_border=which in (1,3)))
        solved.append(result);proofs.append(rows);residuals.append(res)
        print(json.dumps(dict(phase='UNIFORM_AFFINE_BASIS_SOLVE',solve=which,columns=count,
            maximum_radius=float(max(v.rad() for v in result.flat)))),flush=True)
        return result
    try:
        graph._solve=solve;graph._batch_scalar=scalar_capture
        cert._eigenline=lambda *args:(psi,lam,arb(0),arb(0))
        with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,full):
            uniform=graph.batched_axis_map(full,source['raw_domain'][98],weights,reference,axis,directions)
    finally:graph._solve=original_solve;graph._batch_scalar=original_scalar;cert._eigenline=original_eigen
    if len(solved)!=7 or len(scalar)!=1 or uniform.shape!=(99,249):raise ArithmeticError('complete 249-direction graph required')
    cr,cru,crv,cruv=scalar[0]
    def jet(line,response,configuration,descriptor,values):
        return dict(configuration=configuration,psi=solved[line][:61],hard=solved[response][:61],
            border=solved[response][-1],descriptor=descriptor,cpsi=values[:,0],remainder=values[:,1])
    u=jet(1,2,(q*raw_axis[37:74])[:,None],axis[98:99],cru[None,:])
    v=jet(3,4,q[:,None]*raw_v[37:74],directions[98],crv)
    uv=jet(5,6,np.full((37,249),arb(0),dtype=object),np.full(249,arb(0),dtype=object),cruv)
    normalized,norm_proof=normalization.normalized_mixed(q*full[37:74],reduced,psi,solved[0][:61,0],solved[0][-1,0],
        source['raw_domain'][98],*cr,u,v,uv,coupled_identities_and_variations=True)
    if not all(a.overlaps(b) for a,b in zip(normalized.flat,uniform.flat,strict=True)):
        raise ArithmeticError('equivalent complete physical Hessian normalizations disagree')
    if not all(a.contains(b) for a,b in zip(normalized.flat,point.flat,strict=True)):
        raise ArithmeticError('all 249 verified point Hessian columns must be contained')
    physical_support=support(normalized);line_support=support(solved[5][:61]);response_support=support(solved[6])
    def candidate(anchor,bound):return anchor+np.array([arb(0,v) for v in bound],dtype=object)[:,None]
    arrays=dict(point_hessian=point,uniform_hessian=uniform,normalized_hessian=normalized,point_derivative=point_df,
        raw_domain=source['raw_domain'],weighted_input_axis=axis,weighted_tube_directions=directions,
        physical_mean_value_support=physical_support,line_mean_value_support=line_support,response_mean_value_support=response_support,
        derivative_candidate=candidate(point_df,physical_support),line_candidate=candidate(point_full[1][:61],line_support),
        response_candidate=candidate(point_full[2],response_support))
    for i in range(7):
        arrays[f'point_solve_{i}']=point_full[i];arrays[f'point_center_{i}']=point_centers[i];arrays[f'uniform_solve_{i}']=solved[i]
        if i:arrays[f'preconditioned_residual_{i}']=residuals[i-1]
    for name,value in zip(('descriptor_base','descriptor_first_axis','descriptor_first_transverse','descriptor_mixed'),scalar[0]):arrays[name]=value
    report=dict(point_eigenpair_checks=checks,point_derivative_checks=df_checks,solve_proofs=proofs,normalization_proof=norm_proof,
        all_249_scaled_midpoint_directions_enclosed=True,source_trial_column=column,full_physical_input_basis=False,
        paired_first_variation_seeds_used=True,seed_selections=seed_selections,
        mean_value_candidates_require_same_family_segment_smoothness=True,candidates_consumed_by_production=False,
        maximum_physical_mean_value_support=float(max(physical_support)),maximum_line_mean_value_support=float(max(line_support)),
        maximum_response_mean_value_support=float(max(response_support)),maximum_normalized_hessian_radius=float(max(v.rad() for v in normalized.flat)),
        maximum_point_hessian_absolute=float(max(abs(v).upper() for v in point.flat)),
        complete_original_seven_solve_graph_used=True,complete_original_scalar_contractions_used=True,
        all_249_point_columns_contained=True,independent_recomputation=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return arrays,report

"""All 75 scaled tube directions against one fixed physical input column."""
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
import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
import certify_n12_gate7_ball_physical_hessian_graph as graph
import bhsm_immutable_input_hash_cache as cache
from bhsm.interface import centered_coupled_variation_residual as signed
from bhsm.interface import centered_mixed_coupled_variation_residual as mixed_signed
from bhsm.interface import coupled_physical_normalization_second as normalization
from bhsm.interface.componentwise_weighted_response import enclose_response_rows
from bhsm.interface.ball_factored_arb_integrand import use_ball_factored_integrand


def support(array):
    """Scaled long interval plus scaled 74-dimensional Euclidean support."""
    if array.ndim!=2 or array.shape[1]!=75:raise ValueError('all 75 scaled tube columns required')
    return np.array([(abs(row[0]).upper()+sum((abs(v).upper()**2 for v in row[1:]),arb(0)).sqrt()).upper()
        for row in array],dtype=object)


def evaluate(source,column):
    p=engine.p;cert=p.values.cert
    if cert is not graph.cert:raise ArithmeticError('same retained physical graph required')
    paired=source['paired'];center=paired['center'];full=paired['full'];tube=source['tube']
    _,weights,descriptors,reference,_=p.values.operands()
    w=np.array([arb(float(v)) for v in weights],dtype=object)
    qw,rw,_,_=cert.metric_data();q=np.array([arb(float(v)) for v in qw],dtype=object)
    reduced=np.array([arb(float(v)) for v in rw],dtype=object)
    residual=p.geometry.residual
    with np.load(residual.center.JACOBIAN.with_suffix('.npz'),allow_pickle=False) as a:
        frame=residual.center.cert._frame(a['endpoint_physical_tangent_action'][source['index']],residual.center.cert.TRIAL_DESCRIPTOR_SCALE)
    if frame.shape!=(99,74):raise ArithmeticError('complete frozen augmented frame required')
    axis=np.full(99,arb(0),dtype=object);axis[column]=arb(1)
    raw_axis=axis.copy();raw_axis[:98]/=w
    directions=np.empty((99,75),dtype=object)
    directions[:,0]=tube['raw_longitudinal_direction']*tube['radius_longitudinal']
    directions[:98,0]*=w
    directions[:,1:]=np.array([arb(float(v)) for v in frame.flat],dtype=object).reshape(frame.shape)*tube['radius_transverse']
    raw_v=directions[:98]/w[:,None]
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
                point=graph.batched_axis_map(center,arb(float(descriptors[source['index']])),weights,reference,axis,directions)
    finally:graph._solve=original_solve
    shapes=[(62,1)]*3+[(62,75)]*4
    if len(checks)!=1 or not p.proof_valid(checks[0]) or len(point_centers)!=7 or [v.shape for v in point_centers]!=shapes:
        raise ArithmeticError('verified point and complete mixed-column solve graph required')
    df_checks=[]
    with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,center):
        with p.hs.verified_eigenline(cert,df_checks,expected_index=24,normalize_proposal_center=True):
            point_df=cert._rate_enclosure(center,arb(float(descriptors[source['index']])),weights,reference,axis[:,None]).derivative
    if len(df_checks)!=1 or not p.proof_valid(df_checks[0]) or point_df.shape!=(99,1):
        raise ArithmeticError('verified point derivative for the identical input column required')
    print(json.dumps(dict(phase='VERIFIED_POINT_AFFINE_BASIS',columns=75,input_column=column)),flush=True)
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
    if len(solved)!=7 or len(scalar)!=1 or uniform.shape!=(99,75):raise ArithmeticError('complete 75-direction graph required')
    cr,cru,crv,cruv=scalar[0]
    def jet(line,response,configuration,descriptor,values):
        return dict(configuration=configuration,psi=solved[line][:61],hard=solved[response][:61],
            border=solved[response][-1],descriptor=descriptor,cpsi=values[:,0],remainder=values[:,1])
    u=jet(1,2,(q*raw_axis[37:74])[:,None],axis[98:99],cru[None,:])
    v=jet(3,4,q[:,None]*raw_v[37:74],directions[98],crv)
    uv=jet(5,6,np.full((37,75),arb(0),dtype=object),np.full(75,arb(0),dtype=object),cruv)
    normalized,norm_proof=normalization.normalized_mixed(q*full[37:74],reduced,psi,solved[0][:61,0],solved[0][-1,0],
        source['raw_domain'][98],*cr,u,v,uv,coupled_identities_and_variations=True)
    if not all(a.overlaps(b) for a,b in zip(normalized.flat,uniform.flat,strict=True)):
        raise ArithmeticError('equivalent complete physical Hessian normalizations disagree')
    if not all(a.contains(b) for a,b in zip(normalized.flat,point.flat,strict=True)):
        raise ArithmeticError('all 75 verified point Hessian columns must be contained')
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
        all_75_scaled_affine_tube_directions_enclosed=True,physical_input_columns=[column],full_physical_input_basis=False,
        mean_value_candidates_require_same_family_segment_smoothness=True,candidates_consumed_by_production=False,
        maximum_physical_mean_value_support=float(max(physical_support)),maximum_line_mean_value_support=float(max(line_support)),
        maximum_response_mean_value_support=float(max(response_support)),maximum_normalized_hessian_radius=float(max(v.rad() for v in normalized.flat)),
        maximum_point_hessian_absolute=float(max(abs(v).upper() for v in point.flat)),
        complete_original_seven_solve_graph_used=True,complete_original_scalar_contractions_used=True,
        all_75_point_columns_contained=True,independent_recomputation=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return arrays,report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--endpoint',type=int,default=13)
    parser.add_argument('--column',type=int,default=0);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    if not 0<=args.column<99:raise ValueError('physical input column in 0..98 required')
    args.out.mkdir(parents=True,exist_ok=False);ctx.prec=512;p=engine.p;residual=p.geometry.residual
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with cache.cache_hashes(targets,excluded_roots=[args.out]):
        source=engine.load_inputs(args.endpoint)
        for file in (Path(__file__),Path(graph.__file__),Path(graph.parent.__file__),Path(graph.parent.original.__file__),
            Path(graph._batch_scalar.__code__.co_filename),Path(p.values.cert._rate_enclosure.__code__.co_filename),
            Path(signed.__file__),Path(mixed_signed.__file__),Path(normalization.__file__),
            Path(sys.modules[enclose_response_rows.__module__].__file__),Path(cache.__file__)):
            residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
        p.verify_sources(source['binding'])
        try:arrays,report=evaluate(source,args.column)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error),binding=source['binding'],FULL_BHSM_COMPLETE=False)))
            raise
        encoded={}
        for name,array in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(array)
        data=args.out/'hessian.npz';np.savez_compressed(data,**encoded);p.verify_sources(source['binding'])
        (args.out/'record.json').write_bytes(p.geometry.encoded(dict(binding=source['binding'],endpoint=args.endpoint,column=args.column,
            data_SHA256=p.values.sha(data),report=report,independent_recomputation=False,FULL_BHSM_COMPLETE=False)))
        print(json.dumps({k:v for k,v in report.items() if not isinstance(v,(dict,list))}),flush=True)


if __name__=='__main__':main()

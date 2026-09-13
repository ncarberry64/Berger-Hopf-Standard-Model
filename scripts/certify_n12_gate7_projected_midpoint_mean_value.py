"""Project paired midpoint jets before scalar normalization; evaluate no action derivatives."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse,json
from pathlib import Path
import numpy as np
from flint import arb,ctx
import diagnose_n12_gate7_directed_trial_hs_column as base
from bhsm.interface import projected_coupled_physical_normalization_second as projected
from bhsm.interface import affine_hs_midpoint_domain as grouped

p=base.p
THEORY=base.ROOT/'theory/n12_gate7_projected_midpoint_mean_value.md'
ALGORITHM='PAIRED_MIDPOINT_JETS_FIXED_OUTPUT_MEAN_VALUE_ARB512_V1'

def evaluate(args):
    local=base.reader.load_inputs(args.interval)
    _,source,_,_=base.load_stage(args.interval,'midpoint',args.primal_pair)
    record,a,files=base.read_pair(args.midpoint_pair)
    report=record.get('report',{})
    required=('uniform_midpoint_center_derivative_enclosed','same_family_segment_smoothness_established',
        'all_249_scaled_directions_verified','all_249_point_columns_contained',
        'complete_original_seven_solve_graph_used','complete_original_scalar_contractions_used')
    if (record.get('algorithm')!='UNIFORM_ACTUAL_MIDPOINT_CENTER_DIRECTION_MEAN_VALUE_ARB512_V1'
            or record.get('interval')!=args.interval or record.get('trial_column')!=args.column
            or record.get('side')!=args.side or not all(report.get(k) is True for k in required)):
        raise ValueError('paired complete same-family midpoint mixed jets required')
    for key in ('point_eigenpair_checks','point_derivative_checks'):
        checks=report.get(key,[])
        if len(checks)!=1 or not p.proof_valid(checks[0]):raise ValueError('verified original point anchor required')
    for key,value in source['binding'].items():
        if key=='files':
            if any(record['binding']['files'].get(name)!=digest for name,digest in value.items()):
                raise ValueError('saved mixed jets and original primal family differ')
        elif record['binding'].get(key)!=value:raise ValueError('saved midpoint geometry differs: '+key)
    p.geometry.residual.merge(source['binding']['files'],record['binding']['files'])
    p.geometry.residual.merge(source['binding']['files'],local['binding']['files'])
    base.bind(source,*files,Path(__file__),THEORY,Path(projected.__file__),Path(grouped.__file__),Path(base.__file__))
    P=base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    def product(values):return base.array(P*base.matrix(values))
    solved=[a[f'uniform_solve_{i}'] for i in range(7)]
    if [v.shape for v in solved]!=[(62,1)]*3+[(62,249)]*4:
        raise ValueError('all complete original saved solves required')
    axis=a['weighted_input_axis'];directions=a['weighted_tube_directions']
    if axis.shape!=(99,) or directions.shape!=(99,249) or any(not v.rad().is_zero() for v in axis):
        raise ValueError('exact original center axis and complete midpoint directions required')
    _,weights,_,_,_=p.values.operands()
    w=np.array([arb(float(v)) for v in weights],dtype=object)
    qw,rw,_,_=p.values.cert.metric_data()
    q=np.array([arb(float(v)) for v in qw],dtype=object)
    reduced=np.array([arb(float(v)) for v in rw],dtype=object)
    raw_axis=axis.copy();raw_axis[:98]/=w
    raw_v=directions[:98]/w[:,None]
    def jet(line,response,configuration,descriptor,scalars):
        return dict(configuration=configuration,psi=solved[line][:61],hard=solved[response][:61],
            border=solved[response][-1],descriptor=descriptor,cpsi=scalars[:,0],remainder=scalars[:,1])
    u=jet(1,2,(q*raw_axis[37:74])[:,None],axis[98:99],a['descriptor_first_axis'][None,:])
    v=jet(3,4,q[:,None]*raw_v[37:74],directions[98],a['descriptor_first_transverse'])
    uv=jet(5,6,np.full((37,249),arb(0),dtype=object),np.full(249,arb(0),dtype=object),a['descriptor_mixed'])
    hessian,proof=projected.normalized_mixed(q*source['paired']['full'][37:74],reduced,
        source['paired']['eigenbox'][:61],solved[0][:61,0],solved[0][-1,0],source['raw_domain'][98],
        *a['descriptor_base'],u,v,uv,base.array(P),coupled_identities_and_variations=True)
    direct=product(a['normalized_hessian'])
    selected_hessian=direct.copy()
    count=base.select_first_variation(selected_hessian.reshape(-1),hessian.reshape(-1))
    point=product(a['point_hessian'])
    if not all(x.contains(y) for x,y in zip(selected_hessian.flat,point.flat,strict=True)):
        raise ArithmeticError('projected uniform jets must contain every original point column')
    unit=[dict(g,radius=arb(1)) for g in source['groups']]
    support=grouped.group_row_bounds(selected_hessian,unit)
    anchor=product(a['point_derivative'])
    candidate=anchor+np.array([arb(0,x) for x in support],dtype=object)[:,None]
    previous=product(a['uniform_center_derivative']);selected=previous.copy()
    changed=base.select_first_variation(selected[:,0],candidate[:,0])
    arrays=dict(projected_center_derivative=selected,previous_projected_center_derivative=previous,
        mean_value_candidate=candidate,projected_point_derivative=anchor,projected_point_hessian=point,
        early_projected_hessian=hessian,direct_projected_hessian=direct,selected_projected_hessian=selected_hessian,
        projected_mean_value_support=support,weighted_input_axis=axis,fixed_output_projection=base.array(P))
    report=dict(normalization=proof,paired_complete_midpoint_jets_reused=True,new_action_derivative_evaluations=0,
        same_family_segment_smoothness_inherited=True,uniform_projected_center_derivative_enclosed=True,
        all_249_projected_point_columns_contained=True,projected_hessian_coordinates_tightened=count,
        coordinates_tightened=changed,previous_maximum_radius=float(max(v.rad() for v in previous.flat)),
        selected_maximum_radius=float(max(v.rad() for v in selected.flat)),
        maximum_mean_value_support=float(max(support)),
        full_trial_basis_enclosed=False,physical_quotient_identified=False,full_path_contraction=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    p.verify_sources(source['binding'])
    return source,arrays,report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--interval',type=int,default=13)
    parser.add_argument('--column',type=int,default=14)
    parser.add_argument('--side',choices=('left','right'),required=True)
    for name in ('primal-pair','midpoint-pair','out'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if not 0<args.interval<370 or not 0<=args.column<74:raise ValueError('interior interval and valid trial required')
    for name in ('primal_pair','midpoint_pair','out'):setattr(args,name,getattr(args,name).resolve())
    args.out.mkdir(parents=True,exist_ok=False);ctx.prec=512
    residual=p.geometry.residual
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with base.cache.cache_hashes(targets,excluded_roots=[args.out]):
        try:
            source,arrays,report=evaluate(args);encoded={}
            for name,values in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(values)
            data=args.out/'column.npz';np.savez_compressed(data,**encoded)
            record=dict(algorithm=ALGORITHM,binding=source['binding'],interval=args.interval,trial_column=args.column,
                side=args.side,data_SHA256=p.values.sha(data),report=report,FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record));print(json.dumps(report),flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error),FULL_BHSM_COMPLETE=False)))
            raise

if __name__=='__main__':main()

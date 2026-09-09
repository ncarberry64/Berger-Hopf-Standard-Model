"""Recover signed physical midpoint DF/output errors from attested HS images."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
from flint import arb,arb_mat,ctx
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_current_green_midpoint_ambient_df as ambient
import certify_n12_gate7_physical_first_causal_envelope as causal
from bhsm.interface import stored_midpoint_kinematic_error as kinematic

cert=ambient.cert;campaign=causal.coordinates.endpoint.campaign
RESULT=ROOT/'artifacts/flagship_integration/.physical_midpoint_incidence_error_work'
THEORY=ROOT/'theory/n12_gate7_physical_midpoint_incidence_errors.md'
COMMON=None


def recover_ambient(direction,image,selected):
    """Enclose D from certified images D M and an invertible square of M."""
    m=np.asarray(direction,dtype=object);y=np.asarray(image,dtype=object);indices=np.asarray(selected)
    if (m.ndim!=2 or y.ndim!=2 or min(m.shape)==0 or min(y.shape)==0 or m.shape[1]!=y.shape[1]
            or indices.shape!=(m.shape[0],) or not np.issubdtype(indices.dtype,np.integer)
            or len(set(indices.tolist()))!=m.shape[0] or np.any(indices<0) or np.any(indices>=m.shape[1])
            or not all(isinstance(x,arb) and x.is_finite() for x in (*m.flat,*y.flat))):
        raise ValueError('finite Arb image/direction matrices and distinct square selection required')
    square=cert._arb_mat_from_array(m[:,indices]);inverse=square.inv()
    residual=arb_mat(np.eye(square.nrows(),dtype=int).tolist())-square*inverse
    inverse_error=max(sum(abs(residual[i,j]) for j in range(residual.ncols())).upper() for i in range(residual.nrows()))
    if not inverse_error.is_finite() or not inverse_error<1:raise ArithmeticError('direction inverse not certified')
    derivative=cert._arb_mat_from_array(y[:,indices])*inverse
    reconstruction=derivative*cert._arb_mat_from_array(m)-cert._arb_mat_from_array(y)
    if not all(reconstruction[i,j].contains(0) for i in range(reconstruction.nrows()) for j in range(reconstruction.ncols())):
        raise ArithmeticError('physical derivative image identity does not reconcile')
    return derivative,kinematic.resolved._float_upper(inverse_error)


def output_errors(right,test,derivative,step,stored):
    """Enclose the complete physical left/right output maps minus stored maps."""
    r,t,h,p=[kinematic.resolved._real_binary64(v,n) for v,n in
             ((right,'right block'),(test,'test frame'),(step,'step'),(stored,'stored output maps'))]
    if (r.ndim!=2 or r.shape[0]==0 or r.shape[0]!=r.shape[1] or t.ndim!=2 or t.shape[0]!=r.shape[0]
            or derivative.nrows()!=t.shape[1] or derivative.ncols()!=t.shape[1] or p.shape!=(2,*t.shape)
            or h.shape!=() or float(h)<=0):raise ValueError('compatible physical incidence operands required')
    exact=kinematic.resolved._exact_matrix(r);inverse=exact.inv()
    residual=arb_mat(np.eye(r.shape[0],dtype=int).tolist())-exact*inverse
    inverse_error=max(sum(abs(residual[i,j]) for j in range(r.shape[0])).upper() for i in range(r.shape[0]))
    if not inverse_error.is_finite() or not inverse_error<1:raise ArithmeticError('frozen right inverse not certified')
    b=-inverse*kinematic.resolved._exact_matrix(t);incidence=b*derivative;h=arb(float(h));arrays={};bounds={}
    for index,sign,label in ((0,1,'left'),(1,-1,'right')):
        error=b*h/6+sign*incidence*h*h/12-kinematic.resolved._exact_matrix(p[index])
        frob=kinematic.resolved._block_error_norm(error,0,error.nrows(),error.ncols())
        scalar=sum(abs(error[i,error.ncols()-1]).upper()**2 for i in range(error.nrows())).sqrt().upper()
        arrays[label+'_output_error_mid'],arrays[label+'_output_error_radius']=kinematic._export(error)
        bounds[label]=dict(operator_error_upper=kinematic.resolved._float_upper(kinematic.resolved._operator_norm_upper(error,frob)),
            frobenius_error_upper=kinematic.resolved._float_upper(frob),scalar_column_error_upper=kinematic.resolved._float_upper(scalar))
    return arrays,bounds


def common():
    global COMMON
    if COMMON is not None:return COMMON
    record=json.loads(ambient.RESULT.read_text());parent=json.loads(ambient.PARENT.read_text())
    if (record.get('validation_passed') is not True or record.get('artifact')!='BHSM_N12_GATE7_CURRENT_GREEN_MIDPOINT_AMBIENT_DF'
            or record.get('authority')!='384_BIT_ARB_SURJECTIVE_HERMITE_SIMPSON_DIRECTION_MAP_IDENTITY'
            or campaign.cache.file_sha(ambient.DATA)!=record['data_SHA256']):
        raise RuntimeError('complete same-center physical midpoint derivative certificate required')
    sources=causal.prior.coordinate._verified_inputs(record).copy()
    causal.merge_sources(sources,causal.prior.coordinate._verified_inputs({'inputs':parent['provenance_SHA256']}))
    for kind,count,label in (('endpoint',371,'371_outward_endpoint_rate_and_DF_shards'),('midpoint',370,'370_outward_midpoint_rate_and_DF_shards')):
        paths=[ambient.DEFAULT_CACHE/f'{kind}_{i:03d}.npz' for i in range(count)]
        if cert._aggregate_sha256(paths)!=parent['derived_work_aggregate_SHA256'][label]:
            raise RuntimeError('attested physical derivative cache changed')
    with np.load(cert.ENDPOINT.with_suffix('.npz')) as source:
        times=source['collocation_arc_parameters'].copy();weights=source['state_weights'].copy();reference=source['branch_reference'].copy()
    with np.load(cert.REPLAY.with_suffix('.npz')) as source:state=source['midpoint_augmented_action_values'].copy()
    with np.load(cert.OLD_JACOBIAN.with_suffix('.npz')) as source:tangents=source['endpoint_physical_tangent_action'].copy()
    with np.load(cert.PRECONDITIONER.with_suffix('.npz')) as source:right=source['reduced_right_Newton_blocks'].copy()
    with np.load(ambient.DATA) as source:stored=source['ambient_DF_mid'].copy()
    current=campaign.center.center._load_inputs()
    if (not np.array_equal(current['midpoint'][0],state[:,:98]/weights) or not np.array_equal(current['midpoint'][1],state[:,98])
            or not np.array_equal(current['weights'],weights) or not np.array_equal(current['reference'],reference)
            or not np.array_equal(current['endpoint'][2],tangents)):
        raise RuntimeError('physical derivative and current center operands differ')
    output=json.loads(causal.prior.output.RESULT.read_text())
    causal.merge_sources(sources,causal.prior.coordinate._verified_inputs(output))
    for path in (Path(__file__),THEORY,Path(kinematic.__file__),Path(kinematic.resolved.__file__),
                 ambient.RESULT,ambient.DATA,causal.prior.output.RESULT):
        causal.merge_sources(sources,{path.relative_to(ROOT).as_posix():campaign.sha(path)})
    COMMON=dict(sources=sources,times=times,weights=weights,reference=reference,state=state,tangents=tangents,right=right,
                stored=stored,output=output)
    return COMMON


def build_point(index):
    if type(index) is not int or not 0<=index<370:raise ValueError('midpoint outside 0..369')
    loaded=common();previous=ctx.prec;ctx.prec=512
    try:
        h=float(loaded['times'][index+1]-loaded['times'][index]);blocks=[];paths=[]
        for node,sign in ((index,1),(index+1,-1)):
            path=ambient.DEFAULT_CACHE/f'endpoint_{node:03d}.npz';paths.append(path)
            with np.load(path) as source:derivative=cert._parse_arb_string_array(source['derivative_arb'])
            frame=cert._frame(loaded['tangents'][node],cert.TRIAL_DESCRIPTOR_SCALE)
            block=np.empty((99,74),dtype=object)
            for i,j in np.ndindex(block.shape):block[i,j]=arb(float(.5*frame[i,j]))+sign*arb(h)*derivative[i,j]/8
            blocks.append(block)
        path=ambient.DEFAULT_CACHE/f'midpoint_{index:03d}.npz';paths.append(path)
        with np.load(path) as source:image=cert._parse_arb_string_array(source['derivative_arb'])
        selected_path=ambient.WORK/f'midpoint_{index:03d}.npz';paths.append(selected_path)
        with np.load(selected_path) as source:selected=source['selected_direction_columns'].copy()
        derivative,inverse_error=recover_ambient(np.column_stack(blocks),image,selected)
        error=derivative-kinematic.resolved._exact_matrix(loaded['stored'][index])
        mid,radius=kinematic._export(error)
        test=cert._frame(loaded['tangents'][index+1],cert.TEST_DESCRIPTOR_SCALE).T
        b=-np.linalg.solve(loaded['right'][index],test);incidence=b@loaded['stored'][index]
        output=np.asarray([h*b/6+h*h*incidence/12,h*b/6-h*h*incidence/12])
        for slot,label in enumerate(('left','right')):
            node=index+slot
            if node==0:continue
            rows=[r for r in loaded['output']['rows'][index]['components'] if r['kind']=='endpoint' and r['index']==node]
            if len(rows)!=1 or rows[0]['output_map_SHA256']!=causal.prior.maps._array_hash(output[slot]):
                raise RuntimeError('stored endpoint output map differs')
        arrays,bounds=output_errors(loaded['right'][index],test,derivative,h,output)
        arrays.update(ambient_DF_error_mid=mid,ambient_DF_error_radius=radius,stored_ambient_DF=loaded['stored'][index],
                      stored_output_maps=output,selected_direction_columns=selected)
        sources=dict(loaded['sources'])
        for path in paths:causal.merge_sources(sources,{path.relative_to(ROOT).as_posix():campaign.sha(path)})
        payload=dict(interval=index,scope='PHYSICAL_MIDPOINT_DF_AND_FROZEN_ENDPOINT_OUTPUT_CONSTRUCTION_ERROR',
            precision_bits=512,source_SHA256=sources,output_map_error_bounds=bounds,
            direction_inverse_residual_infinity_upper=inverse_error,
            ambient_DF_error_frobenius_upper=kinematic.resolved._float_upper(kinematic.resolved._block_error_norm(error,0,99,99)),
            operand_binary64_SHA256={k:campaign.array_sha(v) for k,v in arrays.items()},
            combined_endpoint_output_bounds_replace_stored_construction_bounds=True,
            physical_midpoint_DF_incidence_error_enclosed=True,all_midpoints_covered=False,
            physical_Hessian_error_enclosed=False,physical_frame_error_enclosed=False,
            neighborhood_remainder_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
        return arrays,payload
    finally:ctx.prec=previous


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--midpoints');group.add_argument('--all-midpoints',action='store_true');args=parser.parse_args()
    indices=list(range(370)) if args.all_midpoints else campaign.parse_intervals(args.midpoints)
    RESULT.mkdir(parents=True,exist_ok=True)
    for index in indices:
        arrays,payload=build_point(index);stem=RESULT/f'midpoint_{index:03d}'
        np.savez_compressed(stem.with_suffix('.npz'),**arrays)
        payload['data_SHA256']=campaign.cache.file_sha(stem.with_suffix('.npz'))
        stem.with_suffix('.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
        if not args.all_midpoints or (index+1)%50==0 or index==369:
            print(json.dumps(dict(interval=index,ambient_DF_error=payload['ambient_DF_error_frobenius_upper'],output=payload['output_map_error_bounds'])),flush=True)
    causal.prior.coordinate._verified_inputs({'inputs':common()['sources']})


if __name__=='__main__':main()

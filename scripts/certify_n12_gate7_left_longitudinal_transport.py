"""Transport the retained left axis with a separately evaluated scalar pivot.

All 61 source-bound velocity models remain in the reconstruction. Base
equations are cancelled before the interval midpoint derivative acts, and
every weighted residual tail is retained through the common-input mapping.
This certifies only the first column of the original two-radius majorant.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain,Taylor
from bhsm.interface.input_linear_taylor import InputLinearTaylor,vector_norm
import bhsm.interface.input_linear_taylor as input_arithmetic
import bhsm.interface.shared_action_taylor as state_arithmetic
import bhsm.interface.shared_parameter_residual as support_arithmetic
import bhsm.interface.fixed_axis_input_restriction as restriction
import bhsm.interface.base_residual_cancellation as cancellation
import bhsm.interface.two_sided_input_transport as transport
import n12_gate7_left_corrected_numerator_models as reconstruction
import n12_gate7_left_longitudinal_error_bounds as error_bounds
import n12_gate7_left_input_error_maps as error_maps
import n12_gate7_base_residual_models as base_models
import n12_gate7_left_saved_family as saved
from certify_n12_gate7_endpoint_vector_transport import restore,upper,dot


def load_scalar(folder,parent,domain,axis,error_map,verified):
    record=json.loads((folder/'record.json').read_bytes())
    archive=folder/'scalar_model.json.gz'
    scaled=record.get('algorithm')=='LEFT_SCALED_LONGITUDINAL_DEFERRED_BASE_SHARED_SCALAR_PIVOT_V2'
    producer=ROOT/'scripts'/('certify_n12_gate7_left_scaled_longitudinal_scalar.py' if scaled
                            else 'certify_n12_gate7_left_longitudinal_scalar.py')
    if (record.get('algorithm') not in ('LEFT_LONGITUDINAL_DEFERRED_BASE_SHARED_SCALAR_PIVOT_V1',
            'LEFT_SCALED_LONGITUDINAL_DEFERRED_BASE_SHARED_SCALAR_PIVOT_V2')
            or record.get('side')!='left' or record['family']!=parent['family']
            or record['physical_input_columns']!=1 or record['original_physical_input_columns']!=74
            or record['fixed_input_axis_node']!=13
            or record['fixed_input_axis_exact']!=[str(v.fmpq()) for v in axis.entries()]
            or record['original_full_input_map']!=parent['input_map']
            or record['original_axis_correction_radii' if scaled else 'axis_correction_radii']!=parent['axis_correction_radii']
            or record['original_state_groups']!=parent['original_state_groups']
            or record['input_groups']!=[[0,1,'euclidean'],[1,125,'box']]
            or record['scalar_model_SHA256']!=saved.sha(archive)
            or record['source_hashes']['evaluator']!=saved.sha(producer)
            or any(record['source_hashes'].get(k)!=parent['source_hashes'].get(k)
                   for k in ('adjoint','refined_base_radii','directional_cancellation_proposal'))
            or any(record['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items())):
        raise ValueError('unchanged complete retained-axis scalar construction required')
    scales=[arb(v) for v in record['auxiliary_scales_exact']] if scaled else [arb(1)]*124
    if scaled:
        bounds=[abs(v).upper() for v in (error_map*axis).entries()]
        if (len(scales)!=124 or record.get('directional_error_inclusion_from_original_uniform_derivative') is not True
                or record['normalized_axis_error_bounds_exact']!=[str(v.fmpq()) for v in bounds]
                or any(not s.is_finite() or not s>=b or not s.rad().is_zero()
                       for s,b in zip(scales,bounds,strict=True))
                or record['axis_correction_radii']!=[str((arb(r)*s).fmpq())
                    for r,s in zip(parent['axis_correction_radii'],scales,strict=True)]):
            raise ValueError('original uniform derivative must justify every auxiliary rescaling')
    encoded=json.loads(gzip.decompress(archive.read_bytes()))
    if len(encoded)!=125*(domain.dimension+1)+1:
        raise ValueError('all fixed-axis scalar coefficients required')
    values=[restore(v) for v in encoded]
    result=InputLinearTaylor(domain,arb_mat(1,125,values[:125]),
        arb_mat(domain.dimension,125,values[125:-1]),values[-1],
        [tuple(group) for group in record['input_groups']])
    for key,value in (('support',result.support()),('linear',result.linear_bound()),('nonlinear',result.r)):
        if str(value.fmpq())!=record['scalar_row_bound'][key]['exact']:
            raise ArithmeticError('fixed-axis scalar bounds failed exact replay')
    return result,scales


def evaluate(args):
    if ctx.prec!=512:
        raise ValueError('the retained 512-bit arithmetic precision is required')
    root=args.evidence_root.resolve()
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(root/'src/bhsm/interface'))
    verified=saved.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p=base.p
    residual=p.geometry.residual
    with base.cache.cache_hashes([(p.values,'sha'),(residual.center,'_sha'),
                                 (residual.foundation.coordinate.center,'_sha')]):
        local=base.reader.load_inputs(13)
    axesfile=root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axesfile,allow_pickle=False) as z:
        axes=z['current_center_green_image_unit_mid'].copy()
    axes[1:]/=np.linalg.norm(axes[1:],axis=1)[:,None]
    axes[0]=0
    if hashlib.sha256(np.asarray(axes,dtype='<f8').tobytes()).hexdigest().upper()!=local['binding']['axes_SHA256']:
        raise ValueError('unchanged retained input and output axes required')
    axis=arb_mat(74,1,[arb(float(v)) for v in axes[13]])
    output_axis=[arb(float(v)) for v in axes[14]]
    paths={'evaluator':Path(__file__),'axis':axesfile,
        'exact_ball_restoration':Path(restore.__code__.co_filename),
        'retained_trial_column':Path(base.__file__),
        'retained_transport_reader':Path(base.reader.__file__),
        'retained_action_reader':Path(p.__file__),
        'retained_action_values':Path(p.values.__file__),
        'retained_action_certificate':Path(p.values.cert.__file__),
        'scalar_producer':ROOT/'scripts/certify_n12_gate7_left_longitudinal_scalar.py',
        'scaled_scalar_producer':ROOT/'scripts/certify_n12_gate7_left_scaled_longitudinal_scalar.py'}
    for module in (restriction,cancellation,transport,reconstruction,error_bounds,error_maps,base_models,saved,
                   input_arithmetic,state_arithmetic,support_arithmetic):
        paths[module.__name__]=Path(module.__file__)
    families={}
    for family in ('midpoint','endpoint'):
        parent_path=getattr(args,family)
        velocity=getattr(args,family+'_corrected')
        adjoint=getattr(args,family+'_adjoint')
        refined=getattr(args,family+'_refined')
        scalar=getattr(args,family+'_scalar')
        base_folder=getattr(args,family+'_base_residual')
        errors=getattr(args,family+'_error_refinement')
        for key,path in dict(parent=parent_path/'record.json',velocity=velocity/'record.json',
            manifest=velocity.with_suffix('.terms')/'sources.json',adjoint=adjoint,refined=refined,
            scalar_record=scalar/'record.json',scalar_model=scalar/'scalar_model.json.gz',
            base_record=base_folder/'record.json',base_model=base_folder/'models.json.gz',errors=errors).items():
            paths[family+'_'+key]=path
        for i in range(61): paths[f'{family}_velocity_{i:02d}']=velocity/f'component_{i:02d}.json.gz'
        for name in ('scalar_model.json.gz','models.json.gz','scalar_model_receipt.json'):
            if (parent_path/name).exists(): paths[family+'_parent_'+name]=parent_path/name
        record,domain,_,numerators,U,directions=reconstruction.reconstruct(
            root,family,parent_path,velocity,adjoint,refined,verified)
        error_map=error_maps.load_error_map(root,record,adjoint)
        W,scales=load_scalar(scalar,record,domain,axis,error_map,verified)
        numerators=[restriction.restrict_physical_axis(value,axis,auxiliary_scales=scales) for value in numerators]
        eta=error_bounds.load_direction(errors,parent_path,adjoint,refined,axis,error_map,verified)
        eta=arb_mat(124,1,[arb(0) if scale.is_zero() else (value/scale).intersection(arb(0,1))
            for value,scale in zip(eta.entries(),scales,strict=True)])
        families[family]=(record,domain,W,numerators,U*axis,directions,eta)
    hashes={k:saved.sha(path) for k,path in paths.items()}
    mid,mdomain,midW,midN,midU,mdirections,mideta=families['midpoint']
    end,edomain,endW,endN,endU,edirections,endeta=families['endpoint']
    P=base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    Q=arb_mat(74,74,[arb(i==j)-output_axis[i]*output_axis[j] for i in range(74) for j in range(74)])
    QP=Q*P
    h=arb(float(local['step']))
    L=QP*(2*h/3)
    if L[73,98].contains(0): raise ValueError('nonzero descriptor pivot required')
    E=base.matrix(local['trial_left'])*axis
    M=arb_mat(99,99,list(local['midpoint_df'].flat))
    endpoint_df=root/'artifacts/flagship_integration/.primal_mean_value_component_centered_endpoint_uniform_df_work/endpoint_013/derivative.npz'
    endpoint_adjoint=json.loads(args.endpoint_adjoint.read_bytes())
    if endpoint_adjoint['source_hashes'].get(endpoint_df.relative_to(root).as_posix())!=saved.sha(endpoint_df):
        raise ValueError('same left endpoint derivative source required')
    with np.load(endpoint_df,allow_pickle=False) as z:
        A0=(saved.read_matrix(z,'point_derivative')*E).mid()
        input_roundoff=saved.read_matrix(z,'derivative')*(E-endU)
    paths['endpoint_derivative']=endpoint_df
    hashes['endpoint_derivative']=saved.sha(endpoint_df)
    endblock=base_models.load_block(args.endpoint_base_residual,args.endpoint,args.endpoint_refined,
        edomain,list(range(edomain.dimension)),verified)
    endW,Wweights=endblock.cancel(endW)
    cancelled=[]
    weights=[]
    for model in endN:
        value,weight=endblock.cancel(model)
        cancelled.append(value)
        weights.append(weight)
    weight_matrix=arb_mat(98,124*125,[v for weight in weights for v in weight.entries()])
    del weights
    def constant(value):
        result=InputLinearTaylor(edomain,arb_mat(1,125,[value]+[arb(0)]*124),
            arb_mat(edomain.dimension,125),input_groups=[(0,1,'euclidean'),(1,125,'box')])
        result._linear=arb(0)
        return result
    difference=[value-constant(A0[i,0]) for i,value in enumerate(cancelled)]
    scalar_difference=endW-constant((L*A0)[73,0])
    common=TaylorDomain(mid['original_state_groups']+[[373,497,'box']],497)
    inputs=[(0,1,'euclidean'),(1,249,'box')]
    endpoint_state=[0]+list(range(2,76))+list(range(373,497))
    midpoint_state=list(range(373))
    if any(not (2*mdirections[i,k]-edirections[i,j]).contains(0)
           for i in range(99) for j,k in enumerate(endpoint_state[:75])):
        raise ValueError('identical retained endpoint state coordinates required')
    midpoint_inputs=list(range(125))
    endpoint_inputs=[0]+list(range(125,249))
    midblock=base_models.load_block(args.midpoint_base_residual,args.midpoint,args.midpoint_refined,
        common,midpoint_state,verified)
    direction=arb_mat(249,1,[arb(1)]+mideta.entries()+endeta.entries())
    def embed(value,states,columns):
        c=arb_mat(1,249)
        a=arb_mat(497,249)
        for j,k in enumerate(columns): c[0,k]=value.c[0,j]
        for i,k in enumerate(states):
            for j,l in enumerate(columns): a[k,l]=value.a[i,j]
        return InputLinearTaylor(common,c,a,value.r,inputs)
    def complete_row(qp,q):
        fixed,coefficient=transport.transport_coefficients(qp,q*axis,E,M,h,A0,midU,
            side='left',frozen_left=base.matrix(local['frozen_left']))
        ratio=coefficient[0,98]/L[73,98]
        complement=[coefficient[0,j]-ratio*L[73,j] for j in range(98)]
        endpoint=ratio*scalar_difference+dot(complement,difference)
        endpoint+=constant((coefficient*input_roundoff)[0,0])
        endpoint_weights=ratio*Wweights+arb_mat(124,125,
            (arb_mat(1,98,complement)*weight_matrix).entries())
        projected=qp*(2*h/3)
        midratio=projected[0,98]/L[73,98]
        midpoint=midratio*midW+dot([projected[0,j]-midratio*L[73,j] for j in range(98)],midN)
        value=embed(midpoint,midpoint_state,midpoint_inputs)+embed(endpoint,endpoint_state,endpoint_inputs)
        value+=InputLinearTaylor(common,arb_mat(1,249,[fixed[0,0]]+[arb(0)]*248),arb_mat(497,249),input_groups=inputs)
        value,midweights=midblock.cancel(value)
        endweights=arb_mat(124,249)
        for j,k in enumerate(endpoint_inputs):
            for i in range(124): endweights[i,k]=endpoint_weights[i,j]
        allweights=arb_mat(248,249,midweights.entries()+endweights.entries())
        tail=cancellation.weighted_tail_at_input(allweights,direction)
        result=value.at_input(direction)
        return Taylor(common,result.c,result.a,result.r+tail),tail
    models=[]
    rows=[]
    for i in range(74):
        value,tail=complete_row(arb_mat(1,99,[QP[i,j] for j in range(99)]),
            arb_mat(1,74,[Q[i,j] for j in range(74)]))
        models.append(value)
        rows.append(dict(component=i,support=upper(value.support()),linear=upper(value.linear_bound()),
            nonlinear=upper(value.r),base_residual_tail=upper(tail)))
        print(json.dumps(dict(row=i,axis_support=float(value.support()))),flush=True)
    longQ=arb_mat(1,74,output_axis)
    longitudinal,longtail=complete_row(longQ*P,longQ)
    transverse=min(vector_norm([value.support() for value in models]),
        (vector_norm([value.c for value in models])+vector_norm([value.linear_bound() for value in models])
         +vector_norm([value.r for value in models])).upper())
    encoded=[[[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in [value.c,*value.a.entries(),value.r]]
             for value in models+[longitudinal]]
    archive=gzip.compress(saved.encoded(encoded),mtime=0)
    if hashes!={k:saved.sha(path) for k,path in paths.items()}:
        raise ValueError('proof input changed during longitudinal transport')
    if any(saved.sha(root/key)!=digest for key,digest in verified['paired_source_hashes'].items()):
        raise ValueError('retained physical evidence changed during longitudinal transport')
    result=dict(algorithm='LEFT_RETAINED_AXIS_SHARED_PRETRANSPORT_BOUND_V1',side='left',
        input_axis_node=13,output_axis_node=14,input_axis_exact=[str(v.fmpq()) for v in axis.entries()],
        fixed_physical_input_dimension=1,original_physical_input_dimension=74,
        arithmetic_precision_bits=512,
        original_state_groups=[list(v) for v in common.groups],state_dimension=497,
        endpoint_state_embedding=endpoint_state,rows=rows,
        transverse_output_on_longitudinal_input=upper(transverse),
        longitudinal_output_on_longitudinal_input=upper(longitudinal.support()),
        longitudinal_row=dict(support=upper(longitudinal.support()),linear=upper(longitudinal.linear_bound()),
            nonlinear=upper(longitudinal.r),base_residual_tail=upper(longtail)),
        all_61_velocity_components_retained=True,all_248_base_equations_retained=True,
        endpoint_base_cancelled_before_interval_midpoint_transport=True,
        every_weighted_base_remainder_retained=True,original_physical_domain_unchanged=True,
        all_input_operator_certified_by_this_record=False,
        models_SHA256=hashlib.sha256(archive).hexdigest().upper(),guarded_input_SHA256=hashes,
        source_hashes=verified['paired_source_hashes'],Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    args.out.mkdir(parents=True,exist_ok=False)
    (args.out/'models.json.gz').write_bytes(archive)
    (args.out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(longitudinal=float(longitudinal.support()),transverse=float(transverse))),flush=True)


def main():
    parser=argparse.ArgumentParser()
    for name in ('evidence-root','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    for family in ('midpoint','endpoint'):
        for suffix in ('','-corrected','-adjoint','-refined','-scalar','-base-residual','-error-refinement'):
            parser.add_argument('--'+family+suffix,type=Path,required=True)
    args=parser.parse_args()
    ctx.prec=512
    evaluate(args)


if __name__=='__main__':
    main()

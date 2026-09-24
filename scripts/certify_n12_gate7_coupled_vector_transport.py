"""Assemble the right 74-input HS block from shared endpoint/midpoint models.

The endpoint rate is reconstructed without evaluating the action again. The
constant transport cancellation is formed before the uniform midpoint DF is
applied. Endpoint and midpoint solve corrections remain distinct, while the
74-dimensional physical input and right endpoint state coordinates are shared.
This one local block does not certify the full history or close Gate 7.
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
from contextlib import ExitStack
import numpy as np
from flint import arb,arb_mat,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor,vector_norm
import bhsm.interface.common_input_error_pullback as error_pullback
import bhsm.interface.common_input_error_full_pullback as full_error_pullback
import bhsm.interface.joint_output_support as joint_support
import n12_gate7_common_input_error_maps as error_maps
import bhsm.interface.input_linear_taylor as arithmetic
import evaluate_n12_gate7_coupled_residual_saved as saved
from certify_n12_gate7_endpoint_vector_transport import restore,upper,dot


def transport_coefficients(QP,Q,E,M,h,A0,U):
    """Exact regrouping that retains the small signed anchor transport tail."""
    PM=QP*M*(2*h/3)
    coefficient=QP*(h/6)-PM*(h/8)
    fixed=Q-QP*E+QP*A0*(h/6)+PM*(E/2-A0*(h/8)-U)
    return fixed,coefficient


def eliminate_descriptor(row,pivot_row):
    if pivot_row[-1].contains(0): raise ArithmeticError('nonzero descriptor pivot required')
    ratio=row[-1]/pivot_row[-1]
    return ratio,[a-ratio*b for a,b in zip(row[:-1],pivot_row[:-1],strict=True)]


def json_array_rows(stream,chunk_size=16*1024*1024):
    """Read large coefficient rows without holding the full archive in RAM."""
    decoder=json.JSONDecoder()
    buffer='';eof=False
    def fill():
        nonlocal buffer,eof
        more=stream.read(chunk_size)
        if not more: eof=True
        buffer+=more
    fill()
    buffer=buffer.lstrip()
    if not buffer.startswith('['): raise ValueError('coefficient row array required')
    buffer=buffer[1:];first=True
    while True:
        buffer=buffer.lstrip()
        while not buffer and not eof:
            fill();buffer=buffer.lstrip()
        if buffer.startswith(']'):
            buffer=buffer[1:]
            while not eof: fill()
            if buffer.strip(): raise ValueError('trailing coefficient archive data')
            return
        if not first:
            if not buffer.startswith(','): raise ValueError('coefficient row separator required')
            buffer=buffer[1:].lstrip()
        while True:
            try:
                row,end=decoder.raw_decode(buffer)
                break
            except json.JSONDecodeError:
                if eof: raise
                fill();buffer=buffer.lstrip()
        if not isinstance(row,list): raise ValueError('coefficient row list required')
        buffer=buffer[end:]
        yield row
        first=False


def read_models(path,family,verified):
    record=json.loads((path/'record.json').read_bytes())
    if (record['family']!=family or record['physical_input_columns']!=74
            or record['projected_output_rows']!=74
            or any(record['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items())):
        raise ValueError('matching complete original-domain input/output family required')
    archive=path/'models.json.gz'
    digest=hashlib.sha256()
    with archive.open('rb') as data:
        for block in iter(lambda:data.read(1024*1024),b''): digest.update(block)
    if digest.hexdigest().upper()!=record['models_SHA256']:
        raise ValueError('exact coefficient archive fingerprint mismatch')
    domain=TaylorDomain(record['original_state_groups'],373 if family=='midpoint' else 199)
    def decode(row):
        if len(row)!=198+domain.dimension*198+1:
            raise ValueError('complete common state/input coefficients required')
        v=[restore(pair) for pair in row]
        return InputLinearTaylor(domain,arb_mat(1,198,v[:198]),
            arb_mat(domain.dimension,198,v[198:-1]),v[-1],record['input_groups'])
    def encoded_rows():
        count=0
        with gzip.open(archive,'rt',encoding='utf-8') as stream:
            for row in json_array_rows(stream):
                if count>=74: raise ValueError('exactly 74 projected output rows required')
                count+=1
                yield row
        if count!=74: raise ValueError('all projected output rows required')
    return record,domain,encoded_rows(),decode


def evaluate(root,midpoint_path,endpoint_path,adjoint_path,refined_path,out,midpoint_adjoint_path,midpoint_refined_path,midpoint_corrected,endpoint_corrected,export_models=False,pullback_state_errors=False):
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(root/'src/bhsm/interface'))
    verified=saved.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p,cert=base.p,base.p.values.cert
    import n12_gate7_corrected_numerator_models as corrected_models
    guarded_paths={
        'evaluator':Path(__file__),'arithmetic':Path(arithmetic.__file__),
        'reconstruction':Path(corrected_models.__file__),'source_verifier':Path(saved.__file__),
        'input_error_maps':Path(error_maps.__file__),'input_error_pullback':Path(error_pullback.__file__),
        'joint_support':Path(joint_support.__file__),
        'state_arithmetic':Path(sys.modules[TaylorDomain.__module__].__file__),
        'exact_ball_restoration':Path(restore.__code__.co_filename),
        'midpoint_adjoint':midpoint_adjoint_path,'endpoint_adjoint':adjoint_path,
        'midpoint_base_radii':midpoint_refined_path,'endpoint_base_radii':refined_path}
    if pullback_state_errors: guarded_paths['full_error_pullback']=Path(full_error_pullback.__file__)
    radii_path=root/'artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE.json'
    guarded_paths['original_trial_radii']=radii_path
    for name,folder,parent in (('midpoint',midpoint_corrected,midpoint_path),
                               ('endpoint',endpoint_corrected,endpoint_path)):
        guarded_paths[name+'_corrected_record']=folder/'record.json'
        guarded_paths[name+'_corrected_manifest']=folder.with_suffix('.terms')/'sources.json'
        guarded_paths[name+'_parent_record']=parent/'record.json'
        for i in range(61): guarded_paths[f'{name}_corrected_model_{i:02d}']=folder/f'component_{i:02d}.json.gz'
        for filename in ('scalar_model_receipt.json','scalar_model.json.gz','models.json.gz'):
            if (parent/filename).exists(): guarded_paths[name+'_'+filename]=parent/filename
    input_hashes_before={key:saved.sha(path) for key,path in guarded_paths.items()}
    for folder in (midpoint_corrected,endpoint_corrected):
        corrected_record=json.loads((folder/'record.json').read_bytes())
        manifest=json.loads((folder.with_suffix('.terms')/'sources.json').read_bytes())
        if manifest!=corrected_record['source_hashes']:
            raise ValueError('corrected record and immutable source manifest must agree')
        if corrected_record.get('algorithm') not in (
                'FULL_INPUT_DIRECTIONAL_NUMERATOR_SHARED_RESIDUAL_V1','FULL_INPUT_NUMERATOR_SHARED_RESIDUAL_V1'):
            raise ValueError('complete residual-cancelled velocities required; a raw/hybrid snapshot is insufficient')
    mid,mdomain,midW,midnumerator,U_mid,mdirections=corrected_models.reconstruct(
        root,'midpoint',midpoint_path,midpoint_corrected,midpoint_adjoint_path,midpoint_refined_path,verified)
    end,domain,W,numerator,U,directions=corrected_models.reconstruct(
        root,'endpoint',endpoint_path,endpoint_corrected,adjoint_path,refined_path,verified)
    adjoint=json.loads(adjoint_path.read_bytes())
    midpoint_error_map=error_maps.load_error_map(root,mid,midpoint_adjoint_path)
    endpoint_error_map=error_maps.load_error_map(root,end,adjoint_path)
    def constant_input(c):
        result=InputLinearTaylor(domain,arb_mat(1,198,c),arb_mat(domain.dimension,198),input_groups=end['input_groups'])
        result._linear=arb(0)
        return result
    residual=p.geometry.residual
    with base.cache.cache_hashes([(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]):
        local=base.reader.load_inputs(13)
    P=base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    axesfile=root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axesfile,allow_pickle=False) as z: axes=z['current_center_green_image_unit_mid'].copy()
    axes[1:]/=np.linalg.norm(axes[1:],axis=1)[:,None];axes[0]=0
    if hashlib.sha256(np.asarray(axes,dtype='<f8').tobytes()).hexdigest().upper()!=local['binding']['axes_SHA256']:
        raise ValueError('unchanged physical projection required')
    axis=[arb(float(v)) for v in axes[14]]
    Q=arb_mat(74,74,[arb(i==j)-axis[i]*axis[j] for i in range(74) for j in range(74)])
    h=arb(float(local['step']));QP=Q*P;L=QP*(2*h/3)
    if local['binding']['files'].get(radii_path.relative_to(root).as_posix())!=p.values.sha(radii_path):
        raise ValueError('the original physical domain must bind the unchanged trial radii')
    radii=[arb(float(v)) for v in json.loads(radii_path.read_bytes())['stored_polynomial_adjudication']['witness']['radius']]
    if len(radii)!=2 or any(not v>0 for v in radii): raise ValueError('two positive original trial radii required')
    if L[73,98].contains(0): raise ArithmeticError('nonzero descriptor pivot required')
    E=base.matrix(local['trial_right'])
    M=arb_mat(99,99,list(local['midpoint_df'].flat))
    fullfile=root/'artifacts/flagship_integration/.primal_mean_value_component_centered_endpoint_uniform_df_work/endpoint_014/derivative.npz'
    if adjoint['source_hashes'].get(fullfile.relative_to(root).as_posix())!=saved.sha(fullfile):
        raise ValueError('same endpoint anchor source required')
    with np.load(fullfile,allow_pickle=False) as z:
        A0=(saved.read_matrix(z,'point_derivative')*E).mid()
        input_roundoff=saved.read_matrix(z,'derivative')*(E-U)
    # The proposed input map consists of exact midpoint coefficients. Keep
    # its difference from the original interval trial basis explicitly.
    U_mid=arb_mat([[arb(v) for v in row] for row in mid['input_map']])
    difference=[v-constant_input([A0[i,j] for j in range(74)]+[arb(0)]*124) for i,v in enumerate(numerator)]
    projected_anchor=L*A0
    scalar_difference=W-constant_input([projected_anchor[73,j] for j in range(74)]+[arb(0)]*124)
    fixed,coefficient=transport_coefficients(QP,Q,E,M,h,A0,U_mid)
    mapped_input_roundoff=coefficient*input_roundoff
    groups=mid['original_state_groups']+[[373,497,'box']]
    common=TaylorDomain(groups,497)
    input_groups=[(0,74,'euclidean'),(74,322,'box')]
    endpoint_state=[1]+list(range(76,150))+list(range(373,497))
    endpoint_input=list(range(74))+list(range(198,322))
    midpoint_state=list(range(373));midpoint_input=list(range(198))
    parameter_differences=[2*mdirections[i,k]-directions[i,j]
                          for i in range(99) for j,k in enumerate(endpoint_state[:75])]
    if any(not v.contains(0) for v in parameter_differences):
        raise ValueError('inherited right-endpoint coefficient enclosures must agree')
    # Source-bound endpoint and midpoint domains use the same right state
    # parameters. Their Arb coefficient radii remain in each model; this
    # check neither identifies rounded coefficient balls nor zeroes a radius.
    def embed(value,states,inputs):
        c=arb_mat(1,322);a=arb_mat(497,322)
        for j,k in enumerate(inputs): c[0,k]=value.c[0,j]
        for i,k in enumerate(states):
            for j,l in enumerate(inputs): a[k,l]=value.a[i,j]
        return InputLinearTaylor(common,c,a,value.r,input_groups)
    rows=[];bounds=[];linear_bounds=[];remainder_bounds=[];longitudinal_bounds=[]
    # For the retained two-radius norm, also restrict the physical input
    # to its stored longitudinal axis. The error coordinates are enclosed
    # by their original common-input maps, including their state dependence.
    # These interval coefficients are a pointwise enclosure, not derivatives.
    longitudinal_axis=arb_mat(74,1,axis)
    longitudinal_direction=arb_mat(322,1,axis
        +(midpoint_error_map*longitudinal_axis).entries()
        +(endpoint_error_map*longitudinal_axis).entries())
    midpoint_anchor=error_maps.load_projected_anchor(root,mid)
    endpoint_anchor=error_maps.load_projected_anchor(root,end)
    family_rows={'midpoint':[],'endpoint':[]}
    family_deviations={'midpoint':[],'endpoint':[]}
    def family_bound(name,model,anchor,row):
        c=arb_mat(1,198,[anchor[row,j] for j in range(74)]+[arb(0)]*124)
        deviation=InputLinearTaylor(model.domain,model.c-c,model.a,model.r,model.input_groups).support()
        family_deviations[name].append(deviation)
        family_rows[name].append(dict(component=row,support=upper(model.support()),
            anchor_deviation=upper(deviation),linear=upper(model.linear_bound()),nonlinear=upper(model.r)))
    original_constants=arb_mat(74,322);pulled_constants=arb_mat(74,322)
    out.mkdir(parents=True,exist_ok=False)
    archive=out/'models.jsonl.gz'
    with ExitStack() as stack:
        output=None
        if export_models:
            rawfile=stack.enter_context(archive.open('xb'))
            output=stack.enter_context(gzip.GzipFile(fileobj=rawfile,mode='wb',filename='',mtime=0))
        for i in range(74):
            ratio,complement=eliminate_descriptor([coefficient[i,j] for j in range(99)],
                                                 [L[73,j] for j in range(99)])
            # Eliminate the descriptor before combining remainder bounds:
            # otherwise reconstructing A[98] and multiplying it again would
            # charge the same numerator remainders twice and lose cancellation.
            endpoint_part=ratio*scalar_difference+dot(complement,difference)
            endpoint_part+=constant_input([mapped_input_roundoff[i,j] for j in range(74)]+[arb(0)]*124)
            midratio=arb(1) if i==73 else L[i,98]/L[73,98]
            midpoint_model=midW if i==73 else midratio*midW+dot(
                [L[i,j]-midratio*L[73,j] for j in range(98)],midnumerator)
            endpoint_model=W if i==73 else midratio*W+dot(
                [L[i,j]-midratio*L[73,j] for j in range(98)],numerator)
            family_bound('midpoint',midpoint_model,midpoint_anchor,i)
            family_bound('endpoint',endpoint_model,endpoint_anchor,i)
            value=embed(midpoint_model,midpoint_state,midpoint_input)+embed(endpoint_part,endpoint_state,endpoint_input)
            c=[fixed[i,j] for j in range(74)]+[arb(0)]*248
            fixed_model=InputLinearTaylor(common,arb_mat(1,322,c),arb_mat(497,322),input_groups=input_groups)
            fixed_model._linear=arb(0)
            value=value+fixed_model
            original_support=value.support()
            longitudinal=value.at_input(longitudinal_direction)
            longitudinal_bounds.append(longitudinal.support())
            for j in range(322): original_constants[i,j]=value.c[0,j]
            original_value=value
            value=error_pullback.pullback_constant_errors(value,[(74,midpoint_error_map),(198,endpoint_error_map)])
            state_errors_pulled_back=False
            if pullback_state_errors:
                candidate=full_error_pullback.pullback_all_errors(original_value,
                    [(74,midpoint_error_map),(198,endpoint_error_map)])
                # Both choices have the identical pulled-back constant row.
                # Choose the smaller complete state-linear plus remainder
                # bound, retaining the corresponding remainder scaling.
                if candidate.linear_bound()+candidate.r < value.linear_bound()+value.r:
                    value=candidate;state_errors_pulled_back=True
            for j in range(322): pulled_constants[i,j]=value.c[0,j]
            support=value.support();bounds.append(support)
            linear_bounds.append(value.linear_bound());remainder_bounds.append(value.r)
            rows.append(dict(component=i,support=upper(support),linear=upper(value.linear_bound()),nonlinear=upper(value.r),
                             longitudinal_input_support=upper(longitudinal.support()),
                             state_errors_pulled_back=state_errors_pulled_back,
                             independently_boxed_error_support=upper(original_support)))
            if output is not None:
                encoded=[[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in value.c.entries()+value.a.entries()+[value.r]]
                output.write(json.dumps(encoded,separators=(',',':')).encode()+b'\n')
            print(json.dumps(dict(row=i,support=float(support))),flush=True)
    # The same retained fixed-axis decomposition also requires longitudinal
    # output. Reuse the descriptor pivot and all signed numerator models;
    # no extra action evaluation or physical projection choice is introduced.
    longQ=arb_mat(1,74,axis);longQP=longQ*P;longL=longQP*(2*h/3)
    long_fixed,long_coefficient=transport_coefficients(longQP,longQ,E,M,h,A0,U_mid)
    ratio,complement=eliminate_descriptor(long_coefficient.entries(),[L[73,j] for j in range(99)])
    long_endpoint=ratio*scalar_difference+dot(complement,difference)
    roundoff=long_coefficient*input_roundoff
    long_endpoint+=constant_input(roundoff.entries()+[arb(0)]*124)
    ratio=longL[0,98]/L[73,98]
    long_midpoint=ratio*midW+dot([longL[0,j]-ratio*L[73,j] for j in range(98)],midnumerator)
    long_value=embed(long_midpoint,midpoint_state,midpoint_input)+embed(long_endpoint,endpoint_state,endpoint_input)
    long_value+=InputLinearTaylor(common,arb_mat(1,322,long_fixed.entries()+[arb(0)]*248),
                                 arb_mat(497,322),input_groups=input_groups)
    long_original=long_value
    long_on_axis=long_value.at_input(longitudinal_direction).support()
    long_value=error_pullback.pullback_constant_errors(long_value,[(74,midpoint_error_map),(198,endpoint_error_map)])
    long_state_errors_pulled=False
    if pullback_state_errors:
        candidate=full_error_pullback.pullback_all_errors(long_original,[(74,midpoint_error_map),(198,endpoint_error_map)])
        if candidate.linear_bound()+candidate.r < long_value.linear_bound()+long_value.r:
            long_value=candidate;long_state_errors_pulled=True
    linear_norm=vector_norm(linear_bounds);remainder_norm=vector_norm(remainder_bounds)
    old_joint=joint_support.joint_constant_support(original_constants,input_groups)
    pulled_joint=joint_support.joint_constant_support(pulled_constants,input_groups)
    total=min(vector_norm(bounds),(min(old_joint,pulled_joint)+linear_norm+remainder_norm).upper())
    two_radius=[[long_on_axis,long_value.support()],[vector_norm(longitudinal_bounds),total]]
    weighted_rows=[(sum((two_radius[i][j]*radii[j] for j in range(2)),arb(0))/radii[i]).upper() for i in range(2)]
    constants_bytes=gzip.compress(saved.encoded({name:[[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in matrix.entries()]
        for name,matrix in (('original',original_constants),('pulled',pulled_constants),
                            ('longitudinal_original',long_original.c),('longitudinal_pulled',long_value.c))}),mtime=0)
    (out/'constants.json.gz').write_bytes(constants_bytes)
    if any(saved.sha(path)!=input_hashes_before[key] for key,path in guarded_paths.items()):
        raise ValueError('proof inputs or arithmetic changed during the calculation; partial output preserved')
    if any(saved.sha(root/key)!=digest for key,digest in verified['paired_source_hashes'].items()):
        raise ValueError('original paired physical evidence changed during transport')
    with base.cache.cache_hashes([(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]):
        for key in verified['paired_source_hashes']:
            if key.endswith('/first/record.json'):
                p.verify_sources(json.loads((root/key).read_bytes())['binding'])
    result=dict(algorithm='FULL_INPUT_COUPLED_NUMERATOR_HS_TRANSPORT_V1',physical_input_columns=74,projected_output_rows=74,
        proof_assumptions=[
            'The inherited source-bound endpoint and midpoint implicit solutions satisfy the retained eigenline, response, and directional equations.',
            'The original physical domains and inherited implicit correction inclusions contain those same solutions; no physical domain radius is reduced.',
            'All physical input directions use one common 74-dimensional Euclidean ball; auxiliary directional errors remain shared until residual cancellation.',
            'The source-bound frozen physical projection and Hermite-Simpson transport identity are unchanged.'
        ],
        physical_output_norm='Euclidean norm after the unchanged physical weighted projection',
        original_state_groups=groups,input_groups=input_groups,endpoint_state_embedding=endpoint_state,
        midpoint_state_embedding=midpoint_state,endpoint_input_embedding=endpoint_input,midpoint_input_embedding=midpoint_input,
        identity='Q-QPE+(h/6)QPA0+Bmid+PM(E/2-hA0/8-U_mid)+[(h/6)QP-(h/8)PM](A-A0)',
        fixed_anchor_transport_before_norm=True,midpoint_derivative_coefficient_dependence_relaxed=True,
        endpoint_descriptor_eliminated_before_remainder_bound=True,
        all_61_velocity_residuals_cancelled_before_normalization_and_transport=True,
        corrected_fixed_family_vectors={name:dict(rows=family_rows[name],
            anchor_deviation_operator_norm_upper=upper(vector_norm(family_deviations[name])))
            for name in ('midpoint','endpoint')},
        common_physical_input_retained_in_constant_error_terms=True,
        all_output_rows_combined_before_constant_error_norm=True,
        joint_original_constant_support=upper(old_joint),joint_pulled_constant_support=upper(pulled_joint),
        linear_vector_bound=upper(linear_norm),nonlinear_vector_bound=upper(remainder_norm),
        pointwise_interval_affine_enclosure=True,constant_coefficients_must_not_be_differentiated=True,
        pulled_state_coefficients_must_not_be_differentiated=pullback_state_errors,
        endpoint_input_roundoff_operator_bound=upper(vector_norm(input_roundoff.entries())),
        endpoint_parameter_coefficient_difference=upper(max(abs(v).upper() for v in parameter_differences)),
        all_source_coefficient_radii_retained=True,
        complete_local_right_block_norm_upper=upper(total),strict_local_gain_below_one=bool(total<1),rows=rows,
        longitudinal_input_transverse_output_norm_upper=upper(vector_norm(longitudinal_bounds)),
        longitudinal_input_axis_norm=upper(vector_norm(axis)),
        longitudinal_input_uses_original_directional_error_maps=True,
        two_radius_global_contraction_inferred=False,
        state_error_pullback_compared=pullback_state_errors,
        longitudinal_output=dict(support=upper(long_value.support()),linear=upper(long_value.linear_bound()),
            nonlinear=upper(long_value.r),longitudinal_input_support=upper(long_on_axis),
            state_errors_pulled_back=long_state_errors_pulled),
        local_fixed_axis_two_radius_majorant=dict(
            row_order=['longitudinal_output','transverse_output'],
            column_order=['longitudinal_input','Euclidean_superset_of_transverse_input'],
            bounds=[[upper(v) for v in row] for row in two_radius],
            original_trial_radii_exact=[str(v.fmpq()) for v in radii],
            weighted_row_bounds=[upper(v) for v in weighted_rows],
            strict_local_weighted_gain_below_one=bool(max(weighted_rows)<1),
            all_history_intervals_covered=False,physical_quotient_identification_inferred=False),
        full_history_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        full_shared_models_exported=export_models,models_SHA256=saved.sha(archive) if export_models else None,
        input_hashes_rechecked_after_arithmetic=True,guarded_input_SHA256=input_hashes_before,
        constant_models_SHA256=hashlib.sha256(constants_bytes).hexdigest().upper(),
        source_hashes={**verified['paired_source_hashes'],
            'midpoint_corrected_record':saved.sha(midpoint_corrected/'record.json'),
            'endpoint_corrected_record':saved.sha(endpoint_corrected/'record.json'),
            'corrected_reconstruction':saved.sha(Path(corrected_models.__file__)),
            'midpoint_base_radii':saved.sha(midpoint_refined_path),
            'midpoint_descriptor_receipt':saved.sha(midpoint_path/'scalar_model_receipt.json')
                if (midpoint_path/'scalar_model_receipt.json').exists() else None,
            'endpoint_descriptor_receipt':saved.sha(endpoint_path/'scalar_model_receipt.json')
                if (endpoint_path/'scalar_model_receipt.json').exists() else None,
            'midpoint_descriptor_model':saved.sha(midpoint_path/'scalar_model.json.gz')
                if (midpoint_path/'scalar_model.json.gz').exists() else mid['models_SHA256'],
            'endpoint_descriptor_model':saved.sha(endpoint_path/'scalar_model.json.gz')
                if (endpoint_path/'scalar_model.json.gz').exists() else end['models_SHA256'],
            'midpoint_record':saved.sha(midpoint_path/'record.json'),'endpoint_record':saved.sha(endpoint_path/'record.json'),
            'endpoint_adjoint':saved.sha(adjoint_path),'endpoint_base_radii':saved.sha(refined_path),
            'midpoint_adjoint':saved.sha(midpoint_adjoint_path),
            'evaluator':saved.sha(Path(__file__)),'arithmetic':saved.sha(Path(arithmetic.__file__)),
            'input_error_maps':saved.sha(Path(error_maps.__file__)),
            'input_error_pullback':saved.sha(Path(error_pullback.__file__)),
            'full_input_error_pullback':saved.sha(Path(full_error_pullback.__file__)) if pullback_state_errors else None,
            'joint_output_support':saved.sha(Path(joint_support.__file__))})
    (out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(local_right_block_norm_upper=float(total),Gate7_closed=False)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','midpoint','endpoint','endpoint-adjoint','endpoint-refined','midpoint-adjoint','midpoint-refined','midpoint-corrected','endpoint-corrected','out'):
        parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--export-models',action='store_true')
    parser.add_argument('--pullback-state-errors',action='store_true')
    args=parser.parse_args();ctx.prec=512
    if args.out.exists(): raise FileExistsError('fresh output directory required')
    evaluate(args.evidence_root.resolve(),args.midpoint.resolve(),args.endpoint.resolve(),
             args.endpoint_adjoint.resolve(),args.endpoint_refined.resolve(),args.out.resolve(),args.midpoint_adjoint.resolve(),
             args.midpoint_refined.resolve(),args.midpoint_corrected.resolve(),args.endpoint_corrected.resolve(),args.export_models,args.pullback_state_errors)


if __name__=='__main__': main()

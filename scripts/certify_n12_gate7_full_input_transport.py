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


def evaluate(root,midpoint_path,endpoint_path,adjoint_path,refined_path,out,midpoint_adjoint_path,export_models=False):
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(root/'src/bhsm/interface'))
    verified=saved.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p,cert=base.p,base.p.values.cert
    mid,mdomain,mencoded,mdecode=read_models(midpoint_path,'midpoint',verified)
    end,domain,eencoded,edecode=read_models(endpoint_path,'endpoint',verified)
    if (end['source_hashes']['adjoint']!=saved.sha(adjoint_path)
            or end['source_hashes']['refined_base_radii']!=saved.sha(refined_path)):
        raise ValueError('same endpoint input map and correction radii required')
    adjoint=json.loads(adjoint_path.read_bytes())
    refined=json.loads(refined_path.read_bytes())
    midpoint_error_map=error_maps.load_error_map(root,mid,midpoint_adjoint_path)
    endpoint_error_map=error_maps.load_error_map(root,end,adjoint_path)
    W=None
    for i,row in enumerate(eencoded):
        if i==73: W=edecode(row)
    if W is None: raise ValueError('endpoint descriptor pivot row required')
    del eencoded
    source=root/'tmp/bhsm_endpoint_trial_mean_value_bootstrap_right_pair_20260913/value/first/column.npz'
    eigen=root/'artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_014/eigenpair.npz'
    with np.load(source,allow_pickle=False) as z,np.load(eigen,allow_pickle=False) as e:
        centers=[saved.read_matrix(z,f'point_center_{i}',center=True) for i in range(7)]
        ep=saved.read_matrix(e,'eigenpair_center',center=True)
        center=saved.read_matrix(e,'center_state',center=True)
        directions=saved.read_matrix(z,'weighted_tube_directions')
        raw=saved.read_matrix(z,'raw_domain')
    radii=[arb(v) for v in refined['correction_radii_exact'][:124]]
    axis_radii=[arb(v) for v in end['axis_correction_radii']]
    U=arb_mat([[arb(v) for v in row] for row in adjoint['input_map']])
    def constant_input(c):
        result=InputLinearTaylor(domain,arb_mat(1,198,c),arb_mat(199,198),input_groups=end['input_groups'])
        result._linear=arb(0)
        return result
    def model(c,derivative,rows,offset):
        values=[]
        for i in range(rows):
            a=[derivative[i,j] for j in range(75)]+[arb(0)]*124
            a[75+offset+i]=radii[offset+i]
            values.append(domain.affine(c[i,0],a))
        return values
    def direction_model(key,offset):
        values=[]
        for i,row in enumerate(adjoint[key]):
            c=[arb(v) for v in row]+[arb(0)]*124
            c[74+offset+i]=axis_radii[offset+i]
            values.append(constant_input(c))
        return values
    psi=model(ep,centers[3],61,0)
    hard=model(centers[0],centers[4],62,62)
    psi_u=direction_model('point_line_map',0)
    hard_u=direction_model('point_response_map',62)
    _,weights,_,_,_=p.values.operands()
    qw,rw,_,_=cert.metric_data()
    weights,qw,rw=[[arb(float(v)) for v in vv] for vv in (weights,qw,rw)]
    state=[domain.affine(center[i,0],[directions[i,j]/weights[i] for j in range(75)]+[arb(0)]*124) for i in range(98)]
    u=[constant_input([U[i,j]/weights[i] for j in range(74)]+[arb(0)]*124) for i in range(98)]
    s=domain.affine(raw[98,0].mid(),[directions[98,j] for j in range(75)]+[arb(0)]*124)
    su=constant_input([U[98,j] for j in range(74)]+[arb(0)]*124)
    configuration=[qw[i]*state[37+i] for i in range(37)]
    configuration_u=[qw[i]*u[37+i] for i in range(37)]
    N=[s*v for v in configuration]+[rw[i]*(hard[61]*psi[i]+s*hard[i]) for i in range(61)]
    Nu=[su*x+s*y for x,y in zip(configuration,configuration_u)]
    Nu += [rw[i]*(hard_u[61]*psi[i]+hard[61]*psi_u[i]+su*hard[i]+s*hard_u[i]) for i in range(61)]
    norm=(dot(N,N).log()/2).exp()
    inner=dot(N,Nu)
    numerator=[Nu[i]/norm-N[i]*inner/(norm**3) for i in range(98)]
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
    midfile=root/'tmp/bhsm_midpoint_center_mean_value_right_pair_20260913/value/first/column.npz'
    with np.load(midfile,allow_pickle=False) as z:
        mdirections=saved.read_matrix(z,'weighted_tube_directions')
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
    rows=[];bounds=[];linear_bounds=[];remainder_bounds=[]
    original_constants=arb_mat(74,322);pulled_constants=arb_mat(74,322)
    out.mkdir(parents=True,exist_ok=False)
    archive=out/'models.jsonl.gz'
    with ExitStack() as stack:
        output=None
        if export_models:
            rawfile=stack.enter_context(archive.open('xb'))
            output=stack.enter_context(gzip.GzipFile(fileobj=rawfile,mode='wb',filename='',mtime=0))
        for i,midpoint_coefficients in enumerate(mencoded):
            ratio,complement=eliminate_descriptor([coefficient[i,j] for j in range(99)],
                                                 [L[73,j] for j in range(99)])
            # Eliminate the descriptor before combining remainder bounds:
            # otherwise reconstructing A[98] and multiplying it again would
            # charge the same numerator remainders twice and lose cancellation.
            endpoint_part=ratio*scalar_difference+dot(complement,difference)
            endpoint_part+=constant_input([mapped_input_roundoff[i,j] for j in range(74)]+[arb(0)]*124)
            midpoint_model=mdecode(midpoint_coefficients)
            if str(midpoint_model.support().fmpq())!=mid['rows'][i]['support']['exact']:
                raise ArithmeticError('midpoint operator row does not replay exactly')
            value=embed(midpoint_model,midpoint_state,midpoint_input)+embed(endpoint_part,endpoint_state,endpoint_input)
            c=[fixed[i,j] for j in range(74)]+[arb(0)]*248
            fixed_model=InputLinearTaylor(common,arb_mat(1,322,c),arb_mat(497,322),input_groups=input_groups)
            fixed_model._linear=arb(0)
            value=value+fixed_model
            original_support=value.support()
            for j in range(322): original_constants[i,j]=value.c[0,j]
            value=error_pullback.pullback_constant_errors(value,[(74,midpoint_error_map),(198,endpoint_error_map)])
            for j in range(322): pulled_constants[i,j]=value.c[0,j]
            support=value.support();bounds.append(support)
            linear_bounds.append(value.linear_bound());remainder_bounds.append(value.r)
            rows.append(dict(component=i,support=upper(support),linear=upper(value.linear_bound()),nonlinear=upper(value.r),
                             independently_boxed_error_support=upper(original_support)))
            if output is not None:
                encoded=[[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in value.c.entries()+value.a.entries()+[value.r]]
                output.write(json.dumps(encoded,separators=(',',':')).encode()+b'\n')
            print(json.dumps(dict(row=i,support=float(support))),flush=True)
    linear_norm=vector_norm(linear_bounds);remainder_norm=vector_norm(remainder_bounds)
    old_joint=joint_support.joint_constant_support(original_constants,input_groups)
    pulled_joint=joint_support.joint_constant_support(pulled_constants,input_groups)
    total=min(vector_norm(bounds),(min(old_joint,pulled_joint)+linear_norm+remainder_norm).upper())
    constants_bytes=gzip.compress(saved.encoded({name:[[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in matrix.entries()]
        for name,matrix in (('original',original_constants),('pulled',pulled_constants))}),mtime=0)
    (out/'constants.json.gz').write_bytes(constants_bytes)
    result=dict(algorithm='FULL_INPUT_SHARED_ENDPOINT_HS_TRANSPORT_V1',physical_input_columns=74,projected_output_rows=74,
        original_state_groups=groups,input_groups=input_groups,endpoint_state_embedding=endpoint_state,
        midpoint_state_embedding=midpoint_state,endpoint_input_embedding=endpoint_input,midpoint_input_embedding=midpoint_input,
        identity='Q-QPE+(h/6)QPA0+Bmid+PM(E/2-hA0/8-U_mid)+[(h/6)QP-(h/8)PM](A-A0)',
        fixed_anchor_transport_before_norm=True,midpoint_derivative_coefficient_dependence_relaxed=True,
        endpoint_descriptor_eliminated_before_remainder_bound=True,
        common_physical_input_retained_in_constant_error_terms=True,
        all_output_rows_combined_before_constant_error_norm=True,
        joint_original_constant_support=upper(old_joint),joint_pulled_constant_support=upper(pulled_joint),
        linear_vector_bound=upper(linear_norm),nonlinear_vector_bound=upper(remainder_norm),
        pointwise_interval_affine_enclosure=True,constant_coefficients_must_not_be_differentiated=True,
        endpoint_input_roundoff_operator_bound=upper(vector_norm(input_roundoff.entries())),
        endpoint_parameter_coefficient_difference=upper(max(abs(v).upper() for v in parameter_differences)),
        all_source_coefficient_radii_retained=True,
        complete_local_right_block_norm_upper=upper(total),strict_local_gain_below_one=bool(total<1),rows=rows,
        full_history_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        full_shared_models_exported=export_models,models_SHA256=saved.sha(archive) if export_models else None,
        constant_models_SHA256=hashlib.sha256(constants_bytes).hexdigest().upper(),
        source_hashes={**verified['paired_source_hashes'],
            'midpoint_record':saved.sha(midpoint_path/'record.json'),'endpoint_record':saved.sha(endpoint_path/'record.json'),
            'endpoint_adjoint':saved.sha(adjoint_path),'endpoint_base_radii':saved.sha(refined_path),
            'midpoint_adjoint':saved.sha(midpoint_adjoint_path),
            'evaluator':saved.sha(Path(__file__)),'arithmetic':saved.sha(Path(arithmetic.__file__)),
            'input_error_maps':saved.sha(Path(error_maps.__file__)),
            'input_error_pullback':saved.sha(Path(error_pullback.__file__)),
            'joint_output_support':saved.sha(Path(joint_support.__file__))})
    (out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(local_right_block_norm_upper=float(total),Gate7_closed=False)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','midpoint','endpoint','endpoint-adjoint','endpoint-refined','midpoint-adjoint','out'):
        parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--export-models',action='store_true')
    args=parser.parse_args();ctx.prec=512
    if args.out.exists(): raise FileExistsError('fresh output directory required')
    evaluate(args.evidence_root.resolve(),args.midpoint.resolve(),args.endpoint.resolve(),
             args.endpoint_adjoint.resolve(),args.endpoint_refined.resolve(),args.out.resolve(),args.midpoint_adjoint.resolve(),args.export_models)


if __name__=='__main__': main()

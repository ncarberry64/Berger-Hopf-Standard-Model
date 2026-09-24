"""Tighten full-input output bounds using the original common input matrix."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'): os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
from flint import arb,arb_mat,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bhsm.interface.common_input_error_pullback as pullback
import bhsm.interface.joint_output_support as joint
from bhsm.interface.input_linear_taylor import vector_norm
from bhsm.interface.shared_parameter_residual import linear_support
import certify_n12_gate7_full_input_transport as transport
import evaluate_n12_gate7_coupled_residual_saved as saved
import n12_gate7_common_input_error_maps as maps


def evaluate(root,path,adjoint_path,out):
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(root/'src/bhsm/interface'))
    verified=saved.evaluate(root)
    family=json.loads((path/'record.json').read_bytes())['family']
    record,domain,encoded_rows,_=transport.read_models(path,family,verified)
    error_map=maps.load_error_map(root,record,adjoint_path)
    anchors=maps.load_projected_anchor(root,record)
    rows=[];bounds=[];deviations=[];constant_rows=[]
    original_constants=arb_mat(74,198);pulled_constants=arb_mat(74,198)
    for i,encoded in enumerate(encoded_rows):
        if len(encoded)!=198+198*domain.dimension+1:
            raise ValueError('complete source row required')
        old=arb_mat(1,198,[transport.restore(v) for v in encoded[:198]])
        new=pullback.pullback_constant_coefficients(old,[(74,error_map)])
        for j in range(198):
            original_constants[i,j]=old[0,j]
            pulled_constants[i,j]=new[0,j]
        tail=arb(record['rows'][i]['linear']['exact'])+arb(record['rows'][i]['nonlinear']['exact'])
        bound=(linear_support(new.entries(),record['input_groups'])+tail).upper()
        difference=new-arb_mat(1,198,[anchors[i,j] for j in range(74)]+[arb(0)]*124)
        deviation=(linear_support(difference.entries(),record['input_groups'])+tail).upper()
        chosen=min(bound,arb(record['rows'][i]['support']['exact']))
        chosen_deviation=min(deviation,arb(record['rows'][i]['anchor_deviation']['exact']))
        bounds.append(chosen);deviations.append(chosen_deviation)
        constant_rows.append([[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in new.entries()[:74]])
        rows.append(dict(component=i,pulled_back_support=transport.upper(bound),
            pulled_back_anchor_deviation=transport.upper(deviation),
            chosen_support=transport.upper(chosen),chosen_anchor_deviation=transport.upper(chosen_deviation)))
        print(json.dumps(dict(row=i,anchor_deviation=float(chosen_deviation))),flush=True)
    anchor_matrix=arb_mat(74,198,[anchors[i,j] if j<74 else arb(0) for i in range(74) for j in range(198)])
    linear_norm=vector_norm([arb(row['linear']['exact']) for row in record['rows']])
    remainder_norm=vector_norm([arb(row['nonlinear']['exact']) for row in record['rows']])
    tail=(linear_norm+remainder_norm).upper()
    original_joint=joint.joint_constant_support(original_constants,record['input_groups'])
    pulled_joint=joint.joint_constant_support(pulled_constants,record['input_groups'])
    original_deviation=joint.joint_constant_support(original_constants-anchor_matrix,record['input_groups'])
    pulled_deviation=joint.joint_constant_support(pulled_constants-anchor_matrix,record['input_groups'])
    full_norm=min(vector_norm(bounds),(min(original_joint,pulled_joint)+tail).upper())
    deviation_norm=min(vector_norm(deviations),(min(original_deviation,pulled_deviation)+tail).upper())
    result=dict(algorithm='COMMON_PHYSICAL_INPUT_AND_JOINT_OUTPUT_SUPPORT_V2',family=family,
        physical_input_columns=74,projected_output_rows=74,original_domain_unchanged=True,
        linear_and_nonlinear_terms_unchanged=True,constant_error_terms_pulled_back_before_norm=True,
        pointwise_interval_affine_enclosure=True,constant_coefficients_must_not_be_differentiated=True,
        complete_fixed_family_operator_norm_upper=transport.upper(full_norm),
        anchor_deviation_operator_norm_upper=transport.upper(deviation_norm),rows=rows,
        joint_constant_support=transport.upper(original_joint),joint_pulled_constant_support=transport.upper(pulled_joint),
        joint_constant_deviation=transport.upper(original_deviation),joint_pulled_constant_deviation=transport.upper(pulled_deviation),
        linear_vector_bound=transport.upper(linear_norm),nonlinear_vector_bound=transport.upper(remainder_norm),
        all_output_rows_combined_before_constant_error_norm=True,
        physical_constant_replacements=constant_rows,remaining_constant_error_slots_exactly_zero=True,
        source_hashes={'parent_record':saved.sha(path/'record.json'),'parent_models':record['models_SHA256'],
            'adjoint':saved.sha(adjoint_path),'evaluator':saved.sha(Path(__file__)),
            'input_error_maps':saved.sha(Path(maps.__file__)),'pullback_arithmetic':saved.sha(Path(pullback.__file__)),
            'joint_output_norm':saved.sha(Path(joint.__file__))},
        full_history_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    with out.open('xb') as output: output.write(saved.encoded(result))
    print(json.dumps({k:result[k] for k in ('family','complete_fixed_family_operator_norm_upper','anchor_deviation_operator_norm_upper')}),flush=True)


def main():
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','certificate','adjoint','out'): parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();ctx.prec=512
    evaluate(args.evidence_root.resolve(),args.certificate.resolve(),args.adjoint.resolve(),args.out.resolve())


if __name__=='__main__': main()

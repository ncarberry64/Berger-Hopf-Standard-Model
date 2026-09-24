"""Replay every retained-axis row and combine it with a full-input bound."""
import argparse
import gzip
import json
from pathlib import Path
import sys
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain,Taylor
from bhsm.interface.input_linear_taylor import vector_norm
from certify_n12_gate7_endpoint_vector_transport import restore,upper
import n12_gate7_left_saved_family as saved
import verify_n12_gate7_left_transport as full_verifier


def verify(folder,full):
    record=json.loads((folder/'record.json').read_bytes())
    archive=folder/'models.json.gz'
    producer=ROOT/'scripts/certify_n12_gate7_left_longitudinal_transport.py'
    if (record.get('algorithm')!='LEFT_RETAINED_AXIS_SHARED_PRETRANSPORT_BOUND_V1'
            or record.get('side')!='left' or record['input_axis_node']!=13
            or record['output_axis_node']!=14 or record['state_dimension']!=497
            or record['fixed_physical_input_dimension']!=1
            or record['original_physical_input_dimension']!=74
            or record['models_SHA256']!=saved.sha(archive)
            or record['guarded_input_SHA256']['evaluator']!=saved.sha(producer)
            or record['all_input_operator_certified_by_this_record'] is not False
            or any(record[k] is not True for k in ('all_61_velocity_components_retained',
                'all_248_base_equations_retained','endpoint_base_cancelled_before_interval_midpoint_transport',
                'every_weighted_base_remainder_retained','original_physical_domain_unchanged'))):
        raise ValueError('complete unchanged retained-axis proof required')
    domain=TaylorDomain(record['original_state_groups'],497)
    encoded=json.loads(gzip.decompress(archive.read_bytes()))
    if len(encoded)!=75 or len(record['rows'])!=74:
        raise ValueError('74 transverse components and one longitudinal row required')
    models=[]
    for i,row in enumerate(encoded):
        if len(row)!=499: raise ValueError('every constant, state coefficient and remainder required')
        values=[restore(v) for v in row]
        model=Taylor(domain,values[0],arb_mat(1,497,values[1:-1]),values[-1])
        saved_row=record['rows'][i] if i<74 else record['longitudinal_row']
        if i<74 and saved_row['component']!=i: raise ValueError('ordered transverse components required')
        for key,value in (('support',model.support()),('linear',model.linear_bound()),('nonlinear',model.r)):
            if str(value.fmpq())!=saved_row[key]['exact']:
                raise ArithmeticError('outward state-model bound failed exact replay')
        models.append(model)
    transverse=min(vector_norm([v.support() for v in models[:74]]),
        (vector_norm([v.c for v in models[:74]])+vector_norm([v.linear_bound() for v in models[:74]])
         +vector_norm([v.r for v in models[:74]])).upper())
    longitudinal=models[-1].support()
    for name,value in (('transverse_output_on_longitudinal_input',transverse),
                       ('longitudinal_output_on_longitudinal_input',longitudinal)):
        if str(value.fmpq())!=record[name]['exact']:
            raise ArithmeticError('retained-axis vector aggregation failed exact replay')
    result=dict(algorithm='LEFT_RETAINED_AXIS_TRANSPORT_REPLAY_V1',
        replayed_state_models=75,all_bounds_replayed_exactly=True,
        transverse_output_on_longitudinal_input=upper(transverse),
        longitudinal_output_on_longitudinal_input=upper(longitudinal),
        record_SHA256=saved.sha(folder/'record.json'),models_SHA256=saved.sha(archive),
        verifier_SHA256=saved.sha(Path(__file__)),Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    if full is not None:
        original=json.loads((full/'record.json').read_bytes())
        constants=full/'constants.json.gz'
        if saved.sha(constants)!=original['constant_models_SHA256']:
            raise ValueError('unchanged full-input constant coefficients required')
        full_verifier.verify(original,json.loads(gzip.decompress(constants.read_bytes())))
        for family in ('midpoint','endpoint'):
            for old,new in ((family+'_parent_record',family+'_parent'),
                            (family+'_error_refinement',family+'_errors'),
                            (family+'_base_residual_record',family+'_base_record')):
                if original['guarded_input_SHA256'][old]!=record['guarded_input_SHA256'][new]:
                    raise ValueError('both bounds must use identical physical families and refinements')
        if original['source_hashes']['evaluator']!=saved.sha(ROOT/'scripts/certify_n12_gate7_left_refined_transport.py'):
            raise ValueError('reviewed complete left-block producer required')
        old=original['local_fixed_axis_two_radius_majorant']
        bounds=[[arb(v['exact']) for v in row] for row in old['bounds']]
        bounds[0][0]=min(bounds[0][0],longitudinal)
        bounds[1][0]=min(bounds[1][0],transverse)
        radii=[arb(v) for v in old['original_trial_radii_exact']]
        weighted=[(sum((bounds[i][j]*radii[j] for j in range(2)),arb(0))/radii[i]).upper() for i in range(2)]
        result.update(full_input_record_SHA256=saved.sha(full/'record.json'),
            combined_two_radius_bounds=[[upper(v) for v in row] for row in bounds],
            original_trial_radii_exact=old['original_trial_radii_exact'],
            weighted_row_bounds=[upper(v) for v in weighted],
            strict_local_weighted_gain_below_one=bool(max(weighted)<1),
            local_margin_lower=upper((1-max(weighted)).lower()),
            all_history_intervals_covered=False,physical_quotient_identification_inferred=False)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--transport',type=Path,required=True)
    parser.add_argument('--full-transport',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    ctx.prec=512
    result=verify(args.transport,args.full_transport)
    with args.out.open('xb') as stream: stream.write(saved.encoded(result))
    print(json.dumps({k:v for k,v in result.items() if k not in ('combined_two_radius_bounds','original_trial_radii_exact')},sort_keys=True))


if __name__=='__main__':
    main()

"""Combine verified left/right interval-13 bounds in the retained product norm.

For endpoint perturbations each bounded by the same two radii, the
componentwise sum of the two nonnegative majorants bounds the complete
local defect row by the triangle inequality. This is not a bound for the
full causal history operator or a self-map certificate.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from flint import arb,ctx
from certify_n12_gate7_endpoint_vector_transport import upper
import n12_gate7_left_saved_family as saved
import verify_n12_gate7_refined_transport as right_verifier
import verify_n12_gate7_left_longitudinal_transport as left_verifier


def verify(right_folder,left_folder,axis_folder):
    right=json.loads((right_folder/'record.json').read_bytes())
    left=json.loads((left_folder/'record.json').read_bytes())
    expected={
        'right':('FULL_INPUT_REFINED_DIRECTIONAL_HS_TRANSPORT_V4',
                 'certify_n12_gate7_refined_directional_transport.py'),
        'left':('LEFT_FULL_INPUT_REFINED_DIRECTIONAL_HS_TRANSPORT_V1',
                'certify_n12_gate7_left_refined_transport.py')}
    for name,record in [('right',right),('left',left)]:
        algorithm,producer=expected[name]
        if record['algorithm']!=algorithm or record['source_hashes']['evaluator']!=saved.sha(ROOT/'scripts'/producer):
            raise ValueError('unchanged reviewed interval-13 producer required')
    if (left['side']!='left' or left['input_axis_node']!=13 or left['output_axis_node']!=14
            or left['guarded_input_SHA256']['original_trial_radii']!=right['guarded_input_SHA256']['original_trial_radii']):
        raise ValueError('same retained output frame and original trial radii required')
    shared=[k for k in right['source_hashes'] if k.startswith(('artifacts/','tmp/'))]
    if not shared or any(left['source_hashes'].get(k)!=right['source_hashes'][k] for k in shared):
        raise ValueError('the left and right bounds must retain the same physical evidence')
    archive=right_folder/'constants.json.gz'
    if saved.sha(archive)!=right['constant_models_SHA256']:
        raise ValueError('unchanged right constant archive required')
    right_verifier.verify(right,json.loads(gzip.decompress(archive.read_bytes())))
    replay=left_verifier.verify(axis_folder,left_folder)
    right_majorant=right['local_fixed_axis_two_radius_majorant']
    if replay['original_trial_radii_exact']!=right_majorant['original_trial_radii_exact']:
        raise ValueError('identical original radii required')
    radii=[arb(v) for v in replay['original_trial_radii_exact']]
    matrices=[replay['combined_two_radius_bounds'],right_majorant['bounds']]
    bounds=[[sum((arb(m[i][j]['exact']) for m in matrices),arb(0)).upper()
             for j in range(2)] for i in range(2)]
    weighted=[(sum((bounds[i][j]*radii[j] for j in range(2)),arb(0))/radii[i]).upper()
              for i in range(2)]
    gain=max(weighted)
    return dict(algorithm='TWO_SIDED_INTERVAL_013_LOCAL_ROW_MAJORANT_V1',
        interval=13,input_axis_nodes=[13,14],output_axis_node=14,
        original_trial_radii_exact=replay['original_trial_radii_exact'],
        row_order=['longitudinal_output','transverse_output'],
        column_order=['longitudinal_input','Euclidean_superset_of_transverse_input'],
        summed_majorant=[[upper(v) for v in row] for row in bounds],
        weighted_row_bounds=[upper(v) for v in weighted],
        local_row_gain_upper=upper(gain),local_row_margin_lower=upper((1-gain).lower()),
        strict_local_row_gain_below_one=bool(gain<1),
        independent_endpoint_inputs_each_bounded_by_original_radii=True,
        both_endpoint_blocks_and_all_74_output_rows_included=True,
        right_record_SHA256=saved.sha(right_folder/'record.json'),
        left_record_SHA256=saved.sha(left_folder/'record.json'),
        left_axis_record_SHA256=saved.sha(axis_folder/'record.json'),
        evaluator_SHA256=saved.sha(Path(__file__)),
        right_verifier_SHA256=saved.sha(Path(right_verifier.__file__)),
        left_verifier_SHA256=saved.sha(Path(left_verifier.__file__)),
        all_history_intervals_covered=False,global_causal_operator_bound_inferred=False,
        physical_self_map_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser()
    for key in ('right','left','left-axis','out'):
        parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();ctx.prec=512
    result=verify(args.right,args.left,args.left_axis)
    with args.out.open('xb') as stream: stream.write(saved.encoded(result))
    print(json.dumps({k:result[k] for k in ('local_row_gain_upper','local_row_margin_lower','strict_local_row_gain_below_one')}))


if __name__=='__main__': main()

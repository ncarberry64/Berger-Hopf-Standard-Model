"""Replay all final norms while enforcing the left input/output identification."""
import argparse
import gzip
import json
from pathlib import Path
from flint import ctx
import verify_n12_gate7_coupled_transport_bounds as aggregation
import n12_gate7_left_saved_family as saved


def verify(record, constants):
    if (record.get('algorithm') != 'LEFT_FULL_INPUT_REFINED_DIRECTIONAL_HS_TRANSPORT_V1'
            or record.get('side') != 'left'
            or record.get('input_axis_node') != 13 or record.get('output_axis_node') != 14
            or record.get('endpoint_state_embedding') != [0]+list(range(2, 76))+list(range(373, 497))):
        raise ValueError('the retained left input and right output identifications are required')
    for key in ('all_248_base_residuals_used',
                'endpoint_base_cancelled_before_interval_midpoint_transport',
                'base_residuals_cancelled_before_common_input_substitution',
                'added_base_residual_remainders_retained_until_input_substitution',
                'longitudinal_errors_intersected_using_shared_implicit_residuals'):
        if record.get(key) is not True:
            raise ValueError('complete source-bound cancellations and remainders required')
    # The existing numerical aggregator is side-independent. Its historical
    # field name is adapted here only after checking the left scope above.
    result = aggregation.verify({**record,
        'algorithm':'FULL_INPUT_COUPLED_NUMERATOR_HS_TRANSPORT_V1',
        'complete_local_right_block_norm_upper':record['complete_local_left_block_norm_upper']}, constants)
    return dict(result, side='left', input_axis_node=13, output_axis_node=14)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--transport', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    path = args.transport/'record.json'
    archive = args.transport/'constants.json.gz'
    record = json.loads(path.read_bytes())
    if saved.sha(archive) != record['constant_models_SHA256']:
        raise ValueError('exact transported constant archive required')
    result = verify(record, json.loads(gzip.decompress(archive.read_bytes())))
    result.update(record_SHA256=saved.sha(path), constants_SHA256=saved.sha(archive),
        verifier_SHA256=saved.sha(Path(__file__)),
        aggregation_verifier_SHA256=saved.sha(Path(aggregation.__file__)),
        residual_models_recomputed=False)
    with args.out.open('xb') as f:
        f.write(saved.encoded(result))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()

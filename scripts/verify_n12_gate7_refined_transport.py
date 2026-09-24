"""Replay complete local norm aggregation after dependency refinements."""
import argparse
import gzip
import json
from pathlib import Path
from flint import ctx
import verify_n12_gate7_coupled_transport_bounds as aggregation
import evaluate_n12_gate7_coupled_residual_saved as saved


def verify(record, constants):
    if record['algorithm'] not in (
            'FULL_INPUT_PRETRANSPORT_BASE_RESIDUAL_HS_TRANSPORT_V3',
            'FULL_INPUT_REFINED_DIRECTIONAL_HS_TRANSPORT_V4'):
        raise ValueError('reviewed pretransport cancellation algorithm required')
    for key in ('all_248_base_residuals_used',
                'endpoint_base_cancelled_before_interval_midpoint_transport',
                'base_residuals_cancelled_before_common_input_substitution',
                'added_base_residual_remainders_retained_until_input_substitution'):
        if record.get(key) is not True:
            raise ValueError('complete base residual cancellation and tails required')
    if (record['algorithm'].endswith('_V4')
            and record.get('longitudinal_errors_intersected_using_shared_implicit_residuals') is not True):
        raise ValueError('source-bound longitudinal error refinement required')
    return aggregation.verify({**record,'algorithm':'FULL_INPUT_COUPLED_NUMERATOR_HS_TRANSPORT_V1'},constants)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--transport',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();ctx.prec=512
    if args.out.exists():raise FileExistsError('fresh verification receipt required')
    path=args.transport/'record.json';archive=args.transport/'constants.json.gz'
    record=json.loads(path.read_bytes())
    if saved.sha(archive)!=record['constant_models_SHA256']:
        raise ValueError('exact transported constant archive required')
    result=verify(record,json.loads(gzip.decompress(archive.read_bytes())))
    result.update(record_SHA256=saved.sha(path),constants_SHA256=saved.sha(archive),
        verifier_SHA256=saved.sha(Path(__file__)),
        aggregation_verifier_SHA256=saved.sha(Path(aggregation.__file__)),
        residual_models_recomputed=False)
    args.out.write_bytes(saved.encoded(result));print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()

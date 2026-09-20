"""Replay norm aggregation for transport with added base-residual tails."""
import argparse
import gzip
import json
from pathlib import Path
from flint import ctx
import verify_n12_gate7_coupled_transport_bounds as aggregation
import evaluate_n12_gate7_coupled_residual_saved as saved


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--transport',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();ctx.prec=512
    if args.out.exists(): raise FileExistsError('fresh aggregation verification required')
    path=args.transport/'record.json';record=json.loads(path.read_bytes())
    if (record['algorithm']!='FULL_INPUT_BASE_RESIDUAL_COUPLED_HS_TRANSPORT_V2'
            or record['all_248_base_residuals_used'] is not True
            or record['base_residuals_cancelled_before_common_input_substitution'] is not True
            or record['added_base_residual_remainders_retained_until_input_substitution'] is not True):
        raise ValueError('complete base-cancelled local transport required')
    archive=args.transport/'constants.json.gz'
    if saved.sha(archive)!=record['constant_models_SHA256']: raise ValueError('exact constant archive required')
    # The generic aggregation is identical. Only its producer identifier is
    # adapted here; every numeric field and every claim-scope flag is checked.
    check={**record,'algorithm':'FULL_INPUT_COUPLED_NUMERATOR_HS_TRANSPORT_V1'}
    result=aggregation.verify(check,json.loads(gzip.decompress(archive.read_bytes())))
    result.update(record_SHA256=saved.sha(path),constants_SHA256=saved.sha(archive),
        verifier_SHA256=saved.sha(Path(__file__)),aggregation_verifier_SHA256=saved.sha(Path(aggregation.__file__)),
        base_residual_models_recomputed=False)
    args.out.write_bytes(saved.encoded(result));print(json.dumps(result,sort_keys=True))


if __name__=='__main__': main()

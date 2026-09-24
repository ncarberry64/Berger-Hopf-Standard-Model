"""Retain the exact descriptor pivot from a verified full coefficient archive."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
from flint import arb_mat,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from certify_n12_gate7_full_input_transport import json_array_rows
from certify_n12_gate7_endpoint_vector_transport import restore
import evaluate_n12_gate7_coupled_residual_saved as saved


def evaluate(parent,out):
    record=json.loads((parent/'record.json').read_bytes())
    archive=parent/'models.json.gz'
    if saved.sha(archive)!=record['models_SHA256']: raise ValueError('exact parent archive fingerprint required')
    count=0;selected=None
    with gzip.open(archive,'rt',encoding='utf-8') as stream:
        for i,row in enumerate(json_array_rows(stream)):
            count+=1
            if i==73: selected=row
    if count!=74 or selected is None: raise ValueError('complete 74-row parent archive required')
    dimension={'midpoint':373,'endpoint':199}[record['family']]
    domain=TaylorDomain(record['original_state_groups'],dimension)
    if len(selected)!=198+dimension*198+1: raise ValueError('complete descriptor coefficient row required')
    v=[restore(pair) for pair in selected]
    model=InputLinearTaylor(domain,arb_mat(1,198,v[:198]),arb_mat(dimension,198,v[198:-1]),v[-1],record['input_groups'])
    if str(model.support().fmpq())!=record['rows'][73]['support']['exact']:
        raise ArithmeticError('descriptor support failed exact replay')
    data=gzip.compress(saved.encoded(selected),mtime=0)
    receipt=dict(algorithm='EXACT_FULL_INPUT_DESCRIPTOR_PIVOT_EXTRACTION_V1',family=record['family'],
        parent_record_SHA256=saved.sha(parent/'record.json'),parent_models_SHA256=record['models_SHA256'],
        scalar_model_SHA256=hashlib.sha256(data).hexdigest().upper(),scalar_row=73,
        source_archive_scanned_rows=count,coefficient_arithmetic_recomputed=False,
        descriptor_support_replayed=True,evaluator_SHA256=saved.sha(Path(__file__)),
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    out.mkdir(parents=True,exist_ok=False)
    # Preserve the original full result record byte-for-byte, with an
    # explicit receipt explaining the compact backing representation.
    (out/'record.json').write_bytes((parent/'record.json').read_bytes())
    (out/'scalar_model.json.gz').write_bytes(data)
    (out/'scalar_model_receipt.json').write_bytes(saved.encoded(receipt))
    print(json.dumps(dict(family=record['family'],scalar_model_bytes=len(data),scalar_model_SHA256=receipt['scalar_model_SHA256'])))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--parent',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();ctx.prec=512
    if args.out.exists(): raise FileExistsError('fresh compact output required')
    evaluate(args.parent.resolve(),args.out.resolve())


if __name__=='__main__': main()

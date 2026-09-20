"""Independently replay every coefficient support in a complete numerator set."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
from flint import arb, arb_mat, ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from certify_n12_gate7_endpoint_vector_transport import restore
import evaluate_n12_gate7_coupled_residual_saved as saved


def evaluate(folder):
    record=json.loads((folder/'record.json').read_bytes())
    if (record['components']!=list(range(61)) or len(record['records'])!=61
            or record['all_61_velocity_components_certified'] is not True
            or record['physical_input_columns']!=74
            or record['input_groups']!=[[0,74,'euclidean'],[74,198,'box']]
            or any(record[k] is not False for k in ('full_history_certified','Gate7_closed','FULL_BHSM_COMPLETE'))):
        raise ValueError('complete local numerator set with unchanged scope required')
    dimension=373 if record['family']=='midpoint' else 199 if record['family']=='endpoint' else None
    if dimension is None: raise ValueError('known physical family required')
    domain=TaylorDomain(record['original_state_groups'],dimension)
    source_file=folder.with_suffix('.terms')/'sources.json'
    sources=json.loads(source_file.read_bytes())
    if sources!=record['source_hashes']: raise ValueError('same immutable source manifest required')
    binding=saved.sha(source_file)
    digests=[]
    for i,row in enumerate(record['records']):
        path=folder/f'component_{i:02d}.json.gz'
        if row['component']!=i or saved.sha(path)!=row['models_SHA256']:
            raise ValueError('complete ordered source-bound coefficients required')
        payload=json.loads(gzip.decompress(path.read_bytes()))
        if payload['component']!=i or payload['source_binding']!=binding:
            raise ValueError('unchanged component/source binding required')
        v=[restore(pair) for pair in payload['coefficients']]
        if len(v)!=198+dimension*198+1: raise ValueError('complete coefficient model required')
        model=InputLinearTaylor(domain,arb_mat(1,198,v[:198]),arb_mat(dimension,198,v[198:-1]),v[-1],record['input_groups'])
        actual=dict(cancelled_support=model.support(),linear=model.linear_bound(),nonlinear=model.r,
                    constant_correction_support=sum((abs(model.c[0,j]).upper() for j in range(74,198)),arb(0)).upper())
        for key,value in actual.items():
            if str(value.fmpq())!=row[key]['exact']:
                raise ArithmeticError(f'component {i} {key} failed exact outward replay')
        numerical={k:payload[k] for k in ('component','coefficients','axis_covectors')}
        if 'base_adjoint_rows' in payload: numerical['base_adjoint_rows']=payload['base_adjoint_rows']
        digest=hashlib.sha256(saved.encoded(numerical)).hexdigest().upper()
        digests.append(digest)
        print(json.dumps(dict(verified_component=i,numerical_SHA256=digest)),flush=True)
    return dict(family=record['family'],all_61_component_bounds_replayed=True,
        record_SHA256=saved.sha(folder/'record.json'),numerical_component_SHA256=digests,
        canonical_numerical_set_SHA256=hashlib.sha256(saved.encoded(digests)).hexdigest().upper(),
        verifier_SHA256=saved.sha(Path(__file__)),action_contracts_recomputed=False,
        full_history_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--models',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();ctx.prec=512
    if args.out.exists(): raise FileExistsError('fresh verification output required')
    result=evaluate(args.models.resolve())
    args.out.write_bytes(saved.encoded(result))


if __name__=='__main__': main()

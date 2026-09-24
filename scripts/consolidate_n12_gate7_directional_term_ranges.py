"""Consolidate completed source-bound action terms without new arithmetic.

Only the selected disjoint component ranges are copied. The common Rayleigh
and slope terms must be byte-identical across every range. Full gzip and
coefficient-shape checks reject partial or foreign checkpoints.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import evaluate_n12_gate7_coupled_residual_saved as saved

NAMES = ('axis_gradient','axis_hessian','axis_configuration','axis_line',
         'axis_line_source','axis_response','axis_response_source')


def evaluate(shards, assembled):
    record_path = assembled/'record.json'
    record = json.loads(record_path.read_bytes())
    if (record.get('all_61_velocity_components_certified') is not True
            or record.get('components') != list(range(61))
            or record.get('physical_input_columns') != 74):
        raise ValueError('complete 61-component assembly required')
    selected = [i for _,start,stop in shards for i in range(start,stop)]
    if sorted(selected) != list(range(61)):
        raise ValueError('disjoint exact coverage of 0 through 60 required')
    target = assembled.with_suffix('.terms')
    manifest = (target/'sources.json').read_bytes()
    binding = saved.sha(target/'sources.json')
    if json.loads(manifest) != record['source_hashes']:
        raise ValueError('assembled record and term manifest must match')
    dimension = {'midpoint':373,'endpoint':199}[record['family']]
    paths = {}
    for folder,start,stop in shards:
        source = folder.with_suffix('.terms')
        if (source/'sources.json').read_bytes() != manifest:
            raise ValueError('byte-identical term manifests required')
        for name in ('rayleigh','slope'):
            path = source/(name+'.json.gz')
            if name in paths and path.read_bytes() != paths[name].read_bytes():
                raise ValueError('common action checkpoints differ between ranges')
            paths[name] = path
        for i in range(start,stop):
            component = json.loads((folder/f'component_{i:02d}.json').read_bytes())
            if component != record['records'][i]:
                raise ValueError('selected completed component is not the assembled component')
            for name in NAMES:
                key = f'component_{i:02d}_{name}'
                paths[key] = source/(key+'.json.gz')
    digests = {}
    for name,path in sorted(paths.items()):
        data = path.read_bytes()
        payload = json.loads(gzip.decompress(data))
        expected_kind = 'Taylor' if name == 'rayleigh' else 'InputLinearTaylor'
        expected_length = dimension+2 if name == 'rayleigh' else 198*(dimension+1)+1
        if (payload.get('binding') != binding or payload.get('kind') != expected_kind
                or len(payload['values']) != expected_length
                or any(not isinstance(pair,list) or len(pair) != 2 for pair in payload['values'])):
            raise ValueError('complete source-bound action checkpoint required')
        destination = target/path.name
        if destination.exists():
            if destination.read_bytes() != data:
                raise ValueError('immutable destination checkpoint differs')
        else:
            with destination.open('xb') as stream:
                stream.write(data)
        digests[path.name] = saved.sha(destination)
    receipt = dict(algorithm='EXACT_DIRECTIONAL_TERM_RANGE_CONSOLIDATION_V1',
        family=record['family'], components=61, action_terms=len(digests),
        assembled_record_SHA256=saved.sha(record_path), source_manifest_SHA256=binding,
        checkpoint_SHA256=digests, coefficients_copied_byte_identically=True,
        new_action_derivative_evaluations=0, evaluator_SHA256=saved.sha(Path(__file__)))
    with (target/'consolidation_receipt.json').open('xb') as stream:
        stream.write(saved.encoded(receipt))
    print(json.dumps(dict(family=record['family'],complete_action_terms=len(digests))),flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shard',nargs=3,action='append',required=True)
    parser.add_argument('--assembled',type=Path,required=True)
    args = parser.parse_args()
    evaluate([(Path(p),int(a),int(b)) for p,a,b in args.shard],args.assembled)


if __name__ == '__main__':
    main()

"""Assemble all 61 source-bound velocities from disjoint completed ranges."""
import argparse
import gzip
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import evaluate_n12_gate7_coupled_residual_saved as saved


def evaluate(shards,out):
    coverage=[i for _,start,stop in shards for i in range(start,stop)]
    if (any(not 0<=start<stop<=61 for _,start,stop in shards)
            or sorted(coverage)!=list(range(61))):
        raise ValueError('every physical velocity component must occur exactly once')
    if out.exists() or out.with_suffix('.terms').exists(): raise FileExistsError('fresh assembly required')
    source_bytes=(shards[0][0].with_suffix('.terms')/'sources.json').read_bytes()
    if any((folder.with_suffix('.terms')/'sources.json').read_bytes()!=source_bytes for folder,_,_ in shards):
        raise ValueError('byte-identical physical and arithmetic source manifests required')
    sources=json.loads(source_bytes)
    binding=saved.sha(shards[0][0].with_suffix('.terms')/'sources.json')
    templates=[]
    for folder,start,stop in shards:
        path=folder/'record.json'
        if path.exists():
            record=json.loads(path.read_bytes())
            if (record['components']!=list(range(start,stop)) or record['source_hashes']!=sources
                    or record['algorithm']!='FULL_INPUT_DIRECTIONAL_NUMERATOR_SHARED_RESIDUAL_V1'
                    or record['base_residuals_subtracted'] is not False):
                raise ValueError('completed range record must match the requested shard')
            templates.append(record)
    if not templates: raise ValueError('at least one completed producer record required')
    template=templates[0]
    for record in templates[1:]:
        for key in ('family','original_state_groups','input_groups','input_map','axis_correction_radii',
                    'physical_input_columns','algorithm','base_residuals_subtracted'):
            if record[key]!=template[key]: raise ValueError('identical physical family required')
    if template['physical_input_columns']!=74: raise ValueError('complete physical input sphere required')
    dimension={'midpoint':373,'endpoint':199}[template['family']]
    selected={};provenance=[]
    for folder,start,stop in shards:
        for i in range(start,stop):
            row_path=folder/f'component_{i:02d}.json';model_path=folder/f'component_{i:02d}.json.gz'
            row=json.loads(row_path.read_bytes())
            if row['component']!=i or row['models_SHA256']!=saved.sha(model_path):
                raise ValueError('complete ordered coefficient fingerprint required')
            payload=json.loads(gzip.decompress(model_path.read_bytes()))
            if (payload['component']!=i or payload['source_binding']!=binding
                    or len(payload['coefficients'])!=198+dimension*198+1
                    or row['base_residuals_subtracted'] is not False):
                raise ValueError('complete source-bound coefficient row required')
            selected[i]=(row_path,model_path,row)
            provenance.append(dict(component=i,range=[start,stop],record_SHA256=saved.sha(row_path),
                                   models_SHA256=row['models_SHA256']))
    out.mkdir(parents=True);out.with_suffix('.terms').mkdir()
    (out.with_suffix('.terms')/'sources.json').write_bytes(source_bytes)
    for i in range(61):
        row_path,model_path,_=selected[i]
        (out/row_path.name).write_bytes(row_path.read_bytes())
        (out/model_path.name).write_bytes(model_path.read_bytes())
    result={**template,'components':list(range(61)),'records':[selected[i][2] for i in range(61)],
            'all_61_velocity_components_certified':True,
            'component_shard_assembly':dict(evaluator_SHA256=saved.sha(Path(__file__)),sources=provenance,
                coefficients_copied_byte_identically=True,coefficient_arithmetic_recomputed=False)}
    (out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(family=result['family'],components=61,record_SHA256=saved.sha(out/'record.json'),Gate7_closed=False)))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--shard',nargs=3,action='append',required=True,metavar=('PATH','START','STOP'))
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    evaluate([(Path(folder).resolve(),int(start),int(stop)) for folder,start,stop in args.shard],args.out.resolve())


if __name__=='__main__': main()

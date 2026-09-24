"""Join disjoint velocity ranges after their numerical producers finish."""
import argparse
import gzip
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import evaluate_n12_gate7_coupled_residual_saved as saved


def evaluate(low,middle,high,out):
    source_bytes=(high.with_suffix('.terms')/'sources.json').read_bytes()
    if any((folder.with_suffix('.terms')/'sources.json').read_bytes()!=source_bytes for folder in (low,middle)):
        raise ValueError('byte-identical physical/arithmetic source manifests required')
    sources=json.loads(source_bytes)
    binding=saved.sha(high.with_suffix('.terms')/'sources.json')
    template=json.loads((high/'record.json').read_bytes())
    middle_record=json.loads((middle/'record.json').read_bytes())
    for key in ('family','original_state_groups','input_groups','input_map','axis_correction_radii',
                'physical_input_columns','algorithm','base_residuals_subtracted'):
        if middle_record[key]!=template[key]: raise ValueError('identical physical family and correction representation required')
    if (template['components']!=list(range(41,61)) or middle_record['components']!=list(range(21,41))
            or template['source_hashes']!=sources or middle_record['source_hashes']!=sources
            or template['base_residuals_subtracted'] is not False
            or template['algorithm']!='FULL_INPUT_DIRECTIONAL_NUMERATOR_SHARED_RESIDUAL_V1'):
        raise ValueError('completed reviewed high-component shard required')
    dimension={'midpoint':373,'endpoint':199}[template['family']]
    if out.exists() or out.with_suffix('.terms').exists(): raise FileExistsError('fresh assembly output required')
    selected=[];provenance=[]
    for i in range(61):
        folder=low if i<21 else middle if i<41 else high
        row_path=folder/f'component_{i:02d}.json'
        model_path=folder/f'component_{i:02d}.json.gz'
        row=json.loads(row_path.read_bytes())
        if row['component']!=i or row['models_SHA256']!=saved.sha(model_path):
            raise ValueError('complete ordered model/fingerprint pair required')
        payload=json.loads(gzip.decompress(model_path.read_bytes()))
        if (payload['component']!=i or payload['source_binding']!=binding
                or len(payload['coefficients'])!=198+dimension*198+1
                or row['base_residuals_subtracted'] is not False):
            raise ValueError('same complete physical component model required')
        selected.append((row_path,model_path,row))
        provenance.append(dict(component=i,shard='low' if i<21 else 'middle' if i<41 else 'high',record_SHA256=saved.sha(row_path),
                               models_SHA256=row['models_SHA256']))
    # Do not publish a partial assembly if a source is missing or invalid.
    out.mkdir(parents=True)
    out.with_suffix('.terms').mkdir(parents=True)
    (out.with_suffix('.terms')/'sources.json').write_bytes(source_bytes)
    for row_path,model_path,row in selected:
        (out/row_path.name).write_bytes(row_path.read_bytes())
        (out/model_path.name).write_bytes(model_path.read_bytes())
    result={**template,'components':list(range(61)),'records':[row for _,_,row in selected],
            'all_61_velocity_components_certified':True,
            'component_shard_assembly':dict(evaluator_SHA256=saved.sha(Path(__file__)),
                sources=provenance,high_record_SHA256=saved.sha(high/'record.json'),
                middle_record_SHA256=saved.sha(middle/'record.json'),
                coefficients_copied_byte_identically=True,coefficient_arithmetic_recomputed=False)}
    (out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(family=result['family'],components=61,record_SHA256=saved.sha(out/'record.json'),Gate7_closed=False)))


def main():
    parser=argparse.ArgumentParser()
    for key in ('low','middle','high','out'): parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();evaluate(args.low.resolve(),args.middle.resolve(),args.high.resolve(),args.out.resolve())


if __name__=='__main__': main()

"""Preserve reproduced Layer-B results and the explicit failed kappa screen."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import certify_n12_gate7_local_physical_tube as parent
inputs=parent.inputs


def run(work,atlas,out):
    if out.exists():raise FileExistsError('fresh checkpoint directory required')
    atlas_record=json.loads((atlas/'certificate.json').read_bytes())
    atlas_receipt=json.loads((atlas/'reproduction.json').read_bytes())
    if (not atlas_record['complete_physical_tube_cover_certified'] or not atlas_receipt['byte_identical']
            or atlas_receipt['certificate_SHA256']!=inputs.sha(atlas/'certificate.json')):
        raise ValueError('complete reproduced atlas required')
    names=['authority','interval13_boxed_remainder','interval13_inherited_remainder']
    names += [f'interval13_{method}_{site}' for method in ('ballrate','inherited2rate') for site in ('left','middle','right')]
    data={};aliases={};pairs=[]
    for name in names:
        a=work/f'{name}_first.json';b=work/f'{name}_repeat.json'
        if a.read_bytes()!=b.read_bytes():raise ValueError(f'independent reproduction failed: {name}')
        record=json.loads(a.read_bytes())
        for p,h in record['source_SHA256'].items():
            if inputs.sha(Path(p))!=h:raise ValueError(f'changed input: {p}')
        for path in (a,b):data[path.name]=path.read_bytes();aliases[str(path.resolve())]=path.name
        pairs.append(dict(name=name,SHA256=inputs.sha(a),independent_recomputation=True,byte_identical=True))
    best=json.loads(data['interval13_inherited_remainder_first.json'])
    if best['enclosure_viable']:raise ValueError('this checkpoint schema is for a failed enclosure screen')
    rate_bounds=[json.loads(data[f'interval13_inherited2rate_{site}_first.json'])['mixed_norm_upper'] for site in ('left','middle','right')]
    result=dict(algorithm='LAYER_B_INTERVAL13_PHYSICAL_ATLAS_AND_REMAINDER_CHECKPOINT_V1',
        Layer_A_frozen_commit='452c80a7',Layer_A_recomputed=False,
        complete_physical_tube_intervals=[13],remaining_requested_intervals=[14,15,16,17,18],
        original_physical_radii_changed=False,new_endpoints=0,
        all_states_in_actual_augmented_HS_dense_image_covered=True,
        chart_local_overlap_handoff_proved=True,physical_rate_defined_on_entire_interval13_image=True,
        complete_99_output_rate_mixed_bounds_at_HS_sites=rate_bounds,
        complete_signed_interval13_remainder_enclosed=True,nonaffine_midpoint_incidence_included=True,
        signed_booked_function_subtracted=True,causal_destination_nodes=357,
        isolated_interval13_kappa_upper=best['isolated_interval_kappa_upper'],
        interval13_remainder_enclosure_viable=False,global_kappa_L=None,global_kappa_T=None,
        continuation='Preserve shared state/direction coefficients and mixed monomials through the implicit solves, descriptor normalization, actual midpoint incidence, booked subtraction and output contraction; retest interval 13 before extending 14--18.',
        no_physical_failure_or_decay_inferred=True,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        numerical_reproduction=pairs,
        atlas_certificate_SHA256=inputs.sha(atlas/'certificate.json'),
        artifact_input_aliases=aliases,
        source_SHA256={str(p.resolve()):inputs.sha(p) for p in (Path(__file__),atlas/'certificate.json',atlas/'reproduction.json')})
    out.mkdir(parents=True)
    for name,raw in data.items():(out/name).write_bytes(raw)
    (out/'checkpoint.json').write_bytes(inputs.encode(result))
    (out/'reproduction.json').write_bytes(inputs.encode(dict(checkpoint_SHA256=inputs.sha(out/'checkpoint.json'),
        all_numerical_pairs_byte_identical=True,independent_numerical_pairs=len(pairs),Gate7_closed=False)))
    print(json.dumps(dict(complete_tube_intervals=[13],enclosure_viable=False,numerical_pairs=len(pairs))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True)
    p.add_argument('--atlas',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.work.resolve(),a.atlas.resolve(),a.out.resolve())

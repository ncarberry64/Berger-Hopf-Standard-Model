"""Hash-bound authority inventory for the frozen 13--19 atlas; no producer runs."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import derive_n12_gate7_shared_connecting_hessian as inputs


def run(evidence,out):
    if out.exists():raise FileExistsError('fresh output required')
    base=evidence/'artifacts/flagship_integration';sources={};rows=[]
    ledger=ROOT/'artifacts/flagship_integration/gate7_global_checkpoint_20260923/current_history_budget.json'
    radii=[r['radius']['exact'] for r in json.loads(ledger.read_bytes())['rows']]
    for n in range(13,20):
        domains=[(f'endpoint_{n:03d}','.coupled_normalized_physical_value_work',
                  '.coupled_endpoint_uniform_df_work')]
        if n<19:domains.append((f'interval_{n:03d}','.coupled_midpoint_physical_value_work',
                               '.coupled_midpoint_uniform_df_work'))
        for name,value_kind,df_kind in domains:
            value,_=inputs.import_domain(base/value_kind/name,'value.npz',sources)
            derivative,_=inputs.import_domain(base/df_kind/name,'derivative.npz',sources)
            v,d=value['report'],derivative['report']
            if (not v['validation_passed'] or not v['uniform_physical_value_enclosed']
                    or not v['positive_physical_G_norm'] or not d['validation_passed']
                    or not d['uniform_physical_first_derivatives_enclosed']
                    or not d['full_descriptor_direction_included'] or d['weighted_augmented_basis_columns']!=99):
                raise ValueError('complete frozen physical value/DF authority required')
            rows.append(dict(domain=name,scope=d['scope'],physical_value=True,physical_first_derivative=True,
                full_descriptor_direction=True,physical_second_derivative=d['uniform_physical_hessians_enclosed'],
                higher_remainder=d['higher_remainder_enclosed'],
                authority_limit='Original recorded domain only; no off-center extension by inference.'))
    prototypes=[]
    for folder in ('gate7_mixed_eigenline_20260923','gate7_mixed_response_20260923','gate7_complete_rate_20260923'):
        p=ROOT/'artifacts/flagship_integration'/folder
        header=json.loads((p/'reproduction.json').read_bytes())
        digest=inputs.sha(p/'certificate.json')
        # Existing endpoint-19 receipts use first_SHA256 (or canonical certificate_SHA256).
        if not header.get('byte_identical') or digest not in (
                header.get('first_SHA256'),header.get('certificate_SHA256'),header.get('canonical_first_SHA256')):
            raise ValueError(f'prototype receipt binding failed: {folder}')
        for f in ('certificate.json','reproduction.json'):sources[str((p/f).resolve())]=inputs.sha(p/f)
        prototypes.append(dict(package=folder,scope='FROZEN_ORIGINAL_ENDPOINT19_DOMAIN_ONLY',SHA256=digest))
    for p in (ledger,Path(__file__)):sources[str(p.resolve())]=inputs.sha(p)
    result=dict(algorithm='FROZEN_PHYSICAL_RATE_AUTHORITY_13_TO_19_V1',radius_exact=radii,domains=rows,
        endpoint19_prototypes=prototypes,missing=['Complete local off-center physical-tube domain authority',
        'Same-domain mixed physical-rate jets with full descriptor and normalization',
        'Actual first/second HS incidence and all 99 output contractions',
        'Signed booked subtraction, interval-14 entry mask when applicable, and causal aggregation'],
        inherited_calculations_rerun=False,Layer_A_frozen_commit='452c80a7',
        source_SHA256=sources,Gate7_closed=False,kappa_L=None,kappa_T=None)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as f:f.write(inputs.encode(result))
    print(json.dumps(dict(verified_value_and_DF_domains=len(rows),mixed_rate_prototypes=1,Gate7_closed=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.out.resolve())

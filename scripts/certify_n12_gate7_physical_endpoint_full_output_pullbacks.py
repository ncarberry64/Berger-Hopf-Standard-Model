"""Attach complete physical midpoint DF incidence to selected endpoint Hessians."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_physical_endpoint_hessian_pullbacks as old
import certify_n12_gate7_physical_incidence_causal_envelope as incidence

RESULT=ROOT/'artifacts/flagship_integration/.physical_endpoint_full_output_pullback_work'


def build_point(node):
    arrays,payload=old.build_point(node);components=[];corrections=[];sources=dict(payload['inputs'])
    for index,(interval,label,slot) in enumerate(old.incident_slots(node)):
        record,incidence_arrays,binding=incidence.load_incidence(interval)
        incidence.first.merge_sources(sources,binding)
        output=arrays['output_maps'][index]
        if not np.array_equal(output,incidence_arrays['stored_output_maps'][slot]):
            raise RuntimeError('endpoint physical Hessian and physical incidence output maps differ')
        delta=record['output_map_error_bounds'][label]['operator_error_upper']
        correction,bound=old.pullback.pullback_with_frozen_output(output,arrays['error_mid'],arrays['error_radius'],np.eye(74),0.,delta)
        corrections.append(correction)
        components.append(dict(interval=interval,output_label=label,combined_physical_output_error_upper=delta,
            physical_incidence_point_SHA256=old.producer.campaign.sha(incidence.incidence.RESULT/f'midpoint_{interval:03d}.json'),
            physical_error_pullback=bound,single_endpoint_quadratic_coefficient_upper=bound['total_error_pullback_frobenius_upper']))
    arrays['correction_centers']=np.asarray(corrections)
    for path in (Path(__file__),Path(incidence.__file__),incidence.THEORY):
        incidence.first.merge_sources(sources,{path.relative_to(ROOT).as_posix():old.producer.campaign.sha(path)})
    incidence.prior.coordinate._verified_inputs({'inputs':sources})
    payload.update(scope='SELECTED_PHYSICAL_ENDPOINT_HESSIAN_ERROR_WITH_PHYSICAL_MIDPOINT_DF_AND_FROZEN_OUTPUT_CONSTRUCTION',
        inputs=sources,components=components,physical_midpoint_DF_incidence_error_enclosed=True,
        combined_output_bound_replaces_stored_construction_bound=True,
        operand_binary64_SHA256={k:old.producer.campaign.array_sha(v) for k,v in arrays.items()})
    return arrays,payload


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--nodes',required=True);args=parser.parse_args()
    RESULT.mkdir(parents=True,exist_ok=True)
    for node in old.producer.first.parse_nodes(args.nodes):
        arrays,payload=build_point(node);stem=RESULT/f'endpoint_{node:03d}'
        np.savez_compressed(stem.with_suffix('.npz'),**arrays)
        payload['data_SHA256']=old.producer.cache.file_sha(stem.with_suffix('.npz'))
        incidence.prior.coordinate._verified_inputs({'inputs':payload['inputs']})
        stem.with_suffix('.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(node=node,incident_coefficients=[r['single_endpoint_quadratic_coefficient_upper'] for r in payload['components']])),flush=True)


if __name__=='__main__':main()

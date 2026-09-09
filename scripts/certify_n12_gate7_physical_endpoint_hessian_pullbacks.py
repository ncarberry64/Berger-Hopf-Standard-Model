"""Map complete selected endpoint Hessian errors into both incident intervals."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_physical_endpoint_hessian_errors as producer
import certify_n12_gate7_physical_first_causal_envelope as causal
from bhsm.interface import physical_hessian_frozen_pullback as pullback

RESULT=ROOT/'artifacts/flagship_integration/.physical_endpoint_hessian_pullback_work'
COMMON=None


def incident_slots(node):
    if type(node) is not int or not 1<=node<=370:raise ValueError('noninitial endpoint node 1..370 required')
    return [(node-1,'right',1)]+([(node,'left',0)] if node<370 else [])


def common():
    global COMMON
    if COMMON is None:
        report=json.loads(causal.prior.output.RESULT.read_text())
        if (report.get('artifact')!='BHSM_N12_GATE7_FROZEN_OUTPUT_MAP_CONSTRUCTION'
                or report.get('validation_passed') is not True
                or report.get('coverage')!=dict(intervals=370,nodes=371,complete=True)
                or [r['interval'] for r in report.get('rows',[])]!=list(range(370))):
            raise RuntimeError('complete frozen output-map certificate required')
        inputs=causal.prior.coordinate._verified_inputs(report).copy();c=producer.campaign.center
        with np.load(c.JACOBIAN.with_suffix('.npz')) as source:tangents=source['endpoint_physical_tangent_action'].copy()
        with np.load(c.PRECONDITIONER.with_suffix('.npz')) as source:right=source['reduced_right_Newton_blocks'].copy()
        with np.load(c.ENDPOINT.with_suffix('.npz')) as source:times=source['collocation_arc_parameters'].copy()
        with np.load(c.AMBIENT.with_suffix('.npz')) as source:ambient=source['ambient_DF_mid'].copy()
        COMMON=dict(report=report,inputs=inputs,tangents=tangents,right=right,times=times,ambient=ambient)
    return COMMON


def build_point(node):
    loaded=common();values,binding,fingerprint=producer.load_inputs(node);directory=producer.point_directory(node)
    if json.loads((directory/'binding.json').read_text())!=binding:raise RuntimeError('physical endpoint row binding changed')
    mid,radius,records=producer.cache.assemble_rows(directory,fingerprint,dimension=74)
    inputs=loaded['inputs'].copy();causal.merge_sources(inputs,binding['sources'])
    for path in (Path(__file__),Path(pullback.__file__),Path(pullback.physical.__file__),Path(pullback.arithmetic.__file__),
                 causal.prior.output.RESULT,directory/'binding.json'):
        causal.merge_sources(inputs,{path.relative_to(ROOT).as_posix():producer.campaign.sha(path)})
    for row in range(74):
        for extension in ('npz','json'):
            path=directory/f'row_{row:03d}.{extension}'
            causal.merge_sources(inputs,{path.relative_to(ROOT).as_posix():producer.campaign.sha(path)})
    corrections=[];components=[];outputs=[]
    for interval,label,slot in incident_slots(node):
        h=float(loaded['times'][interval+1]-loaded['times'][interval])
        test=producer.cert._frame(loaded['tangents'][interval+1],producer.cert.TEST_DESCRIPTOR_SCALE).T
        b=-np.linalg.solve(loaded['right'][interval],test);incidence=b@loaded['ambient'][interval]
        maps=np.asarray([h*b/6+h*h*incidence/12,h*b/6-h*h*incidence/12,2*h*b/3])
        output=maps[slot];record=loaded['report']['rows'][interval]
        matches=[r for r in record['components'] if r['kind']=='endpoint' and r['index']==node]
        if len(matches)!=1 or matches[0]['output_map_SHA256']!=causal.prior.maps._array_hash(output):
            raise RuntimeError('endpoint incident output map differs from its certificate')
        delta=record['output_map_error_bounds']['maps'][label]['operator_error_upper']
        correction,bound=pullback.pullback_with_frozen_output(output,mid,radius,np.eye(74),0.,delta)
        outputs.append(output);corrections.append(correction)
        components.append(dict(interval=interval,output_label=label,output_map_error_upper=delta,
            output_map_SHA256=causal.prior.maps._array_hash(output),physical_error_pullback=bound,
            single_endpoint_quadratic_coefficient_upper=bound['total_error_pullback_frobenius_upper']))
    arrays=dict(error_mid=mid,error_radius=radius,output_maps=np.asarray(outputs),correction_centers=np.asarray(corrections))
    causal.prior.coordinate._verified_inputs({'inputs':inputs})
    return arrays,dict(node=node,scope='SELECTED_PHYSICAL_ENDPOINT_HESSIAN_ERROR_THROUGH_FROZEN_STORED_DF_OUTPUT_MAPS',
        rows=74,direction_pairs=2775,physical_source_binding=binding,physical_row_fingerprint=fingerprint,
        row_records=records,inputs=inputs,components=components,
        operand_binary64_SHA256={k:producer.campaign.array_sha(v) for k,v in arrays.items()},
        physical_Hessian_at_this_endpoint_enclosed=True,exact_normalized_projector_direction_errors_included=True,
        frozen_output_construction_and_physical_error_cross_terms_included=True,
        physical_midpoint_DF_incidence_error_enclosed=False,all_endpoints_covered=False,
        causal_transport_of_endpoint_errors_enclosed=False,physical_frame_error_enclosed=False,
        neighborhood_remainder_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--nodes',required=True);args=parser.parse_args()
    RESULT.mkdir(parents=True,exist_ok=True)
    for node in producer.first.parse_nodes(args.nodes):
        arrays,payload=build_point(node);stem=RESULT/f'endpoint_{node:03d}'
        np.savez_compressed(stem.with_suffix('.npz'),**arrays)
        payload['data_SHA256']=producer.cache.file_sha(stem.with_suffix('.npz'))
        causal.prior.coordinate._verified_inputs({'inputs':payload['inputs']})
        stem.with_suffix('.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(node=node,incident_coefficients=[r['single_endpoint_quadratic_coefficient_upper'] for r in payload['components']])),flush=True)


if __name__=='__main__':main()

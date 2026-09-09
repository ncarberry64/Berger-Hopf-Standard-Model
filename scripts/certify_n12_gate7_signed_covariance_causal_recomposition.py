"""Recompose complete signed covariance balls without recursive interval wrapping."""
import json
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_stored_covariance_formation as formation
from bhsm.interface import signed_covariance_causal_bounds as recomposition

center=formation.center
RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_SIGNED_COVARIANCE_CAUSAL_RECOMPOSITION.json'
THEORY=ROOT/'theory/n12_gate7_signed_covariance_causal_recomposition.md'


def _verify_formation(record):
    if (record.get('artifact')!='BHSM_N12_GATE7_STORED_COVARIANCE_FORMATION'
            or record.get('validation_passed') is not True
            or record.get('scope')!='EXACT_RECONSTRUCTED_TENSOR_COVARIANCES_ENCLOSED_ABOUT_SAVED_CENTER_ARRAYS'
            or record.get('coverage')!=dict(intervals=370,local_covariances=1110,adjacent_covariances=370,complete=True)
            or record.get('data_SHA256')!=center._sha(formation.DATA)):
        raise RuntimeError('Complete unchanged covariance formation certificate required')
    inputs=record.get('inputs',{})
    for path in (center.DATA,center.PARTITION.with_suffix('.npz'),Path(center.component.__file__)):
        if path.relative_to(ROOT).as_posix() not in inputs:
            raise RuntimeError('Covariance certificate lacks center/axis bindings')
    formation.assembly.coordinate._verified_inputs(record)
    return inputs


def _worker(nodes):
    with np.load(center.DATA) as d:
        local=d['local_pair_output_covariances'].copy()
        adjacent=d['adjacent_right_left_output_cross_covariances'].copy()
        maps=d['causal_maps_center'].copy()
    with np.load(formation.DATA) as d:
        local_radius=d['local_pair_covariance_radius_upper'].copy()
        adjacent_radius=d['adjacent_covariance_radius_upper'].copy()
    axes=center.component._load_axes()
    if maps.shape!=(370,74,74):raise RuntimeError('Complete same-center maps required')
    def progress(node,l,t):
        if node%30==0:
            print(json.dumps(dict(certified_covariance_node=node,longitudinal=l,transverse=t)),flush=True)
    return recomposition.causal_covariance_bounds(local,local_radius,adjacent,adjacent_radius,
                                                 maps,axes,progress,target_nodes=nodes)


def _merge_chunks(chunks):
    longitudinal=[0.]+[None]*370
    transverse=[0.]+[None]*370
    seen=set()
    for chunk in chunks:
        for n in chunk['coverage']['target_nodes']:
            if n in seen or not isinstance(n,int) or not 1<=n<=370:
                raise RuntimeError('Duplicated or invalid covariance target')
            seen.add(n)
            for name,target in (('longitudinal_coefficient_upper',longitudinal),
                                ('transverse_coefficient_upper',transverse)):
                value=chunk[name][n]
                if value is None or not np.isfinite(value) or value<0:
                    raise RuntimeError('Missing or invalid node coefficient')
                target[n]=value
    if seen!=set(range(1,371)):
        raise RuntimeError('Incomplete covariance target coverage')
    return dict(longitudinal_coefficient_upper=longitudinal,transverse_coefficient_upper=transverse,
                maximum_coefficients_upper=[max(longitudinal),max(transverse)],
                coverage=dict(target_nodes=list(range(1,371)),complete=True),
                arithmetic_precision_bits=512,stored_axis_unit_norm_assumed=False)


def build_payload(workers=6):
    if isinstance(workers,bool) or not isinstance(workers,int) or not 1<=workers<=6:
        raise ValueError('One to six numerical workers required')
    record=json.loads(formation.RESULT.read_text())
    inputs=dict(_verify_formation(record))
    for path in (Path(__file__).resolve(),THEORY,formation.RESULT,formation.DATA,
                 Path(formation.__file__),Path(recomposition.__file__),
                 Path(recomposition.interval_matrix.__code__.co_filename),
                 Path(recomposition._exact_matrix.__code__.co_filename),
                 Path(recomposition._real_binary64.__code__.co_filename)):
        name,digest=path.relative_to(ROOT).as_posix(),center._sha(path)
        if name in inputs and inputs[name]!=digest:
            raise RuntimeError('Conflicting recomposition source binding')
        inputs[name]=digest
    with np.load(center.DATA) as d:maps=d['causal_maps_center'].copy()
    axes=center.component._load_axes()
    groups=[list(range(i+1,371,workers)) for i in range(workers)]
    if workers==1:
        chunks=[_worker(groups[0])]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures=[pool.submit(_worker,nodes) for nodes in groups]
            chunks=[future.result() for future in as_completed(futures)]
    result=_merge_chunks(chunks)
    formation.assembly.coordinate._verified_inputs({'inputs':inputs})
    return dict(artifact='BHSM_N12_GATE7_SIGNED_COVARIANCE_CAUSAL_RECOMPOSITION',
        status='SIGNED_COVARIANCE_RECOMPOSITION_ENCLOSED',
        scope='RECONSTRUCTED_LOCAL_TENSOR_RESPONSE_THROUGH_EXACT_STORED_CAUSAL_MAPS_AND_AXES',
        coverage=dict(intervals=370,nodes=371,complete=True),inputs=inputs,recomposition=result,
        coefficients=result['maximum_coefficients_upper'],
        causal_maps_SHA256=formation.assembly._array_hash(maps),
        axes_SHA256=formation.assembly._array_hash(axes),
        validation_passed=True,claim_boundary=dict(covariance_formation_and_reconciliation_enclosed=True,
            causal_covariance_propagation_enclosed=True,exact_stored_axis_projection_enclosed=True,
            stored_axis_unit_norm_assumed=False,local_tensor_assembly_errors_already_added=False,
            physical_operand_errors_enclosed=False,physical_Hessian_error_enclosed=False,
            neighborhood_remainder_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=6)
    args=parser.parse_args()
    payload=build_payload(args.workers)
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(coefficients=payload['coefficients'],validation_passed=payload['validation_passed'])),flush=True)


if __name__=='__main__':main()

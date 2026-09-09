"""Enclose reconstructed tensor covariances about the saved center arrays."""
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_stored_pullback_assembly as assembly
from bhsm.interface import stored_covariance_enclosure as covariance

center=assembly.center
RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_STORED_COVARIANCE_FORMATION.json'
DATA=RESULT.with_suffix('.npz')
THEORY=ROOT/'theory/n12_gate7_stored_covariance_formation.md'


def _assembly_rows(record):
    if (record.get('artifact')!='BHSM_N12_GATE7_STORED_PULLBACK_ASSEMBLY'
            or record.get('validation_passed') is not True
            or record.get('scope')!='RECONSTRUCTED_LOCAL_TENSOR_ASSEMBLY_THROUGH_EXACT_STORED_CAUSAL_MAPS_ONLY'
            or record.get('coverage')!=dict(intervals=370,nodes=371,complete=True)):
        raise RuntimeError('Complete reconstructed assembly certificate required')
    rows=record.get('rows',[])
    if len(rows)!=370 or [r.get('interval') for r in rows]!=list(range(370)):
        raise RuntimeError('All 370 ordered assembly rows required')
    return rows


def _verify_local_tensor(local,row):
    if assembly._array_hash(local)!=row.get('local_tensor_SHA256'):
        raise RuntimeError('Local tensor differs from its assembly error certificate')


def build_payload():
    record=json.loads(assembly.RESULT.read_text())
    rows=_assembly_rows(record)
    inputs=dict(assembly.coordinate._verified_inputs(record))
    for path in (Path(__file__).resolve(),THEORY,assembly.RESULT,Path(assembly.__file__),
                 Path(covariance.__file__),Path(covariance._gamma.__code__.co_filename),
                 Path(covariance._real_binary64.__code__.co_filename)):
        name,digest=path.relative_to(ROOT).as_posix(),center._sha(path)
        if name in inputs and inputs[name]!=digest:
            raise RuntimeError('Conflicting covariance source binding')
        inputs[name]=digest
    with np.load(center.DATA) as d:
        saved_local=d['local_pair_output_covariances'].copy()
        saved_adjacent=d['adjacent_right_left_output_cross_covariances'].copy()
    with np.load(center.JACOBIAN.with_suffix('.npz')) as d:
        tangents=d['endpoint_physical_tangent_action'].copy()
        midtangents=d['midpoint_physical_tangent_action'].copy()
    with np.load(center.PRECONDITIONER.with_suffix('.npz')) as d:right=d['reduced_right_Newton_blocks'].copy()
    with np.load(center.ENDPOINT.with_suffix('.npz')) as d:times=d['collocation_arc_parameters'].copy()
    with np.load(center.AMBIENT.with_suffix('.npz')) as d:ambient=d['ambient_DF_mid'].copy()
    midaxes=center.center._load_inputs()['midpoint'][3]
    local_radius=np.zeros_like(saved_local)
    adjacent_radius=np.zeros_like(saved_adjacent)
    produced=[]
    previous_right=None
    original=center._covariance_blocks

    def capture(local):
        nonlocal previous_right
        i=len(produced)
        if i>=370:raise RuntimeError('Unexpected extra local covariance')
        _verify_local_tensor(local,rows[i])
        blocks=center._pair_blocks(local)
        flat=[v.reshape(74,-1) for v in blocks]
        for j in range(3):
            local_radius[i,j]=covariance.product_radius_about_stored(flat[j],flat[j].T,saved_local[i,j])
        if previous_right is None:
            if np.any(saved_adjacent[i]!=0):
                raise RuntimeError('Initial adjacent covariance must be exactly zero')
        else:
            adjacent_radius[i]=covariance.product_radius_about_stored(previous_right,flat[0].T,saved_adjacent[i])
        previous_right=flat[2].copy()
        produced.append(dict(interval=i,local_tensor_SHA256=rows[i]['local_tensor_SHA256'],
            saved_local_covariances_SHA256=assembly._array_hash(saved_local[i]),
            saved_adjacent_covariance_SHA256=assembly._array_hash(saved_adjacent[i]),
            maximum_local_covariance_entry_radius_upper=float(np.max(local_radius[i])),
            maximum_adjacent_covariance_entry_radius_upper=float(np.max(adjacent_radius[i]))))
        if (i+1)%50==0:
            print(json.dumps(dict(certified_covariance_intervals=i+1)),flush=True)
        return original(local)

    center._covariance_blocks=capture
    try:
        center._local_covariances(center.component._load_axes(),midaxes,tangents,midtangents,
                                 times,right,ambient,use_supplemental=True)
    finally:
        center._covariance_blocks=original
    if len(produced)!=370:raise RuntimeError('Incomplete local covariance traversal')
    assembly.coordinate._verified_inputs({'inputs':inputs})
    np.savez_compressed(DATA,local_pair_covariance_radius_upper=local_radius,
                        adjacent_covariance_radius_upper=adjacent_radius)
    return dict(artifact='BHSM_N12_GATE7_STORED_COVARIANCE_FORMATION',
        scope='EXACT_RECONSTRUCTED_TENSOR_COVARIANCES_ENCLOSED_ABOUT_SAVED_CENTER_ARRAYS',
        coverage=dict(intervals=370,local_covariances=1110,adjacent_covariances=370,complete=True),
        inputs=inputs,rows=produced,data=DATA.relative_to(ROOT).as_posix(),data_SHA256=center._sha(DATA),
        maximum_local_covariance_entry_radius_upper=float(np.max(local_radius)),
        maximum_adjacent_covariance_entry_radius_upper=float(np.max(adjacent_radius)),
        validation_passed=True,claim_boundary=dict(local_covariance_formation_rounding_enclosed=True,
            reconstructed_to_saved_covariance_difference_enclosed=True,
            causal_covariance_propagation_rounding_enclosed=False,
            physical_operand_errors_enclosed=False,physical_Hessian_error_enclosed=False,
            neighborhood_remainder_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False))


def main():
    payload=build_payload()
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:payload[k] for k in ('maximum_local_covariance_entry_radius_upper',
        'maximum_adjacent_covariance_entry_radius_upper','validation_passed')}),flush=True)


if __name__=='__main__':main()

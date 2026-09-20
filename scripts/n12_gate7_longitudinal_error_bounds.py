"""Replay source-bound implicit error intersections before transport use."""
import json
from pathlib import Path
from flint import arb, arb_mat
import bhsm.interface.directional_error_refinement as arithmetic
import bhsm.interface.base_residual_cancellation as cancellation
import evaluate_n12_gate7_coupled_residual_saved as saved
ROOT=Path(__file__).resolve().parents[1]


def load_direction(path, parent_path, adjoint_path, refined_path, axis, error_map, verified):
    record=json.loads(path.read_bytes())
    parent=json.loads((parent_path/'record.json').read_bytes())
    guard=record['guarded_input_SHA256']
    if (record['algorithm']!='LONGITUDINAL_DIRECTIONAL_ERROR_RESIDUAL_INTERSECTION_V2'
            or record['family']!=parent['family']
            or record['original_state_groups']!=parent['original_state_groups']
            or record['physical_axis_exact']!=[str(v.fmpq()) for v in axis.entries()]
            or guard['parent']!=saved.sha(parent_path/'record.json')
            or guard['adjoint']!=saved.sha(adjoint_path)
            or guard['refined']!=saved.sha(refined_path)
            or guard['arithmetic']!=saved.sha(Path(arithmetic.__file__))
            or guard['base_cancellation']!=saved.sha(Path(cancellation.__file__))
            or guard['evaluator']!=saved.sha(ROOT/'scripts/refine_n12_gate7_retained_axis_directional_errors.py')
            or guard['residual_producer']!=saved.sha(ROOT/'scripts/reconstruct_n12_gate7_directional_residuals.py')
            or any(record['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items())
            or any(record.get(k) is not True for k in (
                'every_iteration_preserves_original_solution_graph','original_physical_domain_unchanged',
                'base_residual_remainders_included','directional_residual_remainders_included'))):
        raise ValueError('unchanged source-bound longitudinal error refinement required')
    original=error_map*axis
    initial=[abs(v).upper() for v in original.entries()]
    if [str(v.fmpq()) for v in initial]!=[v['exact'] for v in record['original_axis_error_bounds']]:
        raise ValueError('refinement must start from the identical original physical inclusion')
    forcing=[arb(v['exact']) for v in record['forcing']]
    coupling=arb_mat([[arb(v['exact']) for v in row] for row in record['coupling']])
    refined=arithmetic.intersect_majorant(initial,forcing,coupling,record['iterations'])
    if [str(v.fmpq()) for v in refined]!=[v['exact'] for v in record['refined_axis_error_bounds']]:
        raise ArithmeticError('outward majorant intersection replay failed')
    return arb_mat(124,1,[v.intersection(arb(0,b)) for v,b in zip(original.entries(),refined,strict=True)])

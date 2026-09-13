"""Refine the paired trial pilot by splitting uncertain midpoint directions."""
from pathlib import Path
import diagnose_n12_gate7_directed_trial_hs_column as base
from bhsm.interface import directional_variation_split as split

ORIGINAL_ALGORITHM = base.ALGORITHM
base.ALGORITHM = 'CENTER_SPLIT_DIRECTED_FROZEN_TRIAL_HS_COLUMN_ARB512_V1'
base.THEORY = base.ROOT/'theory/n12_gate7_split_directed_trial_hs_column.md'
original_evaluate = base.directed.evaluate
original_assemble = base.assemble


def validate_directed(record, stage, side, args):
    expected = ORIGINAL_ALGORITHM if stage == 'endpoint' else base.ALGORITHM
    report = record.get('report', {})
    if (record.get('algorithm') != expected or record.get('stage') != stage
            or record.get('side') != side or record.get('interval') != args.interval
            or record.get('trial_column') != args.column
            or report.get('complete_original_directional_variation') is not True
            or report.get('verified_point_derivative_contained') is not True):
        raise ValueError('matching paired endpoint or center-split midpoint evidence required')


def evaluate(engine, source, directions):
    if 'raw_center' not in source:
        raise ValueError('this variant consumes the already paired endpoint directions')
    reference, derivative = base.reader.read_derivative(None, source['index'], 'midpoint')
    if any(source['binding']['files'].get(name) != digest
           for name, digest in reference['binding']['files'].items()):
        raise ValueError('linear tail requires the identical paired midpoint derivative')
    base.bind(source, Path(__file__), Path(split.__file__))
    center, tail = split.split_directions(directions)
    arrays, proof = original_evaluate(engine, source, base.array(center))
    action, correction = split.enclose_split_action(arrays['derivative'], derivative, tail)
    result = {'center_'+name: value for name, value in arrays.items()}
    result.update(derivative=base.array(action), directions=directions,
                  direction_tail=base.array(tail), tail_action=base.array(correction),
                  point_derivative=arrays['point_derivative'])
    if not all(a.contains(b) for a, b in zip(result['derivative'].flat, result['point_derivative'].flat)):
        raise ArithmeticError('center-split uniform action must contain the verified point action')
    proof.update(direction_split_by_exact_linearity=True, full_uniform_derivative_tail_used=True,
                 centered_variation_proofs_apply_to_direction_centers=True,
                 center_action_maximum_radius=float(max(v.rad() for v in arrays['derivative'].flat)),
                 tail_action_maximum_radius=float(max(v.rad() for v in correction.entries())))
    return result, proof


def assemble(args, source):
    source, arrays, report = original_assemble(args, source)
    base.bind(source, Path(__file__), Path(split.__file__))
    report['paired_center_split_midpoint_directions'] = True
    return source, arrays, report


base.validate_directed = validate_directed
base.directed.evaluate = evaluate
base.assemble = assemble
if __name__ == '__main__':
    base.main()

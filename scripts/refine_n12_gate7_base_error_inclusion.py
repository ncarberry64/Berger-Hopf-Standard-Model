"""Intersect base implicit-error inclusions on the unchanged physical domain.

For G=c+A theta+C eta+e=0 and |eta|<=1, any exact point matrix P gives
|eta| <= |Pc+PA theta| + |I-PC| |eta| + |P|r. No contraction hypothesis
is used. Finite outward intersections preserve the original implicit graph.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import gzip
import json
from pathlib import Path
import sys
from flint import arb, arb_mat, ctx
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain
from bhsm.interface.shared_parameter_residual import linear_support
from bhsm.interface.directional_error_refinement import intersect_majorant
import bhsm.interface.directional_error_refinement as refinement
import bhsm.interface.shared_action_taylor as state_arithmetic
from certify_n12_gate7_endpoint_vector_transport import restore, upper
import evaluate_n12_gate7_coupled_residual_saved as saved


def evaluate(folder):
    paths = dict(record=folder/'record.json', models=folder/'models.json.gz',
        evaluator=Path(__file__), refinement=Path(refinement.__file__),
        state_arithmetic=Path(state_arithmetic.__file__))
    hashes = {key:saved.sha(path) for key,path in paths.items()}
    record = json.loads(paths['record'].read_bytes())
    if (record.get('algorithm') != 'ORIGINAL_DOMAIN_BASE_IMPLICIT_RESIDUAL_VECTOR_V1'
            or record.get('all_base_components_certified') is not True
            or record.get('component_indices') != list(range(124))
            or record.get('models_SHA256') != hashes['models']
            or record['source_hashes']['arithmetic'] != hashes['state_arithmetic']
            or record.get('original_physical_domain_unchanged') is not True):
        raise ValueError('complete unchanged source-bound base equations required')
    n = record['state_dimension']-124
    if record['base_error_state_indices'] != list(range(n, n+124)):
        raise ValueError('the original trailing normalized base-error coordinates are required')
    groups = record['original_state_groups']
    if groups[-1] != [n, n+124, 'box']:
        raise ValueError('the original unit error box is required')
    domain = TaylorDomain(groups, n+124)
    rows = json.loads(gzip.decompress(paths['models'].read_bytes()))
    if len(rows) != 124 or len(record['rows']) != 124:
        raise ValueError('every base equation is required')
    models = []
    for i, encoded in enumerate(rows):
        if len(encoded) != n+126:
            raise ValueError('complete base residual coefficients required')
        v = [restore(pair) for pair in encoded]
        model = Taylor(domain, v[0], arb_mat(1, n+124, v[1:-1]), v[-1])
        if record['rows'][i]['component'] != i or str(model.support().fmpq()) != record['rows'][i]['support']['exact']:
            raise ArithmeticError('base residual support failed exact replay')
        models.append(model)
    C = arb_mat(124, 124, [g.a[0, n+j] for g in models for j in range(124)])
    P = C.mid().inv().mid()
    transported = P*arb_mat(124, n+1, [v for g in models for v in [g.c, *g.a.entries()[:n]]])
    absP = arb_mat(124, 124, [abs(v).upper() for v in P.entries()])
    tail = absP*arb_mat(124, 1, [g.r for g in models])
    defect = arb_mat(124, 124, [int(i == j) for i in range(124) for j in range(124)])-P*C
    coupling = arb_mat(124, 124, [abs(v).upper() for v in defect.entries()])
    forcing = [(abs(transported[i, 0]).upper()+linear_support(
        [transported[i, j+1] for j in range(n)], groups[:-1])+tail[i, 0]).upper() for i in range(124)]
    initial = [arb(1)]*124
    bounds = intersect_majorant(initial, forcing, coupling, iterations=64)
    if {key:saved.sha(path) for key,path in paths.items()} != hashes:
        raise ValueError('source changed during outward intersection')
    return dict(algorithm='BASE_ERROR_INCLUSION_FINITE_INTERSECTION_V1', family=record['family'],
        side=record.get('side', 'right'), original_state_groups=groups,
        base_error_state_indices=record['base_error_state_indices'], iterations=64,
        normalized_initial_bounds=[upper(v) for v in initial],
        normalized_refined_bounds=[upper(v) for v in bounds],
        forcing=[upper(v) for v in forcing],
        coupling=[[upper(coupling[i,j]) for j in range(124)] for i in range(124)],
        maximum_row_sum=upper(max(sum((coupling[i,j] for j in range(124)),arb(0)).upper() for i in range(124))),
        strictly_improved_coordinates=sum(bool(v < 1) for v in bounds),
        smallest_normalized_bound=upper(min(bounds)), largest_normalized_bound=upper(max(bounds)),
        every_iteration_preserves_original_solution_graph=True,
        original_physical_domain_unchanged=True, all_base_equations_and_remainders_retained=True,
        guarded_input_SHA256=hashes, source_hashes=record['source_hashes'],
        new_action_derivative_evaluations=0, contraction_assumption_used=False,
        full_history_certified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-residual', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    result = evaluate(args.base_residual)
    with args.out.open('xb') as f:
        f.write(saved.encoded(result))
    print(json.dumps({k:result[k] for k in ('family', 'strictly_improved_coordinates',
        'smallest_normalized_bound', 'largest_normalized_bound', 'maximum_row_sum')}), flush=True)


if __name__ == '__main__':
    main()

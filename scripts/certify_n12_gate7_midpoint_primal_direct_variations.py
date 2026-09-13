"""Enclose midpoint primal values from all 249 first-variation directions.

Capture three complete point solves of the retained rate graph, then
evaluate the complete uniform signed derivative equations directly. No physical Hessian is
claimed; contracted action calls above order three are rejected.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_coupled_midpoint_uniform_derivatives as engine
from bhsm.interface import affine_hs_midpoint_domain as grouped
import bhsm_immutable_input_hash_cache as cache
from bhsm.interface import centered_coupled_variation_residual as signed
from bhsm.interface.componentwise_weighted_response import enclose_response_rows
from bhsm.interface.midpoint_segment_family import validate_midpoint_segment_family
from bhsm.interface.ball_factored_arb_integrand import use_ball_factored_integrand


class PrimalCaptured(Exception):
    """Internal stop after the complete primal first-response solve."""


def evaluate(source):
    p = engine.p
    cert = p.values.cert
    paired = source['paired']
    center, full = paired['center'], paired['full']
    _, weights, descriptors, reference, _ = p.values.operands()
    w = np.array([arb(float(v)) for v in weights], dtype=object)
    residual = p.geometry.residual
    domain = engine.values.eq.midpoint.WORK/f"interval_{source['index']:03d}"/'domain.npz'
    with np.load(domain, allow_pickle=False) as a:
        raw_augmented = p.hs.restore_balls(a['raw_directions_mid_q'], a['raw_directions_rad_q'])
    if raw_augmented.shape != (99, 249):
        raise ArithmeticError('complete actual midpoint affine directions required')
    groups = source['groups']
    grouped.group_row_bounds(raw_augmented, groups)  # validate complete partition
    scaled = raw_augmented.copy()
    unit_groups = []
    for group in groups:
        scaled[:, group['start']:group['stop']] *= group['radius']
        unit_groups.append(dict(group, radius=arb(1)))
    directions = scaled.copy()
    directions[:98] *= w[:, None]
    raw = directions[:98]/w[:, None]
    value_module = engine.values
    eq = value_module.eq
    eigen = json.loads((eq.WORK/f"interval_{source['index']:03d}"/'record.json').read_bytes())
    value = json.loads((value_module.WORK/f"interval_{source['index']:03d}"/'record.json').read_bytes())
    family = validate_midpoint_segment_family(eigen['report'], value['report'])
    old_solve, old_eigen, old_action = cert._verified_solve, cert._eigenline, cert._contracted_action
    point_solutions, point_centers, checks, orders = [], [], [], set()

    def action(state, legs, maps):
        if len(legs) > 3:
            raise ArithmeticError('primal first variations must not request fourth/fifth action contractions')
        orders.add(len(legs))
        return old_action(state, legs, maps)

    def capture_point(matrix, rhs):
        result = old_solve(matrix, rhs)
        array = np.array(result.entries(), dtype=object).reshape(result.nrows(), result.ncols())
        point_solutions.append(array)
        point_centers.append(np.array([v.mid() for v in array.flat], dtype=object).reshape(array.shape))
        if len(point_solutions) == 3:
            raise PrimalCaptured()
        return result

    def run_until_capture(state, descriptor):
        try:
            cert._rate_enclosure(state, descriptor, weights, reference, directions)
        except PrimalCaptured:
            return
        raise ArithmeticError('expected complete third bordered solve was not captured')

    try:
        cert._contracted_action = action
        cert._verified_solve = capture_point
        with p.df.sparse.use_optimized_mixed(cert), use_ball_factored_integrand(cert, center):
            with p.hs.verified_eigenline(cert, checks, expected_index=24, normalize_proposal_center=True):
                run_until_capture(center, source['raw_center'][98])
    finally:
        cert._verified_solve, cert._contracted_action = old_solve, old_action
    if (len(checks) != 1 or not p.proof_valid(checks[0])
            or [a.shape for a in point_solutions] != [(62, 1), (62, 249), (62, 249)]):
        raise ArithmeticError('verified point family and all three complete solves required')
    print(json.dumps(dict(phase='PRIMAL_POINT_COMPLETE',directions=249)), flush=True)
    with p.df.sparse.use_optimized_mixed(cert), use_ball_factored_integrand(cert, full):
        maps = cert._arb_action_jets(full).dense_maps
    psi, lam, R = paired['eigenbox'][:61], paired['eigenbox'][-1], paired['rm']
    qw, rw, _, _ = cert.metric_data()
    solved, proofs, residuals = [source['response'][:, None].copy()], [], []
    slopes = None
    # Differentiate the same K response equations through their complete
    # signed preconditioned residuals. No unused unpreconditioned uniform
    # direction tensor is formed. The point anchors came from all three
    # original verified solves above.
    with p.df.sparse.use_optimized_mixed(cert), use_ball_factored_integrand(cert, full):
        for which in (1, 2):
            fixed = point_centers[which]
            if which == 1:
                res, slopes = signed.line_residual(action, full, psi, lam, R, fixed, raw, maps)
            else:
                res = signed.physical_response_residual(action, full, psi, lam, source['response'][:61],
                    source['response'][-1], solved[1][:61], slopes, R, fixed, qw, rw, weights, raw, maps)
            result = np.empty_like(fixed)
            rows = []
            for k in range(249):
                z = fixed[:, k].copy()
                z[-1] = -z[-1]
                result[:, k], proof = enclose_response_rows(z, res[:, k], paired['radii'], paired['variation'])
                result[-1, k] = -result[-1, k]
                rows.append(proof)
            if not all(a.contains(b) for a, b in zip(result.flat, point_solutions[which].flat, strict=True)):
                raise ArithmeticError('uniform primal first variations must contain verified point solves')
            solved.append(result)
            proofs.append(rows)
            residuals.append(res)
            print(json.dumps(dict(phase='DIRECT_PRIMAL_UNIFORM_VARIATION', solve=which, columns=249)), flush=True)
    if len(solved) != 3:
        raise ArithmeticError('complete primal variations required')
    point = p.hs.restore_balls(np.array(checks[0]['target_midpoints_rational']),
                               np.array(checks[0]['target_radii_rational']))
    if not all(a.contains(b) for a, b in zip(paired['eigenbox'], point, strict=True)):
        raise ArithmeticError('fresh midpoint point witness must belong to paired family')
    arrays = dict(weighted_midpoint_directions=directions, raw_domain=source['raw_domain'],
                  raw_center=source['raw_center'])
    for name, derivatives, anchor in (('psi_value', solved[1][:61], point[:61, None]),
                                       ('response_value', solved[2], point_solutions[0])):
        bound = grouped.group_row_bounds(derivatives, unit_groups)
        arrays[name+'_support'] = bound
        arrays[name] = anchor+np.array([arb(0, v) for v in bound], dtype=object)[:, None]
    for k in range(3):
        arrays[f'point_solve_{k}'] = point_solutions[k]
        arrays[f'uniform_solve_{k}'] = solved[k]
        if k:
            arrays[f'preconditioned_residual_{k}'] = residuals[k-1]
    if not all(v.is_finite() for a in arrays.values() for v in a.flat):
        raise ArithmeticError('finite complete primal value enclosures required')
    report = dict(family, interval=source['index'], scope='ACTUAL_HS_MIDPOINT_OUTER_DOMAIN', point_eigenpair_checks=checks, solve_proofs=proofs,
        same_family_segment_smoothness_established=True, uniform_primal_psi_and_response_enclosed=True,
        all_249_scaled_directions_verified=True, verified_point_variations_contained=True,
        eigenvalue_refined=False, auxiliary_line_border_used_as_eigenvalue_derivative=False,
        contracted_action_orders=sorted(orders), physical_hessian_evaluated=False,
        uniform_variations_from_complete_signed_residuals=True,
        maximum_psi_value_radius=float(max(v.rad() for v in arrays['psi_value'].flat)),
        maximum_response_value_radius=float(max(v.rad() for v in arrays['response_value'].flat)),
        independent_recomputation=False, full_path_uniform_contraction=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    return arrays, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    ctx.prec = 512
    p = engine.p
    residual = p.geometry.residual
    targets = [(p.values, 'sha'), (residual.center, '_sha'), (residual.foundation.coordinate.center, '_sha')]
    with cache.cache_hashes(targets, excluded_roots=[args.out]):
        source = engine.load_inputs(args.interval)
        for file in (Path(__file__), Path(grouped.__file__), Path(signed.__file__), Path(cache.__file__),
                     Path(sys.modules[enclose_response_rows.__module__].__file__),
                     Path(sys.modules[validate_midpoint_segment_family.__module__].__file__),
                     ROOT/'theory/n12_gate7_midpoint_primal_mean_value.md'):
            residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
        p.verify_sources(source['binding'])
        try:
            arrays, report = evaluate(source)
            p.verify_sources(source['binding'])
            encoded = {}
            for name, a in arrays.items():
                encoded[name+'_mid_q'], encoded[name+'_rad_q'] = p.hs.rational_balls(a)
            data = args.out/'column.npz'
            np.savez_compressed(data, **encoded)
            record = dict(binding=source['binding'], interval=args.interval, report=report,
                          data_SHA256=p.values.sha(data), FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps({k:v for k,v in report.items() if not isinstance(v,(dict,list))}), flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error), FULL_BHSM_COMPLETE=False)))
            raise


if __name__ == '__main__':
    main()

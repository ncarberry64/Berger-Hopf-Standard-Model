"""New all-output connecting Hessian bound from frozen endpoint/HS domains.

Consumes direct reproduced operands without repeating any frozen numerical
producer. Writes to an explicit fresh output; first/repeat runs are independent.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from flint import arb, ctx, fmpq

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts')]
import certify_n12_gate7_accepted_replay_center_outward_74d as action
from bhsm.interface import shared_connecting_hessian as connecting
from bhsm.interface import uniform_action_contraction as producer


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def encode(payload):
    return (json.dumps(payload, sort_keys=True, indent=2) + '\n').encode()


def read_array(data, key):
    mids, radii = data[key + '_mid_q'], data[key + '_rad_q']
    return np.array([arb(fmpq(str(m))) + arb(0, arb(fmpq(str(r))))
                     for m, r in zip(mids.flat, radii.flat, strict=True)],
                    dtype=object).reshape(mids.shape)


def number(value):
    value = value.upper()
    return dict(exact=str(value.fmpq()), approximate=float(value))


def model(value):
    pair = lambda x: [str(x.mid().fmpq()), str(x.rad().fmpq())]
    return dict(c=pair(value.c), a=[[i, pair(x)] for i, x in enumerate(value.a.entries())
                                  if not x.is_zero()], r=str(value.r.fmpq()))


def import_domain(folder, data_name, sources):
    record_path, receipt_path, data_path = (folder / 'record.json',
        folder / 'reproduction.json', folder / data_name)
    record, receipt = [json.loads(p.read_bytes()) for p in (record_path, receipt_path)]
    hashes = {str(p.resolve()): sha(p) for p in (record_path, receipt_path, data_path)}
    if (receipt.get('byte_identical') is not True
            or receipt.get('independent_recomputation') is not True
            or receipt['record_SHA256'] != hashes[str(record_path.resolve())]
            or record['data_SHA256'] != hashes[str(data_path.resolve())]):
        raise ValueError(f'reproduced direct input binding failed: {folder.name}')
    sources.update(hashes)
    return record, data_path


def run(evidence, target, kind, out):
    if out.exists():
        raise FileExistsError('use a fresh output; frozen results are not overwritten')
    ctx.prec = 512
    sources = {}
    base = evidence / 'artifacts/flagship_integration'
    anchor_record, anchor_path = import_domain(
        base / '.affine_eigenpair_pilot_work/endpoint_013', 'eigenpair.npz', sources)
    if not anchor_record['report']['validation_passed']:
        raise ValueError('validated anchor required')
    trial = next(i for i, row in enumerate(anchor_record['report']['trials'])
                 if row['validation_passed'])
    with np.load(anchor_path, allow_pickle=False) as z:
        anchor, eigen, R, w, V, Y = [read_array(z, k) for k in (
            'center_state', 'eigenpair_center', 'preconditioner',
            f'trial_{trial}_radii', f'trial_{trial}_variation_bounds', 'residual_bounds')]
    if not all(x.rad().is_zero() for x in (*anchor, *eigen)):
        raise ValueError('exact anchor and eigenpair predictor required')
    radii = [anchor_record['radius_longitudinal_rational'],
             anchor_record['radius_transverse_rational']]
    if target == 'endpoint14':
        record, path = import_domain(base / '.affine_eigenpair_pilot_work/endpoint_014',
                                    'eigenpair.npz', sources)
        if (not record['report']['validation_passed'] or
                radii != [record['radius_longitudinal_rational'],
                          record['radius_transverse_rational']]):
            raise ValueError('same original target radii and validated input required')
        with np.load(path, allow_pickle=False) as z:
            center, directions = [read_array(z, k) for k in ('center_state', 'affine_directions')]
        groups = [(0, 1, 'interval'), (1, 75, 'euclidean')]
        scales = [arb(fmpq(radii[0]))] + [arb(fmpq(radii[1]))] * 74
    else:
        record, path = import_domain(base / '.coupled_hs_midpoint_domain_work/interval_013',
                                    'domain.npz', sources)
        if (record.get('actual_HS_midpoint_image_enclosed') is not True
                or record.get('uniform_endpoint_fields_independently_paired') is not True):
            raise ValueError('reproduced actual HS midpoint outer domain required')
        with np.load(path, allow_pickle=False) as z:
            center, directions = [read_array(z, k)[:98] for k in ('raw_center', 'raw_directions')]
        groups = [(g['start'], g['stop'], g['norm']) for g in record['groups']]
        scales = [arb(fmpq(g['radius_rational'])) for g in record['groups']
                  for _ in range(g['start'], g['stop'])]
        if [g['radius_rational'] for g in record['groups'][:4]] != [radii[0]]*2 + [radii[1]]*2:
            raise ValueError('midpoint input changes the original physical radii')
    if center.shape != (98,) or directions.shape != (98, len(scales)):
        raise ValueError('complete original raw target domain required')
    scaled = [[directions[i, j] * scales[j] for j in range(len(scales))] for i in range(98)]
    seed_path = ROOT / 'artifacts/flagship_integration/gate7_uniform_action_20260923/scalar.json'
    seed = json.loads(seed_path.read_bytes())
    action_path = Path(action.__file__)
    frozen_action_hashes = {v for k, v in seed['source_SHA256'].items()
                            if Path(k).name == action_path.name}
    if frozen_action_hashes != {sha(action_path)}:
        raise ValueError('retained action source does not match the frozen action leaf')
    for path in (Path(__file__), Path(connecting.__file__), Path(producer.__file__),
                 action_path, seed_path,
                 ROOT / 'src/bhsm/interface/shared_action_taylor.py',
                 ROOT / 'src/bhsm/interface/shared_parameter_residual.py',
                 ROOT / 'src/bhsm/interface/factored_arb_integrand.py',
                 Path(sys.modules[action.metric_data.__module__].__file__),
                 Path(sys.modules[action.standard_model_casimir_coefficient.__module__].__file__)):
        sources[str(path.resolve())] = sha(path)
    operands = connecting.connecting_operands(anchor, center, scaled, groups,
        R.tolist(), list(w), list(eigen[:61]), 37, variation=kind == 'variation')
    print(json.dumps(dict(phase='NEW_CONNECTING_ACTION', target=target, kind=kind,
                         parameters=operands['domain'].dimension)), flush=True)
    def evaluate(state, legs):
        return producer.contract(action, state, legs, lambda done, total:
            print(json.dumps(dict(phase='QUADRATURE', completed=done, total=total)), flush=True))
    result = connecting.enclose_difference(evaluate, operands)
    q0 = max((v / wi).upper() for v, wi in zip(V, w, strict=True))
    y0 = max((y / wi).upper() for y, wi in zip(Y, w, strict=True))
    payload = dict(algorithm='SHARED_STAR_CONNECTING_HESSIAN_DUAL_ARB512_V1',
        anchor=13, target=target, input_kind=kind,
        definition='sup ||W^-1 R ((H_red(x)-H_red(x_anchor))*eta,0)||_infinity',
        domain='x=xa+s*(center+directions*theta-xa), 0<=s<=1; original target groups/radii retained',
        target_parameter_count=len(scales), parameters=operands['domain'].dimension,
        groups=operands['domain'].groups, radius_exact=radii,
        all_62_weighted_output_coordinates_enclosed=True,
        weighted_input_box_enclosed=kind == 'variation',
        anchor_eigenvector_input_enclosed=kind == 'residual',
        actual_HS_midpoint_outer_domain_included=target == 'midpoint13',
        complete_interval_domain_covered_by_this_file=False,
        weighted_output_norm_upper=number(result['weighted_output_norm_upper']),
        integrated_model=model(result['model']),
        positive_global_inertia_lower=dict(exact=str(result['inertia_lower'].lower().fmpq()),
                                          approximate=float(result['inertia_lower'].lower())),
        frozen_weighted_defect_upper=number(q0), frozen_weighted_residual_upper=number(y0),
        sufficient_fixed_witness_contraction_increment_limit=number(1-q0),
        proof='FTC on the full star, preconditioner contracted as one raw action leg, Euclidean dual covers all weighted output coordinates; integrate the shared scalar path only',
        limitation='First-order Taylor tails bound mixed products absolutely; a large upper bound is not a lower bound or physical instability',
        source_SHA256=sources, physical_domain_shrunk=False,
        frozen_calculations_recomputed=False, new_eigenpair_solve=False,
        continuation_certified=False, branch_identity_on_new_domain_certified=False,
        kappa_L=None, kappa_T=None, new_physical_budget_debit=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    # Check direct inputs once again before publishing this new result.
    if any(sha(Path(p)) != digest for p, digest in sources.items()):
        raise RuntimeError('a bound source changed during evaluation')
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('xb') as stream:
        stream.write(encode(payload))
    print(json.dumps(dict(weighted_output_norm_upper=payload['weighted_output_norm_upper'],
                         continuation_certified=False)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--target', choices=('endpoint14', 'midpoint13'), required=True)
    parser.add_argument('--kind', choices=('residual', 'variation'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.evidence_root.resolve(), args.target, args.kind, args.out.resolve())

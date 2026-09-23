"""Bound the curvature and original-tube errors of a joint moving witness."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx, fmpq

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_shared_connecting_hessian as inputs
from bhsm.interface import shared_eigenpair_transport as transport


def operands(evidence):
    base = evidence/'artifacts/flagship_integration'
    sources, endpoints = {}, []
    for index in (13, 14):
        record, path = inputs.import_domain(base/f'.affine_eigenpair_pilot_work/endpoint_{index:03d}',
                                            'eigenpair.npz', sources)
        if not record['report']['validation_passed']:
            raise ValueError('validated original endpoint required')
        trial = next(i for i, t in enumerate(record['report']['trials']) if t['validation_passed'])
        with np.load(path, allow_pickle=False) as z:
            values = {key: inputs.read_array(z, key) for key in (
                'center_state', 'affine_directions', 'eigenpair_center', 'preconditioner',
                'center_defect', f'trial_{trial}_radii', 'eigenpair_box')}
        values['weights'] = values[f'trial_{trial}_radii']
        values['radii'] = [record['radius_longitudinal_rational'], record['radius_transverse_rational']]
        values['groups'] = [(0, 1, 'interval'), (1, 75, 'euclidean')]
        values['scaled'] = [[values['affine_directions'][i, j]*arb(fmpq(values['radii'][j != 0]))
                            for j in range(75)] for i in range(98)]
        R = arb_mat(62, 62, list(values['preconditioner'].flat))
        D = arb_mat(62, 62, list(values['center_defect'].flat))
        identity = arb_mat(np.eye(62, dtype=int).tolist())
        values['R'], values['J'] = R, R.inv()*(identity-D)
        endpoints.append(values)
    if endpoints[0]['radii'] != endpoints[1]['radii']:
        raise ValueError('endpoint radii differ')
    record, path = inputs.import_domain(base/'.coupled_hs_midpoint_domain_work/interval_013',
                                        'domain.npz', sources)
    if (not record.get('actual_HS_midpoint_image_enclosed')
            or not record.get('uniform_endpoint_fields_independently_paired')):
        raise ValueError('reproduced actual midpoint outer domain required')
    if [g['radius_rational'] for g in record['groups'][:4]] != endpoints[0]['radii'][:1]*2+endpoints[0]['radii'][1:]*2:
        raise ValueError('midpoint radii differ')
    with np.load(path, allow_pickle=False) as z:
        center, directions = [inputs.read_array(z, key)[:98] for key in ('raw_center', 'raw_directions')]
    groups = [(g['start'], g['stop'], g['norm']) for g in record['groups']]
    scales = [arb(fmpq(g['radius_rational'])) for g in record['groups'] for _ in range(g['start'], g['stop'])]
    midpoint = dict(center_state=center, groups=groups,
        scaled=[[directions[i, j]*scales[j] for j in range(249)] for i in range(98)])
    return endpoints, midpoint, sources


def run(evidence, target, kind, out):
    if out.exists():
        raise FileExistsError('fresh output required')
    ctx.prec = 512
    (a, b), midpoint, sources = operands(evidence)
    selected = {'curvature': a, 'endpoint13': a, 'endpoint14': b, 'midpoint13': midpoint}[target]
    fraction = {'curvature': arb(0), 'endpoint13': arb(0), 'endpoint14': arb(1), 'midpoint13': arb(1)/2}[target]
    ops = transport.transport_operands(a['center_state'], b['center_state'],
        a['eigenpair_center'], b['eigenpair_center'], a['R'], b['R'], list(a['weights']), 37,
        selected['center_state'], selected['scaled'], selected['groups'], fraction,
        curvature=target == 'curvature', variation=kind == 'variation')
    seed_path = ROOT/'artifacts/flagship_integration/gate7_uniform_action_20260923/scalar.json'
    seed = json.loads(seed_path.read_bytes())
    action_path = Path(inputs.action.__file__)
    if {v for k, v in seed['source_SHA256'].items() if Path(k).name == action_path.name} != {inputs.sha(action_path)}:
        raise ValueError('retained action source changed')
    for path in (Path(__file__), Path(inputs.__file__), Path(transport.__file__),
                 Path(inputs.producer.__file__), action_path, seed_path,
                 ROOT/'src/bhsm/interface/shared_action_taylor.py',
                 ROOT/'src/bhsm/interface/shared_parameter_residual.py',
                 ROOT/'src/bhsm/interface/factored_arb_integrand.py',
                 Path(sys.modules[inputs.action.metric_data.__module__].__file__),
                 Path(sys.modules[inputs.action.standard_model_casimir_coefficient.__module__].__file__)):
        sources[str(path.resolve())] = inputs.sha(path)
    print(json.dumps(dict(phase='NEW_TRANSPORTED_ACTION', target=target, kind=kind,
                         parameters=ops['domain'].dimension)), flush=True)
    value, inertia = inputs.producer.contract(inputs.action, ops['state'], ops['legs'],
        lambda done, total: print(json.dumps(dict(phase='QUADRATURE', completed=done, total=total)), flush=True))
    bound = (value.support()*ops['bound_factor']).upper()
    surrogate = transport.interpolated_defect(a['R'], b['R'], a['J'], b['J'], list(a['weights']))
    payload = dict(algorithm='JOINT_MOVING_EIGENPAIR_PRECONDITIONER_HESSIAN_ERROR_ARB512_V1',
        interval=13, target=target, input_kind=kind, radius_exact=a['radii'],
        parameters=ops['domain'].dimension, groups=ops['domain'].groups,
        moving_preconditioner='R(s)=(1-s)R13+s R14',
        moving_predictor='(psi,lambda)(s)=(1-s)y13+s y14; normalization remains an equation',
        domain=('x=x13+t*(x14-x13), s,t independent in [0,1]' if target == 'curvature' else
                'x=x13+s*(x14-x13)+t*(target_center-x13-target_fraction*(x14-x13)+D*theta); s,t in [0,1]'),
        weighted_operator_error_upper=inputs.number(bound),
        raw_action_model=inputs.model(value), interpolation_factor=inputs.number(ops['bound_factor']),
        positive_global_inertia_lower=dict(exact=str(inertia.lower().fmpq()), approximate=float(inertia.lower())),
        affine_surrogate_defect_upper=inputs.number(surrogate['surrogate_defect_upper']),
        all_62_weighted_output_coordinates_enclosed=True,
        weighted_input_box_enclosed=kind == 'variation',
        moving_predictor_vector_enclosed=kind == 'residual',
        physical_domain_shrunk=False, frozen_calculations_recomputed=False,
        new_eigenpair_solve=False, source_SHA256=sources,
        eigenbranch_continuation_certified=False, kappa_L=None, kappa_T=None,
        new_physical_budget_debit=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    if any(inputs.sha(Path(p)) != digest for p, digest in sources.items()):
        raise RuntimeError('input source changed during calculation')
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('xb') as stream:
        stream.write(inputs.encode(payload))
    print(json.dumps(dict(weighted_operator_error_upper=payload['weighted_operator_error_upper'],
                         affine_surrogate_defect_upper=payload['affine_surrogate_defect_upper'])), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--target', choices=('curvature', 'endpoint13', 'endpoint14', 'midpoint13'), required=True)
    parser.add_argument('--kind', choices=('residual', 'variation'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.evidence_root.resolve(), args.target, args.kind, args.out.resolve())

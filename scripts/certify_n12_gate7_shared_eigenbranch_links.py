"""New moving-witness links through an already certified actual HS midpoint.

The connected evaluation cover retains the complete frozen endpoint and
midpoint domains. New action evaluations concern only the two center-line
links. A dense physical history tube and complete rate jets remain separate.
"""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_shared_connecting_hessian as inputs
from bhsm.interface import shared_eigenpair_transport as transport
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.affine_eigenpair_contraction import nonlinear_eigenpair_variation


def load(evidence):
    base = evidence/'artifacts/flagship_integration'
    sources, rows = {}, []
    names = ['.affine_eigenpair_pilot_work/endpoint_013',
             '.coupled_midpoint_eigenpair_pilot_work/interval_013',
             '.affine_eigenpair_pilot_work/endpoint_014']
    for name in names:
        record, path = inputs.import_domain(base/name, 'eigenpair.npz', sources)
        report = record['report']
        if (not report['validation_passed'] or report.get('selected_zero_based_index_verified') != 24
                or not report.get('witness_contained') or not report.get('positive_original_reference_overlap')):
            raise ValueError('complete oriented index-24 frozen eigenbranch required')
        trial = next(i for i, row in enumerate(report['trials']) if row['validation_passed'])
        with np.load(path, allow_pickle=False) as z:
            x, y, R, D, w, box = [inputs.read_array(z, key) for key in (
                'center_state', 'eigenpair_center', 'preconditioner', 'center_defect',
                f'trial_{trial}_radii', 'eigenpair_box')]
        if not all(v.rad().is_zero() for v in (*x, *y, *w)):
            raise ValueError('exact frozen centers and positive radii required')
        R, D = arb_mat(62, 62, list(R.flat)), arb_mat(62, 62, list(D.flat))
        identity = arb_mat(np.eye(62, dtype=int).tolist())
        J = R.inv()*(identity-D)
        if not all(v.is_finite() for v in J.entries()):
            raise ArithmeticError('frozen center Jacobian recovery failed')
        rows.append(dict(name=name, x=x, y=y, R=R, J=J, w=w, box=box, record=record))
    return rows, sources


def predictor_residual(a, b, weights):
    """Signed complete surrogate residual, including normalization curvature."""
    d = TaylorDomain([(0, 1, 'interval')], 1)
    s = d.affine(arb(1)/2, [arb(1)/2])
    p0, p1 = list(a['y'][:61]), list(b['y'][:61])
    delta = [v-u for u, v in zip(p0, p1, strict=True)]
    def residual(row, p):
        # J's top-left block is H-lambda I. Its center p is exact.
        return [sum((row['J'][i, j]*p[j] for j in range(61)), arb(0)) for i in range(61)] + [
            (sum((v*v for v in p), arb(0))-1)/2]
    f0, f1 = residual(a, p0), residual(b, p1)
    cross = [sum(((b['J'][i, j]-a['J'][i, j])*delta[j] for j in range(61)), arb(0))
             for i in range(61)] + [sum((v*v for v in delta), arb(0))/2]
    f = [(1-s)*u+s*v-s*(1-s)*c for u, v, c in zip(f0, f1, cross, strict=True)]
    pre = [sum(((a['R'][i, j]+s*(b['R'][i, j]-a['R'][i, j]))*f[j]
                for j in range(62)), d.affine(0))/weights[i] for i in range(62)]
    return max(v.support() for v in pre), [inputs.model(v) for v in pre]


def prove_link(a, b, progress):
    weights = [max(u, v) for u, v in zip(a['w'], b['w'], strict=True)]
    surrogate = transport.interpolated_defect(a['R'], b['R'], a['J'], b['J'], weights)
    actions = {}
    for kind in ('variation', 'residual'):
        ops = transport.transport_operands(a['x'], b['x'], a['y'], b['y'],
            a['R'], b['R'], weights, 37, a['x'], [[arb(0)]]*98,
            [(0, 1, 'interval')], arb(0), curvature=True, variation=kind == 'variation')
        value, inertia = inputs.producer.contract(inputs.action, ops['state'], ops['legs'],
            lambda done, total: progress(kind, done, total))
        actions[kind] = dict(upper=inputs.number((value.support()/8).upper()),
            model=inputs.model(value), inertia_lower_exact=str(inertia.lower().fmpq()))
    variation = arb(actions['variation']['upper']['exact'])
    residual_error = arb(actions['residual']['upper']['exact'])
    predictor_Y, predictor_models = predictor_residual(a, b, weights)
    Y = (predictor_Y+residual_error).upper()
    q_base = (surrogate['surrogate_defect_upper']+variation).upper()
    abs_R = np.array([[max(abs(a['R'][i, j]).upper(), abs(b['R'][i, j]).upper())
                       for j in range(62)] for i in range(62)], dtype=object)
    nonlinear = nonlinear_eigenpair_variation(abs_R, np.array(weights, dtype=object))
    q_nonlinear = max((v/w).upper() for v, w in zip(nonlinear, weights, strict=True))
    # Change only the eigenpair witness, never a physical state-domain radius.
    candidates = []
    for power in range(31):
        scale = arb(2)**power
        q = (q_base+scale*q_nonlinear).upper()
        image = (Y/scale+q).upper()
        candidates.append((image, power, q))
    image, power, q = min(candidates, key=lambda row: row[0])
    scale = arb(2)**power
    radii = [scale*w for w in weights]
    endpoint_boxes = all(
        (center+arb(0, radius)).contains(box)
        for row in (a, b) for center, radius, box in zip(row['y'], radii, row['box'], strict=True))
    passed = bool(image < 1 and q < 1 and endpoint_boxes)
    gap = None
    if passed:
        row_norm = max((sum((abs_R[i, j] for j in range(62)), arb(0))/weights[i]).upper()
                       for i in range(62))
        inverse = (sum((w*w for w in weights), arb(0)).sqrt()*row_norm/(1-q)).upper()
        gap = (1/inverse).lower()
        passed = bool(gap > 0)
    return dict(from_domain=a['name'], to_domain=b['name'],
        curvature_contractions=actions,
        surrogate_defect_upper=inputs.number(surrogate['surrogate_defect_upper']),
        complete_centerline_defect_base_upper=inputs.number(q_base),
        signed_predictor_residual_upper=inputs.number(predictor_Y),
        signed_predictor_residual_models=predictor_models,
        residual_upper_in_base_weights=inputs.number(Y),
        nonlinear_defect_per_witness_scale_upper=inputs.number(q_nonlinear),
        eigenpair_witness_scale_exact=str(scale.fmpq()), base_weights_exact=[str(w.fmpq()) for w in weights],
        weighted_contraction_upper=inputs.number(q), image_radius_ratio_upper=inputs.number(image),
        inclusion_margin_lower_exact=str((1-image).lower().fmpq()),
        both_frozen_eigenpair_boxes_contained=endpoint_boxes,
        gap_lower=None if gap is None else dict(exact=str(gap.fmpq()), approximate=float(gap)),
        selected_index_24_continues=passed, normalized_oriented_eigenpair_continues=passed,
        centerline_link_certified=passed)


def run(evidence, out):
    if out.exists():
        raise FileExistsError('fresh output required')
    ctx.prec = 512
    rows, sources = load(evidence)
    # Bind the midpoint image domain directly as well, retaining original radii.
    base = evidence/'artifacts/flagship_integration'
    midpoint_record, midpoint_path = inputs.import_domain(
        base/'.coupled_hs_midpoint_domain_work/interval_013', 'domain.npz', sources)
    if (not midpoint_record.get('actual_HS_midpoint_image_enclosed')
            or not midpoint_record.get('uniform_endpoint_fields_independently_paired')):
        raise ValueError('actual HS image input not certified')
    endpoint_radii = [[r['record']['radius_longitudinal_rational'],
                       r['record']['radius_transverse_rational']] for r in (rows[0], rows[2])]
    if endpoint_radii[0] != endpoint_radii[1]:
        raise ValueError('original endpoint radii differ')
    if [g['radius_rational'] for g in midpoint_record['groups'][:4]] != endpoint_radii[0][:1]*2+endpoint_radii[0][1:]*2:
        raise ValueError('actual midpoint radii differ')
    eigen_binding = rows[1]['record']['binding']['files']
    if not any(Path(k).name == 'domain.npz' and v == inputs.sha(midpoint_path)
               for k, v in eigen_binding.items()):
        raise ValueError('midpoint eigenbranch is not bound to this HS domain')
    seed_path = ROOT/'artifacts/flagship_integration/gate7_uniform_action_20260923/scalar.json'
    seed = json.loads(seed_path.read_bytes())
    action_path = Path(inputs.action.__file__)
    if {v for k, v in seed['source_SHA256'].items() if Path(k).name == action_path.name} != {inputs.sha(action_path)}:
        raise ValueError('retained action source changed')
    for path in (Path(__file__), Path(inputs.__file__), Path(transport.__file__),
                 Path(inputs.producer.__file__), Path(nonlinear_eigenpair_variation.__globals__['__file__']),
                 action_path, seed_path, ROOT/'src/bhsm/interface/shared_action_taylor.py',
                 ROOT/'src/bhsm/interface/shared_parameter_residual.py',
                 ROOT/'src/bhsm/interface/factored_arb_integrand.py',
                 Path(sys.modules[inputs.action.metric_data.__module__].__file__),
                 Path(sys.modules[inputs.action.standard_model_casimir_coefficient.__module__].__file__)):
        sources[str(path.resolve())] = inputs.sha(path)
    links = []
    for index in range(2):
        links.append(prove_link(rows[index], rows[index+1], lambda kind, done, total:
            print(json.dumps(dict(link=index, kind=kind, completed=done, total=total)), flush=True)))
        print(json.dumps(dict(link=index, passed=links[-1]['centerline_link_certified'],
                             image=links[-1]['image_radius_ratio_upper']['approximate'])), flush=True)
    gaps = [(abs(a.mid()-b.mid())-a.rad()-b.rad()).lower()
            for a, b in zip(rows[0]['box'], rows[2]['box'], strict=True)]
    coordinate = max(range(62), key=lambda i: gaps[i])
    payload = dict(algorithm='SHARED_MOVING_WITNESS_CENTERLINE_LINKS_ARB512_V1',
        interval=13, links=links, radius_exact=endpoint_radii[0],
        fixed_endpoint_witnesses_disjoint=dict(coordinate=coordinate,
            gap_lower_exact=str(gaps[coordinate].fmpq()), separated=bool(gaps[coordinate] > 0)),
        frozen_endpoint_and_actual_HS_midpoint_domains_reused=True,
        connected_eigenbranch_evaluation_cover_certified=all(link['centerline_link_certified'] for link in links),
        coverage='union of the two original endpoint affine domains, original actual-HS midpoint outer domain, and two newly certified center-line segments',
        whole_continuous_history_tube_covered=False,
        limitation='The connected evaluation cover is not the image of every continuous dense-output history curve. No uniform complete physical rate jets or global remainder follow.',
        source_SHA256=sources, original_physical_radii_changed=False,
        frozen_calculations_recomputed=False, new_eigenpair_solve=False,
        eigenpair_witness_enlargement_only=True, new_physical_budget_debit=False,
        Gate7_closed=False, kappa_L=None, kappa_T=None, FULL_BHSM_COMPLETE=False)
    if any(inputs.sha(Path(p)) != digest for p, digest in sources.items()):
        raise RuntimeError('source changed during evaluation')
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('xb') as stream:
        stream.write(inputs.encode(payload))
    print(json.dumps(dict(connected_evaluation_cover=payload['connected_eigenbranch_evaluation_cover_certified'],
                         Gate7_closed=False)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.evidence_root.resolve(), args.out.resolve())

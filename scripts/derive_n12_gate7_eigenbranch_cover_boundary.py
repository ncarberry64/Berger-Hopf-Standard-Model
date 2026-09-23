"""Reuse frozen eigenbranch domains; identify the boundary of history coverage.

This derives gaps from saved inverse bounds and proves domain exclusions. It
does not evaluate the action or promote endpoint certificates to segment proofs.
"""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts')]
from derive_n12_gate7_mixed_eigenline_certificate import encode, sha, read_array


def exact(value):
    return dict(exact=str(value.fmpq()), approximate=float(value))


def separation(left, right):
    """A positive coordinate gap rigorously separates two containing boxes."""
    bounds = [(abs(a.mid()-b.mid()).lower()-a.rad()-b.rad()).lower()
              for a, b in zip(left, right, strict=True)]
    i = max(range(len(bounds)), key=lambda j: bounds[j])
    return dict(coordinate=i, gap_lower=exact(bounds[i]), separated=bool(bounds[i] > 0))


def run(evidence, out):
    ctx.prec = 512
    checkpoint = ROOT/'artifacts/flagship_integration/gate7_global_checkpoint_20260923'
    source_path = checkpoint/'global_remainder_checkpoint.json'
    source = json.loads(source_path.read_bytes())
    indices = source['coverage_summary']['uniform_eigenbranch_endpoints']
    state_path = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz'
    with np.load(state_path, allow_pickle=False) as z:
        states = [[arb(float(x)) for x in row] for row in z['projected_states']]
    sources = {str(p.resolve()): sha(p) for p in (source_path, state_path, Path(__file__))}
    anchors, hulls, imports = [], {}, []
    # Each new import boundary binds only its direct record, receipt and data.
    # No recursive verification or numerical reproduction of frozen inputs.
    for index in indices:
        folder = (checkpoint/'endpoint071_eigenbranch' if index == 71 else
                  evidence/f'artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_{index:03d}')
        record_path, receipt_path, data_path = [folder/name for name in ('record.json', 'reproduction.json', 'eigenpair.npz')]
        record, receipt = [json.loads(p.read_bytes()) for p in (record_path, receipt_path)]
        hashes = {str(p.resolve()): sha(p) for p in (record_path, receipt_path, data_path)}
        if (not receipt['byte_identical'] or not receipt['independent_recomputation']
                or hashes[str(record_path.resolve())] != receipt['record_SHA256']
                or hashes[str(data_path.resolve())] != record['data_SHA256']
                or not record['report']['validation_passed']):
            raise ValueError(f'frozen import cannot be reconciled: endpoint {index}')
        sources.update(hashes)
        trial = next(i for i, t in enumerate(record['report']['trials']) if t['validation_passed'])
        with np.load(data_path, allow_pickle=False) as z:
            hulls[index] = read_array(z, 'raw_segment_hull')[:98]
            center = read_array(z, 'center_state')
            R = read_array(z, 'preconditioner')
            w = read_array(z, f'trial_{trial}_radii')
            V = read_array(z, f'trial_{trial}_variation_bounds')
        if not all(c.contains(s) for c, s in zip(center, states[index], strict=True)):
            raise ValueError('history and frozen anchor centers differ')
        q = max((v/wi).upper() for v, wi in zip(V, w, strict=True))
        if not q < 1:
            raise ValueError('frozen inverse defect does not prove invertibility')
        # ||K^-1||2 <= ||w||2 ||diag(w)^-1 R||infty/(1-q).
        # Sign flips between J and K preserve these absolute norm bounds.
        row_norm = max(sum((abs(R[i, j]).upper()/w[i] for j in range(62)), arb(0)).upper()
                       for i in range(62))
        inverse = (sum((wi**2 for wi in w), arb(0)).sqrt()*row_norm/(1-q)).upper()
        gap = (1/inverse).lower()
        if not gap > 0:
            raise ValueError('positive derived gap required')
        anchors.append(dict(endpoint=index, frozen_trial=trial,
            weighted_inverse_defect_upper=exact(q), bordered_inverse_2norm_upper=exact(inverse),
            eigenvalue_gap_lower=exact(gap), original_domain_unchanged=True,
            scope='FROZEN_ENDPOINT_AFFINE_DOMAIN_ONLY'))
        imports.append(dict(endpoint=index, frozen_independent_repeat_reused=True,
                            direct_input_hashes=hashes, numerical_calculation_repeated=False))
    pairs = [dict(left=i, right=j, **separation(hulls[i], hulls[j]))
             for n, i in enumerate(indices) for j in indices[n+1:]]
    if not all(p['separated'] for p in pairs):
        raise ArithmeticError('overlapping hulls require a connected-cover analysis')
    endpoint_membership, exclusions = {}, []
    for i, point in enumerate(states):
        candidates = []
        for anchor in indices:
            proof = separation(point, hulls[anchor])
            if proof['separated']:
                exclusions.append(dict(endpoint=i, anchor=anchor, **proof))
            else:
                candidates.append(anchor)
        # A box inclusion alone would not establish affine-domain membership.
        if candidates != ([i] if i in indices else []):
            raise ArithmeticError('new candidate containment requires affine-domain proof')
        endpoint_membership[i] = candidates
    intervals = []
    for i in range(370):
        left, right = endpoint_membership[i], endpoint_membership[i+1]
        if set(left).intersection(right):
            raise ArithmeticError('potential single-anchor interval requires path proof')
        intervals.append(dict(interval=i, endpoints=[i, i+1],
            classification='uncovered_and_requiring_new_action_evaluation',
            existing_endpoint_certificates=[j for j in (i, i+1) if j in indices],
            existing_union_covers_complete_interval=False,
            reason=('ENDPOINT_OUTSIDE_ALL_FROZEN_DOMAIN_HULLS' if not left or not right else
                    'ENDPOINTS_IN_DISTINCT_STRICTLY_SEPARATED_FROZEN_DOMAIN_HULLS'),
            continuation_certified=False, new_endpoint_anchor_required=None))
    result = dict(algorithm='FROZEN_EIGENBRANCH_DOMAIN_COVER_BOUNDARY_ARB512_V1',
        anchors=anchors, import_receipts=imports, disjoint_anchor_hull_witnesses=pairs,
        endpoint_exclusion_witnesses=exclusions, intervals=intervals,
        covered_intervals=0, total_intervals=370,
        existing_uniform_certificate_intervals=0, continuation_intervals=0,
        uncovered_intervals_requiring_new_action_evaluation=370,
        scope='CURRENT_CERTIFIED_COVERAGE_NOT_PROOF_THAT_CONTINUATION_FAILS',
        route_A=dict(status='MISSING_CONNECTING_DOMAIN_ACTION_BOUND',
            required_operator='sup_{x in X_[a,b]} ||W_a^-1 R_a ((D2S_red(x)-D2S_red(x_a))*eta,0)||_infinity',
            required_eta='psi_a for the residual and all |eta_i| <= w_a,i for the derivative defect',
            equivalent_action='integral_0^1 R_a (D3S_red(x_a+t*(x-x_a))[.,eta,x-x_a],0) dt',
            domain='Connected original history tube including actual HS midpoint images; no radius shrink',
            frozen_local_derivatives_extrapolated=False),
        route_B=dict(status='SEGMENT_SIZES_UNDETERMINED_PENDING_ROUTE_A_OPERATOR'),
        route_C=dict(status='NOT_LAUNCHED', new_anchor_evaluations=0,
                     minimal_new_anchor_set=None,
                     explanation='No justified minimum follows before candidate segment reach is bounded.'),
        frozen_calculations_recomputed=False, physical_domain_shrunk=False,
        gap_argument='For normalized psi, symmetric K has eigenvalues +/-1 and the other eigenvalue differences; 1/||K^-1||2 is a gap lower bound.',
        normalization_and_branch_identity='Inherited only on each frozen connected affine domain; no cross-domain identity claimed.',
        source_SHA256=sources, new_physical_budget_debit=False,
        Gate7_closed=False, kappa_L=None, kappa_T=None)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(encode(result))
    print(json.dumps(dict(covered_intervals=0, total_intervals=370,
        frozen_anchors=indices, minimal_new_anchor_set=None,
        required_new_object=result['route_A']['required_operator'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.evidence_root.resolve(), args.out.resolve())

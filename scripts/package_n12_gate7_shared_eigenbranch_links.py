"""Verify and package two independent new link certificates; no action run."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def verify(payload):
    if payload.get('algorithm') != 'SHARED_MOVING_WITNESS_CENTERLINE_LINKS_ARB512_V1':
        raise ValueError('wrong link certificate type')
    if (payload.get('interval') != 13 or len(payload['links']) != 2
            or payload.get('connected_eigenbranch_evaluation_cover_certified') is not True):
        raise ValueError('complete certified two-link evaluation cover required')
    if (payload['Gate7_closed'] or payload['FULL_BHSM_COMPLETE']
            or payload['kappa_L'] is not None or payload['kappa_T'] is not None
            or payload['new_physical_budget_debit'] or payload['original_physical_radii_changed']
            or payload['frozen_calculations_recomputed'] or payload['new_eigenpair_solve']
            or payload['whole_continuous_history_tube_covered']):
        raise ValueError('local proof has exceeded its authority')
    for link in payload['links']:
        if (not link['centerline_link_certified'] or not link['both_frozen_eigenpair_boxes_contained']
                or not link['selected_index_24_continues']
                or not link['normalized_oriented_eigenpair_continues']):
            raise ValueError('missing link proof or overlap')
        exact = lambda field: Fraction(link[field]['exact'])
        scale = Fraction(link['eigenpair_witness_scale_exact'])
        Y = exact('residual_upper_in_base_weights')
        q = exact('weighted_contraction_upper')
        image = exact('image_radius_ratio_upper')
        q_base = exact('complete_centerline_defect_base_upper')
        nonlinear = exact('nonlinear_defect_per_witness_scale_upper')
        if not (scale >= 1 and 0 <= q < 1 and 0 <= image < 1
                and q >= q_base+scale*nonlinear and image >= Y/scale+q
                and Fraction(link['inclusion_margin_lower_exact']) > 0
                and Fraction(link['inclusion_margin_lower_exact']) <= 1-image
                and Fraction(link['gap_lower']['exact']) > 0):
            raise ValueError('exact Banach/gap inequalities do not pass')
        for contraction in link['curvature_contractions'].values():
            if Fraction(contraction['inertia_lower_exact']) <= 0:
                raise ValueError('action inertia positivity is missing')


def run(first, repeat, out):
    if first.resolve() == repeat.resolve() or first.read_bytes() != repeat.read_bytes():
        raise ValueError('distinct byte-identical first/repeat outputs required')
    data = json.loads(first.read_bytes())
    verify(data)
    for path, digest in data['source_SHA256'].items():
        if sha(Path(path)) != digest:
            raise ValueError(f'bound direct source changed: {Path(path).name}')
    ledger_path = ROOT/'artifacts/flagship_integration/gate7_global_checkpoint_20260923/current_history_budget.json'
    ledger = json.loads(ledger_path.read_bytes())
    if [row['radius']['exact'] for row in ledger['rows']] != data['radius_exact']:
        raise ValueError('certificate differs from current original physical radii')
    receipt = dict(algorithm='SHARED_EIGENBRANCH_LINK_REPRODUCTION_V1',
        certificate_SHA256=sha(first), independent_recomputation=True, byte_identical=True,
        compared_outputs=[str(first.resolve()), str(repeat.resolve())],
        current_original_radius_ledger_SHA256=sha(ledger_path),
        physical_radii_match_current_ledger=True, exact_inequalities_checked=True,
        direct_input_hashes_rechecked=True,
        packaging_source_SHA256=sha(Path(__file__)),
        independent_run_method='Two fresh invocations; all four new D4 contractions independently evaluated; no numerical cache used',
        inherited_frozen_producers_rerun=False, Gate7_closed=False,
        scope='TWO_CENTERLINE_LINKS_AND_CONNECTED_INTERVAL13_EIGENBRANCH_EVALUATION_COVER_ONLY')
    out.mkdir(parents=True, exist_ok=True)
    for name, payload in [('certificate.json', first.read_bytes()),
                          ('independent_repeat.json', repeat.read_bytes()),
                          ('reproduction.json', (json.dumps(receipt, sort_keys=True, indent=2)+'\n').encode())]:
        with (out/name).open('xb') as stream:
            stream.write(payload)
    print(json.dumps(dict(byte_identical=True, exact_inequalities_pass=True,
                         original_radii_preserved=True, Gate7_closed=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--first', type=Path, required=True)
    parser.add_argument('--repeat', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.first, args.repeat, args.out)

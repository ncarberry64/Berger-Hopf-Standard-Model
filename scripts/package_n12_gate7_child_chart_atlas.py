"""Reconcile frozen interval 13 and assemble the 13--19 identity atlas.

No action contractions, eigenpair solves or inherited producer runs occur.
Historical raw source hashes are retained; line-ending equivalence is explicit.
"""
import argparse
import json
from pathlib import Path

import package_n12_gate7_child_chart_interval as current
import package_n12_gate7_shared_eigenbranch_links as inherited

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'artifacts/flagship_integration'
ATLAS = BASE/'gate7_child_atlas_20260924'


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True)+'\n').encode()


def verify_chain(certificates):
    """Validate chart labels, unchanged physical radii and shared node identity."""
    if [d['interval'] for d in certificates] != list(range(13, 19)):
        raise ValueError('exactly intervals 13 through 18, in order, required')
    radii = certificates[0]['radius_exact']
    prior = None
    for data in certificates:
        (inherited if data['interval'] == 13 else current).verify(data)
        n = data['interval']
        names = [f'.affine_eigenpair_pilot_work/endpoint_{n:03d}',
                 f'.coupled_midpoint_eigenpair_pilot_work/interval_{n:03d}',
                 f'.affine_eigenpair_pilot_work/endpoint_{n+1:03d}']
        if [(v['from_domain'], v['to_domain']) for v in data['links']] != list(zip(names, names[1:])):
            raise ValueError('chart sequence does not match interval')
        if data['radius_exact'] != radii:
            raise ValueError('physical radii differ across atlas')
        def node_digest(name):
            suffix = '/'+name+'/eigenpair.npz'
            hashes = [v for p, v in data['source_SHA256'].items()
                      if p.replace('\\', '/').endswith(suffix)]
            if len(hashes) != 1:
                raise ValueError('unique shared endpoint source binding required')
            return hashes[0]
        if prior is not None and node_digest(names[0]) != prior:
            raise ValueError('adjacent intervals do not use the same frozen endpoint chart')
        prior = node_digest(names[-1])


def run(out):
    packages = [BASE/'gate7_shared_eigenbranch_links_20260923']+[
        ATLAS/f'interval_{n:03d}' for n in range(14, 19)]
    data, bindings, reconciliation, archives = [], {}, [], {}
    for folder in packages:
        first, repeat, receipt_path = [folder/name for name in
            ('certificate.json', 'independent_repeat.json', 'reproduction.json')]
        receipt = json.loads(receipt_path.read_bytes())
        if (first.read_bytes() != repeat.read_bytes()
                or current.sha(first) != receipt['certificate_SHA256']
                or receipt['byte_identical'] is not True
                or receipt['independent_recomputation'] is not True):
            raise ValueError('frozen independent reproduction binding failed')
        for p in (first, repeat, receipt_path):
            bindings[p.relative_to(ROOT).as_posix()] = current.sha(p)
        payload = json.loads(first.read_bytes())
        data.append(payload)
        # Relocation of the imported interval-13 checkout is recorded, never
        # implemented by modifying its frozen certificate or source hashes.
        if payload['interval'] == 13:
            marker = 'BHSM-g7-child-closure-assist/'
            for original, digest in payload['source_SHA256'].items():
                portable = original.replace('\\', '/')
                target = ROOT/portable.split(marker, 1)[1] if marker in portable else Path(original)
                target_digest = current.sha(target)
                row = dict(original_path=original, original_SHA256=digest,
                           active_path=str(target.resolve()), active_SHA256=target_digest)
                if target_digest == digest:
                    row['reconciliation'] = 'EXACT_BYTES'
                else:
                    historical = Path(original)
                    if (current.sha(historical) != digest or
                            historical.read_bytes().replace(b'\r\n', b'\n') !=
                            target.read_bytes().replace(b'\r\n', b'\n')):
                        raise ValueError('imported scientific source differs beyond line endings')
                    name = 'historical_source_capsule/'+target.name
                    archives[name] = historical.read_bytes()
                    row.update(reconciliation='CRLF_LF_ONLY_EXPLICIT_EQUIVALENCE',
                               historical_bytes_archive=name)
                reconciliation.append(row)
    verify_chain(data)
    ledger = BASE/'gate7_global_checkpoint_20260923/current_history_budget.json'
    if [r['radius']['exact'] for r in json.loads(ledger.read_bytes())['rows']] != data[0]['radius_exact']:
        raise ValueError('atlas differs from current physical radius ledger')
    atlas = dict(algorithm='FROZEN_CHILD_CHART_ATLAS_13_TO_19_V1',
        imported_commit='86b05bc9633a8d27257c8e391e944bee23372f74',
        integration_commit='7f180488',
        certificates=bindings, interval13_source_reconciliation=reconciliation,
        assembly_source_SHA256=current.sha(Path(__file__)),
        current_radius_ledger_SHA256=current.sha(ledger),
        radius_exact=data[0]['radius_exact'],
        intervals=[dict(interval=d['interval'],
            connected_evaluation_cover=True,
            links=[dict(from_domain=v['from_domain'], to_domain=v['to_domain'],
                contraction=v['weighted_contraction_upper'],
                image_ratio=v['image_radius_ratio_upper'], gap_lower=v['gap_lower'],
                status='CERTIFIED', failure_category=None,
                physical_closure_boundary_demonstrated=False) for v in d['links']]) for d in data],
        failure_categories={'1':'numerical chart conditioning only',
            '2':'insufficient enclosure', '3':'missing intermediate child chart',
            '4':'demonstrated loss of simple eigenline or spectral gap',
            '5':'demonstrated action/domain incompatibility'},
        failure_category_rule='Failure of a bound alone is not evidence for categories 4 or 5. Neither category alone identifies decay or de-encapsulation.',
        certified_centerline_links=12, original_endpoint_charts=7,
        original_actual_HS_midpoint_charts=6,
        Layer_A_connected_eigenbranch_evaluation_cover=True,
        Layer_B_complete_dense_output_physical_tube=False,
        Layer_C_global_physical_remainder=False,
        Layer_D_full_Gate7_contraction=False,
        next_obligation='Enclose the full allowed state/midpoint/output perturbation tube with moving charts, then complete uniform physical response/rate jets and global remainder inequalities.',
        new_endpoint_anchors=0, inherited_successful_calculations_rerun=False,
        original_physical_radii_changed=False, new_physical_budget_debit=False,
        Gate7_closed=False, kappa_L=None, kappa_T=None, FULL_BHSM_COMPLETE=False)
    out.mkdir(parents=True, exist_ok=True)
    for name, content in dict(archives, **{'atlas.json':encode(atlas)}).items():
        p = out/name
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as stream:
            stream.write(content)
    print(json.dumps(dict(intervals=6, links=12, identity_cover=True, Gate7_closed=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    run(parser.parse_args().out)

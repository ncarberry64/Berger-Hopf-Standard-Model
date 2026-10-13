"""Consume new action records without changing any observable contribution."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
TABLE = Path('artifacts/muon_observable_combination_20261011/contribution_error_table.json')
REPORT = Path('theory/muon_coupled_birth_normal_domain_matching_20261012.md')


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def advance(records, output):
    out = (ROOT/output).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise ValueError('new receipt inside this checkout required')
    d = json.loads((ROOT/TABLE).read_bytes())
    original_rows = json.dumps(d['contribution_and_error_table'], sort_keys=True)
    before = digest(ROOT/TABLE)
    evidence = d['active_projected_matching_diagnostics']['coupled_birth_normal_domain_matching']
    added = {}
    for rel in records:
        p = (ROOT/rel).resolve()
        if not p.is_relative_to(ROOT) or p.name != 'result.json':
            raise ValueError('explicit executed action result required')
        r = json.loads(p.read_bytes())
        name = p.parent.parent.name
        row = dict(path=p.relative_to(ROOT).as_posix(), sha256=digest(p), classification=r['classification'])
        evidence['records'][name] = row
        d['input_hashes'][row['path']] = row['sha256']
        added[name] = row
    evidence['report'] = dict(path=REPORT.as_posix(), sha256=digest(ROOT/REPORT))
    d['input_hashes'][REPORT.as_posix()] = digest(ROOT/REPORT)
    evidence['unsewn_partial_D5_boundary_return_is_not_physical_transmission'] = True
    evidence['proper_normal_state_and_phase_rate_source_contacts_retained'] = True
    if d['completed_local_subtotal'] != 0.0011659186179552334 or json.dumps(d['contribution_and_error_table'], sort_keys=True) != original_rows:
        raise ValueError('all evaluated contribution/error rows must remain unchanged')
    if any(d[k] is not None for k in ('complete_a_mu','complete_g_mu','complete_magnetic_moment')):
        raise ValueError('physical normalization and complete observable not supplied')
    out.mkdir(parents=True)
    (ROOT/TABLE).write_text(json.dumps(d, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    receipt = dict(classification='EXECUTED_SAME_LEDGER_ACTION_CONSUMPTION_WITH_OBSERVABLE_ROWS_PRESERVED',
        argv=[sys.executable, *sys.argv], before_table_sha256=before, after_table_sha256=digest(ROOT/TABLE),
        added_records=added, current_report=evidence['report'], source_sha256=digest(Path(__file__)),
        contribution_and_local_uncertainty_rows_unchanged=True, local_subtotal=d['completed_local_subtotal'],
        physical_native_remainder=None, complete_a_mu=None, complete_g_mu=None, complete_uncertainty=None,
        error_scope='Matching/action/domain diagnostics only. No source norm, surface work or algebraic residual becomes an additive anomaly contribution or an uncertainty bound.')
    p = out/'verification.json'
    p.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(records=len(added), local_subtotal=d['completed_local_subtotal'], verification_sha256=digest(p))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    advance(args.record, args.output)

"""Collect additive finite projection replay identities without rewriting inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'artifacts/muon_calibrated_finite_projection_ledger_20261010/verification.json'


def identity(path):
    data = path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest())


def main():
    record = json.loads(OUTPUT.read_text(encoding='utf8')) if OUTPUT.exists() else {}
    left, right = (OUTPUT.parent / f'run_{i}/finite_projection_ledger.json' for i in (1, 2))
    if left.read_bytes() != right.read_bytes():
        raise ValueError('additive finite projection replay mismatch')
    packet = json.loads(left.read_text(encoding='utf8'))
    record.update(byte_identical=True, replay=[identity(left), identity(right)],
        producer_hashes=[identity(ROOT/'scripts/evaluate_muon_calibrated_finite_projection_ledger.py'),
                         identity(Path(__file__))],
        evaluated_subtotal=packet['evaluated_subtotal'],
        scientific_classification=packet['status'],
        g_subtotal=packet['input_uncertainty']['mu_plus']['plus']['accounting']['g_mu'],
        signed_moment_subtotal={charge:packet['input_uncertainty'][charge]['plus']['accounting']
            ['magnetic_moment_Sz_plus_hbar_over_2_J_per_T'] for charge in ('mu_plus','mu_minus')},
        complete_observable=False, native_remainder_enclosed=False,
        focused_math_verification='The independently integrated finite W/Hgamma producer has its own verification and 18 focused tests; this script only adds signed common-source accounting.')
    OUTPUT.write_text(json.dumps(record, sort_keys=True, indent=2, allow_nan=False)+'\n',
                      encoding='utf8', newline='\n')
    print(json.dumps(dict(byte_identical=True, verification=identity(OUTPUT)), sort_keys=True))


if __name__ == '__main__':
    main()

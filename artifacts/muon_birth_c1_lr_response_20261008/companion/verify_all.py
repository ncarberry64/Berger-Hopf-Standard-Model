#!/usr/bin/env python3
"""Replay the C1 LR reduction and carrier bounds using only stdlib Python.

Run from any working directory. This writes no repository files. Optional
--out names a directory for the deterministic results and their SHA-256 hash.
The supplied finite controls verify mathematics; physical C1 operands are not
filled by those controls.
"""
import argparse
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def execute(name):
    result = subprocess.run([sys.executable, str(ROOT/name)], check=True,
                            capture_output=True, text=True)
    return json.loads(result.stdout)


def source_crosscheck(bounds, source_root=None):
    manifest = json.loads((ROOT/'pinned_source_manifest.json').read_text())
    if source_root is None:
        return {'pinned_source_files_verified': 0,
                'source_byte_verification_performed': False,
                'coefficient_inputs_match_exactly': None,
                'reference_commit': manifest['commit'],
                'note': 'Arithmetic replay uses the pinned constants; pass --source-root to verify repository source bytes.'}
    base = source_root
    for row in manifest['sources']:
        raw = (base/row['path']).read_bytes()
        # Accept a Git checkout's LF/CRLF working-tree convention, without
        # editing it. One representation must match BOTH pinned hashes exactly.
        lf = raw.replace(b'\r\n', b'\n')
        candidates = (raw, lf, lf.replace(b'\n', b'\r\n'))
        match = any(hashlib.sha256(c).hexdigest() == row['sha256']
                    and hashlib.sha1(b'blob '+str(len(c)).encode()+b'\0'+c).hexdigest() == row['git_blob_sha1']
                    for c in candidates)
        if not match:
            raise ValueError('Pinned source content changed: '+row['path'])
    af = json.loads((base/'artifacts/flagship_integration/BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json').read_text(), parse_float=Decimal)
    nf = json.loads((base/'artifacts/flagship_integration/BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json').read_text(), parse_float=Decimal)
    if not (af['validation_passed'] and nf['validation_passed']):
        raise ValueError('Inherited input lacks its validation flag')
    family = af['amplitude_family']
    rows = [r for r in nf['factorized_product_Dirac_rows']
            if Fraction(r['absolute_unit_radius_eigenvalue']) == Fraction(3, 2)]
    if len(rows) != 1:
        raise ValueError('Retained lowest channel is not unique')
    row = rows[0]
    probes = [p for p in row['negative_axis_samples'] if Fraction(p['kappa_squared']) == 1]
    if len(probes) != 1 or Fraction(probes[0]['z']) != -1:
        raise ValueError('Retained negative-axis probe is not unique')
    observed = {
        'lambda_star': Fraction(family['parameter_domain'].split('<=')[1]),
        'original_a_upper': Fraction(family['duration_lambda_squared_coefficient_interval'][1]),
        'edge_duration_upper': Fraction(family['endpoint_proof_edge_duration_interval'][1]),
        'superpotential_upper': Fraction(row['incoming_superpotential_absolute_upper']),
        'kappa_squared': Fraction(probes[0]['kappa_squared']),
    }
    declared = {k:Fraction(v) for k,v in bounds['source_decimal_inputs'].items()}
    if observed != declared:
        raise ValueError('Carrier-bound constants do not match pinned source')
    if family['parameter_domain'] != nf['parametric_theorem']['amplitude_domain']:
        raise ValueError('Retained amplitude domains disagree')
    return {'pinned_source_files_verified': len(manifest['sources']),
            'source_byte_verification_performed': True,
            'coefficient_inputs_match_exactly': True,
            'reference_commit': manifest['commit']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--source-root', type=Path,
                        help='Optional existing repository or exact source snapshot at the pinned commit')
    args = parser.parse_args()
    response = execute('response_reduction_verify.py')
    car = execute('car_reduction_verify.py')
    scalar = execute('scalar_reduction_verify.py')
    bounds = execute('response_carrier_bounds.py')
    sources = source_crosscheck(bounds, args.source_root)
    count = response['controls_passed']+car['checks_passed']+scalar['checks_passed']
    result = {
        'schema': 'BHSM_C1_LR_REDUCTION_AND_CARRIER_INTERIOR_BOUNDS_V1',
        'status': 'NEW_CARRIER_RESPONSE_BOUNDS_AND_LOCAL_LR_REDUCTION;_INCOMING_HIGGS_BINDING_OPEN',
        'reference_commit': sources['reference_commit'],
        'exact_control_groups_passed': count,
        'source_verification': sources,
        'response_reduction_controls': response,
        'local_CAR_controls': car,
        'scalar_response_controls': scalar,
        'new_carrier_bounds': bounds,
        'physical_status': {
            'incoming_H_C1': None,
            'incoming_consumed_Higgs_variation': None,
            'incoming_active_Higgs_domain_and_source_binding': None,
            'actual_LR_same_quadratic_form_perturbation': None,
            'actual_LR_perturbation_norm_and_variation': None,
            'complete_E1_kernel': None,
            'complete_CAR_verdict': None,
            'minimal_physical_moment_rank': None,
            'physical_a_mu': None,
            'physical_g_mu': None,
            'physical_member_selection_proved_necessary': False,
            'physical_member_or_covariance_selected': False,
        },
    }
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    raw = text.encode('utf-8')
    summary = {'exact_control_groups_passed': count,
               'source_files_verified': sources['pinned_source_files_verified'],
               'result_bytes': len(raw),
               'result_sha256': hashlib.sha256(raw).hexdigest(),
               'physical_LR_enclosure': 'UNEVALUATED',
               'physical_a_mu_and_g_mu': 'UNEVALUATED'}
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out/'results.json').write_bytes(raw)
        (args.out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

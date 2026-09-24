"""Adjudicate the reproduced all-input local block against global Gate 7.

The local two-radius test and the full-history physical requirements are
separate assertions. An unsuccessful upper bound is not a counterexample.
"""
import argparse
from fractions import Fraction
import gzip
import json
from pathlib import Path
import sys
from flint import ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts')]
import audit_n12_gate7_vector_global_readiness as inherited
import verify_n12_gate7_coupled_transport_bounds as replay


def evaluate(evidence_root, transport, reproduction, verification):
    result = inherited.evaluate(evidence_root)
    owner_path = evidence_root / ('artifacts/flagship_integration/'
        'BHSM_N12_GATE7_FINAL_EXACT_CENTER_FORCE_KKT_HESSIAN_VERDICT.json')
    owner = json.loads(owner_path.read_bytes())
    if (owner['validation_passed'] is not True
            or owner['Gate7_verdict']['geometric_connection_or_stop_owner'] != 'CLOSED_BY_CANONICAL_FIRST_STOP'
            or owner['composition']['actual_projected_force_covector'] != 'NOT_MATERIALIZED'):
        raise ValueError('force/first-stop authority changed; reconcile the new owner result')
    record_path = transport / 'record.json'
    constants_path = transport / 'constants.json.gz'
    record = json.loads(record_path.read_bytes())
    receipt = json.loads(reproduction.read_bytes())
    check = json.loads(verification.read_bytes())
    digest = inherited.sha(record_path.read_bytes())
    constants_digest = inherited.sha(constants_path.read_bytes())
    producer = ROOT / 'scripts/certify_n12_gate7_coupled_vector_transport.py'
    verifier = Path(replay.__file__)
    if (receipt['transport']['byte_identical'] is not True
            or receipt['transport']['independent_transport_arithmetic'] is not True
            or receipt['transport']['SHA256']['record.json'] != digest
            or receipt['transport']['SHA256']['constants.json.gz'] != constants_digest
            or record['constant_models_SHA256'] != constants_digest
            or record['source_hashes']['evaluator'] != inherited.sha(producer.read_bytes())
            or check['record_SHA256'] != digest
            or check['constants_SHA256'] != constants_digest
            or check['verifier_SHA256'] != inherited.sha(verifier.read_bytes())):
        raise ValueError('reproduced local arithmetic and its exact norm replay required')
    for name in ('midpoint', 'endpoint'):
        numerical = receipt['velocity_models'][name]
        if (numerical['numerical_payloads_byte_identical'] is not True
                or numerical['fresh_residual_arithmetic'] is not True
                or numerical['immutable_action_derivatives_reused'] is not True
                or numerical['action_derivatives_recomputed'] is not False):
            raise ValueError('explicit complete numerator reproduction scope required')
        family_checks = []
        for which in ('first', 'repeat'):
            path = reproduction.parent / f'{name}_complete_verification_{which}.json'
            payload = path.read_bytes()
            family_check = json.loads(payload)
            if (inherited.sha(payload) != numerical[f'{which}_verification_SHA256']
                    or family_check['all_61_component_bounds_replayed'] is not True
                    or len(family_check['numerical_component_SHA256']) != 61
                    or family_check['canonical_numerical_set_SHA256'] != numerical['canonical_numerical_set_SHA256']):
                raise ValueError('complete source-bound numerator verification pair required')
            family_checks.append(family_check)
            result['source_hashes'][f'{name}_{which}_numerator_verification'] = inherited.sha(payload)
        if (family_checks[0]['numerical_component_SHA256'] != family_checks[1]['numerical_component_SHA256']
                or family_checks[0]['record_SHA256'] != record['source_hashes'][name + '_corrected_record']):
            raise ValueError('reproduced numerator coefficients must be those used in transport')
    actual = replay.verify(record, json.loads(gzip.decompress(constants_path.read_bytes())))
    if any(check.get(key) != value for key, value in actual.items()):
        raise ArithmeticError('local norm verification receipt does not replay')
    bounds = record['local_fixed_axis_two_radius_majorant']
    weighted = [Fraction(item['exact']) for item in bounds['weighted_row_bounds']]
    norm = Fraction(record['complete_local_right_block_norm_upper']['exact'])
    weighted_pass = max(weighted) < 1
    local = dict(interval=13, side='right', physical_input_columns=74,
                 projected_output_rows=74, enclosure_status='CERTIFIED',
                 norm_upper_exact=str(norm), norm_margin_lower_exact=str(1-norm),
                 strict_Euclidean_gain_below_one=norm < 1,
                 original_trial_radii_exact=bounds['original_trial_radii_exact'],
                 fixed_axis_two_radius_majorant=bounds['bounds'],
                 weighted_row_bounds_exact=[str(v) for v in weighted],
                 weighted_margin_lower_exact=str(1-max(weighted)),
                 strict_local_weighted_gain_below_one=weighted_pass,
                 arithmetic_reproduced=True, original_action_derivatives_reused=True,
                 all_history_intervals_covered=False,
                 physical_quotient_identification_inferred=False)
    if weighted_pass:
        obstruction = ('The interval-13 right block is bounded in the retained fixed-axis '
                       'two-radius norm. A same-map uniform enclosure is still required '
                       'for its left input block and the other 369 intervals, together '
                       'with physical branch/quotient identification and the retained '
                       'global self-map and contraction inequalities.')
    else:
        obstruction = ('The complete interval-13 right-block enclosure does not yet '
                       'certify strict contraction in the original two-radius norm: '
                       'its largest weighted row upper bound is ' + str(float(max(weighted)))
                       + '. This is an unresolved enclosure bound, not a proof that '
                       'the retained physical realization violates contraction.')
    result.update(algorithm='COMPLETE_LOCAL_VECTOR_TO_GLOBAL_GATE7_AUTHORITY_AUDIT_V2',
                  evaluator_SHA256=inherited.sha(Path(__file__).read_bytes()),
                  local_full_input_block=local, full_input_basis_certified=True,
                  full_input_basis_scope='interval 13, right block only',
                  exact_remaining_numerical_obstruction=obstruction,
                  full_history_physical_contraction_certified=False,
                  certified_canonical_first_stop_retained=True,
                  remaining_force_oracle_arrays=owner['missing_force_oracle_arrays'],
                  remaining_physical_Hessian_arrays=owner['missing_Hessian_arrays'],
                  physical_violation_proved=False, completion_audit_started=False,
                  Gate7_verdict='OPEN — SPECIFIC REMAINING OBSTRUCTION',
                  BHSM_status='OPEN', Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    result['source_hashes'].update({
        'complete_local_transport_record': digest,
        'complete_local_transport_constants': constants_digest,
        'complete_local_reproduction': inherited.sha(reproduction.read_bytes()),
        'complete_local_norm_verification': inherited.sha(verification.read_bytes()),
        'final_exact_center_force_KKT_Hessian_owner': inherited.sha(owner_path.read_bytes()),
        'inherited_global_requirement_evaluator': inherited.sha(Path(inherited.__file__).read_bytes()),
        'complete_local_transport_evaluator': inherited.sha(producer.read_bytes()),
        'complete_local_norm_verifier': inherited.sha(verifier.read_bytes())})
    return result


def main():
    parser = argparse.ArgumentParser()
    for name in ('evidence-root', 'transport', 'reproduction', 'verification', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('fresh global adjudication required')
    ctx.prec = 512
    result = evaluate(args.evidence_root.resolve(), args.transport.resolve(),
                      args.reproduction.resolve(), args.verification.resolve())
    args.out.write_bytes(inherited.encoded(result))
    print(json.dumps(dict(Gate7_verdict=result['Gate7_verdict'],
                          local_weighted_pass=result['local_full_input_block']['strict_local_weighted_gain_below_one'],
                          global_radii_passed=result['global_radii_passed'],
                          global_radii_total=result['global_radii_total'])))


if __name__ == '__main__':
    main()

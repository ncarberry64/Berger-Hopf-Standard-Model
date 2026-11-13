"""Update only matching evidence in the sole observable contribution ledger."""
from pathlib import Path
from hashlib import sha256
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
TABLE = Path('artifacts/muon_observable_combination_20261011/contribution_error_table.json')
MARKDOWN = TABLE.with_suffix('.md')
REPORT = Path('theory/muon_coupled_birth_normal_domain_matching_20261012.md')
RECORDS = {
    'complete_finite_work_consumption': 'artifacts/muon_corrected_finite_fiber_work_20261012/run_1/result.json',
    'bounded_material_parent_control': 'artifacts/muon_positive_parent_material_control_20261012/run_1/result.json',
    'normal_flow_and_domain_returns': 'artifacts/muon_sigma_normal_collar_transport_20261012/trial_0000_run_2/result.json',
    'actual_reached_complex_action': 'artifacts/muon_reached_complex_normal_history_20261012/trial_0000_run_1/result.json',
}


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def update(output):
    out = (ROOT/output).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise ValueError('new execution receipt inside this checkout required')
    d = json.loads((ROOT/TABLE).read_bytes())
    if d['completed_local_subtotal'] != 0.0011659186179552334:
        raise ValueError('preserve the current matched local subtotal')
    retained = {k:d[k] for k in ('contribution_and_error_table', 'completed_local_subtotal',
        'completed_local_subtotal_g', 'completed_local_uncertainty_contract')}
    before = {str(p):digest(ROOT/p) for p in (TABLE, MARKDOWN,
        Path('docs/frozen_predictions.md'), Path('docs/frozen_predictions.json'))}
    records = {}
    for name, rel in RECORDS.items():
        r = json.loads((ROOT/rel).read_bytes())
        records[name] = dict(path=rel, sha256=digest(ROOT/rel), classification=r['classification'])
    work = json.loads((ROOT/RECORDS['complete_finite_work_consumption']).read_bytes())
    control = json.loads((ROOT/RECORDS['bounded_material_parent_control']).read_bytes())
    original = json.loads((ROOT/RECORDS['actual_reached_complex_action']).read_bytes())
    evidence = dict(
        classification='EVALUATED_ACTION_AND_DOMAIN_CORRECTIONS_WITH_PHYSICAL_MATCHING_UNADMITTED',
        records=records, report=dict(path=REPORT.as_posix(), sha256=digest(ROOT/REPORT)),
        original_birth226_residual_max=work['original_base_birth226_max'],
        complete67_finite_work_max=work['complete_work_max'],
        stored_response_correction_to_work_max=work['corrected_minus_binary_complete_work_max'],
        complete106_terminal_return_norm=work['full_terminal106_norm'],
        bounded_parent_control146_max=control['original146_max'],
        original_reached_complex_action_guard=original['original_action_rows_guard'],
        reached_complex_steps_and_endpoints_passed=original['all_steps_and_endpoints_passed'],
        actual_current_frame_correction=original['actual_endpoint_comparison'],
        generated_past_full_internal_data_are_not_fixed_physical_environment=True,
        finite_terminal_zero_or_temporal_zero_Cauchy_source_return_is_not_outgoing_DtN=True,
        partial_normal_integral_is_not_complete_normalization=True,
        current_operator_response_and_domain_corrections_not_grafted_across_backgrounds=True,
        physical_birth_formation_energy_gamma_exterior_match_admitted=False,
        physical_pole_charge_residue_or_normalized_Pauli_admitted=False,
        native_remainder=None, total_a_mu=None, total_g_mu=None, total_uncertainty=None,
        error_scope='Executed same-action finite candidate/control residuals and reached complex current/frame/domain corrections. No conversion of these quantities into anomaly contributions or uncertainty allowances; no definition gap or physical underdetermination inferred.')
    d['active_projected_matching_diagnostics']['coupled_birth_normal_domain_matching'] = evidence
    d['input_hashes'].update({rel:digest(ROOT/rel) for rel in (*RECORDS.values(), REPORT.as_posix())})
    d['refinement_priority'] = ('Solve the common-source nonlinear birth/natural/formation/energy/gamma/exterior matching and consume the corrected normal/current/frame domain in the physical pole/Pauli combination. Stored-work arithmetic changes are negligible for the executed work; no production heat refinement or observable error inferred from matrix/contour residuals.')
    if any(d[k] != v for k,v in retained.items()):
        raise ValueError('matching evidence must preserve all contribution and uncertainty rows')
    if any(d[k] is not None for k in ('complete_a_mu', 'complete_g_mu', 'complete_magnetic_moment')):
        raise ValueError('no complete observable supplied by this application')
    text = (ROOT/MARKDOWN).read_text(encoding='utf8')
    tag = '## Coupled birth and normal-domain action applications'
    if tag in text:
        raise ValueError('preserve earlier accounting edits; use a new reviewed update')
    text += ('\n'+tag+'\n\n'
        'The matched local subtotal remains **0.0011659186179552334**. '
        'The actual complex continuation passes its original action equations, '
        'but complete natural/formation/energy/gamma/exterior matching and physical '
        'pole/residue normalization remain unadmitted. Its material current/frame '
        'correction is retained in the existing native consumer; it is not an '
        'additive anomaly row. The corrected complete67 work changes by only '
        '8.435421026188149e-12, while the finite work and full terminal return remain '
        'nonzero. Partial normal integrals and real-linear interpolation returns '
        'do not supply physical normalization or an observable uncertainty.\n\n'
        'The existing disjoint native and surviving weak/quark rows, complete '
        'a_mu, g_mu and total uncertainty remain null. See '
        '[the executed action/domain report](../../theory/muon_coupled_birth_normal_domain_matching_20261012.md) '
        'for actual operands, residuals, commands, hashes and the five scientific classifications.\n')
    out.mkdir(parents=True)
    (ROOT/TABLE).write_text(json.dumps(d, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    (ROOT/MARKDOWN).write_text(text, encoding='utf8', newline='\n')
    after = {str(p):digest(ROOT/p) for p in (TABLE, MARKDOWN,
        Path('docs/frozen_predictions.md'), Path('docs/frozen_predictions.json'))}
    record = dict(classification='EXECUTED_MATCHING_EVIDENCE_UPDATE_PRESERVING_SOLE_CONTRIBUTION_LEDGER',
        argv=['C:/Python314/python.exe', 'scripts/update_muon_coupled_birth_matching_accounting.py', '--output', str(output)],
        before_hashes=before, after_hashes=after,
        all_contribution_rows_and_local_uncertainty_preserved=True,
        frozen_predictions_unchanged=all(before[str(p)] == after[str(p)] for p in
            (Path('docs/frozen_predictions.md'),Path('docs/frozen_predictions.json'))),
        source_sha256=digest(Path(__file__)), records=records,
        supported_complete_a_mu=None, supported_complete_g_mu=None, supported_total_uncertainty=None,
        error_scope=evidence['error_scope'])
    p = out/'verification.json'
    p.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(local_subtotal=d['completed_local_subtotal'],
        frozen_predictions_unchanged=record['frozen_predictions_unchanged'], verification_sha256=digest(p))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    update(parser.parse_args().output)

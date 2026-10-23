"""Bind new regular-interface applications without admitting physical gates.

Repeating this binder checks serialization only. Independent numerical runs
are separately executed and must already exist, with identical exact bytes.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root/'artifacts/muon_regular_birth_response_20261015'
    pins = {}
    checks=json.loads((base/'publication_checks/results.json').read_bytes())
    if len(checks) != 5 or any(check['exit_code'] != 0 for check in checks.values()):
        raise ValueError('The five publication audit commands must complete successfully')

    def pin(path):
        path = Path(path)
        digest = sha256(path.read_bytes()).hexdigest()
        pins[path.relative_to(root).as_posix()] = digest
        return digest

    pairs = []
    for name in ('spatial_jet', 'actual_scalar', 'finite_curvature_memory'):
        a, b = (base/f'{name}_run_{i}' for i in (1, 2))
        if not a.is_dir() or not b.is_dir():
            raise FileNotFoundError(f'Independent numerical pair missing: {name}')
        left = {p.relative_to(a).as_posix():p for p in a.rglob('*') if p.is_file()}
        right = {p.relative_to(b).as_posix():p for p in b.rglob('*') if p.is_file()}
        if left.keys() != right.keys():
            raise ValueError(f'Independent file lists differ: {name}')
        digests = {}
        for key, path in left.items():
            if path.read_bytes() != right[key].read_bytes():
                raise ValueError(f'Independent numerical outputs differ: {name}/{key}')
            digests[key] = pin(path)
            pin(right[key])
        result = json.loads((a/'result.json').read_bytes())
        for rel, expected in result.get('input_hashes', {}).items():
            if pin(root/rel) != expected:
                raise ValueError(f'Input changed after numerical application: {rel}')
        pairs.append(dict(kind=name, files=digests,
            scope=('manufactured spatial-map controls' if name=='spatial_jet' else
                   'actual saved complex candidate scalar identities' if name=='actual_scalar' else
                   'actual older real finite phase only; not current candidate or future tail')))

    spatial=json.loads((base/'spatial_jet_run_1/result.json').read_bytes())
    scalar=json.loads((base/'actual_scalar_run_1/result.json').read_bytes())
    if spatial['public_api_sha256'] != pin(root/'src/bhsm/interface/muon_worldvolume_spatial_birth_jet.py'):
        raise ValueError('Independent runs did not use the published API bytes')
    if spatial.get('physical_outgoing_derivative_gate_passed') is not False:
        raise ValueError('Manufactured controls must not admit physical gate')
    if scalar.get('physical_outgoing_derivative_pass_2e10') is not False:
        raise ValueError('Coordinate scalar identities must not admit physical gate')
    memory=json.loads((base/'finite_curvature_memory_run_1/result.json').read_bytes())
    if memory.get('physical_outgoing_energy_field_derivative_gate_passed') is not False:
        raise ValueError('Finite curvature application must not admit physical gate')
    if memory.get('current_complex_trial0000_consumed') is not False:
        raise ValueError('The historical real phase is distinct from current complex candidate')
    for result, source, key in (
        (spatial, 'bhsm_muon_worldvolume_spatial_one_jet_20261016.py', 'source_sha256'),
        (scalar, 'bhsm_intrinsic_scalar_direct_conormal_20261015.py', 'producer_sha256'),
        (memory, 'bhsm_muon_finite_connection_memory_20261015.py', 'producer_sha256'),
    ):
        if pin(root/'audits'/source) != result[key]:
            raise ValueError(f'Numerical producer changed: {source}')

    cut=root/'artifacts/muon_baton_zoo_maximal_current_realization_20261013/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
    if pin(cut) != 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b':
        raise ValueError('Authoritative retained matching cut changed')
    owners=(
        'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        'src/bhsm/interface/muon_intrinsic_coupled_primal.py',
        'src/bhsm/interface/muon_intrinsic_worldvolume_scalar_transport.py',
        'src/bhsm/interface/muon_intrinsic_scalar_birth_rows.py',
        'src/bhsm/interface/gauge_connection_reset_bundle_lift_adjudication.py',
        'src/bhsm/interface/muon_matched_mechanical_source.py',
        'src/bhsm/interface/muon_birth_phase_continuation.py',
    )
    for rel in owners:
        pin(root/rel)
    for rel in (
        'audits/bhsm_muon_worldvolume_spatial_one_jet_20261016.py',
        'audits/bhsm_intrinsic_scalar_direct_conormal_20261015.py',
        'audits/bhsm_muon_finite_connection_memory_20261015.py',
        'audits/bhsm_muon_regular_birth_binding_20261015.py',
        'tests/test_muon_worldvolume_spatial_birth_jet.py',
    ):
        pin(root/rel)
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pin(path)
    result=dict(
        classification='REGULAR_MUON_SAME_E1_LAW_CONSTRUCTION_WITH_UNEVALUATED_PHYSICAL_OUTGOING_APPLICATION',
        correction='The current regular mechanics already own gauge/scalar birth incidence; earlier blanket undefined-reset-law claims were too broad. No historical packet is rewritten.',
        scientific_repeat_pairs=pairs,
        finite_control_metrics=dict(
            spatial_five_point_max=max(max(row['finite_five_point_spatial_derivative_max'].values()) for row in spatial['fixtures']),
            actual_scalar_conormal_max=max(row['momentum_identity_max_absolute_error'] for row in scalar['records']),
            actual_scalar_conormal_coefficient_derivative_relative_max=max(row['independent_conormal_first_jet_relative_error'] for row in scalar['records']),
            historical_real_connection_memory_norm=memory['volterra_connection_memory_norm'],
            historical_real_nonzero_temporal_commutator_memory_norm=memory['nonzero_temporal_commutator_memory_norm'],
            historical_real_direct_vs_volterra_absolute=memory['direct_vs_volterra_max_difference'],
        ),
        manifest_repeat_is_independent_scientific_solve=False,
        intrinsic_Higgs_and_bare_algebraic_HS_distinguished=True,
        nonzero_scalar_temporal_connection_and_spin_terms_preserved=True,
        physical_outgoing_solution_evaluated=False,
        physical_energy_field_and_moving_domain_derivative_evaluated=False,
        full_physical_derivative_gate_passed_2e_minus_10=False,
        physical_radial_convergence_established=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None,
        physical_muon_magnetic_moment=None,
        original_Maxwell_after_correction=None,
        original_226_rows_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_best_before_original226_max=9.602842247524184e-7,
        retained_best_before_original226_row='226 common_normal_temporal_dual[0]',
        gate_tolerance=2e-10,
        input_and_publication_hashes=dict(sorted(pins.items())),
    )
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',
                   encoding='utf-8',newline='\n')
    print(json.dumps(dict(output=out.name, sha256=sha256(out.read_bytes()).hexdigest(),
        numerical_repeat_pairs=len(pairs), physical_derivative_pass=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    bind(args.repository,args.output)

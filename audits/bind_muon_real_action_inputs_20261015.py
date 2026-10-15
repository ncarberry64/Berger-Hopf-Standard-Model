"""Bind exact local diagnostics; do not admit any physical prediction gate."""
from pathlib import Path
from hashlib import sha256
import argparse
import json


def bind(repository, output):
    root, out=Path(repository).resolve(),Path(output).resolve()
    if out.exists(): raise FileExistsError(out)
    base=root/'artifacts/muon_real_action_inputs_20261015'
    pins={}
    def pin(path):
        digest=sha256(path.read_bytes()).hexdigest()
        pins[path.relative_to(root).as_posix()]=digest
        return digest
    pairs=[]
    results={}
    for name,producer in (
        ('parameter_contacts','bhsm_real_phase_parameter_contacts_20261015.py'),
        ('scalar_cauchy_direction','bhsm_muon_real_cauchy_radial_direction_20261015.py'),
    ):
        left,right=(base/f'{name}_run_{i}' for i in (1,2))
        names={p.name for p in left.iterdir() if p.is_file()}
        if names != {p.name for p in right.iterdir() if p.is_file()}:
            raise ValueError('Independent numerical file lists differ')
        files={}
        for filename in sorted(names):
            a,b=left/filename,right/filename
            if a.read_bytes()!=b.read_bytes(): raise ValueError(f'Nonidentical numerical pair: {name}/{filename}')
            files[filename]=pin(a)
            pin(b)
        result=json.loads((left/'result.json').read_bytes())
        if result['producer_sha256'] != pin(root/'audits'/producer):
            raise ValueError('Numerical producer differs from published source')
        for group in ('input_hashes','owner_hashes'):
            for rel,expected in result.get(group,{}).items():
                if pin(root/rel)!=expected: raise ValueError(f'Input changed: {rel}')
        results[name]=result
        pairs.append(dict(kind=name,files=files,physical_history_solve=False))
    contact=results['parameter_contacts']
    radial=results['scalar_cauchy_direction']
    assert contact['real_physical_stationary_history_constructed'] is False
    assert contact['coupled_matching_corrections_applied']==0
    assert radial['physical_full_outgoing_derivative_passed'] is False
    assert radial['full_gravity_or_Maxwell_constraint_family_established'] is False
    assert radial['coupled_corrections']==0
    assert radial['physical_two_spin_normalization'] is None
    assert contact['physical_muon_moment'] is None
    checks=json.loads((base/'publication_checks/results.json').read_bytes())
    if len(checks)!=5 or any(c['exit_code']!=0 for c in checks.values()):
        raise ValueError('Five publication audit commands must succeed')
    cut=root/'artifacts/muon_baton_zoo_maximal_current_realization_20261013/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
    if pin(cut)!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b':
        raise ValueError('Authoritative original matching cut changed')
    for filename in (
        'aether_unified_m5_m4_pushforward_v15_69.py',
        'ae4_stratified_dirac_zeta_induced_owner.py',
        'ae4_current_c2_hs_frechet_hessian.py',
        'ae31_c2_intrinsic_m4_lepton_action.py',
        'muon_intrinsic_coupled_primal.py',
        'muon_birth_coupled_primal_midpoint.py',
        'muon_parent_gauge_geometry_correction.py',
        'covariant_bubble_interface_mechanics.py',
        'muon_unsquared_physical_boundary_pole.py',
    ):
        pin(root/'src/bhsm/interface'/filename)
    pin(Path(__file__).resolve())
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pin(path)
    result=dict(
        classification='REAL_ACTION_COEFFICIENT_AND_CAUCHY_CONTACTS_WITH_UNINSTANTIATED_PHYSICAL_BACKGROUND',
        scientific_repeat_pairs=pairs,
        binder_repeat_is_independent_physical_or_scientific_solve=False,
        normalized_dimensionless_g_has_no_absolute_unit_gate=True,
        overall_operator_and_spinor_scaling_cancel_from_simple_pole_slope=True,
        dimensionless_action_coefficients_can_be_ignored=False,
        general_Pauli_parameter_dependence_proved=False,
        local_scalar_Gauss_direction_is_full_coupled_solution_family=False,
        intrinsic_pole_requires_collider_history=False,
        actual_local_metrics=dict(
            scalar_partial_lambda_cotangent_norm=[r['partial_lambda_H_action_cotangent_norm'] for r in contact['records']],
            held_gamma_original_cap_area_gradient_norm=[r['geometry_gradient_per_gamma_norm'] for r in contact['records']],
            local_coefficient_FD_max_scaled=max(c[k] for r in contact['records'] for c in r['finite_difference_checks'] for k in ('value_to_gradient_max_scaled_error','gradient_to_Hessian_vector_max_scaled_error')),
            scalar_Gauss_radial_direction_max=radial['all_four_scalar_Gauss_moment_map_direction_max'],
            canonical_radial_energy_quadratic=radial['radial_canonical_energy_polynomial']['quadratic'],
        ),
        physical_real_coupled_background_and_outgoing_fields_evaluated=False,
        full_physical_derivative_passed_at_2e_minus_10=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None,physical_muon_magnetic_moment=None,
        original_Maxwell_after_correction=None,original226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        retained_before_original226_row='226 common_normal_temporal_dual[0]',
        required_original_residual_tolerance=2e-10,
        input_and_publication_hashes=dict(sorted(pins.items())),
    )
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(file=out.name,sha256=sha256(out.read_bytes()).hexdigest(),numerical_pairs=2,physical_solve=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    bind(a.repository,a.output)

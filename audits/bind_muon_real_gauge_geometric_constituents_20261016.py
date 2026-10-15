"""Bind reviewed real gauge, conormal and original geometric spin components."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import xml.etree.ElementTree as ET

from bind_muon_real_coupled_open_operator_20261016 import staged_blobs, digest, read_pair


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root/'artifacts/muon_real_ew_common_forms_20261016'
    specs = {
        'EW_Higgs_FP': ('application_run_', 'forms.npz'),
        'color8_complement': ('color_run_', 'forms.npz'),
        'birth_conormal': ('birth_conormal_run_', 'application.npz'),
        'original_M8_geometric_spin': ('original_m8_run_', 'application.npz')}
    apps, evidence = {}, {}
    for key, (prefix, archive) in specs.items():
        apps[key], evidence[key] = read_pair(base, prefix, archive)
        assert apps[key]['coupled_corrections'] == 0
        assert digest(base/(prefix+'1')/archive) == apps[key]['numerical_sha256']
    ew, color, flux, m8 = (apps[k] for k in specs)
    assert ew['classification'] == 'ACTUAL_REAL_EW4_HIGGS_FP_FROZEN_COEFFICIENT_CELL_FORMS'
    assert ew['offshell_Euler_contact_retained']
    assert not ew['potential_matching_values_selected']
    assert not ew['physical_E_B_full_derivative_at_2e_minus10']
    assert not ew['microscopic_Pstrat_identity']
    assert color['classification'] == 'REAL_SM12_CLASSICAL_EW_COLOR_HIGGS_FP_COMMON_COEFFICIENT_FORMS'
    assert color['zero_color_background_does_not_remove_fluctuations_or_ghosts']
    assert not color['rank16_trace_basis_identified_with_native_D5_or_M8_spin_basis']
    assert not color['M8_spin16_tensor_SM16_or_extra_UV_fermion_copy_added']
    assert not color['measured_coupling_or_new_factor_coefficient_used']
    assert len(color['records']) == 2
    for r in color['records']:
        assert r['common_test_dimension'] == 3440 and r['common_ghost_dimension'] == 960
        assert r['color_one_form_Hessian_nonzero_norm'] > 0
        assert r['color_ghost_Hessian_nonzero_norm'] > 0
        assert r['zero_mixed_blocks_proved_by_direct_sum_trace_and_Higgs_singlet']
        assert r['literal_full_rank16_action_controls']['color_nonabelian_vertices_not_set_zero']
    assert flux['classification'] == 'ACTUAL_REAL_BIRTH_FP_WEIGHTED_CONORMAL_AND_GAUGE_VERTICAL_CONSTITUENTS'
    assert flux['all_internal_four_Lie_components_retained']
    assert flux['same_coordinate_ratios_are_not_total_reset_J']
    assert flux['physical_base_reset_F_B'] is None
    assert flux['ghost_trace_or_conormal_loads'] is None
    assert not flux['physical_derivative_at_2e_minus10_passed']
    assert m8['classification'] == 'ACTUAL_REAL_ORIGINAL_FRAME_M8_GEOMETRIC_EXPRESSION_FOURJET_APPLICATION'
    assert len(m8['records']) == 80
    assert {r['full_geometric_spin_rows'] for r in m8['records']} == {16,80,400}
    assert m8['complete_spin16_retained'] and m8['all_eight_coordinate_directions_retained']
    assert m8['no_adapted_KK_spin_frame_body_mixed']
    assert m8['worst_literal_value_scaled'] < 1e-12
    assert not m8['source_xy_is_physical_E_B_or_outgoing_response']
    assert not m8['native_full_graded_operator_and_domain_completed']
    suite = ET.fromstring((base/'original_m8_tests.xml').read_bytes()).find('testsuite')
    assert suite is not None and suite.attrib['tests']=='4'
    assert suite.attrib['failures']=='0' and suite.attrib['errors']=='0'

    wanted = {}
    for component in apps.values():
        for rel, expected in component['input_and_source_sha256'].items():
            if rel in wanted and wanted[rel] != expected:
                raise ValueError('Consumed source/input disagreement: '+rel)
            wanted[rel] = expected
    blobs = staged_blobs(root, sorted(wanted))
    sources, numeric = {}, {}
    for rel, expected in sorted(wanted.items()):
        raw, blob = (root/rel).read_bytes(), blobs[rel]
        if sha256(raw).hexdigest() != expected:
            raise ValueError('Actual consumed bytes changed: '+rel)
        if rel.endswith('.py'):
            if raw == blob:
                recipe = 'identity'
            elif b'\r\n' not in blob and raw == blob.replace(b'\n',b'\r\n'):
                recipe = 'replace every staged LF with CRLF'
            else:
                raise ValueError('Unreconstructible source: '+rel)
            sources[rel] = dict(actual_consumed_byte_sha256=expected,
                staged_byte_sha256=sha256(blob).hexdigest(), reconstruction=recipe)
        else:
            if raw != blob:
                raise ValueError('Numerical input/index bytes differ: '+rel)
            numeric[rel] = expected
    checks = json.loads((base/'publication_checks/results.json').read_bytes())
    assert len(checks)==5 and all(r['exit_code']==0 for r in checks.values())
    for name, record in checks.items():
        assert digest(base/'publication_checks'/(name+'.log')) == record['log_sha256']
    pins = {p.relative_to(root).as_posix():digest(p) for p in sorted(base.rglob('*'))
            if p.is_file() and not p.name.startswith('publication_manifest_run_')}
    for rel in ('audits/bind_muon_real_gauge_geometric_constituents_20261016.py',
                'audits/bind_muon_real_coupled_open_operator_20261016.py',
                'src/bhsm/interface/muon_original_m8_geometric_expression.py',
                'tests/test_muon_original_m8_geometric_expression.py',
                'artifacts/muon_m8_m5_geometric_operator_20261016/muon_m8_geometric_dirac_hopf_incidence_20261016.txt',
                'artifacts/muon_real_core_precision_domain_20261016/publication_manifest_run_1.json'):
        pins[rel] = digest(root/rel)
    result = dict(classification='REVIEWED_REAL_CLASSICAL_GAUGE_AND_GEOMETRIC_SPIN_CONSTITUENTS',
        independent_control_pairs=evidence, original_M8_component_tests_passed=4,
        five_repository_publication_audits_passed=True,
        full_SM12_classical_test_coordinates=3440, separate_FP_ghost_coordinates=960,
        intrinsic_potential_left_as_exact_action_coefficient_polynomial=True,
        color_fluctuations_and_nonabelian_vertices_retained=True,
        actual_birth_measure_and_conormal_source_firsts_evaluated=True,
        actual_reset_base_map_or_pulled_loads_solved=False,
        original_M8_all_eight_directions_and_geometric_spin16_retained=True,
        original_M8_value_literal_worst_scaled=m8['worst_literal_value_scaled'],
        original_M8_germ_axes=['inside_saved_cell_time','declared_qb0_raw25_partial'],
        physical_outgoing_E_B_source_domain_full_derivative_at_2e_minus10=False,
        common_native_graded_operator_domain_or_force_solved=False,
        physical_radial_space_or_state_convergence=False,
        coupled_matching_corrections_applied=0,
        normalized_physical_two_spin_muon_state=None, muon_magnetic_moment_prediction=None,
        Maxwell_after_correction=None, all226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        required_physical_tolerance=2e-10,
        numerical_input_byte_hashes=numeric, source_byte_reconstruction=sources,
        current_artifact_byte_hashes=dict(sorted(pins.items())))
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(sha256=digest(out),source_pins=len(sources),
                         numeric_pins=len(numeric),artifact_pins=len(pins))))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args();bind(args.repository,args.output)

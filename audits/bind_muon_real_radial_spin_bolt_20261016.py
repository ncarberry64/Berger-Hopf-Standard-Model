"""Bind radial diagnostics, full geometric Spin transport and bolt controls."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import xml.etree.ElementTree as ET

from bind_muon_real_coupled_open_operator_20261016 import staged_blobs,digest,read_pair
from bind_muon_real_changing_gauge_transport_20261016 import archive_bytes


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError(out)
    base=root/'artifacts/muon_real_radial_spin_bolt_20261016'
    previous=root/'artifacts/muon_real_changing_gauge_transport_20261016'
    original=archive_bytes(previous,'stable_time6_run_1/changing_forms.npz')
    assert sha256(original).hexdigest()=='9a132366d729c85ea1d83815a5482fbf6352b117507e9f447abb4c3b7534739d'
    pair=json.loads((base/'radial_pair_verification.json').read_bytes())
    assert len(pair['files'])==13 and pair['no_physical_derivative_or_convergence_claim']
    for item in pair['files']:
        a,b=[(base/f'radial_run_{run}'/item['path']).read_bytes()for run in(1,2)]
        assert a==b and len(a)==item['bytes'] and sha256(a).hexdigest()==item['sha256']
    radial=json.loads((base/'radial_run_1/result.json').read_bytes())
    assert radial['classification']=='EXACT_CACHED_SPARSE_REAL_CHANGING_EW_RADIAL_REFINEMENT'
    assert radial['original_time6_archive_sha256']==sha256(original).hexdigest()
    assert not radial['physical_native_outgoing_or_state_convergence']
    assert radial['coupled_corrections']==0 and len(radial['records'])==6
    final={}
    for row in radial['records']:
        assert len(row['matrix_comparisons'])==15
        assert not row['physical_derivative_or_state_convergence'] and row['coupled_corrections']==0
        path=base/'radial_run_1'/f"{row['side']}_radial{row['radial_order']}"/'forms.npz'
        assert digest(path)==row['numerical_sha256']
        if row['radial_order']==128:
            d=row['matrix_comparisons'];final[row['side']]=d
            assert d['curvature_contact_per_kappa']['max_entry_scaled']<2e-10
            assert d['one_form_Hessian_per_kappa']['max_entry_scaled']<2e-10
            assert d['common_kinetic_Hessian']['max_entry_scaled']<2e-10
            assert d['FP_Hessian_per_kappa']['max_entry_scaled']>2e-10
            assert row['maximum_all_blocks_entry_scaled']>2e-10
    assert set(final)=={'incoming','outgoing'}
    mpraw=(base/'lorenz_MP_run_1.json').read_bytes()
    assert mpraw==(base/'lorenz_MP_run_2.json').read_bytes()
    mp=json.loads(mpraw)
    assert mp['classification']=='MP80_DIAGNOSIS_OF_LORENZ_COMPONENT_PRECISION_ONLY'
    assert mp['original_time6_npz_sha256']==sha256(original).hexdigest()
    assert not mp['full_physical_derivative_pass'] and mp['coupled_corrections']==0
    assert mp['fast_validation_receipt_sha256']==digest(base/'original_fast_validation_receipt.json')
    for row in mp['records']:
        assert row['ghost_Gram_exact_tensor_defect']==[0.,0.]
        assert row['integrated_Gram4_max_absolute']==0.
        assert max(row['ghost_Gram_condition_2'])<400
        assert row['integrated_B_max_absolute']>0.
        for control in row['controls'].values():
            assert control['change_due_to_integrated_G_only']==0.
            assert abs(control['change_due_to_integrated_B_only'])>max(control['old_binary_vs_MP80'],control['new_binary_vs_MP80'])
    for alias,h in mp['input_archive_sha256'].items():
        rel=alias.removeprefix('retained_inputs/fast_validation/')
        assert digest(base/'radial_run_1'/rel)==h
    spin,se=read_pair(base,'geometric_spin_run_','application.npz')
    assert spin['classification']=='ACTUAL_REAL_CHILD_WALL_UNCONTRACTED_M5_GEOMETRIC_SPIN_PARALLEL_TRANSPORT'
    assert spin['full_128_and_384_existing_D5_Clifford_carriers_used']
    assert spin['original_eta_contact_retained_separately']
    assert not spin['original_eta_contact_included_in_Spin_parallel_generator']
    assert spin['angular_connection_kernels_and_full10_primitive_wall_covector_retained']
    assert not spin['full_physical_outgoing_derivative_at_2e_minus10']
    assert spin['physical_initial_Spin_lift'] is None and spin['coupled_corrections']==0
    assert spin['adapted_source_integral_vs_endpoint_rapidity']['relative_to_nonzero']>2e-10
    coframe=max(c['binary_relative_to_nonzero']for c in spin['independent_literal_MP_coframe_precision']['controls'])
    assert coframe<2e-10
    suite=ET.fromstring((base/'spin_unit_tests.xml').read_bytes()).find('testsuite')
    assert suite is not None and suite.attrib['tests']=='4' and suite.attrib['failures']=='0' and suite.attrib['errors']=='0'
    bolt,be=read_pair(base,'bolt_run_','controls.npz')
    assert bolt['classification']=='ORIGINAL_M8_GEOMETRIC_S3_BOLT_SOURCE_CONTROLS'
    assert bolt['normal_slice_dimension']==4 and bolt['surviving_orbit']=='S3_u'
    assert bolt['all_spin16_retained'] and bolt['tangential_u_spectrum_not_cut_off_in_theorem']
    assert not bolt['lorentz_positive_square_ellipticity_claimed']
    assert not bolt['global_outgoing_or_physical_derivative_claimed'] and bolt['coupled_corrections']==0
    assert len(bolt['actual_real_orbit_asymptotic_records'])==24
    assert len(bolt['angular_records'])==5 and len(bolt['unitary_polar_frame_records'])==5

    wanted={}
    def include(items):
        for rel,h in items.items():
            if rel in wanted and wanted[rel]!=h:raise ValueError('Operand disagreement: '+rel)
            wanted[rel]=h
    include(radial['input_and_source_sha256']);include(spin['input_and_source_sha256'])
    include(bolt['source_pins']);include(bolt['exact_input_chunk_pins'])
    include({'audits/bhsm_changing_lorenz_mp_precision_diagnosis_20261016.py':mp['source_sha256'],
        'src/bhsm/interface/muon_parent_mean_causal_action.py':mp['actual_action_factor_source_sha256']})
    blobs=staged_blobs(root,sorted(wanted));sources={};numeric={}
    for rel,h in sorted(wanted.items()):
        raw,blob=(root/rel).read_bytes(),blobs[rel]
        assert sha256(raw).hexdigest()==h,rel
        if rel.endswith('.py'):
            if raw==blob:recipe='identity'
            elif b'\r\n'not in blob and raw==blob.replace(b'\n',b'\r\n'):recipe='replace every staged LF with CRLF'
            else:raise ValueError('Unreconstructible consumed source: '+rel)
            sources[rel]=dict(actual_consumed_byte_sha256=h,staged_byte_sha256=sha256(blob).hexdigest(),reconstruction=recipe)
        else:
            assert raw==blob,rel
            numeric[rel]=h
    citations=json.loads((base/'action_scope_citation_pins.json').read_bytes())
    assert citations['classification']=='READ_ONLY_ACTION_SCOPE_CITATIONS'
    cited_index=staged_blobs(root,sorted(citations['LF_sha256']))
    for rel,h in citations['LF_sha256'].items():
        assert sha256((root/rel).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==h,rel
        assert sha256(cited_index[rel].replace(b'\r\n',b'\n')).hexdigest()==h,rel
    checks=json.loads((base/'publication_checks/results.json').read_bytes())
    assert len(checks)==5 and all(v['exit_code']==0 for v in checks.values())
    for name,record in checks.items():assert digest(base/'publication_checks'/(name+'.log'))==record['log_sha256']
    pins={p.relative_to(root).as_posix():digest(p)for p in sorted(base.rglob('*'))
        if p.is_file()and not p.name.startswith('publication_manifest_run_')}
    indexed=staged_blobs(root,sorted(pins))
    for rel,h in pins.items():assert sha256(indexed[rel]).hexdigest()==h,rel
    for rel in('audits/bind_muon_real_radial_spin_bolt_20261016.py',
               'audits/bind_muon_real_changing_gauge_transport_20261016.py',
               'audits/bind_muon_real_coupled_open_operator_20261016.py',
               'tests/test_muon_m5_geometric_spin_connection.py',
               'artifacts/muon_real_changing_gauge_transport_20261016/publication_manifest_run_1.json'):
        pins[rel]=digest(root/rel)
    result=dict(classification='REAL_FIXED_FORM_RADIAL_DIAGNOSIS_AND_GEOMETRIC_SPIN_BOLT_COMPONENTS',
        paired_radial_files=pair['files'],geometric_spin_independent_pair=se,original_M8_bolt_independent_pair=be,
        Lorenz_MP80_diagnosis_pair_sha256=sha256(mpraw).hexdigest(),
        radial64_to128_entrywise_scaled_all15={side:{name:r['max_entry_scaled']for name,r in d.items()}for side,d in final.items()},
        selected_curvature_and_one_form_quadratures_below_scaled_2e_minus10=True,
        complete15_form_radial_precision_at_2e_minus10=False,
        Lorenz_failure_origin_evaluated_in_integrated_B_not_just_Cholesky_solve=True,
        actual_geometric_wall_spin_value_and_supplied_source_integrals_evaluated=True,
        full_geometric_Spin_carriers_and_angular_variation_kernels_retained=True,
        local_original_M8_regular_S3_bolt_geometric_plus_form_H1_constructed=True,
        local_form_result_is_a_full_native_or_Lorentz_positive_square_domain=False,
        five_repository_publication_audits_passed=True,geometric_spin_component_tests_passed=4,
        complete_physical_operator_domain_and_coefficients_matched=False,
        physical_outgoing_E_B_source_domain_derivative_at_2e_minus10=False,
        coupled_matching_corrections_applied=0,physical_normalized_spins=None,muon_magnetic_moment_prediction=None,
        Maxwell_after_correction=None,original226_after_correction=None,
        retained_before_Maxwell=2.4777309846820184,retained_before_original226_max=9.602842247524184e-7,
        required_physical_tolerance=2e-10,numerical_input_byte_hashes=numeric,
        separately_read_only_action_citation_LF_sha256=citations['LF_sha256'],
        source_byte_reconstruction=sources,current_artifact_byte_hashes=dict(sorted(pins.items())))
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(sha256=digest(out),source_pins=len(sources),numeric_pins=len(numeric),artifact_pins=len(pins))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

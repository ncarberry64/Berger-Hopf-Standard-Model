"""Index-bind actual native coefficients, source corner and birth Legendre data."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
from xml.etree import ElementTree
from bind_muon_real_coupled_open_operator_20261016 import staged_blobs


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent index binding')
    base=root/'artifacts/muon_actual_native_coefficients_source_completion_20261016'
    selection=json.loads((base/'packet_selection.json').read_bytes())
    aliases=json.loads((base/'consumed_input_aliases.json').read_bytes())

    def reconstructed(receipt,stage=None):
        if 'path'in receipt:
            p=root/receipt['path'];raw=p.read_bytes()
        else:
            blocks=[]
            for c in receipt['raw_byte_concatenation']:
                b=(root/c['path']).read_bytes()
                if sha256(b).hexdigest()!=c['sha256']or len(b)!=c['bytes']:raise ValueError('Raw chunk changed')
                blocks.append(b)
            raw=b''.join(blocks)
            if len(raw)!=receipt['bytes']:raise ValueError('Raw concatenation length changed')
        if sha256(raw).hexdigest()!=receipt['sha256']:raise ValueError('Consumed raw bytes changed '+str(stage))
        return raw

    reports={};pairs={}
    for key,group in selection['stages'].items():
        folders=[base/group['directory']/r for r in group['runs']]
        if len(folders)!=2:raise ValueError('Two independent applications required')
        inventories=[sorted(p.relative_to(f)for p in f.rglob('*')if p.is_file())for f in folders]
        if inventories[0]!=inventories[1]or not inventories[0]:raise ValueError('Unequal pair inventories')
        files=[]
        for rel in inventories[0]:
            raws=[(f/rel).read_bytes()for f in folders]
            # Recipes contain the distinct run paths. Their concatenated
            # original raw arrays, not these path strings, must agree.
            if rel.name=='raw_byte_concatenation.json':
                recipes=[json.loads(raw)for raw in raws]
                if recipes[0].keys()!=recipes[1].keys():raise ValueError('Raw reconstruction names changed')
                for name in recipes[0]:
                    a,b=[reconstructed(r[name],key+'/'+name)for r in recipes]
                    if a!=b:raise ValueError('Original paired large bytes differ')
                files.append(dict(path=rel.as_posix(),paired_reconstruction=True));continue
            if raws[0]!=raws[1]:raise ValueError('Paired bytes differ '+key+'/'+str(rel))
            files.append(dict(path=rel.as_posix(),sha256=sha256(raws[0]).hexdigest(),bytes=len(raws[0])))
        meta=json.loads((folders[0]/'result.json').read_bytes());reports[key]=meta
        for folder in folders:
            r=json.loads((folder/'result.json').read_bytes())
            executed=sha256((folder/'executed_producer.py').read_bytes()).hexdigest()
            if r.get('source_sha256',r.get('producer_sha256',executed))!=executed:raise ValueError('Execution source differs')
            source='audits/'+group['directory']+'.py'
            if source not in aliases or aliases[source]['sha256']!=executed:raise ValueError('Canonical execution source not bound')
            for field in('input_and_source_hashes','input_hashes','input_and_source_sha256','source_and_owner_sha256','input_sha256'):
                for name,h in r.get(field,{}).items():
                    if isinstance(h,str)and len(h)==64 and(name not in aliases or aliases[name]['sha256']!=h):
                        raise ValueError('Reported input not bound '+name)
            for field in('original_coupled_corrections','original_coupled_corrections_applied'):
                if field in r and r[field]!=0:raise ValueError('Original coupled correction was not authorized by the full gate')
            receipts=r.get('archives',{})
            if 'archive'in r:receipts={**receipts,r['archive']['name']:r['archive']}
            recipes=json.loads((folder/'raw_byte_concatenation.json').read_bytes())if(folder/'raw_byte_concatenation.json').exists()else{}
            for name,rec in receipts.items():
                if name in recipes:raw=reconstructed(recipes[name],key+'/'+name)
                else:raw=(folder/name).read_bytes()
                if sha256(raw).hexdigest()!=rec['sha256']or len(raw)!=rec['bytes']:raise ValueError('Reported archive differs')
        pairs[key]=dict(independent_runs=group['runs'],byte_identical_original_outputs=True,files=files)

    c=reports['coefficient_export'];j=reports['literal_Jacobi']
    assert c['J_tests']==0 and c['coefficient_only_early_return_before_action_density']
    assert c['no_action_gradient_Hessian_or_field_or_response_solve'] and c['actual_Rdot_and_sourceDot_supplied_not_zeroed']
    assert c['original_regular_action_mode_equations_unchanged'] and c['rights']==7
    assert j['independent_all59x7_Jacobi_control_pass'] and j['no_J_axis_AD_used']
    assert max(j['individual_literal_vs_packed_derivative_defect_upper'].values())<2e-10
    assert j['actual_position_Kz_upper']>2e-10 and j['actual_combined_four_position_rows_upper']>2e-10
    assert not j['physical_full_outgoing_derivative_pass'] and not j['physical_radial_solution_convergence']
    for d in(4,6):
        r=reports['SU2_primal_D'+str(d)]
        assert r['degree']==d and r['SU2_parameters']==3*(d+5)
        assert max(r[k]for k in('primary_Noether_upper','differentiated_primary_Noether_upper','full_covariant_source_conservation_upper'))<2e-10
        assert r['temporal_weak_tests_are_unprojected_augmented_functional_tests_not_state_coordinates']
        assert r['actual_augmented_temporal_Gauss_functional_clock_upper']>0
        assert not r['actual_full_primal_Gauss_constraints_satisfied']
    r=reports['SU2_linear']
    assert r['all_independent_native_Gauss_H_R_rows_consumed'] and r['actual_deltaK_A_contact_upper']>0
    assert r['independent_all27x7_linearized_primary_upper']<2e-10
    assert r['actual_combined_four_SU2_constraint_projection_upper']>2e-10
    assert not r['clock_control_independent_mixed_Gauss_Hessian_evaluated']
    g=reports['gauge'];h=reports['higgs_seam'];v=reports['covector'];n=reports['conormal'];m=reports['matched_native_gauge']
    assert g['common_dimension']==1200 and g['complete_product_output_harmonics']==55
    assert g['numerically_applied_saved_trial_columns']==3 and not g['physical_native_application_complete']
    assert h['exact_normal_factor_cancellation_in_intrinsic18_source_equation']
    assert h['complete_known_operator_coefficients_evaluated_not_only_probe_columns']
    assert h['ambient_normal_mode_values_and_source_jets']is None and not h['native_positive_Higgs_seam_identification']
    assert h['original_Dirac_bar_Gamma0_count']==1 and h['independent_H80_and_dependent_minus_eta_H_retained']
    assert v['input_output_fermion_geometric_pairing_bound'] and not v['sin_f_absorbed_in_Riesz_or_eta_deleted']
    assert not v['full_AE4_native_grading_or_global_domain_identified'] and not v['physical_E_dictionary']
    assert n['material_wall_coordinate_fixed'] and not n['Lorentz_surface_clock_reused'] and not n['extra_wall_speed_added']
    assert not n['full_native_wall_conormal_or_domain_evaluated']
    assert m['declared_trial_columns']==3 and not m['full_native_K_M_or_spectral_trace']
    form_controls=[z for r in m['records']for p in r['placements'].values()for z in p['controls'].values()]
    assert max(z['max_entry_scaled']for z in form_controls)<2e-10
    # Raw coordinate-time coefficients are not an absolute admission.
    assert max(z['absolute']for z in form_controls)>2e-10
    assert not m['physical_outgoing_derivative_pass'] and not m['physical_native_energy_dictionary']
    b=reports['same_function_birth']
    assert b['same_raw_reference_time_point_wall_density_functions'] and b['new_zero_field_coefficients_are_representation_only']
    assert max(b['direction_identity_checks'].values())<2e-10
    assert b['original_proper_port_identity_upper']<2e-10 and b['original_named_frame_identity_upper']<2e-10
    assert b['new59_momentum_on_same_original3_ports_upper']>0 and not b['new_canonical_momenta_prescribed_zero']
    assert b['full60_Gauss_on_same_original3_ports_upper']>2e-10
    assert not b['numerical_proper3_port_section_is_full226_event_selector']
    assert not b['new_full_retarded_response_or_physical_outgoing_domain_solved']

    wanted={}
    for name,rec in aliases.items():
        reconstructed(rec,name)
        entries=[dict(path=rec['path'],sha256=rec['sha256'])]if'path'in rec else rec['raw_byte_concatenation']
        for item in entries:
            rel,h=item['path'],item['sha256']
            if rel in wanted and wanted[rel]!=h:raise ValueError('Conflicting alias '+name)
            wanted[rel]=h
    for rel in('tests/test_muon_full_d5_common_gauge_insertion.py',
            'tests/test_muon_real_positive_d5_covector_binding.py',
            'tests/test_muon_common_higgs_seam_insertion.py'):
        wanted[rel]=sha256((root/rel).read_bytes()).hexdigest()
    index=staged_blobs(root,sorted(wanted));sources={};numeric={}
    for rel,h in sorted(wanted.items()):
        raw,blob=(root/rel).read_bytes(),index[rel]
        if sha256(raw).hexdigest()!=h:raise ValueError('Consumed input changed')
        if raw==blob:recipe='identity'
        elif rel.endswith('.py')and b'\r\n'not in blob and raw==blob.replace(b'\n',b'\r\n'):
            recipe='replace_every_index_LF_with_CRLF'
        else:raise ValueError('No exact index-to-consumed recipe '+rel)
        target=sources if rel.endswith('.py')else numeric
        if target is numeric and recipe!='identity':raise ValueError('Numeric normalization forbidden')
        target[rel]=dict(consumed_raw_sha256=h,index_sha256=sha256(blob).hexdigest(),index_to_consumed_recipe=recipe)
    packet={p.relative_to(root).as_posix():p.read_bytes()for p in sorted(base.rglob('*'))if p.is_file()and p.name not in('manifest_run_1.json','manifest_run_2.json')}
    index=staged_blobs(root,sorted(packet))
    for rel,raw in packet.items():
        if raw!=index[rel]:raise ValueError('Packet/index bytes differ '+rel)
        if len(raw)>10*1024*1024:raise ValueError('Unsplit large artifact '+rel)
    tests={}
    for p in sorted((base/'tests').rglob('*.xml')):
        e=ElementTree.fromstring(p.read_bytes());cases=list(e.iter('testcase'))
        assert cases and not list(e.iter('failure'))and not list(e.iter('error'))and not list(e.iter('skipped'))
        tests[p.relative_to(base).as_posix()]=dict(passed=len(cases),sha256=sha256(p.read_bytes()).hexdigest())
    assert sum(v['passed']for v in tests.values())==11
    checks={}
    for name in('status','forbidden_claims','frozen_integrity','precision','public_readiness'):
        p=base/'publication_audits'/f'{name}.log';text=p.read_text(encoding='utf8')
        if name=='precision':assert'PASS'in text and'FAIL'not in text
        else:assert json.loads(text)['passed']
        checks[name]=sha256(p.read_bytes()).hexdigest()
    previous=root/'artifacts/muon_actual_source_corner_radial_jets_20261016/manifest_run_1.json'
    assert sha256(previous.read_bytes()).hexdigest()=='70ec28a5ca87fda2fa72ad34d07379d1fd7c4cdc2f33146230891b0e82f2ddfa'
    me=Path(__file__).resolve();rel=me.relative_to(root).as_posix();raw=me.read_bytes()
    if staged_blobs(root,[rel])[rel]!=raw:raise ValueError('Binder index differs')
    report=dict(classification='INDEX_BOUND_ACTUAL_NATIVE_COEFFICIENTS_FULL59x7_CONTROL_SU2_AND_BIRTH_SOURCE_BLOCK',
        independent_pairs=pairs,consumed_sources=sources,numerical_input_pins=numeric,focused_tests=tests,
        packet_artifact_pins={k:sha256(v).hexdigest()for k,v in packet.items()},publication_audits=checks,
        binder_sha256=sha256(raw).hexdigest(),previous_checkpoint_manifest_sha256=sha256(previous.read_bytes()).hexdigest(),
        preserved_birth_section='caef5647 compatible n158; not silently identified with actual-target83c90d4a source or ea02 chronological Cauchy data',
        independent_finite59x7_radial_derivative_pass=True,nonzero_SU2_generator_variation_retained=True,
        same_function_full_D4_birth_momenta_evaluated=True,known_common_Higgs_seam_coefficients_evaluated=True,
        matched_real_covector_common_gauge_three_trial_form_evaluated=True,
        all_common_form_comparisons_absolute_2e10_pass=False,
        physical_radial_solution_convergence=False,physical_full_outgoing_energy_field_source_domain_derivative_pass=False,
        original_coupled_corrections=0,original_Maxwell_and_all226_after_pass=False,
        physical_normalized_two_spin_muon=None,physical_muon_magnetic_moment=None,
        scientific_scope='Evaluated finite action-owned coefficient/source blocks and independent radial derivative; physical exterior and solved radial response remain required')
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(out.read_bytes()).hexdigest(),sources=len(sources),numeric_inputs=len(numeric),packet_files=len(packet))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

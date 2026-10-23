"""Exact index binding of nonzero source-corner and same-field radial jets."""
from pathlib import Path
from hashlib import sha256
import argparse,json
from bind_muon_real_coupled_open_operator_20261016 import staged_blobs


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve each independent binding')
    base=root/'artifacts/muon_actual_source_corner_radial_jets_20261016'
    selection=json.loads((base/'packet_selection.json').read_bytes())
    aliases=json.loads((base/'consumed_input_aliases.json').read_bytes())
    pairs={};reports={}
    for key,group in selection['stages'].items():
        folders=[base/group['directory']/r for r in group['runs']]
        if len(folders)!=2:raise ValueError('Two independent executions required')
        inventories=[sorted(p.relative_to(f)for p in f.rglob('*')if p.is_file())for f in folders]
        assert inventories[0]==inventories[1] and inventories[0]
        files=[]
        for rel in inventories[0]:
            a,b=[(f/rel).read_bytes()for f in folders]
            if a!=b:raise ValueError('Paired bytes differ '+key+'/'+str(rel))
            files.append(dict(path=rel.as_posix(),sha256=sha256(a).hexdigest(),bytes=len(a)))
        reports[key]=json.loads((folders[0]/'result.json').read_bytes())
        for folder in folders:
            report=json.loads((folder/'result.json').read_bytes())
            executed='executed_guard.py' if key=='bhsm_ea02_seven_clock_additional_incidence_guard_20261016' else 'executed_producer.py'
            if report.get('source_sha256')!=sha256((folder/executed).read_bytes()).hexdigest():
                raise ValueError('Reported execution source differs '+str(folder))
            for field in ('input_and_source_hashes','input_hashes'):
                for name,h in report.get(field,{}).items():
                    if name not in aliases or aliases[name]['sha256']!=h:
                        raise ValueError('Reported consumption not covered by exact alias '+name)
        pairs[key]=dict(independent_runs=group['runs'],byte_identical=True,files=files)
    clock=reports['bhsm_original_ea02_same_field_seven_clock_20261016']
    assert clock['admitted_original210_and_frame7_clock']
    assert clock['records'][0]['original210_linearized_clock_upper']>2e-10
    assert max(clock['records'][-1]['original210_linearized_clock_upper'],clock['records'][-1]['frame7_upper'])<=2e-10
    assert clock['parent_affine_sourceDot_derived_from_exact_map'] and clock['child_qDot_is_retained_velocity']
    assert not clock['phaseDot_zero_assigned'] and clock['stored_Hessian_used_as_preconditioner_only']
    assert not clock['physical_outgoing_or_radial_mean_or_full_derivative'] and clock['original_coupled_corrections_applied']==0
    guard=reports['bhsm_ea02_seven_clock_additional_incidence_guard_20261016']
    assert guard['all_reviewed_source_sha_guards_pass'] and guard['frame_first_zero_owned']
    assert guard['fixed_named_frame_exact_selector_columns']==list(range(185,210,4))
    assert guard['retained_seven_response_seed_difference_upper']==0 and guard['preprojection_seven_field_difference_upper']<1e-100
    assert max(guard['Jacobi_carried_field_and_clock_difference_upper'].values())==0
    assert not guard['full_physical_gate_pass'] and guard['original_coupled_corrections_applied']==0
    position=reports['bhsm_original_ea02_same_field_position_jacobi_20261016']
    assert position['rights']==7 and position['new_positions']==59
    assert position['actual_response_clock_original210_and_frame7_passed'] and position['sourceDot_and_zDot_not_zero_assigned']
    assert position['same_primal_Euler_reproduction_upper']<2e-10
    assert position['actual_new_position_Kz_upper']>2e-10 and position['combined_four_residual_upper']>2e-10
    assert position['primal_r_added_once_only_to_column0'] and position['old_field_and_response_extended_without_retraction']
    assert not position['higher_radial_mean_or_response_solved'] and not position['physical_radial_convergence']
    assert not position['full_physical_outgoing_or_derivative_or_moment'] and position['original_coupled_corrections_applied']==0
    gauss=reports['bhsm_original_ea02_same_field_gauss_jacobi_20261016']
    assert gauss['Gauss_rows']==60 and gauss['actual_native_Gauss_Kz_upper']>2e-10
    assert not gauss['Gauss_retraction_or_correction_applied'] and not gauss['higher_radial_field_or_response_solved']
    for d in (4,6):
        r=reports['central_primal_D'+str(d)]
        assert r['degree']==d and r['central_parameter_count']==d+5
        assert max(r[k]for k in ('primary_Noether_upper','differentiated_primary_Noether_upper','source_conservation_upper'))<=2e-10
        assert r['actual_primal_initial_corner_charge_upper']>2e-10
        assert r['scalar_wall_H_and_Hdot_contact_retained_once'] and r['old_position_Euler_rows_retained_not_zeroed']
        assert r['linearized_native_source_corner_for_seven'] is None and not r['Gauss_retraction_applied']
        assert not r['physical_full_derivative_pass'] and r['original_coupled_corrections']==0
    corner=reports['bhsm_original_ea02_central_linearized_corner_20261016']
    assert corner['independent_all60_Gauss_Hessian_rows_consumed'] and corner['every_old_and_new_velocity_Hessian_row_retained']
    assert corner['independent_linearized_primary_Noether_upper']<=2e-10
    assert corner['independent_affine_primary_Noether_upper']<=2e-10
    assert corner['actual_combined_four_affine_Gauss_charge_upper']>2e-10
    assert corner['deltaV_Higgs_contact_retained_once'] and corner['central_Gauss_map_field_independent']
    assert corner['primal_added_once_to_affine_column0'] and corner['original_seven_to_four_retarded_plus_homogeneous_combination_retained']
    assert not corner['physical_full_derivative_pass'] and not corner['physical_radial_convergence'] and corner['original_coupled_corrections']==0
    assert not corner['full_SU2_source_corner_evaluated'] and not corner['full_retarded_domain_and_exterior_evaluated']
    assert corner['physical_C0_Cj'] is None and corner['physical_outgoing_Y_R'] is None and corner['physical_affine_s_R'] is None

    wanted={}
    for alias,r in aliases.items():
        if r['path']in wanted and wanted[r['path']]!=r['sha256']:raise ValueError('Conflicting input alias '+alias)
        wanted[r['path']]=r['sha256']
    index=staged_blobs(root,sorted(wanted));sources={};numerical={}
    for rel,h in sorted(wanted.items()):
        raw,blob=(root/rel).read_bytes(),index[rel]
        if sha256(raw).hexdigest()!=h:raise ValueError('Consumed bytes changed '+rel)
        if raw==blob:recipe='identity'
        elif rel.endswith('.py')and b'\r\n'not in blob and raw==blob.replace(b'\n',b'\r\n'):
            recipe='replace_every_index_LF_with_CRLF'
        else:raise ValueError('Exact index-to-consumed recipe missing '+rel)
        target=sources if rel.endswith('.py')else numerical
        if target is numerical and recipe!='identity':raise ValueError('Numerical normalization forbidden')
        target[rel]=dict(consumed_raw_sha256=h,index_sha256=sha256(blob).hexdigest(),index_to_consumed_recipe=recipe)
    files={p.relative_to(root).as_posix():p.read_bytes()for p in sorted(base.rglob('*'))if p.is_file()and p.name not in('manifest_run_1.json','manifest_run_2.json')}
    index=staged_blobs(root,sorted(files))
    for rel,raw in files.items():
        if raw!=index[rel]:raise ValueError('Artifact index bytes differ '+rel)
        if len(raw)>10*1024*1024:raise ValueError('Oversized unsplit artifact '+rel)
    me=Path(__file__).resolve();rel=me.relative_to(root).as_posix();raw=me.read_bytes()
    if staged_blobs(root,[rel])[rel]!=raw:raise ValueError('Binder index differs')
    checks={}
    for name in('status','forbidden_claims','frozen_integrity','precision','public_readiness'):
        p=base/'publication_audits'/f'{name}.log';v=p.read_text(encoding='utf8')
        if name=='precision':assert 'PASS'in v and 'FAIL'not in v
        else:assert json.loads(v)['passed']
        checks[name]=sha256(p.read_bytes()).hexdigest()
    previous=root/'artifacts/muon_actual_radial_cauchy_common_forms_20261016/manifest_run_1.json'
    if sha256(previous.read_bytes()).hexdigest()!='6e6b29c3ae8791506105bd39b3899e6083e0ae32b2658816bb863956a4bcea60':raise ValueError('Previous exact paired checkpoint changed')
    result=dict(classification='INDEX_BOUND_ACTUAL_EA02_SOURCE_CORNER_AND_RADIAL_JACOBI_OPERANDS',
        independent_pairs=pairs,consumed_sources=sources,numerical_input_pins=numerical,
        packet_artifact_pins={k:sha256(v).hexdigest()for k,v in files.items()},publication_audits=checks,
        binder_sha256=sha256(raw).hexdigest(),previous_checkpoint_manifest_sha256=sha256(previous.read_bytes()).hexdigest(),
        finite_same_cut_seven_clock_pass=True,actual_added_radial_position_and_Gauss_and_corner_evaluated=True,
        independent_central_Noether_linearization_pass=True,actual_retained_affine_constraint_satisfied=False,
        full59x7_independent_mixed_derivative_pass=False,physical_radial_solution_convergence=False,
        physical_full_outgoing_energy_field_source_domain_derivative_pass=False,original_coupled_corrections=0,
        original_Maxwell_and_all226_after_pass=False,physical_normalized_two_spin_muon=None,physical_muon_magnetic_moment=None,
        scientific_scope='Actual nonzero classical same-field source/Jacobi operands; higher-radial and physical outgoing solution still required')
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(out.read_bytes()).hexdigest(),consumed_sources=len(sources),numeric_inputs=len(numerical),packet_files=len(files))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

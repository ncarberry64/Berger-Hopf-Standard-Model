"""Exact index binding of complete Cauchy/constraint clocks and weak seam."""
from pathlib import Path
from hashlib import sha256
import argparse,json
from bind_muon_real_coupled_open_operator_20261016 import staged_blobs


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent index binding')
    base=root/'artifacts/muon_actual_radial_phase_source_domain_20261016'
    selection=json.loads((base/'packet_selection.json').read_bytes())
    aliases=json.loads((base/'consumed_input_aliases.json').read_bytes())
    pairs={};reports={}
    def raw_alias(rec):
        if 'path'in rec:raw=(root/rec['path']).read_bytes()
        else:
            parts=[]
            for p in rec['raw_byte_concatenation']:
                a=(root/p['path']).read_bytes()
                if len(a)!=p['bytes']or sha256(a).hexdigest()!=p['sha256']:raise ValueError('Raw chunk changed')
                parts.append(a)
            raw=b''.join(parts)
            if len(raw)!=rec['bytes']:raise ValueError('Raw length changed')
        if sha256(raw).hexdigest()!=rec['sha256']:raise ValueError('Raw consumed input changed')
        return raw
    for key,group in selection['stages'].items():
        folders=[base/group['directory']/r for r in group['runs']]
        if len(folders)!=2:raise ValueError('Two executions required')
        inventories=[sorted(p.relative_to(f)for p in f.rglob('*')if p.is_file())for f in folders]
        if inventories[0]!=inventories[1]or not inventories[0]:raise ValueError('Unequal pair inventories')
        files=[]
        for rel in inventories[0]:
            a,b=[(f/rel).read_bytes()for f in folders]
            if a!=b:raise ValueError('Paired bytes differ '+key+'/'+str(rel))
            files.append(dict(path=rel.as_posix(),sha256=sha256(a).hexdigest(),bytes=len(a)))
        for folder in folders:
            r=json.loads((folder/'result.json').read_bytes())
            h=sha256((folder/'executed_producer.py').read_bytes()).hexdigest()
            if h!=r['source_sha256']or aliases['audits/'+group['directory']+'.py']['sha256']!=h:raise ValueError('Execution source not bound')
            for field in('input_and_source_hashes','input_and_source_sha256','input_hashes','source_and_owner_sha256'):
                for name,h in r.get(field,{}).items():
                    if isinstance(h,str)and len(h)==64 and(name not in aliases or aliases[name]['sha256']!=h):raise ValueError('Reported input missing '+name)
            arc=r['archive'];a=(folder/arc['name']).read_bytes()
            if len(a)!=arc['bytes']or sha256(a).hexdigest()!=arc['sha256']:raise ValueError('Reported archive changed')
            if r.get('original_coupled_corrections',r.get('original_coupled_corrections_applied'))!=0:raise ValueError('Premature original correction')
        reports[key]=r;pairs[key]=dict(independent_runs=group['runs'],byte_identical=True,files=files)
    f=reports['original_four_flux']
    assert f['exact_same_seven_column_combination'] and f['initial_face_is_fixed_cut']
    assert not f['parent_gv_added_twice'] and not f['primal_momentum_added_to_affine_column']
    assert f['original_old158_position_identity_upper']<2e-10
    assert not f['all60_Gauss_compatibility_or_new_retarded_solution_admitted']
    assert not f['moving_cut_energy_domain_jet_supplied']
    c=reports['central_mixed_clock']
    assert(c['central_parameters'],c['rights'],c['complete_momentum_rows'])==(9,7,217)
    assert c['independent_central9_first_and_mixed_check_pass']
    assert max(c['independent_central9_first_primary_upper'],c['independent_central9_mixed_primary_upper'])<2e-10
    assert c['all_four_mixed_Q_product_contacts_retained'] and c['actual_deltaVdot_Pi_contact_upper']>0
    assert c['independent_literal_Gauss_clock_compared_only_after_momentum_contraction']
    assert c['all36_independent_corner_clock_checks_completed_with_previous_SU2_27']
    assert c['actual_affine_seven_central_Gauss_clock_upper']>2e-10 and not c['actual_affine_central_Gauss_clock_satisfied']
    q=reports['new59_momentum_rank']
    assert(q['actual_full_rank'],q['actual_old28_rank'],q['actual_new8_rank_while_preserving_old28'])==(28,21,7)
    assert q['free_new_momentum_directions_preserving_all_temporal_rows']==31
    assert q['rank_certified_by_exact_support_and_nonzero_minor_not_SVD'] and q['pivot_determinant_absolute_lower']>0
    assert q['no_pseudoinverse_minimum_norm_or_free_coordinate_values_chosen']
    assert q['range_obstruction_only_under_fixed_old_canonical_momentum_hypothesis']
    assert q['fixed_original_oldPi_primal_range']['interval_certified_out_of_exact_range']
    assert q['fixed_original_oldPi_primal_range']['upper']<2e-10
    assert q['actual_seven_affine_load_range']['interval_certified_out_of_exact_range']
    assert q['actual_seven_affine_load_range']['upper']<2e-10
    assert q['native_primal_charge_vs_action_Gauss_upper']<2e-10 and q['native_point_Dphi_image_upper']<2e-10
    assert q['combined_four_old_momentum_cokernel_image_rank']==4 and q['fixed_oldPi_load_augmented_source_four_rank']==5
    assert q['combined_four_rank_minor_abs_lower']>0 and q['fixed_oldPi_augmented_minor_abs_lower']>0
    assert q['isolated_fixed_q_four_momentum_component_span_cannot_cancel_all_eight_exact_loads']
    assert q['affine_source_column0_is_not_promoted_to_a_free_physical_parameter']
    assert not q['full_BHSM_solution_nonexistence_claim'] and not q['full_outgoing_domain_or_31_free_momenta_selected']
    p=reports['native_phase277']
    assert(p['phase_rows'],p['dynamic_velocity_rows'],p['original_algebraic_rows'])==(277,217,60)
    assert p['cached277_and_F36_are_preconditioner_or_diagnostic_only']
    assert p['packed_and_independent_material_chart_source_pins_enforced']
    assert p['actual_selected_direction_and_original_candidate_rows_checked']
    assert max(z for a in p['fresh_same_primal_point_density_wall_guards'].values()for z in a.values())<2e-10
    assert max(p[k]for k in('fresh_native_actual_direction_symmetry_upper','fresh_native_six_temporal_gauge_upper',
        'cached_original_binary_vs_fresh_native_on_tests_upper','fresh_original_preconditioned_rows_upper'))<2e-10
    assert not p['frame_reaction_counted_as_original_Gauss_pass'] and not p['dense277_rights_campaign_or_Hxx_built']
    assert not p['source_compatible_initial_jump_selected'] and not p['physical_new_retarded_field_or_outgoing_domain_solved']
    normal=json.loads((base/'muon_normal_trace_congruence_and_shape_integral_20261016_source_pins.json').read_bytes())
    assert not normal['new_numerical_model_or_normal_profile_evaluated']
    for name,h in normal['action_source_sha256'].items():
        if name not in aliases or aliases[name]['sha256']!=h:raise ValueError('Normal action anchor not bound')
    for name,h in normal['derivation_and_premise_sha256'].items():
        if sha256((base/name).read_bytes()).hexdigest()!=h:raise ValueError('Normal derivation/premise changed')

    wanted={}
    for rec in aliases.values():
        raw_alias(rec)
        entries=[dict(path=rec['path'],sha256=rec['sha256'])]if'path'in rec else rec['raw_byte_concatenation']
        for v in entries:
            if v['path']in wanted and wanted[v['path']]!=v['sha256']:raise ValueError('Conflicting alias')
            wanted[v['path']]=v['sha256']
    index=staged_blobs(root,sorted(wanted));sources={};numeric={}
    for rel,h in sorted(wanted.items()):
        raw,blob=(root/rel).read_bytes(),index[rel]
        if sha256(raw).hexdigest()!=h:raise ValueError('Consumed bytes changed')
        if raw==blob:recipe='identity'
        elif rel.endswith('.py')and b'\r\n'not in blob and raw==blob.replace(b'\n',b'\r\n'):
            recipe='replace_every_index_LF_with_CRLF'
        else:raise ValueError('Exact consumed-byte recipe missing '+rel)
        target=sources if rel.endswith('.py')else numeric
        if target is numeric and recipe!='identity':raise ValueError('Numeric normalization forbidden')
        target[rel]=dict(consumed_raw_sha256=h,index_sha256=sha256(blob).hexdigest(),index_to_consumed_recipe=recipe)
    files={p.relative_to(root).as_posix():p.read_bytes()for p in sorted(base.rglob('*'))if p.is_file()and p.name not in('manifest_run_1.json','manifest_run_2.json')}
    index=staged_blobs(root,sorted(files))
    for rel,raw in files.items():
        if raw!=index[rel]:raise ValueError('Packet/index bytes differ '+rel)
        if len(raw)>10*1024*1024:raise ValueError('Unsplit oversized artifact')
    checks={}
    for name in('status','forbidden_claims','frozen_integrity','precision','public_readiness'):
        p=base/'publication_audits'/f'{name}.log';v=p.read_text(encoding='utf8')
        if name=='precision':assert'PASS'in v and'FAIL'not in v
        else:assert json.loads(v)['passed']
        checks[name]=sha256(p.read_bytes()).hexdigest()
    previous=root/'artifacts/muon_actual_cauchy_constraint_clock_20261016/manifest_run_1.json'
    assert sha256(previous.read_bytes()).hexdigest()=='fe240ad5ee6b9115a2016d6fa6b45a924bfcedd80aae36d38c25e351721bcd00'
    me=Path(__file__).resolve();rel=me.relative_to(root).as_posix();raw=me.read_bytes()
    if staged_blobs(root,[rel])[rel]!=raw:raise ValueError('Binder index differs')
    result=dict(classification='INDEX_BOUND_ACTUAL_RADIAL_PHASE_SOURCE_DOMAIN_AND_COMPLETE_CORNER_CLOCK',
        independent_pairs=pairs,consumed_sources=sources,numerical_input_pins=numeric,
        packet_artifact_pins={k:sha256(v).hexdigest()for k,v in files.items()},publication_audits=checks,
        binder_sha256=sha256(raw).hexdigest(),previous_checkpoint_manifest_sha256=sha256(previous.read_bytes()).hexdigest(),
        original_four_response_fixed_cut_flux_evaluated=True,independent_all36_temporal_corner_mixed_clock_pass=True,
        actual_new59_temporal_momentum_rank=28,free_new_momentum_directions_under_temporal_constraints_only=31,
        phase277_native_backend_selected_direction_controls_pass=True,full_phase_basis_or_global_kernel_certificate=False,
        action_derived_normal_trace_congruence_available=True,physical_normal_shape_integral_evaluated=False,
        coupled_source_domain_or_physical_outgoing_realization_solved=False,physical_radial_solution_convergence=False,
        physical_full_outgoing_energy_field_source_domain_derivative_pass=False,original_coupled_corrections=0,
        original_Maxwell_and_all226_after_pass=False,physical_normalized_two_spin_muon=None,physical_muon_magnetic_moment=None,
        scientific_scope='Actual larger-radial constitutive operator and unresolved source-domain family; response coefficients remain to be solved with the physical outgoing realization')
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(out.read_bytes()).hexdigest(),sources=len(sources),numeric_inputs=len(numeric),packet_files=len(files))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

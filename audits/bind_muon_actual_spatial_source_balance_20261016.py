"""Exact index binding of complete Cauchy/constraint clocks and weak seam."""
from pathlib import Path
from hashlib import sha256
import argparse,json
from bind_muon_real_coupled_open_operator_20261016 import staged_blobs


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent index binding')
    base=root/'artifacts/muon_actual_spatial_source_balance_20261016'
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
    q=reports['spatial_contact_map']
    assert(q['actual_map_rows'],q['actual_new_spatial_columns'],q['certified_exact_rank'])==(36,59,27)
    assert q['central9_rows_exact_zero'] and q['certified_original_minor_abs_lower']>0
    assert q['new59_physical_Euler_reproduction_upper']<2e-10
    assert q['independent_direction_before_after_contraction_upper']<2e-10
    assert q['actual_new59_wall_value_map_upper']>1
    assert not q['arbitrary_new_q_values_or_cancellation_solution_selected']
    assert not q['full_proper_mechanical_momentum_flux_or_normal_domain_ports_proven_unchanged']
    f=reports['open_spatial_range']
    assert(f['exact_contact_rank'],f['open_response_q_coordinates'])==(27,32)
    assert max(f['right_inverse_range_residual_upper'],f['kernel_residual_upper'])<2e-10
    assert f['small47_column_count']==f['small47_proven_nonzero_column_count']==47
    assert f['full_wall_known_particular_upper']>2e-10
    assert f['all_frozen_wall_coefficients_retained_without_thresholding']
    assert not f['physical_q_or_free32_values_selected'] and not f['minnorm_or_empirical_fitting_used']
    assert not f['wall_normal_flux_or_full_proper_ports_assumed_preserved']
    assert not f['phase_constitutive_or_clock_closure_evaluated_for_this_new_family']
    d=reports['deltaW_Gauss']
    assert d['all36_literal_Gauss_controls_upper']<2e-10 and d['actual_deltaW_G_upper']>0
    assert d['actual_updated_A0_A0radial_wall_potential_preservation_verified']
    assert d['coefficient_action_or_history_sampling_calls']==0
    assert not d['exact_Z_leftnull_or_required_chi_zero_claimed']
    u=reports['updated_momentum_WGauss']
    assert(u['independent_gauge_Higgs_momentum_rows'],u['cached_geometry_momentum_rows'])==(179,38)
    assert max(u['independent179_momentum_control_upper'],u['independent36_updated_Gauss_control_upper'])<2e-10
    assert u['combined_source_domain_pullback_identity_defect_upper']<2e-10
    assert u['cumulative_remainder_after_upper']<2e-10 and u['saved_candidate_original277_rows_upper']>2e-10
    assert u['independent179_not_mislabeled_full217_independent']
    assert u['cached38_cap_momentum_not_reconstructed_from_gauge_p']
    assert u['candidate_projection_is_actual_framed_candidate_not_unframed_clock_pass']
    assert u['fixed_reference_lc_star_at_pi_over4_not_moving_wall']
    assert u['original_primal_Gauss_added_once_only_affine_column0']
    assert u['no_action_AD_coefficient_history_sampling_calls']
    assert not u['exact_Z_leftnull_chi_zero_or_physical_clock_solution_claimed']
    wallproof=json.loads((base/'muon_new59_wall_trace_formula_vs_frozen_map_20261016_source_pins.json').read_bytes())
    note=wallproof['note']
    assert sha256((base/note['name']).read_bytes()).hexdigest()==note['sha256']
    assert wallproof['scope']['all47_frozen_columns_each_have_entry_excluding_zero']
    assert not wallproof['scope']['formula_identities_promoted_to_exact_frozen_W_kernel']
    assert not wallproof['scope']['nonzero_entries_thresholded_or_reencoded']
    assert not wallproof['scope']['proper_flux_domain_preservation_proved']
    for name,v in wallproof['input_and_source_pins'].items():
        if name not in aliases or aliases[name]['sha256']!=v['sha256']:raise ValueError('Wall proof input not bound '+name)
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
    previous=root/'artifacts/muon_actual_clock_euler_decomposition_20261016/manifest_run_1.json'
    assert sha256(previous.read_bytes()).hexdigest()=='d4e12f8c566960a10cafd6178c6af4fe3ad9af07938d4263c57d0b018e058758'
    me=Path(__file__).resolve();rel=me.relative_to(root).as_posix();raw=me.read_bytes()
    if staged_blobs(root,[rel])[rel]!=raw:raise ValueError('Binder index differs')
    result=dict(classification='INDEX_BOUND_ACTUAL_OPEN_SPATIAL_RANGE_AND_SOURCE_CLOCK_DECOMPOSITION',
        independent_pairs=pairs,consumed_sources=sources,numerical_input_pins=numeric,
        packet_artifact_pins={k:sha256(v).hexdigest()for k,v in files.items()},publication_audits=checks,
        binder_sha256=sha256(raw).hexdigest(),previous_checkpoint_manifest_sha256=sha256(previous.read_bytes()).hexdigest(),
        spatial_contact_rank=27,open_spatial_contact_coordinates=32,
        prescribed_contact_load_is_optional_not_a_physical_chi_zero_requirement=True,
        full_frozen_wall_trace_and_conormal_domain_equations_retained=True,
        independent_gauge_Higgs_momentum_rows=179,separately_cached_geometry_momentum_rows=38,
        actual_unprojected_W_affine_Gauss_evaluated=True,
        component_source_Euler_projection_identity_defect_upper=reports['updated_momentum_WGauss']['combined_source_domain_pullback_identity_defect_upper'],
        candidate_original277_residual_upper=reports['updated_momentum_WGauss']['saved_candidate_original277_rows_upper'],
        actual_unframed_clock_or_physical_outgoing_realization_solved=False,
        physical_radial_solution_convergence=False,full_physical_derivative_pass=False,
        original_coupled_corrections=0,original_Maxwell_and_all226_after_pass=False,
        physical_normalized_two_spin_muon=None,physical_muon_magnetic_moment=None,
        retained_original_before_Maxwell_abs=2.4777309846820184,
        retained_original_before_all226_max=9.602842247524184e-7,
        original_before_diagnostics_re_evaluated_in_this_packet=False,
        scientific_scope='Evaluated classical source contacts and open spatial response family; physical outgoing domain and full microscopic operator remain unresolved')
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(out.read_bytes()).hexdigest(),sources=len(sources),numeric_inputs=len(numeric),packet_files=len(files))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

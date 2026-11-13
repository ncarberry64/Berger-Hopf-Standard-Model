"""Exact index binding of complete Cauchy/constraint clocks and weak seam."""
from pathlib import Path
from hashlib import sha256
import argparse,json
from bind_muon_real_coupled_open_operator_20261016 import staged_blobs


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent index binding')
    base=root/'artifacts/muon_actual_cauchy_constraint_clock_20261016'
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
    t=reports['literal_temporal_clock']
    assert(t['temporal_Gauss_rows'],t['rights'])==(36,7)
    assert t['no_Noether_identity_or_charge_used_to_construct_derivative'] and t['no_packed_action_or_derivative_AD_called']
    assert t['mixed_FD4_is_polynomial_in_step_fourth_power_degree2'] and t['exact_coefficient_degree_bound']==5
    assert t['all_fixed_scales_retained'] and t['independent_SU2_Gauss_clock_plus_direct_charge_clock_upper']<2e-10
    assert not t['other24_mechanical_constraints_evaluated'] and not t['full_physical_outgoing_derivative_pass']
    c=reports['complete217_Cauchy']
    assert c['exact_original_ea02_primal_source_response_clock_preserved'] and not c['birth0_section_spliced']
    assert not c['sourceDot_or_Rdot_zero_assigned'] and c['source_complete_momentum_and_Gauss_loads_kept']
    assert max(c['coefficient_clock_germ_checks'].values())<2e-10
    assert c['primal_old158_momentum_epoch_check_upper']<2e-10 and c['exact_new59_canonical_Jacobi_identity_upper']<2e-10
    assert c['new59_primal_momentum_upper']>0 and c['new59_seven_momentum_upper']>0
    assert not c['physical_new_radial_response_or_mean_solved']
    g=reports['complete60_constraint_clock']
    assert g['all60_actual_mixed_source_clock_operands_evaluated']
    assert g['temporal36_independently_differentiated_polynomial']
    assert g['mechanical24_extracted_from_cached_direct_action_mixed_and_Rdot_operands']
    assert not g['mechanical24_only_equation_controls_used'] and not g['all60_independent_literal_derivative_check']
    assert max(g['exact_operand_guards_and_crosschecks_upper'].values())<2e-10
    assert g['actual_mechanical24_affine_clock_rows_upper']<2e-10
    assert g['actual_new8_temporal_affine_clock_rows_upper']>2e-10
    assert g['old52_and_new8_clock_rows_kept_separate'] and g['primal_Gt_added_once_only_affine_column0']
    assert not g['actual_complete60_affine_clock_satisfied'] and not g['original_prefix_cell7_protocol_retroactively_admitted']
    h=reports['weak_Hamiltonian_Higgs_seam']
    assert h['intrinsic_surface_native_scalar_W_vertex_exactly_identified']
    assert h['full384_extension_from_original_seam_not_reduced_point_completion']
    assert h['scalar_term_on_original_intrinsic_surface_stratum_only'] and not h['new_D5_bulk_Higgs_mass_added']
    assert h['complete_known_all1200_operator_coefficients_and_time_evaluated'] and not h['complex_common_source_coefficients_conjugated']
    assert all(r['native_intrinsic_scalar_vertex_identity']['absolute']==0 for r in h['records'])
    assert max(z['max_entry_scaled']for r in h['records']for z in r['controls'].values())<2e-10
    assert h['ambient_normal_values_and_source_jets']is None and not h['full_ambient_normalized_seam_evaluated']
    assert not h['native_full_Dstrat_operator_or_global_coercive_transmission_domain_proved'] and not h['delta_squared_or_H1_domain_used']
    assert not h['physical_outgoing_energy_field_source_domain_derivative_pass']

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
    previous=root/'artifacts/muon_actual_native_coefficients_source_completion_20261016/manifest_run_1.json'
    assert sha256(previous.read_bytes()).hexdigest()=='a48f63a1b9e2445642389b81e5047acdec2133e3d8123484d097dd87c9e403fd'
    me=Path(__file__).resolve();rel=me.relative_to(root).as_posix();raw=me.read_bytes()
    if staged_blobs(root,[rel])[rel]!=raw:raise ValueError('Binder index differs')
    result=dict(classification='INDEX_BOUND_COMPLETE_EA02_D4_CAUCHY_AND_ALL60_SOURCE_CLOCK_WITH_WEAK_NATIVE_SEAM',
        independent_pairs=pairs,consumed_sources=sources,numerical_input_pins=numeric,
        packet_artifact_pins={k:sha256(v).hexdigest()for k,v in files.items()},publication_audits=checks,
        binder_sha256=sha256(raw).hexdigest(),previous_checkpoint_manifest_sha256=sha256(previous.read_bytes()).hexdigest(),
        all217_actual_source_complete_Cauchy_momentum_and_clock_evaluated=True,all60_actual_constraint_clock_operands_evaluated=True,
        independent_literal_temporal36_derivative_pass=True,all60_independent_literal_derivative_pass=False,
        carried_added_radial_constraint_clock_satisfied=False,weak_Hamiltonian_Higgs_surface_coefficients_matched=True,
        physical_radial_solution_convergence=False,physical_full_outgoing_energy_field_source_domain_derivative_pass=False,
        original_coupled_corrections=0,original_Maxwell_and_all226_after_pass=False,
        physical_normalized_two_spin_muon=None,physical_muon_magnetic_moment=None,
        scientific_scope='Complete actual finite Cauchy/source-clock data and known weak surface coefficients; coupled larger-radial/outgoing solution remains open')
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(out.read_bytes()).hexdigest(),sources=len(sources),numeric_inputs=len(numeric),packet_files=len(files))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

"""Exact index binding of complete Cauchy/constraint clocks and weak seam."""
from pathlib import Path
from hashlib import sha256
import argparse,json
from bind_muon_real_coupled_open_operator_20261016 import staged_blobs


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent index binding')
    base=root/'artifacts/muon_actual_open_canonical_clock_20261016'
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
    f=reports['open_family']
    assert(f['certified_new_momentum_rank'],f['open_new_momentum_coordinates'],f['retained_source_domain_cokernel_rows'])==(28,31,8)
    assert f['known_particular_coefficients_original_rows_within_tolerance']
    assert f['all31_free_momentum_coordinates_remain_open'] and f['all8_exact_source_domain_compatibility_rows_retained']
    assert f['computational_kernel_origin_is_not_a_physical_zero_free_choice']
    assert not f['nonzero_cokernel_or_frame_reaction_discarded']
    assert f['old158_fixed_as_diagnostic_not_physical_domain'] and f['bare_primal_momentum_kept_separate']
    assert f['primal_r_added_once_only_to_affine_column0']
    assert max(f[k]for k in('fresh_original277_upper','actual_full60_affine_Gauss_after_upper',
        'old158_native_response_momentum_change_upper','actual_new59_momentum_rows_upper'))<2e-10
    assert f['retained_cokernel_Gauss_after_upper']>0 and f['frame_reaction_upper']>0
    assert not f['new_retarded_evolution_or_outgoing_domain_solved'] and not f['full_physical_derivative_passed']
    p=reports['position_force']
    assert(p['position_rows'],p['actual_right_columns'])==(217,7)
    assert max(p['independent_same_cut_reference_and_cross_controls'].values())<2e-10
    assert p['actual_full217_primal_Euler_residual_upper']>1
    assert p['primal_Euler_is_retained_not_assumed_stationary']
    assert p['classical_inherited_action_parent_source_contacts_retained_once']
    assert p['full217_force_backend_on_general_full746_rights_available']
    assert not p['fourth_clock_derivative_or_dense_Hxx_built']
    assert not p['native_unsquared_or_heat_exterior_operator_identification']
    c=reports['continuous_clock']
    assert c['all36_clock_compatibility_upper']>2e-10
    assert c['eight_source_domain_clock_cokernel_upper']<2e-10
    assert c['primal217_Pi_dot_reproduction_upper']<2e-10
    assert max(c['same_base_and_material_directional_first_germ_guards'].values())<2e-10
    assert c['corrected_native_point_and_wall_clock_incidence_used']
    assert c['known_qDot_uses_UPDATED_particular_velocity'] and c['parent_response_sourceDot_kept_actual']
    assert c['reference_clock_included_once'] and not c['primal_stationarity_assumed']
    assert not c['unknown277_phase_clock_assigned'] and not c['open31_free_coordinate_or_clock_values_selected']
    assert not c['eight_compatibility_rows_or_offshell_Noether_contacts_dropped']
    assert not c['complete_continuous_clock_or_chronological_retarded_solution_claimed']
    assert not c['classical_Hessian_identified_with_native_Dstrat_or_heat']
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
    previous=root/'artifacts/muon_actual_radial_phase_source_domain_20261016/manifest_run_1.json'
    assert sha256(previous.read_bytes()).hexdigest()=='167fb31ce31d008820817fef5dc8b8ae1695b7f7d2ad145db477db8780577218'
    me=Path(__file__).resolve();rel=me.relative_to(root).as_posix();raw=me.read_bytes()
    if staged_blobs(root,[rel])[rel]!=raw:raise ValueError('Binder index differs')
    result=dict(classification='INDEX_BOUND_ACTUAL_OPEN_CANONICAL_FAMILY_FORCE_AND_CLOCK_RELATION',
        independent_pairs=pairs,consumed_sources=sources,numerical_input_pins=numeric,
        packet_artifact_pins={k:sha256(v).hexdigest()for k,v in files.items()},publication_audits=checks,
        binder_sha256=sha256(raw).hexdigest(),previous_checkpoint_manifest_sha256=sha256(previous.read_bytes()).hexdigest(),
        open_initial_particular_original277_and_full60_coefficient_checks_pass=True,
        free31_coordinates_and_eight_exact_compatibility_equations_retained=True,
        full217_force_independent_literal_and_cross_controls_pass=True,
        actual_full277_canonical_clock_rhs_evaluated=True,
        clock_rhs_gauge_projection_upper=c['all36_clock_compatibility_upper'],
        clock_projection_is_not_a_proven_exact_left_null_solvability_obstruction=True,
        full_clock_solution_or_source_domain_cancellation_evaluated=False,
        physical_outgoing_realization_or_radial_solution_convergence=False,
        full_physical_outgoing_energy_field_source_domain_derivative_pass=False,
        original_coupled_corrections=0,original_Maxwell_and_all226_after_pass=False,
        physical_normalized_two_spin_muon=None,physical_muon_magnetic_moment=None,
        scientific_scope='Actual classical action coefficients and open canonical-clock relation; no physical outgoing solution or moment claimed')
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(out.read_bytes()).hexdigest(),sources=len(sources),numeric_inputs=len(numeric),packet_files=len(files))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

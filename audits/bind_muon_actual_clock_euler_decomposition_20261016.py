"""Exact index binding of complete Cauchy/constraint clocks and weak seam."""
from pathlib import Path
from hashlib import sha256
import argparse,json
from bind_muon_real_coupled_open_operator_20261016 import staged_blobs


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent index binding')
    base=root/'artifacts/muon_actual_clock_euler_decomposition_20261016'
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
    c=reports['clock_candidate']
    assert c['computational_framed_problem_within_tolerance']
    assert not c['original277_plus_computational_frame_within_tolerance']
    assert c['original277_clock_rows_upper']>2e-10 and c['reaction_upper']>2e-10
    assert c['plus_frame_reaction_rows_upper']<2e-10
    assert c['original277_radius_envelope']<1e-20
    assert c['actual_projected_LHS_minus_RHS_upper']>2e-10
    assert c['projected_residual_product_identity_upper']<2e-10
    assert c['only_numerical_unknown_candidate_and_reaction_centered']
    assert c['full_physical_operator_and_rhs_balls_retained']
    assert not c['projected_RHS_assumed_zero_or_left_null_certificate_claimed']
    assert not c['reactions_counted_as_unframed_original_equation_pass']
    assert not c['physical_continuous_clock_or_retarded_solution_claimed']
    assert not c['failed_computational_candidate_is_a_physical_nonexistence_claim']
    p=reports['physical_Euler_contact']
    assert p['literal_physical_Euler_represented_controls_count']==179
    assert p['literal_physical_Euler_vs_sameaction_canonical_Euler_upper']<2e-10
    assert p['actual_unprojected_deltaV_Euler_upper']>2e-10
    assert 0<p['chi_plus_actual_deltaV_Euler_remainder_upper']<2e-10
    assert p['coefficient_action_or_field_sampling_calls']==0
    assert p['base_Euler_not_assumed_zero'] and p['actual_physical_generator_not_derivative_of_cached_Z']
    assert p['deltaV_test_not_projected_into_state_carrier']
    assert not p['remaining_source_domain_operator_projection_terms_evaluated_separately']
    assert p['chi_is_not_proven_solvability_obstruction']
    assert not p['unknown_phase_clock_or_free31_or_source_correction_selected']
    assert not p['physical_outgoing_or_full_derivative_Maxwell226_spin_moment_claimed']
    exterior=json.loads((base/'muon_unsquared_exterior_operator_construction_20261016_source_pins.json').read_bytes())
    note=exterior['note']
    assert sha256((base/note['name']).read_bytes()).hexdigest()==note['sha256']
    assert exterior['scope']['local_full_carrier_Lorentz_differential_expression_owned']
    assert exterior['scope']['existing_retarded_consumers_reused']
    assert not exterior['scope']['full_common_graded_operator_domain_identified']
    assert not exterior['scope']['real_exterior_total_fields_and_E_B_jets_evaluated']
    assert not exterior['scope']['proof_of_physical_theory_nonuniqueness']
    for name,v in exterior['owner_and_readout_pins'].items():
        if name not in aliases or aliases[name]['sha256']!=v['sha256']:raise ValueError('Exterior source not bound '+name)
    for name,v in exterior['prior_raw_normal_proofs'].items():
        if 'WORK/'+name not in aliases or aliases['WORK/'+name]['sha256']!=v['sha256']:raise ValueError('Prior normal proof not bound '+name)
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
    previous=root/'artifacts/muon_actual_open_canonical_clock_20261016/manifest_run_1.json'
    assert sha256(previous.read_bytes()).hexdigest()=='ec513fae1683bbcbc4945ebd53aa0d9a620e769381d00290ea646ea2f78eb1d7'
    me=Path(__file__).resolve();rel=me.relative_to(root).as_posix();raw=me.read_bytes()
    if staged_blobs(root,[rel])[rel]!=raw:raise ValueError('Binder index differs')
    result=dict(classification='INDEX_BOUND_ACTUAL_CLOCK_CANDIDATE_AND_PHYSICAL_EULER_CONTACT',
        independent_pairs=pairs,consumed_sources=sources,numerical_input_pins=numeric,
        packet_artifact_pins={k:sha256(v).hexdigest()for k,v in files.items()},publication_audits=checks,
        binder_sha256=sha256(raw).hexdigest(),previous_checkpoint_manifest_sha256=sha256(previous.read_bytes()).hexdigest(),
        framed_candidate_original277_residual_upper=c['original277_clock_rows_upper'],
        computational_reaction_not_an_original_equation_pass=True,
        physical_unprojected_deltaV_Euler_upper=reports['physical_Euler_contact']['actual_unprojected_deltaV_Euler_upper'],
        unresolved_combined_remainder_upper=reports['physical_Euler_contact']['chi_plus_actual_deltaV_Euler_remainder_upper'],
        actual_physical_Euler_contact_controls_pass=True,
        source_domain_or_full_projected_operator_identity_closed=False,
        source_anchored_local_unsquared_exterior_construction_available=True,
        common_native_graded_factor_and_domain_identification_complete=False,
        physical_outgoing_realization_or_radial_solution_convergence=False,
        full_physical_outgoing_energy_field_source_domain_derivative_pass=False,
        original_coupled_corrections=0,original_Maxwell_and_all226_after_pass=False,
        physical_normalized_two_spin_muon=None,physical_muon_magnetic_moment=None,
        scientific_scope='Actual failed original-equation candidate and evaluated physical off-shell Euler contact; remaining coupled unknowns remain open')
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(out.read_bytes()).hexdigest(),sources=len(sources),numeric_inputs=len(numeric),packet_files=len(files))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

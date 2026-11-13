"""Bind actual finite Cauchy progress and same-field radial/MP form evidence.

Index blobs are checked explicitly. No finite/reference calculation is
promoted to a physical outgoing derivative, corrected state or prediction.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json
import mpmath as mp
import numpy as np
from bind_muon_real_coupled_open_operator_20261016 import staged_blobs
from bind_muon_real_changing_gauge_transport_20261016 import archive_bytes


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve every independent index binding')
    base=root/'artifacts/muon_actual_radial_cauchy_common_forms_20261016'
    selection=json.loads((base/'packet_selection.json').read_bytes())
    pairs={};reports={}
    for stem,group in selection['stages'].items():
        runs=group['runs'];directory=group['directory']
        folders=[base/directory/run for run in runs]
        lists=[sorted(p.relative_to(f) for p in f.rglob('*') if p.is_file()) for f in folders]
        if not lists[0] or any(v!=lists[0] for v in lists):raise ValueError('Independent inventories differ: '+stem)
        inventory=[]
        for rel in lists[0]:
            raw=(folders[0]/rel).read_bytes()
            if any((f/rel).read_bytes()!=raw for f in folders):raise ValueError('Independent bytes differ: '+stem+'/'+str(rel))
            inventory.append(dict(path=rel.as_posix(),bytes=len(raw),sha256=sha256(raw).hexdigest()))
        reports[stem]=json.loads((folders[0]/'result.json').read_bytes())
        pairs[stem]=dict(runs=runs,independent_pair=len(runs)==2,files=inventory)
    tail=reports['bhsm_original_target_new_coupled_tail_cell_20261016']
    actual=reports['bhsm_original_target_conditioned_four_canonical_cell_20261016']
    assert tail['status']=='GENUINELY_NEW_CLASSICAL_COUPLED_TAIL_CELL_ADMITTED'
    assert tail['initial_x_fixed_upper']==tail['initial_Pi_fixed_upper']==0
    assert not tail['prefix_replayed'] and tail['original_coupled_corrections']==0
    assert tail['original_target_history_guard']['final_primal_master368_bit_identical']
    assert actual['status']=='ALL_ACTUAL_MATRIX_FREE_ORIGINAL_CANONICAL_ROWS_PASS' and actual['finite_new_response_cell_admitted']
    assert actual['original526_response_upper']<=2e-10
    assert actual['clock_records'][0]['original210_upper']<=2e-10
    assert actual['same_gradient_reproduction_upper']==0
    assert not actual['prefix_primal_recomputed'] and not actual['old_response_prefix_replayed']
    assert actual['direct_CHILD_source_Hpp_not_parent_own'] and actual['parent_and_both_reference_clocks_once']
    assert actual['original_coupled_corrections']==0 and not actual['physical_source_domain_derivative_pass']
    assert actual['physical_outgoing_Y_R'] is None and actual['physical_affine_s_R'] is None
    for stem in ('bhsm_original_target_new_four_response_cell_20261016','bhsm_original_target_accelerated_four_response_cell_20261016','bhsm_original_target_resumed_four_canonical_cell_20261016'):
        assert not reports[stem]['finite_new_response_cell_admitted']
        assert not reports[stem]['physical_source_domain_derivative_pass'] and reports[stem]['original_coupled_corrections']==0
    unconditioned=reports['bhsm_original_target_resumed_four_canonical_cell_20261016']
    assert unconditioned['original526_response_upper']>2e-10
    scalar=reports['bhsm_scalar_wall_mp_complete_forms_20261016']
    assert scalar['full_offshell_gauge_scalar_contacts_retained'] and scalar['dependent_minus_eta_H_and_full_rate_retained']
    assert scalar['potential_lambda_and_lambda_nu_squared_unassigned'] and scalar['original_coupled_corrections']==0
    assert not scalar['physical_derivative_at_2e_minus10_passed']
    ym=reports['bhsm_changing_yang_mills_mp_values_20261016']
    assert ym['cases_radial_and_time']==[[64,8],[128,8],[128,12]]
    assert ym['original_positive_curvature_contact_retained'] and ym['coupled_corrections']==0
    assert not ym['physical_native_outgoing_or_full15_derivative_pass']
    all15=reports['bhsm_matched_common15_mp_composition_20261016']
    assert all15['finite_all15_scaled_matched_rule_pass']
    assert all15['common_kinetic_and_Gram_sum_before_comparison']
    assert not all15['physical_radial_solution_convergence'] and not all15['physical_energy_field_source_domain_derivative_pass']
    assert all15['original_coupled_corrections']==0 and all15['physical_muon_magnetic_moment'] is None
    assert len(all15['records'])==6
    for r in all15['records']:
        assert len(r['dimensions'])==15
        if r['comparisons'] is not None:
            assert len(r['comparisons'])==15 and r['all15_scaled_rule_pass']
    pi=reports['bhsm_matched_finite_lorenz_projectors_20261016']
    assert len(pi['records'])==6 and pi['original_coupled_corrections']==0 and not pi['physical_derivative_passed']
    for r in pi['records']:
        assert r['exact_finite_B_times_Pi_residual']['max_entry_upper']<2e-10
        assert r['exact_finite_Pi_idempotence_residual']['max_entry_upper']<2e-10
    radial={d:reports['original_ea02_same_field_D'+str(d)] for d in (4,6)}
    for d,r in radial.items():
        assert r['degree']==d and r['epoch_basis_value_and_clock_reconstructed_from_native_point_germs']
        assert r['selected_epoch_chart_held_for_variations'] and r['moving_epoch_basis_h_contact_retained_once']
        assert r['new_coefficients_zero_only_as_same_function_representation'] and not r['new_canonical_momenta_zero_assigned']
        assert r['primal_Euler_upper']>2e-10 and r['primal_Gauss_upper']>2e-10
        assert not r['physical_radial_convergence'] and not r['full_derivative_2e_10_passed']
        assert not r['full_linearized_new_position_residual_evaluated'] and r['original_coupled_corrections_applied']==0
    literal=reports['bhsm_original_ea02_same_field_euler_literal_control_20261016']
    assert literal['exact_common_test_value_and_clock_map_matches']==59 and not literal['full_outgoing_or_derivative_or_moment']

    aliases=json.loads((base/'consumed_input_aliases.json').read_bytes());wanted={};special=[]
    for alias,r in aliases.items():
        h=r['sha256']
        if 'path' in r:
            if r['path'] in wanted and wanted[r['path']]!=h:raise ValueError('Alias input conflict')
            wanted[r['path']]=h
        else:
            assert r['recipe']=='exact_raw_chunks_from_previous_packet'
            raw=archive_bytes(root/r['base'],r['archive'])
            assert sha256(raw).hexdigest()==h
            special.append(dict(alias=alias,**r))
    blobs=staged_blobs(root,sorted(wanted));sources={};numerical={}
    for rel,h in sorted(wanted.items()):
        raw=(root/rel).read_bytes();blob=blobs[rel]
        if sha256(raw).hexdigest()!=h:raise ValueError('Consumed raw input changed: '+rel)
        if raw==blob:recipe='identity'
        elif rel.endswith('.py') and b'\r\n' not in blob and raw==blob.replace(b'\n',b'\r\n'):
            recipe='replace_every_index_LF_with_CRLF'
        else:raise ValueError('Exact index reproduction unavailable: '+rel)
        target=sources if rel.endswith('.py') else numerical
        if target is numerical and recipe!='identity':raise ValueError('Numerical input normalization forbidden')
        target[rel]=dict(consumed_raw_sha256=h,index_sha256=sha256(blob).hexdigest(),index_to_consumed_recipe=recipe)
    # Bind copied proofs, all failures, aliases and independent outputs too.
    artifacts={p.relative_to(root).as_posix():p.read_bytes() for p in sorted(base.rglob('*')) if p.is_file() and p.name not in ('manifest_run_1.json','manifest_run_2.json')}
    ab=staged_blobs(root,sorted(artifacts))
    for rel,raw in artifacts.items():
        if raw!=ab[rel]:raise ValueError('Packet artifact index differs: '+rel)
        if len(raw)>10*1024*1024:raise ValueError('Oversized unsplit artifact: '+rel)
    me=Path(__file__).resolve();rel=me.relative_to(root).as_posix();raw=me.read_bytes()
    if staged_blobs(root,[rel])[rel]!=raw:raise ValueError('Binder index differs')
    audit_logs={}
    for name in ('status','forbidden_claims','frozen_integrity','precision','public_readiness'):
        p=base/'publication_audits'/f'{name}.log'
        content=p.read_text(encoding='utf8')
        if name=='precision':assert 'PASS' in content and 'FAIL' not in content
        else:assert json.loads(content)['passed']
        audit_logs[name]=sha256(p.read_bytes()).hexdigest()
    result=dict(classification='INDEX_BOUND_ACTUAL_FINITE_CAUCHY_RADIAL_AND_COMMON_FORM_PROGRESS',
        independent_pairs=pairs,source_pins=sources,numerical_input_pins=numerical,exact_raw_chunk_recipes=special,
        artifact_pins={k:sha256(v).hexdigest() for k,v in artifacts.items()},
        publication_audits=audit_logs,binder_sha256=sha256(raw).hexdigest(),
        new_actual_finite_clock210_upper=actual['clock_records'][0]['original210_upper'],
        new_actual_finite_original526_upper=actual['original526_response_upper'],
        finite_positive_all15_scaled_matched_rule_pass=True,
        physical_radial_solution_convergence=False,physical_outgoing_energy_field_source_domain_derivative_pass=False,
        prefix_cell7_incomplete_density_time_flag_closed=False,original_coupled_corrections=0,
        original_Maxwell_after_or_all226_after_pass=False,physical_normalized_two_spin_muon=None,physical_muon_magnetic_moment=None,
        unchanged_original_before_diagnostics=dict(Maxwell_RZ_3_2_absolute=2.4777309846820184,all226_max_absolute=9.602842247524184e-7),
        scientific_scope='Actual added finite original-branch cell and finite positive-reference quadrature progress; physical outgoing closure and full derivative remain open')
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(out.read_bytes()).hexdigest(),consumed_sources=len(sources),numeric_inputs=len(numerical),packet_files=len(artifacts))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

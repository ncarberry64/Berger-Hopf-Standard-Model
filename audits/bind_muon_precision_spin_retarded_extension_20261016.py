"""Bind same-cell MP precision repair and complete geometric Spin components.

Physical terminal/derivative/correction/prediction gates remain false. A
separate principal continuation is deliberately quarantined by provenance.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import xml.etree.ElementTree as ET
import mpmath as mp
import numpy as np

from bind_muon_real_coupled_open_operator_20261016 import staged_blobs,digest
from bind_muon_real_changing_gauge_transport_20261016 import archive_bytes
from bhsm_changing_lorenz_tensor_precision_20261016 import load_matrix,compare


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError(out)
    base=root/'artifacts/muon_precision_spin_retarded_extension_20261016'
    wanted={};pairs={};reports={}
    def include(items):
        for rel,h in items.items():
            if rel in wanted and wanted[rel]!=h:raise ValueError('Consumed operand disagreement: '+rel)
            wanted[rel]=h
    def pair(stem):
        a,b=[base/(stem+str(i)) for i in (1,2)]
        aa=sorted(p.relative_to(a) for p in a.rglob('*') if p.is_file())
        bb=sorted(p.relative_to(b) for p in b.rglob('*') if p.is_file())
        assert aa==bb and aa
        rows=[]
        for rel in aa:
            raw=(a/rel).read_bytes();assert raw==(b/rel).read_bytes(),str(a/rel)
            rows.append(dict(path=rel.as_posix(),bytes=len(raw),sha256=sha256(raw).hexdigest()))
        r=json.loads((a/'result.json').read_bytes())
        for field in ('source_and_owner_sha256','source_pins','raw_input_pins','input_and_source_sha256','input_sha256'):
            if field in r:include(r[field])
        pairs[stem]=rows;reports[stem]=r
        return r
    frozen=pair('frozen_tensor_run_')
    values=pair('MP_values_run_')
    ordinary=pair('ordinary_Gram_run_')
    gram=pair('complete_Gram_run_')
    spin=pair('spin_insertion_run_')
    positive=pair('positive_Cartan_run_')
    hopf=pair('Hopf_Spin_run_')
    ordinary8=pair('ordinary_time8_run_')
    ordinary12=pair('ordinary_time12_run_')
    temporal=pair('MP_time_run_')
    principal=pair('principal_branch_control_run_')
    assert principal['status']=='GENUINELY_NEW_CLASSICAL_COUPLED_TAIL_CELL_ADMITTED'
    assert principal['initial_x_fixed_upper']==principal['initial_Pi_fixed_upper']==0
    assert not principal['original_birth_matching_state_changed'] and principal['original_coupled_corrections']==0
    assert principal['new_physical_outgoing_graph'] is None and not principal['source_domain_physical_derivative_pass']
    assert not principal['new_four_response_columns_evaluated']
    assert frozen['classification']=='MP_TENSOR_LORENZ_CONTRACTION_OVER_FROZEN_ACTUAL_REAL_SAMPLES'
    assert not frozen['physical_derivative_pass'] and frozen['coupled_corrections']==0
    assert not frozen['fields_or_basis_resampled'] and not frozen['constant_background_moments_substituted']
    assert values['classification']=='MP_SAME_AFFINE_REAL_CELL_COEFFICIENT_AND_LORENZ_VALUES'
    assert values['quadrature_rule_mode']=='mp' and values['arithmetic_dps']==80
    assert values['anchored_response_order']==96 and values['temporal_order_per_half']==6
    assert not values['reference_coordinates_renormalized'] and not values['new_history_or_field_solution_selected']
    assert not values['physical_derivative_pass'] and values['coupled_corrections']==0
    assert values['physical_native_heat_operator'] is None and values['physical_exterior_load'] is None
    assert values['physical_reset_incidence'] is None and not values['matched_Higgs_or_surface_coefficients_assigned']
    radial={}
    for row in values['records']:
        assert digest(base/'MP_values_run_1'/f"{row['side']}_radial{row['radial_order']}"/'forms.npz')==row['numerical_sha256']
        assert row['no_physical_native_outgoing_derivative_or_state_claim']
        if row['radial_order']==128:
            d=row['full_unrounded_MP_adjacent_rule_comparisons']
            assert set(d)=={'B','F','fixing'}
            assert all(mp.mpf(v['max_entry_scaled'])<mp.mpf('2e-10') for v in d.values())
            radial[row['side']]=d
    assert set(radial)=={'incoming','outgoing'}
    assert not ordinary['complete15_form_or_native_convergence'] and not ordinary['physical_source_or_domain_derivatives_evaluated']
    assert not gram['all15_form_convergence'] and not gram['all1200_common_Gram_or_scalar_blocks_completed']
    assert gram['input_result_sha256']==dict(MP_values=digest(base/'MP_values_run_1/result.json'),ordinary_Gram=digest(base/'ordinary_Gram_run_1/result.json'))
    for r in gram['records']:
        selected=next(a for a in values['records'] if a['side']==r['side'] and a['radial_order']==r['radial_order'])
        assert r['source_B_numerical_sha256']==selected['numerical_sha256']
        if r['radial_order']==128:
            assert r['adjacent_orders_explicitly_guarded']==[64,128]
            assert r['component_bound_below_scaled_2e_minus10']
    assert spin['all10_noncommuting_and_commuting_channels_kept'] and spin['full128_and384_rows_preserved']
    assert not spin['physical_derivative_at_2e_minus10_passed'] and not spin['physical_outgoing_domain_selected']
    assert spin['coupled_corrections']==0 and spin['physical_muon_magnetic_moment'] is None
    assert not positive['actual_native_statistics_or_stratified_operator_identified']
    assert not positive['outgoing_or_wall_selfadjoint_D_E_domain_selected'] and positive['coupled_corrections']==0
    assert hopf['full_original_u_v_operator_directions_retained'] and not hopf['complement_set_zero']
    assert not hopf['associated_mode_projection_selected'] and not hopf['native_grading_or_SM_carrier_identified']
    assert not hopf['physical_energy_or_field_derivative_pass'] and hopf['coupled_corrections']==0
    assert temporal['classification']=='CHANGING_REAL_CELL_MP_TIME6_8_12_LORENZ_COMPONENT_CONTROL'
    assert temporal['completed_time6_receipt_sha256']==digest(base/'MP_values_run_1/result.json')
    assert not temporal['completed_time6_fields_recomputed'] and not temporal['full15_forms_native_outgoing_or_physical_derivative_pass']
    exact_moment_tuples=0
    for r in temporal['records']:
        assert r['radial_order']==128 and r['anchored_response_order']==96
        assert r['finite_Lorenz_component_time_rule_pass'] and not r['physical_derivative_pass'] and r['coupled_corrections']==0
        path=base/'MP_time_run_1'/f"{r['side']}_time{r['time_order_per_half']}/forms.npz"
        assert digest(path)==r['numerical_sha256']
        with np.load(path,allow_pickle=False)as z:
            for name in z.files:
                if name.startswith('moment_') and name.endswith('_exact_MP_tuple'):
                    for text in z[name].flat:
                        s,m,e,b=str(text).split(':');parts=(int(s),int(m,16),int(e),int(b))
                        assert parts[0] in (0,1) and parts[1].bit_length()==parts[3]
                        number=mp.make_mpf(parts)
                        assert number._mpf_==parts
                        exact_moment_tuples+=1
    ordinary_time=[]
    with mp.workdps(80):
        for side in ('incoming','outgoing'):
            rows=[next(r for r in a['records'] if r['side']==side and r['radial_order']==128)
                  for a in (ordinary,ordinary8,ordinary12)]
            for j,(lo,hi) in enumerate(((6,8),(8,12))):
                a,b=[rows[k]['all100_unrounded_MP_entries'] for k in (j,j+1)]
                maximum=mp.mpf(0)
                for ar,br in zip(a,b):
                    for x,y in zip(ar,br):
                        x,y=mp.mpf(x),mp.mpf(y)
                        ex,ey=abs(x)*mp.mpf('1e-62'),abs(y)*mp.mpf('1e-62')
                        value=(abs(x-y)+ex+ey)/max(1,abs(x)-ex,abs(y)-ey)
                        maximum=max(maximum,value)
                ordinary_time.append(dict(side=side,orders=[lo,hi],all100_entry_scaled_with_decimal_margin=mp.nstr(maximum,65),
                    scope='numerical MP80 coefficient/quadrature comparison, not interval upstream or physical-state accuracy'))
    precision=[]
    for stem,primary in (('MP_values_precision100','MP_values_run_1'),('frozen_tensor_precision100','frozen_tensor_run_1')):
        r=json.loads((base/stem/'result.json').read_bytes());include(r['source_and_owner_sha256'])
        assert not r['physical_derivative_pass'] and r['coupled_corrections']==0
        for row in r['records']:
            assert row['radial_order']==128 and row['arithmetic_dps']==100
            path=base/stem/f"{row['side']}_radial128/forms.npz"
            assert digest(path)==row['numerical_sha256']
            with np.load(path,allow_pickle=False)as hi,np.load(base/primary/f"{row['side']}_radial128/forms.npz",allow_pickle=False)as lo:
                d={name:compare(load_matrix(lo,name),load_matrix(hi,name))for name in ('B','F','fixing')}
            precision.append(dict(component=primary,side=row['side'],rounded_MP80_to_MP100=d))
    for stem,numeric in (('ordinary_Gram_run_','ordinary_Gram.npz'),('complete_Gram_run_','complete_one_form_Gram.npz'),
                         ('spin_insertion_run_','application.npz'),('positive_Cartan_run_','controls.npz'),('Hopf_Spin_run_','spin_lift.npz')):
        assert digest(base/(stem+'1')/numeric)==reports[stem]['numerical_sha256']

    previous=root/'artifacts/muon_real_changing_gauge_transport_20261016'
    original=archive_bytes(previous,'stable_time6_run_1/changing_forms.npz')
    assert sha256(original).hexdigest()=='9a132366d729c85ea1d83815a5482fbf6352b117507e9f447abb4c3b7534739d'
    for alias,h in frozen['actual_input_archive_sha256'].items():
        assert digest(root/'artifacts/muon_real_radial_spin_bolt_20261016/radial_run_1'/alias)==h
    for alias,h in values['input_archive_sha256'].items():
        if alias=='original_TIME6_archive':assert h==sha256(original).hexdigest()
        else:assert alias.startswith('frozen_MP_tensor/') and digest(base/'frozen_tensor_run_1'/alias.removeprefix('frozen_MP_tensor/'))==h
    for alias,h in temporal['input_archive_sha256'].items():
        assert alias.startswith('time6/') and digest(base/'MP_values_run_1'/alias.removeprefix('time6/'))==h
    for stem in ('anchored_root_run_','native_constraint_run_'):
        raw=(base/(stem+'1.json')).read_bytes();assert raw==(base/(stem+'2.json')).read_bytes()
        report=json.loads(raw);pairs[stem]=dict(sha256=sha256(raw).hexdigest())
        if stem.startswith('anchored'):
            include(report['source_byte_sha256'])
            assert not report['full_physical_derivative_at_2e_minus10'] and report['coupled_corrections']==0
        else:
            assert digest(base/'muon_ae4_native_heat_matching_constraints_20261016.txt')==report['note_sha256']
            assert not report['BHSM_continuum_nonuniqueness_proved'] and report['coupled_matching_corrections_applied']==0
            include({'audits/bhsm_native_heat_source_constraints_check_20261016.py':report['producer_sha256']})
    for stem in ('original_ea02_provenance_run_','mixed_angular_control_run_'):
        raw=(base/(stem+'1.json')).read_bytes();assert raw==(base/(stem+'2.json')).read_bytes()
        r=json.loads(raw);pairs[stem]=dict(sha256=sha256(raw).hexdigest())
        if stem.startswith('original'):
            include(r['input_sha256'])
            include({'audits/bhsm_original_ea02_saved_chain_provenance_20261016.py':r['source_sha256']})
            assert r['saved_accepted_chronology_only'] and not r['action_or_history_recomputed']
            assert r['final_master368_and_Pi158_high_low_bit_identical'] and len(r['records'])==8
            assert not r['physical_derivative_or_Maxwell226_pass'] and r['coupled_corrections']==0
        else:
            include({'audits/bhsm_changing_lorenz_mixed_tensor_control_20261016.py':r['control_source_sha256']})
            assert not r['physical_derivative_pass'] and not r['fields_changed'] and r['coupled_corrections']==0
    suite=ET.fromstring((base/'spin_insertion_unit_tests.xml').read_bytes()).find('testsuite')
    assert suite is not None and suite.attrib['tests']=='3' and suite.attrib['failures']=='0' and suite.attrib['errors']=='0'
    suite=ET.fromstring((base/'Hopf_Spin_unit_tests.xml').read_bytes()).find('testsuite')
    assert suite is not None and suite.attrib['tests']=='4' and suite.attrib['failures']=='0' and suite.attrib['errors']=='0'

    extra_sources=('audits/bind_muon_precision_spin_retarded_extension_20261016.py',
        'audits/bind_muon_real_changing_gauge_transport_20261016.py',
        'audits/bind_muon_real_coupled_open_operator_20261016.py',
        'tests/test_muon_spin_duhamel_insertion.py','tests/test_muon_m8_original_hopf_spin_lift.py')
    include({rel:digest(root/rel) for rel in extra_sources})
    blobs=staged_blobs(root,sorted(wanted));sources={};numeric={}
    for rel,h in sorted(wanted.items()):
        raw,blob=(root/rel).read_bytes(),blobs[rel]
        assert sha256(raw).hexdigest()==h,rel
        if rel.endswith('.py'):
            if raw==blob:recipe='identity'
            elif b'\r\n' not in blob and raw==blob.replace(b'\n',b'\r\n'):recipe='replace every staged LF with CRLF'
            else:raise ValueError('Unreconstructible consumed source: '+rel)
            sources[rel]=dict(actual_consumed_byte_sha256=h,staged_byte_sha256=sha256(blob).hexdigest(),reconstruction=recipe)
        else:
            assert raw==blob,rel
            numeric[rel]=h
    checks=json.loads((base/'publication_checks/results.json').read_bytes())
    assert len(checks)==5 and all(x['exit_code']==0 for x in checks.values())
    for name,r in checks.items():assert digest(base/'publication_checks'/(name+'.log'))==r['log_sha256']
    pins={p.relative_to(root).as_posix():digest(p) for p in sorted(base.rglob('*'))
          if p.is_file() and not p.name.startswith('publication_manifest_run_')}
    indexed=staged_blobs(root,sorted(pins))
    for rel,h in pins.items():assert sha256(indexed[rel]).hexdigest()==h,rel
    for rel in extra_sources:
        pins[rel]=digest(root/rel)
    result=dict(classification='MP_COEFFICIENT_RADIAL_REPAIR_AND_COMPLETE_GEOMETRIC_SPIN_COMPONENTS',
        independent_byte_identical_primary_pairs=pairs,
        principal_branch_control_is_original_ea02_response_branch=False,
        principal_branch_control_admissible_for_original226_or_four_histories=False,
        equal_coordinate_times_are_sufficient_to_splice_Cauchy_states=False,
        radial64_to128_unrounded_MP80_Lorenz_entrywise_scaled=radial,
        ordinary_covector_Gram_time6_8_12_numerical_comparisons=ordinary_time,
        full_Lorenz_component_time6_8_12_comparisons=temporal['records'],
        exact_MP_working_binary_moment_tuples_roundtrip_verified=exact_moment_tuples,
        explicit_MP80_to_MP100_precision_checks=precision,
        original_ea02_eight_cell_Cauchy_response_epoch_provenance_verified=True,
        full1120_one_form_Gram_completed=True,
        full15_form_time_source_or_physical_state_convergence=False,
        all10_spin_insertion_and_full_original_Hopf_frame_components_retained=True,
        quantum_native_module_statistics_or_global_domain_selected=False,
        physical_four_outgoing_histories_and_C0_Cj_completed=False,
        physical_full_energy_field_source_domain_derivative_at_2e_minus10=False,
        original_coupled_matching_corrections_applied=0,physical_normalized_muon_spins=None,
        muon_magnetic_moment_prediction=None,Maxwell_after_correction=None,original226_after_correction=None,
        retained_before_Maxwell=2.4777309846820184,retained_before_original226_max=9.602842247524184e-7,
        required_original_physical_tolerance=2e-10,
        five_repository_publication_checks_passed=True,
        numerical_input_exact_byte_hashes=numeric,source_byte_reconstruction=sources,
        current_artifact_byte_hashes=dict(sorted(pins.items())))
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(sha256=digest(out),sources=len(sources),numeric=len(numeric),artifacts=len(pins))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

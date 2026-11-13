"""Bind changing-cell quadrature diagnosis and supported wall transport."""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
import argparse
import json
import numpy as np
from scipy.sparse import csr_matrix

from bind_muon_real_coupled_open_operator_20261016 import staged_blobs, digest


def archive_bytes(base, rel):
    path=base/rel
    if path.exists():return path.read_bytes()
    recipes=json.loads((base/'exact_archive_reconstruction.json').read_bytes())
    recipe=recipes[rel];chunks=[]
    for part in recipe['chunks']:
        raw=(base/part['path']).read_bytes()
        assert len(raw)==part['bytes'] and sha256(raw).hexdigest()==part['sha256']
        chunks.append(raw)
    raw=b''.join(chunks)
    assert len(raw)==recipe['original_bytes'] and sha256(raw).hexdigest()==recipe['original_byte_sha256']
    return raw


def matrix(z,name):
    return csr_matrix((z[name+'_data'],z[name+'_indices'],z[name+'_indptr']),shape=tuple(z[name+'_shape']))


def scaled_difference(a,b):
    d=(a-b).tocoo()
    if not d.nnz:return 0.
    scale=np.maximum(1.,np.maximum(abs(a[d.row,d.col]).A1,abs(b[d.row,d.col]).A1))
    return float(np.max(abs(d.data)/scale))


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError(out)
    base=root/'artifacts/muon_real_changing_gauge_transport_20261016'
    specs=dict(naive=('preserved_naive16_run_','changing_forms.npz'),
        stable_time4=('stable_time4_run_','changing_forms.npz'),
        stable_time6=('stable_time6_run_','changing_forms.npz'),
        SM12=('changing_SM12_run_','changing_SM12_forms.npz'),
        child_transport=('child_transport_run_','application.npz'))
    reports,pairs={},{}
    for key,(prefix,archive) in specs.items():
        dirs=[prefix+str(i) for i in(1,2)]
        left,right=[(base/d/'result.json').read_bytes() for d in dirs]
        assert left==right
        a,b=[archive_bytes(base,d+'/'+archive) for d in dirs]
        assert a==b
        report=json.loads(left)
        assert sha256(a).hexdigest()==report['numerical_sha256']
        reports[key]=report
        pairs[key]=dict(directories=dirs,independent_executions_byte_identical=True,
            numerical_sha256=report['numerical_sha256'],result_sha256=sha256(left).hexdigest())
    naive,t4,t6,sm,transport=(reports[k] for k in specs)
    assert naive['radial_orders']==[4,8,16] and naive['time_order_per_tent_half']==4
    for report,n in((t4,4),(t6,6)):
        assert report['radial_orders']==[4,8,16,32] and report['time_order_per_tent_half']==n
        assert report['rounded_sigma_not_used_to_reconstruct_production_weight']
        assert not report['full_physical_outgoing_E_B_derivative_at_2e_minus10']
        assert report['coupled_corrections']==0
    assert t4['preserved_naive_reference_sha256']==dict(result=pairs['naive']['result_sha256'],archive=pairs['naive']['numerical_sha256'])
    assert t6['preserved_naive_reference_sha256'] is None
    assert sm['consumed_EW_numerical_sha256']==pairs['stable_time6']['numerical_sha256']
    assert sm['radial_orders']==[4,8,16,32] and sm['time_order_per_tent_half']==6
    assert sm['full_actual_EW_Higgs_matrices_copied_without_modification']
    assert not sm['full_physical_E_B_derivative_at_2e_minus10'] and sm['coupled_corrections']==0
    with (np.load(BytesIO(archive_bytes(base,'stable_time6_run_1/changing_forms.npz')),allow_pickle=False) as ew,
          np.load(BytesIO(archive_bytes(base,'changing_SM12_run_1/changing_SM12_forms.npz')),allow_pickle=False) as full):
        comparisons={}
        for side in('incoming','outgoing'):
            comparisons[side]={}
            prefix=f'{side}_radial32_'
            names=sorted(k[len(prefix):-6]for k in ew.files if k.startswith(prefix)and k.endswith('_shape'))
            assert len(names)==15
            for name in names:
                comparisons[side][name]=scaled_difference(matrix(ew,f'{side}_radial16_{name}'),matrix(ew,f'{side}_radial32_{name}'))
            for q in(4,8,16,32):
                prefix=f'{side}_radial{q}_'
                for left,right in(('common_kinetic_Hessian','kinetic_Hessian'),('common_Gram','Gram'),
                        ('scalar_lambda_coefficient','lambda_coefficient'),('scalar_lambda_nu_squared_coefficient','lambda_nu_squared_coefficient')):
                    original=matrix(ew,prefix+left);expanded=matrix(full,prefix+'SM12_'+right)
                    assert expanded.shape==(3440,3440) and original.shape==(1200,1200)
                    assert (expanded[:1200,:1200]-original).nnz==0
                    assert expanded[:1200,1200:].nnz==0 and expanded[1200:,:1200].nnz==0
    assert transport['classification']=='SUPPORTED_REAL_CHILD_WALL_FUNDAMENTAL_WORLDVOLUME_CLOCK_U2_TRANSPORT'
    assert transport['physical_initial_F0'] is None and transport['physical_initial_U0'] is None
    assert not transport['physical_F_B_or_full_spin_bundle_lift_evaluated']
    assert not transport['complete_physical_derivative_at_2e_minus10']
    assert transport['spin_deletion_or_coupled_corrections']==0
    assert transport['Wilson_increment_nonzero_norm']>0 and transport['nonzero_wall_spin_boost_and_source_frames_retained']
    assert transport['independent_MP_exponential_increment']['max_nonzero_component_relative']<2e-10
    assert transport['local_conditional_metric_radius_first_residual']!=0
    assert not transport['supported_orientation_preserving_two_side_clock_interval_has_positive_length']

    first=(base/'rule_comparison_run_1.json').read_bytes()
    assert first==(base/'rule_comparison_run_2.json').read_bytes()
    rule=json.loads(first)
    assert rule['classification']=='SAME_CHANGING_BACKGROUND_FIXED_CHART_RULE_COMPARISONS'
    assert len(rule['temporal_comparisons'])==8 and len(rule['time6_radial_comparisons'])==6
    assert rule['all_matrix_entries_and_unfavorable_rules_retained']
    assert not rule['physical_convergence_claimed'] and rule['coupled_corrections']==0
    for row in rule['time6_radial_comparisons']:
        if row['radial_orders']==[16,32]:
            assert len(row['matrices'])==15
            for name,record in row['matrices'].items():
                assert abs(comparisons[row['side']][name]-record['max_entry_scaled'])<5e-15
    assert max(comparisons['incoming'].values())>0.005
    moments=rule['constant_owned_ghost_temporal_moment_controls']
    assert abs(moments[0]['odd_bubble_square_relative'])>0.004
    assert abs(moments[1]['odd_bubble_square_relative'])<2e-12
    assert abs(moments[2]['odd_bubble_square_relative'])<2e-12
    reports['all_block_rule_comparison']=rule
    pairs['all_block_rule_comparison']=dict(independent_executions_byte_identical=True,
        result_sha256=sha256(first).hexdigest())

    # These aliases retain the exact externally consumed bytes, including a
    # lossless chunk reconstruction of the original >10MiB numerical archive.
    aliases={'retained_inputs/result.json':'stable_time6_run_1/result.json',
             'retained_inputs/changing_forms.npz':'stable_time6_run_1/changing_forms.npz',
             'stable_time4/result.json':'stable_time4_run_1/result.json',
             'stable_time4/changing_forms.npz':'stable_time4_run_1/changing_forms.npz',
             'stable_time6/result.json':'stable_time6_run_1/result.json',
             'stable_time6/changing_forms.npz':'stable_time6_run_1/changing_forms.npz'}
    wanted={};external={}
    for report in reports.values():
        for rel,h in report['input_and_source_sha256'].items():
            if rel=='comparison_source':rel='audits/bhsm_changing_cell_rule_comparison_20261016.py'
            if rel in aliases:
                assert sha256(archive_bytes(base,aliases[rel])).hexdigest()==h
                external[rel]=dict(original_byte_sha256=h,archived_relative_path=aliases[rel],
                    encoding='identity or exact raw-chunk concatenation; no numeric reencoding')
                continue
            if rel in wanted and wanted[rel]!=h:raise ValueError('Conflicting operand: '+rel)
            wanted[rel]=h
    blobs=staged_blobs(root,sorted(wanted));sources={};numeric={}
    for rel,h in sorted(wanted.items()):
        raw,blob=(root/rel).read_bytes(),blobs[rel]
        assert sha256(raw).hexdigest()==h,rel
        if rel.endswith('.py'):
            if raw==blob:recipe='identity'
            elif b'\r\n' not in blob and raw==blob.replace(b'\n',b'\r\n'):recipe='replace every staged LF with CRLF'
            else:raise ValueError('Unreconstructible source: '+rel)
            sources[rel]=dict(actual_consumed_byte_sha256=h,staged_byte_sha256=sha256(blob).hexdigest(),reconstruction=recipe)
        else:
            assert raw==blob,rel
            numeric[rel]=h
    checks=json.loads((base/'publication_checks/results.json').read_bytes())
    assert len(checks)==5 and all(v['exit_code']==0 for v in checks.values())
    for name,record in checks.items():assert digest(base/'publication_checks'/(name+'.log'))==record['log_sha256']
    pins={p.relative_to(root).as_posix():digest(p) for p in sorted(base.rglob('*'))
        if p.is_file() and not p.name.startswith('publication_manifest_run_')}
    # Every archived chunk must be raw/index-identical, just like a whole NPZ.
    staged=staged_blobs(root,sorted(pins))
    for rel,h in pins.items():assert sha256(staged[rel]).hexdigest()==h,rel
    for rel in('audits/bind_muon_real_changing_gauge_transport_20261016.py',
              'audits/bind_muon_real_coupled_open_operator_20261016.py',
              'artifacts/muon_real_ew_common_forms_20261016/publication_manifest_run_1.json'):
        pins[rel]=digest(root/rel)
    result=dict(classification='CHANGING_REAL_CLASSICAL_GAUGE_QUADRATURE_REPAIR_AND_SUPPORTED_WALL_TRANSPORT',
        independent_control_pairs=pairs, five_repository_publication_audits_passed=True,
        corrected_density_evaluates_owned_4p_1_minus_p_directly=True,
        corrected_six_point_trial_rule_resolves_degree10_ghost_moment=True,
        corrected_temporal_rule_is_exact_for_all_changing_physical_coefficients=False,
        all_failed_coarse_and_naive_controls_retained=True,
        radial16_to32_entrywise_absolute_or_relative_comparisons=comparisons,
        component_radial32_convergence_at_2e_minus10=False,
        exact_SM12_expansion_retains_original_EW_blocks=True,
        supported_child_wall_clock_and_U2_fundamental_transport_evaluated=True,
        physical_initial_F0_U0_or_full_reset_solved=False,
        physical_common_native_operator_domain_and_outgoing_E_B_response_solved=False,
        physical_full_derivative_at_2e_minus10=False,coupled_corrections_applied=0,
        normalized_physical_spins=None,muon_magnetic_moment_prediction=None,
        Maxwell_after_correction=None,original226_after_correction=None,
        required_physical_tolerance=2e-10, retained_before_Maxwell=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        external_numerical_aliases=external,numerical_input_byte_hashes=numeric,
        source_byte_reconstruction=sources,current_artifact_byte_hashes=dict(sorted(pins.items())))
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(sha256=digest(out),sources=len(sources),numerical=len(numeric),artifacts=len(pins))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.output)

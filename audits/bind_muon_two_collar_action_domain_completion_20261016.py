"""Bind the original two-collar correction without promoting physical gates."""
from pathlib import Path
from hashlib import sha256
import argparse
import json

from bind_muon_real_coupled_open_operator_20261016 import staged_blobs


def digest(raw):return sha256(raw).hexdigest()


def bind(repository,output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError(out)
    base=root/'artifacts/muon_two_collar_action_domain_completion_20261016'
    index=json.loads((base/'evidence_index.json').read_bytes())
    review=json.loads((base/'review_receipt.json').read_bytes())
    assert review['mathematics_and_scope_review_passed']
    assert all(review['scope_checks'].values())
    assert len(index['proofs'])==3 and len(index['source_snapshots'])==28
    for stem,item in index['proofs'].items():
        assert digest((base/item['note']).read_bytes())==item['sha256']
        assert digest((base/item['pins']).read_bytes())==item['pins_sha256']
        assert review['proof_sha256'][stem]==item['sha256']
    rels=sorted(set(index['source_snapshots'])|set(index['exact_data_references']))
    blobs=staged_blobs(root,rels)
    for rel,item in index['source_snapshots'].items():
        raw=(root/item['snapshot']).read_bytes();blob=blobs[rel]
        assert digest(raw)==item['sha256'] and digest(blob)==item['index_sha256'],rel
        if item['reconstruction']=='identity':assert raw==blob,rel
        elif item['reconstruction']=='replace_every_index_LF_with_CRLF':
            assert b'\r\n'not in blob and raw==blob.replace(b'\n',b'\r\n'),rel
        else:raise ValueError('Unknown source reconstruction')
    for rel,expected in index['exact_data_references'].items():
        assert digest((root/rel).read_bytes())==expected,rel
        assert digest(blobs[rel])==expected,rel
    for name,expected in index['archival_generators'].items():
        assert digest((base/'archival_generators'/name).read_bytes())==expected
    a,b=(base/f'application_run_{i}/result.json'for i in(1,2))
    assert a.read_bytes()==b.read_bytes()
    assert digest(a.read_bytes())==index['paired_original_two_boundary_result_sha256']
    application=json.loads(a.read_bytes())
    assert application['new_D5_profile_history_or_quadrature_integrations']==0
    assert not application['earlier_isotropic_Cayley_campaign_rerun']
    assert not application['complete_common_native_graded_domain_realized']
    assert not application['full_physical_derivative_passed_at_2e_minus_10']
    assert application['original_coupled_corrections_applied']==0
    for row in application['records']:
        assert row['full_spin_SM_family_fiber']==384
        assert row['original_two_boundary_traces']==768 and row['additional_trace_copies']==0
        assert max(row['independent_literal_two_boundary_comparison'].values())<2e-11
        assert row['nonzero_free_hard_graph_surface_defect_norm']>1e-4
        assert row['supplied_partial_zero_contacts_are_not_physical_E_B_domain_zeros']
        assert max(v for values in row['original_equation_rows'].values()for v in values.values())<1e-9
    tests=json.loads((base/'focused_tests.json').read_bytes())
    assert tests['passed']==3 and tests['exit_code']==0
    assert digest((base/'focused_tests.log').read_bytes())==tests['log_sha256']
    for rel,expected in tests['source_sha256'].items():
        assert digest((root/rel).read_bytes())==expected
        assert digest(staged_blobs(root,[rel])[rel])==expected
    checks=json.loads((base/'publication_audits/results.json').read_bytes())
    assert len(checks)==5
    for name,item in checks.items():
        assert item['exit_code']==0 and item['passed']
        raw=(base/'publication_audits'/(name+'.log')).read_bytes()
        assert digest(raw)==item['log_sha256']
        if name=='precision':assert b'PASS'in raw and b'FAIL'not in raw
        else:assert json.loads(raw)['passed']
    pins={}
    for path in sorted(base.rglob('*')):
        if path.is_file()and not path.name.startswith('publication_manifest_run_'):
            pins[path.relative_to(root).as_posix()]=digest(path.read_bytes())
    pins[Path(__file__).resolve().relative_to(root).as_posix()]=digest(Path(__file__).read_bytes())
    result=dict(classification='ACTION_DERIVED_ORIGINAL_TWO_COLLAR_DOMAIN_CORRECTION_WITH_COMMON_ASSEMBLY_IDENTITIES',
        modern_local_collar_laws_reconciled_from_original_action=True,
        old_free_hard_interacting_domain_preserved_unchanged=False,
        original_two_trace_count=768,full_spin_SM_family_fiber=384,extra_field_copies=0,
        paired_component_result_sha256=digest(a.read_bytes()),
        component_partial_source_check_is_full_physical_derivative_gate=False,
        focused_tests_passed=3,publication_process_audits_passed=5,
        shared_background_scalar_Jacobi_and_conditional_localization_maps_derived=True,
        complete_physical_common_native_graded_operator_domain_realized=False,
        physical_radial_convergence_established=False,
        full_outgoing_energy_magnetic_domain_response_evaluated=False,
        full_physical_derivative_passed_at_2e_minus_10=False,
        original_coupled_corrections_applied=0,
        Maxwell_and_all226_after_correction_validated=False,
        physical_two_spin_normalization=None,physical_muon_magnetic_moment=None,
        new_D5_profile_history_or_quadrature_integrations=0,
        unchanged_before_Maxwell=2.4777309846820184,
        unchanged_before_226_maximum=9.602842247524184e-7,
        before_residuals_recomputed_by_this_packet=False,
        required_original_full_residual_tolerance=2e-10,
        source_snapshots=28,exact_data_references=7,
        packet_and_binder_sha256=pins)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest=out.name,sha256=digest(out.read_bytes()),local_domain_reconciled=True,full_physical_derivative_passed=False,corrections=0)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();bind(args.repository,args.output)

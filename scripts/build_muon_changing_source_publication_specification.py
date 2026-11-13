"""Explicit publication recipe for the reviewed inherited-source application."""
from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]


def main():
    base=ROOT/'artifacts/muon_changing_source_publication_20261012'
    if base.exists():raise FileExistsError('preserve prior selection output')
    manifests=[]
    for folder in ('muon_stored_admission_correction_20261012','muon_changing_canonical_source_20261012',
            'muon_corrected_birth_source_endpoint_20261012','muon_changing_source_action_accuracy_20261012'):
        manifests.append(f'artifacts/{folder}/pair_verification/publication_manifest.json')
    for side in ('incoming','outgoing'):
        for case in ('normal_basis','area_source'):
            manifests.extend((f'artifacts/muon_holomorphic_current_source_20261012/{side}_{case}_pair_verification/publication_manifest.json',
                f'artifacts/muon_holomorphic_current_source_20261012/{side}_{case}_em_current_pair_verification/publication_manifest.json',
                f'artifacts/muon_holomorphic_n1_magnetic_action_20261012/{side}_{case}_pair_verification/publication_manifest.json'))
    manifests.extend(('artifacts/muon_holomorphic_n1_magnetic_operands_20261012/compact_publication_run_1/publication_manifest.json',
        'artifacts/muon_holomorphic_n1_magnetic_quadratic_action_20261012/pair_verification/publication_manifest.json',
        'artifacts/muon_holomorphic_n3_magnetic_return_20261012/pair_verification/publication_manifest.json',
        'artifacts/muon_holomorphic_magnetic_birth_source_20261012/pair_verification/publication_manifest.json',
        'artifacts/muon_inherited_magnetic_endpoint_cotangent_20261012/pair_verification/publication_manifest.json',
        'artifacts/muon_inherited_magnetic_weak_combination_20261012/pair_verification_final/publication_manifest.json',
        'artifacts/muon_inherited_magnetic_pure_trace_20261012/pair_verification/publication_manifest.json'))
    extra=['theory/muon_common_domain_physical_matching_20261012.md',
        'artifacts/muon_observable_combination_20261011/contribution_error_table.json',
        'artifacts/muon_observable_combination_20261011/contribution_error_table.md',
        'scripts/update_muon_observable_accounting.py',
        'src/bhsm/interface/muon_full_profile_source_weak_application.py',
        'tests/test_muon_full_profile_source_weak_application.py',
        'src/bhsm/interface/muon_holomorphic_magnetic_current_source_jet.py',
        'tests/test_muon_mixed_magnetic_current_independent.py',
        'tests/test_muon_stored_admission_transpose.py',
        'artifacts/muon_changing_source_final_focused_tests_20261012.log',
        'artifacts/muon_mixed_magnetic_current_independent_tests_20261012.log',
        'artifacts/muon_holomorphic_n1_magnetic_action_20261012/consumption_summary.json',
        'artifacts/muon_holomorphic_n1_magnetic_operands_20261012/compact_publication_run_2/publication_manifest.json',
        'artifacts/muon_holomorphic_n1_magnetic_operands_20261012/compact_pair_verification/verification.json',
        'artifacts/muon_holomorphic_n1_magnetic_operands_20261012/compact_publication_run_1.stdout.txt',
        'artifacts/muon_holomorphic_n1_magnetic_operands_20261012/compact_publication_run_2.stdout.txt',
        'artifacts/muon_holomorphic_n1_magnetic_operands_20261012/compact_pair_verification.stdout.txt',
        'artifacts/muon_changing_canonical_source_20261012/run_1/failure_verification.json',
        'artifacts/muon_inherited_magnetic_weak_combination_20261012/final_execution_records.json',
        'artifacts/muon_changing_source_accounting_20261012.stdout.txt',
        'artifacts/muon_changing_source_accounting_20261012.stderr.txt',
        'artifacts/muon_changing_source_accounting_20261012.execution.json',
        'artifacts/muon_holomorphic_magnetic_birth_source_pair_verification_20261012.stdout.txt',
        Path(__file__).relative_to(ROOT).as_posix()]
    for n in manifests+extra:
        if not (ROOT/n).is_file():raise FileNotFoundError(n)
    frozen={'docs/frozen_predictions.md':'9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4',
        'docs/frozen_predictions.json':'f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7'}
    for rel,h in frozen.items():
        b=(ROOT/rel).read_bytes()
        if sha256(b).hexdigest()!=h:raise ValueError('frozen working bytes changed')
        head=subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false','show','HEAD:'+rel],cwd=ROOT)
        if b.replace(b'\r\n',b'\n')!=head.replace(b'\r\n',b'\n'):
            raise ValueError('frozen prediction content changed from checked HEAD')
    spec=dict(manifests=manifests,manifest_hashes={p:sha256((ROOT/p).read_bytes()).hexdigest()for p in manifests},
        additional_files=extra,frozen_predictions=frozen,
        commands=dict(accounting_execution='artifacts/muon_changing_source_accounting_20261012.execution.json',
            source_action_reproduction='exact commands/environment/logs owned by each selected pair manifest',
            final_weak_execution='artifacts/muon_inherited_magnetic_weak_combination_20261012/final_execution_records.json',
            selection=['C:/Python314/python.exe','scripts/verify_muon_changing_source_publication.py','--specification',
                'artifacts/muon_changing_source_publication_20261012/specification.json','--output','artifacts/muon_changing_source_publication_20261012/run_1'],
            publication_audits=['C:/Python314/python.exe','scripts/record_muon_matching_publication_audits.py',
                '--output','artifacts/muon_changing_source_publication_audits_20261012/run_1']),
        classifications=dict(DERIVED='signed action/source/canonical/transpose/weak-corner and Duhamel/boundary consumer identities at declared domains',
            EVALUATED='bounded stored correction, full complementary source, fresh canonical source responses, actual constrained birth and inherited child, complete endpoint/source/weak returns and unsquared current/transfer operands',
            CONTROL_ONLY='computational normal/area and n0+n1 states; preserved old restarted-child contacts/quadratic/n3 and initial-I domain',
            UNEVALUATED='candidate natural endpoint stationarity and physical formation/energy/tension/exterior; pole/charge/residue/LSZ, positive native own mean/both insertions/overlap, angular/weak/quark completion and final normalized Pauli uncertainty',
            OWNER_DEFINITION_GAP='none established: action/matching equations and concrete candidate residual remain'),
        scientific_remaining_relation=dict(row_index_zero_based=223,row_index_one_based=224,owner='coupled_reset_application',
            term='first normalized common attachment temporal dual from full292 phase lift and theta=(2PiP_own-PiP_graph,-PiC_graph,0_y)',
            real=1.6604341810934722e-6,imaginary=-4.698748509499356e-6,absolute=4.983500699836006e-6,
            guard=2e-10,scope='retained tree-lambda/unassigned-tension candidate binary action; no physical branch nonexistence or definition gap'),
        preserved_local_subtotal=.0011659186179552334,physical_native_remainder_or_a_mu_completed=False)
    base.mkdir();p=base/'specification.json'
    p.write_text(json.dumps(spec,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifests=len(manifests),additional_files=len(extra),
        specification_sha256=sha256(p.read_bytes()).hexdigest(),ledger_bytes=(ROOT/extra[1]).stat().st_size)))


if __name__=='__main__':main()

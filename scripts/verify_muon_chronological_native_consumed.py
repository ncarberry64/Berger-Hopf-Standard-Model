"""Verify executed chronological contractions and their exact consumer bytes."""
from __future__ import annotations
import argparse
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify_muon_primal_native_action_applications as publication

FOLDER=ROOT/'artifacts/muon_chronological_native_consumed_20261011'
BASELINE='6d5c74706d7ae3a55d889c3610ea3131dd7e7a13'
COMPONENTS=(
    'artifacts/muon_parent_gauge_geometry_correction_20261010/full220_attachment_verification.json',
    'artifacts/muon_parent_gauge_geometry_correction_20261010/attached_phase_verification.json',
    'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_verification.json',
    'artifacts/muon_primal_cell_native_heat_20261010/verification.json',
    'artifacts/muon_primal_cell_reached_source_heat_20261010/verification.json',
    'artifacts/muon_current_source_motion_mean_load_20261010/verification.json',
    'artifacts/muon_attached_source_mean_load_20261011/verification.json',
    'artifacts/muon_attached_native_source_pair_20261011/publication_manifest.json',
    'artifacts/muon_attached_native_source_pair_20261011/verification.json',
    'artifacts/muon_primal_electromagnetic_source_20261011/publication_manifest.json',
    'artifacts/muon_primal_electromagnetic_source_20261011/verification.json',
    'artifacts/muon_electromagnetic_source_mean_load_20261011/verification.json',
    'artifacts/muon_electromagnetic_native_source_pair_20261011/publication_manifest.json',
    'artifacts/muon_electromagnetic_native_source_pair_20261011/verification.json',
    'artifacts/muon_electromagnetic_soft_magnetic_source_20261011/publication_manifest.json',
    'artifacts/muon_electromagnetic_soft_magnetic_source_20261011/verification.json',
    'artifacts/muon_chronological_boundary_action_20261011/verification.json',
    'artifacts/muon_chronological_normal_inertia_20261011/verification.json',
    'artifacts/muon_chronological_normal_boundary_response_20261011/verification.json',
)
PAIRS=(
    ('muon_trace_enriched_reached_action_20261010','incoming_run_1','incoming_run_2'),
    ('muon_trace_enriched_reached_action_20261010','outgoing_run_1','outgoing_run_2'),
    ('muon_attached_reached_action_20261011','incoming_run_1','incoming_run_2'),
    ('muon_attached_reached_action_20261011','outgoing_run_1','outgoing_run_2'),
    ('muon_primal_native_phase_adjoint_20261010','run_1','run_2'),
    ('muon_primal_native_phase_adjoint_20261010','certificate_run_1','certificate_run_2'),
    ('muon_attached_native_phase_adjoint_20261011','run_1','run_2'),
    ('muon_attached_native_phase_adjoint_20261011','certificate_run_1','certificate_run_2'),
    ('muon_attached_native_photon_return_20261011','run_2','run_3'),
    ('muon_electromagnetic_native_phase_adjoint_20261011','run_1','run_2'),
    ('muon_electromagnetic_native_phase_adjoint_20261011','certificate_run_1','certificate_run_2'),
    ('muon_electromagnetic_native_photon_return_20261011','run_2','run_3'),
    ('muon_paired_local_vp_pauli_20261011','run_1','run_2'),
    ('muon_paired_local_vp_soft_readout_20261011','run_3','run_4'),
    ('muon_magnetic_source_action_20261011','incoming_run_4','incoming_run_5'),
    ('muon_magnetic_source_action_20261011','outgoing_run_1','outgoing_run_2'),
    ('muon_magnetic_source_mean_load_20261011','run_3','run_4'),
    ('muon_magnetic_native_phase_adjoint_20261011','run_1','run_2'),
    ('muon_magnetic_native_phase_adjoint_20261011','certificate_run_1','certificate_run_2'),
)
EXTRA_STEMS=('muon_trace_enriched_reached_action','muon_primal_native_phase_adjoint')
ROOT_SOURCE_FILES=(
    'src/bhsm/interface/muon_causal_source_photon_action.py',
    'tests/test_muon_causal_source_photon_action.py',
    'src/bhsm/interface/muon_native_adjoint_arithmetic.py',
    'tests/test_muon_native_adjoint_arithmetic.py',
    'scripts/evaluate_muon_attached_reached_action.py',
    'scripts/evaluate_muon_attached_native_phase_adjoint.py',
    'scripts/certify_muon_primal_native_phase_adjoint.py',
    'scripts/certify_muon_attached_native_phase_adjoint.py',
    'scripts/evaluate_muon_attached_native_photon_return.py',
    'src/bhsm/interface/muon_electromagnetic_source_photon_action.py',
    'tests/test_muon_electromagnetic_source_photon_action.py',
    'scripts/evaluate_muon_electromagnetic_native_phase_adjoint.py',
    'scripts/certify_muon_electromagnetic_native_phase_adjoint.py',
    'scripts/evaluate_muon_electromagnetic_native_photon_return.py',
    'src/bhsm/interface/muon_paired_local_vp_pauli.py',
    'tests/test_muon_paired_local_vp_pauli.py',
    'scripts/evaluate_muon_paired_local_vp_pauli.py',
    'scripts/evaluate_muon_paired_local_vp_soft_readout.py',
    'src/bhsm/interface/muon_magnetic_source_photon_action.py',
    'tests/test_muon_magnetic_source_photon_action.py',
    'scripts/evaluate_muon_magnetic_source_action.py',
    'scripts/evaluate_muon_magnetic_native_phase_adjoint.py',
    'scripts/certify_muon_magnetic_native_phase_adjoint.py',
)


def execution_record(argv,stem,exit_code,error_scope):
    logs={name:ROOT/f'artifacts/{stem}.{name}.txt' for name in ('stdout','stderr')}
    return dict(argv=argv,cwd=str(ROOT),exit_code=exit_code,
        environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),
        logs={name:dict(**publication.identity(path),text=path.read_text(encoding='utf8',errors='replace')) for name,path in logs.items()},
        error_scope=error_scope)


def root_executions():
    py='C:\\Python314\\python.exe';rows=[]
    response_scope='finite coupled488 first source/adjoint/Gauss application; no continuum or Pauli bound'
    for tag,phase in (('trace_enriched','enriched'),('attached','attached')):
        for side in ('incoming','outgoing'):
            for run in (1,2):
                command=[py,f'scripts/evaluate_muon_{tag}_reached_action.py','--phase-directory',
                    f'artifacts/muon_parent_gauge_geometry_correction_20261010/{phase}_phase_{side}_1steps_run_1',
                    '--output',f'artifacts/muon_{tag}_reached_action_202610'+('10' if tag=='trace_enriched' else '11')+f'/{side}_run_{run}',
                    '--time-nodes','5','--time-steps','64']
                rows.append(execution_record(command,f'muon_{tag}_reached_{side}_run_{run}',0,response_scope))
    for tag,date,mean in (('primal','20261010','muon_current_source_motion_mean_load_20261010/run_3'),
                          ('attached','20261011','muon_attached_source_mean_load_20261011/run_1')):
        for run in (1,2):
            rows.append(execution_record([py,f'scripts/evaluate_muon_{tag}_native_phase_adjoint.py','--mean-directory',
                'artifacts/'+mean,'--output',f'artifacts/muon_{tag}_native_phase_adjoint_{date}/run_{run}'],
                f'muon_{tag}_native_phase_adjoint_run_{run}',0,'stored full358 phase response contracted through the same raw268 native target; physical soft vertex not supplied by this contraction'))
            rows.append(execution_record([py,f'scripts/certify_muon_{tag}_native_phase_adjoint.py','--application-directory',
                f'artifacts/muon_{tag}_native_phase_adjoint_{date}/run_1','--output',
                f'artifacts/muon_{tag}_native_phase_adjoint_{date}/certificate_run_{run}','--precision-bits','192'],
                f'muon_{tag}_native_phase_adjoint_certificate_run_{run}',0,'outward exact stored matrix/readout/load arithmetic only; source formation, continuum, cutoff, overlap and soft matching excluded'))
    for run in (1,2,3):
        argv=[py,'scripts/evaluate_muon_attached_native_photon_return.py','--pair-directory',
            'artifacts/muon_attached_native_source_pair_20261011/run_3','--incoming-response',
            'artifacts/muon_attached_reached_action_20261011/incoming_run_1','--outgoing-response',
            'artifacts/muon_attached_reached_action_20261011/outgoing_run_1','--output',
            f'artifacts/muon_attached_native_photon_return_20261011/run_{run}','--precision-bits','192']
        rows.append(execution_record(argv,f'muon_attached_native_photon_return_run_{run}',1 if run==1 else 0,
            'run1 rejected the weak-form archive absent from the direct read-list; identical hashed producer receipt subsequently verified its transitive ownership. Runs2/3 exact finite inverse/return; not full disjoint R_ind or anomaly error'))
    test_files=['test_muon_trace_enriched_reached_action.py','test_muon_primal_native_phase_adjoint.py',
        'test_muon_native_adjoint_arithmetic.py','test_muon_causal_source_photon_action.py',
        'test_muon_attached_source_mean_load.py','test_muon_attached_native_source_pair.py']
    rows.append(execution_record([py,'-m','pytest','--noconftest','-q']+['tests/'+name for name in test_files],
        'muon_chronological_native_consumed_tests',0,'23 focused tests; action pairing/constraint checks and exact arithmetic; no physical anomaly enclosure'))
    for run in (1,2):
        rows.append(execution_record([py,'scripts/evaluate_muon_electromagnetic_native_phase_adjoint.py','--mean-directory','artifacts/muon_electromagnetic_source_mean_load_20261011/run_1','--output',f'artifacts/muon_electromagnetic_native_phase_adjoint_20261011/run_{run}'],f'muon_electromagnetic_native_phase_adjoint_run_{run}',0,'exact same-background per-arm native target mean adjoint; no full-domain or Pauli promotion'))
        rows.append(execution_record([py,'scripts/certify_muon_electromagnetic_native_phase_adjoint.py','--application-directory','artifacts/muon_electromagnetic_native_phase_adjoint_20261011/run_1','--output',f'artifacts/muon_electromagnetic_native_phase_adjoint_20261011/certificate_run_{run}','--precision-bits','192'],f'muon_electromagnetic_native_phase_adjoint_certificate_run_{run}',0,'exact stored arithmetic only'))
        rows.append(execution_record([py,'scripts/evaluate_muon_paired_local_vp_pauli.py','--output',f'artifacts/muon_paired_local_vp_pauli_20261011/run_{run}'],f'muon_paired_local_vp_pauli_run_{run}',0,'certified exact central decimal continuum integral/endtails; measurement and native matching excluded'))
    for run in (1,2,3):
        rows.append(execution_record([py,'scripts/evaluate_muon_electromagnetic_native_photon_return.py','--pair-directory','artifacts/muon_electromagnetic_native_source_pair_20261011/run_1','--incoming-response','artifacts/muon_primal_electromagnetic_source_20261011/incoming_run_1','--outgoing-response','artifacts/muon_primal_electromagnetic_source_20261011/outgoing_run_1','--output',f'artifacts/muon_electromagnetic_native_photon_return_20261011/run_{run}','--precision-bits','192'],f'muon_electromagnetic_native_photon_return_run_{run}',1 if run==1 else 0,'run1 failed absent coordinate_time_interval metadata; verified source arrays subsequently supplied actual clock. Runs2/3 exact finite inverse, not bilocal quantum propagator'))
    for run in (1,2,3,4):
        rows.append(execution_record([py,'scripts/evaluate_muon_paired_local_vp_soft_readout.py','--application','artifacts/muon_paired_local_vp_pauli_20261011/run_1','--output',f'artifacts/muon_paired_local_vp_soft_readout_20261011/run_{run}'],f'muon_paired_local_vp_soft_readout_run_{run}',1 if run<3 else 0,'run1 failed mass-key lookup; run2 failed scalar complex JSON export after array output. Runs3/4 use actual on-shell tensor/LSZ target; certified continuum scalar+soft bound, not full BHSM LSZ'))
    for side,runs in (('incoming',(4,5)),('outgoing',(1,2))):
        for run in runs:
            rows.append(execution_record([py,'scripts/evaluate_muon_magnetic_source_action.py','--response',f'artifacts/muon_electromagnetic_soft_magnetic_source_20261011/{side}_run_1','--output',f'artifacts/muon_magnetic_source_action_20261011/{side}_run_{run}'],f'muon_magnetic_source_action_{side}_run_{run}',0,'unhalved path-action Hessian on actual ramp/inherited plateau; three exact active axes; not quantum photon covariance'))
    for stem,test in (('muon_electromagnetic_source_photon_action','test_muon_electromagnetic_source_photon_action.py'),('muon_paired_local_vp_pauli','test_muon_paired_local_vp_pauli.py'),('muon_magnetic_source_photon_action','test_muon_magnetic_source_photon_action.py')):
        rows.append(execution_record([py,'-m','pytest','--noconftest','-q','tests/'+test],stem+'_tests',0,'focused action normalization/constraint or certified continuum/soft bound checks; no final anomaly enclosure'))
    for run in (1,2):
        rows.append(execution_record([py,'scripts/evaluate_muon_magnetic_native_phase_adjoint.py','--mean-directory','artifacts/muon_magnetic_source_mean_load_20261011/run_3','--output',f'artifacts/muon_magnetic_native_phase_adjoint_20261011/run_{run}'],f'muon_magnetic_native_phase_adjoint_run_{run}',0,'complete represented mean target with per-arm initial second mean held; first-source canonical birth transfer does not imply second mean/event transfer'))
        rows.append(execution_record([py,'scripts/certify_muon_magnetic_native_phase_adjoint.py','--application-directory','artifacts/muon_magnetic_native_phase_adjoint_20261011/run_1','--output',f'artifacts/muon_magnetic_native_phase_adjoint_20261011/certificate_run_{run}','--precision-bits','192'],f'muon_magnetic_native_phase_adjoint_certificate_run_{run}',0,'outward exact stored all64 mean contractions including three active axes; no source formation/physical Pauli bound'))
    return rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',action='store_true');p.add_argument('--audits',action='store_true')
    a=p.parse_args();FOLDER.mkdir(exist_ok=True)
    publication.FOLDER=FOLDER;publication.MANIFEST=FOLDER/'publication_manifest.json';publication.VERIFICATION=FOLDER/'verification.json'
    publication.BASELINE=BASELINE;publication.COMPONENTS=COMPONENTS;publication.PAIRS=PAIRS
    publication.EXTRA_STEMS=EXTRA_STEMS
    # Reuse byte ownership/replay verification, while selecting this report
    # and the new additive producers instead of altering prior receipts.
    original=publication.reviewed_manifest
    # That routine explicitly includes its frozen prior report, verifier and
    # optional evaluator files; they remain unchanged and are hash-checked.
    manifest=original();selected={v['path']:v for v in manifest['files']}
    extra=list(ROOT_SOURCE_FILES)+[Path(__file__).relative_to(ROOT).as_posix(),
        'theory/muon_chronological_native_consumed_20261011.md']
    extra += [p.relative_to(ROOT).as_posix() for p in (ROOT/'artifacts').glob('muon_*native_phase_adjoint*.txt')]
    extra += [p.relative_to(ROOT).as_posix() for p in (ROOT/'artifacts').glob('muon_attached_native_photon_return_run_*.txt')]
    extra += [p.relative_to(ROOT).as_posix() for p in (ROOT/'artifacts').glob('muon_*reached_*run_*.txt') if 'trace_enriched' in p.name or 'attached' in p.name]
    extra += [p.relative_to(ROOT).as_posix() for p in (ROOT/'artifacts').glob('muon_chronological_native_consumed_tests.*.txt')]
    for prefix in ('muon_electromagnetic_native_photon_return','muon_electromagnetic_source_photon_action_tests','muon_paired_local_vp','muon_magnetic_source_action','muon_magnetic_source_photon_action_tests'):
        extra += [p.relative_to(ROOT).as_posix() for p in (ROOT/'artifacts').glob(prefix+'*.txt')]
    known=set(publication.git('ls-tree','-r','--name-only',BASELINE).decode().splitlines())
    for name in extra:
        entry=publication.identity(ROOT/name);entry['exists_at_baseline']=name in known;selected[name]=entry
    manifest['files']=[selected[name] for name in sorted(selected)];manifest['classification']='EXPLICIT_CHRONOLOGICAL_CONSUMED_ACTION_APPLICATIONS'
    publication.MANIFEST.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    pairs=publication.verify_pairs()
    record=dict(classification='VERIFIED_CHRONOLOGICAL_NATIVE_CONSUMER_APPLICATIONS',baseline=BASELINE,
        publication_manifest=publication.identity(publication.MANIFEST),component_receipts=[publication.identity(ROOT/name) for name in COMPONENTS],
        executed_root_commands=root_executions(),independent_byte_replays=pairs,
        runtime=dict(executable=sys.executable,python=sys.version,packages={name:version(name) for name in ('numpy','scipy','pytest','python-flint')}),
        scientific_classification=dict(DERIVED='same signed chronological action, actual source weak form, contact and both heat orders, stable photon inverse identity',
            EVALUATED='normalized continuum paired local VP Pauli overlap and signed soft target; causal common-birth three-axis magnetic action; complete raw268 induced mean, full358 adjoint with named reactions, graded direct plus mean source pair, nonzero family-dependent local moment, both coupled source actions and photon returns',
            CONTROL_ONLY='finite normalized tent/constant angular heat trace and compact pulse, probe cutoff values, assigned nu-squared4/gamma-null action',
            UNEVALUATED='same-domain positive quantum field propagator inside the mixed open-lepton Pauli loop, induced second-mean birth transfer; physical disjoint native three-point Pauli contraction, matched local overlap, full-domain relative completion, owned cutoff if consumed, continuum/soft errors and final a_mu/g_mu',
            OWNER_DEFINITION_GAP='none established'),
        complete_observable=False,complete_a_mu=None,complete_g_mu=None,complete_anomaly_uncertainty=None,
        physical_photon_soft_momentum_identified_with_compact_pulse=False,
        finite_heat_norm_used_as_anomaly_bound=False,continued_production_required=True)
    code=0
    if a.stage:
        # The explicit scientific path list can exceed Windows' command
        # line limit. Batch only the already-reviewed add paths; preserve
        # the original stage routine's per-file exact-byte checks.
        original_git=publication.git
        def bounded_git(*args):
            if len(args)>2 and args[:2]==('add','--'):
                batch=[];size=0
                for name in args[2:]:
                    if batch and size+len(name)+3>10000:
                        original_git('add','--',*batch);batch=[];size=0
                    batch.append(name);size+=len(name)+3
                return original_git('add','--',*batch) if batch else b''
            return original_git(*args)
        publication.git=bounded_git
        publication.stage(manifest)
    if a.audits:
        from concurrent.futures import ThreadPoolExecutor
        commands=dict(status=['tools/audit_bhsm_status.py','--format','json'],claims=['tools/audit_forbidden_claims.py','--format','json'],
            frozen=['tools/audit_frozen_prediction_integrity.py','--format','json'],precision=['tools/verify_precision.py'],public=['tools/audit_public_readiness.py','--format','json'])
        with ThreadPoolExecutor(max_workers=5) as pool:outputs=list(pool.map(publication.execute,([sys.executable]+v for v in commands.values())))
        record['publication_audits']=dict(zip(commands,outputs));code=max(v['exit_code'] for v in outputs)
    publication.VERIFICATION.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    if a.stage:
        publication.git('add','--',publication.VERIFICATION.relative_to(ROOT).as_posix())
        if sha256(publication.git('show',':'+publication.VERIFICATION.relative_to(ROOT).as_posix())).hexdigest()!=publication.identity(publication.VERIFICATION)['sha256']:
            raise ValueError('staged verification bytes changed')
    print(json.dumps(dict(files=len(manifest['files']),verification=publication.identity(publication.VERIFICATION),
        audit_exit_codes={k:v['exit_code'] for k,v in record.get('publication_audits',{}).items()}),sort_keys=True))
    return code


if __name__=='__main__':raise SystemExit(main())

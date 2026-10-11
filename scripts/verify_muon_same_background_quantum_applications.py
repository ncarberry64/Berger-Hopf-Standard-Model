"""Verify reviewed same-background applications, replays and publication bytes."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify_muon_primal_native_action_applications as publication

BASELINE='d80d77273102b7728e4d6f967dd652f80b79ad3b'
FOLDER=ROOT/'artifacts/muon_same_background_quantum_applications_20261011'
COMPONENTS=(
 'artifacts/muon_intrinsic_higgs_positive_green_20261011/publication_manifest.json',
 'artifacts/muon_intrinsic_higgs_positive_source_20261011/publication_manifest.json',
 'artifacts/muon_magnetic_chronological_mean_response_20261011/publication_manifest.json',
)
PAIRS=(
 ('muon_intrinsic_higgs_positive_green_20261011','run_1','run_2'),
 ('muon_intrinsic_higgs_positive_source_20261011','run_1','run_2'),
 ('muon_magnetic_true_birth_mean_load_20261011','run_1','run_2'),
 ('muon_magnetic_birth_mean_rows_20261011','run_1','run_2'),
 ('muon_magnetic_birth_ward_mean_20261011','run_1','run_2'),
 ('muon_magnetic_chronological_mean_response_20261011','run_1','run_2'),
 ('muon_magnetic_chronological_heat_contact_20261011','run_1','run_2'),
 ('muon_magnetic_cutoff_mean_contact_20261011','run_1','run_2'),
 ('muon_magnetic_mixed_green_20261011','run_3','run_4'),
 ('muon_paired_vp_magnetic_moment_20261011','run_2','run_3'),
 ('muon_chronological_native_return_20261011','run_3','run_4'),
)
EXTRA=(
 'src/bhsm/interface/muon_common_cutoff_green_kernel.py',
 'tests/test_muon_common_cutoff_green_kernel.py',
 'src/bhsm/interface/muon_chronological_native_return.py',
 'tests/test_muon_chronological_native_return.py',
 'scripts/evaluate_muon_chronological_native_return.py',
 'scripts/evaluate_muon_paired_vp_magnetic_moment.py',
 'theory/muon_same_background_quantum_applications_20261011.md',
)
LOG_PREFIXES=('muon_common_cutoff_green_kernel_tests',
 'muon_chronological_native_return_tests','muon_chronological_native_return_run_',
 'muon_paired_vp_magnetic_moment_run_','muon_paired_vp_magnetic_moment_independent')


def manifest(components):
    files={};pending=[];processed=set()
    def add(name,digest=None):
        path=ROOT/name
        if not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('reviewed dependency outside repository')
        actual=publication.identity(path)
        if digest is not None and actual['sha256']!=digest:raise ValueError('consumed bytes changed: '+name)
        if name not in files:
            files[name]=actual
            if path.suffix=='.json':pending.append(name)
    def dependencies(value):
        if isinstance(value,dict):
            if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):
                if value['path'].startswith(('src/','tests/','scripts/','theory/','artifacts/')):
                    add(value['path'],value['sha256'])
            for key,item in value.items():
                if key in ('input_hashes','source_hashes') and isinstance(item,dict):
                    for name,digest in item.items():add(name,digest)
                elif key in ('files','manifests') and isinstance(item,dict):
                    for name,record in item.items():
                        if isinstance(record,dict) and 'sha256' in record:add(name,record['sha256'])
                    dependencies(item)
                else:dependencies(item)
        elif isinstance(value,list):
            for item in value:dependencies(item)
    for name in components+EXTRA+(Path(__file__).relative_to(ROOT).as_posix(),):add(name)
    for folder,a,b in PAIRS:
        for arm in (a,b):
            for path in sorted((ROOT/'artifacts'/folder/arm).iterdir()):
                if path.is_file():add(path.relative_to(ROOT).as_posix())
    for prefix in LOG_PREFIXES:
        for path in sorted((ROOT/'artifacts').glob(prefix+'*.txt')):add(path.relative_to(ROOT).as_posix())
    while pending:
        name=pending.pop()
        if name not in processed:
            processed.add(name);dependencies(json.loads((ROOT/name).read_bytes()))
    known=set(publication.git('ls-tree','-r','--name-only',BASELINE).decode().splitlines())
    for name,value in files.items():value['exists_at_baseline']=name in known
    return dict(classification='REVIEWED_IMMUTABLE_SAME_BACKGROUND_QUANTUM_ACTION_APPLICATIONS',
        baseline=BASELINE,files=[files[k] for k in sorted(files)],retained_scratch_not_selected=True,
        complete_observable=False)


def root_commands():
    records=[];py='C:\\Python314\\python.exe'
    def add(argv,stem,code,scope,**extra):
        logs={kind:ROOT/f'artifacts/{stem}.{kind}.txt' for kind in ('stdout','stderr')}
        records.append(dict(argv=argv,cwd=str(ROOT),exit_code=code,
            environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),
            logs={kind:dict(**publication.identity(p),text=p.read_text(encoding='utf8',errors='replace')) for kind,p in logs.items()},
            error_scope=scope,**extra))
    for stem,count in (('muon_common_cutoff_green_kernel',4),('muon_chronological_native_return',2)):
        add([py,'-m','pytest','--noconftest',f'tests/test_{stem}.py','-q'],stem+'_tests',0,
            str(count)+' passed; kernel/interval source inclusion checks, not a physical anomaly enclosure')
    for run in (1,2,3):
        add([py,'scripts/evaluate_muon_paired_vp_magnetic_moment.py','--output',
            f'artifacts/muon_paired_vp_magnetic_moment_20261011/run_{run}'],
            f'muon_paired_vp_magnetic_moment_run_{run}',1 if run==1 else 0,
            'initial key mismatch retained' if run==1 else 'outward continuum local graph/SI normalization on shared selected input box')
    for run in (1,2,3,4):
        add([py,'scripts/evaluate_muon_chronological_native_return.py','--output',
            f'artifacts/muon_chronological_native_return_20261011/run_{run}','--precision-bits','192'],
            f'muon_chronological_native_return_run_{run}',1 if run<3 else 0,
            'exact zero outward padding guard retained' if run<3 else 'exact stored signed source action and chronological mean inclusion; no quantum photon/Pauli promotion')
    add([py,'-'],'muon_paired_vp_magnetic_moment_independent',0,
        'independent binary SI/GeV unit conversion contains in the Arb component interval; not a full observable bound',
        stdin_application='Primary optical ratio, recoil alpha and R_infinity give m_mu_GeV=2*h*c*R_infinity*r*alpha_inverse^2/(e*1e9); magnetic_moment_accounting(a_mu=0,charge_sign=-1).da_to_dmoment times the midpoint local VP a component is compared with its outward J/T interval.')
    return records


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--component',action='append',default=[])
    p.add_argument('--stage',action='store_true');p.add_argument('--audits',action='store_true');args=p.parse_args()
    components=COMPONENTS+tuple(args.component);FOLDER.mkdir(exist_ok=True)
    publication.FOLDER=FOLDER;publication.MANIFEST=FOLDER/'publication_manifest.json'
    publication.VERIFICATION=FOLDER/'verification.json';publication.PAIRS=PAIRS
    reviewed=manifest(components);pairs=publication.verify_pairs()
    publication.MANIFEST.write_text(json.dumps(reviewed,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    record=dict(classification='VERIFIED_REVIEWED_SAME_BACKGROUND_QUANTUM_APPLICATIONS',baseline=BASELINE,
        invocation=[sys.executable,*sys.argv],publication_manifest=publication.identity(publication.MANIFEST),
        component_receipts=[publication.identity(ROOT/name) for name in components],
        root_executions=root_commands(),independent_byte_replays=pairs,
        runtime=dict(executable=sys.executable,python=sys.version,
            packages={name:version(name) for name in ('numpy','scipy','pytest','python-flint')}),
        scientific_classification=dict(
            DERIVED='same-background nonnormal Green derivative and both factor placements; common-total-cutoff scalar identities and outward stored-spectrum series tails; named Ward relations; canonical true-birth mean and signed SI normalization',
            EVALUATED='actual positive scalar images and all-family mixed magnetic insertions, true-birth original-row compatible and propagated mean with DΓ contact/cutoff partial, signed interval photon boundary response, continuum local overlap signed SI component and primary box',
            CONTROL_ONLY='finite reference cells and explicit common cutoff probes; assigned nu-squared4/gamma-null trial; stored-array arithmetic certificates',
            UNEVALUATED='complete same-background graded quantum open-leg action and complement/domain/pole matching; physical formation/cutoff if consumed; disjoint native soft Pauli remainder, remaining matched finite weak terms and total uncertainty',
            OWNER_DEFINITION_GAP='none established'),
        complete_a_mu=None,complete_g_mu=None,complete_anomaly_uncertainty=None,
        continued_action_production_required=True,complete_observable=False,
        finite_response_norm_used_as_anomaly_enclosure=False,
        frozen_local_result_or_prior_milestone_bytes_changed=False)
    if args.stage:
        original=publication.git
        def bounded_git(*argv):
            if argv[:2]==('add','--'):
                batch=[];size=0
                for name in argv[2:]:
                    if batch and size+len(name)+3>10000:original('add','--',*batch);batch=[];size=0
                    batch.append(name);size+=len(name)+3
                return original('add','--',*batch) if batch else b''
            return original(*argv)
        publication.git=bounded_git;publication.stage(reviewed)
    code=0
    if args.audits:
        commands=dict(status=['tools/audit_bhsm_status.py','--format','json'],claims=['tools/audit_forbidden_claims.py','--format','json'],
            frozen=['tools/audit_frozen_prediction_integrity.py','--format','json'],precision=['tools/verify_precision.py'],
            public=['tools/audit_public_readiness.py','--format','json'])
        with ThreadPoolExecutor(max_workers=5) as pool:outputs=list(pool.map(publication.execute,([sys.executable]+v for v in commands.values())))
        record['publication_audits']=dict(zip(commands,outputs));code=max(r['exit_code'] for r in outputs)
    publication.VERIFICATION.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    if args.stage:
        publication.git('add','--',publication.VERIFICATION.relative_to(ROOT).as_posix())
        if sha256(publication.git('show',':'+publication.VERIFICATION.relative_to(ROOT).as_posix())).hexdigest()!=publication.identity(publication.VERIFICATION)['sha256']:
            raise ValueError('staged verification bytes changed')
    print(json.dumps(dict(files=len(reviewed['files']),verification=publication.identity(publication.VERIFICATION),
        audit_exit_codes={k:v['exit_code'] for k,v in record.get('publication_audits',{}).items()}),sort_keys=True))
    return code


if __name__=='__main__':raise SystemExit(main())

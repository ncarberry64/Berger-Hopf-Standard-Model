"""Verify immutable consumed magnetic applications and publication bytes."""
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

BASELINE='50b13755cfbea4efc0ed1afd68ef5d358ace4641'
FOLDER=ROOT/'artifacts/muon_magnetic_open_native_application_20261011'
COMPONENTS=(
 'artifacts/muon_magnetic_native_source_pair_20261011/downstream_publication_manifest.json',
 'artifacts/muon_magnetic_open_lepton_vertex_20261011/publication_manifest.json',
 'artifacts/muon_magnetic_true_birth_fields_20261011/publication_manifest.json',
 'artifacts/muon_chronological_canonical_graph_20261011/publication_verification.json',
)
PAIRS=(
 ('muon_magnetic_native_source_heat_20261011','run_1','run_2'),
 ('muon_magnetic_native_source_pair_20261011','run_1','run_2'),
 ('muon_magnetic_birth_mean_load_20261011','run_1','run_2'),
 ('muon_magnetic_retarded_operators_20261011','run_1','run_2'),
 ('muon_magnetic_open_lepton_vertex_20261011','run_1','run_2'),
 ('muon_magnetic_true_birth_fields_20261011','run_1','run_2'),
 ('muon_magnetic_native_photon_return_20261011','run_1','run_2'),
 ('muon_paired_vp_input_uncertainty_20261011','run_1','run_2'),
)
EXTRA=(
 'src/bhsm/interface/muon_magnetic_native_return_enclosure.py',
 'tests/test_muon_magnetic_native_return_enclosure.py',
 'scripts/evaluate_muon_magnetic_native_photon_return.py',
 'scripts/evaluate_muon_paired_vp_input_uncertainty.py',
 'theory/muon_magnetic_open_native_application_20261011.md',
)


def manifest():
    selected={};pending=[];processed=set()
    def add(name,digest=None):
        path=ROOT/name
        if not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('publication dependency outside repository')
        record=publication.identity(path)
        if digest is not None and digest!=record['sha256']:
            raise ValueError('immutable consumed bytes changed: '+name)
        if name not in selected:
            selected[name]=record
            if path.suffix=='.json':pending.append(name)
    def dependencies(value):
        if isinstance(value,dict):
            if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):
                name=value['path']
                if name.startswith(('src/','tests/','scripts/','theory/','artifacts/')):
                    add(name,value['sha256'])
            for key,item in value.items():
                if key=='input_hashes' and isinstance(item,dict):
                    for name,digest in item.items():add(name,digest)
                elif key in ('files','manifests') and isinstance(item,dict):
                    for name,record in item.items():
                        if isinstance(record,dict) and 'sha256' in record:
                            add(name,record['sha256'])
                    dependencies(item)
                else:dependencies(item)
        elif isinstance(value,list):
            for item in value:dependencies(item)
    for name in COMPONENTS+EXTRA:add(name)
    add(Path(__file__).relative_to(ROOT).as_posix())
    for folder,a,b in PAIRS:
        for arm in (a,b):
            for path in sorted((ROOT/'artifacts'/folder/arm).iterdir()):
                if path.is_file():add(path.relative_to(ROOT).as_posix())
    for prefix in ('muon_magnetic_native_photon_return_run_',
                   'muon_magnetic_native_return_enclosure_tests',
                   'muon_paired_vp_input_uncertainty_run_'):
        for path in sorted((ROOT/'artifacts').glob(prefix+'*.txt')):
            add(path.relative_to(ROOT).as_posix())
    while pending:
        name=pending.pop()
        if name in processed:continue
        processed.add(name);dependencies(json.loads((ROOT/name).read_bytes()))
    known=set(publication.git('ls-tree','-r','--name-only',BASELINE).decode().splitlines())
    for name,record in selected.items():record['exists_at_baseline']=name in known
    return dict(classification='EXPLICIT_IMMUTABLE_MAGNETIC_OPEN_ACTION_APPLICATIONS',
        baseline=BASELINE,files=[selected[k] for k in sorted(selected)],
        retained_scratch_not_selected=True,complete_observable=False)


def root_commands():
    result=[];py='C:\\Python314\\python.exe'
    def record(argv,stem,scope):
        logs={kind:ROOT/f'artifacts/{stem}.{kind}.txt' for kind in ('stdout','stderr')}
        result.append(dict(argv=argv,cwd=str(ROOT),exit_code=0,
            environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),
            logs={kind:dict(**publication.identity(path),text=path.read_text(encoding='utf8',errors='replace'))
                  for kind,path in logs.items()},error_scope=scope))
    record([py,'-m','pytest','--noconftest','-q','tests/test_muon_magnetic_native_return_enclosure.py'],
        'muon_magnetic_native_return_enclosure_tests',
        '2 passed; interval mean reaches signed active-three inverse and absent axes are rejected; no quantum/Pauli bound')
    for run in (1,2):
        record([py,'scripts/evaluate_muon_magnetic_native_photon_return.py','--pair-directory',
            'artifacts/muon_magnetic_native_source_pair_20261011/run_1','--incoming-response',
            'artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',
            '--outgoing-response','artifacts/muon_electromagnetic_soft_magnetic_source_20261011/outgoing_run_1',
            '--output',f'artifacts/muon_magnetic_native_photon_return_20261011/run_{run}',
            '--precision-bits','192'],f'muon_magnetic_native_photon_return_run_{run}',
            'outward stored bare plus certified real mean/stored direct entry arithmetic; response/heat/continuum/matching errors remain separate')
        record([py,'scripts/evaluate_muon_paired_vp_input_uncertainty.py','--output',
            f'artifacts/muon_paired_vp_input_uncertainty_20261011/run_{run}'],
            f'muon_paired_vp_input_uncertainty_run_{run}',
            'actual continuum extrema on specified primary +/-1sigma box; not a confidence region or final native uncertainty')
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');parser.add_argument('--audits',action='store_true')
    args=parser.parse_args();FOLDER.mkdir(exist_ok=True)
    publication.FOLDER=FOLDER;publication.MANIFEST=FOLDER/'publication_manifest.json'
    publication.VERIFICATION=FOLDER/'verification.json';publication.PAIRS=PAIRS
    reviewed=manifest();pairs=publication.verify_pairs()
    publication.MANIFEST.write_text(json.dumps(reviewed,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    record=dict(classification='VERIFIED_MAGNETIC_OPEN_NATIVE_CONSUMED_APPLICATIONS',
        baseline=BASELINE,publication_manifest=publication.identity(publication.MANIFEST),
        component_receipts=[publication.identity(ROOT/name) for name in COMPONENTS],
        root_executions=root_commands(),independent_byte_replays=pairs,
        runtime=dict(executable=sys.executable,python=sys.version,
            packages={name:version(name) for name in ('numpy','scipy','pytest','python-flint')}),
        scientific_classification=dict(
            DERIVED='same-action source contact/both insertions; canonical open-field vertices and birth Legendre/Gauss; signed interval return; VP measurement-box monotonicity',
            EVALUATED='direct/mean magnetic graded form, interval boundary return, open18 vertices and neutral leakage, true-birth fields, chronological field/lepton propagator applications, canonical x/Pi graph; continuum local VP measurement box',
            CONTROL_ONLY='finite cells and probe cutoff; nu-squared4/gamma-null trial action; matched free rest-symbol spin normalization',
            UNEVALUATED='complete same-background positive BRST/HS mixed quantum contraction, second-mean birth/event composition, matched disjoint native soft vertex and total a_mu/g_mu uncertainty',
            OWNER_DEFINITION_GAP='none established'),
        complete_a_mu=None,complete_g_mu=None,complete_anomaly_uncertainty=None,
        continued_production_required=True,complete_observable=False,
        no_retarded_or_source_inverse_promoted_to_quantum_Green=True,
        finite_response_norm_used_as_anomaly_bound=False)
    if args.stage:
        original=publication.git
        def bounded_git(*argv):
            if argv[:2]==('add','--'):
                batch=[];size=0
                for name in argv[2:]:
                    if batch and size+len(name)+3>10000:
                        original('add','--',*batch);batch=[];size=0
                    batch.append(name);size+=len(name)+3
                return original('add','--',*batch) if batch else b''
            return original(*argv)
        publication.git=bounded_git;publication.stage(reviewed)
    code=0
    if args.audits:
        commands=dict(status=['tools/audit_bhsm_status.py','--format','json'],
            claims=['tools/audit_forbidden_claims.py','--format','json'],
            frozen=['tools/audit_frozen_prediction_integrity.py','--format','json'],
            precision=['tools/verify_precision.py'],public=['tools/audit_public_readiness.py','--format','json'])
        with ThreadPoolExecutor(max_workers=5) as pool:
            outputs=list(pool.map(publication.execute,([sys.executable]+v for v in commands.values())))
        record['publication_audits']=dict(zip(commands,outputs));code=max(v['exit_code'] for v in outputs)
    publication.VERIFICATION.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    if args.stage:
        publication.git('add','--',publication.VERIFICATION.relative_to(ROOT).as_posix())
        if sha256(publication.git('show',':'+publication.VERIFICATION.relative_to(ROOT).as_posix())).hexdigest()!=publication.identity(publication.VERIFICATION)['sha256']:
            raise ValueError('staged verification bytes changed')
    print(json.dumps(dict(files=len(reviewed['files']),verification=publication.identity(publication.VERIFICATION),
        audit_exit_codes={k:v['exit_code'] for k,v in record.get('publication_audits',{}).items()}),sort_keys=True))
    return code


if __name__=='__main__':raise SystemExit(main())

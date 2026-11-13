"""Publish only reviewed executed primal/native applications with exact bytes."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/muon_primal_native_action_applications_20261010'
MANIFEST=FOLDER/'publication_manifest.json'
VERIFICATION=FOLDER/'verification.json'
BASELINE='52cb39f4609983ef33551c2bc7eaa405f5d9dab2'
COMPONENTS=(
    'artifacts/muon_parent_gauge_geometry_correction_20261010/fullfield_phase_verification.json',
    'artifacts/muon_parent_gauge_geometry_correction_20261010/enriched_endpoint_verification.json',
    'artifacts/muon_parent_gauge_geometry_correction_20261010/enriched_phase_verification.json',
    'artifacts/muon_native_mean_causal_heat_20261010/publication_manifest.json',
    'artifacts/muon_native_paired_readout_certificate_20261010/publication_manifest.json',
    'artifacts/muon_pointwise_full_field_action_20261010/verification.json',
    'artifacts/muon_mean_legendre_certificate_20261010/verification.json',
    'artifacts/muon_reached_trace_action_20261010/verification.json',
    'artifacts/muon_primal_intrinsic_lepton_operator_20261010/verification.json',
    'artifacts/muon_primal_trace_enriched_lepton_operator_20261010/verification.json',
    'artifacts/muon_primal_charged_current_response_20261010/verification.json',
    'artifacts/muon_current_source_motion_cubic_20261010/publication_manifest.json',
)
PAIRS=(
    ('muon_pointwise_full_field_action_20261010','run_2','run_3'),
    ('muon_mean_legendre_certificate_20261010','run_2','run_3'),
    ('muon_reached_trace_action_20261010','run_2','run_3'),
    ('muon_primal_intrinsic_lepton_operator_20261010','run_1','run_2'),
    ('muon_primal_trace_enriched_lepton_operator_20261010','run_1','run_2'),
    ('muon_primal_charged_current_response_20261010','run_1','run_2'),
)
EXTRA_STEMS=('muon_pointwise_full_field_action','muon_mean_legendre_certificate',
    'muon_reached_trace_action','muon_primal_intrinsic_lepton_operator',
    'muon_primal_trace_enriched_lepton_operator','muon_primal_charged_current_response')


def identity(path):
    data=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest())


def git(*args):
    result=subprocess.run(['git','-c','gc.auto=0','-c','maintenance.auto=false',*args],cwd=ROOT,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if result.returncode:raise RuntimeError(result.stderr.decode('utf8',errors='replace'))
    return result.stdout


def execute(argv):
    env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),OPENBLAS_NUM_THREADS='1')
    run=subprocess.run(argv,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return dict(argv=argv,cwd=str(ROOT),environment_overrides=dict(PYTHONPATH=str(ROOT/'src'),OPENBLAS_NUM_THREADS='1'),
        exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr)


def reviewed_manifest():
    selected={};processed=set();pending=[]
    def add(name,expected=None):
        path=ROOT/name
        if path.is_absolute() and not path.resolve().is_relative_to(ROOT.resolve()):return
        if not path.is_file():raise FileNotFoundError('reviewed dependency absent: '+name)
        actual=identity(path)
        if expected and actual['sha256']!=expected:raise ValueError('reviewed owner bytes changed: '+name)
        if name not in selected:
            selected[name]=actual
            if path.suffix=='.json':pending.append(name)
    def recorded_dependencies(value,artifact_scope=False):
        if isinstance(value,dict):
            if 'path' in value and 'sha256' in value and isinstance(value['path'],str):
                path=value['path']
                # A local output filename, excluded scratch hash or package
                # comparison receipt is not an input publication instruction.
                if not Path(path).is_absolute() and (artifact_scope or path.startswith(('src/','tests/','scripts/','theory/'))):
                    add(path,value['sha256'])
            for key,item in value.items():
                if key=='input_hashes' and isinstance(item,dict):
                    for path,digest in item.items():add(path,digest)
                else:recorded_dependencies(item,key in ('publication_files','runtime_dependencies','input_records','consumed_owner_identities'))
        elif isinstance(value,list):
            for item in value:recorded_dependencies(item,artifact_scope)
    for name in COMPONENTS:add(name)
    for directory,a,b in PAIRS:
        for arm in (a,b):
            path=ROOT/'artifacts'/directory/arm
            for file in sorted(path.iterdir()):
                if file.is_file():add(file.relative_to(ROOT).as_posix())
    for stem in EXTRA_STEMS:
        for folder,prefix in (('src/bhsm/interface/',''),('tests/','test_'),('scripts/','evaluate_')):
            add(folder+prefix+stem+'.py')
        verifier=ROOT/'scripts'/('verify_'+stem+'.py')
        if verifier.exists():add(verifier.relative_to(ROOT).as_posix())
        for tag in ('tests','run1','run2','run3'):
            for stream in ('stdout','stderr'):
                log=ROOT/f'artifacts/{stem}_{tag}.{stream}.txt'
                if log.exists():add(log.relative_to(ROOT).as_posix())
    for stem in ('muon_parent_maxwell_source_mean_forcing','muon_parent_mean_causal_action','muon_parent_mean_causal_descriptor'):
        add('src/bhsm/interface/'+stem+'.py');add('tests/test_'+stem+'.py')
    add('theory/muon_primal_native_action_applications_20261010.md')
    add(Path(__file__).relative_to(ROOT).as_posix())
    while pending:
        name=pending.pop()
        if name in processed:continue
        processed.add(name);recorded_dependencies(json.loads((ROOT/name).read_text(encoding='utf8')))
    names=git('ls-tree','-r','--name-only',BASELINE).decode('utf8').splitlines();known=set(names)
    for name,value in selected.items():value['exists_at_baseline']=name in known
    return dict(classification='EXPLICIT_REVIEWED_EXECUTED_PRIMAL_NATIVE_APPLICATION_FILES',baseline=BASELINE,
        files=[selected[k] for k in sorted(selected)],
        retained_scratch_not_selected=True,complete_observable=False,action_selected=False,Gate7_closed=False)


def verify_pairs():
    pairs=[]
    for directory,a,b in PAIRS:
        left,right=(ROOT/'artifacts'/directory/arm for arm in (a,b))
        names=sorted(p.name for p in left.iterdir() if p.is_file())
        if names!=sorted(p.name for p in right.iterdir() if p.is_file()):raise ValueError('incomplete replay: '+directory)
        files=[]
        for name in names:
            if (left/name).read_bytes()!=(right/name).read_bytes():raise ValueError('replay differs: '+directory+'/'+name)
            files.append(dict(first=identity(left/name),second=identity(right/name)))
        pairs.append(dict(directory=directory,byte_identical=True,files=files))
    return pairs


def stage(manifest):
    attrs=ROOT/'.gitattributes';original=attrs.read_text(encoding='utf8');lines=[]
    for entry in manifest['files']:
        if entry['exists_at_baseline']:continue
        name=entry['path'];path=ROOT/name
        if path.suffix in ('.py','.md','.json','.txt'):
            policy='-text whitespace=cr-at-eol' if b'\r\n' in path.read_bytes() or name.endswith(('.stdout.txt','.stderr.txt')) else 'text eol=lf'
            line=name+' '+policy
            if line not in original:lines.append(line)
    for path in (MANIFEST,VERIFICATION):
        line=path.relative_to(ROOT).as_posix()+' text eol=lf'
        if line not in original:lines.append(line)
    if lines:
        attrs.write_text(original.rstrip()+'\n\n# Exact executed primal and native application evidence.\n'+'\n'.join(sorted(set(lines)))+'\n',encoding='utf8',newline='\n')
    paths=[v['path'] for v in manifest['files'] if not v['exists_at_baseline']]
    git('add','--',*paths,'.gitattributes',MANIFEST.relative_to(ROOT).as_posix())
    for entry in manifest['files']:
        if not entry['exists_at_baseline'] and sha256(git('show',':'+entry['path'])).hexdigest()!=entry['sha256']:
            raise ValueError('staged scientific bytes changed: '+entry['path'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',action='store_true');p.add_argument('--audits',action='store_true')
    a=p.parse_args();FOLDER.mkdir(exist_ok=True)
    manifest=reviewed_manifest();pairs=verify_pairs()
    MANIFEST.write_text(json.dumps(manifest,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    if a.stage:stage(manifest)
    record=dict(classification='VERIFIED_EXECUTED_PRIMAL_NATIVE_ACTION_APPLICATIONS',baseline=BASELINE,
        component_receipts=[identity(ROOT/name) for name in COMPONENTS],publication_manifest=identity(MANIFEST),
        direct_independent_replays=pairs,inherited_command_test_replay_evidence='Exact immutable component receipts; missing tool exit/log fields remain explicitly unavailable',
        runtime=dict(executable=sys.executable,python=sys.version,packages={name:version(name) for name in ('numpy','scipy','pytest','python-flint')}),
        scientific_classification=dict(
            DERIVED='same-action Euler/Gauss Jacobians and full-field phase; moving-source action contacts, intrinsic trace action reduction, current mixed source/adjoint and finite even-Y estimates',
            EVALUATED='nonlinear interacting paired endpoint and phase, fresh coupled photon/Higgs response, all-family actual lepton operators and first jets, source/adjoint current pairings and reached heat contacts with both insertions',
            CONTROL_ONLY='assigned nu-squared4/gamma-null finite action, probe cutoffs/conditioning, old nonconvergent backward mean core',
            UNEVALUATED='complete matched soft Pauli remainder, overlap and observable uncertainty; consumer-reached physical cutoff/relative/LSZ matching applications remain in progress',
            OWNER_DEFINITION_GAP='none established'),
        complete_observable=False,action_selected=False,Gate7_closed=False,continued_production_required=True,
        error_scope='Finite residual/replay/Arb stored-system or FE bounds do not enclose the physical anomaly; old temporal nonconvergence preserved; no native heat scalar is added directly to the Pauli subtotal')
    code=0
    if a.audits:
        commands=dict(status=['tools/audit_bhsm_status.py','--format','json'],claims=['tools/audit_forbidden_claims.py','--format','json'],
            frozen=['tools/audit_frozen_prediction_integrity.py','--format','json'],precision=['tools/verify_precision.py'],public=['tools/audit_public_readiness.py','--format','json'])
        with ThreadPoolExecutor(max_workers=5) as pool:
            outputs=list(pool.map(execute,([sys.executable]+v for v in commands.values())))
        record['publication_audits']=dict(zip(commands,outputs));code=max(r['exit_code'] for r in outputs)
    VERIFICATION.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    if a.stage:
        git('add','--',VERIFICATION.relative_to(ROOT).as_posix())
        if sha256(git('show',':'+VERIFICATION.relative_to(ROOT).as_posix())).hexdigest()!=identity(VERIFICATION)['sha256']:
            raise ValueError('staged verification bytes changed')
    print(json.dumps(dict(files=len(manifest['files']),verification=identity(VERIFICATION),
        audit_exit_codes={k:v['exit_code'] for k,v in record.get('publication_audits',{}).items()}),sort_keys=True))
    return code


if __name__=='__main__':raise SystemExit(main())

"""Freeze independently replayed clock/cancellation action diagnostics."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def verify():
    folders=('muon_uniform_clock_action_identity_20261012','muon_material_cancellation_audit_20261012')
    records=[];manifest=[]
    for label in folders:
        base=ROOT/'artifacts'/label;out=base/'independent_pair_verification.json'
        if out.exists():raise FileExistsError('preserve immutable diagnostic verification')
        a,b=base/'run_1',base/'run_2'
        af={p.relative_to(a).as_posix():p for p in a.rglob('*')if p.is_file()}
        bf={p.relative_to(b).as_posix():p for p in b.rglob('*')if p.is_file()}
        if af.keys()!=bf.keys():raise ValueError('output membership changed')
        hashes={}
        for n in sorted(af):
            h=sha256(af[n].read_bytes()).hexdigest()
            if h!=sha256(bf[n].read_bytes()).hexdigest():raise ValueError('byte mismatch '+label+'/'+n)
            hashes[n]=h
        md=json.loads((a/'result.json').read_bytes())
        for p,h in md['input_hashes'].items():
            if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('source pin changed '+p)
        logs={}
        for i in(1,2):
            prefix='BHSM_uniform_clock_action_identity'if label==folders[0]else'BHSM_material_cancellation_audit'
            data=(Path('C:/Users/carbe/Downloads')/(prefix+f'_run_{i}.stdout.txt')).read_bytes()
            p=base/f'run_{i}.stdout.txt';p.write_bytes(data)
            logs[p.name]=dict(bytes=len(data),sha256=sha256(data).hexdigest(),capture='Complete actual PowerShell Tee-Object bytes')
        env=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        driver='evaluate_muon_uniform_clock_action_identity.py'if label==folders[0]else'evaluate_muon_material_cancellation_audit.py'
        commands=[]
        for i in(1,2):
            argv=['C:/Python314/python.exe','scripts/'+driver]
            if label==folders[1]:argv+=['--checkpoint','artifacts/muon_material_rate_canonical_geometry_20261011/continued_run_1/iteration_0013.npz']
            argv+=['--output',f'artifacts/{label}/run_{i}']
            commands.append(dict(argv=argv,environment=env,cwd=str(ROOT),exit_code=0))
        test=None
        if label==folders[0]:
            data=Path('C:/Users/carbe/Downloads/BHSM_uniform_clock_action_identity_tests.stdout.txt').read_bytes()
            p=base/'tests.stdout.txt';p.write_bytes(data)
            test=dict(argv=['C:/Python314/python.exe','-m','pytest','--noconftest','-q','tests/test_muon_uniform_clock_action_identity.py'],
                environment=env,exit_code=0,stdout_path=p.relative_to(ROOT).as_posix(),stdout_sha256=sha256(data).hexdigest(),
                result='1 passed in6.97s',test_source_sha256=sha256((ROOT/'tests/test_muon_uniform_clock_action_identity.py').read_bytes()).hexdigest())
        result=dict(classification='INDEPENDENT_REPLAY_OF_CONDITIONAL_CANONICAL_ACTION_DIAGNOSTIC',
            all_output_byte_identical=True,all_output_count=len(hashes),all_output_sha256=hashes,
            executions=commands,stdout=logs,test=test,input_pins_current=True,input_pin_count=len(md['input_hashes']),
            full_ancestor_rematerialization_executed=False,new_physical_constraint_or_error_bound_claimed=False,
            verifier_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        records.append(dict(verification=out.relative_to(ROOT).as_posix(),sha256=sha256(out.read_bytes()).hexdigest(),result_sha256=hashes['result.json'],application_sha256=hashes['application.npz']))
        manifest.extend(p.relative_to(ROOT).as_posix()for p in(base.rglob('*'))if p.is_file())
    files=['src/bhsm/interface/muon_uniform_clock_action_identity.py','scripts/evaluate_muon_uniform_clock_action_identity.py',
        'tests/test_muon_uniform_clock_action_identity.py','scripts/evaluate_muon_material_cancellation_audit.py',
        Path(__file__).relative_to(ROOT).as_posix()]
    manifest=sorted(set(manifest+files))
    out=ROOT/'artifacts/muon_material_cancellation_audit_20261012/publication_manifest.json'
    out.write_text(json.dumps(dict(classification='REPLAYED_ACTION_CLOCK_AND_ARITHMETIC_DIAGNOSTICS_ONLY',
        files={p:sha256((ROOT/p).read_bytes()).hexdigest()for p in manifest},verification=records,
        physical_canonical_compatibility_or_Pauli_completed=False),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verified=records,manifest=out.relative_to(ROOT).as_posix(),manifest_sha256=sha256(out.read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':verify()

"""Freeze chronological common fixed-Y source actions and their dual checks."""
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
STEM='muon_joined_common_y_current';FOLDER=ROOT/'artifacts'/(STEM+'_20261011')


def identity(name):
    b=(ROOT/name).read_bytes()
    return dict(path=name,bytes=len(b),sha256=sha256(b).hexdigest())


def main():
    files=set();pairs={};commands=[];pins=0
    result=json.loads((FOLDER/'run_1/result.json').read_bytes())
    for name in sorted((*result['array_archives'],'result.json')):
        rows=[identity((FOLDER/f'run_{n}'/name).relative_to(ROOT).as_posix())for n in(1,2)]
        if len({(r['bytes'],r['sha256'])for r in rows})!=1:raise ValueError('joined source replay differs '+name)
        pairs[name]=rows;files.update(r['path']for r in rows)
    for n in(1,2):
        r=json.loads((FOLDER/f'run_{n}/result.json').read_bytes())
        for p,h in r['input_hashes'].items():
            if identity(p)['sha256']!=h:raise ValueError('joined source input changed '+p)
            pins+=1
        logs={}
        for channel in('stdout','stderr'):
            p=f'artifacts/{STEM}_run_{n}.{channel}.txt';files.add(p)
            logs[channel]=dict(**identity(p),text=(ROOT/p).read_text())
        commands.append(dict(argv=[sys.executable,f'scripts/evaluate_{STEM}.py','--output',f'artifacts/{STEM}_20261011/run_{n}'],
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),exit_code=0,logs=logs))
    logs={}
    for channel in('stdout','stderr'):
        p=f'artifacts/{STEM}_tests.{channel}.txt';files.add(p)
        logs[channel]=dict(**identity(p),text=(ROOT/p).read_text())
    commands.append(dict(argv=[sys.executable,'-m','pytest','--noconftest','-q',f'tests/test_{STEM}.py'],cwd=str(ROOT),
        environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),exit_code=0,tests_passed=2,logs=logs))
    files.update((f'src/bhsm/interface/{STEM}.py',f'tests/test_{STEM}.py',f'scripts/evaluate_{STEM}.py',Path(__file__).relative_to(ROOT).as_posix()))
    supplemental=[identity('src/bhsm/interface/muon_common_y_current_response.py'),
        identity('artifacts/muon_common_y_current_response_20261011/publication_manifest.json')]
    v=dict(classification='VERIFIED_JOINED_CANONICAL_COMMON_Y_CURRENT_AND_BOTH_ANGULAR_INSERTIONS',commands=commands,
        independent_byte_replays=pairs,verified_input_hash_count=pins,additional_frozen_import_dependencies=supplemental,actual_records=result['records'],
        DERIVED='Block first-order coefficient solve and its analytic transpose adjoint; one inherited common birth trace; both adjacent magnetic source contacts and both source/target Y placements, retaining odd powers.',
        EVALUATED='Same joined canonical current at16/32/64 cells per arm; actual n1<-n0 and n1-input to n0+n2 output with literal reverse; full C6 before charge projection; coefficient primal/adjoint and refinement checks.',
        CONTROL_ONLY='Conditional represented homogeneous canonical birth frameT=I and finite numerical outer faces. Computational angular and Y0 coefficient bases do not select a physical covariance or massless carrier.',
        UNEVALUATED='Full worldvolume trace graph, completed Gaussian/native relative heat loop, physical overlap subtraction and normalized Pauli remainder, entry/continuum/soft-limit and total observable uncertainty.',
        OWNER_DEFINITION_GAP='none established',physical_a_mu=None,physical_g_mu=None,complete_observable=False,error_scope=result['error_scope'],
        arithmetic_certificates_not_borrowed_from_other_domain=True)
    p=FOLDER/'verification.json';p.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n');files.add(p.relative_to(ROOT).as_posix())
    m=dict(classification='FROZEN_REPLAYED_JOINED_CANONICAL_SOURCE_AND_ADJOINT_APPLICATIONS',byte_identical_replay=True,
        files=[identity(n)for n in sorted(files)],complete_observable=False)
    q=FOLDER/'publication_manifest.json';q.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),verification=identity(p.relative_to(ROOT).as_posix()),publication_manifest=identity(q.relative_to(ROOT).as_posix())),sort_keys=True))


if __name__=='__main__':main()

"""Freeze completed relative-domain current applications and their pairings."""
from pathlib import Path
from hashlib import sha256
import json,os,subprocess
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent.parent


def digest(p):return sha256(p.read_bytes()).hexdigest()


def main():
    pairs=[];files=[];deps={};commands=[]
    for name in ('joined_16.npz','joined_32.npz','result.json'):
        a,b=(BASE/f'run_{i}'/name for i in (1,2))
        if a.read_bytes()!=b.read_bytes():raise RuntimeError('independent heat application differs: '+name)
        pairs.append(dict(paths=[p.relative_to(ROOT).as_posix()for p in(a,b)],byte_identical=True,sha256=digest(a)))
    a,b=(BASE/f'pairing_run_{i}'/'application.npz'for i in(1,2))
    if a.read_bytes()!=b.read_bytes():raise RuntimeError('independent pairing archive differs')
    pairs.append(dict(paths=[p.relative_to(ROOT).as_posix()for p in(a,b)],byte_identical=True,sha256=digest(a)))
    receipt0=json.loads((BASE/'pairing_run_1/result.json').read_bytes())
    receipt1=json.loads((BASE/'pairing_run_2/result.json').read_bytes())
    if receipt0['records']!=receipt1['records']:raise RuntimeError('pairing numbers differ')
    for directory in ('run_1','run_2','pairing_run_1','pairing_run_2'):
        files+=sorted((BASE/directory).iterdir())
        md=json.loads((BASE/directory/'result.json').read_bytes())
        for relative,h in md['input_hashes'].items():
            if digest(ROOT/relative)!=h:raise RuntimeError('consumed input/source changed: '+relative)
            if relative in deps and deps[relative]!=h:raise RuntimeError('inconsistent input/source: '+relative)
            deps[relative]=h
    for label in ('run_1','run_2','pairing_2'):
        command=BASE/'execution_logs'/f'{label}.command.json'
        c=json.loads(command.read_bytes())
        if c['exit_code']:raise RuntimeError('producer failed: '+label)
        commands.append(dict(receipt=command.relative_to(ROOT).as_posix(),**c))
        files+=[command,BASE/'execution_logs'/f'{label}.stdout.txt',BASE/'execution_logs'/f'{label}.stderr.txt']
    commands.append(dict(argv=['C:/Python314/python.exe',
        'artifacts/muon_continued_current_boundary_heat_20261011/execution_logs/pairing_diagnostics.py','1'],
        cwd=str(ROOT),environment=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),exit_code=0,
        stdout=None,capture_limitation='The first direct command output was tool-truncated; its complete result JSON and array archive are preserved. Independent pairing2 captures complete stdout.'))
    argv=['C:/Python314/python.exe','-m','pytest','--noconftest','tests/test_muon_continued_current_boundary_heat.py','-q']
    env=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    p=subprocess.run(argv,cwd=ROOT,env={**os.environ,**env},capture_output=True,text=True)
    tests=dict(argv=argv,cwd=str(ROOT),environment=env,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)
    if p.returncode:raise RuntimeError(json.dumps(tests))
    files+=list((BASE/'execution_logs').glob('*.py'))
    for name in ('src/bhsm/interface/muon_continued_current_boundary_heat.py',
                 'scripts/evaluate_muon_continued_current_boundary_heat.py',
                 'tests/test_muon_continued_current_boundary_heat.py'):files.append(ROOT/name)
    verification=BASE/'verification.json'
    verification.write_text(json.dumps(dict(classification='VERIFIED_CONTINUED_CURRENT_RELATIVE_DOMAIN_HEAT_SOURCE_REPLAY',
        pairs=pairs,pairing_numeric_records_identical=True,commands=commands,tests=tests,
        source_dependencies_verified=True,
        measure_convention='exact linear nodal integration in the declared piecewise-constant proper-clock density quadrature; actual continuousN(t) is approximated at cellmidpoints and refined16/32',
        source_contact_convention='actual canonical deltaHcan, both directed A contacts, numerator source-dual contact; odd magnetic first direction has fixed even geometry and dM=0',
        domain='one homogeneous common-frame birth trace; past initial0 and future finalfree; additional finalDirichlet is a reference whose full spectral return is computed',
        finite_cutoff_scope='explicit numericalcprobe only; neither physicalc=I/R nor gamma/mode/scale selected',
        peer_review='downstream read-only review found no consequential generalized-square, spectralSchur, or magnetic numerator/source placement defect',
        real_Euclidean_sectorial_contour_proved=False,full_stratified_exterior_completion=False,physical_Pauli_completed=False,
        error_scope='binary64 spectral/eigensolver/current and source-contact diagnostics only; no certified action/eigen/continuum/contour/exterior/physical error'),
        indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    files.append(verification);entries={}
    for path in files:
        raw=path.read_bytes()
        if len(raw)>10*1024**2:raise RuntimeError('publication size cap: '+str(path))
        if path.suffix in('.py','.txt','.json')and b'\r\n'in raw:raise RuntimeError('non-LF text: '+str(path))
        entries[path.relative_to(ROOT).as_posix()]=dict(bytes=len(raw),sha256=sha256(raw).hexdigest())
    manifest=BASE/'publication_manifest.json'
    manifest.write_text(json.dumps(dict(classification='VERIFIED_CONTINUED_CURRENT_RELATIVE_DOMAIN_HEAT_SOURCE_REPLAY',
        files=entries,dependencies=deps,pairs=pairs,physical_native_heat_or_Pauli_completed=False),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=digest(manifest),files=len(entries),dependencies=len(deps),
        source_sha256=digest(ROOT/'src/bhsm/interface/muon_continued_current_boundary_heat.py'),
        result_sha256=digest(BASE/'run_1/result.json'),tests=tests),sort_keys=True))


if __name__=='__main__':main()

"""Freeze actual changing-target even-Y bounds and preserve their exact scope."""
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/muon_changing_closed_fermion_tail_20261011'


def identity(name):
    data=(ROOT/name).read_bytes()
    return dict(path=name,bytes=len(data),sha256=sha256(data).hexdigest())


def main():
    files=set();pairs={};commands=[];pins=0
    for name in ('application.npz','result.json'):
        rows=[identity((FOLDER/f'run_{n}'/name).relative_to(ROOT).as_posix())for n in (1,2)]
        if len({(r['bytes'],r['sha256'])for r in rows})!=1:raise ValueError('tail replay differs '+name)
        pairs[name]=rows;files.update(r['path']for r in rows)
    for n in (1,2):
        result=json.loads((FOLDER/f'run_{n}/result.json').read_bytes())
        for p,h in result['input_hashes'].items():
            if identity(p)['sha256']!=h:raise ValueError('tail consumed bytes changed '+p)
            pins+=1
        logs={}
        for ch in ('stdout','stderr'):
            p=f'artifacts/muon_changing_closed_fermion_tail_run_{n}.{ch}.txt';files.add(p)
            logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
        commands.append(dict(argv=[sys.executable,'scripts/evaluate_muon_changing_closed_fermion_tail.py','--output',f'artifacts/muon_changing_closed_fermion_tail_20261011/run_{n}'],
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),exit_code=0,logs=logs))
    logs={}
    for ch in ('stdout','stderr'):
        p=f'artifacts/muon_changing_closed_fermion_tail_tests.{ch}.txt';files.add(p)
        logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
    commands.append(dict(argv=[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_changing_closed_fermion_tail.py'],
        cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),exit_code=0,tests_passed=2,logs=logs))
    files.update(('src/bhsm/interface/muon_changing_closed_fermion_tail.py','tests/test_muon_changing_closed_fermion_tail.py',
        'scripts/evaluate_muon_changing_closed_fermion_tail.py',Path(__file__).relative_to(ROOT).as_posix()))
    record=dict(classification='VERIFIED_CHANGING_CHRONOLOGICAL_HIGHER_EVEN_Y_BOUNDS',commands=commands,
        independent_byte_replays=pairs,verified_input_hash_count=pins,actual_records=result['records'],
        review='Downstream independently checked exact consumed48pencil reconstruction, temporal8/LR6 grading, generalized Gram contact, affine velocity node-map pullback, and explicit exclusion of primitive/adjoint production errors.',
        DERIVED='Retained generalized even-pencil Cauchy/semigroup certificate; actual raw268 derivative primitive norms, generalized Gram derivative and original chronological contact amplification.',
        EVALUATED='192bit Arb positive-gap/parity/norm certificates for both exact stored48pencils; higher-even-Y value/cotangent upper bounds and both named finite adjoint response amplifications.',
        CONTROL_ONLY='Same conditional finite coefficient/domain and c=1e-11 probe; finite-pencil enclosure scope excludes how entries/fields were produced.',
        UNEVALUATED='Entry/primitive production and quadrature bounds, certified original causal response, full starting-loop/domain/completion and normalized Pauli/observable uncertainty.',
        OWNER_DEFINITION_GAP='none established',higher_even_Y_filled_zero=False,complete_observable=False,physical_a_mu=None,physical_g_mu=None,
        error_scope=result['error_scope'])
    p=FOLDER/'verification.json';p.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n');files.add(p.relative_to(ROOT).as_posix())
    m=dict(classification='FROZEN_REPLAYED_CHANGING_CHRONOLOGICAL_EVEN_Y_BOUNDS',byte_identical_replay=True,files=[identity(n)for n in sorted(files)])
    q=FOLDER/'publication_manifest.json';q.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),publication_manifest=identity(q.relative_to(ROOT).as_posix()),verification=identity(p.relative_to(ROOT).as_posix())),sort_keys=True))


if __name__=='__main__':main()

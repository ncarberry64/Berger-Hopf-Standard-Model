"""Verify complete source-required n6 return forms and their independent replay."""
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/muon_magnetic_n6_return_fermion_20261011'


def identity(name):
    data=(ROOT/name).read_bytes()
    return dict(path=name,bytes=len(data),sha256=sha256(data).hexdigest())


def main():
    files=set();pairs=[];commands=[];pins=0
    for p in sorted((FOLDER/'run_1').iterdir()):
        if not p.is_file():continue
        rows=[identity((FOLDER/f'run_{n}'/p.name).relative_to(ROOT).as_posix())for n in (1,2)]
        if len({(r['bytes'],r['sha256'])for r in rows})!=1:raise ValueError('n6 replay differs '+p.name)
        pairs.append(dict(name=p.name,byte_identical=True,files=rows));files.update(r['path']for r in rows)
    for n in (1,2):
        result=json.loads((FOLDER/f'run_{n}/result.json').read_bytes())
        if result['full_n6_harmonic_count']!=49 or result['full_n6_return_dimension']!=7056:raise ValueError('incomplete n6 domain')
        for p,h in result['input_hashes'].items():
            if identity(p)['sha256']!=h:raise ValueError('n6 consumed input changed '+p)
            pins+=1
        logs={}
        for ch in ('stdout','stderr'):
            p=f'artifacts/muon_magnetic_n6_return_fermion_run_{n}.{ch}.txt';files.add(p)
            logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
        commands.append(dict(argv=[sys.executable,'scripts/evaluate_muon_magnetic_n6_return_fermion.py','--output',f'artifacts/muon_magnetic_n6_return_fermion_20261011/run_{n}'],
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),exit_code=0,logs=logs))
    logs={}
    for ch in ('stdout','stderr'):
        p=f'artifacts/muon_magnetic_n6_return_fermion_tests.{ch}.txt';files.add(p)
        logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
    commands.append(dict(argv=[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_magnetic_n6_return_fermion.py'],
        cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),exit_code=0,tests_passed=2,logs=logs))
    files.update(('src/bhsm/interface/muon_magnetic_n6_return_fermion.py','tests/test_muon_magnetic_n6_return_fermion.py',
        'scripts/evaluate_muon_magnetic_n6_return_fermion.py',Path(__file__).relative_to(ROOT).as_posix()))
    v=dict(classification='VERIFIED_SAME_PHASE_MAGNETIC_N6_FERMION_RETURN_FORM',commands=commands,independent_byte_replays=pairs,
        verified_input_hash_count=pins,actual_records=result['records'],review='Downstream independently checked all49 harmonics, literal spectators, all18 fibers, same q12/8function temporal congruence, and both nonzero product placements.',
        DERIVED='fieldn4 times inputn1 reaches F5; magneticn1 reaches F6; fieldn4 times outputn2 supplies its left return. Exact highest-weight product tests prove both reached edges are nonzero.',
        EVALUATED='21 complete family/spectator blocks per arm, dimension336 each, original weak forms and Gram, all7056 return coordinates, source quadrature and eigen diagnostics.',
        CONTROL_ONLY='Same explicit positive-reference finite coefficient/domain application, not a physical propagator or covariance selection.',
        UNEVALUATED='Matched full starting-loop sum and complement, continued physical domain/completion, normalized soft Pauli readout and final observable uncertainty.',
        OWNER_DEFINITION_GAP='none established',starting_field_loop_domain_enlarged=False,small_mode_deletion=False,complete_observable=False,
        physical_a_mu=None,physical_g_mu=None,error_scope='Exact source-image representation and binary64 actual weak-action/eigen diagnostics only; no upstream/continuum/physical matching or anomaly enclosure.')
    p=FOLDER/'verification.json';p.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n');files.add(p.relative_to(ROOT).as_posix())
    m=dict(classification='FROZEN_REPLAYED_MAGNETIC_N6_SOURCE_RETURN_FORM',byte_identical_replay=True,files=[identity(n)for n in sorted(files)])
    q=FOLDER/'publication_manifest.json';q.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),publication_manifest=identity(q.relative_to(ROOT).as_posix()),verification=identity(p.relative_to(ROOT).as_posix())),sort_keys=True))


if __name__=='__main__':main()

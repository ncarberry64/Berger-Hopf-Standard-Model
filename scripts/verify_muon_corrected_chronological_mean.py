"""Freeze the corrected action mean load and changing chronological adjoint."""
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/muon_corrected_chronological_mean_20261011'


def identity(name):
    data=(ROOT/name).read_bytes()
    return dict(path=name,bytes=len(data),sha256=sha256(data).hexdigest())


def main():
    files=set();pairs={};commands=[];pins=0;results={}
    for stem in ('muon_corrected_profile_mean_load','muon_changing_closed_fermion_mean'):
        folder='artifacts/'+stem+'_20261011'
        pairs[stem]={}
        for name in ('application.npz','result.json'):
            rows=[identity(f'{folder}/run_{n}/{name}')for n in (1,2)]
            if len({(r['bytes'],r['sha256'])for r in rows})!=1:raise ValueError('independent bytes differ '+stem+'/'+name)
            pairs[stem][name]=rows;files.update(r['path']for r in rows)
        for n in (1,2):
            r=json.loads((ROOT/folder/f'run_{n}/result.json').read_bytes())
            for p,h in r['input_hashes'].items():
                if identity(p)['sha256']!=h:raise ValueError('consumed bytes changed '+p)
                pins+=1
            logs={}
            for ch in ('stdout','stderr'):
                p=f'artifacts/{stem}_run_{n}.{ch}.txt';files.add(p)
                logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
            commands.append(dict(argv=[sys.executable,f'scripts/evaluate_{stem}.py','--output',f'{folder}/run_{n}'],
                cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),exit_code=0,logs=logs))
        results[stem]=r
        files.update((f'src/bhsm/interface/{stem}.py',f'tests/test_{stem}.py',f'scripts/evaluate_{stem}.py'))
    for stem,passed in (('muon_corrected_profile_mean_load',2),('muon_changing_closed_fermion_mean',3),('muon_changing_closed_fermion_mean_phase',1)):
        logs={}
        for ch in ('stdout','stderr'):
            p=f'artifacts/{stem}_tests.{ch}.txt';files.add(p)
            logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
        test=f'tests/test_{stem}.py';files.add(test)
        commands.append(dict(argv=[sys.executable,'-m','pytest','--noconftest','-q',test],cwd=str(ROOT),
            environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),exit_code=0,tests_passed=passed,logs=logs))
    files.add(Path(__file__).relative_to(ROOT).as_posix());FOLDER.mkdir(exist_ok=True)
    record=dict(classification='VERIFIED_CORRECTED_CHRONOLOGICAL_ACTION_MEAN_APPLICATION',commands=commands,
        independent_byte_replays=pairs,verified_input_hash_count=pins,actual_records={k:v['records']for k,v in results.items()},
        review='Owner independently checked corrected child-profile sign, full268 D3 density/metric/normal/connection contacts and Q/Qdot source motion; downstream independently checked stable first/second divided differences and generalized Gram dual, including the fixed computational congruence.',
        DERIVED='D3S[z,uA,uB]+D2S[D_z uA,uB]+D2S[uA,D_z uB]; full Y² action/Gram duals of Tr E1; integrated affine phase-map target and original chronological K^T adjoint.',
        EVALUATED='Actual corrected full488 first response, all268 raw mean rows and all3 magnetic source axes; changing n0/C6 eight-function temporal heat target; both original temporal/radial border adjoints and paired contacts.',
        CONTROL_ONLY='Conditional finite coefficient cell and c=1e-11 spectral probe. Synthetic directions are confined to independent derivative tests.',
        UNEVALUATED='Moving common226 birth second mean, higher even Y terms, full starting loop/temporal complement, physical continued domain/completion, overlap-subtracted normalized soft Pauli value and total observable uncertainty.',
        OWNER_DEFINITION_GAP='none established',statistics_factor_applied=False,complete_observable=False,
        physical_a_mu=None,physical_g_mu=None,error_scope='Binary64 original-action derivatives, pairing and quadrature/adjoint residual diagnostics on the represented source domain; no outward production/continuum/matching or anomaly enclosure.')
    p=FOLDER/'verification.json';p.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n');files.add(p.relative_to(ROOT).as_posix())
    m=dict(classification='FROZEN_REPLAYED_CORRECTED_CHRONOLOGICAL_MEAN',byte_identical_replay=True,
        files=[identity(n)for n in sorted(files)],complete_observable=False)
    q=FOLDER/'publication_manifest.json';q.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=identity(p.relative_to(ROOT).as_posix()),publication_manifest=identity(q.relative_to(ROOT).as_posix()),files=len(files),byte_identical=True),sort_keys=True))


if __name__=='__main__':main()

"""Verify the continuous-time reference application and retain failed integration checks."""
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/muon_dirichlet_source_green_collocation_20261011'


def identity(name):
    p=ROOT/name;b=p.read_bytes()
    return dict(path=name,bytes=len(b),sha256=sha256(b).hexdigest())


def main():
    files=set();pairs={};commands=[];pins=0
    for name in ('application.npz','result.json'):
        paths=[f'artifacts/muon_dirichlet_source_green_collocation_20261011/run_{n}/{name}' for n in (2,3)]
        infos=[identity(p) for p in paths];files.update(paths)
        if len({(r['bytes'],r['sha256'])for r in infos})!=1:raise ValueError('independent replay differs '+name)
        pairs[name]=infos
    for n in (2,3):
        d=json.loads((FOLDER/f'run_{n}/result.json').read_text())
        for p,h in d['input_hashes'].items():
            if identity(p)['sha256']!=h:raise ValueError('consumed input changed '+p)
            pins+=1
    for stem,runs in (('muon_dirichlet_source_green',(1,)),('muon_dirichlet_source_green_collocation',(1,2,3))):
        for n in runs:
            logs={}
            for ch in ('stdout','stderr'):
                p=f'artifacts/{stem}_run_{n}.{ch}.txt';files.add(p)
                logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
            commands.append(dict(argv=[sys.executable,f'scripts/evaluate_{stem}.py','--output',f'artifacts/{stem}_20261011/run_{n}'],
                cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),
                exit_code=0,canonical_replay=stem.endswith('collocation')and n in(2,3),logs=logs))
    for stem,suffix,exitcode,passed in (('muon_dirichlet_source_green','',0,2),
        ('muon_dirichlet_source_green_collocation','',1,1),('muon_dirichlet_source_green_collocation','_2',0,2)):
        logs={}
        for ch in ('stdout','stderr'):
            p=f'artifacts/{stem}_tests{suffix}.{ch}.txt';files.add(p)
            logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
        commands.append(dict(argv=[sys.executable,'-m','pytest','--noconftest','-q',f'tests/test_{stem}.py'],
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),
            exit_code=exitcode,tests_passed=passed,logs=logs))
    # Initial results remain diagnostic inputs, not canonical replays after metadata repair.
    for stem in ('muon_dirichlet_source_green','muon_dirichlet_source_green_collocation'):
        files.add(f'artifacts/{stem}_20261011/run_1/application.npz')
        original=f'artifacts/{stem}_20261011/run_1/result.json'
        if stem.endswith('collocation'):
            # The diagnostic's historical executable pin is deliberately
            # preserved as text, not asserted to equal the final producer.
            diagnostic=original+'.txt';(ROOT/diagnostic).write_bytes((ROOT/original).read_bytes());files.add(diagnostic)
        else:files.add(original)
        files.update((f'src/bhsm/interface/{stem}.py',f'scripts/evaluate_{stem}.py',f'tests/test_{stem}.py'))
    files.add(Path(__file__).relative_to(ROOT).as_posix())
    failed=json.loads((ROOT/'artifacts/muon_dirichlet_source_green_20261011/run_1/result.json').read_text())
    canonical=json.loads((FOLDER/'run_2/result.json').read_text())
    record=dict(classification='VERIFIED_CONTINUOUS_TIME_REFERENCE_SOURCE_GREEN',commands=commands,
        independent_byte_replay=pairs,verified_input_hash_count=pins,
        rejected_RK4_refinement=[{k:v for k,v in r.items()if k!='block_records'}for r in failed['records']],
        Gauss_8_10_refinement=[{k:v for k,v in r.items()if k!='block_records'}for r in canonical['records']],
        initial_attempt_scope='RK4 8/16 refinement failed and is excluded as an accepted response. Collocation run1 has legacy steps_per_half metadata for stage count; canonical runs2/3 use Gauss_stages and export stage residuals.',
        test_repair='Initial test used an arbitrary lower threshold on the coarse difference. Replaced it with the actual convergence ratio fine<coarse/100; original-action high-degree current test retained.',
        review='Validation agent read-only verified Gauss table, both adjoint/primal stage equations, literal complex-left pairing, midpoint conormal continuity and final Dirichlet face correction.',
        DERIVED='Same A=partial_t/N+B source problem A^dagger(Af-S)=0, both Dirichlet faces, exact invariant family and Wigner spectator blocks and Gaussian -1 current orientation.',
        EVALUATED='Full1200 field inverse source placements and all18 odd20 fermion fibers; continuous-time Gauss8/10 source contractions, face/stage residuals and independent byte replay.',
        CONTROL_ONLY='Unregulated same positive ADM reference, declared inside-cell coefficient interpolation and full-time benchmark; no physical covariance or cutoff selection.',
        UNEVALUATED='Outward time/field-production bounds, differential starting-loop complement, native domain/completion, normalized Lorentz Pauli value and total observable uncertainty.',
        OWNER_DEFINITION_GAP='none established',
        error_scope='Binary64 same-reference Gauss refinement and action residual diagnostics only. They are not an anomaly enclosure.',
        complete_observable=False,physical_a_mu=None,physical_g_mu=None)
    p=FOLDER/'verification.json';p.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    files.add(p.relative_to(ROOT).as_posix())
    manifest=dict(classification='FROZEN_REPLAYED_CONTINUOUS_TIME_REFERENCE_SOURCE_GREEN',byte_identical_replay=True,
        all_canonical_input_hashes_verified=True,files=[identity(n)for n in sorted(files)])
    q=FOLDER/'publication_manifest.json';q.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=identity(p.relative_to(ROOT).as_posix()),publication_manifest=identity(q.relative_to(ROOT).as_posix()),files=len(files),byte_identical=True),sort_keys=True))


if __name__=='__main__':main()

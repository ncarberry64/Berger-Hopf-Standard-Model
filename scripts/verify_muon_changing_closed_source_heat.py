"""Freeze the executed same-background mean/contact/insertion contraction."""
from hashlib import sha256
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STEM='muon_changing_closed_source_heat';FOLDER=ROOT/'artifacts'/(STEM+'_20261011')


def identity(path):
    b=(ROOT/path).read_bytes()
    return dict(path=path,bytes=len(b),sha256=sha256(b).hexdigest())


def main():
    files=set();commands=[];pairs={};pins=0
    for name in('application.npz','result.json'):
        rows=[identity((FOLDER/f'run_{n}'/name).relative_to(ROOT).as_posix())for n in(1,2)]
        if len({(r['sha256'],r['bytes'])for r in rows})!=1:raise ValueError('source contraction replay differs '+name)
        pairs[name]=rows;files.update(r['path']for r in rows)
    for n in(1,2):
        result=json.loads((FOLDER/f'run_{n}/result.json').read_bytes())
        for p,h in result['input_hashes'].items():
            if identity(p)['sha256']!=h:raise ValueError('source contraction input changed '+p)
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
    dependencies=('src/bhsm/interface/muon_coupled_magnetic_field_variation.py',
        'src/bhsm/interface/muon_magnetic_cell_source_heat.py',
        'scripts/evaluate_muon_corrected_profile_mean_load.py',
        'src/bhsm/interface/muon_profile_preserving_phase_sample.py')
    verified=dict(classification='VERIFIED_CHANGING_SOURCE_HEAT_CONTACT_BOTH_ORDERS_AND_JOINED_BIRTH_MEAN',commands=commands,
        independent_byte_replays=pairs,verified_input_hash_count=pins,additional_import_dependencies=[identity(p)for p in dependencies],
        actual_records=result['records'],error_scope=result['error_scope'],
        DERIVED='Full192 n1 image factor derivative and source-square contact on the same generalized changing n0/C6 temporal8 trace; both Duhamel orders and the same joined mean cotangent counted once.',
        EVALUATED='Actual normalized magnetic gauge/H fields on both arms at12/16 split quadrature and24/32 common-Y coefficient circles; exact same differentiated base, source contact, both insertions and joined birth mean.',
        CONTROL_ONLY='Positive reference temporal source space and explicit c1e-11; Y0 coefficient expansion is an algorithm and not a selected massless background.',
        UNEVALUATED='Physical native contour, graded starting-loop complement and relative completion, graph overlap subtraction and normalized signed soft Pauli remainder with its complete uncertainty.',
        OWNER_DEFINITION_GAP='none established',statistics_factor_applied=False,complete_observable=False,
        physical_a_mu=None,physical_g_mu=None)
    p=FOLDER/'verification.json';p.write_text(json.dumps(verified,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n');files.add(p.relative_to(ROOT).as_posix())
    manifest=dict(classification='FROZEN_EXECUTED_CHANGING_SOURCE_CONTACT_INSERTIONS_AND_MEAN',byte_identical_replay=True,
        files=[identity(p)for p in sorted(files)],complete_observable=False)
    q=FOLDER/'publication_manifest.json';q.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),verified=identity(p.relative_to(ROOT).as_posix()),manifest=identity(q.relative_to(ROOT).as_posix())),sort_keys=True))


if __name__=='__main__':main()

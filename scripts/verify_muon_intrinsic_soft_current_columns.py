"""Freeze the independently replayed n0/n1 source-image Gaussian applications."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/muon_intrinsic_soft_current_columns_20261011'


def identity(name):
    p=ROOT/name;b=p.read_bytes()
    return dict(path=name,bytes=len(b),sha256=sha256(b).hexdigest())


def main():
    files=set();pairs=[];commands=[];input_count=0
    for stem,runs,attempts in (('soft_current',(3,4),range(1,5)),('soft_constant',(2,3),range(1,4))):
        folder='artifacts/muon_intrinsic_'+stem+'_columns_20261011'
        equal={}
        for filename in ('application.npz','result.json'):
            names=[folder+'/run_'+str(n)+'/'+filename for n in runs]
            infos=[identity(n)for n in names];files.update(names)
            if len({(x['bytes'],x['sha256'])for x in infos})!=1:
                raise ValueError('canonical independent replay differs: '+filename)
            equal[filename]=infos
        pairs.append(dict(folder=folder,runs=list(runs),byte_identical=True,files=equal))
        for n in runs:
            result=json.loads((ROOT/folder/('run_'+str(n))/'result.json').read_text())
            for name,h in result['input_hashes'].items():
                if identity(name)['sha256']!=h:raise ValueError('consumed input changed '+name)
                input_count+=1
        for n in attempts:
            logs={}
            for channel in ('stdout','stderr'):
                name='artifacts/muon_intrinsic_'+stem+'_columns_run_'+str(n)+'.'+channel+'.txt'
                files.add(name);logs[channel]=dict(**identity(name),text=(ROOT/name).read_text())
            commands.append(dict(argv=['C:\\Python314\\python.exe',
                'scripts/evaluate_muon_intrinsic_'+stem+'_columns.py','--output',folder+'/run_'+str(n)],
                cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),
                exit_code=0,canonical_replay=n in runs,logs=logs))
    for suffix,exitcode,count in (('',1,2),('_2',0,2),('_3',0,3)):
        logs={}
        for channel in ('stdout','stderr'):
            name='artifacts/muon_intrinsic_soft_current_columns_tests'+suffix+'.'+channel+'.txt'
            files.add(name);logs[channel]=dict(**identity(name),text=(ROOT/name).read_text())
        commands.append(dict(argv=['C:\\Python314\\python.exe','-m','pytest','--noconftest','-q',
            'tests/test_muon_intrinsic_soft_current_columns.py'],cwd=str(ROOT),
            environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),
            exit_code=exitcode,test_count=count,logs=logs))
    files.update(('src/bhsm/interface/muon_intrinsic_soft_current_columns.py',
        'src/bhsm/interface/muon_intrinsic_soft_constant_columns.py',
        'scripts/evaluate_muon_intrinsic_soft_current_columns.py',
        'scripts/evaluate_muon_intrinsic_soft_constant_columns.py',
        'tests/test_muon_intrinsic_soft_current_columns.py',Path(__file__).relative_to(ROOT).as_posix()))
    record=dict(classification='VERIFIED_REPLAYED_COMPLETE_HIGGS_SOURCE_IMAGE_SOFT_COLUMNS',
        commands=commands,independent_byte_replays=pairs,verified_input_hash_count=input_count,
        review=dict(downstream='clean read-only review of both helpers',validation='clean read-only review of both helpers'),
        correction='The independent c=0 original-action derivative initially exposed an omitted even-Higgs unchanged block. Both unchanged H blocks, both PF square placements, the numerator, and both PH mixed placements are now retained.',
        replay_metadata_correction='A third constant-input orientation test was added after earlier applications completed. Their arrays were unchanged but their recorded test-file pins were stale. Canonical tangent runs 3/4 and constant runs 2/3 consume the final identical test bytes. Earlier logs are preserved, not promoted to canonical replays.',
        DERIVED='exact angular source-image closure and both orientations of the one common full Hodd80 plus Heven140 Gaussian graph',
        EVALUATED='three fixed-Y families on each pinned incoming/outgoing background; n0->n1 and n1->n0+n2 columns; independent original-action derivative and three focused tests',
        CONTROL_ONLY='common finite spectral cutoff probe and stored coefficient cell; no physical cutoff, formation mode or state selector',
        UNEVALUATED='differential starting-loop complements, continuum/native completion, normalized pole and signed Pauli contraction with matching and full uncertainty',
        OWNER_DEFINITION_GAP='none established',
        error_scope='outward contracted Hermite-kernel approximation only; no total observable enclosure; floating assembly, angular quadrature, eigen/contraction rounding and physical domain complements remain separate',
        complete_observable=False,physical_a_mu=None,physical_g_mu=None)
    verification=FOLDER/'verification.json'
    verification.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    files.add(verification.relative_to(ROOT).as_posix())
    manifest=dict(classification='FROZEN_REPLAYED_FULL_HIGGS_SOFT_CURRENT_SOURCE_COLUMNS',
        byte_identical_replay=True,all_input_hashes_verified=True,
        files=[identity(n)for n in sorted(files)],complete_observable=False)
    (FOLDER/'publication_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=identity(verification.relative_to(ROOT).as_posix()),
        publication_manifest=identity((FOLDER/'publication_manifest.json').relative_to(ROOT).as_posix()),
        byte_replay=True,files=len(files),input_hashes=input_count),sort_keys=True))


if __name__=='__main__':main()

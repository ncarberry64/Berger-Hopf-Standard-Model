"""Verify the immutable corrected birth-source endpoint pair and current pins."""
from pathlib import Path
from hashlib import sha256
import argparse, json
ROOT = Path(__file__).resolve().parents[1]


def verify(first, second, output):
    out = ROOT/output
    if out.exists(): raise FileExistsError('preserve endpoint pair verification')
    paths = [ROOT/first, ROOT/second]
    receipts = [json.loads((p/'result.json').read_bytes()) for p in paths]
    if receipts[0]['input_hashes'] != receipts[1]['input_hashes']:
        raise ValueError('both applications must consume the identical source paths and pins')
    names = sorted(set(receipts[0]['archives']) | {'result.json'})
    if names != sorted(set(receipts[1]['archives']) | {'result.json'}):
        raise ValueError('every output must be present in both applications')
    pairs = []
    for name in names:
        a, b = [p/name for p in paths]
        ab, bb = a.read_bytes(), b.read_bytes()
        if ab != bb: raise ValueError('nonidentical endpoint output '+name)
        h = sha256(ab).hexdigest()
        if name != 'result.json' and any(r['archives'][name]['sha256'] != h for r in receipts):
            raise ValueError('archive receipt disagrees '+name)
        pairs.append(dict(first=a.relative_to(ROOT).as_posix(),
            second=b.relative_to(ROOT).as_posix(), bytes=len(ab), sha256=h))
    for p,h in receipts[0]['input_hashes'].items():
        if sha256((ROOT/p).read_bytes()).hexdigest() != h:
            raise ValueError('consumed source changed '+p)
    logs = []
    for folder in (first, second):
        p = ROOT/folder.parent/(folder.name+'.stdout.txt')
        logs.append(dict(path=p.relative_to(ROOT).as_posix(),
            sha256=sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size))
    code = ['src/bhsm/interface/muon_corrected_birth_source_endpoint.py',
        'scripts/evaluate_muon_corrected_birth_source_endpoint.py',
        'tests/test_muon_corrected_birth_source_endpoint.py',
        'scripts/verify_muon_corrected_birth_source_endpoint_pair.py']
    out.mkdir(parents=True)
    result = dict(classification='IMMUTABLE_CORRECTED_TWO_TERM_BIRTH_ENDPOINT_SOURCE_PAIR_VERIFICATION',
        all_output_bytes_identical=True, all_consumed_pins_current=True,
        output_pairs=pairs, all_output_count=len(pairs), checked_input_hashes=len(receipts[0]['input_hashes']),
        stdout=logs, source_hashes={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in code},
        commands=[['C:/Python314/python.exe','-u','scripts/evaluate_muon_corrected_birth_source_endpoint.py',
            '--stage-folder','artifacts/muon_changing_canonical_source_20261012/run_3',
            '--output',p.as_posix()] for p in (first, second)],
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
        working_directory=str(ROOT),
        focused_control=dict(command=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',
            'tests/test_muon_corrected_birth_source_endpoint.py'],
            observed_tool_result='2 passed in 1.18s',exit_code=0,
            evidence_scope='observed tool result; no reconstructed stdout digest'),
        retained_error_scope='stored coefficient arithmetic and binary two-direction endpoint/step-halving controls; no certified third-action, physical event/pole, continuum or Pauli bound',
        source_seed='fresh parent and child reconstitution from changing-stage run3, both coefficient terms retained',
        baseline_reset_guard_is_not_promoted=True,
        full_ancestor_regeneration_or_physical_normalization_claimed=False)
    p=out/'verification.json'; p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    selected = []
    for item in pairs:
        for key in ('first','second'):
            selected.append(dict(path=item[key],sha256=item['sha256'],bytes=item['bytes']))
    selected.extend(dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest(),bytes=(ROOT/p).stat().st_size) for p in code)
    selected.extend(logs)
    selected.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
    manifest = dict(classification='COMPACT_CORRECTED_BIRTH_SOURCE_ENDPOINT_PUBLICATION_MANIFEST',
        selected=selected,selected_count=len(selected),total_bytes=sum(i['bytes'] for i in selected),
        verification_sha256=sha256(p.read_bytes()).hexdigest(),
        provenance_scope='two byte-identical endpoint applications; no physical source/branch/pole promotion')
    q=out/'publication_manifest.json';q.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(all_output_bytes_identical=True,all_output_count=len(pairs),
        checked_input_hashes=len(receipts[0]['input_hashes']),
        verification_sha256=sha256(p.read_bytes()).hexdigest(),
        manifest_sha256=sha256(q.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first',type=Path,default=Path('artifacts/muon_corrected_birth_source_endpoint_20261012/run_1'))
    parser.add_argument('--second',type=Path,default=Path('artifacts/muon_corrected_birth_source_endpoint_20261012/run_2'))
    parser.add_argument('--output',type=Path,default=Path('artifacts/muon_corrected_birth_source_endpoint_20261012/pair_verification'))
    args=parser.parse_args();verify(args.first,args.second,args.output)

"""Freeze the independently replayed analytic dual/current application."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent.parent
files=[];pairs=[];deps={}
for name in('result.json','joined_16.npz','joined_32.npz'):
    a,b=(BASE/f'run_{i}'/name for i in(1,2))
    if a.read_bytes()!=b.read_bytes():raise RuntimeError('independent action replay differs')
    pairs.append(dict(paths=[p.relative_to(ROOT).as_posix()for p in(a,b)],byte_identical=True,
        sha256=sha256(a.read_bytes()).hexdigest()));files.extend((a,b))
md=json.loads((BASE/'run_1/result.json').read_bytes())
for p,h in md['input_hashes'].items():
    if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise RuntimeError('consumed source changed: '+p)
    deps[p]=h
files.extend((BASE/'execution_logs').iterdir());files.append(BASE/'verification.json')
files.extend(ROOT/p for p in('src/bhsm/interface/muon_continued_action_dual.py',
    'scripts/evaluate_muon_continued_action_dual.py','tests/test_muon_continued_action_dual.py'))
entries={}
for p in files:
    raw=p.read_bytes()
    if len(raw)>10*1024**2:raise RuntimeError('publication size cap exceeded')
    if p.suffix in('.py','.json','.txt')and b'\r\n'in raw:raise RuntimeError('text LF required: '+str(p))
    entries[p.relative_to(ROOT).as_posix()]=dict(bytes=len(raw),sha256=sha256(raw).hexdigest())
manifest=BASE/'publication_manifest.json'
manifest.write_text(json.dumps(dict(classification=md['classification'],files=entries,dependencies=deps,pairs=pairs,
    physical_Euclidean_relative_heat_or_Pauli_completed=False),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),files=len(entries),dependencies=len(deps),
    source_sha256=sha256((ROOT/'src/bhsm/interface/muon_continued_action_dual.py').read_bytes()).hexdigest(),
    result_sha256=sha256((BASE/'run_1/result.json').read_bytes()).hexdigest()),sort_keys=True))

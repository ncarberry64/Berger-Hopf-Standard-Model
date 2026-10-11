"""Verify actual canonical graph pairs and their small lossless packages."""
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[3]
base=ROOT/'artifacts/muon_chronological_canonical_graph_20261011'
old=base/'verification.json';receipt=json.loads(old.read_bytes())
paths=[ROOT/r['path'] for r in receipt['publication_files']
    if not r['path'].endswith('/record_canonical_verification.py')]
paths.append(Path(__file__))
for row in receipt['publication_files']:
    p=ROOT/row['path'];data=p.read_bytes()
    if len(data)!=row['bytes'] or sha256(data).hexdigest()!=row['sha256']:
        raise ValueError('receipt-bound reviewed file changed: '+row['path'])
for pair in receipt['independent_process_comparisons']:
    side,steps=pair['side'],pair['steps']
    a=base/f'{side}_{steps}steps_run_1';b=base/f'{side}_{steps}steps_run_2'
    for name in ('application.npz','result.json'):
        if (a/name).read_bytes()!=(b/name).read_bytes():raise ValueError('producer replays differ')
    if steps>1:
        a=a.with_name(a.name+'_cell_package');b=b.with_name(b.name+'_cell_package')
        r=json.loads((a/'result.json').read_bytes())
        if not r['all_arrays_bit_identical']:raise ValueError('package not verified')
        for name in ['result.json',*r['pieces']]:
            if (a/name).read_bytes()!=(b/name).read_bytes():raise ValueError('package replays differ')
rows=[]
for p in sorted(set(paths)):
    data=p.read_bytes()
    if len(data)>10*1024**2:raise ValueError('publication file exceeds10MiB')
    rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest()))
receipt['publication_files']=rows
receipt['collector_correction']='earlier collector assumed unsplit archives; this collector verifies the actual lossless packages and excludes that obsolete collector source'
receipt['prior_local_verification_sha256']=sha256(old.read_bytes()).hexdigest()
out=base/'publication_verification.json'
if out.exists():raise FileExistsError('preserve immutable publication receipt')
out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(path=out.relative_to(ROOT).as_posix(),sha256=sha256(out.read_bytes()).hexdigest(),files=len(rows),pairs=len(receipt['independent_process_comparisons']))))

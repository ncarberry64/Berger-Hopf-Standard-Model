"""Lossless cell packaging of completed canonical action graph values."""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
import json
import numpy as np
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

def digest(a):
    b=BytesIO();np.lib.format.write_array(b,a,allow_pickle=False)
    return sha256(b.getvalue()).hexdigest()

def package(source,output):
    source=Path(source);out=Path(output)
    if out.exists():raise FileExistsError('preserve previous packages')
    rb=(source/'result.json').read_bytes();r=json.loads(rb);data=(source/'application.npz').read_bytes()
    if sha256(data).hexdigest()!=r['numerical_sha256']:raise ValueError('canonical application changed')
    with np.load(BytesIO(data),allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
    pieces={'reference.npz':{}};inventory={}
    for name,a in arrays.items():
        file=name[:9]+'.npz' if name.startswith('cell_') and name[5:9].isdigit() else 'reference.npz'
        pieces.setdefault(file,{})[name]=a
        inventory[name]=dict(storage=[file],operation='identity',dtype=str(a.dtype),shape=list(a.shape),npy_sha256=digest(a))
    out.mkdir(parents=True);records={}
    for file,values in pieces.items():
        _compressed_npz(out/file,values);raw=(out/file).read_bytes()
        if len(raw)>10*1024**2:raise ValueError('publication piece exceeds10MiB')
        records[file]=dict(bytes=len(raw),sha256=sha256(raw).hexdigest())
    for file,values in pieces.items():
        with np.load(out/file,allow_pickle=False) as f:
            for name,a in values.items():
                if digest(f[name])!=digest(a):raise RuntimeError('packaged values differ: '+name)
    md=dict(scope='LOSSLESS_CELL_PACKAGING_OF_CANONICAL_ACTION_GRAPH',original_receipt=r,
        original_receipt_sha256=sha256(rb).hexdigest(),original_archive_sha256=sha256(data).hexdigest(),
        all_arrays_bit_identical=True,computation_reexecuted=False,array_inventory=inventory,pieces=records,
        packaging_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    return dict(array_count=len(arrays),pieces=len(pieces),all_arrays_bit_identical=True,
        maximum_piece_bytes=max(a['bytes'] for a in records.values()))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();print(json.dumps(package(a.source,a.output),sort_keys=True))

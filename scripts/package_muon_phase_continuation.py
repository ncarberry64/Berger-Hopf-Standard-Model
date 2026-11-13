"""Losslessly split an evaluated phase archive into small publication files.

No numerical action or trajectory is re-executed.  Every original array
is reconstructed and checked bit for bit before the package is accepted.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import numpy as np
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def array_digest(value):
    stream=BytesIO();np.lib.format.write_array(stream,np.asarray(value),allow_pickle=False)
    return sha256(stream.getvalue()).hexdigest()


def package_phase_application(source,output):
    source=Path(source);out=Path(output)
    if out.exists():raise FileExistsError('preserve existing packages')
    receipt_bytes=(source/'result.json').read_bytes();receipt=json.loads(receipt_bytes)
    original_bytes=(source/'application.npz').read_bytes()
    if sha256(original_bytes).hexdigest()!=receipt['numerical_sha256']:raise ValueError('phase archive hash mismatch')
    with np.load(BytesIO(original_bytes),allow_pickle=False) as data:arrays={k:data[k] for k in data.files}
    indices=arrays['stage_indices'];pieces={'reference.npz':{}};inventory={}
    stage_indexed={'stage_unknowns','stage_midpoint_raw','stage_residual','stage_row_scale','stage_jacobian',
        'stage_initial_face','stage_final_face','material_wall_conormals'}
    for k in indices:pieces[f'stage_{int(k):04d}.npz']={}
    for name,value in arrays.items():
        if name in stage_indexed:
            storage=[]
            for j,k in enumerate(indices):
                file=f'stage_{int(k):04d}.npz';pieces[file][name]=value[j];storage.append(file)
            inventory[name]=dict(storage=storage,operation='stack')
        elif name.startswith('stage_') and '_iteration_' in name:
            file=name[:10]+'.npz';pieces[file][name]=value
            inventory[name]=dict(storage=[file],operation='identity')
        else:
            pieces['reference.npz'][name]=value;inventory[name]=dict(storage=['reference.npz'],operation='identity')
        inventory[name].update(dtype=str(value.dtype),shape=list(value.shape),npy_sha256=array_digest(value))
    out.mkdir(parents=True);piece_rows={}
    for file,values in pieces.items():
        _compressed_npz(out/file,values);raw=(out/file).read_bytes()
        if len(raw)>10*1024**2:raise ValueError('stage package exceeds publication limit; preserve original output')
        piece_rows[file]=dict(bytes=len(raw),sha256=sha256(raw).hexdigest())
    loaded={}
    for file in pieces:
        with np.load(out/file,allow_pickle=False) as f:loaded[file]={name:f[name] for name in f.files}
    for name,row in inventory.items():
        recovered=np.stack([loaded[file][name] for file in row['storage']]) if row['operation']=='stack' else loaded[row['storage'][0]][name]
        if array_digest(recovered)!=row['npy_sha256']:raise RuntimeError('lossless reconstruction failed: '+name)
    md=dict(scope='LOSSLESS_STAGE_PACKAGING_OF_EVALUATED_FULL_ACTION_PHASE_CONTINUATION',
        original_receipt_sha256=sha256(receipt_bytes).hexdigest(),original_archive_sha256=sha256(original_bytes).hexdigest(),
        original_receipt=receipt,all_arrays_bit_identical=True,array_count=len(arrays),array_inventory=inventory,pieces=piece_rows,
        packaging_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        computation_reexecuted=False,numerical_or_scientific_scope_changed=False)
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(array_count=len(arrays),pieces=len(pieces),all_arrays_bit_identical=True,
        maximum_piece_bytes=max(r['bytes'] for r in piece_rows.values()),receipt_sha256=sha256((out/'result.json').read_bytes()).hexdigest())


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(package_phase_application(a.source,a.output),sort_keys=True))

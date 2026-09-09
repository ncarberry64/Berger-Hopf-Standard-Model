"""Strict, hash-bound row storage for symmetric physical Hessian error balls."""
import hashlib
import json
from pathlib import Path
import numpy as np


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def validate_arrays(midpoint, radius, row, dimension=99, outputs=99):
    if type(row) is not int or not 0 <= row < dimension:
        raise ValueError('invalid Hessian row')
    for value in (midpoint, radius):
        if (np.asarray(value).dtype != np.dtype('float64')
                or np.shape(value) != (outputs, dimension-row)
                or not np.all(np.isfinite(value))):
            raise ValueError('row requires complete finite binary64 arrays')
    if np.any(radius < 0):
        raise ValueError('negative error radius')


def save_row(path, midpoint, radius, row, fingerprint, origin,
             *, dimension=99, outputs=99, precision=256):
    """Write only after the producer verifies outward export containment."""
    path=Path(path)
    validate_arrays(midpoint,radius,row,dimension,outputs)
    if path.exists() or path.with_suffix('.json').exists():
        raise FileExistsError('existing row evidence must be preserved')
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.partial.npz')
    np.savez_compressed(temporary,error_mid=midpoint,error_radius=radius,
                       row=np.asarray(row),fingerprint=np.asarray(fingerprint),
                       precision_bits=np.asarray(precision))
    record=dict(row=row,fingerprint=fingerprint,precision_bits=precision,
                dimension=dimension,outputs=outputs,data_SHA256=file_sha(temporary),
                origin=origin,scope='PHYSICAL_HESSIAN_ERROR_ROW_AT_STORED_OPERANDS_ONLY',
                Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    temporary.replace(path)
    metadata=path.with_suffix('.json');temporary_meta=metadata.with_suffix('.partial.json')
    temporary_meta.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    temporary_meta.replace(metadata)


def load_row(path, row, fingerprint, *, dimension=99, outputs=99, precision=256):
    path=Path(path)
    record=json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    expected=dict(row=row,fingerprint=fingerprint,precision_bits=precision,
                  dimension=dimension,outputs=outputs)
    if any(record.get(k)!=v for k,v in expected.items()) or record.get('data_SHA256')!=file_sha(path):
        raise ValueError('row metadata or data hash changed')
    with np.load(path,allow_pickle=False) as source:
        if (int(source['row'])!=row or str(source['fingerprint'].item())!=fingerprint
                or int(source['precision_bits'])!=precision):
            raise ValueError('row internal binding mismatch')
        midpoint=source['error_mid'].copy();radius=source['error_radius'].copy()
    validate_arrays(midpoint,radius,row,dimension,outputs)
    return midpoint,radius,record


def assemble_rows(directory, fingerprint, *, dimension=99, outputs=99, precision=256):
    """Use Hessian symmetry only after every upper-triangular row is present."""
    midpoint=np.full((outputs,dimension,dimension),np.nan);radius=midpoint.copy()
    records=[]
    for row in range(dimension):
        m,r,record=load_row(Path(directory)/f'row_{row:03d}.npz',row,fingerprint,
                            dimension=dimension,outputs=outputs,precision=precision)
        midpoint[:,row,row:]=m;midpoint[:,row:,row]=m
        radius[:,row,row:]=r;radius[:,row:,row]=r
        records.append(record)
    if not np.all(np.isfinite(midpoint)) or not np.all(np.isfinite(radius)):
        raise RuntimeError('full physical Hessian error coverage is required')
    return midpoint,radius,records

"""Reconstruct the exact original time6 NPZ from lossless raw transport chunks."""
from pathlib import Path
from hashlib import sha256
import argparse
import json


def reconstruct(base,run,output):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError(out)
    rel=f'stable_time6_run_{run}/changing_forms.npz'
    recipe=json.loads((base/'exact_archive_reconstruction.json').read_bytes())[rel]
    chunks=[]
    for item in recipe['chunks']:
        raw=(base/item['path']).read_bytes()
        if len(raw)!=item['bytes'] or sha256(raw).hexdigest()!=item['sha256']:
            raise ValueError('Changed chunk: '+item['path'])
        chunks.append(raw)
    raw=b''.join(chunks)
    if len(raw)!=recipe['original_bytes'] or sha256(raw).hexdigest()!=recipe['original_byte_sha256']:
        raise ValueError('Original archive reconstruction failed')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
    print(json.dumps(dict(output=str(out),bytes=len(raw),sha256=sha256(raw).hexdigest())))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=int,choices=(1,2),required=True)
    p.add_argument('--output',required=True);a=p.parse_args()
    reconstruct(Path(__file__).resolve().parent,a.run,a.output)

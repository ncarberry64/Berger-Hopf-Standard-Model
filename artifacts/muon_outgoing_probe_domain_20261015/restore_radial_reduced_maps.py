"""Restore the exact chunked radial reduced maps into an explicit directory."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path


def restore(destination):
    packet=Path(__file__).resolve().parent
    destination=destination.resolve()
    records=json.loads((packet/'radial_reduced_chunk_manifest.json').read_bytes())
    pending=[]
    for record in records:
        parts=[]
        for chunk in record['chunks']:
            source=(packet/chunk['path']).resolve()
            if not source.is_relative_to(packet):raise ValueError('Chunk path leaves packet')
            data=source.read_bytes()
            if len(data)!=chunk['bytes'] or sha256(data).hexdigest()!=chunk['sha256']:
                raise ValueError('Chunk hash or length mismatch')
            parts.append(data)
        data=b''.join(parts)
        if len(data)!=record['bytes'] or sha256(data).hexdigest()!=record['sha256']:
            raise ValueError('Reassembled map hash or length mismatch')
        target=(destination/record['target_relative']).resolve()
        if not target.is_relative_to(destination):raise ValueError('Map path leaves destination')
        if target.exists() and target.read_bytes()!=data:
            raise FileExistsError('Different map already exists: '+str(target))
        pending.append((target,data))
    for target,data in pending:
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        print(json.dumps(dict(path=str(target),bytes=len(data),sha256=sha256(data).hexdigest())))


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('destination',type=Path)
    restore(parser.parse_args().destination)

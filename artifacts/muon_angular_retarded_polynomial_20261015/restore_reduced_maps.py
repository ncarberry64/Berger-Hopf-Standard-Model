"""Verify and restore exact reduced-map archives into an explicit directory."""
import argparse
from hashlib import sha256
import json
from pathlib import Path


def restore(destination):
    """Verify every chunk before writing; refuse to replace different bytes."""
    packet = Path(__file__).resolve().parent
    destination = destination.resolve()
    records = json.loads((packet / 'reduced_maps/chunk_manifest.json').read_text())
    outputs = [('result.json', (packet / 'reduced_maps/result.json').read_bytes())]
    for record in records:
        parts = []
        for chunk in record['chunks']:
            source = (packet / chunk['path']).resolve()
            if not source.is_relative_to(packet):
                raise ValueError('Chunk path leaves this packet')
            data = source.read_bytes()
            if len(data) != chunk['bytes'] or sha256(data).hexdigest() != chunk['sha256']:
                raise ValueError('Chunk hash/length mismatch: ' + chunk['path'])
            parts.append(data)
        data = b''.join(parts)
        if len(data) != record['bytes'] or sha256(data).hexdigest() != record['sha256']:
            raise ValueError('Reassembled archive hash/length mismatch')
        name = record['original_name']
        if Path(name).name != name:
            raise ValueError('Archive name must be a basename')
        outputs.append((name, data))
    for name, data in outputs:
        target = destination / name
        if target.exists() and target.read_bytes() != data:
            raise FileExistsError('Different bytes already exist: ' + str(target))
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in outputs:
        target = destination / name
        target.write_bytes(data)
        print(json.dumps(dict(path=str(target), bytes=len(data), sha256=sha256(data).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    restore(parser.parse_args().destination)

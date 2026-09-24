"""Read-only, bounded-memory index of the cef38b6b DAG; no producer calls."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bhsm.interface.adaptive_expression_reader import read_graph


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--graph', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    digest = hashlib.file_digest(args.graph.open('rb'), 'sha256').hexdigest()
    expected = 'e104d285f142a40dcd307d5a1d6ee633e2b89c3f85ff62aa052041ec572724d9'
    if digest != expected:
        raise ValueError('not the frozen cef38b6b midpoint DAG')
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out / 'receipt.json').exists():
        raise FileExistsError('index already complete')
    with (args.out / 'nodes.jsonl').open('wb') as data, (args.out / 'offsets.bin').open('wb') as offsets:
        def visit(i, node):
            offsets.write(struct.pack('<Q', data.tell()))
            data.write(json.dumps(node, separators=(',', ':')).encode() + b'\n')
            if i % 1000000 == 0:
                print('indexed', i, flush=True)
        metadata = read_graph(args.graph, visit)
        offsets.write(struct.pack('<Q', data.tell()))
    receipt = dict(frozen_checkpoint='cef38b6b', graph_SHA256=digest,
                   node_count=metadata['node_count'], scientific_producers_run=False)
    for name in ('nodes.jsonl', 'offsets.bin'):
        with (args.out / name).open('rb') as f:
            receipt[name] = hashlib.file_digest(f, 'sha256').hexdigest()
    (args.out / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()

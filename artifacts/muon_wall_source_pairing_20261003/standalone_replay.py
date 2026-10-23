"""Replay the new source-pairing/collar-coordinate calculation only.

This packet never evaluates a wall projection, stationary exterior solve
or physical anomaly. It avoids unrelated package initializers.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
import types


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();root=a.packet_root.resolve();output=a.output.resolve()
    for entry in json.loads((root/'bundle_hashes.json').read_text()):
        if hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('changed input '+entry['path'])
    if output.exists():raise FileExistsError('fresh output directory required')
    for name,folder in [('bhsm',root/'src/bhsm'),('bhsm.interface',root/'src/bhsm/interface')]:
        module=types.ModuleType(name);module.__path__=[str(folder)];sys.modules[name]=module
    script=root/'scripts/replay_muon_wall_source_pairing.py'
    sys.argv=[str(script),'--repository',str(root),'--output',str(output)]
    runpy.run_path(str(script),run_name='__main__')


if __name__=='__main__':main()

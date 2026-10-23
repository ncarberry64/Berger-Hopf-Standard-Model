"""Standalone local launcher for the saved BHSM source-jet milestone.

The PR worktree and its retained caches are required. This is not a physical
muon anomaly calculator. A fresh --output is mandatory.
"""
from pathlib import Path
import argparse
import subprocess
import sys

DEFAULT_REPOSITORY=Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,default=DEFAULT_REPOSITORY)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    target=args.repository/'scripts/replay_muon_native_induced_polarization.py'
    if not target.is_file():raise FileNotFoundError(target)
    if args.output.exists():raise FileExistsError('Use a fresh output; preserve all checkpoints')
    raise SystemExit(subprocess.call([sys.executable,str(target),'--output',str(args.output.resolve())],cwd=args.repository))

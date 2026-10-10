"""Local launcher: operator/length-owner reconciliation, NOT a muon number.

Requires the retained PR worktree. Uses only a fresh output directory.
"""
from pathlib import Path
import argparse
import subprocess
import sys

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',type=Path,default=Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    script=a.repository/'scripts/replay_muon_native_impedance_energy_response.py'
    if not script.is_file():raise FileNotFoundError(script)
    if a.output.exists():raise FileExistsError('Use a fresh output; preserve checkpoints')
    raise SystemExit(subprocess.call([sys.executable,str(script),'--output',str(a.output.resolve())],cwd=a.repository))

"""Fresh replay launcher for cutoff derivation; NOT a physical muon number."""
from pathlib import Path
import argparse,subprocess,sys
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',type=Path,default=Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001'))
    p.add_argument('--history-repository',type=Path,default=Path(r'C:\Users\carbe\OneDrive\Documents\CODEX\Berger-Hopf-Standard-Model'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('Fresh output required; preserve prior checkpoints')
    script=a.repository/'scripts/replay_muon_native_support_loss_cutoff.py'
    raise SystemExit(subprocess.call([sys.executable,str(script),'--history-repository',str(a.history_repository),'--output',str(a.output.resolve())],cwd=a.repository))

"""Isolated package-local worker; only a prewritten source-bound request is used."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from bhtracker.photometry_mc import MCWorkspace
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('workspace and exact request SHA256 required')
    MCWorkspace._open_worker(sys.argv[1],sys.argv[2])._execute()

"""Windows source-package launcher; no activation or execution-policy change."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT=Path(__file__).resolve().parents[1]
VERSION='0.2.0rc2'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--no-open',action='store_true',help='run without opening a browser')
    parser.add_argument('--check-install',action='store_true',help='install/check dependencies and exit')
    args=parser.parse_args()
    python=ROOT/'.venv'/'Scripts'/'python.exe'
    env=os.environ.copy()
    for name in ('PYTHONPATH','PYTHONHOME'):env.pop(name,None)
    try:
        if not python.is_file():
            print('Creating the local Python environment...',flush=True)
            venv.create(ROOT/'.venv',with_pip=True)
        check=subprocess.run([str(python),'-I','-c',
            f'import bhtracker,numpy,scipy,matplotlib; assert bhtracker.__version__ == {VERSION!r}'],
            cwd=ROOT,env=env,capture_output=True,text=True)
        if check.returncode:
            print('Installing Blackhole Tracker and its runtime dependencies. First installation needs a package-index network connection.',flush=True)
            subprocess.run([str(python),'-I','-m','pip','install','--upgrade',str(ROOT)],cwd=ROOT,env=env,check=True)
        if args.check_install:
            print('Blackhole Tracker '+VERSION+' installation is ready.',flush=True)
            return 0
        command=[str(python),'-I','-m','bhtracker','serve','--port',str(args.port)]
        if not args.no_open:command.append('--open')
        return subprocess.run(command,cwd=ROOT,env=env).returncode
    except (OSError,subprocess.CalledProcessError) as error:
        print(f'Local setup failed: {error}\nCheck your Python installation and network access for first-install dependencies.\nSee README.md for explicit installation commands.',file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())

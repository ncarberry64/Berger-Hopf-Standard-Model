"""Windows source-package launcher; no activation or execution-policy change."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tomllib
import venv

ROOT=Path(__file__).resolve().parents[1]
VERSION=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--no-open',action='store_true',help='run without opening a browser')
    parser.add_argument('--check-install',action='store_true',help='install/check dependencies and exit')
    parser.add_argument('--astrometry',action='store_true',help='explicitly install/check optional Astropy support for joint research')
    args=parser.parse_args()
    python=ROOT/'.venv'/'Scripts'/'python.exe'
    env=os.environ.copy()
    for name in ('PYTHONPATH','PYTHONHOME'):env.pop(name,None)
    try:
        if not python.is_file():
            print('Creating the local Python environment...',flush=True)
            venv.create(ROOT/'.venv',with_pip=True)
        check=subprocess.run([str(python),'-I','-c',
            f'import bhtracker,numpy,scipy,matplotlib; assert bhtracker.__version__ == {VERSION!r}'+('; import astropy' if args.astrometry else '')],
            cwd=ROOT,env=env,capture_output=True,text=True)
        if check.returncode:
            print('Installing Blackhole Tracker'+(' with explicitly requested optional Astropy support' if args.astrometry else ' and its runtime dependencies')+'. First installation needs a package-index network connection.',flush=True)
            requirement=str(ROOT)+('[astrometry]' if args.astrometry else '')
            subprocess.run([str(python),'-I','-m','pip','install','--upgrade',requirement],cwd=ROOT,env=env,check=True)
        if args.check_install:
            print('Blackhole Tracker '+VERSION+' installation is ready'+(' with optional joint astrometry support.' if args.astrometry else '.'),flush=True)
            if not args.astrometry:
                print('Joint research requires optional Astropy. Explicitly enable it with Start_Blackhole_Tracker_Joint.cmd or --astrometry.',flush=True)
            return 0
        command=[str(python),'-I','-m','bhtracker','serve','--port',str(args.port)]
        if not args.no_open:command.append('--open')
        return subprocess.run(command,cwd=ROOT,env=env).returncode
    except (OSError,subprocess.CalledProcessError) as error:
        print(f'Local setup failed: {error}\nCheck your Python installation and network access for first-install dependencies.\nSee README.md for explicit installation commands.',file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())

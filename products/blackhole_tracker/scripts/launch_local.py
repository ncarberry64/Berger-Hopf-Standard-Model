"""Windows source-package launcher; no activation or execution-policy change."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib
import venv

ROOT=Path(__file__).resolve().parents[1]
VERSION=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
OWNER_FILE='.bhsm-tracker-environment.json'

def environment_path(explicit=None):
    if explicit is not None:return Path(explicit).expanduser().resolve()
    local=os.environ.get('LOCALAPPDATA')
    if not local:raise ValueError('LOCALAPPDATA is unavailable; choose a fresh short path with --environment PATH.')
    source_id=hashlib.sha256(str(ROOT.resolve()).encode('utf-8')).hexdigest()[:8]
    safe_version=''.join(char if char.isalnum() or char in '.-' else '_' for char in VERSION)
    return (Path(local)/'BHSM'/'e'/f'{safe_version}-{source_id}-py{sys.version_info.major}{sys.version_info.minor}').resolve()

def ownership(directory):
    return {'schema':'bhsm.local_environment.v1','application':'bhsm-blackhole-tracker',
      'source_root':str(ROOT.resolve()),'environment':str(directory.resolve()),'package_version':VERSION,
      'python_major_minor':[sys.version_info.major,sys.version_info.minor]}

def owned_environment(directory):
    """Never adopt, clear or overwrite an unrelated existing environment."""
    if directory.is_symlink():raise ValueError('Environment symlinks are not owned setup targets.')
    marker=directory/OWNER_FILE;expected=ownership(directory)
    if directory.exists():
        if not directory.is_dir() or not marker.is_file():raise ValueError('Existing environment is unowned; it was preserved. Choose a fresh --environment PATH.')
        saved=json.loads(marker.read_text(encoding='utf-8'))
        if not isinstance(saved,dict):raise ValueError('Environment ownership record must be a JSON object; existing files were preserved.')
        if any(saved.get(key)!=value for key,value in expected.items()):raise ValueError('Environment ownership/version/source differs; existing files were preserved.')
    else:
        directory.parent.mkdir(parents=True,exist_ok=True);directory.mkdir(exist_ok=False)
        with marker.open('x',encoding='utf-8') as stream:json.dump(expected,stream,sort_keys=True);stream.write('\n')
        saved=expected
    return marker,saved

def source_signature():
    digest=hashlib.sha256()
    files=[ROOT/'pyproject.toml']+sorted(path for path in (ROOT/'bhtracker').rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc')
    for path in files:
        digest.update(path.relative_to(ROOT).as_posix().encode('utf-8')+b'\0')
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
        digest.update(b'\0')
    return digest.hexdigest()

def dependency_probe(*,astrometry=False,joint_research=False):
    code=f'import bhtracker,numpy,scipy,matplotlib; assert bhtracker.__version__ == {VERSION!r}'
    if astrometry or joint_research:code+='; import astropy; import importlib.metadata; assert int(importlib.metadata.version("astropy").split(".",1)[0]) >= 6; from astropy.io import fits; from astropy.io.fits.hdu.compressed import _compression'
    if joint_research:code+='; import celerite2; import importlib.metadata; assert importlib.metadata.version("celerite2") == "0.3.3"'
    return code

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--no-open',action='store_true',help='run without opening a browser')
    parser.add_argument('--check-install',action='store_true',help='install/check dependencies and exit')
    parser.add_argument('--astrometry',action='store_true',help='explicitly install/check optional Astropy support for joint research')
    parser.add_argument('--joint-research',action='store_true',help='explicitly install/check Astropy FITS and celerite2 support for the experimental known-system engine')
    parser.add_argument('--environment',type=Path,help='fresh or launcher-owned short environment path; unrelated existing environments are preserved')
    parser.add_argument('--page',choices=['resolved','photometry','photometry-mc','joint','atlas','spectrum','skytrack'],default='resolved')
    args=parser.parse_args(argv)
    env=os.environ.copy()
    for name in ('PYTHONPATH','PYTHONHOME'):env.pop(name,None)
    try:
        directory=environment_path(args.environment);marker,owner=owned_environment(directory)
        python=directory/'Scripts'/'python.exe'
        print('Python environment: '+str(directory),flush=True)
        if not python.is_file():
            print('Creating the local Python environment...',flush=True)
            venv.create(directory,with_pip=True)
        probe=[str(python),'-I','-c',dependency_probe(astrometry=args.astrometry,joint_research=args.joint_research)]
        signature=source_signature()
        check=subprocess.run(probe,cwd=ROOT,env=env,capture_output=True,text=True)
        if check.returncode or owner.get('installed_source_sha256')!=signature:
            extra='joint-research' if args.joint_research else 'astrometry' if args.astrometry else None
            print('Installing Blackhole Tracker'+(' with explicitly requested '+extra+' support' if extra else ' and its runtime dependencies')+'. First installation needs a package-index network connection.',flush=True)
            requirement=str(ROOT)+('['+extra+']' if extra else '')
            subprocess.run([str(python),'-I','-m','pip','install','--upgrade',requirement],cwd=ROOT,env=env,check=True)
            check=subprocess.run(probe,cwd=ROOT,env=env,capture_output=True,text=True)
            if check.returncode:raise RuntimeError('Installed dependency check failed: '+check.stderr.strip())
            owner={**owner,'installed_source_sha256':signature}
            temporary=marker.with_name(marker.name+'.tmp')
            with temporary.open('x',encoding='utf-8') as stream:json.dump(owner,stream,sort_keys=True);stream.write('\n')
            temporary.replace(marker)
        if args.check_install:
            print('Blackhole Tracker '+VERSION+' installation is ready'+(' with optional joint-research support.' if args.joint_research else ' with optional joint astrometry support.' if args.astrometry else '.'),flush=True)
            if not (args.astrometry or args.joint_research):
                print('Joint astrometry requires --astrometry; the experimental known-system engine requires --joint-research. Both are explicit optional installs.',flush=True)
            return 0
        command=[str(python),'-I','-m','bhtracker','serve','--port',str(args.port),'--page',args.page]
        if not args.no_open:command.append('--open')
        return subprocess.run(command,cwd=ROOT,env=env).returncode
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as error:
        print(f'Local setup failed: {error}\nCheck your Python installation and network access for first-install dependencies.\nSee README.md for explicit installation commands.',file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())

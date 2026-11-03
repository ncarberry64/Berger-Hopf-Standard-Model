"""Sequential, isolated reproduction from frozen inputs; no repository imports.

Run with Python -I -S and explicitly supplied trusted site-packages directories.
No .pth processing, PYTHONPATH, user startup, pytest plugins or conftest is used.
This bounds imports; it is not a security certification of supplied packages.
"""
import sys
if not(sys.flags.isolated and sys.flags.no_site and sys.flags.no_user_site):
    raise RuntimeError('Run with Python -I -S')
from pathlib import Path
PREFIX=Path(sys.base_prefix).resolve()
def under(p,r):return p==r or r in p.parents
for entry in sys.path:
    if not entry or not under(Path(entry).resolve(),PREFIX):raise RuntimeError('Unexpected startup import path')
import argparse,json,os,subprocess,importlib,importlib.machinery
from hashlib import sha256
HERE=Path(__file__).resolve().parent
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site-packages',type=Path,action='append',required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--stage');p.add_argument('--mode',choices=['all','produce','tests'],default='all')
    args=p.parse_args();out=args.out.resolve()
    manifest=json.loads((HERE/'release_manifest.json').read_text())
    for f in manifest['files']:
        if digest(HERE/f['path'])!=f['sha256']:raise RuntimeError('Release file hash mismatch: '+f['path'])
    roots=[x.resolve() for x in args.site_packages]
    if not all(x.is_dir() for x in roots):raise RuntimeError('Explicit trusted package directories required')
    stages={s['stage']:s for s in manifest['stages']}
    if args.mode=='all':
        if out.exists():raise FileExistsError('Use a fresh output directory')
        out.mkdir(parents=True);rows=[]
        for stage in stages:
            for mode in ('produce','tests'):
                argv=[sys.executable,'-I','-S',str(Path(__file__).resolve()),'--stage',stage,'--mode',mode,'--out',str(out/stage)]
                for root in roots:argv.extend(['--site-packages',str(root)])
                run=subprocess.run(argv,capture_output=True,text=True)
                (out/(stage+'_'+mode+'.log')).write_text(run.stdout+run.stderr,encoding='utf-8')
                if run.returncode:raise RuntimeError(stage+' '+mode+' failed; inspect its local log')
                rows.append(json.loads(run.stdout.splitlines()[-1]))
                print(json.dumps(dict(stage=stage,mode=mode,passed=True)),flush=True)
        summary=dict(schema='bhsm.muon-release-reproduction.v1',all_passed=True,rows=rows,
            worker_count=1,new_history_or_heat_campaign=False,physical_prediction=False)
        (out/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        return
    if args.stage not in stages:raise ValueError('Known release stage required')
    stage=HERE/args.stage
    allowed=[PREFIX,*roots,stage]
    class BoundedFinder(importlib.machinery.PathFinder):
        @classmethod
        def find_spec(cls,fullname,path=None,target=None):
            spec=super().find_spec(fullname,path,target)
            if spec:
                locations=[]
                if spec.origin and spec.origin not in ('built-in','frozen'):locations.append(spec.origin)
                if spec.submodule_search_locations:locations.extend(spec.submodule_search_locations)
                if any(not any(under(Path(x).resolve(),r) for r in allowed) for x in locations):
                    raise ImportError('Import outside explicit roots blocked: '+fullname)
            return spec
    sys.meta_path[:]=[BoundedFinder if x is importlib.machinery.PathFinder else x for x in sys.meta_path]
    sys.path.extend(str(r) for r in roots)
    os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    for name in ('PYTEST_ADDOPTS','PYTEST_PLUGINS'):os.environ.pop(name,None)
    for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
    sys.dont_write_bytecode=True
    import numpy,pytest
    sys.path.append(str(stage))
    module=stages[args.stage]['module'];out.mkdir(parents=True,exist_ok=True)
    if args.mode=='produce':
        target=out/'calculation';sys.argv=[module,'--out',str(target)]
        importlib.import_module(module).main()
        if (target/'result.json').read_bytes()!=(stage/'expected_result.json').read_bytes():
            raise AssertionError('Final result differs from verified checkpoint')
        # The only shipped binaries are frozen evidence. Reject object arrays
        # and inspect string metadata rather than permitting pickle loading.
        arrays=0
        for archive in stage.rglob('*.npz'):
            with numpy.load(archive,allow_pickle=False) as data:
                for key in data.files:
                    a=data[key];arrays+=1
                    if a.dtype.hasobject:raise AssertionError('Object array is not permitted')
        row=dict(stage=args.stage,mode='produce',passed=True,result_byte_identical=True,
                 inspected_frozen_arrays=arrays,result_sha256=digest(target/'result.json'))
    else:
        code=pytest.main(['--noconftest','-q','-p','no:cacheprovider','-c',str(HERE/'pytest.ini'),
            '--rootdir',str(stage),str(stage/('test_'+module+'.py')),'--junitxml',str(out/'tests.xml')])
        if code:raise SystemExit(code)
        import xml.etree.ElementTree as ET
        suite=ET.parse(out/'tests.xml').getroot().find('testsuite')
        row=dict(stage=args.stage,mode='tests',passed=True,tests=int(suite.attrib['tests']))
    for name,m in tuple(sys.modules.items()):
        file=getattr(m,'__file__',None)
        if file and not file.startswith('<'):
            q=Path(file).resolve()
            if q!=Path(__file__).resolve() and not any(under(q,r) for r in allowed):raise RuntimeError('Unexpected loaded origin: '+name)
    row.update(numpy=numpy.__version__,pytest=pytest.__version__,python=sys.version.split()[0],imports_bounded=True)
    print(json.dumps(row))
if __name__=='__main__':main()

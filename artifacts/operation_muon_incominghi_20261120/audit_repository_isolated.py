"""Run owned audits with inspected imports and an isolated CLI child."""
import sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and sys.flags.no_user_site
import argparse, contextlib, io, json, os, runpy, subprocess
p=argparse.ArgumentParser()
p.add_argument('--repo',required=True)
p.add_argument('--site-packages',required=True)
p.add_argument('--output')
p.add_argument('--cli-help',action='store_true')
a=p.parse_args()
root=Path(a.repo).resolve();runtime=Path(sys.base_prefix).resolve();site=Path(a.site_packages).resolve()
assert site.is_relative_to(runtime) and site.name=='site-packages'
assert all(Path(x).resolve().is_relative_to(runtime) for x in sys.path)
sys.dont_write_bytecode=True
sys.path[:0]=[str(root/'src'),str(site)]
for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
if sys.platform=='win32':
    import platform,sysconfig
    w=sys.getwindowsversion();arch={'win-amd64':'AMD64','win-arm64':'ARM64','win32':'x86'}[sysconfig.get_platform()]
    platform._uname_cache=platform.uname_result('Windows','',f'{w.major}.{w.minor}',f'{w.major}.{w.minor}.{w.build}',arch)
real_run=subprocess.run
child=[sys.executable,'-I','-S',str(Path(__file__).resolve()),'--repo',str(root),'--site-packages',str(site),'--cli-help']
def bounded_run(argv,*args,**kwargs):
    if argv==[sys.executable,'-m','bhsm.interface','--help']:
        argv=child
    elif argv!=['git','ls-files']:
        raise RuntimeError('Unapproved subprocess')
    return real_run(argv,*args,**kwargs)
subprocess.run=bounded_run
def hook(event,details):
    if event in ('os.system','socket.connect','socket.getaddrinfo'):raise RuntimeError(event)
    if event=='subprocess.Popen':
        argv=details[1]
        allowed=any(argv==cmd or argv==subprocess.list2cmdline(cmd) for cmd in (['git','ls-files'],child))
        if not allowed:raise RuntimeError('Unapproved child process')
sys.addaudithook(hook)
def check_imports():
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            loc=Path(name).resolve()
            assert loc.is_relative_to(runtime) or loc.is_relative_to(root) or loc==Path(__file__).resolve(),str(loc)
if a.cli_help:
    sys.argv=['bhsm.interface','--help']
    try:runpy.run_module('bhsm.interface',run_name='__main__')
    finally:check_imports()
else:
    outputs={}
    for file in ('audit_bhsm_status.py','audit_forbidden_claims.py','audit_frozen_prediction_integrity.py','verify_precision.py','audit_public_readiness.py'):
        sys.argv=[str(root/'tools'/file)]+(['--format','json'] if file=='audit_public_readiness.py' else [])
        out=io.StringIO();err=io.StringIO();code=0
        try:
            with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
                runpy.run_path(str(root/'tools'/file),run_name='__main__')
        except SystemExit as e:code=e.code or 0
        except Exception as e:code=1;err.write(type(e).__name__+': '+str(e))
        outputs[file]=dict(exit_code=code,stdout=out.getvalue(),stderr=err.getvalue())
        print(file+': '+str(code),flush=True)
    check_imports()
    Path(a.output).write_bytes((json.dumps(outputs,indent=2)+'\n').encode('utf-8'))

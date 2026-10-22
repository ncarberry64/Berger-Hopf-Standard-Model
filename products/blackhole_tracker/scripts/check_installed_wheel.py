"""Execute a wheel in a fresh dependency-resolved venv, outside the checkout.

This driver uses only the standard library. Its probe is copied into a temporary
directory with spaces; isolated Python cannot import the developer checkout.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

PROBE = r'''
import hashlib, json, os, pathlib, queue, subprocess, sys, threading, urllib.request
import bhtracker
from bhtracker.examples import make_example
from bhtracker.data import load_dataset
from bhtracker.inference import fit
root = pathlib.Path(bhtracker.__file__).resolve().parent
assert pathlib.Path(sys.prefix).resolve() in root.parents, str(root)
assert root.parent != pathlib.Path.cwd(), str(root)
assert (root/'web/index.html').is_file()
assert (root/'web/app.js').stat().st_size > 100
pins=[]
for manifest in (root/'theory').rglob('*.json'):
    # All package files are hashed below; runtime checks exercise the pinned providers.
    pins.append(str(manifest.relative_to(root)))
assert len(pins) >= 2
for manifest_name,list_key,base in [('provider/SOURCE_MANIFEST.json','files','provider/'),
                                  ('BHSM_INTERPRETATION_MANIFEST.json','sources','')]:
    manifest=json.loads((root/'theory'/manifest_name).read_text())
    for entry in manifest[list_key]:
        assert hashlib.sha256((root/'theory'/base/entry['path']).read_bytes()).hexdigest()==entry['sha256']
raw, truth = make_example('nearby_motion')
d = load_dataset(raw)
assert len(d.epochs) >= 3
pathlib.Path('input.json').write_text(json.dumps(raw),encoding='utf8')
result = fit(raw, family='gr', starts=1)
assert result['status'] == 'TRACKED', result['diagnostics']
assert result['bhsm_interpretation']['spherical_boundary']['status'] == 'AVAILABLE'
meaning=result['bhsm_interpretation']
assert meaning['interpretation_schema_version']==2
assert meaning['core_surface']['status']=='PROPOSED_NOT_INFERRED'
assert meaning['core_surface']['core_parameters_fitted'] is False
assert all(v['value'] is None for v in meaning['core_surface']['unavailable_quantities'].values())
assert json.loads((root/'theory'/meaning['source_provenance']['interpretation_contract_path']).read_text(encoding='utf8'))==meaning['core_surface']
# Exercise the conditional provider and its packaged action/source pins.
r1 = fit(raw, family='r1', starts=1, max_nfev=30)
assert r1['model']['family'] == 'r1'
commands=[['example','nearby_motion','--output','cli-input.json'],
          ['validate','cli-input.json'],
          ['fit','cli-input.json','--starts','1','--output','cli analysis'],
          ['replay','cli analysis','--output','CLI replay']]
for args in commands:
    subprocess.run([sys.executable,'-I','-m','bhtracker',*args],check=True,
                   stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
saved=json.loads(pathlib.Path('cli analysis/result.json').read_text())
assert saved['data_summary']['sha256'] == result['data_summary']['sha256']
import numpy as np
np.testing.assert_allclose(saved['predictions'],result['predictions'],rtol=2e-11,atol=2e-11)
assert saved['bhsm_interpretation']==result['bhsm_interpretation']
assert json.loads(pathlib.Path('CLI replay/replay_check.json').read_text())['passed']
from bhtracker.report import export_analysis_bundle, replay_analysis
pathlib.Path('analysis.zip').write_bytes(export_analysis_bundle(result))
assert replay_analysis('analysis.zip','API replay')['passed']
proc=subprocess.Popen([sys.executable,'-I','-u','-m','bhtracker','serve','--port','0'],
                      stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
lines=queue.Queue()
def reader():
    for line in proc.stdout: lines.put(line)
threading.Thread(target=reader,daemon=True).start()
try:
    line=lines.get(timeout=40)
    assert 'ready at http://127.0.0.1:' in line,line
    url=line.split('ready at ',1)[1].strip()
    for endpoint in ('api/health','','app.js','style.css','api/examples/nearby_motion','api/examples/nearby_motion/bundle'):
        with urllib.request.urlopen(url+endpoint,timeout=10) as response:
            assert response.status == 200
            assert len(response.read()) > 0
finally:
    proc.terminate()
    try: proc.wait(timeout=10)
    except subprocess.TimeoutExpired: proc.kill();proc.wait()
from importlib.metadata import version
receipt={'status':'passed','python':sys.version,'executable':sys.executable,
 'package_path':str(root),'cwd':str(pathlib.Path.cwd()),'isolated':bool(sys.flags.isolated),
 'version':version('bhsm-blackhole-tracker'),
 'dependencies':{n:version(n) for n in ('numpy','scipy','matplotlib')},
 'checks':['fresh venv with resolved dependencies','outside-checkout isolated import',
 'packaged assets/examples','GR and R1 runtime providers','API/CLI prediction agreement',
 'CLI example validate fit export and replay','API ZIP export and replay',
 'six R1 and BHSM source pin checks','actual loopback HTTP startup and complete example download'],
 'packaged_files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
  for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}}
pathlib.Path('receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
'''

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--wheel-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--keep-work',action='store_true')
    a=p.parse_args()
    wheels=list(a.wheel_dir.resolve().glob('*.whl'))
    if len(wheels)!=1:p.error('wheel-dir must contain exactly one wheel')
    work=Path(tempfile.mkdtemp(prefix='bhtracker clean wheel '))
    output=a.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    for name in ('PYTHONPATH','PYTHONHOME'):env.pop(name,None)
    env.update(PYTHONNOUSERSITE='1',MPLBACKEND='Agg',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    receipt={'status':'failed','work_directory':str(work),'wheel':str(wheels[0])}
    try:
        venv.create(work/'venv',with_pip=True)
        python=work/'venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        install=subprocess.run([str(python),'-I','-m','pip','install',str(wheels[0])],
                               cwd=work,env=env,text=True,capture_output=True,timeout=600)
        receipt['installation_log']=install.stdout+install.stderr
        install.check_returncode()
        (work/'probe.py').write_text(PROBE,encoding='utf8')
        probe=subprocess.run([str(python),'-I',str(work/'probe.py')],cwd=work,env=env,
                             text=True,capture_output=True,timeout=600)
        receipt['probe_log']=probe.stdout+probe.stderr
        probe.check_returncode()
        receipt.update(json.loads((work/'receipt.json').read_text()))
    finally:
        output.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
        print(str(output),flush=True)
        if not a.keep_work:
            import shutil
            shutil.rmtree(work)

if __name__=='__main__':main()

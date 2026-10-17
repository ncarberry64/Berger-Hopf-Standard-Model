"""Replay verified source controls and canonical port; write atomic evidence.

Reproduction: PYTHONPATH=src python scripts/evaluate_electromagnetic_carrier_mode_reduction.py --output-dir <new-directory>
No physical reference, collider state, terminal derivative or moment is selected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
import scipy
import sympy

from bhsm.interface.electromagnetic_carrier_mode_reduction import exact_checks, numerical_checks

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts/electromagnetic_carrier_reduction_20261016'
PACKAGES={
    'electromagnetic':('BHSM_electromagnetic_carrier_reduction_20261016','check_carrier_reduction.py','verification.json'),
    'operator':('BHSM_operator_reference_construction_20261016','verify_constructions.py','SHA256SUMS.json'),
    'scalar':('BHSM_scalar_reference_continuation_20261016','continue_operator_reference.py','SHA256SUMS.json'),
}


def atomic_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_bytes((json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
    temp.replace(path)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def differences(a,b,path=''):
    """Report exact JSON differences, with absolute differences for numbers."""
    out=[]
    if isinstance(a,dict) and isinstance(b,dict):
        for k in sorted(a.keys()|b.keys()):
            if k not in a or k not in b: out.append({'path':path+'/'+k,'historical':a.get(k),'fresh':b.get(k)})
            else: out.extend(differences(a[k],b[k],path+'/'+k))
    elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        for i,(x,y) in enumerate(zip(a,b)): out.extend(differences(x,y,f'{path}/{i}'))
    elif a!=b:
        item={'path':path,'historical':a,'fresh':b}
        if isinstance(a,(int,float)) and isinstance(b,(int,float)): item['absolute_difference']=abs(a-b)
        out.append(item)
    return out


def source_replay(label,package,script,manifest_name,output):
    archive=ART/'source_handoff/sources'/f'{package}.zip'
    provenance=json.loads((ART/'SOURCE_MAP.json').read_text())
    expected=provenance['source_archives'][archive.name]
    if sha(archive.read_bytes())!=expected: raise ValueError(f'archive hash mismatch: {archive}')
    with zipfile.ZipFile(archive) as z:
        names=[name for name in z.namelist() if not name.endswith('/')]
        if len({Path(n).name for n in names})!=len(names):
            raise ValueError('duplicate flattened archive members')
        contents={Path(name).name:z.read(name) for name in names}
    if manifest_name not in contents: raise ValueError('required source manifest absent')
    # Source receipts use different manifest filenames. Verify every advertised
    # file hash again; the archive itself was checked against supplied manifests.
    manifests=[(n,json.loads(v)) for n,v in contents.items() if n.endswith('.json') and ('manifest' in n.lower() or n in ('verification.json','SHA256SUMS.json'))]
    checked={}
    for name,m in manifests:
        hashes=m.get('file_sha256',m.get('sha256',m.get('files',m)))
        if isinstance(hashes,dict):
            for n,h in hashes.items():
                if isinstance(h,dict): h=h.get('sha256')
                if isinstance(h,str) and len(h)==64:
                    if Path(n).name not in contents: raise ValueError(f'hashed member absent: {n}')
                    if sha(contents[Path(n).name])!=h: raise ValueError(f'inner hash mismatch: {n}')
                    checked[n]=h
    script_sha=sha(contents[script])
    if script_sha!=provenance['source_scripts'][label]['sha256']: raise ValueError('source script mismatch')
    with tempfile.TemporaryDirectory(prefix='bhsm_carrier_control_') as temp:
        source=Path(temp)/script
        source.write_bytes(contents[script])
        dest=(output/'source_controls'/label/'result.json').resolve()
        dest.parent.mkdir(parents=True,exist_ok=True)
        run=subprocess.run([sys.executable,str(source),'--output',str(dest)],capture_output=True,text=True)
        if run.returncode: raise RuntimeError(f'{label} failed: {run.stdout}\n{run.stderr}')
        fresh=dest.read_bytes()
    historical_names=sorted(n for n in contents if n.endswith('.json') and ('run_1' in n or 'run1' in n))
    if not historical_names:
        historical_names=sorted(n for n in contents if n.endswith('.json') and n not in [p[0] for p in manifests])[:1]
    if not historical_names: raise ValueError('missing historical result receipt')
    historical=contents[historical_names[0]]
    return {'archive_sha256':sha(archive.read_bytes()),'source_script_sha256':script_sha,
            'verified_inner_file_count':len(checked),'fresh_sha256':sha(fresh),
            'historical_result_file':historical_names[0],'historical_sha256':sha(historical),
            'historical_bytes_identical':fresh==historical,
            'historical_json_differences':differences(json.loads(historical),json.loads(fresh)),
            'fresh_result':str(dest.relative_to(output.resolve()))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True,type=Path)
    args=parser.parse_args()
    out=args.output_dir.resolve()
    symbolic=exact_checks(); numerical=numerical_checks()
    source={label:source_replay(label,*spec,out) for label,spec in PACKAGES.items()}
    primary=json.loads((out/source['electromagnetic']['fresh_result']).read_text())
    if symbolic!=primary['symbolic'] or numerical!=primary['numerical']:
        raise ValueError('canonical controls differ from unmodified source controls')
    result={'classification':'EXACT_CONTROL_AND_CONDITIONAL_MATHEMATICS',
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'sympy':sympy.__version__},
        'symbolic':symbolic,'numerical':numerical,'source_replays':source,
        'canonical_equals_unmodified_source_json_controls':True,
        'erratum':'Unrestricted CAR optimizer retains tiny nonzero eigenvalues; original source archive unchanged.',
        'physical_status':{'matching_guard':2e-10,'physical_packets':False,'physical_reference_selected':False,
            'physical_carrier_domain_completed':False,'full_outgoing_derivative_passed':False,
            'coupled_corrections_applied':0,'fresh_adopted_preparation_Maxwell':None,
            'fresh_adopted_preparation_226_rows':None,'a_mu':None,'g_mu':None,'total_uncertainty':None},
        'producer_sha256':sha(Path(__file__).read_bytes()),
        'module_sha256':sha((ROOT/'src/bhsm/interface/electromagnetic_carrier_mode_reduction.py').read_bytes())}
    atomic_json(out/'result.json',result)
    print(json.dumps({'symbolic_groups':symbolic['group_count'],'numerical_groups':numerical['group_count'],'source_replays':list(source)}))


if __name__=='__main__':
    main()

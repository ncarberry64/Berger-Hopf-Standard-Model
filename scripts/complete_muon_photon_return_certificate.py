"""Certify final returned-current multiplication without repeating any solve."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_native_photon_response import certify_frozen_component


def run(inputs,output):
    if output.exists():raise FileExistsError('Use a fresh certificate output')
    output.mkdir(parents=True)
    start=time.perf_counter()
    with np.load(inputs/'component_action_and_current.npz') as z:
        data={k:np.array(z[k]) for k in z.files}
    result=json.loads((inputs/'result.json').read_text())
    action=dict(K_per_kappa1=data['K_per_kappa1'],M_geometric_scalar=float(data['M_geometric_scalar']))
    current=dict(dual_current_basis=data['dual_current_basis'],mode_current_covector=data['mode_current_covector'])
    certs=[]
    for i,row in enumerate(result['shifts']):
        with np.load(inputs/f'response_{i}.npz') as z:
            record={k:np.array(z[k]) for k in z.files}
        record['zeta_over_kappa1']=row['zeta_over_kappa1']
        cert=certify_frozen_component(action,current,record)
        cert['zeta_over_kappa1']=row['zeta_over_kappa1']
        certs.append(cert)
        (output/f'certificate_{i}.json').write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
    receipt=dict(scope='Completes final current-return rounding bounds and per-column relative residuals; no solve or source action repeated',
        certificates=certs,inputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs.iterdir() if p.is_file()},
        implementation_sha256=hashlib.sha256((ROOT/'src/bhsm/interface/muon_native_photon_response.py').read_bytes()).hexdigest(),
        new_shifted_solves=0,elapsed_seconds=time.perf_counter()-start)
    (output/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(output),max_consumed_bound=max(c['current_return_frobenius_error_upper'] for c in certs),
        max_relative_residual=max(x for c in certs for x in c['current_residual_relative_upper'] if x is not None),new_solves=0)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.input,a.output)

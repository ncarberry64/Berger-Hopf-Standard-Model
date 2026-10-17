"""Apply the magnetic causal source Hessian without a padded inverse."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_magnetic_source_photon_action import executed_magnetic_photon_quadratic_action
from evaluate_muon_native_product_factor_graph import serial,deterministic_npz


def materialize(response,output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve executed source action')
    a=executed_magnetic_photon_quadratic_action(response,repository=ROOT)
    arrays={k:v for k,v in a.items() if isinstance(v,np.ndarray)}
    A=arrays['source_quadratic_action']
    if np.any(A[3:]) or np.any(A[:,3:]):raise ValueError('exact active-axis restriction failed')
    result={k:v for k,v in a.items() if k not in arrays}
    result.update(classification='EVALUATED_CAUSAL_MAGNETIC_THREE_AXIS_SOURCE_ACTION',
        active_source_eigenvalues=np.linalg.eigvalsh(A[:3,:3]).tolist(),
        action_hessian_unhalved=True,complete_bilocal_photon_or_Pauli_application=False)
    for name in ('src/bhsm/interface/muon_magnetic_source_photon_action.py',Path(__file__).relative_to(ROOT).as_posix()):
        result['input_hashes'][name]=sha256((ROOT/name).read_bytes()).hexdigest()
    out.mkdir(parents=True);data=deterministic_npz(arrays);(out/'response.npz').write_bytes(data)
    result['archive']=dict(path='response.npz',bytes=len(data),sha256=sha256(data).hexdigest())
    (out/'result.json').write_text(json.dumps(serial(result),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--response',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.response,a.output),sort_keys=True))

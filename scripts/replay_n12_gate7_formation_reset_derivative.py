"""Independent residual secants at new nearby points; numerical AD cross-check only."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from certify_n12_gate7_coupled_center_neighborhood import load
from certify_n12_c2_refined_reset_root_center import _augmented_residual
from audit_n12_finite_terminal_directed_center import _normalization_coordinates
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded


def calculate(source,out):
    source=Path(source).resolve();out=Path(out)
    base=ROOT/'artifacts/flagship_integration'
    candidate=base/'gate7_current_reset_connection_20260927/reset_match_complete/candidate.npz'
    with np.load(candidate) as z:state=z['joint_state_raw'];w=np.tile(z['state_weights'],2);ref=z['branch_reference']
    with np.load(base/'BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER_DATA.npz') as z:scale=float(z['child_gradient_scale'])
    ordered=json.loads((ROOT/'artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json').read_bytes())['ordered_scale']
    normq=_normalization_coordinates();a=load(source/'arrays.npz')
    J=np.array([float(v.mid()) for v in a['terminal_reset_J'].flat]).reshape(58,196)
    kernel=np.array([float(v.mid()) for v in a['incoming_kernel_basis_numerical'].flat]).reshape(98,66)
    directions={};d=np.zeros(196);d[98]=1;directions['incoming_configuration_coordinate']=d
    directions['incoming_reset_kernel_direction']=np.r_[np.zeros(98),kernel[:,0]]
    rows=[]
    for name,d in directions.items():
        for exponent in (18,19):
            h=2.**-exponent
            plus=state+h*d/w;minus=state-h*d/w
            fp=_augmented_residual(plus,w[:98],ref,float(ordered),normq,scale)
            fm=_augmented_residual(minus,w[:98],ref,float(ordered),normq,scale)
            secant=(fp-fm)/(2*h)
            # Bind the derivative comparison to the actual rounded sample displacement.
            actual_direction=(plus-minus)*w/(2*h)
            expected=J@actual_direction
            rows.append(dict(direction=name,step=h,secant_norm=float(np.linalg.norm(secant)),
                derivative_norm=float(np.linalg.norm(expected)),
                difference_norm=float(np.linalg.norm(secant-expected)),
                relative_difference=float(np.linalg.norm(secant-expected)/max(1.,np.linalg.norm(expected)))))
            print(rows[-1],flush=True)
    report=dict(scope='Numerical first-derivative cross-check; no certificate tolerance or stationarity inference',
        samples=rows,source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in (source/'arrays.npz',candidate,Path(__file__))},
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    out.mkdir(parents=True,exist_ok=False);(out/'report.json').write_bytes(encoded(report))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();calculate(a.source,a.out)

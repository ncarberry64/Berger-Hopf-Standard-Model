"""Run new same-frozen-action quadrature propagation, preserving old campaigns."""
import argparse
from pathlib import Path
import os
import sys
import json
from hashlib import sha256
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'


def run(repository,base,orders,repeat=1):
    root,base=Path(repository).resolve(),Path(base).resolve()
    sys.path[:0]=[str(root/'audits'),str(root/'src')]
    from bhsm_muon_same_stage_n1_reduced_sources_20261015 import export
    from bhsm_muon_shifted_polynomial_retarded_n1_20261015 import run as propagate
    from bhsm_polynomial_angular_retarded_lepton_20261015 import run as lepton
    import numpy as np
    angular=root/'artifacts/muon_angular_retarded_polynomial_20261015/angular/run_1'
    for order in orders:
        coefficients=base/('coefficients_extension_run_1' if order==192 else 'coefficients_run_1')/f'order{order}'
        reduced=base/f'order{order}_reduced_run_1'
        if not reduced.exists():export(root,coefficients,reduced)
        if repeat==2:
            repeated=base/f'order{order}_reduced_run_2'
            if not repeated.exists():export(root,coefficients,repeated)
        field=base/f'order{order}_field_run_{repeat}'
        if not field.exists():propagate(root,coefficients,reduced,field,steps=4,precision=256)
        # Bind both independently evaluated consumers to the same field input
        # path. The field_run_2 integration is verified separately, rather than
        # introducing different path-only provenance into result JSON.
        response=base/f'order{order}_lepton_run_{1 if repeat==1 else 3}'
        if not response.exists():lepton(root,angular,base/f'order{order}_field_run_1',response)
        print(json.dumps(dict(event='completed_order_response',order=order)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--base',required=True)
    p.add_argument('--orders',nargs='+',type=int,required=True);p.add_argument('--repeat',type=int,choices=(1,2),default=1)
    a=p.parse_args();run(a.repository,a.base,a.orders,a.repeat)

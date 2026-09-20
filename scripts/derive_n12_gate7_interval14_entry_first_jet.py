"""Recover the 73<-14 entry's linear state dependence from frozen Hessians."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from flint import arb, ctx


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bound(x):
    return dict(exact=str(x.upper().fmpq()), approximate=float(x.upper()))


def evaluate(root, budget_path, out):
    ctx.prec=512
    base=root/'artifacts/flagship_integration/.direct_physical_quadratic_source_work/interval_014'
    manifest_path, receipt_path=base/'manifest.json',base/'reproduction.json'
    manifest=json.loads(manifest_path.read_bytes())
    receipt=json.loads(receipt_path.read_bytes())
    if (receipt['manifest_SHA256']!=sha(manifest_path)
            or not receipt['byte_identical'] or not receipt['independent_recomputation']):
        raise ValueError('Frozen independently reproduced source lemma required')
    paths=[manifest_path,receipt_path,budget_path,Path(__file__)]
    def row(family,pair):
        path=base/f'{family}_{pair}.json'; data=path.with_suffix('.npz')
        record=json.loads(path.read_bytes())
        if (record['interval']!=14 or record['family']!=family or record['endpoint_pair']!=pair
                or not record['taylor_half_included'] or record['data_SHA256']!=sha(data)):
            raise ValueError('Matching half-Hessian source required')
        for file in (path,data):
            payload=file.read_bytes()
            if file.suffix=='.json':payload=payload.replace(b'\r\n',b'\n')
            if hashlib.sha256(payload).hexdigest().upper()!=manifest['files'][file.relative_to(root).as_posix()]:
                raise ValueError('Operand outside retained source lemma')
        paths.extend((path,data))
        with np.load(data,allow_pickle=False) as z:
            mids=z['Q_mid_q'][73].copy(); rads=z['Q_rad_q'][73].copy()
        return np.array([arb(str(m))+arb(0,arb(str(r))) for m,r in zip(mids,rads,strict=True)],dtype=object)
    lt0=2*row('LT','01')[14]; lt1=2*row('LT','11')[14]
    q01=row('TT','01').reshape(74,74)
    q10=row('TT','10').reshape(74,74)
    q11=row('TT','11').reshape(74,74)
    left=q01[:,14]+q10[14,:]
    right=q11[:,14]+q11[14,:]
    norm=lambda a:sum((abs(v).upper()**2 for v in a),arb(0)).sqrt().upper()
    budget=json.loads(budget_path.read_bytes())
    rL,rT=map(arb,budget['operands']['original_radius'])
    longitudinal=(abs(lt0)+abs(lt1))*rL
    transverse=(norm(left)+norm(right))*rT
    payload=dict(algorithm='INTERVAL14_ENTRY_FROZEN_POINT_HESSIAN_FIRST_JET_V1',
        scope='LINEAR_STATE_DEPENDENCE_AT_CENTER_ONLY_NOT_UNIFORM_REMAINDER',
        interval=14,output_coordinate=73,input_coordinate=14,
        formula='da = 2 LT01[14] l_left + 2 LT11[14] l_right + (TT01[:,14]+TT10[14,:]).t_left + (TT11[:,14]+TT11[14,:]).t_right',
        LT_linear_state_support_upper=bound(longitudinal),
        TT_linear_state_support_upper=bound(transverse),
        complete_linear_state_support_upper=bound(longitudinal+transverse),
        LT_already_in_selected_global_quadratic_budget=True,
        TT_not_yet_in_selected_global_quadratic_budget=True,
        uniform_higher_order_entry_remainder_bound=None,
        signed_shared_coefficients_combined_before_norm=True,
        local_interval13_reopened=False,Gate7_closed=False,
        source_SHA256={str(path.resolve()):sha(path) for path in paths})
    with out.open('xb') as stream:stream.write((json.dumps(payload,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in payload.items() if k!='source_SHA256'},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--budget',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    evaluate(args.evidence_root.resolve(),args.budget.resolve(),args.out)

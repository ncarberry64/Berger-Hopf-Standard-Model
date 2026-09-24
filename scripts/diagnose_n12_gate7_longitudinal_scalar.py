"""Locate the state groups in the retained descriptor's axis restriction."""
import argparse
import gzip
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor,vector_norm
from certify_n12_gate7_endpoint_vector_transport import restore,upper
import n12_gate7_common_input_error_maps as maps
import evaluate_n12_gate7_coupled_residual_saved as saved


def evaluate(root,parent,adjoint):
    record=json.loads((parent/'record.json').read_bytes())
    family=record['family'];dimension={'midpoint':373,'endpoint':199}[family]
    receipt=json.loads((parent/'scalar_model_receipt.json').read_bytes())
    path=parent/'scalar_model.json.gz'
    if receipt['scalar_model_SHA256']!=saved.sha(path): raise ValueError('unaltered scalar coefficients required')
    domain=TaylorDomain(record['original_state_groups'],dimension)
    v=[restore(pair) for pair in json.loads(gzip.decompress(path.read_bytes()))]
    value=InputLinearTaylor(domain,arb_mat(1,198,v[:198]),arb_mat(dimension,198,v[198:-1]),v[-1],record['input_groups'])
    error=maps.load_error_map(root,record,adjoint)
    with np.load(root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz',allow_pickle=False) as z:
        a=z['current_center_green_image_unit_mid'][14].copy();a/=np.linalg.norm(a)
    axis=arb_mat(74,1,[arb(float(x)) for x in a])
    direction=arb_mat(198,1,axis.entries()+(error*axis).entries())
    restricted=value.at_input(direction)
    groups=[]
    for start,stop,kind in domain.groups:
        coefficients=[restricted.a[0,i] for i in range(start,stop)]
        bound=vector_norm(coefficients) if kind=='euclidean' else sum((abs(x).upper() for x in coefficients),arb(0)).upper()
        groups.append(dict(group=[start,stop,kind],bound=upper(bound),
            midpoint_bound=upper(vector_norm([x.mid() for x in coefficients]) if kind=='euclidean'
                else sum((abs(x.mid()) for x in coefficients),arb(0))),
            coefficient_radius_bound=upper(vector_norm([x.rad() for x in coefficients]) if kind=='euclidean'
                else sum((x.rad() for x in coefficients),arb(0)))))
    top=sorted(range(dimension),key=lambda i:float(abs(restricted.a[0,i]).upper()),reverse=True)[:20]
    return dict(family=family,scope='DIAGNOSTIC_SCALAR_AXIS_RESTRICTION_NOT_COMPLETE_TRANSPORT',
        scalar_support=upper(restricted.support()),constant=upper(abs(restricted.c)),
        linear=upper(restricted.linear_bound()),nonlinear=upper(restricted.r),state_groups=groups,
        largest_state_coefficients=[dict(index=i,midpoint=str(restricted.a[0,i].mid().fmpq()),
            radius=str(restricted.a[0,i].rad().fmpq()),absolute_upper=float(abs(restricted.a[0,i]).upper())) for i in top],
        all_state_coefficients=[[str(x.mid().fmpq()),str(x.rad().fmpq())] for x in restricted.a.entries()],
        source_hashes=dict(parent=saved.sha(parent/'record.json'),scalar=saved.sha(path),
                           adjoint=saved.sha(adjoint),evaluator=saved.sha(Path(__file__))),
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser()
    for name in ('evidence-root','parent','adjoint','out'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();ctx.prec=512
    if args.out.exists(): raise FileExistsError('fresh diagnostic output required')
    result=evaluate(args.evidence_root.resolve(),args.parent.resolve(),args.adjoint.resolve())
    args.out.write_bytes(saved.encoded(result))
    print(json.dumps({k:result[k] for k in ('family','linear','nonlinear','state_groups')}))


if __name__=='__main__': main()

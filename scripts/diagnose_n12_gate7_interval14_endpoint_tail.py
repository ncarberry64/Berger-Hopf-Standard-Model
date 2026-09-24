"""Locate the fixed linear transport cost of the endpoint nonlinear tail."""
import argparse
import json
from pathlib import Path
import sys


def evaluate(root,endpoint,midpoint):
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    import numpy as np
    from flint import arb,arb_mat,ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm_immutable_input_hash_cache as cache
    ctx.prec=512;p=engine.p;r=p.geometry.residual
    with cache.cache_hashes([(p.values,'sha'),(r.center,'_sha'),(r.foundation.coordinate.center,'_sha')]):
        with np.load(r.center.JACOBIAN.with_suffix('.npz'),allow_pickle=False) as z:t=z['endpoint_physical_tangent_action'][15]
        with np.load(r.center.PRECONDITIONER.with_suffix('.npz'),allow_pickle=False) as z:R=z['reduced_right_Newton_blocks'][14]
        with np.load(midpoint/'operands.npz',allow_pickle=False) as z:
            read=lambda k:p.hs.restore_balls(z[k+'_mid_q'],z[k+'_rad_q'])
            df=read('point_scaled_derivative');directions=read('weighted_tube_directions')
        M=arb_mat([[df[i,150+j]/directions[j,150+j] for j in range(99)] for i in range(99)])
        P=arb_mat(R.tolist()).solve(arb_mat(r.center.cert._frame(t,r.center.cert.TEST_DESCRIPTOR_SCALE).T.tolist()))
        row=arb_mat(1,99,[P[73,j] for j in range(99)])
        h=arb(float(p.values.operands()[-1][14]));direct=row*h/6;indirect=row*M*h*h/12;combined=direct-indirect
    record=json.loads(endpoint.read_bytes())
    radii=[arb(v[-1][0])+arb(0,arb(v[-1][1])) for v in record['physical_derivative_models']]
    contributions=[(abs(combined[0,j])*radii[j]).upper() for j in range(99)]
    out=dict(step=float(h),combined_endpoint_tail_linear_support_upper=float(sum(contributions,arb(0))),
        separately_bounded_endpoint_tail_support_upper=float(sum(((abs(direct[0,j])+abs(indirect[0,j]))*radii[j] for j in range(99)),arb(0))),
        largest_components=[dict(coordinate=j,contribution=float(contributions[j])) for j in sorted(range(99),key=lambda i:float(contributions[i]),reverse=True)[:8]],
        diagnostic_only=True,actual_entry_error_certified=False,interval13_recomputed=False)
    print(json.dumps(out,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','endpoint','midpoint'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();evaluate(args.evidence_root.resolve(),args.endpoint.resolve(),args.midpoint.resolve())

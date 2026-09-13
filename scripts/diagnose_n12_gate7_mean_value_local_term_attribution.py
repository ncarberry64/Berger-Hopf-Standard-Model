"""Attribute the saved local-column interval widths; no new action derivatives."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import sys, json, argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
import certify_n12_gate7_mean_value_trial_local_integration as producer
from flint import arb,arb_mat,ctx
import numpy as np

parser=argparse.ArgumentParser()
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
args.out.mkdir(parents=True,exist_ok=False)
args.interval=13;args.column=14
args.evidence_root=ROOT/'tmp/bhsm_split_directed_trial13_pair_20260913'
args.mean_value_root=ROOT/'tmp/bhsm_endpoint_trial_mean_value_pair_20260913'
args.previous_pair=ROOT/'tmp/bhsm_preconditioned_split_trial13_pair_20260913/value'
ctx.prec=512
original=producer.algebra.local_columns
attribution={};saved={}
def capture(trial,endpoint_action,center_direction,center_action,direction_tail,midpoint_df,step,test,frozen_left,frozen_right,column,side):
    result=original(trial,endpoint_action,center_direction,center_action,direction_tail,midpoint_df,step,test,frozen_left,frozen_right,column,side)
    matrix=producer.algebra._matrix
    e,a,w,b,m,t,l,r=map(matrix,(trial,endpoint_action,center_direction,center_action,midpoint_df,test,frozen_left,frozen_right))
    h=producer.algebra._step(step);sign=1 if side=='left' else -1
    p=r.solve(t);q=p*m
    a0=arb_mat(a.nrows(),1,[v.mid() for v in a.entries()])
    fixed=p*(l*e+e) if side=='left' else arb_mat(r.nrows(),1,[arb(i==column) for i in range(r.nrows())])-p*e
    terms=dict(fixed=fixed,endpoint_center=(p*a0)*(h/6),midpoint_center_action=(p*b)*(2*h/3),
        shared_endpoint_uncertainty=(p*(h/6)+q*(sign*h*h/12))*(a-a0),
        old_center_shift=(q*(e/2+a0*(sign*h/8)-w))*(2*h/3))
    combined=result['combined_endpoint_tail']
    worst=max(range(combined.nrows()),key=lambda i:combined[i,0].rad())
    attribution[side]=dict(worst_output_row=worst,combined_maximum_radius=float(combined[worst,0].rad()),
        terms={name:dict(maximum_radius=float(max(v.rad() for v in value.entries())),radius_at_worst_output=float(value[worst,0].rad())) for name,value in terms.items()})
    for name,value in terms.items():saved[side+'_'+name]=producer.base.array(value)
    return result
producer.algebra.local_columns=capture
residual=producer.p.geometry.residual
targets=[(producer.p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
try:
    with producer.base.cache.cache_hashes(targets,excluded_roots=[args.out]):
        source,_,_=producer.evaluate(args)
        producer.base.bind(source,Path(__file__))
        producer.p.verify_sources(source['binding'])
    encoded={}
    for name,values in saved.items():
        encoded[name+'_mid_q'],encoded[name+'_rad_q']=producer.p.hs.rational_balls(values)
    data=args.out/'column.npz'
    np.savez_compressed(data,**encoded)
    record=dict(algorithm='SAVED_MEAN_VALUE_LOCAL_TERM_ATTRIBUTION_ARB512_V1',binding=source['binding'],
        data_SHA256=producer.p.values.sha(data),report=dict(attribution=attribution,new_action_derivative_evaluations=0,
        interval_width_attribution_only=True,Gate7_closed=False,FULL_BHSM_COMPLETE=False),FULL_BHSM_COMPLETE=False)
    (args.out/'record.json').write_bytes(producer.p.geometry.encoded(record))
    print(json.dumps(attribution),flush=True)
finally:
    producer.algebra.local_columns=original

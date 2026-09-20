"""Read the original interval-14 family; optionally recover missing point jets.

Writes only a fresh continuation directory, never the evidence checkout.
No interval-13 local certificate is opened or evaluated.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def evaluate(root,stage,out,point_jets=False):
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    import numpy as np
    from flint import arb,arb_mat,ctx
    import bhsm_immutable_input_hash_cache as cache
    if stage=='endpoint':
        import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
        index=15
    else:
        import certify_n12_gate7_coupled_midpoint_uniform_derivatives as engine
        index=14
    p=engine.p;residual=p.geometry.residual;ctx.prec=512
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with cache.cache_hashes(targets,excluded_roots=[out]):
        source=engine.load_inputs(index)
        paired=source['paired'];cert=p.values.cert
        _,weights,descriptors,reference,_=p.values.operands()
        arrays={f'paired_{k}':v for k,v in paired.items() if isinstance(v,np.ndarray) and v.dtype==object}
        arrays.update(response=source['response'],raw_domain=source['raw_domain'])
        if stage=='endpoint':
            with np.load(residual.center.JACOBIAN.with_suffix('.npz'),allow_pickle=False) as z:
                frame=cert._frame(z['endpoint_physical_tangent_action'][index],cert.TRIAL_DESCRIPTOR_SCALE)
            directions=np.empty((99,75),dtype=object)
            directions[:,0]=source['tube']['raw_longitudinal_direction']*source['tube']['radius_longitudinal']
            directions[:98,0]*=np.array([arb(float(v)) for v in weights],dtype=object)
            directions[:,1:]=np.array([arb(float(v)) for v in frame.flat],dtype=object).reshape(frame.shape)*source['tube']['radius_transverse']
            descriptor=arb(float(descriptors[index]))
            groups=[(0,1,'interval'),(1,75,'euclidean')]
        else:
            domain_path=engine.values.eq.midpoint.WORK/f'interval_{index:03d}/domain.npz'
            with np.load(domain_path,allow_pickle=False) as z:
                directions=p.hs.restore_balls(z['raw_directions_mid_q'],z['raw_directions_rad_q'])
            groups=[]
            for group in source['groups']:
                directions[:,group['start']:group['stop']]*=group['radius']
                groups.append((group['start'],group['stop'],group['norm']))
            directions[:98]*=np.array([arb(float(v)) for v in weights],dtype=object)[:,None]
            descriptor=source['raw_center'][98]
        arrays['weighted_tube_directions']=directions
        arrays['point_descriptor']=np.array([descriptor],dtype=object)
        report=dict(stage=stage,index=index,parameter_groups=groups,
            original_domain_preserved=True,interval13_recomputed=False,
            source_keys=list(source),paired_keys=list(paired),
            array_shapes={k:list(v.shape) for k,v in arrays.items()},
            point_jets_computed=False,uniform_entry_remainder_certified=False,Gate7_closed=False)
        print(json.dumps(report),flush=True)
        if point_jets:
            from bhsm.interface.ball_factored_arb_integrand import use_ball_factored_integrand
            original=cert._verified_solve;solves=[];checks=[]
            def capture(matrix,rhs):
                result=original(matrix,rhs)
                solves.append(np.array(result.entries(),dtype=object).reshape(result.nrows(),result.ncols()))
                return result
            try:
                cert._verified_solve=capture
                with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,paired['center']):
                    with p.hs.verified_eigenline(cert,checks,expected_index=24,normalize_proposal_center=True):
                        point=cert._rate_enclosure(paired['center'],descriptor,weights,reference,directions)
            finally:cert._verified_solve=original
            if len(checks)!=1 or not p.proof_valid(checks[0]) or len(solves)!=3:
                raise ArithmeticError('Verified normalized root and three complete point solves required')
            for i,v in enumerate(solves):arrays[f'point_solve_{i}']=v
            arrays.update(point_rate=point.value,point_scaled_derivative=point.derivative)
            report.update(point_jets_computed=True,point_root_checks=checks)
        p.verify_sources(source['binding'])
        encoded={}
        for name,value in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(value)
        out.mkdir(parents=True,exist_ok=False)
        data=out/'operands.npz';np.savez_compressed(data,**encoded)
        record=dict(algorithm='INTERVAL14_SHARED_ENTRY_ORIGINAL_OPERANDS_V1',binding=source['binding'],
            report=report,data_SHA256=p.values.sha(data),
            producer_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest().upper())
        (out/'record.json').write_bytes(p.geometry.encoded(record))
        print(json.dumps(dict(stage=stage,index=index,completed=True,point_jets_computed=point_jets)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--stage',choices=('endpoint','midpoint'),required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--point-jets',action='store_true')
    args=parser.parse_args()
    evaluate(args.evidence_root.resolve(),args.stage,args.out.resolve(),args.point_jets)

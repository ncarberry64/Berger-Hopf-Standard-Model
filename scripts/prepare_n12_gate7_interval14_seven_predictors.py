"""Missing same-parameter implicit point jets for interval 14's single input."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import hashlib
import json
from pathlib import Path
import sys


def evaluate(root,stage,operands,endpoint_operands,out):
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    import numpy as np
    from flint import arb,ctx
    import certify_n12_gate7_ball_physical_hessian_graph as graph
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm_immutable_input_hash_cache as cache
    from bhsm.interface.ball_factored_arb_integrand import use_ball_factored_integrand
    ctx.prec=512;p=engine.p;cert=p.values.cert;residual=p.geometry.residual
    def load(folder):
        record=json.loads((folder/'record.json').read_bytes())
        if p.values.sha(folder/'operands.npz')!=record['data_SHA256']:
            raise ValueError('Original operand bytes required')
        with np.load(folder/'operands.npz',allow_pickle=False) as z:
            arrays={k[:-6]:p.hs.restore_balls(z[k],z[k[:-6]+'_rad_q']) for k in z.files if k.endswith('_mid_q')}
        return record,arrays
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with cache.cache_hashes(targets,excluded_roots=[out]):
        record,a=load(operands);endpoint_record,e=load(endpoint_operands)
        if record['report']['stage']!=stage or endpoint_record['report']['index']!=15:
            raise ValueError('Original interval-14 stage required')
        p.verify_sources(record['binding']);p.verify_sources(endpoint_record['binding'])
        _,weights,_,reference,steps=p.values.operands()
        rT_path=root/'artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE.json'
        rT=arb(json.loads(rT_path.read_bytes())['stored_polynomial_adjudication']['witness']['radius'][1])
        axis=e['weighted_tube_directions'][:,15]/rT
        if stage=='midpoint':
            action=e['point_scaled_derivative'][:,15]/rT
            axis=axis/2-arb(float(steps[14]))*action/8
            # The predictor direction must be exact. Its tiny Arb discrepancy
            # is saved explicitly and must be included by the consumer.
        exact_axis=np.array([v.mid() for v in axis],dtype=object)
        center=a['paired_center'];directions=a['weighted_tube_directions']
        original=graph._solve;solves=[];checks=[]
        def capture(matrix,rhs):
            result=original(matrix,rhs);solves.append(result.copy())
            print(json.dumps(dict(stage=stage,point_solve=len(solves)-1,shape=list(result.shape))),flush=True)
            return result
        try:
            graph._solve=capture
            with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,center):
                with p.hs.verified_eigenline(cert,checks,expected_index=24,normalize_proposal_center=True):
                    result=graph.batched_axis_map(center,a['point_descriptor'][0],weights,reference,exact_axis,directions)
        finally:graph._solve=original
        count=directions.shape[1]
        if ([v.shape for v in solves]!=[(62,1)]*3+[(62,count)]*4
                or len(checks)!=1 or not p.proof_valid(checks[0])):
            raise ArithmeticError('Seven complete same-anchor implicit jets required')
        arrays=dict(point_mixed_derivative=result,weighted_input_axis=exact_axis,
            input_axis_ball=axis,weighted_tube_directions=directions,raw_domain=a['raw_domain'],
            center_state=center,point_descriptor=a['point_descriptor'])
        for i,v in enumerate(solves):arrays[f'point_solve_{i}']=v
        encoded={}
        for name,value in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(value)
        p.verify_sources(record['binding']);out.mkdir(parents=True,exist_ok=False)
        data=out/'predictors.npz';np.savez_compressed(data,**encoded)
        result_record=dict(algorithm='INTERVAL14_SINGLE_INPUT_SEVEN_POINT_PREDICTORS_V1',stage=stage,
            interval=14,input_coordinate=14,output_coordinate=73,
            parameter_groups=record['report']['parameter_groups'],binding=record['binding'],
            point_checks=checks,point_input_axis_discrepancy_must_be_enclosed=True,
            original_domain_preserved=True,interval13_recomputed=False,
            uniform_second_order_entry_bound_certified=False,Gate7_closed=False,
            data_SHA256=p.values.sha(data),source_SHA256={str(path.resolve()):p.values.sha(path) for path in (
                operands/'record.json',operands/'operands.npz',endpoint_operands/'record.json',endpoint_operands/'operands.npz',
                rT_path,Path(__file__),Path(graph.__file__))})
        (out/'record.json').write_bytes(p.geometry.encoded(result_record))
        print(json.dumps(dict(stage=stage,completed=True,parameter_count=count)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--stage',choices=('endpoint','midpoint'),required=True)
    parser.add_argument('--operands',type=Path,required=True)
    parser.add_argument('--endpoint-operands',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    evaluate(args.evidence_root.resolve(),args.stage,args.operands.resolve(),args.endpoint_operands.resolve(),args.out.resolve())

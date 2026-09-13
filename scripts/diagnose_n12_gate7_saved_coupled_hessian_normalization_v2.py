"""Apply common-border normalization to a bound, saved seven-solve diagnostic."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
import bhsm_immutable_input_hash_cache as cache
from bhsm.interface import coupled_physical_normalization_second as normalization


def evaluate(source,arrays):
    p=engine.p;cert=p.values.cert
    if not all(b.contains(a) for a,b in zip(source['raw_domain'],arrays['raw_domain'],strict=True)):
        raise ArithmeticError('restored domain must contain the identical serialized input')
    solved=arrays['uniform_solutions']
    if solved.shape!=(7,62,1):raise ValueError('all seven original variation solves required')
    _,weights,_,_,_=p.values.operands()
    qw,rw,_,_=cert.metric_data()
    w=np.array([arb(float(v)) for v in weights],dtype=object)
    q=np.array([arb(float(v)) for v in qw],dtype=object)
    reduced=np.array([arb(float(v)) for v in rw],dtype=object)
    u=arrays['weighted_axis'];v=arrays['weighted_transverse']
    if u.shape!=(99,) or v.shape!=(99,1):raise ValueError('single saved direction pair required')
    raw_u=u[:98]/w;raw_v=v[:98]/w[:,None]
    zeros=np.full(1,arb(0),dtype=object)
    def jet(line,response,config,ds,scalar):
        return dict(configuration=config,psi=solved[line,:61],hard=solved[response,:61],
            border=solved[response,-1],descriptor=ds,cpsi=scalar[:,0],remainder=scalar[:,1])
    axis=jet(1,2,(q*raw_u[37:74])[:,None],u[98:99],arrays['descriptor_first_axis'][None,:])
    transverse=jet(3,4,q[:,None]*raw_v[37:74],v[98],arrays['descriptor_first_transverse'])
    mixed=jet(5,6,np.full((37,1),arb(0),dtype=object),zeros,arrays['descriptor_mixed'])
    result,proof=normalization.normalized_mixed(q*source['paired']['full'][37:74],reduced,
        source['paired']['eigenbox'][:61],solved[0,:61,0],solved[0,-1,0],source['raw_domain'][98],
        *arrays['descriptor_base'],axis,transverse,mixed,coupled_identities_and_variations=True)
    old=arrays['uniform_hessian'];point=arrays['point_hessian']
    if not all(a.overlaps(b) for a,b in zip(result.flat,old.flat,strict=True)):
        raise ArithmeticError('equivalent normalizations disagree')
    if not all(a.contains(b) for a,b in zip(result.flat,point.flat,strict=True)):
        raise ArithmeticError('normalized uniform Hessian must contain verified point result')
    proof.update(maximum_original_radius=float(max(v.rad() for v in old.flat)),
        maximum_normalized_radius=float(max(v.rad() for v in result.flat)),
        maximum_point_absolute=float(max(abs(v).upper() for v in point.flat)),
        point_contained=True,original_enclosure_overlap=True,
        full_affine_direction_coverage=False,independent_recomputation=False,
        saved_complete_original_scalar_contractions_used=True)
    return result,proof


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);ctx.prec=512;p=engine.p
    record_path=args.source/'record.json';data=args.source/'hessian.npz'
    record=json.loads(record_path.read_bytes())
    if record['data_SHA256']!=p.values.sha(data):raise ArithmeticError('saved Hessian data changed')
    report=record['report']
    if (report['complete_original_seven_solve_graph_used'] is not True
            or report['complete_original_scalar_contractions_used'] is not True
            or record['independent_recomputation'] is not False):
        raise ArithmeticError('complete original diagnostic required; no certificate promotion')
    residual=p.geometry.residual
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with cache.cache_hashes(targets,excluded_roots=[args.out]):
        p.verify_sources(record['binding']);source=engine.load_inputs(record['endpoint'])
        residual.merge(source['binding']['files'],record['binding']['files'])
        for file in (record_path,data,Path(__file__),Path(normalization.__file__)):
            residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
        with np.load(data,allow_pickle=False) as saved:
            mid,rad=p.hs.rational_balls(source['raw_domain'])
            if not (np.array_equal(mid,saved['raw_domain_mid_q']) and np.array_equal(rad,saved['raw_domain_rad_q'])):
                raise ArithmeticError('exact saved physical domain strings must match')
            arrays={key[:-6]:p.hs.restore_balls(saved[key],saved[key[:-6]+'_rad_q'])
                for key in saved.files if key.endswith('_mid_q')}
        try:result,proof=evaluate(source,arrays)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error),FULL_BHSM_COMPLETE=False)))
            raise
        mid,rad=p.hs.rational_balls(result);output=args.out/'normalized_hessian.npz'
        np.savez_compressed(output,hessian_mid_q=mid,hessian_rad_q=rad)
        p.verify_sources(source['binding'])
        (args.out/'record.json').write_bytes(p.geometry.encoded(dict(binding=source['binding'],
            report=proof,data_SHA256=p.values.sha(output),FULL_BHSM_COMPLETE=False)))
        print(json.dumps(proof),flush=True)


if __name__=='__main__':main()

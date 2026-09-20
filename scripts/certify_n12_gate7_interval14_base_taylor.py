"""Uniform base-solve Taylor errors for the original interval-14 domain.

Common physical parameters stay symbolic in every action contraction.
Only the explicit nonlinear Taylor tails enter the retained inverse bound.
This is a prerequisite, not the requested complete derivative-entry proof.
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


def evaluate(root,operands,predictors,out):
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    import numpy as np
    from flint import arb,arb_mat,ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm_immutable_input_hash_cache as cache
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(ROOT/'src/bhsm/interface'))
    from bhsm.interface import shared_action_taylor as arithmetic
    from bhsm.interface.shared_action_taylor import Taylor,TaylorDomain,scalar_taylor_action
    from bhsm.interface.componentwise_weighted_response import enclose_response_rows
    ctx.prec=512;p=engine.p;cert=p.values.cert;residual=p.geometry.residual
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
    def load(folder,name):
        record=json.loads((folder/'record.json').read_bytes())
        if sha(folder/name)!=record['data_SHA256']:raise ValueError('Original verified data required')
        with np.load(folder/name,allow_pickle=False) as z:
            arrays={k[:-6]:p.hs.restore_balls(z[k],z[k[:-6]+'_rad_q']) for k in z.files if k.endswith('_mid_q')}
        return record,arrays
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with cache.cache_hashes(targets,excluded_roots=[out]):
        ore,a=load(operands,'operands.npz');pre,s=load(predictors,'predictors.npz')
        if pre['interval']!=14 or pre['stage']!=ore['report']['stage'] or pre['binding']!=ore['binding']:
            raise ValueError('Matching original interval-14 physical family required')
        p.verify_sources(ore['binding'])
        sources={str(path.resolve()):sha(path) for path in (operands/'record.json',operands/'operands.npz',
            predictors/'record.json',predictors/'predictors.npz',Path(__file__),Path(arithmetic.__file__),
            Path(cert.__file__),Path(enclose_response_rows.__code__.co_filename))}
        binding=hashlib.sha256(p.geometry.encoded(sources)).hexdigest().upper()
        out.mkdir(parents=True,exist_ok=True)
        manifest=out/'sources.json'
        if manifest.exists() and manifest.read_bytes()!=p.geometry.encoded(sources):
            raise ValueError('Checkpoint operands changed; use a fresh directory')
        if not manifest.exists():manifest.write_bytes(p.geometry.encoded(sources))
        n=s['weighted_tube_directions'].shape[1]
        domain=TaylorDomain(pre['parameter_groups'],n)
        _,weights,_,_,_=p.values.operands();qw,rw,_,_=cert.metric_data()
        weights,qw,rw=[[arb(float(v)) for v in values] for values in (weights,qw,rw)]
        center=s['center_state'];directions=s['weighted_tube_directions']
        state=[domain.affine(center[i],[directions[i,j]/weights[i] for j in range(n)]) for i in range(98)]
        if any(not a['raw_domain'][i].contains(v.enclosure()) for i,v in enumerate(state)):
            raise ArithmeticError('Original complete state domain must be preserved')
        witness=pre['point_checks'][0]
        ep=[arb(str(v)) for v in witness['target_midpoints_rational']]
        if len(ep)!=62:raise ValueError('Complete normalized point eigenpair required')
        def predictor(c,derivative):
            return [domain.affine(v.mid(),[derivative[i,j].mid() for j in range(n)]) for i,v in enumerate(c)]
        psi=predictor(ep[:61],s['point_solve_3'][:61])
        hard=predictor(s['point_solve_0'][:,0],s['point_solve_4'])
        dot=lambda x,y:sum((u*v for u,v in zip(x,y,strict=True)),arb(0))
        pad=lambda v:[arb(0)]*37+list(v[:61])
        maps=[cert._dense_mapping(cert._integrand(center,node,0).maps) for node in range(cert.POINTS)]
        def encode(v):return [[str(x.mid().fmpq()),str(x.rad().fmpq())] for x in [v.c,*v.a.entries(),v.r]]
        def action(name,legs):
            path=out/(name+'.json')
            if path.exists():
                record=json.loads(path.read_bytes())
                if record['binding']!=binding:raise ValueError('Immutable action checkpoint required')
                values=[arb(m)+arb(0,arb(r)) for m,r in record['values']]
                result=Taylor(domain,values[0],arb_mat(1,n,values[1:-1]),values[-1])
            else:
                if any(all(isinstance(v,arb) and v.is_zero() or isinstance(v,int) and v==0 for v in leg) for leg in legs):
                    result=domain.affine(0)
                else:
                    with scalar_taylor_action(cert):
                        result=cert._contracted_action(np.array(state,dtype=object),[np.array(v,dtype=object) for v in legs],maps)
                    if isinstance(result,arb):result=domain.affine(result)
                path.write_bytes(p.geometry.encoded(dict(binding=binding,values=encode(result))))
            print(json.dumps(dict(stage=pre['stage'],term=name,nonlinear_upper=float(result.r))),flush=True)
            return result
        rayleigh=action('rayleigh',[pad(psi),pad(psi)])/dot(psi,psi)
        lam=domain.affine(ep[61],[v.mid() for v in rayleigh.a.entries()])
        eigen_predictor=psi+[lam]
        inside=[a['paired_eigenbox'][i].contains(v.enclosure()) for i,v in enumerate(eigen_predictor)]
        if not all(inside):
            (out/'predictor_containment_failure.json').write_bytes(p.geometry.encoded(dict(
                original_domain_unchanged=True,failed_coordinates=[i for i,ok in enumerate(inside) if not ok],
                uniform_entry_remainder_certified=False)))
            raise ArithmeticError('Eigenpair predictor leaves original implicit solution box; retained defect cannot yet be applied')
        R=a['paired_rm'];weights_solve=a['paired_radii'];variation=a['paired_variation']
        eigen_residuals=[]
        for i in range(62):
            v=list(R[i,:61]);bottom=R[i,61]
            g=action(f'eigen_{i:02d}',[pad(v),pad(psi)])-lam*dot(v,psi)+bottom*(dot(psi,psi)-1)/2
            eigen_residuals.append(g)
        def errors(models):
            forcing=np.array([v.support() for v in models],dtype=object)
            _,proof=enclose_response_rows(np.array([arb(0)]*62,dtype=object),forcing,weights_solve,variation)
            return [arb(x) for x in proof['component_radii_upper_rational']],proof
        eigen_error,eigen_proof=errors(eigen_residuals)
        psi=[Taylor(domain,v.c,v.a,eigen_error[i]) for i,v in enumerate(psi)]
        lam=Taylor(domain,lam.c,lam.a,eigen_error[61])
        configuration=[qw[i]*state[37+i] for i in range(37)]
        d=[configuration[i]/weights[i] for i in range(37)]+[arb(0)]*61
        response_residuals=[]
        for i in range(62):
            v=list(R[i,:61]);bottom=R[i,61]
            gl=[v[j]*rw[j]*qw[j]/weights[j] for j in range(37)]+[arb(0)]*61
            cl=[arb(0)]*37+[v[j]*rw[j]/weights[37+j] for j in range(61)]
            source=action(f'response_{i:02d}_gradient',[gl])-action(f'response_{i:02d}_source',[cl,d])
            g=action(f'response_{i:02d}_action',[pad(v),pad(hard)])-lam*dot(v,hard[:61])+hard[61]*dot(v,psi)-source+bottom*dot(psi,hard[:61])
            response_residuals.append(g)
        response_error,response_proof=errors(response_residuals)
        result=dict(algorithm='INTERVAL14_ORIGINAL_DOMAIN_BASE_IMPLICIT_TAYLOR_ERRORS_V1',
            stage=pre['stage'],interval=14,parameter_groups=pre['parameter_groups'],
            original_domain_unchanged=True,shared_state_coefficients_preserved=True,
            eigenpair_predictor_contained_in_original_box=True,
            eigenpair_error_upper_exact=[str(v.fmpq()) for v in eigen_error],
            response_error_upper_exact=[str(v.fmpq()) for v in response_error],
            eigenpair_proof=eigen_proof,response_proof=response_proof,
            eigenvalue_predictor=encode(domain.affine(lam.c,lam.a.entries())),
            eigenpair_max_error=float(max(eigen_error)),response_max_error=float(max(response_error)),
            input_source_SHA256=sources,interval13_recomputed=False,
            full_entry_remainder_certified=False,Gate7_closed=False)
        if any(sha(Path(path))!=digest for path,digest in sources.items()):raise ValueError('Source changed during proof')
        (out/'record.json').write_bytes(p.geometry.encoded(result))
        print(json.dumps(dict(stage=pre['stage'],eigenpair_max_error=result['eigenpair_max_error'],
            response_max_error=result['response_max_error'],completed=True)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','operands','predictors','out'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args()
    evaluate(args.evidence_root.resolve(),args.operands.resolve(),args.predictors.resolve(),args.out.resolve())

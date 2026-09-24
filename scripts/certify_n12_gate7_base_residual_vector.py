"""Enclose the 124 retained base implicit equations on the original domain.

These shared state-only residuals can cancel base-error/input-error products
in any projected output without evaluating another action for every output.
They vanish on the inherited implicit solution graph, not throughout its box.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import argparse
import gzip
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bhsm.interface.shared_action_taylor as arithmetic
from bhsm.interface.shared_action_taylor import TaylorDomain,scalar_taylor_action
from certify_n12_gate7_endpoint_vector_transport import upper
import evaluate_n12_gate7_coupled_residual_saved as saved


def dot(a,b): return sum((x*y for x,y in zip(a,b,strict=True)),arb(0))


def encode(value):
    return [[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in [value.c,*value.a.entries(),value.r]]


def evaluate(root,parent_path,refined_path,out):
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(root/'src/bhsm/interface'))
    verified=saved.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p,cert=base.p,base.p.values.cert
    parent=json.loads((parent_path/'record.json').read_bytes())
    refined=json.loads(refined_path.read_bytes())
    family=parent['family'];middle=family=='midpoint'
    if family not in ('midpoint','endpoint'): raise ValueError('known physical family required')
    if (parent['source_hashes']['refined_base_radii']!=saved.sha(refined_path)
            or any(parent['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items())
            or any(refined['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items())):
        raise ValueError('same physical domain and base corrections required')
    pair='bhsm_midpoint_center_mean_value_right_pair_20260913' if middle else 'bhsm_endpoint_trial_mean_value_bootstrap_right_pair_20260913'
    eigen_name='.coupled_midpoint_eigenpair_pilot_work/interval_013' if middle else '.affine_eigenpair_pilot_work/endpoint_014'
    data=root/'tmp'/pair/'value/first/column.npz'
    eigenfile=root/'artifacts/flagship_integration'/eigen_name/'eigenpair.npz'
    sources={**verified['paired_source_hashes'],data.relative_to(root).as_posix():saved.sha(data),
             eigenfile.relative_to(root).as_posix():saved.sha(eigenfile),
             'parent_record':saved.sha(parent_path/'record.json'),'refined_base_radii':saved.sha(refined_path),
             'arithmetic':saved.sha(Path(arithmetic.__file__)),'evaluator':saved.sha(Path(__file__))}
    with np.load(data,allow_pickle=False) as z,np.load(eigenfile,allow_pickle=False) as e:
        centers=[saved.read_matrix(z,f'point_center_{i}',center=True) for i in range(7)]
        center=saved.read_matrix(e,'center_state',center=True)
        ep=saved.read_matrix(e,'eigenpair_center',center=True)
        eigenbox=saved.read_matrix(e,'eigenpair_box')
        directions=saved.read_matrix(z,'weighted_tube_directions')
        raw=saved.read_matrix(z,'raw_domain')
    nstate=directions.ncols()
    groups=verified['families'][family]['groups']+[(nstate,nstate+124,'box')]
    if [list(g) for g in groups]!=parent['original_state_groups']:
        raise ValueError('identical original state domain required')
    domain=TaylorDomain(groups,nstate+124)
    radii=[arb(v) for v in refined['correction_radii_exact'][:124]]
    def model(c,derivative,rows,offset):
        result=[]
        for i in range(rows):
            a=[derivative[i,j] for j in range(nstate)]+[arb(0)]*124
            a[nstate+offset+i]=radii[offset+i]
            result.append(domain.affine(c[i,0],a))
        return result
    psi=model(ep,centers[3],61,0)
    hard=model(centers[0],centers[4],62,62)
    _,weights,_,_,_=p.values.operands();qw,rw,_,_=cert.metric_data()
    weights,qw,rw=[[arb(float(v)) for v in vv] for vv in (weights,qw,rw)]
    state=[domain.affine(center[i,0],[directions[i,j]/weights[i] for j in range(nstate)]+[arb(0)]*124) for i in range(98)]
    if any(not raw[i,0].contains(v.enclosure()) for i,v in enumerate(state)):
        raise ValueError('unchanged original outer state enclosure required')
    pad=lambda v:[domain.affine(0)]*37+list(v[:61])
    maps=[cert._dense_mapping(cert._integrand(center.entries(),node,0).maps) for node in range(cert.POINTS)]
    out.mkdir(parents=True,exist_ok=False)
    (out/'sources.json').write_bytes(saved.encoded(sources))
    binding=saved.sha(out/'sources.json')
    def action(name,legs):
        if any(all((isinstance(v,arb) and v.is_zero()) or isinstance(v,int) and v==0 for v in leg) for leg in legs):
            value=domain.affine(0)
        else:
            with scalar_taylor_action(cert):
                value=cert._contracted_action(np.array(state,dtype=object),[np.array(leg,dtype=object) for leg in legs],maps)
        if isinstance(value,arb): value=domain.affine(value)
        payload=dict(binding=binding,coefficients=encode(value))
        (out/(name+'.json.gz')).write_bytes(gzip.compress(saved.encoded(payload),mtime=0))
        print(json.dumps(dict(term=name,nonlinear=float(value.r))),flush=True)
        return value
    predicted=[domain.affine(ep[i,0],[centers[3][i,j] for j in range(nstate)]+[arb(0)]*124) for i in range(61)]
    rayleigh=action('rayleigh',[pad(predicted),pad(predicted)])/dot(predicted,predicted)
    la=[v.mid() for v in rayleigh.a.entries()]
    predictor=domain.affine(ep[61,0],la)
    la[nstate+61]=(abs(eigenbox[61,0]-ep[61,0]).upper()+predictor.linear_bound()).upper()
    lam=domain.affine(ep[61,0],la)
    configuration=[qw[i]*state[37+i] for i in range(37)]
    d=[configuration[i]/weights[i] for i in range(37)]+[arb(0)]*61
    line=[];response=[]
    for i in range(61):
        basis=[arb(i==j) for j in range(61)]
        g=[basis[j]*rw[j]*qw[j]/weights[j] for j in range(37)]+[arb(0)]*61
        c=[arb(0)]*37+[basis[j]*rw[j]/weights[37+j] for j in range(61)]
        source=action(f'component_{i:02d}_gradient',[g])-action(f'component_{i:02d}_hessian',[c,d])
        line.append(action(f'component_{i:02d}_line',[pad(basis),pad(psi)])-lam*psi[i])
        response.append(action(f'component_{i:02d}_response',[pad(basis),pad(hard)])-lam*hard[i]+hard[61]*psi[i]-source)
    values=line+[(dot(psi,psi)-1)/2]+response+[dot(psi,hard[:61])]
    archive=out/'models.json.gz'
    archive.write_bytes(gzip.compress(saved.encoded([encode(v) for v in values]),mtime=0))
    result=dict(algorithm='ORIGINAL_DOMAIN_BASE_IMPLICIT_RESIDUAL_VECTOR_V1',family=family,
        components=124,original_state_groups=groups,state_dimension=domain.dimension,
        base_error_state_indices=list(range(nstate,nstate+124)),
        equations=['H psi-lambda psi','(psi^T psi-1)/2','H h-lambda h+b psi-f','psi^T h'],
        vanishes_only_on_inherited_implicit_solution_graph=True,
        original_physical_domain_unchanged=True,source_hashes=sources,models_SHA256=saved.sha(archive),
        rows=[dict(component=i,support=upper(v.support()),linear=upper(v.linear_bound()),nonlinear=upper(v.r)) for i,v in enumerate(values)],
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    guarded={'parent_record':parent_path/'record.json','refined_base_radii':refined_path,
             'arithmetic':Path(arithmetic.__file__),'evaluator':Path(__file__)}
    if any(saved.sha(path)!=sources[key] for key,path in guarded.items()):
        raise ValueError('source changed during residual arithmetic')
    if any(saved.sha(root/key)!=digest for key,digest in sources.items() if key not in guarded):
        raise ValueError('physical source changed during residual arithmetic')
    (out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(family=family,base_residual_components=124,Gate7_closed=False)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    for name in ('evidence-root','parent','refined','out'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();ctx.prec=512
    if args.out.exists(): raise FileExistsError('fresh residual directory required')
    evaluate(args.evidence_root.resolve(),args.parent.resolve(),args.refined.resolve(),args.out.resolve())


if __name__=='__main__': main()

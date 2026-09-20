"""Refine the midpoint contribution to entry 73<-14 using Y-beta G.

All four implicit corrections retain common parameters until cancellation.
The supplied uniform solve enclosures own the correction radii; the adjoint
is an arbitrary exact proposal, not a new physical assumption.
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


def evaluate(root,operands,predictors,base_path,direction_path,adjoint_path,out,workers):
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    import numpy as np
    from flint import arb,arb_mat,ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm_immutable_input_hash_cache as cache
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(ROOT/'src/bhsm/interface'))
    from bhsm.interface import shared_action_taylor as arithmetic
    from bhsm.interface.shared_action_taylor import Taylor,TaylorDomain,scalar_taylor_action
    import n12_gate7_parallel_scalar_taylor as parallel
    ctx.prec=512;p=engine.p;cert=p.values.cert;r=p.geometry.residual
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
    def load(folder,name):
        record=json.loads((folder/'record.json').read_bytes())
        if sha(folder/name)!=record['data_SHA256']:raise ValueError('Exact verified input bytes required')
        with np.load(folder/name,allow_pickle=False) as z:
            return record,{k[:-6]:p.hs.restore_balls(z[k],z[k[:-6]+'_rad_q']) for k in z.files if k.endswith('_mid_q')}
    with cache.cache_hashes([(p.values,'sha'),(r.center,'_sha'),(r.foundation.coordinate.center,'_sha')],excluded_roots=[out]):
        ore,a=load(operands,'operands.npz');pre,s=load(predictors,'predictors.npz')
        base=json.loads(base_path.read_bytes());old=json.loads(direction_path.read_bytes());adj=json.loads(adjoint_path.read_bytes())
        if any(v['stage']!='midpoint' or v['interval']!=14 for v in (base,old,adj)):
            raise ValueError('Matching interval-14 midpoint graph required')
        for record in (base,old,adj):
            if any(sha(Path(path))!=digest for path,digest in record['input_source_SHA256'].items()):
                raise ValueError('A prerequisite proof input changed')
        p.verify_sources(ore['binding'])
        paths=[operands/'record.json',operands/'operands.npz',predictors/'record.json',predictors/'predictors.npz',
            base_path,direction_path,adjoint_path,Path(__file__),Path(arithmetic.__file__),Path(parallel.__file__),Path(cert.__file__)]
        sources={str(path.resolve()):sha(path) for path in paths}
        binding=hashlib.sha256(p.geometry.encoded(sources)).hexdigest().upper()
        out.mkdir(parents=True,exist_ok=True)
        manifest=out/'sources.json'
        if manifest.exists() and manifest.read_bytes()!=p.geometry.encoded(sources):raise ValueError('Checkpoint source changed')
        if not manifest.exists():manifest.write_bytes(p.geometry.encoded(sources))
        prior_n=348;n=prior_n+248
        if not old['endpoint_nonlinear_error_parameters_shared'] or len(old['implicit_models'])!=248:
            raise ValueError('Complete shared endpoint-chain implicit predictors required')
        domain=TaylorDomain(old['parameter_groups']+[(prior_n,n,'box')],n)
        def values(data):
            vv=[arb(m)+arb(0,arb(r)) for m,r in data]
            if len(vv)!=prior_n+2:raise ValueError('Complete original shared model required')
            return vv
        corrected=[]
        for i,data in enumerate(old['implicit_models']):
            vv=values(data);coefficients=vv[1:-1]+[arb(0)]*248
            coefficients[prior_n+i]=vv[-1]
            corrected.append(domain.affine(vv[0],coefficients))
        psi,lam=corrected[:61],corrected[61]
        hard,pu,hu=corrected[62:124],corrected[124:186],corrected[186:248]
        _,weights,_,_,_=p.values.operands();qw,rw,_,_=cert.metric_data()
        weights,qw,rw=[[arb(float(v)) for v in values] for values in (weights,qw,rw)]
        state=[domain.affine(s['center_state'][i],[s['weighted_tube_directions'][i,j]/weights[i] for j in range(249)]+[arb(0)]*(n-249)) for i in range(98)]
        if any(not a['raw_domain'][i].contains(value.enclosure()) for i,value in enumerate(state)):
            raise ArithmeticError('Original physical state domain required')
        axis=[]
        for data in old['input_axis_models']:
            vv=values(data)
            axis.append(domain.affine(vv[0],vv[1:-1]+[arb(0)]*248,vv[-1]))
        if len(axis)!=99:raise ValueError('Complete variable input axis required')
        u=[axis[i]/weights[i] for i in range(98)]
        dot=lambda x,y:sum((v*w for v,w in zip(x,y,strict=True)),arb(0))
        pad=lambda v:[arb(0)]*37+list(v[:61])
        beta={key:[arb(v) for v in values] for key,values in adj['exact_covectors'].items()}
        if any(len(v)!=62 or any(not x.rad().is_zero() for x in v) for v in beta.values()):
            raise ValueError('Complete exact residual covectors required')
        names=('eigenline','response','axis_line','axis_response');v0,v1,v2,v3=[beta[k][:61] for k in names]
        bottom={key:values[61] for key,values in beta.items()}
        configuration=[qw[i]*state[37+i] for i in range(37)]
        configuration_u=[qw[i]*u[37+i] for i in range(37)]
        d=[configuration[i]/weights[i] for i in range(37)]+[arb(0)]*61
        du=[configuration_u[i]/weights[i] for i in range(37)]+[arb(0)]*61
        def source(v):
            return ([v[i]*rw[i]*qw[i]/weights[i] for i in range(37)]+[arb(0)]*61,
                    [arb(0)]*37+[v[i]*rw[i]/weights[37+i] for i in range(61)])
        g1,c1=source(v1);g3,c3=source(v3)
        scale=lambda v:[rw[i]/weights[37+i]*v[i] for i in range(61)]
        legs=dict(p=pad(psi),h=pad(hard),pu=pad(pu),hu=pad(hu),u=u,d=d,du=du,
            v0=pad(v0),v1=pad(v1),v2=pad(v2),v3=pad(v3),g1=g1,c1=c1,g3=g3,c3=c3,
            aa=pad(scale(psi)),au=pad(scale(pu)),
            dd=[configuration[i]/weights[i] for i in range(37)]+scale(hard),
            ddu=[configuration_u[i]/weights[i] for i in range(37)]+scale(hu))
        tasks=[('source_gradient',['g1']),('source_hessian',['c1','d']),
            ('source_axis_gradient',['g3','u']),('source_axis_hessian',['c3','d','u']),('source_axis_configuration',['c3','du']),
            ('slope',['p','p','u']),('eigenline',['v0','p']),('response',['v1','h']),
            ('axis_line',['v2','pu']),('axis_line_source',['v2','p','u']),
            ('axis_response',['v3','hu']),('axis_response_source',['v3','h','u']),
            ('descriptor_c',['p','p','aa']),('descriptor_r',['p','p','dd']),
            ('descriptor_cu4',['p','p','aa','u']),('descriptor_cu3a',['p','pu','aa']),('descriptor_cu3b',['p','p','au']),
            ('descriptor_ru4',['p','p','dd','u']),('descriptor_ru3a',['p','pu','dd']),('descriptor_ru3b',['p','p','ddu'])]
        parallel.precompute(root,domain,state,legs,tasks,binding,out,workers)
        maps=[cert._dense_mapping(cert._integrand(s['center_state'],node,0).maps) for node in range(cert.POINTS)]
        def encode(value):return [[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in [value.c,*value.a.entries(),value.r]]
        terms={}
        for name,keys in tasks:
            path=out/(name+'.json')
            if path.exists():
                data=json.loads(path.read_bytes())
                if data['binding']!=binding:raise ValueError('Scalar checkpoint binding changed')
                vv=[arb(m)+arb(0,arb(r)) for m,r in data['values']]
                value=Taylor(domain,vv[0],arb_mat(1,n,vv[1:-1]),vv[-1])
            else:
                with scalar_taylor_action(cert):
                    value=cert._contracted_action(np.array(state,dtype=object),[np.array(legs[k],dtype=object) for k in keys],maps)
                if isinstance(value,arb):value=domain.affine(value)
                path.write_bytes(p.geometry.encoded(dict(binding=binding,values=encode(value))))
            terms[name]=value
        t=terms;f=t['source_gradient']-t['source_hessian']
        fu=t['source_axis_gradient']-t['source_axis_hessian']-t['source_axis_configuration']
        G=[t['eigenline']-lam*dot(v0,psi)+bottom['eigenline']*(dot(psi,psi)-1)/2,
            t['response']-lam*dot(v1,hard[:61])+hard[61]*dot(v1,psi)-f+bottom['response']*dot(psi,hard[:61]),
            t['axis_line']-lam*dot(v2,pu[:61])+pu[61]*dot(v2,psi)+t['axis_line_source']-t['slope']*dot(v2,psi)
                +bottom['axis_line']*dot(psi,pu[:61]),
            t['axis_response']-lam*dot(v3,hu[:61])+hu[61]*dot(v3,psi)+t['axis_response_source']-t['slope']*dot(v3,hard[:61])
                +hard[61]*dot(v3,pu[:61])-fu+bottom['axis_response']*(dot(psi,hu[:61])+dot(pu[:61],hard[:61]))]
        parameter_s=domain.affine(s['point_descriptor'][0],[s['weighted_tube_directions'][98,j] for j in range(249)]+[arb(0)]*(n-249))
        su=axis[98];cp=t['descriptor_c'];rem=t['descriptor_r']
        cu=t['descriptor_cu4']+2*t['descriptor_cu3a']+t['descriptor_cu3b']
        ru=t['descriptor_ru4']+2*t['descriptor_ru3a']+t['descriptor_ru3b']
        N=[parameter_s*v for v in configuration]+[rw[i]*(hard[61]*psi[i]+parameter_s*hard[i]) for i in range(61)]
        Nu=[su*v+parameter_s*w for v,w in zip(configuration,configuration_u,strict=True)]
        Nu += [rw[i]*(hu[61]*psi[i]+hard[61]*pu[i]+su*hard[i]+parameter_s*hu[i]) for i in range(61)]
        delta=hard[61]*cp+parameter_s*rem;delta_u=hu[61]*cp+hard[61]*cu+su*rem+parameter_s*ru
        norm=(dot(N,N).log()/2).exp()
        output=[arb(m)+arb(0,arb(r)) for m,r in adj['output_covector']]
        if len(output)!=99:raise ValueError('Complete local midpoint scalar covector required')
        Y=dot(output,Nu+[delta_u])/norm-dot(output,N+[delta])*dot(N,Nu)/norm**3
        W=Y-sum(G,domain.affine(0))
        original_scalar=domain.affine(0)
        for weight,data in zip(output,old['physical_derivative_models'],strict=True):
            vv=values(data)
            original_scalar += weight*domain.affine(vv[0],vv[1:-1]+[arb(0)]*248,vv[-1])
        original_affine=domain.affine(original_scalar.c,original_scalar.a.entries())
        difference=W-original_affine;new_radius=difference.support()
        refinement=dict(algorithm='INTERVAL14_MIDPOINT_LOCAL_SCALAR_RESIDUAL_CANCELLED_TAYLOR_V1',
            interval=14,stage='midpoint',original_domain_unchanged=True,common_correction_parameters=248,
            nonlinear_tail_upper_exact=str(difference.r.fmpq()),
            constant_translation_upper_exact=str(abs(difference.c).upper().fmpq()),
            linear_translation_and_correction_support_upper_exact=str(difference.linear_bound().fmpq()),
            refined_scalar_remainder_upper_exact=str(new_radius.fmpq()),
            previous_scalar_remainder_upper_exact=str(original_scalar.r.fmpq()),
            strict_improvement=bool(new_radius<original_scalar.r),
            residual_identity_applied_before_support=True,full_normalization_included=True,
            refined_scalar_model=encode(W),input_source_SHA256=sources,interval13_recomputed=False,Gate7_closed=False)
        if any(sha(Path(path))!=digest for path,digest in sources.items()):raise ValueError('Proof source changed')
        (out/'refinement.json').write_bytes(p.geometry.encoded(refinement))
        if not refinement['strict_improvement']:raise ArithmeticError('Scalar refinement did not improve the enclosure')
        updated=dict(algorithm='INTERVAL14_MIDPOINT_LOCAL_SCALAR_TAYLOR_V1',interval=14,stage='midpoint',
            original_domain_unchanged=True,endpoint_nonlinear_error_parameters_shared=True,
            parameter_groups=old['parameter_groups'],base_midpoint_record_SHA256=sha(direction_path),
            output_covector=adj['output_covector'],input_source_SHA256={**old['input_source_SHA256'],**sources,
                str((out/'refinement.json').resolve()):sha(out/'refinement.json')},Gate7_closed=False)
        reduced=Taylor(TaylorDomain(old['parameter_groups'],prior_n),original_scalar.c,
            arb_mat(1,prior_n,original_scalar.a.entries()[:prior_n]),new_radius)
        updated['scalar_model']=encode(reduced)
        (out/'record.json').write_bytes(p.geometry.encoded(updated))
        print(json.dumps(dict(completed=True,old_scalar_tail=float(original_scalar.r),new_scalar_tail=float(new_radius))),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','operands','predictors','base','direction','adjoint','out'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--workers',type=int,default=8)
    args=parser.parse_args();evaluate(args.evidence_root.resolve(),args.operands.resolve(),args.predictors.resolve(),
        args.base.resolve(),args.direction.resolve(),args.adjoint.resolve(),args.out.resolve(),args.workers)

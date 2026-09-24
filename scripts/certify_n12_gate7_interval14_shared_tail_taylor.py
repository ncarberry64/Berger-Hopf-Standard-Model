"""Midpoint direction with shared endpoint nonlinear-error parameters.

The midpoint direction may depend on the endpoint through u/2-h*DF*u/8.
Only nonlinear tails are hulled; the common affine parameters are retained.
This producer alone does not certify the final transported entry.
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


def evaluate(root,operands,predictors,base_path,out,endpoint_path=None,workers=1):
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
    import n12_gate7_parallel_scalar_taylor as parallel
    ctx.prec=512;p=engine.p;cert=p.values.cert;residual=p.geometry.residual
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
    def load(folder,name):
        record=json.loads((folder/'record.json').read_bytes())
        if sha(folder/name)!=record['data_SHA256']:raise ValueError('Verified operand bytes required')
        with np.load(folder/name,allow_pickle=False) as z:
            arrays={k[:-6]:p.hs.restore_balls(z[k],z[k[:-6]+'_rad_q']) for k in z.files if k.endswith('_mid_q')}
        return record,arrays
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with cache.cache_hashes(targets,excluded_roots=[out]):
        ore,a=load(operands,'operands.npz');pre,s=load(predictors,'predictors.npz')
        base=json.loads(base_path.read_bytes())
        if (pre['interval']!=14 or pre['stage']!=ore['report']['stage'] or pre['binding']!=ore['binding']
                or base['stage']!=pre['stage'] or base['interval']!=14
                or not base['original_domain_unchanged'] or not base['eigenpair_predictor_contained_in_original_box']):
            raise ValueError('Matching original interval-14 physical family required')
        if any(sha(Path(path))!=digest for path,digest in base['input_source_SHA256'].items()):
            raise ValueError('Base proof operands changed')
        p.verify_sources(ore['binding'])
        paths=[operands/'record.json',operands/'operands.npz',predictors/'record.json',
               predictors/'predictors.npz',base_path,Path(__file__),Path(arithmetic.__file__),
               Path(cert.__file__),Path(enclose_response_rows.__code__.co_filename),Path(parallel.__file__)]
        if endpoint_path is not None:paths.append(endpoint_path)
        sources={str(path.resolve()):sha(path) for path in paths}
        binding=hashlib.sha256(p.geometry.encoded(sources)).hexdigest().upper()
        out.mkdir(parents=True,exist_ok=True)
        manifest=out/'sources.json'
        if manifest.exists() and manifest.read_bytes()!=p.geometry.encoded(sources):
            raise ValueError('Checkpoint operands changed; use a fresh directory')
        if not manifest.exists():manifest.write_bytes(p.geometry.encoded(sources))
        original_n=s['weighted_tube_directions'].shape[1]
        if pre['stage']!='midpoint' or original_n!=249:
            raise ValueError('Original midpoint-14 parameter domain required')
        n=original_n+99
        domain=TaylorDomain(pre['parameter_groups']+[(original_n,n,'box')],n)
        _,weights,_,_,steps=p.values.operands();qw,rw,_,_=cert.metric_data()
        weights,qw,rw=[[arb(float(v)) for v in values] for values in (weights,qw,rw)]
        center=s['center_state'];directions=s['weighted_tube_directions']
        state=[domain.affine(center[i],[directions[i,j]/weights[i] for j in range(original_n)]+[arb(0)]*99) for i in range(98)]
        if any(not a['raw_domain'][i].contains(v.enclosure()) for i,v in enumerate(state)):
            raise ArithmeticError('Original complete state domain must be preserved')
        def decode(data,target=domain):
            values=[arb(m)+arb(0,arb(r)) for m,r in data]
            coefficients=values[1:-1]
            if target is domain and len(coefficients)==original_n:
                coefficients += [arb(0)]*99
            if len(coefficients)!=target.dimension:raise ValueError('Complete Taylor coefficient domain required')
            return Taylor(target,values[0],arb_mat(1,target.dimension,coefficients),values[-1])
        def encode(v):return [[str(x.mid().fmpq()),str(x.rad().fmpq())] for x in [v.c,*v.a.entries(),v.r]]
        ep=[arb(str(v)) for v in pre['point_checks'][0]['target_midpoints_rational']]
        def predictor(c,derivative,errors=None):
            return [domain.affine(v.mid(),[derivative[i,j].mid() for j in range(original_n)]+[arb(0)]*99,
                    0 if errors is None else arb(errors[i])) for i,v in enumerate(c)]
        psi=predictor(ep[:61],s['point_solve_3'][:61],base['eigenpair_error_upper_exact'])
        lp=decode(base['eigenvalue_predictor'])
        lam=Taylor(domain,lp.c,lp.a,arb(base['eigenpair_error_upper_exact'][61]))
        hard=predictor(s['point_solve_0'][:,0],s['point_solve_4'],base['response_error_upper_exact'])
        psi_u=predictor(s['point_solve_1'][:,0],s['point_solve_5'])
        hard_u=predictor(s['point_solve_2'][:,0],s['point_solve_6'])
        axis=[domain.affine(v) for v in s['input_axis_ball']]
        if pre['stage']=='midpoint':
            if endpoint_path is None:raise ValueError('Full endpoint direction Taylor enclosure required')
            endpoint=json.loads(endpoint_path.read_bytes())
            if (endpoint['stage']!='endpoint' or endpoint['interval']!=14
                    or not endpoint['original_domain_unchanged'] or len(endpoint['physical_derivative_models'])!=99):
                raise ValueError('Complete original endpoint directional model required')
            if any(sha(Path(path))!=digest for path,digest in endpoint['input_source_SHA256'].items()):
                raise ValueError('Endpoint directional enclosure inputs changed')
            endpoint_domain=TaylorDomain([(0,1,'interval'),(1,75,'euclidean')],75)
            def embed(value,component):
                coefficients=[arb(0)]*n
                coefficients[1]=value.a[0,0]
                coefficients[76:150]=value.a.entries()[1:]
                # The SAME error parameter is used again in the direct
                # endpoint term by the final scalar assembler. This preserves
                # its transport cancellation instead of summing two tails.
                coefficients[original_n+component]=value.r
                return domain.affine(value.c,coefficients)
            end_models=[embed(decode(value,endpoint_domain),i) for i,value in enumerate(endpoint['physical_derivative_models'])]
            end_axis=[arb(m)+arb(0,arb(r)) for m,r in endpoint['input_axis_ball']]
            h=arb(float(steps[14]))
            axis=[domain.affine(u/2)-h*df/8 for u,df in zip(end_axis,end_models,strict=True)]
            # The last 99 ORIGINAL midpoint parameters are scaled coordinate
            # directions. Their already verified point solves recover the full
            # linear operators, without another action derivative evaluation.
            for j in range(99):
                if directions[j,150+j].contains(0) or any(not directions[i,150+j].is_zero() for i in range(99) if i!=j):
                    raise ValueError('Original complete diagonal midpoint remainder directions required')
            delta=[v-s['weighted_input_axis'][i] for i,v in enumerate(axis)]
            for target,key in ((psi_u,'point_solve_1'),(hard_u,'point_solve_2')):
                for i in range(62):
                    change=sum((delta[j]*(a[key][i,150+j]/directions[j,150+j]) for j in range(99)),domain.affine(0))
                    # Arbitrary exact affine predictors are allowed; residuals
                    # below enclose discarded tails and coefficient uncertainty.
                    old=target[i]+change
                    target[i]=domain.affine(old.c.mid(),[v.mid() for v in old.a.entries()])
        elif endpoint_path is not None:raise ValueError('Endpoint cannot depend on itself')
        raw_axis=[axis[i]/weights[i] for i in range(98)]
        dot=lambda x,y:sum((u*v for u,v in zip(x,y,strict=True)),arb(0))
        pad=lambda v:[arb(0)]*37+list(v[:61])
        maps=[cert._dense_mapping(cert._integrand(center,node,0).maps) for node in range(cert.POINTS)]
        def action(name,legs):
            path=out/(name+'.json')
            if path.exists():
                record=json.loads(path.read_bytes())
                if record['binding']!=binding:raise ValueError('Immutable action checkpoint required')
                value=decode(record['values'])
            else:
                with scalar_taylor_action(cert):
                    value=cert._contracted_action(np.array(state,dtype=object),[np.array(v,dtype=object) for v in legs],maps)
                if isinstance(value,arb):value=domain.affine(value)
                path.write_bytes(p.geometry.encoded(dict(binding=binding,values=encode(value))))
            print(json.dumps(dict(stage=pre['stage'],term=name,nonlinear_upper=float(value.r))),flush=True)
            return value
        R=a['paired_rm'];weights_solve=a['paired_radii'];variation=a['paired_variation']
        def errors(models):
            forcing=np.array([v.support() for v in models],dtype=object)
            _,proof=enclose_response_rows(np.array([arb(0)]*62,dtype=object),forcing,weights_solve,variation)
            return [arb(x) for x in proof['component_radii_upper_rational']],proof
        slope=action('axis_eigenvalue',[pad(psi),pad(psi),raw_axis])
        legs=dict(psi=pad(psi),psi_u=pad(psi_u),axis=raw_axis)
        tasks=[]
        for i in range(62):
            legs[f'v{i}']=pad(list(R[i,:61]))
            tasks.extend([(f'axis_line_{i:02d}_matrix',[f'v{i}','psi_u']),
                          (f'axis_line_{i:02d}_source',[f'v{i}','psi','axis'])])
        parallel.precompute(root,domain,state,legs,tasks,binding,out,workers)
        residuals=[]
        for i in range(62):
            v=list(R[i,:61]);bottom=R[i,61]
            g=(action(f'axis_line_{i:02d}_matrix',[pad(v),pad(psi_u)])-lam*dot(v,psi_u[:61])
                +psi_u[61]*dot(v,psi)+action(f'axis_line_{i:02d}_source',[pad(v),pad(psi),raw_axis])
                -slope*dot(v,psi)+bottom*dot(psi,psi_u[:61]))
            residuals.append(g)
        line_error,line_proof=errors(residuals)
        psi_u=[Taylor(domain,v.c,v.a,line_error[i]) for i,v in enumerate(psi_u)]
        configuration=[qw[i]*state[37+i] for i in range(37)]
        configuration_u=[qw[i]*raw_axis[37+i] for i in range(37)]
        d=[configuration[i]/weights[i] for i in range(37)]+[arb(0)]*61
        du=[configuration_u[i]/weights[i] for i in range(37)]+[arb(0)]*61
        legs=dict(hard=pad(hard),hard_u=pad(hard_u),axis=raw_axis,d=d,du=du)
        tasks=[]
        for i in range(62):
            v=list(R[i,:61]);legs[f'v{i}']=pad(v)
            legs[f'g{i}']=[v[j]*rw[j]*qw[j]/weights[j] for j in range(37)]+[arb(0)]*61
            legs[f'c{i}']=[arb(0)]*37+[v[j]*rw[j]/weights[37+j] for j in range(61)]
            tasks.extend([(f'axis_response_{i:02d}_gradient',[f'g{i}','axis']),
                (f'axis_response_{i:02d}_source',[f'c{i}','d','axis']),
                (f'axis_response_{i:02d}_configuration',[f'c{i}','du']),
                (f'axis_response_{i:02d}_matrix',[f'v{i}','hard_u']),
                (f'axis_response_{i:02d}_matrix_source',[f'v{i}','hard','axis'])])
        parallel.precompute(root,domain,state,legs,tasks,binding,out,workers)
        residuals=[]
        for i in range(62):
            v=list(R[i,:61]);bottom=R[i,61]
            gl=[v[j]*rw[j]*qw[j]/weights[j] for j in range(37)]+[arb(0)]*61
            cl=[arb(0)]*37+[v[j]*rw[j]/weights[37+j] for j in range(61)]
            fu=(action(f'axis_response_{i:02d}_gradient',[gl,raw_axis])
                -action(f'axis_response_{i:02d}_source',[cl,d,raw_axis])
                -action(f'axis_response_{i:02d}_configuration',[cl,du]))
            g=(action(f'axis_response_{i:02d}_matrix',[pad(v),pad(hard_u)])-lam*dot(v,hard_u[:61])
                +hard_u[61]*dot(v,psi)+action(f'axis_response_{i:02d}_matrix_source',[pad(v),pad(hard),raw_axis])
                -slope*dot(v,hard[:61])+hard[61]*dot(v,psi_u[:61])-fu
                +bottom*(dot(psi,hard_u[:61])+dot(psi_u[:61],hard[:61])))
            residuals.append(g)
        response_error,response_proof=errors(residuals)
        hard_u=[Taylor(domain,v.c,v.a,response_error[i]) for i,v in enumerate(hard_u)]
        parameter_s=domain.affine(s['point_descriptor'][0],[directions[98,j] for j in range(original_n)]+[arb(0)]*99)
        su=axis[98]
        scale=lambda vec:[rw[i]/weights[37+i]*vec[i] for i in range(61)]
        pp,pu=pad(psi),pad(psi_u);aa,au=pad(scale(psi)),pad(scale(psi_u))
        dd=[configuration[i]/weights[i] for i in range(37)]+scale(hard)
        ddu=[configuration_u[i]/weights[i] for i in range(37)]+scale(hard_u)
        cp=action('descriptor_c',[pp,pp,aa]);rem=action('descriptor_r',[pp,pp,dd])
        cu=(action('descriptor_cu_4',[pp,pp,aa,raw_axis])+2*action('descriptor_cu_3a',[pp,pu,aa])
            +action('descriptor_cu_3b',[pp,pp,au]))
        ru=(action('descriptor_ru_4',[pp,pp,dd,raw_axis])+2*action('descriptor_ru_3a',[pp,pu,dd])
            +action('descriptor_ru_3b',[pp,pp,ddu]))
        N=[parameter_s*x for x in configuration]+[rw[i]*(hard[61]*psi[i]+parameter_s*hard[i]) for i in range(61)]
        Nu=[su*x+parameter_s*y for x,y in zip(configuration,configuration_u,strict=True)]
        Nu += [rw[i]*(hard_u[61]*psi[i]+hard[61]*psi_u[i]+su*hard[i]+parameter_s*hard_u[i]) for i in range(61)]
        delta=hard[61]*cp+parameter_s*rem
        delta_u=hard_u[61]*cp+hard[61]*cu+su*rem+parameter_s*ru
        norm_squared=dot(N,N)
        if not norm_squared.enclosure()>0:
            (out/'normalization_failure.json').write_bytes(p.geometry.encoded(dict(
                norm_squared_model=encode(norm_squared),uniform_entry_remainder_certified=False)))
            raise ArithmeticError('Original-domain normalization lower bound not established by this enclosure')
        norm=(norm_squared.log()/2).exp();normalization_variation=dot(N,Nu)/norm**3
        output=[v/norm-u*normalization_variation for u,v in zip(N+[delta],Nu+[delta_u],strict=True)]
        result=dict(algorithm='INTERVAL14_ORIGINAL_DOMAIN_SHARED_DIRECTION_TAYLOR_V1',
            stage=pre['stage'],interval=14,parameter_groups=domain.groups,
            original_physical_parameter_groups=pre['parameter_groups'],
            endpoint_nonlinear_error_parameters_shared=True,
            endpoint_error_parameter_start=original_n,endpoint_error_parameter_count=99,
            original_domain_unchanged=True,shared_state_coefficients_preserved=True,
            variable_endpoint_chain_included=pre['stage']=='midpoint',
            input_axis_ball=[[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in s['input_axis_ball']],
            axis_line_error_upper_exact=[str(v.fmpq()) for v in line_error],
            axis_response_error_upper_exact=[str(v.fmpq()) for v in response_error],
            axis_line_proof=line_proof,axis_response_proof=response_proof,
            implicit_models=[encode(v) for v in psi+[lam]+hard+psi_u+hard_u],
            input_axis_models=[encode(v) for v in axis],
            physical_derivative_models=[encode(v) for v in output],
            physical_derivative_remainder_max=float(max(v.r for v in output)),
            norm_squared_lower_exact=str(norm_squared.enclosure().lower().fmpq()),
            input_source_SHA256=sources,interval13_recomputed=False,
            final_entry_remainder_certified=False,Gate7_closed=False)
        if any(sha(Path(path))!=digest for path,digest in sources.items()):raise ValueError('Source changed during proof')
        (out/'record.json').write_bytes(p.geometry.encoded(result))
        print(json.dumps(dict(stage=pre['stage'],completed=True,
            physical_derivative_remainder_max=result['physical_derivative_remainder_max'])),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','operands','predictors','base','out'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--endpoint',type=Path)
    parser.add_argument('--workers',type=int,default=1)
    args=parser.parse_args()
    evaluate(args.evidence_root.resolve(),args.operands.resolve(),args.predictors.resolve(),
             args.base.resolve(),args.out.resolve(),None if args.endpoint is None else args.endpoint.resolve(),args.workers)

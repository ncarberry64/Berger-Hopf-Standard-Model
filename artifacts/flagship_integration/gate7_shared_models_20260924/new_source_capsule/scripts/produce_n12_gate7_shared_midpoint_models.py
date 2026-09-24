"""Actual HS midpoint graph, retaining both serialized endpoint histories."""
import argparse,json
from pathlib import Path
import numpy as np
from flint import arb,ctx,fmpq
import regenerate_n12_gate7_shared_site_models as base
import produce_n12_gate7_shared_models as producer
from bhsm.interface.disk_expression_graph import DiskExpressionDomain
from bhsm.interface.shared_history_expression import point_history
from bhsm.interface.streamed_expression_artifact import read_graph
from bhsm.interface.certified_expression_constraints import install
from bhsm.interface.shared_expression_graph import pair
from bhsm.interface.disk_affine_cache import DiskAffineCache


def setup(evidence,left,right):
    charts,rates,step,atlas,sources,descriptors=base.inherited.operands(evidence,13)
    metadata=[read_graph(p) for p in (left,right)]
    for side,z in zip(('left','right'),metadata):
        if z['site']!=side or z['interval']!=13 or z['radius_exact']!=atlas['radius_exact']:
            raise ValueError('same interval-13 endpoint graphs required')
        for p,h in z['source_SHA256'].items():
            if base.sha(Path(p))!=h:raise ValueError('endpoint shared-model input changed')
    d=DiskExpressionDomain([tuple(g) for g in metadata[0]['groups']],metadata[0]['parameter_order']);d.flatten_limit=32
    d.bounds=DiskAffineCache(d.backend)
    with np.load(Path(base.inputs.action.ENDPOINT).with_suffix('.npz'),allow_pickle=False) as z:
        weights=[arb(float(x)) for x in z['state_weights']]
    history,endpoints,_=point_history(d,left,right,weights,step,arb(1)/2,metadata)
    folder=evidence/'artifacts/flagship_integration'
    facts={}
    for side,n in enumerate((13,14)):
        header,path=base.inputs.import_domain(folder/f'.coupled_normalized_physical_value_work/endpoint_{n:03d}','value.npz',sources)
        if not header['report']['uniform_physical_value_enclosed']:raise ValueError('same-family endpoint value authority required')
        with np.load(path,allow_pickle=False) as data:bounds=base.inputs.read_array(data,'rate_candidate')
        for i,bound in enumerate(bounds):
            facts[str(endpoints[side][f'rate/value/{i}'].index)]={'ball':pair(bound),
                'role':'frozen_same_family_endpoint_rate_value','endpoint':n,'component':i,
                'data_path':str(path.resolve()),'data_SHA256':base.sha(path),'physical_radii_unchanged':True}
    install(d,facts)
    eh,ep=base.inputs.import_domain(folder/'.coupled_midpoint_eigenpair_pilot_work/interval_013','eigenpair.npz',sources)
    vh,vp=base.inputs.import_domain(folder/'.coupled_midpoint_physical_value_work/interval_013','value.npz',sources)
    dh,dp=base.inputs.import_domain(folder/'.coupled_midpoint_uniform_df_work/interval_013','derivative.npz',sources)
    if not all(z['report']['validation_passed'] for z in (eh,vh,dh)):raise ValueError('certified actual-HS site required')
    trial=next(i for i,t in enumerate(eh['report']['trials']) if t['validation_passed'])
    with np.load(ep,allow_pickle=False) as z:
        eig=base.inputs.read_array(z,'eigenpair_box');w=base.inputs.read_array(z,f'trial_{trial}_radii');V=base.inputs.read_array(z,f'trial_{trial}_variation_bounds');R=base.inputs.read_array(z,'preconditioner')
    with np.load(vp,allow_pickle=False) as z:response=base.inputs.read_array(z,'response_box')
    with np.load(dp,allow_pickle=False) as z:
        pre=base.inputs.read_array(z,'preconditioned_variation_rhs');A=base.inputs.read_array(z,'derivative')
    q=max((a/b).upper() for a,b in zip(V,w))
    if not 0<=q<1 or not response[-1].lower()>0:raise ValueError('frozen midpoint inverse and positive common border required')
    s={'domain':d,'state':history['value'][:98],'u':history['u'][:98],'v':history['v'][:98],
       'history':history,'endpoints':endpoints,'frozen_DF':A,
       'psi':{'value':[d.affine(x,provenance={'role':'inherited_midpoint_eigenline','row':i,'dependency_unresolved':True}) for i,x in enumerate(eig[:61])]},
       'response':{'value':[d.affine(x,provenance={'role':'inherited_midpoint_response','row':i,'dependency_unresolved':True}) for i,x in enumerate(response)]},
       'descriptor':{'value':history['value'][98],'u':history['u'][98],'v':history['v'][98],'uv':d.affine(0)},
       'R':[[d.affine(R[i,j]*(-1 if i==61 else 1),provenance={'role':'frozen_midpoint_inverse','row':i,'column':j}) for j in range(62)] for i in range(62)],
       'weights':weights,'w':list(w),'q':q,'b_lower':response[-1].lower(),
       'sources':sources,'radius_exact':atlas['radius_exact'],'site':'middle','step':step}
    for block,size,name in ((0,61,'psi'),(1,62,'response')):
        alpha=[]
        for batch in dh['report']['coupled_inverse_bounds']:
            alpha.extend(arb(fmpq(a['weighted_error_upper_rational'])) for a in batch['solve_bounds'][block])
        if len(alpha)!=99:raise ValueError('complete midpoint first-derivative certificate required')
        coeff=[[d.affine((pre[block,i,j]+arb(0,(V[i]*alpha[j]).upper()))*(-1 if i==61 else 1),
            provenance={'role':'inherited_midpoint_first_derivative','quantity':name,'row':i,'column':j,'dependency_unresolved':True}) for j in range(99)] for i in range(size)]
        for key in ('u','v'):
            weighted=[x*(weights[i] if i<98 else 1) for i,x in enumerate(history[key])]
            s[name][key]=[sum((a*b for a,b in zip(row,weighted)),d.affine(0)) for row in coeff]
    qw,rw,_,_=base.inputs.action.metric_data();s['qw']=[arb(float(x)) for x in qw];s['rw']=[arb(float(x)) for x in rw]
    for p in (left,right,Path(__file__),base.ROOT/'src/bhsm/interface/shared_history_expression.py',
              base.ROOT/'src/bhsm/interface/streamed_expression_artifact.py',base.ROOT/'src/bhsm/interface/shared_mixed_rate_graph.py',
              base.ROOT/'src/bhsm/interface/certified_expression_constraints.py',
              base.ROOT/'src/bhsm/interface/disk_affine_cache.py',
              base.ROOT/'src/bhsm/interface/shared_expression_graph.py',base.ROOT/'src/bhsm/interface/sparse_affine_enclosure.py',
              base.ROOT/'src/bhsm/interface/shared_action_gradient.py',base.ROOT/'src/bhsm/interface/uniform_action_contraction.py'):
        sources[str(p.resolve())]=base.sha(p)
    return s


def run(args):
    original_setup,original_mixed=base.setup,base.mixed_graph
    def setup_adapter(evidence,site):return setup(evidence,args.left.resolve(),args.right.resolve())
    def mixed_adapter(evaluate,solve,s):
        rate,roots=original_mixed(evaluate,solve,s);d=s['domain'];A=s['frozen_DF']
        second=[x*(s['weights'][i] if i<98 else 1) for i,x in enumerate(s['history']['uv'])]
        incidence=[]
        for i in range(99):
            row=[d.affine(A[i,j],provenance={'role':'inherited_midpoint_DF','row':i,'column':j,'dependency_unresolved':True}) for j in range(99)]
            term=sum((a*b for a,b in zip(row,second)),d.affine(0));incidence.append(term)
            roots[f'physical_field_hessian/{i}']=rate['uv'][i]
            roots[f'nonaffine_midpoint_incidence/{i}']=term
            rate['uv'][i]+=term;roots[f'rate/uv/{i}']=rate['uv'][i]
        for key,vec in s['history'].items():
            for i,x in enumerate(vec):roots[f'history/{key}/{i}']=x
        for side,endpoint in zip(('left','right'),s['endpoints']):
            for name,x in endpoint.items():roots[f'endpoint_{side}/{name}']=x
        return rate,roots
    base.setup,base.mixed_graph=setup_adapter,mixed_adapter
    args.site='middle'
    try:producer.run(args)
    finally:base.setup,base.mixed_graph=original_setup,original_mixed


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--left',type=Path,required=True);p.add_argument('--right',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--previous',type=Path,nargs='*',default=[])
    run(p.parse_args())

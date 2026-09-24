"""Authorized regeneration of never-serialized interval-13 mixed graphs.

Inherited domains, values, first derivatives and inverse certificates are
read-only. Only missing shared action expressions are evaluated. New action
blocks are restart-safe; a repeat must use a distinct empty work directory.
"""
import argparse,gzip,hashlib,json,os,sys
from pathlib import Path
import numpy as np
from flint import arb,arb_mat,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_augmented_tube_domain as inherited
from bhsm.interface.shared_expression_graph import ExpressionDomain,Expression,pair
from bhsm.interface.shared_mixed_rate_graph import mixed_graph
from bhsm.interface.shared_action_gradient import gradient
from bhsm.interface.uniform_action_contraction import contract
inputs=inherited.inputs


def encode(z):return (json.dumps(z,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def fresh(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError(str(path))
    pending=path.with_suffix(path.suffix+'.pending')
    pending.write_bytes(data);os.replace(pending,path)


def setup(evidence,site):
    charts,rates,step,atlas,sources,descriptors=inherited.operands(evidence,13)
    base=evidence/'artifacts/flagship_integration'
    names=[f'{family}/endpoint{n}/{"L" if j==0 else "T"+str(j)}' for family in ('theta','u','v') for n in (13,14) for j in range(75)]
    groups=[g for k in range(0,450,75) for g in ((k,k+1,'interval'),(k+1,k+75,'euclidean'))]
    d=ExpressionDomain(groups,names)
    with np.load(Path(inputs.action.ENDPOINT).with_suffix('.npz'),allow_pickle=False) as z:
        weights=[arb(float(x)) for x in z['state_weights']]
    side=0 if site=='left' else 1;n=13+side
    if site not in ('left','right'):raise ValueError('endpoint import required; midpoint must consume both serialized endpoint graphs')
    eh,ep=inputs.import_domain(base/f'.affine_eigenpair_pilot_work/endpoint_{n:03d}','eigenpair.npz',sources)
    vh,vp=inputs.import_domain(base/f'.affine_physical_value_pilot_work/endpoint_{n:03d}','value.npz',sources)
    dh,dp=inputs.import_domain(base/f'.coupled_endpoint_uniform_df_work/endpoint_{n:03d}','derivative.npz',sources)
    if not all(z['report']['validation_passed'] for z in (eh,vh,dh)):raise ValueError('certified imported site required')
    trial=next(i for i,t in enumerate(eh['report']['trials']) if t['validation_passed'])
    with np.load(ep,allow_pickle=False) as z:
        eig=inputs.read_array(z,'eigenpair_box');w=inputs.read_array(z,f'trial_{trial}_radii');V=inputs.read_array(z,f'trial_{trial}_variation_bounds')
        preconditioner=inputs.read_array(z,'preconditioner')
    with np.load(vp,allow_pickle=False) as z:response=inputs.read_array(z,'response_box')
    with np.load(dp,allow_pickle=False) as z:pre=inputs.read_array(z,'preconditioned_variation_rhs')
    q=max((a/b).upper() for a,b in zip(V,w))
    if not 0<=q<1 or not response[-1].lower()>0:raise ValueError('frozen inverse and positive common border required')
    R=[[d.affine(preconditioner[i,j]*(-1 if i==61 else 1),provenance={'role':'frozen_inverse','site':site,'row':i,'column':j}) for j in range(62)] for i in range(62)]
    E=[[charts[2*side]['scaled'][i][j]*weights[i] if i<98 else descriptors[side]['scaled'][j] for j in range(75)] for i in range(99)]
    def mapped(row,block,center=0,label='physical_map'):
        a=[arb(0)]*450;a[block+75*side:block+75*side+75]=row
        return d.affine(center,a,provenance={'role':label,'site':site,'source':'frozen endpoint map','parameter_block':block})
    weighted_u=[mapped(row,150,label='physical_direction_u') for row in E]
    weighted_v=[mapped(row,300,label='physical_direction_v') for row in E]
    state=[mapped(charts[2*side]['scaled'][i],0,charts[2*side]['x'][i],'endpoint_state') for i in range(98)]
    s={'domain':d,'state':state,'u':[weighted_u[i]/weights[i] for i in range(98)],'v':[weighted_v[i]/weights[i] for i in range(98)],
       'psi':{'value':[d.affine(x,provenance={'role':'inherited_eigenline_value','site':site,'row':i,'dependency_unresolved':True}) for i,x in enumerate(eig[:61])]},
       'response':{'value':[d.affine(x,provenance={'role':'inherited_response_value','site':site,'row':i,'dependency_unresolved':True}) for i,x in enumerate(response)]},
       'descriptor':{'value':mapped(E[98],0,descriptors[side]['center'],'descriptor_state'),'u':weighted_u[98],'v':weighted_v[98],'uv':d.affine(0)},
       'b_lower':response[-1].lower(),'R':R,'weights':weights,'w':list(w),'q':q,
       'sources':sources,'radius_exact':atlas['radius_exact'],'site':site,'step':step}
    # The same pointwise derivative coefficient object is used for u and v.
    # Its inherited enclosure still lacks explicit dependence on theta; that
    # unresolved input correlation is preserved in the provenance ledger.
    for block,size,name in ((0,61,'psi'),(1,62,'response')):
        alpha=[]
        for batch in dh['report']['coupled_inverse_bounds']:
            alpha.extend(arb(fmpq(a['weighted_error_upper_rational'])) for a in batch['solve_bounds'][block])
        if len(alpha)!=99:raise ValueError('complete first derivative coverage required')
        coeff=[[d.affine((pre[block,i,j]+arb(0,(V[i]*alpha[j]).upper()))*(-1 if i==61 else 1),
            provenance={'role':'inherited_first_derivative','quantity':name,'site':site,'row':i,'column':j,'dependency_unresolved':True}) for j in range(99)] for i in range(size)]
        for key,direction in (('u',weighted_u),('v',weighted_v)):
            s[name][key]=[sum((x*y for x,y in zip(row,direction)),d.affine(0)) for row in coeff]
    qw,rw,_,_=inputs.action.metric_data();s['qw']=[arb(float(x)) for x in qw];s['rw']=[arb(float(x)) for x in rw]
    if any(not x>=1 for x in s['rw']):raise ValueError('common-border metric identity requires weights >=1')
    modules=[Path(__file__),ROOT/'src/bhsm/interface/shared_expression_graph.py',ROOT/'src/bhsm/interface/sparse_affine_enclosure.py',
        ROOT/'src/bhsm/interface/shared_mixed_rate_graph.py',ROOT/'src/bhsm/interface/shared_action_gradient.py',ROOT/'src/bhsm/interface/uniform_action_contraction.py']
    sources.update({str(p.resolve()):sha(p) for p in modules})
    return s


class Evaluator:
    def __init__(self,s,work):self.s,self.work,self.receipts=s,work,[]
    def calculate(self,legs,all_rows):
        d=self.s['domain'];legs=[[d.coerce(x) for x in leg] for leg in legs]
        if any(all(d.nodes[x.index]==['constant','0'] for x in leg) for leg in legs):
            return [d.affine(0)]*98 if all_rows else d.affine(0)
        key=hashlib.sha256(encode({'gradient':all_rows,'legs':[[x.index for x in leg] for leg in legs],
            'state':[x.index for x in self.s['state']],'prefix':d.digest.hexdigest(),'sources':self.s['sources']})).hexdigest()
        path=self.work/(key+'.json.gz');start=len(d.nodes);before=d.digest.hexdigest()
        if path.exists():
            record=json.loads(gzip.decompress(path.read_bytes()))
            if record['prefix']!=before or record['start']!=start:raise ValueError('shared action cache belongs to another graph')
            for i,n in enumerate(record['nodes'],start):
                if d.node(n).index!=i:raise ValueError('shared cache node identity mismatch')
            d.leaf_provenance.update(record['leaf_provenance'])
            values=[Expression(d,i) for i in record['roots']]
            phase='REUSE_NEW_SERIALIZED_ACTION'
        else:
            print(json.dumps({'phase':'NEW_MISSING_SHARED_ACTION','order':len(legs)+int(all_rows),'gradient':all_rows,'key':key[:12]}),flush=True)
            progress=lambda done,total:print(json.dumps({'phase':'quadrature','done':done,'total':total,'nodes':len(d.nodes)}),flush=True)
            values=gradient(inputs.action,self.s['state'],legs,progress) if all_rows else [contract(inputs.action,self.s['state'],legs,progress)[0]]
            record={'prefix':before,'start':start,'nodes':d.nodes[start:],'roots':[x.index for x in values],
                'leaf_provenance':{k:v for k,v in d.leaf_provenance.items() if int(k)>=start}}
            fresh(path,gzip.compress(encode(record),mtime=0));phase='SAVED_NEW_SHARED_ACTION'
        self.receipts.append({'file':path.name,'SHA256':sha(path),'new_derived_evidence':True})
        print(json.dumps({'phase':phase,'key':key[:12],'nodes':len(d.nodes)}),flush=True)
        return values if all_rows else values[0]
    def __call__(self,legs):return self.calculate(legs,False)
    def gradient(self,legs):return self.calculate(legs,True)


def run(evidence,site,work,out):
    if out.exists():raise FileExistsError('fresh final artifact required')
    ctx.prec=512;work.mkdir(parents=True,exist_ok=True);s=setup(evidence,site);d=s['domain']
    manifest={'sources':s['sources'],'site':site,'interval':13,'radius_exact':s['radius_exact'],'parameter_order':d.names,'groups':d.groups}
    mp=work/'immutable_inputs.json';data=encode(manifest)
    if mp.exists():
        if mp.read_bytes()!=data:raise ValueError('immutable new-derived input receipt changed')
    else:fresh(mp,data)
    def solve(rhs,label,roots):
        proposal=[sum((a*b for a,b in zip(row,rhs)),d.affine(0)) for row in s['R']]
        for i,x in enumerate(rhs):roots[f'{label}/rhs/{i}']=x
        print(json.dumps({'phase':'BOUND_NEW_IMPLICIT_CORRECTION','quantity':label,'nodes':len(d.nodes)}),flush=True)
        alpha=max((x.support()/w).upper() for x,w in zip(proposal,s['w']))
        error=(alpha*s['q']/(1-s['q'])).upper()
        return [x+d.affine(0,remainder=(w*error).upper(),provenance={'role':'new_implicit_remainder','quantity':label,'row':i,
            'formula':'w_i*q/(1-q)*norm_w(R rhs)','q_exact':str(s['q'].fmpq()),'dependency_unresolved':True}) for i,(x,w) in enumerate(zip(proposal,s['w']))]
    evaluate=Evaluator(s,work);rate,roots=mixed_graph(evaluate,solve,s)
    roots.update({f'endpoint/state/{i}':x for i,x in enumerate(s['state'])})
    print(json.dumps({'phase':'SERIALIZE_COMPLETE_NEW_GRAPH','nodes':len(d.nodes),'roots':len(roots)}),flush=True)
    # Save the exact graph first, independently of the chosen support method.
    graph=d.export(roots,include_bounds=False)
    graph.update({'interval':13,'site':site,'radius_exact':s['radius_exact'],'source_SHA256':s['sources'],
        'new_action_receipts':evaluate.receipts,'frozen_checkpoint':'baf41b96','correlation_audit':'f5b6b4b6',
        'inherited_certificates_recomputed':False,'physical_budget_debit':False,'Gate7_closed':False,
        'remaining_input_relaxations':['inherited primal value dependence on theta','inherited first derivative coefficient dependence on theta','implicit correction tails'],
        'full_correlated_Layer_C_certified':False})
    if any(sha(Path(p))!=h for p,h in s['sources'].items()):raise ValueError('frozen input changed during derived calculation')
    fresh(out,gzip.compress(encode(graph),mtime=0))
    print(json.dumps({'phase':'GRAPH_SAVED','SHA256':sha(out),'nodes':len(d.nodes)}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--site',choices=('left','right'),required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.site,a.work.resolve(),a.out.resolve())

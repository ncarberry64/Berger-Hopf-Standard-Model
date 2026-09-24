"""Eight restrictions of one shared Hermite history, with immutable parents.

This localizes the actual dense-output history jets. It does not replace the
three-site HS residual by a sum of eight copies, or identify interpolant
velocity with the ODE right-hand side at every dense time.
"""
import argparse,json
from pathlib import Path
import numpy as np
from flint import arb,ctx,fmpq
import regenerate_n12_gate7_shared_site_models as base
from bhsm.interface.shared_expression_graph import ExpressionDomain,restore
from bhsm.interface.adaptive_expression_reader import read_graph
from bhsm.interface.shared_hs_physical_pullback import dense_incidence


def descriptor_model(path,metadata):
    indices=[int(i) for i,p in metadata['leaf_provenance'].items() if p.get('role')=='descriptor_state']
    if len(indices)!=1:raise ValueError('one endpoint descriptor map required')
    target=indices[0];found={}
    class Finished(Exception):pass
    def visit(i,node):
        if i==target:
            if node[0]!='leaf':raise ValueError('affine descriptor map required')
            found.update(c=node[2],a=node[3],r=node[4]);raise Finished
    try:read_graph(path,visit)
    except Finished:pass
    if not found:raise ValueError('descriptor source node not found')
    return target,found


def run(evidence,left,right,middle,out):
    ctx.prec=512
    if out.exists():raise FileExistsError('fresh cell artifact directory required')
    package=base.ROOT/'artifacts/flagship_integration/gate7_physical_tube_20260924/interval_013'
    atlas=json.loads((package/'certificate.json').read_bytes());receipt=json.loads((package/'reproduction.json').read_bytes())
    if receipt['certificate_SHA256']!=base.sha(package/'certificate.json') or not atlas['complete_physical_tube_cover_certified']:
        raise ValueError('frozen complete Layer-B cover required')
    metadata=[read_graph(p) for p in (left,right,middle)]
    if [z['site'] for z in metadata]!=['left','right','middle'] or any(z['radius_exact']!=atlas['radius_exact'] for z in metadata):
        raise ValueError('matching unchanged interval-13 shared models required')
    _,_,step,_,sources,_=base.inherited.operands(evidence,13)
    with np.load(Path(base.inputs.action.ENDPOINT).with_suffix('.npz'),allow_pickle=False) as z:
        weights=[arb(float(x)) for x in z['state_weights']]
    desc=[descriptor_model(p,z) for p,z in zip((left,right),metadata)]
    parent_hashes={site:base.sha(p) for site,p in zip(('left','right','middle'),(left,right,middle))}
    for p in (left,right,middle,Path(__file__),package/'certificate.json',package/'reproduction.json',
              base.ROOT/'src/bhsm/interface/shared_expression_graph.py',base.ROOT/'src/bhsm/interface/sparse_affine_enclosure.py',
              base.ROOT/'src/bhsm/interface/shared_hs_physical_pullback.py',base.ROOT/'src/bhsm/interface/streamed_expression_artifact.py',
              base.ROOT/'src/bhsm/interface/adaptive_expression_reader.py'):
        sources[str(p.resolve())]=base.sha(p)
    out.mkdir(parents=True)
    for cell in atlas['cells']:
        index=cell['cell'];names=list(metadata[0]['parameter_order'])+[f'local_time/cell{index}']
        d=ExpressionDomain([tuple(g) for g in metadata[0]['groups']]+[(450,451,'interval')],names)
        cache={}
        def linked(side,root,model=None,node=None):
            z=metadata[side];site=('left','right')[side]
            if node is None:node=z['roots'][root]
            identity=(side,node)
            if identity not in cache:
                m=z['affine_enclosures'][root] if model is None else model
                a=[arb(0)]*451
                for i,v in m['a']:a[i]=restore(v)
                cache[identity]=d.affine(restore(m['c']),a,arb(fmpq(m['r'])),provenance={
                    'role':'external_shared_expression','parent_SHA256':parent_hashes[site],
                    'parent_site':site,'parent_root':root if root in z['roots'] else None,
                    'source_label':root,'parent_node':node,
                    'interpretation':'the same referenced physical function in every cell; not an independent local error'})
            return cache[identity]
        states=[];fields=[]
        for side,z in enumerate(metadata[:2]):
            state={'value':[linked(side,f'endpoint/state/{i}') for i in range(98)],'u':[],'v':[],'uv':[d.affine(0)]*99}
            node,model=desc[side];state['value'].append(linked(side,'descriptor/state',model,node))
            for i in range(99):
                m=z['affine_enclosures'][f'endpoint/state/{i}'] if i<98 else model
                if m['r']!='0' or any(j>=150 for j,_ in m['a']):raise ValueError('frozen affine endpoint state required')
                for key,offset in (('u',150),('v',300)):
                    a=[arb(0)]*451
                    for j,value in m['a']:a[j+offset]=restore(value)
                    state[key].append(d.affine(0,a,provenance={'role':'endpoint_state_direction','site':side,'row':i,'direction':key}))
            states.append(state)
            fields.append({key:[linked(side,f'rate/{key}/{i}')/(weights[i] if i<98 else 1) for i in range(99)] for key in ('value','u','v','uv')})
        low,high=[arb(fmpq(v)) for v in cell['tau_exact']]
        tau=d.variable(450,(low+high)/2,(high-low)/2,provenance={'role':'time_localization','global_tau_exact':cell['tau_exact']})
        history=dense_incidence(tau,step,*states,*fields)
        roots={f'history/{key}/{i}':x for key,vec in history.items() for i,x in enumerate(vec)}
        coefficients=((-6*tau+6*tau**2)/step,(6*tau-6*tau**2)/step,1-4*tau+3*tau**2,-2*tau+3*tau**2)
        for key in ('value','u','v','uv'):
            for i in range(99):
                roots[f'dense_velocity/{key}/{i}']=sum((a*jet[key][i] for a,jet in zip(coefficients,states+fields)),d.affine(0))
        result={'format':'LINKED_SHARED_HISTORY_CELL_V1','interval':13,'cell':index,'radius_exact':atlas['radius_exact'],
            'frozen_cover_cell':cell,'frozen_cover_SHA256':base.sha(package/'certificate.json'),
            'common_parent_graphs_SHA256':parent_hashes,'local_model':d.export(roots),
            'parameter_identity_across_cells':'first 450 symbols are common; local time maps to the recorded global tau interval',
            'source_SHA256':sources,'dense_history_and_all_first_mixed_incidence_included':True,
            'inherited_chart_identity_and_handoff_recomputed':False,'physical_radii_changed':False,
            'HS_physical_rate_evaluation_sites':['endpoint13','actual_HS_midpoint13','endpoint14'],
            'shared_HS_rate_model_references':{site:{'parent_SHA256':parent_hashes[site],
                'shared_parameter_indices':[0,450],'rate_jet_roots':{key:[f'rate/{key}/{i}' for i in range(99)] for key in ('value','u','v','uv')},
                'all_eigenline_response_descriptor_normalization_roots_retained_in_parent':True}
                for site in ('left','middle','right')},
            'aggregation':'restrictions of one history; the discrete HS residual is evaluated once',
            'arbitrary_dense_time_ODE_rhs_Hessian_claimed':False,
            'physical_budget_debit':False,'Gate7_closed':False}
        base.fresh(out/f'cell_{index:02d}.json',base.encode(result))
    if any(base.sha(Path(p))!=h for p,h in sources.items()):raise ValueError('cell source changed')
    print(json.dumps({'cells':8,'new_action_evaluations':0,'shared_parent_graphs':parent_hashes}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    for name in ('left','right','middle','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.left.resolve(),a.right.resolve(),a.middle.resolve(),a.out.resolve())

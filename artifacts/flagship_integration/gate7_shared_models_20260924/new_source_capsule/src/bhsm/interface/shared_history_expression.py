"""Import shared endpoint graphs and retain the exact cubic history jets.

Time-cell localization changes only the time coordinate. Endpoint theta/u/v
names retain their positions. Coverage cells are never added as independent
copies of the discrete HS residual.
"""
from flint import arb,fmpq
from bhsm.interface.shared_expression_graph import ExpressionDomain,Expression,restore
from bhsm.interface.sparse_affine_enclosure import SparseAffine
from bhsm.interface.shared_hs_physical_pullback import dense_incidence
from bhsm.interface.streamed_expression_artifact import read_graph
from array import array


def import_graph(domain,payload):
    names=tuple(payload['parameter_order'])
    if domain.names[:len(names)]!=names or list(domain.groups[:len(payload['groups'])])!=[tuple(g) for g in payload['groups']]:
        raise ValueError('shared endpoint parameter ordering and norms required')
    remap={}
    for old,n in enumerate(payload['nodes']):
        op=n[0]
        if op=='leaf':
            data=[op,len(domain.nodes),*n[2:]]
        elif op=='linear':data=[op,[[remap[i],c] for i,c in n[1]]]
        elif op=='product':data=[op,sorted(remap[i] for i in n[1])]
        elif op in ('exp','log','inverse','sqrt_positive'):data=[op,remap[n[1]],*n[2:]]
        elif op=='constant':data=n
        else:raise ValueError('unsupported imported expression')
        value=domain.node(data);remap[old]=value.index
        if op=='leaf':domain.leaf_provenance[str(value.index)]=payload['leaf_provenance'][str(old)]
    return {name:Expression(domain,remap[i]) for name,i in payload['roots'].items()},remap


def import_saved_graph(domain,path,metadata):
    if domain.names[:len(metadata['parameter_order'])]!=tuple(metadata['parameter_order']):
        raise ValueError('one shared physical parameter ordering required')
    if list(domain.groups[:len(metadata['groups'])])!=[tuple(g) for g in metadata['groups']]:
        raise ValueError('same physical parameter groups required')
    remap=array('Q')
    def visit(old,n):
        if old!=len(remap):raise ValueError('sequential source nodes required')
        op=n[0]
        if op=='leaf':data=[op,len(domain.nodes),*n[2:]]
        elif op=='linear':data=[op,[[remap[i],c] for i,c in n[1]]]
        elif op=='product':data=[op,sorted(remap[i] for i in n[1])]
        elif op in ('exp','log','inverse','sqrt_positive'):data=[op,remap[n[1]],*n[2:]]
        elif op=='constant':data=n
        else:raise ValueError('unsupported saved expression')
        value=domain.node(data);remap.append(value.index)
        if op=='leaf':domain.leaf_provenance[str(value.index)]=metadata['leaf_provenance'][str(old)]
    actual=read_graph(path,visit)
    if actual!=metadata:raise ValueError('saved graph changed between metadata and node import')
    # Reuse the already serialized outward root models. Their exact ancestor
    # graphs remain present; no new evaluation of an inherited parent model
    # is needed just to form the history incidence.
    for name,m in metadata.get('affine_enclosures',{}).items():
        domain.bounds[remap[metadata['roots'][name]]]=SparseAffine(domain.backend,
            restore(m['c']),{i:restore(v) for i,v in m['a']},arb(fmpq(m['r'])))
    if metadata.get('certified_enclosures'):
        from bhsm.interface.certified_expression_constraints import install
        install(domain,{str(remap[int(i)]):fact for i,fact in metadata['certified_enclosures'].items()})
    return {name:Expression(domain,remap[i]) for name,i in metadata['roots'].items()},remap


def point_history(domain,left_path,right_path,weights,step,tau,payloads=None):
    if payloads is None:payloads=[read_graph(p) for p in (left_path,right_path)]
    if payloads[0]['radius_exact']!=payloads[1]['radius_exact']:raise ValueError('same unchanged physical radii required')
    states=[];rates=[];endpoints=[]
    for path,payload in zip((left_path,right_path),payloads):
        roots,remap=import_saved_graph(domain,path,payload)
        endpoints.append(roots)
        states.append(endpoint_state_jet(domain,payload,roots,remap))
        rates.append({key:[roots[f'rate/{key}/{i}']/(weights[i] if i<98 else 1) for i in range(99)] for key in ('value','u','v','uv')})
    history=dense_incidence(domain.coerce(tau),step,*states,*rates)
    return history,endpoints,payloads


def endpoint_state_jet(domain,payload,roots,remap):
    descriptor=[int(i) for i,p in payload['leaf_provenance'].items() if p.get('role')=='descriptor_state']
    if len(descriptor)!=1:raise ValueError('one bound endpoint descriptor state required')
    values=[roots[f'endpoint/state/{i}'] for i in range(98)]+[Expression(domain,remap[descriptor[0]])]
    jet={'value':values,'u':[],'v':[],'uv':[domain.affine(0)]*99}
    for x in values:
        n=domain.nodes[x.index]
        if n[0]=='constant':
            jet['u'].append(domain.affine(0));jet['v'].append(domain.affine(0))
            continue
        if n[0]!='leaf' or n[4]!='0' or any(i>=150 for i,_ in n[3]):
            raise ValueError('frozen affine endpoint state map required')
        for key,offset in (('u',150),('v',300)):
            co=[arb(0)]*domain.dimension
            from bhsm.interface.shared_expression_graph import restore
            for i,value in n[3]:co[i+offset]=restore(value)
            jet[key].append(domain.affine(0,co,provenance={'role':'endpoint_state_direction','direction':key,'derived_from_node':x.index}))
    return jet


def cell_history(left,right,weights,step,cell):
    if not 0<=cell<8:raise ValueError('frozen interval-13 eight-cell partition required')
    if left['radius_exact']!=right['radius_exact']:raise ValueError('unchanged common radii required')
    names=list(left['parameter_order'])+[f'local_time/cell{cell}']
    groups=[tuple(g) for g in left['groups']]+[(450,451,'interval')]
    d=ExpressionDomain(groups,names)
    a,am=import_graph(d,left);b,bm=import_graph(d,right)
    x=endpoint_state_jet(d,left,a,am);y=endpoint_state_jet(d,right,b,bm)
    rates=[]
    for roots in (a,b):
        rates.append({key:[roots[f'rate/{key}/{i}']/(weights[i] if i<98 else 1) for i in range(99)] for key in ('value','u','v','uv')})
    tau=d.variable(450,arb(2*cell+1)/16,arb(1)/16,
        provenance={'role':'localized_time','global_tau_interval':[f'{cell}/8',f'{cell+1}/8'],'shared_endpoint_parameters':True})
    history=dense_incidence(tau,step,x,y,*rates)
    roots={f'history/{key}/{i}':v for key,vec in history.items() for i,v in enumerate(vec)}
    roots['time/global_tau']=tau
    return d,history,roots

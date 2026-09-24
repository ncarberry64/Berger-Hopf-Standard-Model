import gzip,json
from flint import arb,fmpq
from bhsm.interface.shared_expression_graph import ExpressionDomain,restore,pair
from bhsm.interface.streamed_expression_artifact import read_graph
from bhsm.interface.shared_history_expression import cell_history
from bhsm.interface.certified_expression_constraints import install


def test_streamed_nodes_and_metadata_reconstruct_exact_payload(tmp_path):
    d=ExpressionDomain([(0,1,'interval')],['theta'])
    x=d.variable(0);payload=d.export({'x':x*x+2*x})
    p=tmp_path/'graph.json.gz';p.write_bytes(gzip.compress(json.dumps(payload).encode(),mtime=0))
    nodes=[];metadata=read_graph(p,lambda i,n:nodes.append(n))
    assert metadata.pop('node_count')==len(nodes)
    metadata['nodes']=nodes
    assert json.dumps(metadata,sort_keys=True)==json.dumps(payload,sort_keys=True)


def test_frozen_value_fact_preserves_expression_and_signed_coefficients():
    d=ExpressionDomain([(0,1,'interval')],['theta'])
    f=d.affine(2,[arb(1)/100],100,provenance={'role':'test_physical_function'})
    before=d.digest.hexdigest();a=f.a[0,0]
    install(d,{str(f.index):{'ball':pair(arb(2,arb(1)/10)),'role':'test_same_family_value'}})
    assert pair(f.a[0,0])==pair(a)
    assert f.support()<3
    assert d.digest.hexdigest()==before
    assert (f-f).support().is_zero()
    assert d.export({'f':f})['auxiliary_leaves_constrained_to_actual_physical_family']


def endpoint(side):
    names=[f'{family}/{n}/{i}' for family in ('theta','u','v') for n in (13,14) for i in range(75)]
    groups=[g for k in range(0,450,75) for g in ((k,k+1,'interval'),(k+1,k+75,'euclidean'))]
    d=ExpressionDomain(groups,names);z=d.affine(0)
    x=d.variable(75*side,side+1);u=d.variable(150+75*side);v=d.variable(300+75*side)
    descriptor=d.variable(74+75*side,arb(1)/10,arb(1)/100,
        provenance={'role':'descriptor_state','site':('left','right')[side]})
    roots={f'endpoint/state/{i}':x if i==0 else z for i in range(98)}
    roots['descriptor/state']=descriptor
    for key,value in (('value',x*x),('u',2*x*u),('v',2*x*v),('uv',2*u*v)):
        for i in range(99):roots[f'rate/{key}/{i}']=value if i==0 else z
    payload=d.export(roots)
    payload.update(radius_exact=['1','1'],site=('left','right')[side],interval=13)
    return payload


def evaluate(domain,root,theta):
    values=[]
    for n in domain.nodes:
        if n[0]=='constant':v=arb(fmpq(n[1]))
        elif n[0]=='leaf':
            assert n[4]=='0'
            v=restore(n[2])+sum((restore(a)*theta[i] for i,a in n[3]),arb(0))
        elif n[0]=='linear':v=sum((values[i]*arb(fmpq(c)) for i,c in n[1]),arb(0))
        elif n[0]=='product':
            v=arb(1)
            for i in n[1]:v*=values[i]
        else:raise AssertionError(n[0])
        values.append(v)
    return values[root.index]


def test_adjacent_cells_have_same_global_endpoint_variables_and_handoff():
    left,right=endpoint(0),endpoint(1)
    d0,h0,_=cell_history(left,right,[arb(1)]*98,arb(1)/4,3)
    d1,h1,_=cell_history(left,right,[arb(1)]*98,arb(1)/4,4)
    assert d0.names[:450]==d1.names[:450]
    point=[arb(0)]*451
    point[0]=arb(1)/4;point[75]=-arb(1)/4
    point[150]=1;point[300]=1
    point[225]=arb(1)/2;point[375]=-arb(1)/2
    for key in ('value','u','v','uv'):
        point[450]=1;a=evaluate(d0,h0[key][0],point)
        point[450]=-1;b=evaluate(d1,h1[key][0],point)
        assert (a-b).contains(0)
    point[450]=1
    expected=(arb(1)/4)/8*(2*point[150]*point[300]-2*point[225]*point[375])
    assert (evaluate(d0,h0['uv'][0],point)-expected).contains(0)

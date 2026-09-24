import json
import pytest
from flint import arb,ctx
from bhsm.interface.shared_expression_graph import ExpressionDomain


def domain():
    return ExpressionDomain([(0,1,'interval'),(1,2,'interval')],['physical_u','physical_v'])


def test_bilinear_identity_survives_arithmetic_and_restart():
    d=domain();u=d.variable(0);v=d.variable(1)
    x=u*v
    p=d.export({'x':x,'same':v*u},include_bounds=True)
    assert p['roots']['x']==p['roots']['same']
    assert p['affine_enclosures']['x']['r']!='0'
    q,roots=ExpressionDomain.from_payload(json.loads(json.dumps(p)))
    assert (roots['x']-roots['same']).support().is_zero()
    assert (x-x).support().is_zero()


def test_equal_looking_independent_errors_do_not_cancel():
    d=domain()
    a=d.affine(0,remainder=1,provenance={'role':'first_error'})
    b=d.affine(0,remainder=1,provenance={'role':'second_error'})
    assert a.index!=b.index
    assert (a-b).support()>=2
    assert (a-a).support().is_zero()


def test_foreign_namespace_and_cycles_rejected():
    a,b=domain(),domain()
    with pytest.raises(ValueError): a.variable(0)+b.variable(0)
    p=a.export({'x':a.variable(1)},include_bounds=False)
    p['nodes'].append(['exp',len(p['nodes'])])
    with pytest.raises(ValueError): ExpressionDomain.from_payload(p)


def test_positive_normalization_uses_exact_expression():
    old=ctx.prec;ctx.prec=128
    try:
        d=domain();x=d.variable(0,center=2,scale=arb(1)/100)
        y=x.sqrt_positive(1)
        assert (y-y).support().is_zero()
        assert y.enclosure().contains(arb(2).sqrt())
        assert (1/x).enclosure().contains(arb(1)/2)
    finally: ctx.prec=old


def test_disk_storage_has_identical_expression_and_enclosure_bytes():
    from bhsm.interface.disk_expression_graph import DiskExpressionDomain
    payloads=[]
    for cls in (ExpressionDomain,DiskExpressionDomain):
        d=cls([(0,1,'interval'),(1,2,'interval')],['u','v'])
        u,v=d.variable(0),d.variable(1)
        x=u*v+2*u-3*v
        payloads.append(json.dumps(d.export({'x':x,'cancel':x-x}),sort_keys=True))
    assert payloads[0]==payloads[1]


def test_common_border_cancellation_precedes_enclosure():
    from bhsm.interface.shared_mixed_rate_graph import normalized_graph
    d=domain();z=d.affine(0)
    scalar=lambda value,u=0,uv=0:{'value':d.affine(value),'u':d.affine(u),'v':d.affine(u),'uv':d.affine(uv)}
    psi={'value':[d.affine(1)]+[z]*60,'u':[z]*61,'v':[z]*61,'uv':[z]*61}
    h={k:[z]*61 for k in psi};c={k:[z]*37 for k in psi};roots={}
    rate=normalized_graph(psi,h,scalar(2,10**8,10**12),scalar(0),c,[arb(1)]*61,scalar(3),scalar(4),arb(1),roots)
    assert len(rate['uv'])==99
    assert all(x.support().is_zero() for x in rate['uv'])
    assert rate['value'][-1].enclosure().contains(3)
    assert roots['normalization/Q/value'].enclosure().contains(1)


def test_sparse_arithmetic_encloses_same_physical_samples_as_dense():
    import itertools
    from bhsm.interface.shared_action_taylor import TaylorDomain
    from bhsm.interface.sparse_affine_enclosure import SparseDomain
    old=ctx.prec;ctx.prec=128
    try:
        groups=[(0,1,'interval'),(1,4,'euclidean')]
        coefficients=list(map(arb,('0.01','0.02','-0.01','0.03')))
        outputs=[]
        for cls in (TaylorDomain,SparseDomain):
            d=cls(groups,4);x=d.affine(2,coefficients,arb('0.00001'))
            outputs.append((x*x+x).exp().enclosure())
        for theta in itertools.product((-arb('0.5'),arb('0.5')),repeat=4):
            value=2+sum((a*t for a,t in zip(coefficients,theta)),arb(0))
            exact=(value*value+value).exp()
            assert all(bound.contains(exact) for bound in outputs)
    finally:ctx.prec=old

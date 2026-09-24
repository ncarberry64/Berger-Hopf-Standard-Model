from flint import arb
from bhsm.interface.shared_expression_graph import ExpressionDomain
from bhsm.interface.shared_projected_rate import LinkedModels,projected_mixed,booked_mixed


def test_projection_cancels_same_numerator_before_normalization():
    d=ExpressionDomain([(0,1,'interval'),(1,2,'interval')],['u','v'])
    u,v=d.variable(0),d.variable(1);z=d.affine(0);one=d.affine(1)
    roots={}
    for key,x in (('value',one),('u',u),('v',v),('uv',u*v)):
        for i in range(2):roots[f'factored_numerator/{key}/{i}']=x
    roots.update({'normalization/norm':one,'normalization/norm_u':u,
        'normalization/norm_v':v,'normalization/norm_uv':u*v})
    payload=d.export(roots)
    q=ExpressionDomain(d.groups,d.names)
    models=LinkedModels(q,payload,'test-parent')
    result=projected_mixed(models,[arb(1),arb(-1)])
    assert result.support().is_zero()


def test_signed_cross_endpoint_booking_cancels_before_support():
    names=[str(i) for i in range(450)]
    d=ExpressionDomain([(i,i+1,'interval') for i in range(450)],names)
    terms={'LL':{'01':[arb(2)],'10':[arb(-2)]},'LT':{}}
    assert booked_mixed(d,terms,arb(1),arb(1),{}).support().is_zero()

"""All moving-leg terms and exact common-border cancellation of the rate."""
from flint import arb
from bhsm.interface.shared_implicit_response_jet import dot
from bhsm.interface.shared_positive_norm_jet import reciprocal_positive


def trilinear_jet(evaluate,legs,u,v,value,second_action_leaf=None):
    """Jet of S3[l0,l1,l2]: 4 first and all 16 mixed assignments.

    Each leg is a dictionary with value/u/v/uv Taylor vectors. `value` is an
    inherited certified value enclosure. Only new derivative terms are run.
    The optional fifth-action leaf must be certified for these SAME legs.
    """
    primal=[p['value'] for p in legs]
    def selected(changes):return [p[changes.get(i,'value')] for i,p in enumerate(legs)]
    first=[]
    for name,direction in (('u',u),('v',v)):
        first.append(evaluate(primal+[direction])+sum((evaluate(selected({i:name})) for i in range(3)),0))
    mixed=evaluate(primal+[u,v]) if second_action_leaf is None else second_action_leaf
    for i in range(3):
        mixed+=evaluate(selected({i:'u'})+[v])+evaluate(selected({i:'v'})+[u])
        mixed+=evaluate(selected({i:'uv'}))
        for j in range(3):
            if i!=j:mixed+=evaluate(selected({i:'u',j:'v'}))
    return dict(value=value,u=first[0],v=first[1],uv=mixed)


def coupled_rate(psi,h,b,s,c,weights,C,J,b_lower):
    """Cancel the positive common b using certified psi.psi=1, psi.h=0.

    Inputs are value/u/v/uv jets, all on the same physical domain. The caller
    binds the eigenline/response normalization equations and w_i>=1. Those
    equations imply the factored squared norm Q>=1 throughout that domain.
    """
    w=list(weights)
    if any(not wi>=1 for wi in w) or not arb(b_lower)>0:
        raise ArithmeticError('certified positive border and retained metric weights required')
    ib=reciprocal_positive(b['value'],b_lower)
    t=s['value']*ib
    tu=(s['u']-t*b['u'])*ib;tv=(s['v']-t*b['v'])*ib
    tuv=(s['uv']-tu*b['v']-tv*b['u']-t*b['uv'])*ib
    k=[p+t*hi for p,hi in zip(psi['value'],h['value'])]
    ku=[p+tu*hi+t*hui for p,hi,hui in zip(psi['u'],h['value'],h['u'])]
    kv=[p+tv*hi+t*hvi for p,hi,hvi in zip(psi['v'],h['value'],h['v'])]
    kuv=[p+tuv*hi+tu*hvi+tv*hui+t*huvi for p,hi,hui,hvi,huvi in
          zip(psi['uv'],h['value'],h['u'],h['v'],h['uv'])]
    M=dot(h['value'],h['value'])+dot(c['value'],c['value'])
    Mu=2*(dot(h['value'],h['u'])+dot(c['value'],c['u']))
    Mv=2*(dot(h['value'],h['v'])+dot(c['value'],c['v']))
    Muv=2*(dot(h['u'],h['v'])+dot(h['value'],h['uv'])+dot(c['u'],c['v'])+dot(c['value'],c['uv']))
    weighted=lambda a,z:sum(((wi*wi-1)*ai*zi for wi,ai,zi in zip(w,a,z)),0)
    Q=1+weighted(k,k)+t*t*M
    Qu=2*weighted(k,ku)+2*t*tu*M+t*t*Mu
    Qv=2*weighted(k,kv)+2*t*tv*M+t*t*Mv
    Quv=2*(weighted(ku,kv)+weighted(k,kuv))+2*(tu*tv+t*tuv)*M+2*t*tu*Mv+2*t*tv*Mu+t*t*Muv
    center=Q.c.sqrt()
    if not center>0:raise ArithmeticError('positive factored normalization center required')
    safe=min(arb(1),center.lower())
    nu=Q._unary(center,1/(2*center),(1/(4*safe**3)).upper())
    inv=reciprocal_positive(nu,arb(1))
    nuu=Qu*inv/2;nuv=Qv*inv/2;nuuv=Quv*inv/2-Qu*Qv*inv**3/4
    numerator=[t*ci for ci in c['value']]+[wi*ki for wi,ki in zip(w,k)]+[C['value']+t*J['value']]
    du=[tu*ci+t*cui for ci,cui in zip(c['value'],c['u'])]+[wi*ki for wi,ki in zip(w,ku)]+[C['u']+tu*J['value']+t*J['u']]
    dv=[tv*ci+t*cvi for ci,cvi in zip(c['value'],c['v'])]+[wi*ki for wi,ki in zip(w,kv)]+[C['v']+tv*J['value']+t*J['v']]
    duv=[tuv*ci+tu*cvi+tv*cui+t*cuvi for ci,cui,cvi,cuvi in zip(c['value'],c['u'],c['v'],c['uv'])]
    duv += [wi*ki for wi,ki in zip(w,kuv)]+[C['uv']+tuv*J['value']+tu*J['v']+tv*J['u']+t*J['uv']]
    mixed=[uv*inv-(u*nuv+v*nuu+n*nuuv)*inv**2+2*n*nuu*nuv*inv**3
           for n,u,v,uv in zip(numerator,du,dv,duv)]
    return dict(mixed=mixed,norm=nu,norm_u=nuu,norm_v=nuv,norm_uv=nuuv,
                factored_norm_squared=Q,factored_norm_lower=arb(1),common_border_canceled=True,
                descriptor_numerator_uv=duv[-1])

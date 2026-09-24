"""Missing mixed-rate expressions with inherited primal/first authorities.

Every named expression remains in one DAG. The caller supplies the frozen
inverse authority; this module neither certifies a branch nor computes an
inverse. Descriptor assignments are individually retained in the DAG.
"""
from bhsm.interface.shared_implicit_response_jet import dot


def descriptor_jet(evaluate,legs,u,v,label,roots):
    p=[x['value'] for x in legs]
    result={'value':evaluate(p)}
    selected=lambda changes:[x[changes.get(i,'value')] for i,x in enumerate(legs)]
    for name,direction in (('u',u),('v',v)):
        terms=[evaluate(p+[direction])]+[evaluate(selected({i:name})) for i in range(3)]
        for j,x in enumerate(terms): roots[f'{label}/{name}/term{j}']=x
        result[name]=sum(terms,0)
    terms=[evaluate(p+[u,v])]
    for i in range(3):
        terms.extend((evaluate(selected({i:'u'})+[v]),evaluate(selected({i:'v'})+[u]),evaluate(selected({i:'uv'}))))
        terms.extend(evaluate(selected({i:'u',j:'v'})) for j in range(3) if j!=i)
    if len(terms)!=16: raise ValueError('all mixed moving-leg assignments required')
    for j,x in enumerate(terms): roots[f'{label}/uv/term{j}']=x
    result['uv']=sum(terms,0)
    for k,x in result.items(): roots[f'{label}/{k}']=x
    return result


def normalized_graph(psi,h,b,s,c,rw,C,J,b_lower,roots):
    """Use b>0, psi.psi=1 and psi.h=0 before taking any norm support."""
    inv=b['value'].reciprocal_positive(b_lower)
    t={'value':s['value']*inv}
    for k in ('u','v'): t[k]=(s[k]-t['value']*b[k])*inv
    t['uv']=(s['uv']-t['u']*b['v']-t['v']*b['u']-t['value']*b['uv'])*inv
    def prod(a,z):
        return dict(value=a['value']*z['value'],u=a['u']*z['value']+a['value']*z['u'],
            v=a['v']*z['value']+a['value']*z['v'],
            uv=a['uv']*z['value']+a['u']*z['v']+a['v']*z['u']+a['value']*z['uv'])
    def scalar(v,i):return {k:v[k][i] for k in ('value','u','v','uv')}
    k=[]
    for i in range(61):
        th=prod(t,scalar(h,i));k.append({a:psi[a][i]+th[a] for a in th})
    squared={'value':1,'u':0,'v':0,'uv':0}
    for i,ki in enumerate(k):
        kk=prod(ki,ki)
        for key in squared:squared[key]+=(rw[i]**2-1)*kk[key]
    for vec in (h,c):
        for i in range(len(vec['value'])):
            x=prod(t,scalar(vec,i));xx=prod(x,x)
            for key in squared:squared[key]+=xx[key]
    nu=squared['value'].sqrt_positive(1);iv=nu.reciprocal_positive(1)
    nuu=squared['u']*iv/2;nuv=squared['v']*iv/2
    nuuv=(squared['uv']/2-nuu*nuv)*iv
    numerators=[prod(t,scalar(c,i)) for i in range(37)]
    numerators += [{a:rw[i]*ki[a] for a in ki} for i,ki in enumerate(k)]
    tj=prod(t,J);numerators.append({a:C[a]+tj[a] for a in C})
    rate={a:[] for a in ('value','u','v','uv')}
    for i,N in enumerate(numerators):
        value=N['value']*iv
        du=(N['u']-nuu*value)*iv;dv=(N['v']-nuv*value)*iv
        mixed=(N['uv']-nuuv*value-nuu*dv-nuv*du)*iv
        for key,x in zip(rate,(value,du,dv,mixed)):
            rate[key].append(x);roots[f'rate/{key}/{i}']=x
        for key,x in N.items():roots[f'factored_numerator/{key}/{i}']=x
    for key,x in dict(norm=nu,norm_u=nuu,norm_v=nuv,norm_uv=nuuv,**{'Q/'+k:v for k,v in squared.items()}).items():
        roots['normalization/'+key]=x
    return rate


def mixed_graph(evaluate,solve,inputs):
    state,psi,response=inputs['state'],inputs['psi'],inputs['response']
    u,v=inputs['u'],inputs['v'];qw,rw,w=inputs['qw'],inputs['rw'],inputs['weights']
    zero=state[0].domain.affine(0);pad=lambda x:[zero]*37+list(x)
    roots={};p=pad(psi['value'])
    lu=evaluate([p,p,u]);lv=evaluate([p,p,v])
    huv=evaluate.gradient([p,u,v])[37:]
    hupv=evaluate.gradient([pad(psi['v']),u])[37:]
    hvpu=evaluate.gradient([pad(psi['u']),v])[37:]
    rhs=[-huv[i]-hupv[i]-hvpu[i]+lu*psi['v'][i]+lv*psi['u'][i] for i in range(61)]
    psimixed=solve(rhs+[-dot(psi['u'],psi['v'])],'eigenline/uv',roots)
    psi['uv']=psimixed[:61];luv=-psimixed[-1]
    c={key:[qw[i]*x[37+i] for i in range(37)] for key,x in (('value',state),('u',u),('v',v))};c['uv']=[zero]*37
    craw={key:[x/w[i] for i,x in enumerate(vec)]+[zero]*61 for key,vec in c.items()}
    guv=evaluate.gradient([u,v]);gcuv=evaluate.gradient([craw['value'],u,v])
    gcu=evaluate.gradient([craw['u'],v]);gcv=evaluate.gradient([craw['v'],u])
    h={key:vec[:61] for key,vec in response.items()};b={key:vec[-1] for key,vec in response.items()}
    gh=evaluate.gradient([pad(h['value']),u,v])
    ghu=evaluate.gradient([pad(h['u']),v]);ghv=evaluate.gradient([pad(h['v']),u])
    force=[(rw[i]*qw[i]*guv[i]/w[i] if i<37 else zero)-rw[i]*(gcuv[37+i]+gcu[37+i]+gcv[37+i])/w[37+i] for i in range(61)]
    rhs=[force[i]-gh[37+i]-ghu[37+i]-ghv[37+i]+luv*h['value'][i]+lu*h['v'][i]+lv*h['u'][i]
        -psi['uv'][i]*b['value']-psi['u'][i]*b['v']-psi['v'][i]*b['u'] for i in range(61)]
    border=-dot(psi['uv'],h['value'])-dot(psi['u'],h['v'])-dot(psi['v'],h['u'])
    response['uv']=solve(rhs+[border],'response/uv',roots)
    h['uv']=response['uv'][:61];b['uv']=response['uv'][-1]
    pj={key:pad(vec) for key,vec in psi.items()}
    aj={key:pad([rw[i]*vec[i]/w[37+i] for i in range(61)]) for key,vec in psi.items()}
    dj={key:craw[key][:37]+[rw[i]*h[key][i]/w[37+i] for i in range(61)] for key in h}
    C=descriptor_jet(evaluate,[pj,pj,aj],u,v,'descriptor/C',roots)
    J=descriptor_jet(evaluate,[pj,pj,dj],u,v,'descriptor/J',roots)
    rate=normalized_graph(psi,h,b,inputs['descriptor'],c,rw,C,J,inputs['b_lower'],roots)
    for label,jet in (('eigenline',psi),('response',response)):
        for key,vec in jet.items():
            for i,x in enumerate(vec):roots[f'{label}/{key}/{i}']=x
    roots.update({'eigenvalue/u':lu,'eigenvalue/v':lv,'eigenvalue/uv':luv})
    return rate,roots

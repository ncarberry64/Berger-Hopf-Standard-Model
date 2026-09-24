"""Complete interval extension of the frozen physical mixed-rate equations.

This deliberately exposes coordinate boxing as an enclosure limitation.
It computes every signed term before returning a bound; it supplies no
branch authority, inverse certificate, or positive norm on its own.
"""
from flint import arb
from bhsm.interface.shared_complete_rate_jet import trilinear_jet


KEYS=('value','u','v','uv')
def dot(a,b):return sum((x*y for x,y in zip(a,b,strict=True)),arb(0))
def product(a,b):
    return dict(value=a['value']*b['value'],
                u=a['u']*b['value']+a['value']*b['u'],
                v=a['v']*b['value']+a['value']*b['v'],
                uv=a['uv']*b['value']+a['u']*b['v']+a['v']*b['u']+a['value']*b['uv'])


def normalize_augmented(U,lower):
    """Normalize all 99 outputs by the norm of precisely the first 98."""
    if any(len(U[k])!=99 for k in KEYS) or not lower>0:
        raise ValueError('complete 99-component jets and same-domain positive norm required')
    N,Nu,Nv,Nuv=[U[k][:98] for k in KEYS]
    upper=sum((abs(x).upper()**2 for x in N),arb(0)).sqrt().upper()
    if not upper>=lower:raise ArithmeticError('normalization bounds contradict')
    nu=arb(lower).union(upper)
    # A very wide Arb midpoint/radius may round its lower endpoint below
    # zero. Invert the proven endpoints, never that enlarged display ball.
    inv=(1/upper).union((1/lower).upper())
    nuu=dot(N,Nu)*inv;nuv=dot(N,Nv)*inv
    nuuv=(dot(Nu,Nv)+dot(N,Nuv)-nuu*nuv)*inv
    return dict(value=[x*inv for x in U['value']],
        u=[a*inv-x*nuu*inv**2 for x,a in zip(U['value'],U['u'])],
        v=[a*inv-x*nuv*inv**2 for x,a in zip(U['value'],U['v'])],
        uv=[ab*inv-(a*nuv+b*nuu+x*nuuv)*inv**2+2*x*nuu*nuv*inv**3
            for x,a,b,ab in zip(U['value'],U['u'],U['v'],U['uv'])],norm=nu)


def complete_rate(evaluate,solve,state,psi_value,u,v,descriptor,qw,rw,weights,norm_lower):
    """Enclose D2 f[u,v] for affine augmented directions on this exact tube.

    evaluate.gradient(legs) returns the 98 raw rows of the complete action.
    solve uses the separately certified pointwise bordered K inverse. All
    eigenline norm and response orthogonality border terms are retained.
    Non-affine history incidence is composed by the caller, after this graph.
    """
    zero=arb(0);pad=lambda x:[zero]*37+list(x)
    psi={'value':list(psi_value)};lam={}
    for name,direction in (('u',u),('v',v)):
        h=evaluate.gradient([pad(psi_value),direction])[37:]
        z=solve([-x for x in h]+[zero]);psi[name]=z[:61];lam[name]=-z[-1]
    huv=evaluate.gradient([pad(psi_value),u,v])[37:]
    hupv=evaluate.gradient([pad(psi['v']),u])[37:]
    hvpu=evaluate.gradient([pad(psi['u']),v])[37:]
    rhs=[-huv[i]-hupv[i]-hvpu[i]+lam['u']*psi['v'][i]+lam['v']*psi['u'][i] for i in range(61)]
    z=solve(rhs+[-dot(psi['u'],psi['v'])]);psi['uv']=z[:61];lam['uv']=-z[-1]
    c={k:[qw[i]*x[37+i] for i in range(37)] for k,x in (('value',state),('u',u),('v',v))}
    c['uv']=[zero]*37
    craw={k:[x/weights[i] for i,x in enumerate(c[k])]+[zero]*61 for k in KEYS}
    def forcing(name,legs):
        g=evaluate.gradient(legs)
        hc=evaluate.gradient([craw['value']]+legs)
        if name in ('u','v'):
            extra=evaluate.gradient([craw[name]])
            hc=[x+y for x,y in zip(hc,extra)]
        elif name=='uv':
            a=evaluate.gradient([craw['u'],v]);b=evaluate.gradient([craw['v'],u])
            hc=[x+y+z for x,y,z in zip(hc,a,b)]
        return [(rw[i]*qw[i]*g[i]/weights[i] if i<37 else zero)-rw[i]*hc[37+i]/weights[37+i] for i in range(61)]
    response={'value':solve(forcing('value',[])+[zero])}
    h=response['value'][:61];b=response['value'][-1]
    for name,direction in (('u',u),('v',v)):
        force=forcing(name,[direction]);gh=evaluate.gradient([pad(h),direction])[37:]
        rhs=[force[i]-gh[i]+lam[name]*h[i]-psi[name][i]*b for i in range(61)]
        response[name]=solve(rhs+[-dot(psi[name],h)])
    hu,hv=response['u'][:61],response['v'][:61];bu,bv=response['u'][-1],response['v'][-1]
    force=forcing('uv',[u,v]);gh=evaluate.gradient([pad(h),u,v])[37:]
    ghu=evaluate.gradient([pad(hu),v])[37:];ghv=evaluate.gradient([pad(hv),u])[37:]
    rhs=[force[i]-gh[i]-ghu[i]-ghv[i]+lam['uv']*h[i]+lam['u']*hv[i]+lam['v']*hu[i]
         -psi['uv'][i]*b-psi['u'][i]*bv-psi['v'][i]*bu for i in range(61)]
    response['uv']=solve(rhs+[-dot(psi['uv'],h)-dot(psi['u'],hv)-dot(psi['v'],hu)])
    h={k:response[k][:61] for k in KEYS};b={k:response[k][-1] for k in KEYS}
    p={k:pad(psi[k]) for k in KEYS}
    a={k:pad([rw[i]*psi[k][i]/weights[37+i] for i in range(61)]) for k in KEYS}
    rawd={k:craw[k][:37]+[rw[i]*h[k][i]/weights[37+i] for i in range(61)] for k in KEYS}
    C=trilinear_jet(evaluate,[p,p,a],u,v,evaluate([p['value'],p['value'],a['value']]))
    J=trilinear_jet(evaluate,[p,p,rawd],u,v,evaluate([p['value'],p['value'],rawd['value']]))
    output=[]
    for i in range(37):output.append(product(descriptor,{k:c[k][i] for k in KEYS}))
    for i in range(61):
        bp=product(b,{k:psi[k][i] for k in KEYS});sh=product(descriptor,{k:h[k][i] for k in KEYS})
        output.append({k:rw[i]*(bp[k]+sh[k]) for k in KEYS})
    bc=product(b,C);sj=product(descriptor,J);output.append({k:bc[k]+sj[k] for k in KEYS})
    U={k:[o[k] for o in output] for k in KEYS}
    return dict(rate=normalize_augmented(U,norm_lower),psi=psi,response=response,C=C,J=J,
                all_16_mixed_trilinear_assignments=True,normalization_uses_98_state_components=True,
                affine_field_directions=True,nonaffine_incidence_composed=False)

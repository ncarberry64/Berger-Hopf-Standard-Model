"""Shared normalization jets with an inherited positive-domain certificate."""
from flint import arb
from bhsm.interface.shared_implicit_response_jet import dot,_domain


def reciprocal_positive(value,lower):
    lower=arb(lower)
    if not lower>0 or not value.c>0:raise ArithmeticError('certified positive value and expansion center required')
    safe=min(lower,value.c.lower())
    return value._unary(1/value.c,-1/value.c**2,(2/safe**3).upper())


def normalize(N,Nu,Nv,Nuv,certified_norm_lower):
    """Caller binds lower>0 to this exact physical family, not an unrelated box.

    nu derives from N.N. The inherited lower controls the unary remainder on
    the actual family even when an enlarged auxiliary error box crosses zero.
    No independent normalization-error budget is introduced.
    """
    if not N or any(len(v)!=len(N) for v in (Nu,Nv,Nuv)):raise ValueError('complete physical numerator jets required')
    _domain(list(N)+list(Nu)+list(Nv)+list(Nuv))
    lower=arb(certified_norm_lower);squared=dot(N,N)
    if not lower>0 or not squared.c>0:raise ArithmeticError('positive inherited norm and center required')
    center=squared.c.sqrt();safe=min(lower,center.lower())
    nu=squared._unary(center,1/(2*center),(1/(4*safe**3)).upper())
    inv=reciprocal_positive(nu,lower)
    nuu=dot(N,Nu)*inv;nuv=dot(N,Nv)*inv
    nuuv=(dot(Nu,Nv)+dot(N,Nuv)-nuu*nuv)*inv
    result=[uv*inv-(u*nuv+v*nuu+n*nuuv)*inv**2+2*n*nuu*nuv*inv**3
            for n,u,v,uv in zip(N,Nu,Nv,Nuv,strict=True)]
    return dict(norm=nu,norm_u=nuu,norm_v=nuv,norm_uv=nuuv,physical_mixed=result,
                norm_inverse=inv,positive_lower_reused=lower)

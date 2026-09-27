"""Outward first jets of the existing C2 Riccati/Mobius recurrence.

Formula owner: aether_forward_c2_weyl_riccati._map. Three local derivatives
(terminal load, midpoint log radius, proper duration) precede contraction.
"""
from flint import arb, arb_mat


class Jet:
    def __init__(self, value, derivative=None):
        self.v=arb(value)
        self.d=list(derivative) if derivative is not None else [arb(0)]*3

    def __add__(self, other):
        b=other if isinstance(other,Jet) else Jet(other)
        return Jet(self.v+b.v,[a+c for a,c in zip(self.d,b.d)])
    __radd__=__add__

    def __neg__(self):return Jet(-self.v,[-a for a in self.d])
    def __sub__(self, other):return self+-asjet(other)
    def __rsub__(self, other):return asjet(other)+-self

    def __mul__(self, other):
        b=asjet(other)
        return Jet(self.v*b.v,[a*b.v+self.v*c for a,c in zip(self.d,b.d)])
    __rmul__=__mul__

    def __truediv__(self, other):
        b=asjet(other)
        return Jet(self.v/b.v,[(a*b.v-self.v*c)/(b.v*b.v) for a,c in zip(self.d,b.d)])
    def __rtruediv__(self, other):return asjet(other)/self
    def exp(self):
        v=self.v.exp();return Jet(v,[v*a for a in self.d])
    def sqrt(self):
        v=self.v.sqrt();return Jet(v,[a/(2*v) for a in self.d])
    def tanh(self):
        v=self.v.tanh();return Jet(v,[(1-v*v)*a for a in self.d])


def asjet(v):return v if isinstance(v,Jet) else Jet(v)


def local_map(load, xmid, duration, *, channel, value, z, chirality=1):
    if not arb(duration)>0 or not arb(z)<0 or not arb(value)>=0:
        raise ValueError('positive duration, nonnegative channel value and z<0 required')
    x=Jet(xmid,[arb(0),arb(1),arb(0)])
    h=Jet(duration,[arb(0),arb(0),arb(1)])
    L=None if load is None else Jet(load,[arb(1),arb(0),arb(0)])
    if L is not None and not L.v>=0:raise ValueError('nonnegative terminal load required')
    if channel=='scalar':
        k=(value*(-2*x).exp()-z).sqrt();t=(k*h).tanh()
        result=k/t if L is None else (k*t+L)/(1+L*t/k)
    elif channel=='product_Dirac' and chirality in (-1,1):
        W=chirality*value*(-x).exp();k=(W*W-z).sqrt();t=(k*h).tanh()
        a=1-W*t/k;b=t/k;c=-z*t/k;d=1+W*t/k
        result=a/b if L is None else (c+L*a)/(d+L*b)
    else:raise ValueError('owned scalar or signed product_Dirac channel required')
    return result.v,result.d


def first_pullback(x, h, dx, dh, **channel):
    """One coefficient history, one reverse cotangent, all launch directions."""
    count=len(h);m=dx.ncols()
    if len(x)!=count+1 or dx.nrows()!=count+1 or dh.nrows()!=count or dh.ncols()!=m:
        raise ValueError('aligned coefficient history and first jets required')
    local=[None]*count;load=None;forward=arb_mat(1,m)
    for i in reversed(range(count)):
        load,partials=local_map(load,(x[i]+x[i+1])/2,h[i],**channel)
        a,b,c=partials;local[i]=partials
        for j in range(m):forward[0,j]=a*forward[0,j]+b*(dx[i,j]+dx[i+1,j])/2+c*dh[i,j]
    gx=[arb(0)]*(count+1);gh=[arb(0)]*count;adjoint=arb(1)
    for i,(a,b,c) in enumerate(local):
        gx[i]+=adjoint*b/2;gx[i+1]+=adjoint*b/2;gh[i]=adjoint*c
        adjoint*=a
    backward=arb_mat(1,count+1,gx)*dx+arb_mat(1,count,gh)*dh
    replay=forward-backward
    if not all(v.contains(0) for v in replay.entries()):
        raise ArithmeticError('forward/reverse first pullback do not overlap')
    return dict(value=load,first=backward,forward=forward,replay=replay,
                coefficient_cotangent=arb_mat(1,count+1,gx),duration_cotangent=arb_mat(1,count,gh))

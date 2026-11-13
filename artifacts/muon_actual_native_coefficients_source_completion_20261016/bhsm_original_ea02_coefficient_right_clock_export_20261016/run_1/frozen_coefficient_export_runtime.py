"""Original scalar action J*h*R jets on the complete phase row set.

J consists of literal velocity/Gauss tests, h is one actual source or clock
direction, and R is the supplied collection of fixed right columns.  No
J*J block or unused third tensor is formed.  Geometry positions are held by
every J test, so the fourth implicit-response derivative is not required.
"""
from pathlib import Path
from hashlib import sha256
import json
import os
import sys
import time
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'


class PhaseJet:
    nj=0
    nr=0
    include_first=True
    _zero_shape=None

    def __init__(self,v,g=None,h=None,r=None,gh=None,gR=None,hR=None,ghR=None):
        from flint import acb,acb_mat
        if self._zero_shape!=(self.nj,self.nr):
            type(self)._zero_shape=(self.nj,self.nr)
            type(self)._zg=acb_mat(self.nj,1);type(self)._zr=acb_mat(1,self.nr)
            type(self)._zgr=acb_mat(self.nj,self.nr)
        self.value=v if isinstance(v,acb)else acb(complex(v))
        self.g=self._zg if g is None else g
        self.h=acb(0)if h is None else h
        self.r=self._zr if r is None else r
        self.gh=self._zg if gh is None else gh
        self.gR=self._zgr if gR is None else gR
        self.hR=self._zr if hR is None else hR
        self.ghR=self._zgr if ghR is None else ghR
        self.is_constant=(g is None and h is None and r is None and gh is None
            and gR is None and hR is None and ghR is None)

    @property
    def gradient(self):
        # The original geometry's _fields uses this only for its dimension.
        return range(self.nj)

    @classmethod
    def constant(cls,v,n=None):return cls(v)

    def __add__(self,o):
        if not isinstance(o,PhaseJet):
            if self.is_constant:return PhaseJet(self.value+complex(o))
            z=PhaseJet(self.value+complex(o),self.g,self.h,self.r,self.gh,self.gR,self.hR,self.ghR)
            z.is_constant=self.is_constant
            return z
        if self.is_constant and o.is_constant:return PhaseJet(self.value+o.value)
        if not self.include_first:
            gr=None if self.gR is self._zgr and o.gR is self._zgr else self.gR+o.gR
            return PhaseJet(self.value+o.value,self.g+o.g,r=self.r+o.r,gR=gr)
        z=PhaseJet(self.value+o.value,self.g+o.g,self.h+o.h,self.r+o.r,
            self.gh+o.gh,self.gR+o.gR,self.hR+o.hR,self.ghR+o.ghR)
        z.is_constant=self.is_constant and o.is_constant
        return z
    __radd__=__add__

    def __neg__(self):return self*-1
    def __sub__(self,o):return self+(-o)
    def __rsub__(self,o):return -self+o

    def __mul__(self,o):
        from flint import acb
        if not isinstance(o,PhaseJet):
            a=o if isinstance(o,acb)else acb(complex(o))
            if self.is_constant:return PhaseJet(a*self.value)
            if not self.include_first:return PhaseJet(a*self.value,a*self.g,r=a*self.r,
                gR=None if self.gR is self._zgr else a*self.gR)
            z=PhaseJet(a*self.value,a*self.g,a*self.h,a*self.r,a*self.gh,a*self.gR,a*self.hR,a*self.ghR)
            z.is_constant=self.is_constant
            return z
        if self.is_constant:return o*self.value
        if o.is_constant:return self*o.value
        v,w=self.value,o.value
        if not self.include_first:
            return PhaseJet(v*w,self.g*w+v*o.g,r=self.r*w+v*o.r,
                gR=self.gR*w+self.g*o.r+o.g*self.r+v*o.gR)
        return PhaseJet(v*w,self.g*w+v*o.g,self.h*w+v*o.h,self.r*w+v*o.r,
            self.gh*w+self.g*o.h+self.h*o.g+v*o.gh,
            self.gR*w+self.g*o.r+o.g*self.r+v*o.gR,
            self.hR*w+self.h*o.r+self.r*o.h+v*o.hR,
            self.ghR*w+v*o.ghR+self.gh*o.r+o.gh*self.r+
            self.gR*o.h+o.gR*self.h+self.g*o.hR+o.g*self.hR)
    __rmul__=__mul__

    def unary(self,v,f1,f2,f3):
        if self.is_constant:return PhaseJet(v)
        if not self.include_first:return PhaseJet(v,f1*self.g,r=f1*self.r,gR=f1*self.gR+f2*self.g*self.r)
        return PhaseJet(v,f1*self.g,f1*self.h,f1*self.r,
            f1*self.gh+f2*self.g*self.h,
            f1*self.gR+f2*self.g*self.r,
            f1*self.hR+f2*self.h*self.r,
            f1*self.ghR+f2*(self.gh*self.r+self.gR*self.h+self.g*self.hR)+
            f3*self.g*self.r*self.h)

    def reciprocal(self):
        v=self.value
        return self.unary(1/v,-1/v**2,2/v**3,-6/v**4)
    def __truediv__(self,o):return self*(o.reciprocal()if isinstance(o,PhaseJet)else 1/o)
    def __rtruediv__(self,o):return self.reciprocal()*o
    def __pow__(self,p):
        v=self.value
        return self.unary(v**p,p*v**(p-1),p*(p-1)*v**(p-2),p*(p-1)*(p-2)*v**(p-3))
    def exp(self):
        a=self.value.exp();return self.unary(a,a,a,a)


def _sin(x):
    s,c=x.value.sin(),x.value.cos();return x.unary(s,c,-s,-c)


def _cos(x):
    s,c=x.value.sin(),x.value.cos();return x.unary(c,-s,-c,s)


def _sqrt(x):
    r=x.value.sqrt()
    if float(r.real.mid())<=0:raise ValueError('same original principal metric square-root branch required')
    return x.unary(r,1/(2*r),-1/(4*r**3),3/(8*r**5))


def _atanh(x):
    v=x.value
    if float(abs(v).upper())>=1:raise ValueError('same retained timelike chart required')
    d=1-v*v
    return x.unary(v.atanh(),1/d,2*v/d**2,2*(1+3*v*v)/d**3)


def _compose_phase_position(x,value,first,second):
    from flint import acb
    if not x.include_first:return x.unary(_C(value),_C(first),_C(second),acb(0))
    if any(x.g[i,0]!=0 for i in range(x.nj)):
        raise ValueError('implicit chart phase tests must hold delta and chi positions exactly')
    # F''' has no placement: g=gh=gR=ghR=0 for the position-only delta.
    if any(x.gh[i,0]!=0 for i in range(x.nj))or any(x.gR[i,j]!=0 for i in range(x.nj)for j in range(x.nr)):
        raise ValueError('phase-position germ has an unexpected mixed J contact')
    return x.unary(_C(value),_C(first),_C(second),acb(0))


def _geometry_variables(raw,*,differentiate=True):
    from bhsm.interface.muon_holomorphic_normal_geometry import RADIUS0
    import numpy as np
    if len(raw)!=100 or not all(isinstance(x,PhaseJet)for x in raw):
        raise ValueError('explicit packed original geometry100 seeds required')
    q,v,m=raw[:37],raw[37:74],raw[74:98];s,rate=raw[98:]
    sk=(-1.)**np.arange(1,13);sj=(-1.)**np.arange(12)
    Cstar=RADIUS0*(q[0]+sum((a*b for a,b in zip(q[1:13],sk)),PhaseJet(0))+
        sum((a*b for a,b in zip(q[13:25],sj)),PhaseJet(0))).exp()
    lc=(v[0]+sum((a*b for a,b in zip(v[1:13],sk)),PhaseJet(0))+
        sum((a*b for a,b in zip(v[13:25],sj)),PhaseJet(0)))
    delta=s/Cstar;dr=(rate-lc*s)/Cstar
    return q,v,m,delta,dr,np.pi/4+delta,Cstar


def _mid_scalar(x):return complex(float(x.real.mid()),float(x.imag.mid()))


def _C(x):
    from flint import acb
    return x if isinstance(x,acb)else acb(complex(x))


class MaterialSeries3:
    """Only the original implicit chart's three necessary Taylor orders."""
    order=3
    def __init__(self,c):self.c=[_C(x)for x in c]
    @classmethod
    def constant(cls,v):return cls([v]+[0]*cls.order)
    @classmethod
    def variable(cls,v):return cls([v,1]+[0]*(cls.order-1))
    def __add__(self,o):
        o=o if isinstance(o,MaterialSeries3)else self.constant(o)
        return type(self)([x+y for x,y in zip(self.c,o.c)])
    __radd__=__add__
    def __neg__(self):return type(self)([-x for x in self.c])
    def __sub__(self,o):return self+(-o if isinstance(o,MaterialSeries3)else -_C(o))
    def __rsub__(self,o):return -self+o
    def __mul__(self,o):
        o=o if isinstance(o,MaterialSeries3)else self.constant(o)
        return type(self)([sum((self.c[j]*o.c[k-j]for j in range(k+1)),_C(0))for k in range(self.order+1)])
    __rmul__=__mul__
    def reciprocal(self):
        b=[1/self.c[0]]
        for k in range(1,self.order+1):b.append(-sum((self.c[j]*b[k-j]for j in range(1,k+1)),_C(0))/self.c[0])
        return type(self)(b)
    def __truediv__(self,o):return self*(o.reciprocal()if isinstance(o,MaterialSeries3)else 1/_C(o))


class MaterialSeries4(MaterialSeries3):order=4


def _material_series_sin(x):
    c=x.c;s,v=c[0].sin(),c[0].cos()
    values=[s,v*c[1],v*c[2]-s*c[1]**2/2,v*c[3]-s*c[1]*c[2]-v*c[1]**3/6]
    if x.order==4:values.append(v*c[4]-s*(c[1]*c[3]+c[2]**2/2)-v*c[1]**2*c[2]/2+s*c[1]**4/24)
    return type(x)(values)


def _material_constraint_series(a,delta,points):
    import numpy as np
    from bhsm.interface.muon_exact_material_response import _rule
    nodes,weights=_rule(points);wall=float(np.pi/4)+delta
    S=type(delta);Z=S.constant(0);N=S.constant(0)
    for x,w in zip(nodes,weights):
        # These are precisely the original supplied quadrature and pi
        # constants; only arithmetic and the implicit solve gain precision.
        chi=_C(float(np.pi*float(x)/2))
        f=chi+a[0]*(2*chi).sin()+a[1]*(6*chi).sin()
        s=_material_series_sin(2*f);Z+=float(w)*s*s*.25*float(np.pi/2)
        c=wall*float(x);fp=c+a[0]*_material_series_sin(2*c)+a[1]*_material_series_sin(6*c)
        sp=_material_series_sin(2*fp);N+=float(w)*sp*sp*.25*wall
    fw=wall+a[0]*_material_series_sin(2*wall)+a[1]*_material_series_sin(6*wall)
    return [fw-float(np.pi/4),N/Z-.5],Z


_material_chart_cache={}


def anchored_material_chart_mp(delta,*,points=96,derivative_order=3,**unused):
    """Higher precision solve of the SAME two original implicit equations."""
    import numpy as np
    from flint import ctx,acb_mat
    delta=_C(delta);key=(str(delta),int(points),int(ctx.prec),int(derivative_order))
    if key in _material_chart_cache:return _material_chart_cache[key]
    if float(abs(delta).upper())>=2/9:raise ValueError('same original local anchored chart required')
    a=[-21*delta/16,-5*delta/16]
    S=MaterialSeries3 if derivative_order==3 else MaterialSeries4
    def equations(aa):
        e,_=_material_constraint_series([S.constant(v)for v in aa],S.constant(delta),points)
        J=acb_mat(2,2)
        for j in range(2):
            v=[S.constant(z)for z in aa];v[j]=S.variable(aa[j])
            q,_=_material_constraint_series(v,S.constant(delta),points)
            for i in range(2):J[i,j]=q[i].c[1]
        return acb_mat([[q.c[0]]for q in e]),J
    tolerance=2.**(-min(int(ctx.prec)//2,500))
    for k in range(16):
        e,J=equations(a)
        if max(float(abs(e[i,0]).upper())for i in range(2))<=tolerance:break
        step=J.solve(-e);a=[a[i]+step[i,0]for i in range(2)]
    e,J=equations(a)
    if max(float(abs(e[i,0]).upper())for i in range(2))>tolerance:
        raise ArithmeticError('same material implicit equations did not converge at requested precision')
    t=[[z]+[_C(0)]*derivative_order for z in a]
    for order in range(1,derivative_order+1):
        E,_=_material_constraint_series([S(v)for v in t],S.variable(delta),points)
        rhs=acb_mat([[-q.c[order]]for q in E]);coeff=J.solve(rhs)
        for i in range(2):t[i][order]=coeff[i,0]
    E,Z=_material_constraint_series([S(v)for v in t],S.variable(delta),points)
    import math
    result=dict(coefficients=np.asarray(a,dtype=object),derivatives=np.asarray([[math.factorial(k)*v[k]for k in range(1,derivative_order+1)]for v in t],dtype=object),
        normalization=Z.c[0],normalization_derivatives=np.asarray([math.factorial(k)*Z.c[k]for k in range(1,derivative_order+1)],dtype=object),
        points=int(points),implicit_residual=e,implicit_Taylor_residual=E,implicit_jacobian=J,
        same_original_quadrature_and_constraint_law=True,arithmetic_precision_bits=int(ctx.prec))
    _material_chart_cache[key]=result;return result


def _response(chi,delta,dr,chart):
    """Original implicit profile, with its complete necessary two placements."""
    from flint import acb,acb_mat
    from bhsm.interface.muon_exact_material_response import _rule
    general=delta.include_first and any(delta.g[i,0]!=0 for i in range(delta.nj))
    if general:
        if chart['derivatives'].shape[1]<4:raise ValueError('actual original implicit fourth derivative required for position J*h*R')
        a=[delta.unary(_C(chart['coefficients'][j]),*[_C(x)for x in chart['derivatives'][j,:3]])for j in range(2)]
        ap=[delta.unary(*[_C(x)for x in chart['derivatives'][j,:4]])for j in range(2)]
    else:
        a=[_compose_phase_position(delta,chart['coefficients'][j],*chart['derivatives'][j,:2])for j in range(2)]
        ap=[_compose_phase_position(delta,*chart['derivatives'][j,:3])for j in range(2)]
    f=chi+a[0]*_sin(2*chi)+a[1]*_sin(6*chi)
    fp=1+2*a[0]*_cos(2*chi)+6*a[1]*_cos(6*chi)
    ft=dr*(ap[0]*_sin(2*chi)+ap[1]*_sin(6*chi))
    if chi.include_first and not general and any(chi.g[i,0]!=0 for i in range(chi.nj)):
        raise ValueError('material radial position tests require the original fourth implicit operand')
    nodes,weights=_rule(chart['points'])
    av=[_C(v)for v in chart['coefficients']]
    dv=[_C(v)for v in chart['derivatives'][:,0]]
    ddv=[_C(v)for v in chart['derivatives'][:,1]]
    dddv=[_C(v)for v in chart['derivatives'][:,2]]
    N=Nd=Ndd=Nddd=acb(0)
    for x,w in zip(nodes,weights):
        c=chi.value*float(x);basis=[(2*c).sin(),(6*c).sin()]
        fv=c+sum((v*b for v,b in zip(av,basis)),acb(0))
        fd=sum((v*b for v,b in zip(dv,basis)),acb(0))
        fdd=sum((v*b for v,b in zip(ddv,basis)),acb(0))
        fddd=sum((v*b for v,b in zip(dddv,basis)),acb(0))
        W=(2*fv).sin()**2/4;Wf=(4*fv).sin()/2;Wff=2*(4*fv).cos()
        N+=float(w)*W;Nd+=float(w)*Wf*fd
        Ndd+=float(w)*(Wff*fd*fd+Wf*fdd)
        if general:Nddd+=float(w)*(-8*(4*fv).sin()*fd**3+3*Wff*fd*fdd+Wf*fddd)
    N*=chi.value;Nd*=chi.value;Ndd*=chi.value;Nddd*=chi.value
    Z=_C(chart['normalization'])
    Zd,Zdd=(_C(v)for v in chart['normalization_derivatives'][:2])
    wb=[(2*chi.value).sin(),(6*chi.value).sin()]
    fw=chi.value+sum((v*b for v,b in zip(av,wb)),acb(0))
    fdw=sum((v*b for v,b in zip(dv,wb)),acb(0))
    fc=1+2*av[0]*(2*chi.value).cos()+6*av[1]*(6*chi.value).cos()
    Ww=(2*fw).sin()**2/4;Wfw=(4*fw).sin()/2
    if delta.value==0:
        import numpy as np
        Z=acb(float(np.pi/16))
    d0=Nd/Z-N*Zd/Z**2;d1=Ww/Z
    d00=Ndd/Z-2*Nd*Zd/Z**2-N*Zdd/Z**2+2*N*Zd*Zd/Z**3
    d01=Wfw*fdw/Z-Ww*Zd/Z**2;d11=Wfw*fc/Z
    pr=d0*delta.r+d1*chi.r;ph=d0*delta.h+d1*chi.h
    phr=(d0*delta.hR+d1*chi.hR+d00*delta.h*delta.r+
        d01*(delta.h*chi.r+chi.h*delta.r)+d11*chi.h*chi.r)
    if not chi.include_first:
        pg=d0*delta.g+d1*chi.g
        pgR=(d0*delta.gR+d1*chi.gR+d00*delta.g*delta.r+
            d01*(delta.g*chi.r+chi.g*delta.r)+d11*chi.g*chi.r)
        p=PhaseJet(N/Z,pg,r=pr,gR=pgR)
    else:p=PhaseJet(N/Z,h=ph,r=pr,hR=phr)
    if general:
        Zddd=_C(chart['normalization_derivatives'][2])
        fddw=sum((v*b for v,b in zip(ddv,wb)),acb(0))
        fdc=2*dv[0]*(2*chi.value).cos()+6*dv[1]*(6*chi.value).cos()
        fcc=-4*av[0]*(2*chi.value).sin()-36*av[1]*(6*chi.value).sin()
        Wffw=2*(4*fw).cos()
        d000=(Nddd/Z-3*Ndd*Zd/Z**2-3*Nd*Zdd/Z**2+6*Nd*Zd**2/Z**3-
            N*Zddd/Z**2+6*N*Zd*Zdd/Z**3-6*N*Zd**3/Z**4)
        d001=((Wffw*fdw**2+Wfw*fddw)/Z-2*Wfw*fdw*Zd/Z**2-
            Ww*Zdd/Z**2+2*Ww*Zd**2/Z**3)
        d011=(Wffw*fc*fdw+Wfw*fdc)/Z-Wfw*fc*Zd/Z**2
        d111=(Wffw*fc**2+Wfw*fcc)/Z
        xs=[delta,chi];first=[d0,d1];second=[[d00,d01],[d01,d11]]
        third={0:d000,1:d001,2:d011,3:d111}
        pg=sum((first[i]*xs[i].g for i in range(2)),PhaseJet._zg)
        pgh=sum((first[i]*xs[i].gh for i in range(2)),PhaseJet._zg)
        pgR=sum((first[i]*xs[i].gR for i in range(2)),PhaseJet._zgr)
        pghR=sum((first[i]*xs[i].ghR for i in range(2)),PhaseJet._zgr)
        for i in range(2):
            for j in range(2):
                pgh+=second[i][j]*xs[i].g*xs[j].h
                pgR+=second[i][j]*xs[i].g*xs[j].r
                pghR+=second[i][j]*(xs[i].gh*xs[j].r+xs[i].gR*xs[j].h+xs[i].g*xs[j].hR)
                for k in range(2):pghR+=third[i+j+k]*xs[i].g*xs[j].h*xs[k].r
        p=PhaseJet(N/Z,pg,ph,pr,pgh,pgR,phr,pghR)
    return dict(f=f,fprime=fp,fdot=ft,sigma=p-.5,localization_weight=4*p*(1-p))


class OriginalGeometryPatch:
    def __init__(self,material_chart_precision='original_binary',derivative_order=3,material_chart_owner=None):
        self.material_chart_precision=material_chart_precision
        self.derivative_order=int(derivative_order);self.material_chart_owner=material_chart_owner
    def __enter__(self):
        import bhsm.interface.muon_holomorphic_normal_geometry as G
        self.G=G
        names=('Jet','_compose','_sin','_cos','_sqrt','_atanh','_geometry_variables','_response','anchored_holomorphic_chart')
        self.old={k:getattr(G,k)for k in names}
        chart=self.old['anchored_holomorphic_chart']
        G.Jet=PhaseJet;G._compose=_compose_phase_position;G._sin=_sin;G._cos=_cos
        G._sqrt=_sqrt;G._atanh=_atanh;G._geometry_variables=_geometry_variables;G._response=_response
        if self.material_chart_owner is not None:G.anchored_holomorphic_chart=self.material_chart_owner
        elif self.material_chart_precision=='original_binary':G.anchored_holomorphic_chart=lambda d,**kw:chart(_mid_scalar(d),**kw)
        elif self.material_chart_precision=='native_mp':G.anchored_holomorphic_chart=lambda d,**kw:anchored_material_chart_mp(d,derivative_order=self.derivative_order,**kw)
        else:raise ValueError('explicit original_binary or native_mp material coefficient precision required')
        return G
    def __exit__(self,*args):
        for k,v in self.old.items():setattr(self.G,k,v)


def _linear(coefficients,seeds):
    return sum((s*_C(c)for c,s in zip(coefficients,seeds)if c!=0),PhaseJet(0))


def _coefficient_array(base,high=None,low=None):
    """Keep same-law supplied Acb or high/low physical profile tables."""
    import numpy as np
    if high is None:return np.asarray(base)
    high=np.asarray(high);low=np.zeros_like(high)if low is None else np.asarray(low)
    if high.shape!=low.shape:raise ValueError('same physical coefficient table high/low shapes required')
    z=np.empty(high.shape,dtype=object)
    for i in np.ndindex(high.shape):z[i]=_C(high[i])+_C(low[i])
    return z


def _linear_moving_basis(coefficients,first,seeds):
    if first is None:return _linear(coefficients,seeds)
    return sum((s*PhaseJet(_C(c),h=_C(d))for c,d,s in zip(coefficients,first,seeds)if c!=0 or d!=0),PhaseJet(0))


def _comm(a,b):
    import numpy as np
    c=float(1/np.sqrt(2))
    return [c*(a[1]*b[2]-a[2]*b[1]),c*(a[2]*b[0]-a[0]*b[2]),
        c*(a[0]*b[1]-a[1]*b[0]),PhaseJet(0)]


def _add(a,b):return [x+y for x,y in zip(a,b)]
def _norm(a):return sum((x*x for x in a),PhaseJet(0))


def _bulk_density(A,At,Ar,row):
    X=_add([x-y for x,y in zip(At[1],Ar[0])],_comm(A[0],A[1]))
    T=[_add(At[k],_comm(A[0],A[k]))for k in range(2,5)]
    R=[_add(Ar[k],_comm(A[1],A[k]))for k in range(2,5)]
    B=[_add([2*x for x in A[i+2]],_comm(A[j+2],A[k+2]))for i,j,k in((0,1,2),(1,2,0),(2,0,1))]
    e,r,d,k,beta=(row[name]for name in('electric','radial','angular','electric_radial','shift'))
    Y=[[a-beta*b for a,b in zip(u,v)]for u,v in zip(T,R)]
    return (k*_norm(X)+e*sum((_norm(y)for y in Y),PhaseJet(0))-
        r*sum((_norm(y)for y in R),PhaseJet(0))-d*sum((_norm(y)for y in B),PhaseJet(0)))/2


def _scalar_wall(wall,Q,Qdot,cap,rep,nu):
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    gen=higgs_u2_real_representation()['real_generators']
    def O(a,q):
        return [sum((a[k]*sum((complex(gen[k][i,j])*q[j]for j in range(4)if gen[k][i,j]!=0),PhaseJet(0))
            for k in range(4)),PhaseJet(0))for i in range(4)]
    Dt=_add(Qdot,O(wall[0],Q));Ds=[O(wall[k],Q)for k in range(2,5)]
    return (cap['wT']*_norm(Dt)-cap['wS']*sum((_norm(a)for a in Ds),PhaseJet(0))-
        cap['wV']*rep['scalar_matching']['lambda_H']*(_norm(Q)-nu)**2)/VOLUME


def phase_action_contractions(raw_pair,reference_pair,representation,one_lift,maps,
        test_full_indices,direction_high,direction_low,right_high,right_low,*,
        extra_base=None,reference_direction=None,nu_squared_action=4,surface_gamma=None,precision_bits=192,
        include_directional_first=True,material_chart_precision='original_binary',
        allow_geometry_position_tests=False,material_chart_owner=None,
        extra_point_lift_first=None,extra_wall_lift=None,extra_wall_lift_first=None,
        export_point_jacobians=False,include_parent_action=True,
        raw_pair_low=None,reference_pair_low=None,extra_base_low=None,
        export_exact_action_balls=False,direction_exact=None,right_exact=None,
        raw_pair_exact=None,reference_pair_exact=None,extra_base_exact=None,reference_direction_exact=None,
        coefficient_export_only=False):
    """Evaluate same scalar, its full phase gradient and J*h*R contraction."""
    import numpy as np
    from flint import ctx,acb,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_parent_maxwell_full_weak import M
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    ctx.prec=int(precision_bits)
    rep=representation;raw=np.asarray(raw_pair,complex);ref=np.asarray(reference_pair,complex)
    rawlo=np.zeros_like(raw)if raw_pair_low is None else np.asarray(raw_pair_low,complex)
    reflo=np.zeros_like(ref)if reference_pair_low is None else np.asarray(reference_pair_low,complex)
    if rawlo.shape!=raw.shape or reflo.shape!=ref.shape:raise ValueError('same original raw/reference high-low shapes required')
    rawexact=None if raw_pair_exact is None else acb_mat(raw_pair_exact)
    refexact=None if reference_pair_exact is None else acb_mat(reference_pair_exact)
    if any(q is not None and(q.nrows()!=2 or q.ncols()!=268)for q in(rawexact,refexact)):
        raise ValueError('exact raw/reference coefficient inputs require two original268 rows')
    old=np.asarray(maps['old504_to_full'],int);extra=np.asarray(maps['extra_coordinates_to_full'],int)
    T=_coefficient_array(maps.get('extra_point_lift'),maps.get('extra_point_lift_high'),maps.get('extra_point_lift_low'))
    dim=int(maps['full_dimension']);tests=np.asarray(test_full_indices,int)
    Th=None if extra_point_lift_first is None else np.asarray(extra_point_lift_first)
    Wextra=maps.get('extra_wall_lift')if extra_wall_lift is None else extra_wall_lift
    Wextra=_coefficient_array(Wextra,maps.get('extra_wall_lift_high'),maps.get('extra_wall_lift_low'))if Wextra is not None or'extra_wall_lift_high'in maps else None
    Wextra=None if Wextra is None else Wextra.reshape(20,len(extra))
    Wh=None if extra_wall_lift_first is None else np.asarray(extra_wall_lift_first).reshape(20,len(extra))
    if Th is not None and Th.shape!=T.shape:raise ValueError('explicit same-basis point lift first dimensions required')
    if Wh is not None and Wextra is None:raise ValueError('actual wall basis required before its first motion')
    H=(_matrix(np.asarray(direction_high).reshape(dim,1))+_matrix(np.asarray(direction_low).reshape(dim,1))
        if direction_exact is None else acb_mat(direction_exact))
    R=_matrix(right_high)+_matrix(right_low)if right_exact is None else acb_mat(right_exact)
    P=_matrix(one_lift)
    if H.nrows()!=dim or H.ncols()!=1 or R.nrows()!=dim or sorted(np.r_[old,extra].tolist())!=list(range(dim)):
        raise ValueError('complete explicit original/extra coefficient maps and same-state rights required')
    PhaseJet.nj=len(tests);PhaseJet.nr=R.ncols();PhaseJet.include_first=bool(include_directional_first)
    if not include_directional_first and any(H[i,0]!=0 for i in range(dim)):
        raise ValueError('base Hessian-only application requires the explicitly zero h direction')
    def rows(A,ids):return acb_mat([[A[int(i),j]for j in range(A.ncols())]for i in ids])
    def col(A,i):return acb_mat([[A[i,j]]for j in range(A.ncols())])
    rawseeds=[]
    for arm in range(2):
        ids=old[252*arm:252*(arm+1)];test=np.zeros((252,len(tests)))
        for j,t in enumerate(tests):test[ids==t,j]=1
        G=P*_matrix(test);h=P*rows(H,ids);rr=P*rows(R,ids)
        if include_directional_first and not allow_geometry_position_tests and any(G[i,j]!=0 for i in list(range(37))+[98]for j in range(len(tests))):
            raise ValueError('phase tests must hold all original geometry positions, including the wall displacement')
        seeds=[]
        for i in range(268):
            v=acb(complex(raw[arm,i]))+acb(complex(rawlo[arm,i]))if rawexact is None else rawexact[arm,i]
            if h[i,0]==0 and all(G[i,j]==0 for j in range(len(tests)))and all(rr[i,j]==0 for j in range(R.ncols())):
                seeds.append(PhaseJet(v))
            else:seeds.append(PhaseJet(v,None if coefficient_export_only else acb_mat([[G[i,j]]for j in range(len(tests))]),h[i,0],
                acb_mat([[rr[i,j]for j in range(R.ncols())]])))
        rawseeds.append(seeds)
    refh=np.zeros((2,268),complex)if reference_direction is None else np.asarray(reference_direction,complex)
    refhc=_matrix(refh)if reference_direction_exact is None else acb_mat(reference_direction_exact)
    if refhc.nrows()!=2 or refhc.ncols()!=268:raise ValueError('exact reference direction requires two original268 rows')
    if not include_directional_first and any(refhc[a,i]!=0 for a in range(2)for i in range(268)):
        raise ValueError('base Hessian-only application holds the supplied source clocks explicitly')
    refs=[]
    for a in range(2):
        seeds=[]
        for i in range(268):
            v=acb(complex(ref[a,i]))+acb(complex(reflo[a,i]))if refexact is None else refexact[a,i]
            seeds.append(PhaseJet(v)if refhc[a,i]==0 else PhaseJet(v,h=refhc[a,i]))
        refs.append(seeds)
    z=np.zeros(len(extra),complex)if extra_base is None else np.asarray(extra_base,complex)
    zlo=np.zeros_like(z)if extra_base_low is None else np.asarray(extra_base_low,complex)
    if zlo.shape!=z.shape:raise ValueError('same complete extra coefficients high-low shape required')
    zexact=None if extra_base_exact is None else acb_mat(extra_base_exact)
    if zexact is not None and(zexact.nrows()!=len(extra)or zexact.ncols()!=1):raise ValueError('exact extra coefficient input requires the complete extra column')
    zs=[]
    for i,e in enumerate(extra):
        g=acb_mat(len(tests),1)
        for j,t in enumerate(tests):
            if e==t:g[j,0]=1
        rr=acb_mat([[R[int(e),j]for j in range(R.ncols())]])
        if H[int(e),0]==0 and all(g[j,0]==0 for j in range(len(tests)))and all(rr[0,j]==0 for j in range(R.ncols())):
            zs.append(PhaseJet(acb(complex(z[i]))+acb(complex(zlo[i]))if zexact is None else zexact[i,0]))
        else:zs.append(PhaseJet(acb(complex(z[i]))+acb(complex(zlo[i]))if zexact is None else zexact[i,0],g,H[int(e),0],rr))
    gb=_coefficient_array(rep['gauge_basis'],maps.get('original_gauge_basis_high'),maps.get('original_gauge_basis_low')).reshape(len(T),80,20)
    gr=_coefficient_array(rep['gauge_radial_basis'],maps.get('original_gauge_radial_basis_high'),maps.get('original_gauge_radial_basis_low')).reshape(len(T),80,20)
    original_wall=_coefficient_array(rep['wall_trace_map'],maps.get('original_wall_trace_map_high'),maps.get('original_wall_trace_map_low')).reshape(5,4,80)
    order=4 if allow_geometry_position_tests and include_directional_first else 3
    with OriginalGeometryPatch(material_chart_precision,order,material_chart_owner)as G:
        pp=G.holomorphic_geometry_rows(rawseeds[0][:100],rep['rho'],connection_only=True)['rows']
        rp,rc=(G.holomorphic_geometry_rows(x[:100],rep['rho'],connection_only=True)['rows']for x in refs)
        pw=G.holomorphic_geometry_rows(rawseeds[0][:100],[WALL],connection_only=True)['rows'][0]
        rw=[G.holomorphic_geometry_rows(x[:100],[WALL],connection_only=True)['rows'][0]for x in refs]
        if coefficient_export_only:
            # Separate explicit early mode. The regular action path below is
            # unchanged; this return precedes cap/action density assembly.
            if len(tests) or include_parent_action:
                raise ValueError('Coefficient-only export requires zero J tests and child inherited source mode')
            from bhsm_exact_action_balls import export_acb_exact_dyadic
            x=rawseeds[1]
            built=G.holomorphic_geometry_rows(x[:100],rep['rho']);geo=built['rows']
            points=[];densities=[]
            for ir,row in enumerate(geo):
                eff={k:pp[ir][k]-rp[ir][k]+rc[ir][k]
                    for k in('connection_lambda','lambda_tau','lambda_rho')}
                packed=([_linear(gb[ir,:,j],x[100:180])for j in range(20)]+
                    [_linear(gb[ir,:,j],x[180:260])for j in range(20)]+
                    [_linear(gr[ir,:,j],x[100:180])for j in range(20)])
                packed=[a+_linear_moving_basis(T[ir,j],None if Th is None else Th[ir,j],zs)for j,a in enumerate(packed)]
                for k,key in enumerate(('connection_lambda','lambda_tau','lambda_rho')):
                    for j,m in enumerate(M.reshape(-1)):
                        packed[k*20+8+j]+=complex(m)*(eff[key]-(1 if k==0 else 0))
                points.append(packed)
                densities.append([row[name]for name in('electric','radial','angular','electric_radial','shift')])
            effw=pw['connection_lambda']-rw[0]['connection_lambda']+rw[1]['connection_lambda']
            wall=[[_linear(original_wall[f,c],x[100:180])for c in range(4)]for f in range(5)]
            if Wextra is not None:
                for f in range(5):
                    for c in range(4):wall[f][c]+=_linear_moving_basis(Wextra[f*4+c],None if Wh is None else Wh[f*4+c],zs)
            for j,m in enumerate(M.reshape(-1)):wall[2+j//4][j%4]+=complex(m)*(effw-1)
            # Pure boundary weight extraction: the final owned formulas of
            # holomorphic_cap_and_weights, without its bulk/FR/action loop.
            q,v,m,delta,dr,wallchi,Cstar=G._geometry_variables(x[:100])
            F=G._fields(12,q,v,m,wallchi);A,B,N=(F[k]for k in('A','B','N'))
            R4=A*B/G._sqrt(A*A+B*B);U=F['C']*(dr+F['beta'])/N
            lapse=N*G._sqrt(1-U*U)
            weights=[R4**3/lapse,lapse*R4,lapse*R4**3,R4,lapse,U]
            result=dict(coefficient_export_only=True,action_density_or_gradient_or_Hessian_assembled=False,
                zero_J_test_count=np.asarray(0),right_count=np.asarray(R.ncols()),
                inherited_source_parent_minus_reference_parent_plus_reference_child_once=True,
                actual_total_clock_basis_motion_retained_once=Th is not None or Wh is not None,
                cap_weights_extracted_without_cap_action_loop=True,
                arithmetic_precision_bits=np.asarray(int(precision_bits)))
            def export_jets(name,table):
                values=acb_mat([[z.value for z in row]for row in table])
                hs=acb_mat([[z.h for z in row]for row in table])
                rs=acb_mat([[z.r[0,j]for j in range(R.ncols())]for row in table for z in row])
                hrs=acb_mat([[z.hR[0,j]for j in range(R.ncols())]for row in table for z in row])
                for suffix,matrix in(('',values),('_h',hs),('_R',rs),('_hR',hrs)):
                    key=name+suffix;result[key+'_high'],result[key+'_low']=_split(matrix)
                    result.update(export_acb_exact_dyadic(matrix,key+'_exact'))
            for name,table in(('point',points),('density',densities),('wall',[sum(wall,[])]),
                ('boundary_weights',[weights]),('material_coordinates',[[delta,dr,wallchi,Cstar]]),
                ('raw_child',[x]),('raw_parent',[rawseeds[0]]),('raw_references',[sum(refs,[])])):
                export_jets(name,table)
            for key in('coefficients','derivatives','normalization','normalization_derivatives','implicit_Taylor_residual','implicit_jacobian'):
                value=built['response_chart'][key]
                if isinstance(value,acb_mat):matrix=acb_mat(value)
                else:
                    value=np.asarray(value,dtype=object)
                    if value.ndim==0:value=value.reshape(1,1)
                    elif value.ndim==1:value=value.reshape(1,-1)
                    matrix=acb_mat(value.tolist())
                name='implicit_material_'+key
                result[name+'_high'],result[name+'_low']=_split(matrix)
                result.update(export_acb_exact_dyadic(matrix,name+'_exact'))
            for key,matrix in(('actual_complete_right',R),('actual_total_clock',H),('reference_clock_once',refhc)):
                result[key+'_high'],result[key+'_low']=_split(matrix)
                result.update(export_acb_exact_dyadic(matrix,key+'_exact'))
            return result
        total=PhaseJet(0);branches={};child_points=[];child_densities=[];child_wall=None
        arms=[0,1]if include_parent_action and any(t<252 for t in tests)else[1]
        for arm in arms:
            x=rawseeds[arm]
            cap=G.holomorphic_cap_and_weights(x[:100],points=rep['cap_points'])
            geo=G.holomorphic_geometry_rows(x[:100],rep['rho'])['rows']
            val=cap['total']
            if surface_gamma is not None:val+=surface_gamma*cap['surface_per_gamma']
            for ir,(row,w0)in enumerate(zip(geo,rep['radial_quadrature'])):
                eff={k:pp[ir][k]if arm==0 else pp[ir][k]-rp[ir][k]+rc[ir][k]
                    for k in('connection_lambda','lambda_tau','lambda_rho')}
                packed=([_linear(gb[ir,:,j],x[100:180])for j in range(20)]+
                    [_linear(gb[ir,:,j],x[180:260])for j in range(20)]+
                    [_linear(gr[ir,:,j],x[100:180])for j in range(20)])
                if arm==1:packed=[a+_linear_moving_basis(T[ir,j],None if Th is None else Th[ir,j],zs)for j,a in enumerate(packed)]
                for k,key in enumerate(('connection_lambda','lambda_tau','lambda_rho')):
                    for j,m in enumerate(M.reshape(-1)):
                        packed[k*20+8+j]+=complex(m)*(eff[key]-(1 if k==0 else 0))
                if arm==1:
                    child_points.append([(x.value,x.h,x.g if export_point_jacobians else None)for x in packed])
                    child_densities.append([(row[name].value,row[name].h,row[name].g if export_point_jacobians else None)
                        for name in('electric','radial','angular','electric_radial','shift')])
                A,At,Ar=([[packed[20*k+4*f+c]for c in range(4)]for f in range(5)]for k in range(3))
                lam,lt,lr=(row[k]for k in('connection_lambda','lambda_tau','lambda_rho'))
                e,r,d,beta=(row[k]for k in('electric','radial','angular','shift'))
                baseline=.5*float(np.sum(M*M))*(e*(lt-beta*lr)**2-r*lr**2-d*(2*(lam-1)*lam)**2)
                val+=float(MAXWELL_TO_CAP)*float(w0)*(_bulk_density(A,At,Ar,row)-baseline)
            effw=pw['connection_lambda']if arm==0 else pw['connection_lambda']-rw[0]['connection_lambda']+rw[1]['connection_lambda']
            wall=[[_linear(original_wall[f,c],x[100:180])for c in range(4)]for f in range(5)]
            if arm==1 and Wextra is not None:
                for f in range(5):
                    for c in range(4):wall[f][c]+=_linear_moving_basis(Wextra[f*4+c],None if Wh is None else Wh[f*4+c],zs)
            for j,m in enumerate(M.reshape(-1)):wall[2+j//4][j%4]+=complex(m)*(effw-1)
            if arm==1:child_wall=[(a.value,a.h)for f in wall for a in f]
            val+=_scalar_wall(wall,x[260:264],x[264:268],cap,rep,nu_squared_action)
            branches[arm]=val;total+=val
    result=dict(test_full_action_indices=tests,complete_augmented_direction_high=np.asarray(direction_high),
        complete_augmented_direction_low=np.asarray(direction_low),actual_right_high=np.asarray(right_high),
        actual_right_low=np.asarray(right_low),scalar_value=np.asarray(_mid_scalar(total.value)),
        complete_phase_J_h_R_analytic=bool(include_directional_first),unused_full_third_tensor_formed=False,
        phase_geometry_positions_held_exactly=bool(include_directional_first and not allow_geometry_position_tests),
        fourth_implicit_profile_derivative_not_required=order<4,
        arithmetic_precision_bits=int(precision_bits),material_chart_precision=np.asarray(material_chart_precision),reference_clock_direction=refh,
        original_parent_reference_child_source_contacts_retained_once=True,moving_source_adjoint_inserted=False)
    result.update(extra_wall_scalar_action_retained=Wextra is not None,
        actual_epoch_basis_motion_retained_once=Th is not None or Wh is not None,
        basis_held_on_J_and_R_but_actual_h_motion_applied=Th is not None or Wh is not None)
    result['parent_own_action_included']=0 in branches
    if export_exact_action_balls:
        from bhsm_exact_action_balls import export_acb_exact_dyadic
        result.update(export_acb_exact_dyadic(H,'complete_augmented_direction_exact'))
        result.update(export_acb_exact_dyadic(R,'actual_right_exact'))
        result.update(export_acb_exact_dyadic(refhc,'reference_direction_exact'))
        result.update(export_acb_exact_dyadic(acb_mat([[total.value]]),'scalar_value_exact'))
        result['exact_action_ball_export_format']=np.asarray('acb_exact_dyadic_midpoint_and_radius_v1')
        result['exact_direction_input_used']=direction_exact is not None
        result['exact_right_input_used']=right_exact is not None
    for name,m in dict(phase_gradient=total.g,phase_Hessian_on_actual_right=total.gR,
            phase_gradient_first=total.gh,phase_Hessian_first_on_actual_right=total.ghR).items():
        result[name+'_high'],result[name+'_low']=_split(m)
        if export_exact_action_balls:result.update(export_acb_exact_dyadic(m,name+'_exact'))
    for arm,jet in branches.items():
        name='parent_own'if arm==0 else'child_inherited'
        for key,m in dict(phase_gradient=jet.g,phase_Hessian_on_actual_right=jet.gR,
                phase_gradient_first=jet.gh,phase_Hessian_first_on_actual_right=jet.ghR).items():
            result[name+'_'+key+'_high'],result[name+'_'+key+'_low']=_split(m)
            if export_exact_action_balls:result.update(export_acb_exact_dyadic(m,name+'_'+key+'_exact'))
    if child_points:
        for name,rows0 in (('child_point_coefficients',child_points),('child_metric_density',child_densities)):
            values=acb_mat([[x[0]for x in row]for row in rows0])
            first=acb_mat([[x[1]for x in row]for row in rows0])
            result[name+'_high'],result[name+'_low']=_split(values)
            result[name+'_directional_first_high'],result[name+'_directional_first_low']=_split(first)
            if export_exact_action_balls:
                result.update(export_acb_exact_dyadic(values,name+'_exact'))
                result.update(export_acb_exact_dyadic(first,name+'_directional_first_exact'))
            if export_point_jacobians:
                jac=acb_mat([[x[2][j,0]for j in range(len(tests))]for row in rows0 for x in row])
                jh,jl=_split(jac)
                result[name+'_test_first_high']=jh.reshape(len(rows0),len(rows0[0]),len(tests))
                result[name+'_test_first_low']=jl.reshape(len(rows0),len(rows0[0]),len(tests))
        wall=acb_mat([[x[0]for x in child_wall]])
        wallh=acb_mat([[x[1]for x in child_wall]])
        result['child_wall_connection_high'],result['child_wall_connection_low']=_split(wall)
        result['child_wall_connection_directional_first_high'],result['child_wall_connection_directional_first_low']=_split(wallh)
        if export_exact_action_balls:
            result.update(export_acb_exact_dyadic(wall,'child_wall_connection_exact'))
            result.update(export_acb_exact_dyadic(wallh,'child_wall_connection_directional_first_exact'))
    result['literal_high_precision_point_density_coefficients_from_same_scalar_owner']=True
    return result


def run_first_clock(repository,output,*,precision_bits=192,material_chart_precision='original_binary'):
    import numpy as np
    from flint import ctx,acb_mat
    root,out=Path(repository),Path(output)
    if out.exists():raise FileExistsError('preserve all analytic phase clock controls')
    out.mkdir(parents=True);sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    ctx.prec=int(precision_bits);pins={};archives={};a=root/'artifacts'
    p=a/'muon_baton_zoo_augmented_source_domain_derivative_20261013'
    def read(q):
        q=Path(q);pins[str(q)]=sha256(q.read_bytes()).hexdigest()
        with np.load(q,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    base=read(p/'first_cell_column0_run_1/same_augmented_first_cell_original_action_base.npz')
    directions=read(p/'first_cell_column0_run_1/actual_new_proper_first_cell_direction_and_separated_rights.npz')
    clock=read(p/'first_cell_full_clock_run_2/actual_clock_direction_and_separate_rights.npz')
    current=read(a/'muon_baton_zoo_saved_rate_operands_20261013/joint_run_1/cell_0000_independent_rate_and_source_operands.npz')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    maps={k:base[k]for k in('old504_to_full','extra_coordinates_to_full','extra_point_lift')}
    maps['full_dimension']=len(base['Hessian'])
    clockh=clock['full_augmented_base_master_rate'].copy();clockl=np.zeros_like(clockh)
    clockh[maps['old504_to_full'][252:]]=current['original_phase_rate_high'][:,0]
    clockl[maps['old504_to_full'][252:]]=current['original_phase_rate_low'][:,0]
    # All literal child v/y phase coordinates: no inferred variable span.
    n=154;tests=np.arange(252+n,len(base['Hessian']))
    print(json.dumps(dict(stage='complete_phase_same_action_clock_started',tests=len(tests),rights=8)),flush=True)
    result=phase_action_contractions(base['raw_pair'],base['reference_pair'],rep,P,maps,tests,
        clockh,clockl,
        directions['child_and_parent_separated_right_high'],directions['child_and_parent_separated_right_low'],
        reference_direction=clock['reference_pair_rate'],precision_bits=precision_bits,material_chart_precision=material_chart_precision)
    hi,lo=result['phase_Hessian_on_actual_right_high'],result['phase_Hessian_on_actual_right_low']
    ref=_matrix(base['Hessian'][tests])*(_matrix(directions['child_and_parent_separated_right_high'])+
        _matrix(directions['child_and_parent_separated_right_low']))
    defect=_matrix(hi)+_matrix(lo)-ref
    gradient_defect=_matrix(result['phase_gradient_high'])+_matrix(result['phase_gradient_low'])-_matrix(base['gradient'][tests,None])
    q=out/'complete_child_phase_full_clock_contracted_action.npz';_compressed_npz(q,result)
    archives[q.name]=dict(bytes=q.stat().st_size,sha256=sha256(q.read_bytes()).hexdigest())
    pins[str(Path(__file__))]=sha256(Path(__file__).read_bytes()).hexdigest()
    report=dict(classification='COMPLETE_PHASE_SAME_ORIGINAL_SCALAR_ACTION_ANALYTIC_CLOCK_CONTRACTION',
        input_hashes=pins,archives=archives,phase_rows=len(tests),actual_right_columns=8,
        phase_gradient_difference_upper=_upper(gradient_defect),phase_Hessian_action_difference_upper=_upper(defect),
        full_outgoing_realization_admitted=False,physical_terminal_derivative_admitted=False)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(report),flush=True);return report


def run_birth(repository,output,*,precision_bits=192,material_chart_precision='original_binary'):
    """All original phase rows on the three actual proper birth directions."""
    import numpy as np
    from flint import ctx,acb_mat
    root,out=Path(repository),Path(output)
    if out.exists():raise FileExistsError('preserve all complete phase birth contractions')
    out.mkdir(parents=True);sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm_baton_zoo_augmented_source_domain_derivative import augmented_maps
    ctx.prec=int(precision_bits);a=root/'artifacts';pins={};archives={};records=[]
    bfolder=a/'muon_baton_zoo_radial_completion_20261013/action_gauge_degree2_run_1'
    old=a/'muon_baton_zoo_row490_analytic_precision_20261013/birth_and_clock_run_1'
    def read(q):
        q=Path(q);pins[str(q)]=sha256(q.read_bytes()).hexdigest()
        with np.load(q,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def save(name,data):
        q=out/name;_compressed_npz(q,data);archives[name]=dict(bytes=q.stat().st_size,sha256=sha256(q.read_bytes()).hexdigest())
    b=read(bfolder/'enlarged_birth_proper_three_columns_and_canonical_seeds.npz')
    c=read(bfolder/'birth_current288_connected_action_and_rate_operands.npz')
    r=read(bfolder/'enlarged_birth_radial_action.npz');maps=augmented_maps(c,r)
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    tests=b['phase_to_full_action_indices'];n=int(b['dynamic_count'])
    rights=_matrix(b['full_two_arm_fixed_position_phase_high'])+_matrix(b['full_two_arm_fixed_position_phase_low'])
    ref=_matrix(b['full_two_arm_Hessian'][tests])*rights
    for j in range(3):
        print(json.dumps(dict(stage='complete_phase_same_action_birth_started',direction=j,phase_rows=len(tests))),flush=True)
        result=phase_action_contractions(b['raw_pair'],b['reference_pair'],rep,P,maps,tests,
            b['full_two_arm_fixed_position_phase_high'][:,j],b['full_two_arm_fixed_position_phase_low'][:,j],
            b['full_two_arm_fixed_position_phase_high'],b['full_two_arm_fixed_position_phase_low'],precision_bits=precision_bits,
            material_chart_precision=material_chart_precision)
        defect=_matrix(result['phase_Hessian_on_actual_right_high'])+_matrix(result['phase_Hessian_on_actual_right_low'])-ref
        result['supported_full_action_rows']=tests
        result['analytic_supported_Hessian_on_right_high']=result['phase_Hessian_on_actual_right_high']
        result['analytic_supported_Hessian_on_right_low']=result['phase_Hessian_on_actual_right_low']
        save(f'birth_direction_{j}_analytic_supported_DhHfull_on_complete_U3.npz',result)
        exact=_matrix(result['phase_Hessian_first_on_actual_right_high'])+_matrix(result['phase_Hessian_first_on_actual_right_low'])
        for radius in(.032,.016,.008):
            d=read(old/f'birth_direction_{j}_radius_{radius:.0e}_analytic_supported_repaired_DhHfull_on_complete_U3.npz')
            original=_matrix(d['contracted_Hessian_first_on_actual_right_high'])+_matrix(d['contracted_Hessian_first_on_actual_right_low'])
            for q,i in enumerate(tests):
                for k in range(3):original[int(i),k]=exact[q,k]
            d['contracted_Hessian_first_on_actual_right_high'],d['contracted_Hessian_first_on_actual_right_low']=_split(original)
            d.update(complete_phase_rows_analytic=tests,unsupported_position_rows_retained_from_original_polarization=True)
            save(f'birth_direction_{j}_radius_{radius:.0e}_analytic_supported_repaired_DhHfull_on_complete_U3.npz',d)
        rec=dict(direction=j,phase_Hessian_action_difference_upper=_upper(defect),complete_phase_rows=len(tests))
        records.append(rec);print(json.dumps(dict(stage='complete_phase_same_action_birth_finished',**rec)),flush=True)
    pins[str(Path(__file__))]=sha256(Path(__file__).read_bytes()).hexdigest()
    report=dict(classification='COMPLETE_PHASE_SAME_ORIGINAL_SCALAR_ACTION_ANALYTIC_BIRTH_CONTRACTIONS',
        records=records,input_hashes=pins,archives=archives,physical_terminal_derivative_admitted=False,
        all_phase_thirds_analytic=True,unsupported_position_thirds_retained_from_original_polarization=True,
        completed_integrations_repeated=False)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    return report


def run_first_cell_full_tests(repository,output,*,precision_bits=192,columns=(0,1,2),**unused):
    """Actual first-cell full source/domain DhH on all supplied right columns."""
    import numpy as np
    from flint import ctx
    root,out=Path(repository),Path(output)
    if out.exists():raise FileExistsError('preserve complete original contracted source/domain jets')
    out.mkdir(parents=True);sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    ctx.prec=int(precision_bits);a=root/'artifacts';pins={};archives={};records=[]
    p=a/'muon_baton_zoo_augmented_source_domain_derivative_20261013'
    def read(q):
        q=Path(q);pins[str(q)]=sha256(q.read_bytes()).hexdigest()
        with np.load(q,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def save(name,data):
        q=out/name;_compressed_npz(q,data);archives[name]=dict(bytes=q.stat().st_size,sha256=sha256(q.read_bytes()).hexdigest())
    base=read(p/'first_cell_column0_run_1/same_augmented_first_cell_original_action_base.npz')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    maps={k:base[k]for k in('old504_to_full','extra_coordinates_to_full','extra_point_lift')}
    maps['full_dimension']=len(base['Hessian']);tests=np.arange(maps['full_dimension'])
    for j in columns:
        directions=read(p/f'first_cell_column{j}_run_1/actual_new_proper_first_cell_direction_and_separated_rights.npz')
        print(json.dumps(dict(stage='all_original_source_domain_test_rows_started',direction=j,test_rows=len(tests))),flush=True)
        result=phase_action_contractions(base['raw_pair'],base['reference_pair'],rep,P,maps,tests,
            directions['complete_augmented_direction_high'][:,0],directions['complete_augmented_direction_low'][:,0],
            directions['child_and_parent_separated_right_high'],directions['child_and_parent_separated_right_low'],
            precision_bits=precision_bits,material_chart_precision='native_mp',allow_geometry_position_tests=True)
        rhs=_matrix(directions['child_and_parent_separated_right_high'])+_matrix(directions['child_and_parent_separated_right_low'])
        diff=(_matrix(result['phase_Hessian_on_actual_right_high'])+
            _matrix(result['phase_Hessian_on_actual_right_low'])-_matrix(base['Hessian'])*rhs)
        gdiff=(_matrix(result['phase_gradient_high'])+_matrix(result['phase_gradient_low'])-_matrix(base['gradient'][:,None]))
        for suffix in('high','low'):
            C=result['phase_Hessian_first_on_actual_right_'+suffix]
            leaf=result['child_inherited_phase_Hessian_first_on_actual_right_'+suffix]
            result['contracted_Hessian_first_on_actual_right_'+suffix]=C
            result['daughter_bulk_DhHzz_on_actual_child4_'+suffix]=C[252:,:4]
            result['inherited_source_DhHzp_on_actual_parent4_'+suffix]=C[252:,4:]
            result['inherited_return_DhHpz_on_actual_child4_'+suffix]=leaf[:252,:4]
            result['direct_CHILD_source_DhHpp_on_actual_parent4_'+suffix]=leaf[:252,4:]
        save(f'direction_{j}_complete_original_analytic_contracted_source_domain_action.npz',result)
        rec=dict(direction=j,full_original_test_rows=len(tests),gradient_original_binary_difference_upper=_upper(gdiff),
            full_Hessian_action_original_binary_difference_upper=_upper(diff))
        records.append(rec);print(json.dumps(dict(stage='all_original_source_domain_test_rows_finished',**rec)),flush=True)
    pins[str(Path(__file__))]=sha256(Path(__file__).read_bytes()).hexdigest()
    report=dict(classification='ALL_ORIGINAL_AUGMENTED_ACTION_ROWS_CONTRACTED_SOURCE_DOMAIN_THIRD_JETS',
        records=records,input_hashes=pins,archives=archives,completed_integrations_repeated=False,
        physical_terminal_derivative_admitted=False,full_unused_third_tensor_formed=False)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');return report


def run_fresh_original_contracted_controls(repository,output,*,precision_bits=192,direction_index=0,**unused):
    """Fresh original second-jet callbacks at three radii, no third jet use."""
    import numpy as np
    from flint import ctx,acb_mat
    root,out=Path(repository),Path(output)
    if out.exists():raise FileExistsError('preserve fresh original contracted derivative controls')
    out.mkdir(parents=True);sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper,_mid
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    ctx.prec=int(precision_bits);a=root/'artifacts';pins={};records=[];archives={};j=int(direction_index)
    p=a/'muon_baton_zoo_augmented_source_domain_derivative_20261013'
    def read(q):
        q=Path(q);pins[str(q)]=sha256(q.read_bytes()).hexdigest()
        with np.load(q,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def pair(z,k):return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    def save(name,z):
        q=out/name;_compressed_npz(q,z);archives[name]=dict(bytes=q.stat().st_size,sha256=sha256(q.read_bytes()).hexdigest())
    base=read(p/'first_cell_column0_run_1/same_augmented_first_cell_original_action_base.npz')
    d=read(p/f'first_cell_column{j}_run_1/actual_new_proper_first_cell_direction_and_separated_rights.npz')
    analytic_folder=a/'muon_baton_zoo_complete_phase_analytic_20261014'/('first_cell_full_rows_column0_run_1'if j==0 else'first_cell_full_rows_columns1_2_run_1')
    exact=pair(read(analytic_folder/f'direction_{j}_complete_original_analytic_contracted_source_domain_action.npz'),'phase_Hessian_first_on_actual_right')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=_matrix(phase['coordinates']['lift'])
    maps={k:base[k]for k in('old504_to_full','extra_coordinates_to_full','extra_point_lift')}
    maps['full_dimension']=len(base['Hessian']);dim=maps['full_dimension'];tests=np.arange(dim)
    h=pair(d,'complete_augmented_direction');scale=float(np.max(abs(_mid(h))))
    def rows(A,ids):return acb_mat([[A[int(i),k]for k in range(A.ncols())]for i in ids])
    rawh=[P*rows(h,maps['old504_to_full'][252*arm:252*(arm+1)])for arm in range(2)]
    rawbase=[_matrix(base['raw_pair'][arm,:,None])for arm in range(2)]
    zh=rows(h,maps['extra_coordinates_to_full']);previous=None
    for radius in(.032,.016,.008):
        branches=[]
        for axis_index,axis in enumerate((1,1j,-1,-1j)):
            offset=_C(axis)*_C(radius)/_C(scale)
            rawpairs=[_split(rawbase[arm]+offset*rawh[arm])for arm in range(2)]
            rh=np.stack([v[0][:,0]for v in rawpairs]);rl=np.stack([v[1][:,0]for v in rawpairs])
            zhi,zlo=_split(offset*zh)
            result=phase_action_contractions(rh,base['reference_pair'],rep,phase['coordinates']['lift'],maps,tests,
                np.zeros(dim),np.zeros(dim),d['child_and_parent_separated_right_high'],d['child_and_parent_separated_right_low'],
                raw_pair_low=rl,extra_base=zhi[:,0],extra_base_low=zlo[:,0],include_directional_first=False,
                material_chart_precision='native_mp',precision_bits=precision_bits)
            branches.append(pair(result,'phase_Hessian_on_actual_right'))
            save(f'radius_{radius:.0e}_axis_{axis_index}_fresh_original_contracted_second_jet.npz',dict(
                phase_Hessian_on_actual_right_high=result['phase_Hessian_on_actual_right_high'],
                phase_Hessian_on_actual_right_low=result['phase_Hessian_on_actual_right_low'],
                actual_raw_pair_high=rh,actual_raw_pair_low=rl,actual_extra_coefficients_high=zhi,
                actual_extra_coefficients_low=zlo,actual_right_high=d['child_and_parent_separated_right_high'],
                actual_right_low=d['child_and_parent_separated_right_low'],test_full_action_indices=tests,
                third_directional_jet_not_evaluated=True,material_chart_precision=np.asarray('native_mp')))
            print(json.dumps(dict(stage='fresh_original_contracted_second_jet_branch',direction=j,radius=radius,axis=axis_index)),flush=True)
        numerical=_C(scale)*(branches[0]-1j*branches[1]-branches[2]+1j*branches[3])/(4*_C(radius))
        err=numerical-exact;hi,lo=_split(numerical)
        save(f'radius_{radius:.0e}_fresh_original_contracted_derivative_control.npz',dict(
            fresh_original_DhH_on_actual_right_high=hi,fresh_original_DhH_on_actual_right_low=lo,
            analytic_DhH_on_actual_right_high=_split(exact)[0],analytic_DhH_on_actual_right_low=_split(exact)[1],
            direction_normalization=np.asarray(scale),actual_direction_high=d['complete_augmented_direction_high'],
            actual_direction_low=d['complete_augmented_direction_low'],radius=np.asarray(radius)))
        rec=dict(direction=j,radius=radius,fresh_original_vs_analytic_absolute_upper=_upper(err),
            relative_frobenius_error=float(np.linalg.norm(_mid(err))/np.linalg.norm(_mid(exact))),
            prior_radius_change_norm=None if previous is None else float(np.linalg.norm(_mid(numerical-previous))))
        records.append(rec);previous=numerical;print(json.dumps(dict(stage='fresh_original_full_contracted_derivative_control',**rec)),flush=True)
    pins[str(Path(__file__))]=sha256(Path(__file__).read_bytes()).hexdigest()
    report=dict(classification='THREE_FRESH_SAME_ORIGINAL_SCALAR_CONTRACTED_SECOND_JET_DERIVATIVE_CONTROLS',
        records=records,input_hashes=pins,archives=archives,same_primal_same_rights_same_field_profile_chart=True,
        second_jet_callbacks_independent_of_analytic_third_product_rule=True,
        high_low_perturbed_primal_preserved_without_binary_reassembly=True,
        physical_terminal_derivative_admitted=False)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    p.add_argument('--precision',type=int,default=192);p.add_argument('--birth',action='store_true')
    p.add_argument('--material-chart',choices=('original_binary','native_mp'),default='original_binary')
    p.add_argument('--first-cell-full-tests',action='store_true');p.add_argument('--fresh-full-controls',action='store_true')
    p.add_argument('--direction-index',type=int,default=0);p.add_argument('--columns',type=int,nargs='+',default=[0,1,2]);args=p.parse_args()
    try:
        if args.fresh_full_controls:run_fresh_original_contracted_controls(args.repository,args.output,precision_bits=args.precision,direction_index=args.direction_index)
        elif args.first_cell_full_tests:run_first_cell_full_tests(args.repository,args.output,precision_bits=args.precision,columns=tuple(args.columns))
        else:(run_birth if args.birth else run_first_clock)(args.repository,args.output,precision_bits=args.precision,
            material_chart_precision=args.material_chart)
    except Exception as e:
        q=Path(args.output)/'failure.json'
        if q.parent.exists()and not q.exists():q.write_text(json.dumps(dict(type=type(e).__name__,message=str(e)),indent=2)+'\n')
        raise

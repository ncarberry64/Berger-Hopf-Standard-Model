"""Literal analytic extension of the finite anchored cap geometry two-jet.

All constants/integrands are the retained exact-material owner. Complex
coefficients enter independent analytic placements, never a conjugate or
a real projection. The response branch is the local implicit continuation
of f(wall)=pi/4 and sigma(wall)=0, with its normalization unchanged.
"""
from __future__ import annotations
import numpy as np
from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_exact_material_response import _rule
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0,HOPF_ORBIT_VOLUME
from .aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from .muon_parent_retarded_hypercharge import WALL


def _compose(x,value,first,second):
    return Jet(value,first*x.gradient,first*x.hessian+second*np.outer(x.gradient,x.gradient))


def _sin(x):return _compose(x,np.sin(x.value),np.cos(x.value),-np.sin(x.value))
def _cos(x):return _compose(x,np.cos(x.value),-np.sin(x.value),-np.cos(x.value))
def _sqrt(x):
    r=np.sqrt(complex(x.value))
    if not r or r.real<=0:raise ValueError('same local principal metric square-root branch required')
    return _compose(x,r,1/(2*r),-1/(4*r**3))
def _atanh(x):
    u=complex(x.value)
    if abs(u)>=1:raise ValueError('retained local timelike analytic chart required')
    return _compose(x,np.arctanh(u),1/(1-u*u),2*u/(1-u*u)**2)


class _Series3:
    def __init__(self,c):self.c=np.asarray(c,complex)
    @classmethod
    def constant(cls,value):
        a=np.asarray(value,complex);return cls(np.stack((a,np.zeros_like(a),np.zeros_like(a),np.zeros_like(a))))
    @classmethod
    def variable(cls,value):return cls([value,1.,0.,0.])
    def __add__(self,o):
        o=o if isinstance(o,_Series3)else _Series3.constant(o);return _Series3(self.c+o.c)
    __radd__=__add__
    def __neg__(self):return _Series3(-self.c)
    def __sub__(self,o):return self+(-o if isinstance(o,_Series3)else -np.asarray(o))
    def __rsub__(self,o):return -self+o
    def __mul__(self,o):
        o=o if isinstance(o,_Series3)else _Series3.constant(o)
        return _Series3(np.stack([sum(self.c[j]*o.c[k-j]for j in range(k+1))for k in range(4)]))
    __rmul__=__mul__
    def reciprocal(self):
        b=[1/self.c[0]]
        for k in range(1,4):b.append(-sum(self.c[j]*b[k-j]for j in range(1,k+1))/self.c[0])
        return _Series3(np.stack(b))
    def __truediv__(self,o):return self*(o.reciprocal()if isinstance(o,_Series3)else 1/np.asarray(o))
    def integral(self,w):return _Series3(self.c@w)


def _series_sin(x):
    c=x.c;s,v=np.sin(c[0]),np.cos(c[0])
    return _Series3(np.stack((s,v*c[1],v*c[2]-s*c[1]**2/2,v*c[3]-s*c[1]*c[2]-v*c[1]**3/6)))


def _constraint_series(a,delta,points):
    x,w=_rule(points);wall=np.pi/4+delta;chi=np.pi*x/2
    f=_Series3.constant(chi)+a[0]*np.sin(2*chi)+a[1]*np.sin(6*chi)
    s=_series_sin(2*f);Z=(s*s*.25).integral(w)*(np.pi/2)
    c=wall*x;fp=c+a[0]*_series_sin(2*c)+a[1]*_series_sin(6*c)
    sp=_series_sin(2*fp);N=(sp*sp*.25).integral(w)*wall
    fw=wall+a[0]*_series_sin(2*wall)+a[1]*_series_sin(6*wall)
    return np.stack(((fw-np.pi/4).c,(N/Z-.5).c)),Z.c


def anchored_holomorphic_chart(delta,*,points=96,tolerance=4e-15):
    delta=complex(delta)
    if abs(delta)>=2/9:raise ValueError('same local anchored material chart required')
    a=-np.array([21.,5.])*delta/16
    def equations(a):
        e,_=_constraint_series([_Series3.constant(v)for v in a],_Series3.constant(delta),points)
        J=np.empty((2,2),complex)
        for j in range(2):
            v=[_Series3.constant(x)for x in a];v[j]=_Series3.variable(a[j])
            q,_=_constraint_series(v,_Series3.constant(delta),points);J[:,j]=q[:,1]
        return e[:,0],J
    for _ in range(16):
        e,J=equations(a)
        if np.max(abs(e))<=tolerance:break
        a+=np.linalg.solve(J,-e)
    e,J=equations(a)
    if np.max(abs(e))>tolerance or 1-2*abs(a[0])-6*abs(a[1])<=0:
        raise ValueError('holomorphic implicit branch left its retained local chart')
    t=np.zeros((2,4),complex);t[:,0]=a
    for order in range(1,4):
        E,_=_constraint_series([_Series3(v)for v in t],_Series3.variable(delta),points)
        t[:,order]=np.linalg.solve(J,-E[:,order])
    E,Z=_constraint_series([_Series3(v)for v in t],_Series3.variable(delta),points)
    return dict(coefficients=a,derivatives=t[:,1:]*np.array([1.,2.,6.]),normalization=Z[0],
        normalization_derivatives=Z[1:]*np.array([1.,2.,6.]),points=points,
        implicit_residual=e,implicit_Taylor_residual=E,implicit_jacobian=J)


def _fields(order,q,v,m,chi):
    n=len(q[0].gradient);lin=lambda a,b:sum((x*y for x,y in zip(a,b)),Jet.constant(0.,n))
    ks=np.arange(1,order+1);js=np.arange(order)
    ck=[_cos(4*int(j)*chi)for j in ks];cj=[_cos(4*int(j)*chi)for j in js]
    sk=[_sin(4*int(j)*chi)for j in ks];sj=[_sin(4*int(j)*chi)for j in js]
    window=_sin(2*chi)**2;wp=2*_sin(4*chi)
    u=lin(q[1:1+order],ck);w=window*lin(q[1+order:1+2*order],cj);b=window*lin(q[1+2*order:1+3*order],cj)
    up=lin(q[1:1+order],[-4*int(j)*x for j,x in zip(ks,sk)])
    wpc=[wp*x-4*int(j)*window*y for j,x,y in zip(js,cj,sj)]
    bp=lin(q[1+2*order:1+3*order],wpc);cp=up+lin(q[1+order:1+2*order],wpc)
    ap=up+bp-_sin(chi)/_cos(chi);bprime=up-bp+_cos(chi)/_sin(chi)
    radius=RADIUS0*q[0].exp();C=radius*(u+w).exp();A=radius*(u+b).exp()*_cos(chi);B=radius*(u-b).exp()*_sin(chi)
    N=lin(m[:order],ck).exp();np_=lin(m[:order],[-4*int(j)*x for j,x in zip(ks,sk)])
    beta=_sin(4*chi)*lin(m[order:],cj)
    betap=4*_cos(4*chi)*lin(m[order:],cj)+_sin(4*chi)*lin(m[order:],[-4*int(j)*x for j,x in zip(js,sj)])
    udot=lin(v[1:1+order],ck);wdot=window*lin(v[1+order:1+2*order],cj);bdot=window*lin(v[1+2*order:1+3*order],cj)
    return dict(C=C,A=A,B=B,N=N,cp=cp,ap=ap,bp=bprime,np=np_,beta=beta,betap=betap,
        lc=v[0]+udot+wdot,la=v[0]+udot+bdot,lb=v[0]+udot-bdot)


def _geometry_variables(raw,*,differentiate=True):
    raw=np.asarray(raw,complex)
    if raw.shape!=(100,)or not np.isfinite(raw).all():raise ValueError('same geometry100 complex-realified coefficients required')
    n=100 if differentiate else 0
    x=[Jet.affine(a,np.eye(n)[j])if differentiate else Jet.constant(a,0)for j,a in enumerate(raw)]
    q,v,m=x[:37],x[37:74],x[74:98];s,rate=x[98:]
    sk=(-1.)**np.arange(1,13);sj=(-1.)**np.arange(12)
    Cstar=RADIUS0*(q[0]+sum((a*b for a,b in zip(q[1:13],sk)),Jet.constant(0.,n))+sum((a*b for a,b in zip(q[13:25],sj)),Jet.constant(0.,n))).exp()
    lc=v[0]+sum((a*b for a,b in zip(v[1:13],sk)),Jet.constant(0.,n))+sum((a*b for a,b in zip(v[13:25],sj)),Jet.constant(0.,n))
    delta=s/Cstar;dr=(rate-lc*s)/Cstar
    return q,v,m,delta,dr,np.pi/4+delta,Cstar


def _response(chi,delta,dr,chart):
    a=[_compose(delta,chart['coefficients'][j],*chart['derivatives'][j,:2])for j in range(2)]
    ap=[_compose(delta,*chart['derivatives'][j])for j in range(2)]
    f=chi+a[0]*_sin(2*chi)+a[1]*_sin(6*chi)
    fp=1+2*a[0]*_cos(2*chi)+6*a[1]*_cos(6*chi)
    ft=dr*(ap[0]*_sin(2*chi)+ap[1]*_sin(6*chi))
    x,w=_rule(chart['points']);c=chi.value*x;basis=np.array([np.sin(2*c),np.sin(6*c)])
    av=chart['coefficients'];dv=chart['derivatives'][:,0];ddv=chart['derivatives'][:,1]
    fv=c+av@basis;fd=dv@basis;fdd=ddv@basis
    W=.25*np.sin(2*fv)**2;Wf=.5*np.sin(4*fv);Wff=2*np.cos(4*fv)
    N=chi.value*(w@W);Nd=chi.value*(w@(Wf*fd));Ndd=chi.value*(w@(Wff*fd*fd+Wf*fdd))
    Z=chart['normalization'];Zd,Zdd=chart['normalization_derivatives'][:2]
    wb=np.array([np.sin(2*chi.value),np.sin(6*chi.value)]);fw=chi.value+av@wb;fdw=dv@wb
    fc=1+2*av[0]*np.cos(2*chi.value)+6*av[1]*np.cos(6*chi.value)
    Ww=.25*np.sin(2*fw)**2;Wfw=.5*np.sin(4*fw)
    if delta.value==0:Z=np.pi/16
    probability=N/Z;first=np.array([Nd/Z-N*Zd/Z**2,Ww/Z])
    second=np.array([[Ndd/Z-2*Nd*Zd/Z**2-N*Zdd/Z**2+2*N*Zd*Zd/Z**3,Wfw*fdw/Z-Ww*Zd/Z**2],
        [Wfw*fdw/Z-Ww*Zd/Z**2,Wfw*fc/Z]])
    J=np.array([delta.gradient,chi.gradient]);p=Jet(probability,first@J,J.T@second@J+first[0]*delta.hessian+first[1]*chi.hessian)
    return dict(f=f,fprime=fp,fdot=ft,sigma=p-.5,localization_weight=4*p*(1-p))


def holomorphic_geometry_rows(raw,rho,*,differentiate=True,connection_only=False,response_points=96):
    q,v,m,delta,dr,wall,Cstar=_geometry_variables(raw,differentiate=differentiate);n=len(delta.gradient)
    chart=None if connection_only else anchored_holomorphic_chart(delta.value,points=response_points)
    jac=2*wall/WALL;rows=[]
    for rr in np.asarray(rho,float):
        chi=(float(rr)/WALL)*wall;f=_fields(12,q,v,m,chi);LF=_sqrt(f['A']**2+f['B']**2)
        lam=f['A']**2/LF**2;lr=lam*(1-lam)*(f['ap']-f['bp']);lt=2*lam*(1-lam)*(f['la']-f['lb']);adv=(2*float(rr)/WALL)*dr
        row=dict(connection_lambda=lam,lambda_tau=lt+adv*lr,lambda_rho=jac*lr)
        if not connection_only:
            r=_response(chi,delta,dr,chart);R=f['A']*f['B']/LF;Crho=f['C']/2
            common=2*np.pi**4*LF**5*r['localization_weight'];lapse=f['N']
            row.update(electric=jac*common*Crho*R/lapse,electric_radial=common*R**3/(lapse*Crho*jac),
                radial=common*lapse*R/(Crho*jac),angular=jac*common*lapse*Crho/R,shift=(2*f['beta']+adv)/jac)
        rows.append(row)
    return dict(rows=rows,coordinate_count=n,response_chart=chart)


def holomorphic_cap_and_weights(raw,*,points=48,response_points=96):
    q,v,m,delta,dr,wall,Cstar=_geometry_variables(raw);n=100
    chart=anchored_holomorphic_chart(delta.value,points=response_points);nodes,weights=_rule(points)
    bulk=Jet.constant(0.,n);inertia=Jet.constant(0.,n)
    for y,weight in zip(nodes,weights):
        chi=wall*y;F=_fields(12,q,v,m,chi);r=_response(chi,delta,dr,chart)
        C,A,B,N=(F[k]for k in('C','A','B','N'))
        Hc=(F['lc']-F['beta']*F['cp']-F['betap'])/N;Ha=(F['la']-F['beta']*F['ap'])/N;Hb=(F['lb']-F['beta']*F['bp'])/N
        adm=Hc*Hc+3*Ha*Ha+3*Hb*Hb-(Hc+3*Ha+3*Hb)**2
        fn=(r['fdot']-F['beta']*r['fprime'])/N
        X=r['fprime']**2/C**2+3*_cos(r['f'])**2/A**2+3*_sin(r['f'])**2/B**2-fn*fn
        loc=r['localization_weight'];volume=C*A**3*B**3;spatial=A**3*B**3
        grav=3*spatial/C*N*(F['np']*(F['ap']+F['bp'])+F['ap']**2+F['bp']**2+3*F['ap']*F['bp'])
        alg=N*volume*(3/A**2+3/B**2-.5*(15*5**(1/3)/4)-loc*(.5*X+.125*X**4)+.5*adm)
        bulk+=weight*wall*(grav+alg);inertia+=weight*wall*volume*loc*(1+X**3)/N
    FR=-.25/(2*HOPF_ORBIT_VOLUME**2*inertia)
    F=_fields(12,q,v,m,wall);A,B,N=(F[k]for k in('A','B','N'));R=A*B/_sqrt(A*A+B*B)
    casimir=-standard_model_casimir_coefficient()/R*N;U=F['C']*(dr+F['beta'])/N
    theta=_atanh(U);rho=A**3*B**3;rho_rate=3*rho*(F['la']+F['lb']+(F['ap']+F['bp'])*dr)
    boundary=-theta*rho_rate;area=-N*rho*_sqrt(1-U*U);lapse=N*_sqrt(1-U*U)
    return dict(total=bulk+FR+casimir+boundary,surface_per_gamma=area,FR_denominator=inertia,
        wT=R**3/lapse,wS=lapse*R,wV=lapse*R**3,R4=R,N=lapse,chart=chart)

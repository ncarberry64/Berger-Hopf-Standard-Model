"""Literal arbitrary-precision first gradient of the child constitutive action.

All146 original v/y variables are differentiated independently. Geometry
positions and inherited connection germs are fixed inputs to this local
application. There is no conjugation, velocity-chart force substitution,
coefficient fitting or physical-stop selection. The finite quadrature and
stored inherited/profile constants retain their upstream production scope.
"""
from __future__ import annotations
import numpy as np
import mpmath as mp
from .muon_holomorphic_child_action import _affine_geometry,_parameters
from .muon_holomorphic_normal_geometry import _geometry_variables,anchored_holomorphic_chart
from .muon_exact_material_response import _rule
from .muon_parent_retarded_hypercharge import WALL
from .muon_parent_maxwell_full_weak import M
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP,VOLUME
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0,HOPF_ORBIT_VOLUME
from .aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_birth_trace_enriched_action import generic_coordinate_lift


def _number(z):
    if isinstance(z,(mp.mpf,mp.mpc)):return z
    z=complex(z);return mp.mpc(mp.mpf(z.real),mp.mpf(z.imag))


class First:
    """Sparse first-order analytic dual with arbitrary-precision scalars."""
    def __init__(self,value,gradient=None):
        self.value=value if isinstance(value,(mp.mpf,mp.mpc))else _number(value)
        self.gradient={}if gradient is None else {i:v for i,v in gradient.items()if v!=0}
    def __add__(self,o):
        o=o if isinstance(o,First)else First(o);g=self.gradient.copy()
        for i,v in o.gradient.items():g[i]=g.get(i,0)+v
        return First(self.value+o.value,g)
    __radd__=__add__
    def __neg__(self):return First(-self.value,{i:-v for i,v in self.gradient.items()})
    def __sub__(self,o):return self+(-o if isinstance(o,First)else -_number(o))
    def __rsub__(self,o):return -self+o
    def __mul__(self,o):
        o=o if isinstance(o,First)else First(o);g={i:v*o.value for i,v in self.gradient.items()}
        for i,v in o.gradient.items():g[i]=g.get(i,0)+v*self.value
        return First(self.value*o.value,g)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=o if isinstance(o,First)else First(o)
        return self*First(1/o.value,{i:-v/o.value**2 for i,v in o.gradient.items()})
    def __rtruediv__(self,o):return First(o)/self
    def __pow__(self,p):
        if not isinstance(p,int):raise TypeError('literal integer action powers required')
        return First(self.value**p,{i:p*self.value**(p-1)*v for i,v in self.gradient.items()})if p else First(1)
    def exp(self):return _unary(self,mp.exp,mp.exp)


def _unary(x,fun,derivative):
    x=x if isinstance(x,First)else First(x)
    return First(fun(x.value),{i:derivative(x.value)*v for i,v in x.gradient.items()})
def _sin(x):return _unary(x,mp.sin,mp.cos)
def _cos(x):return _unary(x,mp.cos,lambda z:-mp.sin(z))
def _sqrt(x):
    x=x if isinstance(x,First)else First(x);r=mp.sqrt(x.value)
    if r.real<=0:raise ValueError('same principal local metric branch required')
    return First(r,{i:v/(2*r)for i,v in x.gradient.items()})
def _atanh(x):
    if abs(x.value)>=1:raise ValueError('same local holomorphic wall-velocity chart required')
    return _unary(x,mp.atanh,lambda z:1/(1-z*z))
def _dot(a,b):return sum((x*y for x,y in zip(a,b)),First(0))


def _fields(q,v,m,chi):
    ck=[_cos(4*j*chi)for j in range(1,13)];cj=[_cos(4*j*chi)for j in range(12)]
    sk=[_sin(4*j*chi)for j in range(1,13)];sj=[_sin(4*j*chi)for j in range(12)]
    window=_sin(2*chi)**2;wp=2*_sin(4*chi)
    u=_dot(q[1:13],ck);w=window*_dot(q[13:25],cj);b=window*_dot(q[25:37],cj)
    up=_dot(q[1:13],[-4*j*x for j,x in zip(range(1,13),sk)])
    wpc=[wp*x-4*j*window*y for j,x,y in zip(range(12),cj,sj)]
    cp=up+_dot(q[13:25],wpc);bp=_dot(q[25:37],wpc)
    ap=up+bp-_sin(chi)/_cos(chi);br=up-bp+_cos(chi)/_sin(chi)
    radius=RADIUS0*q[0].exp();C=radius*(u+w).exp();A=radius*(u+b).exp()*_cos(chi);B=radius*(u-b).exp()*_sin(chi)
    N=_dot(m[:12],ck).exp();np_=_dot(m[:12],[-4*j*x for j,x in zip(range(1,13),sk)])
    beta=_sin(4*chi)*_dot(m[12:],cj)
    betap=4*_cos(4*chi)*_dot(m[12:],cj)+_sin(4*chi)*_dot(m[12:],[-4*j*x for j,x in zip(range(12),sj)])
    udot=_dot(v[1:13],ck);wdot=window*_dot(v[13:25],cj);bdot=window*_dot(v[25:37],cj)
    return dict(C=C,A=A,B=B,N=N,cp=cp,ap=ap,bp=br,np=np_,beta=beta,betap=betap,
        lc=v[0]+udot+wdot,la=v[0]+udot+bdot,lb=v[0]+udot-bdot)


def _response(chi,dr,chart):
    a=[First(_number(z))for z in chart['coefficients']];ap=[First(_number(z))for z in chart['derivatives'][:,0]]
    f=chi+a[0]*_sin(2*chi)+a[1]*_sin(6*chi)
    fp=1+2*a[0]*_cos(2*chi)+6*a[1]*_cos(6*chi)
    ft=dr*(ap[0]*_sin(2*chi)+ap[1]*_sin(6*chi))
    x,w=_rule(chart['points']);integral=First(0)
    for t,weight in zip(x,w):
        c=chi*float(t);ff=c+a[0]*_sin(2*c)+a[1]*_sin(6*c)
        integral+=float(weight)*_sin(2*ff)**2/4
    probability=chi*integral/_number(chart['normalization'])
    return dict(f=f,fprime=fp,fdot=ft,localization_weight=4*probability*(1-probability))


def _ad(a,b):
    # SAME retained su(2) real structure; hypercharge component commutes.
    c=First(1/np.sqrt(2))
    return [c*(a[1]*b[2]-a[2]*b[1]),c*(a[2]*b[0]-a[0]*b[2]),c*(a[0]*b[1]-a[1]*b[0]),First(0)]
def _add(a,b):return[x+y for x,y in zip(a,b)]
def _sub(a,b):return[x-y for x,y in zip(a,b)]
def _maxwell(A,At,Ar,e,r,d,k,beta):
    X=_add(_sub(At[1],Ar[0]),_ad(A[0],A[1]))
    T=[_add(At[2+i],_ad(A[0],A[2+i]))for i in range(3)]
    R=[_add(Ar[2+i],_ad(A[1],A[2+i]))for i in range(3)]
    B=[_add([2*x for x in A[2+i]],_ad(A[2+(i+1)%3],A[2+(i+2)%3]))for i in range(3)]
    Y=[_sub(t,[beta*x for x in rr])for t,rr in zip(T,R)]
    return (k*_dot(X,X)+e*sum((_dot(y,y)for y in Y),First(0))-r*sum((_dot(y,y)for y in R),First(0))-d*sum((_dot(y,y)for y in B),First(0)))/2


def high_precision_original_constitutive_gradient(raw_child,time,initial_pair,reference_pair,rep,*,
        nu_squared_action,surface_gamma=None,decimal_precision=60):
    """Evaluate the original146 signed action derivatives in mpmath."""
    raw=np.asarray(raw_child,complex);coordinates=generic_coordinate_lift(rep['gauge_labels']);P=coordinates['lift'];n=106
    if raw.shape!=(268,)or rep['gauge_count']!=80 or not np.isfinite(raw).all():raise ValueError('all original complexified real raw268 fields required')
    if decimal_precision<40:raise ValueError('at least40 decimal digits required')
    # Same fixed positional response and inherited clock coefficients;
    # their binary production error is explicitly outside this application.
    geo=_geometry_variables(raw[:100],differentiate=False);chart=anchored_holomorphic_chart(geo[3].value)
    p=_affine_geometry(initial_pair[0],time);rp,rc=(_affine_geometry(x,time)for x in reference_pair)
    eff=_parameters(p,rep['rho'])-_parameters(rp,rep['rho'])+_parameters(rc,rep['rho'])
    effwall=(_parameters(p,[WALL])-_parameters(rp,[WALL])+_parameters(rc,[WALL]))[0]
    with mp.workdps(decimal_precision):
        x=[First(_number(value),{j:mp.mpc(coefficient)for j,coefficient in enumerate(P[i,n:])if coefficient})for i,value in enumerate(raw)]
        q,v,m=x[:37],x[37:74],x[74:98];s,rate=x[98:100]
        ell=np.r_[1.,(-1.)**np.arange(1,13),(-1.)**np.arange(12),np.zeros(12)]
        Cstar=RADIUS0*_dot(q,ell).exp();lc=_dot(v,ell);delta=s/Cstar;dr=(rate-lc*s)/Cstar;wall=First(np.pi/4)+delta
        nodes,quad=_rule(rep['cap_points']);bulk=First(0);inertia=First(0)
        for t,weight in zip(nodes,quad):
            chi=wall*float(t);F=_fields(q,v,m,chi);res=_response(chi,dr,chart)
            C,A,B,N=(F[key]for key in('C','A','B','N'))
            Hc=(F['lc']-F['beta']*F['cp']-F['betap'])/N;Ha=(F['la']-F['beta']*F['ap'])/N;Hb=(F['lb']-F['beta']*F['bp'])/N
            adm=Hc**2+3*Ha**2+3*Hb**2-(Hc+3*Ha+3*Hb)**2
            fn=(res['fdot']-F['beta']*res['fprime'])/N
            X=res['fprime']**2/C**2+3*_cos(res['f'])**2/A**2+3*_sin(res['f'])**2/B**2-fn**2
            loc=res['localization_weight'];volume=C*A**3*B**3;spatial=A**3*B**3
            grav=3*spatial/C*N*(F['np']*(F['ap']+F['bp'])+F['ap']**2+F['bp']**2+3*F['ap']*F['bp'])
            alg=N*volume*(3/A**2+3/B**2-.5*(15*5**(1/3)/4)-loc*(X/2+X**4/8)+adm/2)
            bulk+=float(weight)*wall*(grav+alg);inertia+=float(weight)*wall*volume*loc*(1+X**3)/N
        FR=-.25/(2*HOPF_ORBIT_VOLUME**2*inertia)
        F=_fields(q,v,m,wall);A,B,N=(F[key]for key in('A','B','N'));R=A*B/_sqrt(A**2+B**2)
        U=F['C']*(dr+F['beta'])/N;rho=A**3*B**3;theta=_atanh(U)
        boundary=-theta*3*rho*(F['la']+F['lb']+(F['ap']+F['bp'])*dr)
        total=bulk+FR-standard_model_casimir_coefficient()/R*N+boundary
        induced=N*_sqrt(1-U**2)
        if surface_gamma is not None:total-=surface_gamma*N*rho*_sqrt(1-U**2)
        jac=2*wall/WALL;gb=np.asarray(rep['gauge_basis'])[:,:,0];gr=np.asarray(rep['gauge_radial_basis'])[:,:,0]
        for j,(rr,weight)in enumerate(zip(rep['rho'],rep['radial_quadrature'])):
            chi=wall*(float(rr)/WALL);F=_fields(q,v,m,chi);res=_response(chi,dr,chart)
            LF=_sqrt(F['A']**2+F['B']**2);rad=F['A']*F['B']/LF;Cr=F['C']/2
            common=float(2*np.pi**4)*LF**5*res['localization_weight'];NN=F['N']
            e=jac*common*Cr*rad/NN;k=common*rad**3/(NN*Cr*jac);r=common*NN*rad/(Cr*jac);d=jac*common*NN*Cr/rad
            adv=(2*float(rr)/WALL)*dr;beta=(2*F['beta']+adv)/jac
            lam=F['A']**2/LF**2;lr=lam*(1-lam)*(F['ap']-F['bp']);lt=2*lam*(1-lam)*(F['la']-F['lb'])+adv*lr;lrho=jac*lr
            AA=[[sum((float(gb[j,h,f,c])*x[100+h]for h in range(80)),First(0))for c in range(4)]for f in range(5)]
            TT=[[sum((float(gb[j,h,f,c])*x[180+h]for h in range(80)),First(0))for c in range(4)]for f in range(5)]
            RR=[[sum((float(gr[j,h,f,c])*x[100+h]for h in range(80)),First(0))for c in range(4)]for f in range(5)]
            for i in range(3):
                for c in range(4):
                    AA[2+i][c]+=M[i,c]*(eff[j,0]-1);TT[2+i][c]+=M[i,c]*eff[j,1];RR[2+i][c]+=M[i,c]*eff[j,2]
            baseline=(e*(lt-beta*lrho)**2-r*lrho**2-d*(2*(lam-1)*lam)**2)*float(np.sum(M*M))/2
            total+=MAXWELL_TO_CAP*float(weight)*(_maxwell(AA,TT,RR,e,r,d,k,beta)-baseline)
        wallA=[[sum((float(rep['wall_trace_map'][f,c,h])*x[100+h]for h in range(80)),First(0))for c in range(4)]for f in range(5)]
        for i in range(3):
            for c in range(4):wallA[2+i][c]+=M[i,c]*(effwall[0]-1)
        generators=higgs_u2_real_representation()['real_generators'];H=x[260:264];Hdot=x[264:268]
        DH=[]
        for f in(0,2,3,4):
            oo=[[sum((float(generators[c,i,h])*wallA[f][c]for c in range(4)),First(0))for h in range(4)]for i in range(4)]
            dh=[_dot(row,H)for row in oo];DH.append(_add(dh,Hdot)if f==0 else dh)
        wt=R**3/induced;ws=induced*R;wv=induced*R**3;gap=_dot(H,H)-nu_squared_action
        total+=(wt*_dot(DH[0],DH[0])-ws*sum((_dot(z,z)for z in DH[1:]),First(0))-wv*rep['scalar_matching']['lambda_H']*gap**2)/VOLUME
        gradient=np.array([complex(total.gradient.get(i,mp.mpc(0)))for i in range(146)])
        strings=np.array([[mp.nstr(total.gradient.get(i,mp.mpc(0)).real,decimal_precision),mp.nstr(total.gradient.get(i,mp.mpc(0)).imag,decimal_precision)]for i in range(146)])
        return dict(value=complex(total.value),constitutive_gradient=gradient,gradient_decimal_strings=strings,
            decimal_precision=decimal_precision,material_rate=complex(dr.value),wall_velocity=complex(U.value),
            original_raw_variables_differentiated=True,analytic_source_dual_conjugated=False,
            positional_response_and_inherited_coefficients_scope='same binary-produced fixed-position chart/germs; no upstream coefficient or continuum enclosure',
            complete_action_Hessian_or_original_x_force_replaced=False)

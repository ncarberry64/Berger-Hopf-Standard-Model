"""Uncontracted Levi-Civita Spin connection on the owned RIGHT-Maurer M5 coframe.

This is the geometric connection of e0=N dt, e4=C(drho+z dt), ea=R theta^a.
It is distinct from intrinsic-wall LC, the f_eta zero-order contact, U2
parallel transport, and a choice of physical initial Spin/reset lift.
"""
from __future__ import annotations
import numpy as np

PRIMITIVES=('N','C','z','R','N_rho','C_time','C_rho','z_rho','R_time','R_rho')
FRAME_ORDER=('0','4','1','2','3')

def epsilon():
    e=np.zeros((3,3,3))
    for i in range(3):e[i,(i+1)%3,(i+2)%3]=1;e[i,(i+2)%3,(i+1)%3]=-1
    return e

def _contacts(p,dp):
    N,C,z,R,Nr,Ct,Cr,zr,Rt,Rr=p
    dN,dC,dz,dR,dNr,dCt,dCr,dzr,dRt,dRr=dp
    a=Nr/(N*C);k=(Ct-z*Cr-C*zr)/(N*C)
    H0=(Rt-z*Rr)/(N*R);H4=Rr/(C*R)
    da=dNr/(N*C)-a*(dN/N+dC/C)
    dk=(dCt-dz*Cr-z*dCr-dC*zr-C*dzr)/(N*C)-k*(dN/N+dC/C)
    dH0=(dRt-dz*Rr-z*dRr)/(N*R)-H0*(dN/N+dR/R)
    dH4=dRr/(C*R)-H4*(dC/C+dR/R)
    return np.array([a,k,H0,H4,1/R]),np.array([da,dk,dH0,dH4,-dR/R**2])

def m5_geometric_spin_connection(primitive_value_first,*,gamma,orientation):
    """Value and one explicit REAL source first of all connection one-forms.

    Rows are value/source-first, columns PRIMITIVES. gamma has FRAME_ORDER.
    orientation=eps uses e4_eps=eps*C(drho+zdt), the original D5 sheet sign.
    LOWER Lorentz connection convention is de^A+omega^A_B wedge e^B=0,
    Spin Omega=(1/4)sum_(A,B)omega_AB Gamma^A Gamma^B (FULL ordered sum).
    No missing E/B source, trajectory variation, or initial lift is inferred.
    """
    p=np.asarray(primitive_value_first)
    if (p.shape!=(2,10)or not np.isfinite(p).all()or
        (np.iscomplexobj(p)and np.any(p.imag!=0))):
        raise ValueError('Explicit real primitive value/source-first2x10 required')
    p=np.asarray(p.real,float)
    if min(p[0,0],p[0,1],p[0,3])<=0 or orientation not in(-1,1):
        raise ValueError('Positive real N,C,R and original sheet orientation required')
    G=np.asarray(gamma,complex)
    if G.ndim!=3 or G.shape[0]!=5 or G.shape[1]!=G.shape[2]or not np.isfinite(G).all():
        raise ValueError('Complete existing5D gamma set in0,4,1,2,3 order required')
    eta=np.diag([1.,-1.,-1.,-1.,-1.]);d=G.shape[-1]
    if max(np.max(abs(G[a]@G[b]+G[b]@G[a]-2*eta[a,b]*np.eye(d)))for a in range(5)for b in range(5))>1e-11:
        raise ValueError('OwnedCl(1,4) gamma algebra required')
    contacts=np.array(_contacts(*p));w=np.zeros((2,5,5,5));e=epsilon();eps=orientation
    for s,(a,k,H0,H4,invR)in enumerate(contacts):
        w[s,0,1,0]=eps*a;w[s,0,1,1]=k
        for i in range(3):
            w[s,0,i+2,i+2]=H0;w[s,1,i+2,i+2]=eps*H4
            for j in range(3):
                for l in range(3):w[s,i+2,j+2,l+2]=-invR*e[i,j,l]
        for a in range(5):
            for b in range(a+1,5):w[s,b,a]=-w[s,a,b]
    N,C,z,R=p[0,:4];dN,dC,dz,dR=p[1,:4]
    frame=np.zeros((2,5,5));frame[0]=np.diag([N,eps*C,R,R,R])
    frame[0,1,0]=eps*C*z;frame[1]=np.diag([dN,eps*dC,dR,dR,dR])
    frame[1,1,0]=eps*(dC*z+C*dz)
    pairs=np.einsum('aij,bjk->abik',G,G)
    spin_frame=.25*np.einsum('sabc,abij->scij',w,pairs)
    coordinate=np.array([np.einsum('abc,cm->abm',w[0],frame[0]),
        np.einsum('abc,cm->abm',w[1],frame[0])+np.einsum('abc,cm->abm',w[0],frame[1])])
    spin_coordinate=.25*np.einsum('sabm,abij->smij',coordinate,pairs)
    wall_covector=[]
    for delta in np.eye(10):
        c,dc=_contacts(p[0],delta);a,k=c[:2];da,dk=dc[:2]
        wall_covector.append(delta[4]/C-p[0,4]*delta[1]/C**2
            +(delta[1]*z+C*delta[2])*k+C*z*dk)
    wall_covector=np.array(wall_covector)
    wall_scalar=np.array([coordinate[0,0,1,0]/eps,coordinate[1,0,1,0]/eps])
    return dict(primitive_order=PRIMITIVES,frame_order=FRAME_ORDER,orientation=eps,
        scalar_contacts=contacts,coframe_value_first=frame,
        lower_connection_frame_value_first=w,
        lower_connection_coordinate_value_first=coordinate,
        Spin_connection_frame_value_first=spin_frame,
        Spin_connection_coordinate_value_first=spin_coordinate,
        wall_boost_connection_scalar_value_first=wall_scalar,
        wall_boost_connection_primitive_covector=wall_covector,
        original_Dirac_geometric_body_value_first=1j*np.einsum('aij,sajk->sik',G,spin_frame),
        initial_physical_Spin_lift=None,physical_E_B_source_evaluated=False,
        eta_zero_order_contact_included=False,internal_gauge_or_statistics_selected=False)

def independent_coordinate_tetrad_connection(primitive_value,*,N_time,z_time,orientation):
    """Independent metric-Christoffel check at the SU2 quaternion-chart origin.

    theta^a=dx^a+epsilon_abc*x^b dx^c+O(x^2) is RIGHT Maurer.
    Thus the local round metric has zero angular first derivatives while
    the coframe does not. All5 coordinate derivatives are retained.
    """
    p=np.asarray(primitive_value,float)
    if p.shape!=(10,)or not np.isfinite(np.r_[p,N_time,z_time]).all()or orientation not in(-1,1):
        raise ValueError('Complete finite real local metric first germ required')
    N,C,z,R,Nr,Ct,Cr,zr,Rt,Rr=p;eps=orientation
    if min(N,C,R)<=0:raise ValueError('Positive coframe required')
    coframe=np.diag([N,eps*C,R,R,R]);coframe[1,0]=eps*C*z
    derivative=np.zeros((5,5,5));e=epsilon()
    derivative[0,0,0]=N_time;derivative[1,0,0]=Nr
    derivative[0,1,0]=eps*(Ct*z+C*z_time);derivative[0,1,1]=eps*Ct
    derivative[1,1,0]=eps*(Cr*z+C*zr);derivative[1,1,1]=eps*Cr
    for i in range(3):
        derivative[0,i+2,i+2]=Rt;derivative[1,i+2,i+2]=Rr
        for j in range(3):
            for k in range(3):derivative[j+2,i+2,k+2]=R*e[i,j,k]
    eta=np.diag([1.,-1.,-1.,-1.,-1.]);metric=coframe.T@eta@coframe
    dg=np.array([a.T@eta@coframe+coframe.T@eta@a for a in derivative])
    Christoffel=np.zeros((5,5,5))
    for mu in range(5):
        for nu in range(5):
            Christoffel[:,mu,nu]=np.linalg.solve(metric,
                .5*np.array([dg[mu,s,nu]+dg[nu,s,mu]-dg[s,mu,nu]for s in range(5)]))
    inverse=np.linalg.inv(coframe)
    upper=np.array([(coframe@Christoffel[:,mu,:]-derivative[mu])@inverse for mu in range(5)])
    lower=np.einsum('ab,mbc->acm',eta,upper)
    tetrad=np.array([derivative[mu]-coframe@Christoffel[:,mu,:]+upper[mu]@coframe for mu in range(5)])
    return dict(lower_connection_coordinate=lower,Christoffel=Christoffel,
        metric=metric,metric_derivatives=dg,coframe_derivatives=derivative,
        tetrad_postulate_rows=tetrad,lower_connection_antisymmetry_rows=lower+lower.swapaxes(0,1))

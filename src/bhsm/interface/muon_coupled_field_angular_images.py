"""Exact angular image enlargement of the changing joint field point form.

The same radial/time functions and dependent DG scalar image are retained
on either complete angular parity. No even field is replaced by a scalar
subblock and no Lorenz term is silently added at a single point.
"""
from __future__ import annotations
import numpy as np
from .muon_magnetic_mixed_green import _finite,_positive
from .muon_parent_positive_brst_ghost import _linear_curvature
from .muon_parent_positive_gauge_form import _weighted_curvature_maps,positive_curvature_contact_matrix
from .muon_parent_maxwell_corrected_retarded import _ad,constant_angular_curvatures,higgs_u2_real_representation
from .muon_coupled_higgs_magnetic_source import coupled_intrinsic_wall_images,VOLUME


def one_form_angular_point(connection,connection_time,connection_radial,derivatives,
        radial,metric,densities,temporal):
    """The owned full one-form point form for any complete angular block."""
    A,At,Ar,E,r,g,d,t=[_finite(x,n,real=True)for x,n in zip((connection,connection_time,connection_radial,derivatives,radial,metric,densities,temporal),
        ('actual A','actual A time','actual A radial','complete E','same radial functions','actual positive metric','actual two-form density','same temporal functions'))]
    if (A.shape!=(5,4)or At.shape!=A.shape or Ar.shape!=A.shape or E.ndim!=3 or E.shape[0]!=3 or E.shape[1]!=E.shape[2]
        or r.shape!=(2,3)or g.shape!=(6,)or d.shape!=(5,)or t.shape!=(6,)or min(g[:4])<=0 or min(d[:4])<=0):
        raise ValueError('complete actual positive point images required')
    n=E.shape[1];m=56*n;I=np.eye(20*n).reshape(5,4*n,20*n)
    Ef=np.array([np.kron(np.eye(4),e)for e in E])
    V=np.concatenate([p[0]*I for p in r],axis=2);Vr=np.concatenate([p[1]*I for p in r],axis=2)
    Va=np.einsum('phk,fkA->pfhA',Ef,V);z=np.zeros_like(V)
    convert=lambda x:x.reshape(x.shape[:-1]+(n,40*n))
    c0=_linear_curvature(A,V.reshape(5,4,-1),z.reshape(5,4,-1),Vr.reshape(5,4,-1),Va.reshape(3,5,4,-1))
    c1=_linear_curvature(A,z.reshape(5,4,-1),V.reshape(5,4,-1),z.reshape(5,4,-1),np.zeros_like(Va).reshape(3,5,4,-1))
    c0,c1=[_weighted_curvature_maps(tuple(convert(x)for x in c),d)for c in (c0,c1)]
    F=constant_angular_curvatures(A,At,Ar);D=np.array([np.kron(_ad(a),np.eye(n))for a in A]);D[2:]+=Ef
    G=[];R=[];CG=[];eta=[]
    for p in r:
        gv=p[0]*D;gv[1]+=p[1]*np.eye(4*n);rv=np.zeros_like(gv);rv[0]=p[0]*np.eye(4*n)
        G.append(gv.reshape(20*n,4*n));R.append(rv.reshape(20*n,4*n));eta.append(p[0]*np.eye(4*n))
        fc=tuple(p[0]*np.kron(_ad(a),np.eye(n))for a in (F['Ftr'],*F['Ft'],*F['Fr'],*F['B']))
        CG.append(_weighted_curvature_maps((fc[0],np.array(fc[1:4]),np.array(fc[4:7]),np.array(fc[7:10])),d))
    G,R,CG,eta=[np.concatenate(a,axis=1)for a in (G,R,CG,eta)]
    value=np.zeros((20*n,m));curv=np.zeros((40*n,m));etas=np.zeros((4*n,16*n))
    value[:,:40*n]=t[0]*V.reshape(20*n,40*n);curv[:,:40*n]=t[0]*c0+t[1]*c1
    for i in range(2):
        k=2+2*i;s=slice(40*n+8*n*i,48*n+8*n*i)
        value[:,s]=t[k]*G+t[k+1]*R;curv[:,s]=t[k]*CG
        etas[:,8*n*i:8*n*(i+1)]=t[k]*eta
    C=positive_curvature_contact_matrix(F,d,n);contact=value.T@C@value
    mu,gt,gr,gs,beta,_=g;one=np.diag([gt,gr+beta*beta*gt,gs,gs,gs]);one[0,1]=one[1,0]=-beta*gt
    Gram=value.T@np.kron(one,np.eye(4*n))@value
    return dict(Hessian=curv.T@curv+contact,Gram=Gram,curvature_contact=contact,
        ghost_Gram=mu*(etas.T@etas),value_map=value,curvature_map=curv,
        point_harmonic_count=n,point_field_count=m,curvature=F)


def intrinsic_coupled_angular_point(weights,H,Hdot,connection,derivatives,temporal,wall_radial,*,lambda_H,nu_squared_action):
    """Same coupled intrinsic form with independent and paired scalar maps."""
    w=_finite(weights,'actual positive scalar weights',real=True)
    lam=_positive(lambda_H,'owned lambda_H');nu=_positive(nu_squared_action,'explicit nu squared',zero=True)
    if w.shape!=(3,)or min(w)<=0:raise ValueError('actual positive weights required')
    maps=coupled_intrinsic_wall_images(connection,H,Hdot,derivatives,temporal,wall_radial)
    n=maps['harmonic_count'];m=maps['count'];W=maps['gauge'];h=maps['scalar'];K=np.zeros((m,m))
    T=higgs_u2_real_representation()['real_generators']
    for i,mu in enumerate((w[0],w[1],w[1],w[1])):
        f=(0,2,3,4)[i];B=maps['scalar_covariant_first_images'][i]
        base=maps['covariant_H_time']if i==0 else maps['covariant_H_spatial'][i-1]
        C=np.kron(np.einsum('i,cij->cj',base,T),np.eye(n));cross=W[f].T@C@h
        K+=(2*mu/VOLUME)*(B.T@B+cross+cross.T)
    v=maps['H'];P=np.kron(lam*(4*np.outer(v,v)+2*(v@v-nu)*np.eye(4)),np.eye(n))
    K+=(2*w[2]/VOLUME)*(h.T@P@h)
    return dict(Hessian=K,Gram=(2*w[2]/VOLUME)*(h.T@h),maps=maps,
        ghost_pairing_source='existing DG coefficients carry -Teta H and full -Teta_t H-Teta Hdot',
        no_extra_scalar_state_or_Lorenz_mass_selected=True)

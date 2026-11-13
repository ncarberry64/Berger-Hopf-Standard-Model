"""Magnetic variation of the original natural-wall Maxwell/Higgs action.

The source is a complete first-field value/time/radial germ.  The gauge
Hessian is varied before any Gauss or coordinate-frame solve.  These are
analytic-transpose action rows, including the curvature and off-shell DH
contacts; they are not an absolute-square ADM replacement.
"""
from __future__ import annotations
import numpy as np
from .muon_matched_mechanical_source import epsilon
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_literal_euclidean_wall_action import VOLUME


def _ad(a):
    a=np.asarray(a,complex);out=np.zeros((4,4),complex)
    out[:3,:3]=np.einsum('abc,a->cb',epsilon(),a[:3])/np.sqrt(2)
    return out


def _maps(A):
    """Linear curvature maps in value/time/radial and E_0,E_1,E_2,E_3."""
    S=np.eye(20).reshape(5,4,20)
    X=np.zeros((3,4,4,20),complex)
    T=np.zeros((3,4,12,20),complex);R=T.copy();B=T.copy()
    X[0,0]=_ad(A[0])@S[1]-_ad(A[1])@S[0]
    X[1,0]=S[1];X[2,0]=-S[0]
    for i in range(3):
        sl=slice(4*i,4*i+4)
        T[0,0,sl]=_ad(A[0])@S[2+i]-_ad(A[2+i])@S[0]
        R[0,0,sl]=_ad(A[1])@S[2+i]-_ad(A[2+i])@S[1]
        T[0,i+1,sl]=-S[0];R[0,i+1,sl]=-S[1]
        B[0,0,sl]=2*S[2+i]
    T[1,0]=S[2:].reshape(12,20);R[2,0]=S[2:].reshape(12,20)
    for i,j,k in np.argwhere(epsilon()):
        sl=slice(4*i,4*i+4)
        B[0,j+1,sl]+=epsilon()[i,j,k]*S[2+k]
        B[0,0,sl]+=epsilon()[i,j,k]*(_ad(A[2+j])@S[2+k])
    return X,T,R,B


def _curvature_contact(F,density):
    e,r,d,k,beta=density;X,Ft,Fr,B=F
    C=np.zeros((20,20),complex)
    def add(i,j,f):
        z=np.zeros((4,4),complex)
        z[:3,:3]=np.einsum('abc,c->ab',epsilon(),f[:3])/np.sqrt(2)
        C[4*i:4*i+4,4*j:4*j+4]+=z
        C[4*j:4*j+4,4*i:4*i+4]+=z.T
    add(0,1,k*X)
    for i in range(3):
        add(0,2+i,e*(Ft[i]-beta*Fr[i]))
        add(1,2+i,-e*beta*(Ft[i]-beta*Fr[i])-r*Fr[i])
    for i,j,l in np.argwhere(epsilon()):add(2+j,2+l,-.5*d*epsilon()[i,j,l]*B[i])
    return C


def maxwell_magnetic_coefficient_tensors(connection,source,source_time,
                                        source_radial,densities,source_derivatives):
    """Separate the exact two angular placements before the radial lift.

    This is the same derivative as ``maxwell_magnetic_hessian_blocks``.
    Its small coefficient tensors allow every original radial coordinate
    to be integrated without materializing a large point angular matrix.
    """
    A,a,at,ar,c=[np.asarray(x,complex)for x in
        (connection,source,source_time,source_radial,densities)]
    E=np.asarray(source_derivatives,float);ns=a.shape[-1]
    if (A.shape!=(5,4)or a.shape!=(5,4,ns)or at.shape!=a.shape or ar.shape!=a.shape
        or c.shape!=(5,)or E.shape!=(3,ns,ns)
        or any(not np.isfinite(x).all()for x in(A,a,at,ar,c,E))):
        raise ValueError('complete same source curvature germ required')
    e,r,d,k,beta=c;X,T,R,B=_maps(A);zero=_maps(np.zeros((5,4)))
    base=(X,T-beta*R,R,B);weights=(k,e,-r,-d)
    left=np.zeros((3,3,4,20,20,ns),complex);right=left.copy()
    for h in range(ns):
        z=tuple(x-y for x,y in zip(_maps(a[:,:,h]),zero))
        delta=(z[0],z[1]-beta*z[2],z[2],z[3])
        for m,dm,w in zip(base,delta,weights):
            for i in range(3):
                for j in range(3):
                    for p in range(4):
                        left[i,j,p,:,:,h]+=w*dm[i,0].T@m[j,p]
                        right[i,j,p,:,:,h]+=w*m[i,p].T@dm[j,0]
    angular=np.einsum('ikh,fck->ifch',E,a,optimize=True)
    dX=at[1]-ar[0]+_ad(A[0])@a[1]-_ad(A[1])@a[0]
    dT=at[2:]-angular[:,0];dR=ar[2:]-angular[:,1];dB=2*a[2:].copy()
    for i in range(3):
        dT[i]+=_ad(A[0])@a[2+i]-_ad(A[2+i])@a[0]
        dR[i]+=_ad(A[1])@a[2+i]-_ad(A[2+i])@a[1]
    for i,j,l in np.argwhere(epsilon()):
        dB[i]+=epsilon()[i,j,l]*(angular[j,2+l]+_ad(A[2+j])@a[2+l])
    contact=np.array([_curvature_contact((dX[:,h],dT[:,:,h],dR[:,:,h],dB[:,:,h]),c)
                      for h in range(ns)]).transpose(1,2,0)
    return dict(left=left,right=right,contact=contact,
                source_curvature=(dX,dT,dR,dB))


def maxwell_magnetic_hessian_blocks(connection, source, source_time,
        source_radial, densities, even_derivatives, odd_derivatives,
        source_derivatives, gaunt):
    """Literal D3S[source, even field jet, odd field jet].

    The returned blocks[i,j] act on complete field20 times the supplied
    even/odd harmonics, with i,j=value/time/radial.  Both angular derivative
    placements survive.  No Euler, Gauss, curvature or central row is set
    to zero by this application.
    """
    A=np.asarray(connection,complex);a,at,ar=[np.asarray(x,complex)for x in(source,source_time,source_radial)]
    c=np.asarray(densities,complex);Ee,Eo,Es,G=[np.asarray(x,float)for x in(even_derivatives,odd_derivatives,source_derivatives,gaunt)]
    if (A.shape!=(5,4)or a.ndim!=3 or a.shape[:2]!=(5,4)or at.shape!=a.shape or ar.shape!=a.shape
        or c.shape!=(5,)or G.shape!=(Ee.shape[1],Eo.shape[1],a.shape[2])
        or Ee.shape!=(3,Ee.shape[1],Ee.shape[1])or Eo.shape!=(3,Eo.shape[1],Eo.shape[1])
        or Es.shape!=(3,a.shape[2],a.shape[2])or any(not np.isfinite(x).all()for x in(A,a,at,ar,c,Ee,Eo,Es,G))):
        raise ValueError('complete analytic field source germ and even/odd/source Gaunt maps required')
    e,r,d,k,beta=c;nh=a.shape[2];ne,no=G.shape[:2]
    X,T,R,B=_maps(A);Y=T-beta*R
    maps=(X,Y,R,B);weights=(k,e,-r,-d)
    # A maps are affine.  Subtract their constant derivative/frame part
    # exactly before forming the first source variation.
    zero=_maps(np.zeros((5,4)));dm=[]
    for h in range(nh):
        z=tuple(x-y for x,y in zip(_maps(a[:,:,h]),zero))
        dm.append((z[0],z[1]-beta*z[2],z[2],z[3]))
    ep=np.concatenate((np.eye(ne)[None],Ee));op=np.concatenate((np.eye(no)[None],Eo))
    blocks=np.zeros((3,3,20*ne,20*no),complex)
    for h in range(nh):
        for base,delta,w in zip(maps,dm[h],weights):
            # delta maps have only value/E0 dependence.  The source
            # derivative affects delta curvature/contact below.
            for i in range(3):
                for j in range(3):
                    for p in range(4):
                        left=delta[i,0].T@base[j,p]
                        right=base[i,p].T@delta[j,0]
                        if np.any(left):blocks[i,j]+=w*np.kron(left,G[:,:,h]@op[p])
                        if np.any(right):blocks[i,j]+=w*np.kron(right,ep[p].T@G[:,:,h])
    angular=np.einsum('ikh,fck->ifch',Es,a,optimize=True)
    dX=at[1]-ar[0]+_ad(A[0])@a[1]-_ad(A[1])@a[0]
    dT=at[2:]-angular[:,0]
    dR=ar[2:]-angular[:,1]
    dB=2*a[2:].copy()
    for i in range(3):
        dT[i]+=_ad(A[0])@a[2+i]-_ad(A[2+i])@a[0]
        dR[i]+=_ad(A[1])@a[2+i]-_ad(A[2+i])@a[1]
    for i,j,l in np.argwhere(epsilon()):
        dB[i]+=epsilon()[i,j,l]*(angular[j,2+l]+_ad(A[2+j])@a[2+l])
    contacts=np.zeros((20*ne,20*no),complex)
    for h in range(nh):contacts+=np.kron(_curvature_contact((dX[:,h],dT[:,:,h],dR[:,:,h],dB[:,:,h]),c),G[:,:,h])
    blocks[0,0]+=contacts
    return dict(blocks=blocks,curvature_contact=contacts,
        source_curvature=(dX,dT,dR,dB),analytic_transpose_pairing=True,
        all_original_Gauss_rows_retained=True,physical_P_strat_or_Pauli_identified=False)


def intrinsic_magnetic_hessian_block(connection,H,Hdot,source_wall,source_H,
        source_Hdot,metric_weights,even_derivatives,odd_derivatives,
        source_derivatives,gaunt,*,lambda_H,nu_squared_action):
    """Exact mixed source variation of the full intrinsic wall Hessian.

    Order remains H4, wallA20, Hdot4, each tensor the complete angular
    representation.  The source Hdot enters off-shell DH contacts; it is
    neither fitted independently nor discarded in a mass-only reduction.
    """
    A,h,hd,a,z,zd=[np.asarray(x,complex)for x in(connection,H,Hdot,source_wall,source_H,source_Hdot)]
    w=np.asarray(metric_weights,complex);Ee,Eo,Es,G=[np.asarray(x,float)for x in(even_derivatives,odd_derivatives,source_derivatives,gaunt)]
    lam=float(lambda_H);nu=float(nu_squared_action);ne,no,ns=G.shape
    if (A.shape!=(5,4)or h.shape!=(4,)or hd.shape!=(4,)or a.shape!=(5,4,ns)or z.shape!=(4,ns)or zd.shape!=z.shape
        or w.shape!=(3,)or Ee.shape!=(3,ne,ne)or Eo.shape!=(3,no,no)or Es.shape!=(3,ns,ns)
        or lam<=0 or nu<0 or any(not np.isfinite(x).all()for x in(A,h,hd,a,z,zd,w,Ee,Eo,Es,G))):
        raise ValueError('complete intrinsic H/gauge source germ and action parameters required')
    T=higgs_u2_real_representation()['real_generators'];O=np.einsum('fc,cij->fij',A,T)
    U=np.einsum('cij,j->ic',T,h);dU=np.einsum('cij,jh->ich',T,z)
    dO=np.einsum('fch,cij->fijh',a,T)
    result=np.zeros((28*ne,28*no),complex);contacts=result.copy()
    def maps(n,E):
        I=np.eye(n);vh=np.zeros((4*n,28*n),complex);vh[:,:4*n]=np.eye(4*n)
        vg=np.zeros((5,4*n,28*n),complex)
        for f in range(5):vg[f,:,4*n+f*4*n:4*n+(f+1)*4*n]=np.eye(4*n)
        vt=np.zeros_like(vh);vt[:,24*n:]=np.eye(4*n)
        cov=[vt+np.kron(O[0],I)@vh+np.kron(U,I)@vg[0]]
        cov.extend(np.kron(np.eye(4),E[i])@vh+np.kron(O[2+i],I)@vh+np.kron(U,I)@vg[2+i]for i in range(3))
        return vh,vg,cov
    he,ge,Ce=maps(ne,Ee);ho,go,Co=maps(no,Eo)
    DH=np.r_[(hd+O[0]@h)[None],np.einsum('fij,j->fi',O[2:],h)]
    dDH=np.r_[(zd+O[0]@z+np.einsum('ijh,j->ih',dO[0],h))[None],
        np.einsum('ikh,jk->ijh',Es,z)+np.einsum('fij,jh->fih',O[2:],z)+np.einsum('fijh,j->fih',dO[2:],h)]
    for j,(f,weight)in enumerate(zip((0,2,3,4),(w[0],-w[1],-w[1],-w[1]))):
        oe=np.einsum('ijh,tmh->itjm',dO[f],G,optimize=True).reshape(4*ne,4*no)
        ue=np.einsum('ich,tmh->itcm',dU,G,optimize=True).reshape(4*ne,4*no)
        # Reverse multiplication is the same action coefficient with the
        # angular Gaunt reversed, not a conjugate of continued fields.
        oo=np.einsum('ijh,mth->imjt',dO[f],G.transpose(1,0,2),optimize=True).reshape(4*no,4*ne)
        uo=np.einsum('ich,mth->imct',dU,G.transpose(1,0,2),optimize=True).reshape(4*no,4*ne)
        de=oe@ho+ue@go[f];do=oo@he+uo@ge[f]
        result+=2*weight/VOLUME*(do.T@Co[j]+Ce[j].T@de)
        X=np.einsum('ih,cij->jch',dDH[j],T)
        xe=np.einsum('ich,tmh->itcm',X,G,optimize=True).reshape(4*ne,4*no)
        xr=np.einsum('ich,mth->imct',X,G.transpose(1,0,2),optimize=True).reshape(4*no,4*ne)
        contacts+=2*weight/VOLUME*(he.T@xe@go[f]+ge[f].T@xr.T@ho)
    dpotential=8*lam*(np.einsum('ih,j->ijh',z,h)+np.einsum('i,jh->ijh',h,z)+np.einsum('h,ij->ijh',h@z,np.eye(4)))
    p=np.einsum('ijh,tmh->itjm',dpotential,G,optimize=True).reshape(4*ne,4*no)
    result-=w[2]/VOLUME*he.T@p@ho
    return dict(hessian=result+contacts,off_shell_DH_contact=contacts,
        actual_source_DH=dDH,analytic_transpose_pairing=True,
        scalar_cap_factor_applied_once=True,physical_Pauli_identified=False)

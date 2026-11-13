"""Literal magnetic first variation of the joint intrinsic Higgs field form.

This constructs the dependent gauge-orbit and independent field images
on both angular parities.  It retains the intrinsic boundary mass,
off-shell DH contact and quartic derivative.  It is an application of the
same coupled action, not a sum of independent field inverses.
"""
from __future__ import annotations
import numpy as np
from .muon_magnetic_mixed_green import _finite,_positive
from .muon_parent_maxwell_corrected_retarded import _ad,higgs_u2_real_representation

VOLUME=2*np.pi**2


def _multiplication(coefficients,gaunt):
    """Exact inherited angular product, preserving every stored coefficient."""
    C=np.asarray(coefficients);G=np.asarray(gaunt)
    return np.einsum('kls,eos->kelo',C,G).reshape(C.shape[0]*G.shape[0],C.shape[1]*G.shape[1])


def coupled_intrinsic_wall_images(connection,H,Hdot,derivatives,temporal,radial):
    """All five gauge, independent scalar and paired DG scalar wall images.

    Order is independent one-form(2 radial profiles), DG(2 temporal by
    2 radial profiles), scalar.  For nh scalar harmonics this has60*nh
    coordinates.  Temporal jet is (b,bprime,g0,g0prime,g1,g1prime).
    """
    A=_finite(connection,'actual total material wall connection',real=True)
    H=_finite(H,'actual real4 Higgs',real=True);Hd=_finite(Hdot,'actual Higgs rate',real=True)
    E=_finite(derivatives,'complete inherited angular derivatives',real=True)
    t=_finite(temporal,'actual common temporal image',real=True)
    r=_finite(radial,'actual common wall radial image',real=True)
    if A.shape!=(5,4) or H.shape!=(4,) or Hd.shape!=(4,) or E.ndim!=3 or E.shape[0]!=3 or E.shape[1]!=E.shape[2] or t.shape!=(6,) or r.shape!=(2,3):
        raise ValueError('same material field/first-rate and full angular/time/radial images required')
    n=E.shape[1];m=60*n;T=higgs_u2_real_representation()['real_generators']
    I=np.eye(4*n);W=np.zeros((5,4*n,m));h=np.zeros((4*n,m));ht=h.copy()
    for k in range(2):
        for f in range(5):W[f,:,20*n*k+4*n*f:20*n*k+4*n*(f+1)]=t[0]*r[k,0]*I
    U=np.einsum('cij,j->ci',T,H);Ud=np.einsum('cij,j->ci',T,Hd)
    ad=np.array([np.kron(_ad(a),np.eye(n)) for a in A]);ad[2:]+=np.array([np.kron(np.eye(4),e) for e in E])
    for p in range(2):
        g,gp=t[2+2*p:4+2*p]
        for k in range(2):
            sl=slice(40*n+(2*p+k)*4*n,40*n+(2*p+k+1)*4*n)
            W[:,:,sl]=g*r[k,0]*ad
            W[0,:,sl]+=gp*r[k,0]*I;W[1,:,sl]+=g*r[k,1]*I
            h[:,sl]=-g*r[k,0]*np.kron(U.T,np.eye(n))
            ht[:,sl]=-r[k,0]*np.kron(gp*U.T+g*Ud.T,np.eye(n))
    h[:,56*n:]=t[0]*I;ht[:,56*n:]=t[1]*I
    O=np.einsum('fc,cij->fij',A,T);Umap=np.kron(U.T,np.eye(n))
    B=[]
    for f in (0,2,3,4):
        ordinary=ht if f==0 else np.kron(np.eye(4),E[f-2])@h
        B.append(ordinary+np.kron(O[f],np.eye(n))@h+Umap@W[f])
    return dict(gauge=W,scalar=h,scalar_rate=ht,scalar_covariant_first_images=np.array(B),
        covariant_H_time=Hd+O[0]@H,covariant_H_spatial=O[2:]@H,
        count=m,harmonic_count=n,connection=A,H=H,Hdot=Hd,derivatives=E,temporal=t,radial=r)


def _direction_images(base,target_derivatives,gaunt,source_gauge,source_H,source_Hdot,source_derivatives):
    """Differentiate BOTH independent and paired DG field images."""
    no=base['harmonic_count'];ne=len(target_derivatives[0]);mo=base['count']
    T=higgs_u2_real_representation()['real_generators'];G=np.asarray(gaunt)
    a,h,hd,Es=[np.asarray(x) for x in (source_gauge,source_H,source_Hdot,source_derivatives)]
    if a.shape!=(5,4,G.shape[2]) or h.shape!=(4,G.shape[2]) or hd.shape!=h.shape or Es.shape!=(3,G.shape[2],G.shape[2]):
        raise ValueError('actual complete source value/time/angular images required')
    W=base['gauge'];hv=base['scalar'];ht=base['scalar_rate'];t,r=base['temporal'],base['radial']
    dW=np.zeros((5,4*ne,mo));dh=np.zeros((4*ne,mo));dht=dh.copy()
    Uhs=np.einsum('cij,js->ics',T,h);Uds=np.einsum('cij,js->ics',T,hd)
    mul_h=_multiplication(Uhs,G);mul_hd=_multiplication(Uds,G)
    ma=np.array([_multiplication(np.moveaxis(np.array([_ad(x) for x in f.T]),0,-1),G) for f in a])
    for p in range(2):
        g,gp=t[2+2*p:4+2*p]
        for k in range(2):
            sl=slice(40*no+(2*p+k)*4*no,40*no+(2*p+k+1)*4*no)
            dW[:,:,sl]=g*r[k,0]*ma
            dh[:,sl]=-g*r[k,0]*mul_h
            dht[:,sl]=-r[k,0]*(gp*mul_h+g*mul_hd)
    O=np.einsum('fc,cij->fij',base['connection'],T);U=np.einsum('cij,j->ci',T,base['H'])
    dB=[];dDH=[]
    for f in (0,2,3,4):
        Malpha=_multiplication(np.einsum('cs,cij->ijs',a[f],T),G)
        ordinary=dht if f==0 else np.kron(np.eye(4),target_derivatives[f-2])@dh
        derivative=ordinary+np.kron(O[f],np.eye(ne))@dh+Malpha@hv
        derivative+=np.kron(U.T,np.eye(ne))@dW[f]+mul_h@W[f]
        dB.append(derivative)
        dDH.append((hd if f==0 else h@Es[f-2].T)+O[f]@h+np.einsum('cs,cij,j->is',a[f],T,base['H']))
    return dict(gauge=dW,scalar=dh,scalar_rate=dht,scalar_covariant_first_images=np.array(dB),
        covariant_H_source=np.array(dDH),source_gauge=a,source_H=h)


def intrinsic_coupled_magnetic_source_point(*,weights,H,Hdot,connection,
        odd_derivatives,even_derivatives,source_derivatives,gaunt,
        temporal,wall_radial,source_gauge,source_H,source_Hdot,lambda_H,nu_squared_action):
    """Complete even/odd deltaK and deltaGram of this intrinsic action.

    Sources have axes (three magnetic axes,field/internal,sourceharmonic).
    The result includes d(DH), dDH*(deltaOmega*h), dV_H'', and the
    source motion of BOTH DG gauge/scalar images.  Fixed geometry weights
    are explicit; this does not assign the missing bulk YM derivative0.
    """
    w=_finite(weights,'actual positive intrinsic weights',real=True)
    G=_finite(gaunt,'complete even odd n1 Gaunt image',real=True)
    a=_finite(source_gauge,'actual total magnetic gauge first response',real=True)
    hs=_finite(source_H,'actual total magnetic Higgs first response',real=True)
    hds=_finite(source_Hdot,'actual total magnetic Higgs first rate',real=True)
    lam=_positive(lambda_H,'owned scalar lambda_H');nu=_positive(nu_squared_action,'explicit nu squared',zero=True)
    if w.shape!=(3,) or min(w)<=0 or G.ndim!=3 or a.shape!=(3,5,4,G.shape[2]) or hs.shape!=(3,4,G.shape[2]) or hds.shape!=hs.shape:
        raise ValueError('same positive action weights, complete Gaunt image and all three total sources required')
    bo=coupled_intrinsic_wall_images(connection,H,Hdot,odd_derivatives,temporal,wall_radial)
    be=coupled_intrinsic_wall_images(connection,H,Hdot,even_derivatives,temporal,wall_radial)
    if G.shape[:2]!=(be['harmonic_count'],bo['harmonic_count']):raise ValueError('complete odd/even field spaces differ from Gaunt')
    T=higgs_u2_real_representation()['real_generators'];H=bo['H'];no=bo['harmonic_count'];ne=be['harmonic_count']
    Potential=lam*(4*np.outer(H,H)+2*(H@H-nu)*np.eye(4))
    Vo,Ve=np.kron(Potential,np.eye(no)),np.kron(Potential,np.eye(ne))
    deltaK=[];deltaGram=[];first_images=[];image_motion=[]
    for A in range(3):
        do=_direction_images(bo,even_derivatives,G,a[A],hs[A],hds[A],source_derivatives)
        de=_direction_images(be,odd_derivatives,G.transpose(1,0,2),a[A],hs[A],hds[A],source_derivatives)
        result=np.zeros((be['count'],bo['count']))
        for i,mu in enumerate((w[0],w[1],w[1],w[1])):
            f=(0,2,3,4)[i]
            Be,Bo=be['scalar_covariant_first_images'][i],bo['scalar_covariant_first_images'][i]
            dBe,dBo=de['scalar_covariant_first_images'][i],do['scalar_covariant_first_images'][i]
            pair=Be.T@dBo+dBe.T@Bo
            base=bo['covariant_H_time'] if i==0 else bo['covariant_H_spatial'][i-1]
            C=np.einsum('i,cij->cj',base,T)
            Co,Ce=np.kron(C,np.eye(no)),np.kron(C,np.eye(ne))
            dc=np.einsum('is,cij->cjs',do['covariant_H_source'][i],T)
            Cd=_multiplication(dc,G)
            Cd_reverse=_multiplication(dc.transpose(1,0,2),G)
            W_o,W_e=bo['gauge'][f],be['gauge'][f]
            dW_o,dW_e=do['gauge'][f],de['gauge'][f]
            pair+=W_e.T@Ce@do['scalar']+dW_e.T@Co@bo['scalar']+W_e.T@Cd@bo['scalar']
            pair+=be['scalar'].T@Ce.T@dW_o+de['scalar'].T@Co.T@W_o+be['scalar'].T@Cd_reverse@W_o
            result+=(2*mu/VOLUME)*pair
        dPot=4*lam*(np.einsum('i,js->ijs',H,hs[A])+np.einsum('is,j->ijs',hs[A],H)
            +np.eye(4)[:,:,None]*np.einsum('i,is->s',H,hs[A])[None,None])
        dV=_multiplication(dPot,G)
        result+=(2*w[2]/VOLUME)*(be['scalar'].T@dV@bo['scalar']+de['scalar'].T@Vo@bo['scalar']+be['scalar'].T@Ve@do['scalar'])
        deltaK.append(result)
        deltaGram.append((2*w[2]/VOLUME)*(be['scalar'].T@do['scalar']+de['scalar'].T@bo['scalar']))
        first_images.append(do['scalar_covariant_first_images'])
        image_motion.append(np.r_[np.linalg.norm(do['gauge']),np.linalg.norm(do['scalar']),np.linalg.norm(do['scalar_rate'])])
    return dict(intrinsic_coupled_delta_Hessian_even_odd=np.array(deltaK),
        intrinsic_coupled_delta_Gram_even_odd=np.array(deltaGram),
        source_covariant_first_image_even_odd=np.array(first_images),
        dependent_gauge_scalar_rate_image_motion_norms=np.array(image_motion),
        scalar_action_normalization='real2Re; 2*w_mu/(2pi²), same S4/V² and normalized angular fields',
        full_DH_offshell_cross_and_potential_derivative_retained=True,
        paired_DG_gauge_scalar_image_variations_retained=True,
        bulk_YM_Lorenz_and_ghost_source_variations_not_filled_zero=True,
        same_field_Green_derivative_or_quantum_Sigma_completed=False,
        physical_a_mu=None,physical_g_mu=None)

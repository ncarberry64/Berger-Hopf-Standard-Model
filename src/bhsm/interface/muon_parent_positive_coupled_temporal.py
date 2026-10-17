"""Changing same-phase gauge/H weak action and full18 current application.

All coefficients are reconstructed at chronological quadrature times from
the SAME solved x-linear/vy-midpoint phase chart.  The gauge/H action is
composed before one inverse.  The actual paired scalar BRST images are kept
as dependent images of the existing ghost coordinates.  This application
does not identify the declared positive ADM reference with physical P_strat.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import cholesky, cho_solve, eigh, solve, solve_triangular
from .muon_parent_positive_coupled_field import corrected_positive_parent_reference, coupled_wall_maps, VOLUME
from .muon_parent_positive_brst_ghost import ghost_radial_values, smooth_ghost_temporal_values, _linear_curvature
from .muon_parent_positive_gauge_form import _weighted_curvature_maps, positive_curvature_contact_matrix, stored_inverse_neumann_majorant
from .muon_parent_maxwell_corrected_retarded import _ad, constant_angular_curvatures, higgs_u2_real_representation
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_inherited_lepton_temporal_weak_action import inherited_cell_raw_at_time
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from .muon_parent_retarded_hypercharge import WALL


def one_form_point_row(A,At,Ar,E,radial,metric,densities,temporal):
    """Full literal one-form first-curvature/contact/Gram at one point.

    Unlike a preintegrated constant tent, this retains the b*bprime
    cross term at every point; it cancels only when the actual coefficients
    and the time integration make it cancel.  DG has its true first jets,
    so d_A DG=[F,eta] includes the retained temporal/radial curvature.
    """
    A,At,Ar,E,radial,metric,densities,t=[np.asarray(x) for x in (A,At,Ar,E,radial,metric,densities,temporal)]
    if (A.shape!=(5,4) or At.shape!=A.shape or Ar.shape!=A.shape or E.shape!=(3,20,20) or radial.shape!=(2,3) or
            metric.shape!=(6,) or densities.shape!=(5,) or t.shape!=(6,) or
            any(not np.isrealobj(x) or not np.isfinite(x).all() for x in (A,At,Ar,E,radial,metric,densities,t))):
        raise ValueError('same complete finite positive one-form point jets required')
    I=np.eye(400).reshape(5,80,400);Ef=np.array([np.kron(np.eye(4),a) for a in E])
    V=np.concatenate([p[0]*I for p in radial],axis=2);Vr=np.concatenate([p[1]*I for p in radial],axis=2)
    Va=np.einsum('phk,fkA->pfhA',Ef,V);z=np.zeros_like(V)
    convert=lambda a:a.reshape(a.shape[:-1]+(20,800))
    c0=_linear_curvature(A,V.reshape(5,4,-1),z.reshape(5,4,-1),Vr.reshape(5,4,-1),Va.reshape(3,5,4,-1))
    c1=_linear_curvature(A,z.reshape(5,4,-1),V.reshape(5,4,-1),z.reshape(5,4,-1),np.zeros_like(Va).reshape(3,5,4,-1))
    c0,c1=(_weighted_curvature_maps(tuple(convert(a) for a in c),densities) for c in (c0,c1))
    F=constant_angular_curvatures(A,At,Ar);D=np.array([np.kron(_ad(a),np.eye(20)) for a in A]);D[2:]+=Ef
    G=[];R=[];CG=[];eta=[]
    for p in radial:
        g=p[0]*D;g[1]+=p[1]*np.eye(80);r=np.zeros_like(g);r[0]=p[0]*np.eye(80)
        G.append(g.reshape(400,80));R.append(r.reshape(400,80));eta.append(p[0]*np.eye(80))
        fc=tuple(p[0]*np.kron(_ad(a),np.eye(20)) for a in (F['Ftr'],*F['Ft'],*F['Fr'],*F['B']))
        CG.append(_weighted_curvature_maps((fc[0],np.array(fc[1:4]),np.array(fc[4:7]),np.array(fc[7:10])),densities))
    G,R,CG,eta=(np.concatenate(a,axis=1) for a in (G,R,CG,eta))
    value=np.zeros((400,1120));curv=np.zeros((800,1120));etas=np.zeros((80,320))
    value[:,:800]=t[0]*V.reshape(400,800);curv[:,:800]=t[0]*c0+t[1]*c1
    for i in range(2):
        p=2+2*i;s=slice(800+160*i,960+160*i)
        value[:,s]=t[p]*G+t[p+1]*R;curv[:,s]=t[p]*CG
        etas[:,160*i:160*(i+1)]=t[p]*eta
    C=positive_curvature_contact_matrix(F,densities,20);contact=value.T@C@value
    mu,gt,gr,gs,beta,R=metric
    g=np.diag([gt,gr+beta*beta*gt,gs,gs,gs]);g[0,1]=g[1,0]=-beta*gt
    Gram=value.T@np.kron(g,np.eye(80))@value
    return dict(Hessian=curv.T@curv+contact,Gram=Gram,curvature_contact=contact,
        ghost_Gram=mu*(etas.T@etas),value_map=value,curvature_map=curv)


def paired_scalar_orbit_maps(H,Hdot,temporal,wall_radial):
    """Dependent scalar image deltaH=-eta H and its full coordinate rate.

    The existing320 DG coordinates carry the scalar image at the wall;
    the independent scalar80 coefficients remain the original tent.  This
    is not a new fitted H state or a silent Rxi/H-mass gauge fixing.
    """
    H,Hdot,t,r=[np.asarray(a) for a in (H,Hdot,temporal,wall_radial)]
    if H.shape!=(4,) or Hdot.shape!=(4,) or t.shape!=(6,) or r.shape!=(2,3) or any(not np.isrealobj(a) or not np.isfinite(a).all() for a in (H,Hdot,t,r)):
        raise ValueError('complete real H first germ and same temporal/radial maps required')
    T=higgs_u2_real_representation()['real_generators'];U=np.einsum('cij,j->ci',T,H);Ut=np.einsum('cij,j->ci',T,Hdot)
    h=np.zeros((80,1200));ht=h.copy();h[:,1120:]=t[0]*np.eye(80);ht[:,1120:]=t[1]*np.eye(80)
    for i in range(2):
        p=2+2*i
        for j in range(2):
            s=slice(800+160*i+80*j,880+160*i+80*j)
            h[:,s]=-r[j,0]*t[p]*np.kron(U.T,np.eye(20))
            ht[:,s]=-r[j,0]*np.kron(t[p+1]*U.T+t[p]*Ut.T,np.eye(20))
    return dict(value=h,time=ht)


def intrinsic_coupled_point_form(weights,H,Hdot,connection,E,gauge_map,scalar_map,scalar_time_map,*,lambda_H,nu_squared_action):
    """Literal full real2Re second variation on the combined point images.

    Both DH(deltaOmega h) placements are added alongside the square of
    delta(DH), keeping off-shell contacts.  Potential and Gram use the
    same canonical intrinsic S4/V² normalization as the common action.
    """
    wt,ws,wv=np.asarray(weights,float);H=np.asarray(H);Hdot=np.asarray(Hdot);A=np.asarray(connection)
    E=np.asarray(E);W=np.asarray(gauge_map);h=np.asarray(scalar_map);ht=np.asarray(scalar_time_map)
    lam=float(lambda_H);nu=float(nu_squared_action)
    if (H.shape!=(4,) or Hdot.shape!=(4,) or A.shape!=(5,4) or E.shape!=(3,20,20) or W.shape!=(400,1200) or h.shape!=(80,1200) or ht.shape!=h.shape or
        any(not np.isrealobj(a) or not np.isfinite(a).all() for a in (H,Hdot,A,E,W,h,ht)) or
        not np.isfinite([wt,ws,wv,lam,nu]).all() or min(wt,ws,wv,lam)<=0 or nu<0):
        raise ValueError('same complete scalar/gauge/action point image required')
    T=higgs_u2_real_representation()['real_generators'];O=np.einsum('fc,cij->fij',A,T)
    U=np.einsum('cij,j->ci',T,H);dt=Hdot+O[0]@H;ds=O[2:]@H
    wr=W.reshape(5,80,1200);K=np.zeros((1200,1200));first=[]
    for f,mu in ((0,wt),(2,ws),(3,ws),(4,ws)):
        ordinary=ht if f==0 else np.kron(np.eye(4),E[f-2])@h
        deriv=ordinary+np.kron(O[f],np.eye(20))@h+np.kron(U.T,np.eye(20))@wr[f]
        base=dt if f==0 else ds[f-2]
        cross=wr[f].T@np.kron(np.einsum('i,cij->cj',base,T),np.eye(20))@h
        K+=(2*mu/VOLUME)*(deriv.T@deriv+cross+cross.T);first.append(deriv)
    potential=np.kron(lam*(4*np.outer(H,H)+2*(H@H-nu)*np.eye(4)),np.eye(20))
    K+=(2*wv/VOLUME)*(h.T@potential@h)
    G=(2*wv/VOLUME)*(h.T@h)
    return dict(Hessian=K,Gram=G,scalar_covariant_first_images=np.array(first),
        covariant_H_time=dt,covariant_H_spatial=ds)


def temporal_coupled_field_application(stage_raw,stage_time,representation,angular,*,
        length,quadrature_order,coordinate_time_origin,nu_squared_action,initial_pair=None,reference_pair=None):
    """Integrate the actual changing full action/Gram, then one joint inverse.

    Chronological incoming t=u-L and outgoing t=u both have dt/du=+1.
    The trial/source current norm is int N*b² dt with the proper material
    lapse.  No outgoing-only midpoint body is transplanted into incoming.
    Lorenz fixing remains the one-form FP map; scalar paired orbit images
    do not introduce an unowned Rxi mass.  No negative eigenvalue is shifted.
    """
    L=float(length);origin=float(coordinate_time_origin);E=np.asarray(angular['derivative_matrices'])
    if not np.isfinite([L,origin,stage_time]).all() or L<=0 or E.shape!=(3,20,20) or not np.isfinite(E).all():
        raise ValueError('same positive chronological phase cell and complete odd angular space required')
    if type(quadrature_order)is not int or quadrature_order<6:raise ValueError('resolved split temporal quadrature required')
    nu=float(nu_squared_action);lam=float(representation['scalar_matching']['lambda_H'])
    z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    ghosts=smooth_ghost_temporal_values(times,L);radial=ghost_radial_values(representation['rho']);wallrad=ghost_radial_values(np.array([WALL]))[0]
    K=np.zeros((1200,1200));Gram=K.copy();C=K.copy();gaugeGram=np.zeros((1120,1120));ghostGram=np.zeros((320,320));scalarK=K.copy()
    image=np.zeros((20,1200,18,18),complex);current_norm=0.;snapshots=[];paired_covariance_defect=0.
    for u,weight,tg in zip(times,weights,ghosts):
        t=float(u+origin);raw=inherited_cell_raw_at_time(stage_raw,stage_time,t,representation)
        ref=corrected_positive_parent_reference(raw,representation,coordinate_time=t,initial_pair=initial_pair,reference_pair=reference_pair)
        b=2*min(u/L,1-u/L);bp=2/L if u<L/2 else -2/L
        tf=np.array([b,bp,tg[0,0],tg[0,1],tg[1,0],tg[1,1]])
        for j,(A,At,Ar,metric,dens,rw) in enumerate(zip(ref['background_values'],ref['background_time_derivatives'],ref['background_radial_derivatives'],
                ref['positive_metric_coefficients'],ref['positive_two_form_densities'],ref['radial_weights'])):
            r=one_form_point_row(A,At,Ar,E,radial[j],metric,dens,tf);ww=weight*rw
            K[:1120,:1120]+=ww*MAXWELL_TO_CAP*r['Hessian'];C[:1120,:1120]+=ww*MAXWELL_TO_CAP*r['curvature_contact']
            Gram[:1120,:1120]+=ww*MAXWELL_TO_CAP*r['Gram'];gaugeGram+=ww*r['Gram'];ghostGram+=ww*r['ghost_Gram']
        wr=dict(representation);wr['rho']=np.array([WALL]);wr['radial_quadrature']=np.ones(1)
        wr['gauge_basis']=np.moveaxis(wr['wall_trace_map'],-1,0)[None,:,None]
        wr['gauge_radial_basis']=np.moveaxis(wr['wall_radial_derivative_map'],-1,0)[None,:,None]
        wallref=corrected_positive_parent_reference(raw,wr,coordinate_time=t,initial_pair=initial_pair,reference_pair=reference_pair)
        maps=coupled_wall_maps(wallref['background_values'][0],E,length=L)
        W=np.zeros((400,1200));W[:,:1120]=np.einsum('t,tij->ij',tf,maps['wall_time_profile_value_maps'])
        hs=paired_scalar_orbit_maps(raw[-8:-4],raw[-4:],tf,wallrad)
        geo=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
        coeff=[geo[k].value for k in ('wT','wS','wV')]
        h=intrinsic_coupled_point_form(coeff,raw[-8:-4],raw[-4:],wallref['background_values'][0],E,W,hs['value'],hs['time'],lambda_H=lam,nu_squared_action=nu)
        K+=weight*h['Hessian'];scalarK+=weight*h['Hessian'];Gram+=weight*h['Gram']
        N,R=geo['induced_lapse'].value,geo['R4'].value;vertices=canonical_open_field_vertices(R,N)
        v=np.concatenate((vertices['gauge'].reshape(20,18,18),vertices['scalar']))
        field=np.concatenate((W,hs['value'])).reshape(24,20,1200)
        image+=weight*N*b*b*np.einsum('chj,cab->hjab',field,v);current_norm+=weight*N*b*b
        # Check the actual dependent scalar gauge image against the local
        # covariance identity, retaining Hdot and temporal eta-prime.
        T=higgs_u2_real_representation()['real_generators']
        expected=[]
        for base in (h['covariant_H_time'],*h['covariant_H_spatial']):
            U=np.einsum('cij,j->ci',T,base);block=np.zeros((80,320))
            for i in range(2):
                for q in range(2):block[:,160*i+80*q:160*i+80*(q+1)]=-wallrad[q,0]*tf[2+2*i]*np.kron(U.T,np.eye(20))
            expected.append(block)
        actual=h['scalar_covariant_first_images'][:,:,800:1120]
        paired_covariance_defect=max(paired_covariance_defect,float(np.linalg.norm(actual-np.array(expected))))
        snapshots.append((t,N,R,np.linalg.norm(ref['inherited_profile_value_time_radial']),np.linalg.norm(h['covariant_H_time'])))
    B=gaugeGram[800:];F=cho_solve((cholesky(ghostGram,lower=True),True),B);fix=MAXWELL_TO_CAP*(B.T@F)
    K[:1120,:1120]+=fix
    chol=cholesky(Gram,lower=True);P=solve_triangular(chol,K,lower=True);P=solve_triangular(chol,P.T,lower=True).T
    ev=eigh(P,eigvals_only=True)
    if ev[0]<=0:raise ArithmeticError('changing coupled reference is not positive; no shift permitted')
    inv=solve(P,np.eye(1200),assume_a='gen');Green=solve_triangular(chol.T,inv,lower=False);Green=solve_triangular(chol.T,Green.T,lower=False).T
    image/=current_norm;current=np.zeros((18,18),complex)
    for v in image:
        response=(Green@v.reshape(1200,-1)).reshape(v.shape)
        current+=np.einsum('jai,jak->ik',v.conj(),response)
    return dict(coupled_action_Hessian=K,coupled_action_Gram=Gram,normalized_coupled_operator=P,
        normalized_coupled_eigenvalues=ev,normalized_coupled_Green=inv,coupled_action_Green=Green,
        one_form_curvature_contact_common_cap=C,intrinsic_scalar_complete_Hessian=scalarK,
        one_form_Gram_per_kappa=gaugeGram,ghost_Gram_per_kappa=ghostGram,ghost_FP_Hessian_per_kappa=gaugeGram[800:,800:],
        weak_Lorenz_map=F,canonical_full18_current_source_image=image,
        full18_changing_coupled_open_field_Green_contraction=current,
        chronological_quadrature_samples=np.array(snapshots),proper_time_external_tent_Gram=float(current_norm),
        paired_scalar_gauge_covariance_defect=paired_covariance_defect,
        normalized_inverse_residual=float(np.linalg.norm(P@inv-np.eye(1200))),
        original_coordinate_inverse_residual=float(np.linalg.norm(K@Green-np.eye(1200))),
        normalized_operator_symmetry_defect=float(np.linalg.norm(P-P.T)/np.linalg.norm(P)),
        stored_normalized_inverse_majorant=stored_inverse_neumann_majorant(P,inv),
        finite_coupled_form_positive=True,coordinate_time_origin=origin,cell_length=L,quadrature_order=quadrature_order,
        one_joint_inverse_before_current=True,paired_scalar_BRST_gradient_image_retained=True,
        silent_Rxi_mass_gauge_fixing_added=False,complete_variable_coefficients_at_quadrature_nodes=True,
        proper_clock_current_pairing_applied_once=True,material_At_advection_count=1,
        intermediate_fermion_Green_inserted=False,physical_P_strat_or_Wick_restriction_proved=False,
        full_continuum_domain_or_quantum_Sigma_or_LSZ_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None)

"""One coupled parent gauge/intrinsic-H positive reference application.

The background is the solved finite-normal stage, including the child's
unprojected inherited connection profile.  The reference retains the actual
connection and Higgs first germs, the literal YM curvature contact, and the
complete boundary gauge/H mixed second variation.  It is not an identification
of this finite coefficient-cell form with the completed physical P_strat.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import cholesky, cho_solve, eigh, solve, solve_triangular

from .muon_exact_material_response import exact_geometric_connection_coefficient_jets
from .muon_birth_finite_normal_trace_graph import affine_connection_profile_two_jet
from .muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from .muon_parent_positive_brst_ghost import ghost_radial_values, ghost_temporal_moments, _ghost_form_row
from .muon_parent_positive_gauge_form import (
    one_form_cell_row, one_form_temporal_moments,
    boundary_temporal_product_moments, stored_inverse_neumann_majorant,
)
from .muon_parent_maxwell_corrected_retarded import _ad, higgs_u2_real_representation
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_moving_geometric_action import _fields, _sqrt
from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices

VOLUME = 2*np.pi**2


def corrected_positive_parent_reference(raw_fields, representation, *,
        coordinate_time, initial_pair=None, reference_pair=None):
    """Same exact material metric and full connection image, counted once.

    A child supplies both pair/reference arrays.  Its extra profile is the
    actual parent-minus-child map minus the anchored reference map; value,
    future-coordinate rate and material radial derivative are all applied.
    The parent has no such extra image.  Independent At/Ar are already
    material components: there is no second wall-rate Ar advection.
    """
    x=np.asarray(raw_fields); t=float(coordinate_time); rep=representation
    if not np.isrealobj(x) or x.shape!=(268,) or not np.isfinite(x).all() or not np.isfinite(t):
        raise ValueError('complete actual real raw268 and future coordinate time required')
    if (initial_pair is None)!=(reference_pair is None):
        raise ValueError('the inherited child requires both initial and reference pairs')
    rho=np.asarray(rep['rho']); n=len(rho)
    if rho.ndim!=1 or n==0 or not np.isfinite(rho).all():
        raise ValueError('same regular material quadrature required')
    geo=exact_geometric_connection_coefficient_jets(12,x[:37],x[37:74],x[74:98],rho,
        source_value=x[98],source_rate=x[99])
    A=np.einsum('rj...,j->r...',rep['gauge_basis'],x[100:180])[:,0]
    At=np.einsum('rj...,j->r...',rep['gauge_basis'],x[180:260])[:,0]
    Ar=np.einsum('rj...,j->r...',rep['gauge_radial_basis'],x[100:180])[:,0]
    profile=np.zeros((n,3))
    if initial_pair is not None:
        initial,reference=(np.asarray(a) for a in (initial_pair,reference_pair))
        if any(a.shape!=(2,268) or not np.isrealobj(a) or not np.isfinite(a).all()
               for a in (initial,reference)):
            raise ValueError('same complete real initial/reference pair required')
        parent=affine_geometry_germ(initial[0],t)
        ref=np.array([affine_geometry_germ(a,t) for a in reference])
        profile=(affine_connection_profile_two_jet(np.array([parent,x]),rho)['value']-
                 affine_connection_profile_two_jet(ref,rho)['value'])
    q,v,m=([Jet.constant(float(z),0) for z in b] for b in (x[:37],x[37:74],x[74:98]))
    metric=[]; density=[]
    for j,row in enumerate(geo['rows']):
        A[j,2:]+=M*(row['connection_lambda'].value-1+profile[j,0])
        At[j,2:]+=M*(row['lambda_tau'].value+profile[j,1])
        Ar[j,2:]+=M*(row['lambda_rho'].value+profile[j,2])
        f=_fields(12,q,v,m,float(rho[j])*row['material_jacobian'].value/2)
        R=(f['A']*f['B']/_sqrt(f['A']**2+f['B']**2)).value
        e,r,d,k,beta=[row[a].value for a in ('electric','radial','angular','electric_radial','shift')]
        if min(R,e,r,d,k)<=0:raise ArithmeticError('regular positive reference metric required')
        metric.append((d*R**4,e*R**2,r*R**2,d*R**2,beta,R))
        density.append((e,r,d,k,beta))
    density=np.array(density); metric=np.array(metric)
    residual=abs(density[:,3]-density[:,0]*density[:,1]/density[:,2])/density[:,3]
    if np.max(residual)>2e-14:raise ArithmeticError('same two-form metric identity failed')
    return dict(background_values=A,background_time_derivatives=At,background_radial_derivatives=Ar,
        positive_metric_coefficients=metric,positive_two_form_densities=density,
        inherited_profile_value_time_radial=profile,metric_identity_relative_residual=residual,
        rho=rho,radial_weights=np.asarray(rep['radial_quadrature']),
        material_connection_embedding_count=1,exact_normal_geometry_applied=True,
        extra_connection_Ar_advection_count=0,
        positive_reference_metric='N²dt²+(C_rho J)²(drho+beta dt)²+R²dOmega3²',
        coefficient_cell_scope='actual connection/geometry first germ at a solved stage; not a complete coefficient-time integration or a proved Wick restriction')


def coupled_wall_maps(background_wall, derivative_matrices, *, length):
    """All1120 five-component trace functions at the same actual wall.

    The appended320 covariant ghost-gradient functions retain temporal,
    radial and angular components.  They are not fitted to the800 tent fields.
    """
    A=np.asarray(background_wall); E=np.asarray(derivative_matrices)
    if A.shape!=(5,4) or E.shape!=(3,20,20) or not np.isfinite(A).all() or not np.isfinite(E).all():
        raise ValueError('same full material wall connection and odd derivatives required')
    radial=ghost_radial_values(np.array([WALL]))[0]
    D=np.array([np.kron(_ad(a),np.eye(20)) for a in A]);D[2:]+=np.array([np.kron(np.eye(4),a) for a in E])
    maps=np.zeros((6,400,1120));I=np.eye(400).reshape(5,80,400)
    maps[0,:,:800]=np.concatenate([p[0]*I for p in radial],axis=2).reshape(400,800)
    G=[];R=[]
    for p in radial:
        g=p[0]*D;g[1]+=p[1]*np.eye(80)
        r=np.zeros_like(g);r[0]=p[0]*np.eye(80)
        G.append(g.reshape(400,80));R.append(r.reshape(400,80))
    G,R=(np.concatenate(a,axis=1) for a in (G,R))
    maps[2,:,800:960]=G;maps[3,:,800:960]=R
    maps[4,:,960:]=G;maps[5,:,960:]=R
    temporal=boundary_temporal_product_moments(length)
    return dict(wall_time_profile_value_maps=maps,
        wall_projected_value_map=np.einsum('t,tij->ij',temporal['vertex_time_projection'],maps),
        wall_background_values=A,**temporal)


def intrinsic_gauge_higgs_boundary_blocks(weights, H, Hdot, connection,
        derivative_matrices, wall_time_maps, *, length, lambda_H, nu_squared_action):
    """Literal second variation of one positive intrinsic scalar action.

    S_H^+=(1/V)int[wt|DtH|²+ws sum|DiH|²+wv*lambda*(|H|²-nu²)²]dt.
    Its actual first germ has DtH=Hdot+Omega_t H and DiH=Omega_i H.
    K_aH includes both (Dh,deltaOmega H) and (DH,deltaOmega h).
    The latter is not a mass term and is nonzero off shell.  All real2Re
    factors and unit-Haar timesV/common S4/V² are applied exactly once.
    """
    wt,ws,wv=np.asarray(weights,float);h=np.asarray(H);hd=np.asarray(Hdot)
    a=np.asarray(connection);E=np.asarray(derivative_matrices);W=np.asarray(wall_time_maps)
    lam=float(lambda_H);nu=float(nu_squared_action);L=float(length)
    if (any(not np.isrealobj(z) or not np.isfinite(z).all() for z in (h,hd,a,E,W)) or
        h.shape!=(4,) or hd.shape!=(4,) or a.shape!=(5,4) or E.shape!=(3,20,20) or W.shape!=(6,400,1120) or
        not np.isfinite([wt,ws,wv,lam,nu,L]).all() or min(wt,ws,wv,lam,L)<=0 or nu<0):
        raise ValueError('same finite real scalar/action/connection and complete boundary maps required')
    T=higgs_u2_real_representation()['real_generators'];Omega=np.einsum('fc,cij->fij',a,T)
    dt=hd+Omega[0]@h;ds=np.einsum('aij,j->ai',Omega[2:],h)
    m=one_form_temporal_moments(L);U=np.einsum('cij,j->ci',T,h)
    Kaa=np.zeros((1120,1120));X=np.zeros((1120,80))
    # A square-root factor of the exact temporal Gram reduces this mass
    # application to positive products without a gauge-coordinate inverse.
    time_chol=cholesky(m,lower=True)
    wr=W.reshape(6,5,4,20,1120)
    for f,k,mu in ((0,0,wt),(2,1,ws),(3,2,ws),(4,3,ws)):
        mass=np.einsum('ci,tchA->tihA',U,wr[:,f])
        factor=np.einsum('st,tihA->sihA',time_chol.T,mass).reshape(-1,1120)
        Kaa+=(2*mu/VOLUME)*(factor.T@factor)
        base=dt if f==0 else ds[f-2]
        cross0=np.kron(U@Omega[f]+np.einsum('i,cij->cj',base,T),np.eye(20))
        if f!=0:
            cross0+=np.kron(U,E[f-2])
        cross1=np.kron(U,np.eye(20)) if f==0 else np.zeros((80,80))
        for p in range(6):
            X+=(2*mu/VOLUME)*wr[p,f].reshape(80,1120).T@(m[p,0]*cross0+m[p,1]*cross1)
    Dt=np.kron(Omega[0],np.eye(20))
    Ds=np.array([np.kron(np.eye(4),E[i])+np.kron(Omega[2+i],np.eye(20)) for i in range(3)])
    potential=np.kron(lam*(4*np.outer(h,h)+2*(h@h-nu)*np.eye(4)),np.eye(20))
    P=(12*wt/(wv*L**2))*np.eye(80)+(wt/wv)*(Dt.T@Dt)+(ws/wv)*sum(z.T@z for z in Ds)+potential
    gram=2*wv*L/(3*VOLUME)
    return dict(boundary_gauge_mass_Hessian=Kaa,boundary_gauge_Higgs_mixed_Hessian=X,
        intrinsic_Higgs_Hessian=gram*P,intrinsic_Higgs_Gram_scalar=gram,
        intrinsic_Higgs_normalized_operator=P,intrinsic_Higgs_covariant_angular_derivatives=Ds,
        intrinsic_Higgs_material_temporal_connection=Dt,
        actual_H_covariant_time_derivative=dt,actual_H_covariant_spatial_derivatives=ds,
        intrinsic_Higgs_potential_Hessian=potential,lambda_H=lam,nu_squared_action=nu)


def full18_coupled_current_contraction(field_green, gauge_vertices, scalar_vertices):
    """One full480 field Green contracted with all18 open-field vertices.

    phi_h=Y_h/sqrt(V),phi0=1/sqrt(V) gives no additionalV.  Both
    gauge-scalar offdiagonal placements participate.  This is the open
    field image; it does not insert an intermediate fermion propagator,
    a statistics sign, or an exterior pole/soft-momentum projection.
    """
    G=np.asarray(field_green);v=np.concatenate((np.asarray(gauge_vertices).reshape(20,18,18),
                                               np.asarray(scalar_vertices)),axis=0)
    if G.shape!=(480,480) or v.shape!=(24,18,18) or not np.isfinite(G).all() or not np.isfinite(v).all():
        raise ValueError('complete480 gauge/H field Green and all18 action vertices required')
    paired=np.einsum('ahbh->ab',G.reshape(24,20,24,20))
    return np.einsum('aij,ab,bjk->ik',v.conj().transpose(0,2,1),paired,v)


def positive_coupled_field_application(raw_fields, representation, angular, *, length,
        coordinate_time, nu_squared_action, initial_pair=None, reference_pair=None):
    """Evaluate and invert ONE coupled gauge/intrinsic-H action matrix.

    The full parent gauge matrix, its curvature contact and finite Lorenz
    fixing are normalized to the common cap action.  Intrinsic-H mass,
    cross and Jacobi blocks are then composed BEFORE the single solve.
    No sector Green sum or small-eigenvector deletion is used.
    """
    x=np.asarray(raw_fields);rep=representation;E=np.asarray(angular['derivative_matrices']);L=float(length)
    if E.shape!=(3,20,20) or not np.isfinite(E).all():raise ValueError('complete real odd n1/n3 domain required')
    ref=corrected_positive_parent_reference(x,rep,coordinate_time=coordinate_time,
        initial_pair=initial_pair,reference_pair=reference_pair)
    m=one_form_temporal_moments(L);radial=ghost_radial_values(ref['rho'])
    Kg=np.zeros((1120,1120));Gg=Kg.copy();C=Kg.copy();G0=np.zeros((320,320));K0=G0.copy()
    for j,(A,At,Ar,metric,density,w) in enumerate(zip(ref['background_values'],ref['background_time_derivatives'],
            ref['background_radial_derivatives'],ref['positive_metric_coefficients'],ref['positive_two_form_densities'],ref['radial_weights'])):
        k,g,c=one_form_cell_row(A,At,Ar,E,radial[j],metric,density,m)
        k0,g0=_ghost_form_row(A,E,radial[j],metric,ghost_temporal_moments(L))
        Kg+=w*k;Gg+=w*g;C+=w*c;K0+=w*k0;G0+=w*g0
    # The wall is evaluated directly, not extrapolated from the interior grid.
    wallrep=dict(rep);wallrep['rho']=np.array([WALL]);wallrep['radial_quadrature']=np.ones(1)
    wallrep['gauge_basis']=np.moveaxis(rep['wall_trace_map'],-1,0)[None,:,None]
    wallrep['gauge_radial_basis']=np.moveaxis(rep['wall_radial_derivative_map'],-1,0)[None,:,None]
    wallref=corrected_positive_parent_reference(x,wallrep,coordinate_time=coordinate_time,
        initial_pair=initial_pair,reference_pair=reference_pair)
    wall=coupled_wall_maps(wallref['background_values'][0],E,length=L)
    geo=intrinsic_m4_weight_jet(12,x[:37],x[37:74],x[74:98],source_value=x[98],source_rate=x[99])
    weights=np.array([geo[k].value for k in ('wT','wS','wV')])
    blocks=intrinsic_gauge_higgs_boundary_blocks(weights,x[-8:-4],x[-4:],wallref['background_values'][0],E,
        wall['wall_time_profile_value_maps'],length=L,lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu_squared_action)
    B=Gg[800:];F=cho_solve((cholesky(G0,lower=True),True),B);fix=B.T@F
    alpha=float(MAXWELL_TO_CAP);gh=blocks['intrinsic_Higgs_Gram_scalar']
    K=np.zeros((1200,1200));K[:1120,:1120]=alpha*(Kg+fix)+blocks['boundary_gauge_mass_Hessian']
    K[:1120,1120:]=blocks['boundary_gauge_Higgs_mixed_Hessian'];K[1120:,:1120]=K[:1120,1120:].T
    K[1120:,1120:]=blocks['intrinsic_Higgs_Hessian']
    G=np.zeros_like(K);G[:1120,:1120]=alpha*Gg;G[1120:,1120:]=gh*np.eye(80)
    chol=cholesky(G,lower=True);P=solve_triangular(chol,K,lower=True);P=solve_triangular(chol,P.T,lower=True).T
    ev=eigh(P,eigvals_only=True);positive=bool(ev[0]>0)
    if not positive:raise ArithmeticError('actual coupled positive reference has a nonpositive finite form; no shift permitted')
    inv=solve(P,np.eye(1200),assume_a='gen')
    Green=solve_triangular(chol.T,inv,lower=False);Green=solve_triangular(chol.T,Green.T,lower=False).T
    trace=np.zeros((480,1200));trace[:400,:1120]=wall['wall_projected_value_map'];trace[400:,1120:]=.75*np.eye(80)
    field=trace@Green@trace.T
    vertices=canonical_open_field_vertices(geo['R4'].value,geo['induced_lapse'].value)
    current=full18_coupled_current_contraction(field,vertices['gauge'],vertices['scalar'])
    isolated=np.zeros_like(K);isolated[:1120,:1120]=K[:1120,:1120];isolated[1120:,1120:]=K[1120:,1120:]
    Piso=solve_triangular(chol,isolated,lower=True);Piso=solve_triangular(chol,Piso.T,lower=True).T
    inviso=solve(Piso,np.eye(1200),assume_a='gen')
    # Exact inverse identity retains the cross-block return without subtraction.
    stable=-inviso@(P-Piso)@inv
    dGreen=solve_triangular(chol.T,stable,lower=False);dGreen=solve_triangular(chol.T,dGreen.T,lower=False).T
    dfield=trace@dGreen@trace.T
    dcurrent=full18_coupled_current_contraction(dfield,vertices['gauge'],vertices['scalar'])
    return dict(ref,**wall,**blocks,raw_fields=x.copy(),coordinate_time=float(coordinate_time),cell_length=L,
        one_form_YM_Hessian_per_kappa=Kg,one_form_curvature_contact_per_kappa=C,
        one_form_Gram_per_kappa=Gg,ghost_Gram_per_kappa=G0,ghost_FP_Hessian_per_kappa=K0,
        weak_Lorenz_map=F,weak_gradient_pairing_per_kappa=B,Lorenz_gauge_fixing_per_kappa=fix,
        coupled_action_Hessian=K,coupled_action_Gram=G,normalized_coupled_operator=P,
        normalized_coupled_eigenvalues=ev,normalized_coupled_Green=inv,coupled_action_Green=Green,
        joint_field_trace_map=trace,full_gauge_Higgs_wall_Green=field,
        canonical_gauge_vertices=vertices['gauge'],canonical_scalar_vertices=vertices['scalar'],
        full18_coupled_open_field_Green_contraction=current,
        stable_gauge_Higgs_cross_wall_return=dfield,full18_gauge_Higgs_cross_return=dcurrent,
        stored_normalized_inverse_majorant=stored_inverse_neumann_majorant(P,inv),
        normalized_inverse_residual=float(np.linalg.norm(P@inv-np.eye(1200))),
        original_coordinate_inverse_residual=float(np.linalg.norm(K@Green-np.eye(1200))),
        original_coordinate_inverse_relative_backward_error=float(np.linalg.norm(K@Green-np.eye(1200))/(np.linalg.norm(K)*np.linalg.norm(Green)+np.sqrt(1200))),
        normalized_operator_symmetry_defect=float(np.linalg.norm(P-P.T)/np.linalg.norm(P)),
        ghost_image_FP_relative_error=float(np.linalg.norm(Gg[800:,800:]-K0)/np.linalg.norm(K0)),
        common_cap_Maxwell_factor=alpha,R4=float(geo['R4'].value),induced_lapse=float(geo['induced_lapse'].value),
        finite_coupled_form_positive=positive,gauge_Higgs_boundary_cross_included=True,
        field_inverse_composed_before_open_current_contraction=True,
        actual_Hdot_first_germ_retained=True,material_At_embedding_count=1,
        scalar_temporal_domain='one existing Dirichlet tent; paired scalar ghost orbit and full b² product image are not declared closed',
        field_coordinate_order='1120 parent gauge+gradient images,80 intrinsic real H n1/n3; one1200 matrix',
        complete_variable_body_DdaggerD_time_contact_or_Wick_identification=False,
        physical_BRST_relative_quotient_selected=False,EC_HS_auxiliary_included=False,
        intermediate_fermion_Green_inserted=False,physical_LSZ_soft_Pauli_assigned=False,
        physical_a_mu=None,physical_g_mu=None)

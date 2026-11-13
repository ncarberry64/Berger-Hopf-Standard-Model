"""Reached positive-ADM parent ghost form and off-shell gauge Ward rows.

The reference uses the actual weighted Maxwell metric, not a square of
its Lorentz Hessian.  Smooth H2 ghost polynomials retain both temporal
parities and their complete covariant one-form images.  This finite
reference application does not select a physical Wick/relative domain.
"""
from __future__ import annotations
import numpy as np
from numpy.polynomial import Polynomial
from scipy.linalg import cholesky,eigh,solve_triangular
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_corrected_retarded import _ad,constant_angular_curvatures
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import regular_radial_basis,WALL,ALPHA
from .muon_matched_mechanical_source import epsilon


def smooth_ghost_temporal_values(times,length):
    """Two H2 Dirichlet bubbles and their derivatives, same coefficient maps.

    u²(1-u)² and (2u-1)u²(1-u)² have zero value/first derivative at
    the two faces.  Unlike a tent, their gradient is an H1 one-form.
    The odd bubble also probes temporal divergence of an even field.
    """
    t=np.asarray(times);L=float(length)
    if t.ndim!=1 or not np.isrealobj(t) or not np.isfinite(t).all() or not np.isfinite(L) or L<=0 or np.any(t<0) or np.any(t>L):
        raise ValueError('explicit finite physical reference interval required')
    u=t/L;p=Polynomial([0,0,1,-2,1]);polys=(p,p*Polynomial([-1,2]))
    return np.array([[poly.deriv(k)(u)/L**k for k in range(3)] for poly in polys]).transpose(2,0,1)


def ghost_radial_values(rho):
    """Retained finite-energy interior/wall profiles with analytic second jet."""
    rho=np.asarray(rho,float);v,d=regular_radial_basis(rho,1);x=rho/WALL
    from scipy.special import betaln
    normalization=np.exp(-betaln(3,5+2*ALPHA)/2)
    second=np.column_stack((normalization*(ALPHA*(ALPHA-1)*x**(ALPHA-2)*(1-x)-2*ALPHA*x**(ALPHA-1))/WALL**2,
        ALPHA*(ALPHA-1)*x**(ALPHA-2)/WALL**2))
    return np.stack((v,d,second),axis=2)


def actual_positive_parent_reference(raw_fields,representation):
    """Reconstruct the same full material A,A_tau,A_rho and positive metric.

    ds_E²=N²dt²+(C_rho J)²(drho+beta dt)²+R²dOmega3².
    mu=d R^4 and mu*g^{-1} has time/radial block
    R²[[e,-e beta],[-e beta,r+e beta²]], angular d R².
    The weighted two-form densities are k,e,r,d, k=e*r/d.
    This is the explicitly declared positive ADM reference, not a
    proved analytic continuation of the varying physical geometry.
    """
    raw=np.asarray(raw_fields)
    if not np.isrealobj(raw) or raw.shape!=(268,) or not np.isfinite(raw).all():
        raise ValueError('actual full real raw268 required')
    rep=representation;rho=np.asarray(rep['rho']);nr=len(rho)
    geo=geometric_connection_coefficient_jets(12,raw[:37],raw[37:74],raw[74:98],rho,
        source_value=raw[98],source_rate=raw[99])
    A=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[100:180])[:,0]
    At=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[180:260])[:,0]
    Ar=np.einsum('rj...,j->r...',rep['gauge_radial_basis'],raw[100:180])[:,0]
    from .muon_moving_geometric_action import _fields,_sqrt
    from .aether_exact_radial_schur_lift_v15_83 import Jet
    q,v,m=([Jet.constant(float(z),0) for z in block] for block in (raw[:37],raw[37:74],raw[74:98]))
    metric=[];density=[]
    for j,row in enumerate(geo['rows']):
        A[j,2:]+=M*(row['connection_lambda'].value-1)
        At[j,2:]+=M*row['lambda_tau'].value;Ar[j,2:]+=M*row['lambda_rho'].value
        f=_fields(12,q,v,m,float(rho[j])*row['material_jacobian'].value/2)
        R=(f['A']*f['B']/_sqrt(f['A']**2+f['B']**2)).value
        e,r,d,k,beta=[row[key].value for key in ('electric','radial','angular','electric_radial','shift')]
        if min(R,e,r,d,k)<=0:raise ArithmeticError('regular positive reference metric required')
        metric.append((d*R**4,e*R**2,r*R**2,d*R**2,beta,R))
        density.append((e,r,d,k,beta))
    metric=np.array(metric);density=np.array(density)
    relative=abs(density[:,3]-density[:,0]*density[:,1]/density[:,2])/density[:,3]
    if max(relative)>2e-14:raise ArithmeticError('same Maxwell two-form metric identity failed')
    return dict(background_values=A,background_time_derivatives=At,background_radial_derivatives=Ar,
        positive_metric_coefficients=metric,positive_two_form_densities=density,
        metric_identity_relative_residual=relative,rho=rho,radial_weights=np.asarray(rep['radial_quadrature']),
        positive_reference_metric='N²dt²+(C_rho J)²(drho+beta dt)²+R²dOmega3²',
        ghost_scalar_measure='mu=d*R^4; same connection weight and unit-Tr16 pairing')


def covariant_ghost_gradient_images(A,At,Ar,E,temporal,radial):
    """All gauge one-form images and first jets of eta coefficients.

    Output columns are (temporal parity,radial profile,internal,harmonic).
    δA=D_A eta.  Angular fields retain the full derivative images;
    neither the radial nor temporal component is dropped or fitted.
    """
    A,At,Ar=np.asarray(A),np.asarray(At),np.asarray(Ar)
    E=np.asarray(E);t=np.asarray(temporal);r=np.asarray(radial)
    if A.shape!=(5,4) or At.shape!=A.shape or Ar.shape!=A.shape or E.shape!=(3,20,20) or t.shape!=(2,3) or r.shape!=(2,3):
        raise ValueError('same five-component first jets and complete ghost derivative maps required')
    I=np.eye(80);angular=np.array([np.kron(np.eye(4),e) for e in E])
    ad=np.array([np.kron(_ad(a),np.eye(20)) for a in A])
    adt=np.array([np.kron(_ad(a),np.eye(20)) for a in At]);adr=np.array([np.kron(_ad(a),np.eye(20)) for a in Ar])
    images=[];times=[];radials=[];angles=[];etas=[];etats=[];etars=[]
    for tp in t:
        for rp in r:
            eta=tp[0]*rp[0]*I;et=tp[1]*rp[0]*I;er=tp[0]*rp[1]*I
            ea=angular@eta
            D=ad@eta;D[0]+=et;D[1]+=er;D[2:]+=ea
            Dt=adt@eta+ad@et;Dt[0]+=tp[2]*rp[0]*I;Dt[1]+=tp[1]*rp[1]*I;Dt[2:]+=angular@et
            Dr=adr@eta+ad@er;Dr[0]+=tp[1]*rp[1]*I;Dr[1]+=tp[0]*rp[2]*I;Dr[2:]+=angular@er
            Da=np.einsum('fij,pjk->pfik',ad,ea)
            Da[:,0]+=angular@et;Da[:,1]+=angular@er
            for i in range(3):Da[:,2+i]+=angular@ea[i]
            images.append(D);times.append(Dt);radials.append(Dr);angles.append(Da)
            etas.append(eta);etats.append(et);etars.append(er)
    return dict(value=np.concatenate(images,axis=2),time=np.concatenate(times,axis=2),
        radial=np.concatenate(radials,axis=2),angular=np.concatenate(angles,axis=3),
        eta=np.concatenate(etas,axis=1),eta_time=np.concatenate(etats,axis=1),eta_radial=np.concatenate(etars,axis=1))


def _linear_curvature(A,v,vt,vr,ev):
    """Literal first curvature variation in right coframe; matrix columns."""
    X=vt[1]-vr[0]+_ad(A[0])@v[1]-_ad(A[1])@v[0]
    Ft=np.array([vt[2+i]-ev[i,0]+_ad(A[0])@v[2+i]-_ad(A[2+i])@v[0] for i in range(3)])
    Fr=np.array([vr[2+i]-ev[i,1]+_ad(A[1])@v[2+i]-_ad(A[2+i])@v[1] for i in range(3)])
    B=2*v[2:].copy()
    for i,j,k in np.argwhere(epsilon()):B[i]+=epsilon()[i,j,k]*(ev[j,2+k]+_ad(A[2+j])@v[2+k])
    return (X,Ft,Fr,B)


def _bracket_pair(a,b):
    """Haar paired bracket: a[internal,harmonic,source], b[...,ghost]."""
    out=np.zeros((4,a.shape[-1],b.shape[-1]))
    eps=epsilon()
    for i,j,k in np.argwhere(eps):out[i]+=eps[i,j,k]*(a[j].T@b[k])/np.sqrt(2)
    return out


def ghost_temporal_moments(length):
    """Analytic same-polynomial moments; no temporal quadrature uncertainty."""
    L=float(length)
    if not np.isfinite(L) or L<=0:raise ValueError('positive explicit interval required')
    return dict(value_value=L*np.diag([1/630,1/6930]),
        rate_value=np.array([[0.,-1/630],[1/630,0.]]),
        value_rate=np.array([[0.,1/630],[-1/630,0.]]),
        rate_rate=np.diag([2/105,2/315])/L,
        value_integral=np.array([L/30,0.]),rate_integral=np.zeros(2))


def _ghost_form_row(A,E,radial,metric,moments):
    I=np.eye(80);mu,gt,gr,gs,beta,R=metric
    ad=[np.kron(_ad(a),np.eye(20)) for a in A]
    Di=[np.kron(np.eye(4),E[i])+ad[2+i] for i in range(3)]
    K=np.zeros((320,320));Gram=K.copy()
    for i in range(2):
        for j in range(2):
            pi,pj=radial[i,0],radial[j,0]
            Ni=pi*(ad[0]-beta*ad[1])-beta*radial[i,1]*I
            Nj=pj*(ad[0]-beta*ad[1])-beta*radial[j,1]*I
            Ri=pi*ad[1]+radial[i,1]*I;Rj=pj*ad[1]+radial[j,1]*I
            spatial=pi*pj*sum(D.T@D for D in Di)
            for a in range(2):
                for b in range(2):
                    sl=slice((2*a+i)*80,(2*a+i+1)*80);sr=slice((2*b+j)*80,(2*b+j+1)*80)
                    mm=moments['value_value'][a,b]
                    K[sl,sr]=gt*(moments['rate_rate'][a,b]*pi*pj*I+
                        moments['rate_value'][a,b]*pi*Nj+
                        moments['value_rate'][a,b]*Ni.T*pj+mm*Ni.T@Nj)
                    K[sl,sr]+=mm*(gr*Ri.T@Rj+gs*spatial)
                    Gram[sl,sr]=mu*mm*pi*pj*I
    return K,Gram


def positive_parent_ghost_application(raw_fields,representation,angular,*,length,
                                      first_gauge,first_gauge_rate,first_gauge_radial,time_order=6):
    """Execute actual FP positive form and source Ward/Euler contacts.

    F=d_A^dagger a and M_FP=F(D_A eta).  The weak ghost form is
    <D_A eta,D_A chi> in the explicit positive ADM reference.  Its
    exact stored inverse is a finite reference application only.
    The literal YM source Hessian against D_A eta includes curvature
    contact and is balanced by S'_YM[[a,eta]] on this off-shell base.
    """
    ref=actual_positive_parent_reference(raw_fields,representation)
    E=np.asarray(angular['derivative_matrices']);nr=len(ref['rho']);L=float(length)
    fields=[np.asarray(x) for x in (first_gauge,first_gauge_rate,first_gauge_radial)]
    if (not np.isfinite(L) or L<=0 or E.shape!=(3,20,20) or
        any(not np.isrealobj(x) or x.shape!=(nr,8,5,4,20) or not np.isfinite(x).all() for x in fields)):
        raise ValueError('same actual complete radial magnetic first fields and positive cell interval required')
    if type(time_order) is not int or time_order<6:raise ValueError('resolved smooth ghost temporal quadrature required')
    node,w=np.polynomial.legendre.leggauss(time_order);times=L*(node+1)/2;tw=L*w/2
    temporal=smooth_ghost_temporal_values(times,L);radial=ghost_radial_values(ref['rho']);moments=ghost_temporal_moments(L)
    Gram=np.zeros((320,320));K=Gram.copy();ward=np.zeros((8,320));euler=ward.copy();hessian=ward.copy()
    curvature_image_error=0.;curvature_image_scale=0.
    eps=epsilon();ad=lambda a:np.kron(_ad(a),np.eye(20));I=np.eye(80)
    for j,(A,At,Ar,metric,density) in enumerate(zip(ref['background_values'],ref['background_time_derivatives'],ref['background_radial_derivatives'],ref['positive_metric_coefficients'],ref['positive_two_form_densities'])):
        F=constant_angular_curvatures(A,At,Ar);mu,gt,gr,gs,beta,R=metric;e,r,d,k,_=density
        a,at,ar=(f[j].transpose(1,2,3,0) for f in fields)
        a,at,ar=(x.reshape(5,80,8) for x in (a,at,ar))
        ea=np.einsum('phk,fkA->pfhA',np.array([np.kron(np.eye(4),z) for z in E]),a)
        ca=_linear_curvature(A,a.reshape(5,4,-1),at.reshape(5,4,-1),ar.reshape(5,4,-1),ea.reshape(3,5,4,-1))
        ca=[x.reshape(x.shape[:-1]+(20,8)) for x in ca]
        kg,gg=_ghost_form_row(A,E,radial[j],metric,moments)
        K+=ref['radial_weights'][j]*kg;Gram+=ref['radial_weights'][j]*gg
        # Ward expression is linear in eta and eta's first derivative.
        # Frozen coefficient-cell integration has int ghost'=0 exactly.
        # Evaluate the unit temporal value and multiply its exact moments.
        for t,weight in [(np.array([[1.,0.,0.],[0.,0.,0.]]),ref['radial_weights'][j])]:
            g=covariant_ghost_gradient_images(A,At,Ar,E,t,radial[j]);eta=g['eta']
            V=g['value'];normal=V[0]-beta*V[1]
            cg=_linear_curvature(A,V.reshape(5,4,-1),g['time'].reshape(5,4,-1),g['radial'].reshape(5,4,-1),g['angular'].reshape(3,5,4,-1))
            expected=tuple(ad(f)@eta for f in (F['Ftr'],*F['Ft'],*F['Fr'],*F['B']))
            actual=(cg[0],*cg[1],*cg[2],*cg[3])
            actual=[x.reshape(80,320) for x in actual]
            curvature_image_error=max(curvature_image_error,max(float(np.max(abs(x-y))) for x,y in zip(actual,expected)))
            curvature_image_scale=max(curvature_image_scale,max(float(np.max(abs(x))) for x in expected))
            # First norm term in S''[a,Deta].
            cx,ct,cr,cb=[x.reshape(-1,8) for x in ca]
            ex,et,er,eb=(expected[0],np.concatenate(expected[1:4]),np.concatenate(expected[4:7]),np.concatenate(expected[7:10]))
            H=k*cx.T@ex+e*(ct-beta*cr).T@(et-beta*er)+r*cr.T@er+d*cb.T@eb
            av=a.reshape(5,4,20,8);gv=V.reshape(5,4,20,320);etav=eta.reshape(4,20,320)
            contactX=_bracket_pair(av[0],gv[1])+_bracket_pair(gv[0],av[1]).transpose(0,2,1)
            contactT=np.array([_bracket_pair(av[0],gv[2+i])+_bracket_pair(gv[0],av[2+i]).transpose(0,2,1) for i in range(3)])
            contactR=np.array([_bracket_pair(av[1],gv[2+i])+_bracket_pair(gv[1],av[2+i]).transpose(0,2,1) for i in range(3)])
            contactB=np.zeros_like(contactT)
            for i,p,q in np.argwhere(eps):contactB[i]+=eps[i,p,q]*_bracket_pair(av[2+p],gv[2+q])
            H+=k*np.einsum('c,cAG->AG',F['Ftr'],contactX)+e*np.einsum('ic,icAG->AG',F['Ft']-beta*F['Fr'],contactT-beta*contactR)+r*np.einsum('ic,icAG->AG',F['Fr'],contactR)+d*np.einsum('ic,icAG->AG',F['B'],contactB)
            # Independent first action derivative of [a,eta], including both differentiated brackets.
            C=np.array([_bracket_pair(z,etav) for z in av])
            Ct=np.array([_bracket_pair(z,etav)+_bracket_pair(v,g['eta_time'].reshape(4,20,320)) for z,v in zip(at.reshape(5,4,20,8),av)])
            Cr=np.array([_bracket_pair(z,etav)+_bracket_pair(v,g['eta_radial'].reshape(4,20,320)) for z,v in zip(ar.reshape(5,4,20,8),av)])
            eav=ea.reshape(3,5,4,20,8);eeta=np.einsum('phk,kG->phG',np.array([np.kron(np.eye(4),z) for z in E]),eta).reshape(3,4,20,320)
            Ce=np.array([[_bracket_pair(z,etav)+_bracket_pair(v,eeta[i]) for z,v in zip(eav[i],av)] for i in range(3)])
            cc=_linear_curvature(A,C.reshape(5,4,-1),Ct.reshape(5,4,-1),Cr.reshape(5,4,-1),Ce.reshape(3,5,4,-1))
            cc=[x.reshape(x.shape[:-1]+(8,320)) for x in cc]
            EC=k*np.einsum('c,cAG->AG',F['Ftr'],cc[0])+e*np.einsum('ic,icAG->AG',F['Ft']-beta*F['Fr'],cc[1]-beta*cc[2])+r*np.einsum('ic,icAG->AG',F['Fr'],cc[2])+d*np.einsum('ic,icAG->AG',F['B'],cc[3])
            lift=lambda a:np.concatenate([moments['value_integral'][i]*a[:,:160] for i in range(2)],axis=1)
            hessian+=weight*lift(H);euler+=weight*lift(EC);ward+=weight*lift(H+EC)
    chol=cholesky(Gram,lower=True);P=solve_triangular(chol,K,lower=True)
    P=solve_triangular(chol,P.T,lower=True).T
    values,U=eigh(P)
    if values[0]<=0:raise ArithmeticError('actual positive-ADM FP reference form is not positive')
    inverse=(U/values)@U.T
    inverse=solve_triangular(chol.T,inverse,lower=False)
    inverse=solve_triangular(chol.T,inverse.T,lower=False).T
    return dict(ref,ghost_action_Hessian=K,ghost_action_Gram=Gram,
        normalized_ghost_operator=P,ghost_Green=inverse,ghost_eigenvalues=values,
        ghost_temporal_nodes=times,ghost_temporal_weights=tw,
        ghost_temporal_basis_value_rate_second=temporal,ghost_radial_basis_value_rate_second=radial,
        ghost_temporal_moments=moments,
        ghost_angular_derivative_matrices=E,source_gauge_hessian_against_all_ghost_gradients=hessian,
        source_gauge_Euler_contact=euler,source_offshell_Ward_residual=ward,
        covariant_curvature_image_max_error=curvature_image_error,
        covariant_curvature_image_relative_error=curvature_image_error/max(curvature_image_scale,1e-300),
        inverse_residual=float(np.linalg.norm(K@inverse-np.eye(320))),
        ghost_coordinate_axes=('temporal_parity2','radial_profile2','unit_Tr16_internal4','real_n1_n3_harmonic20'),
        exact_ghost_gradient_images_retained=True,
        coefficient_reference_scope='actual sampled M5 values and first jets held as coefficient-cell germ; temporal ghost moments integrated analytically. Not the varying full-history quantum operator.',
        fixed_boson_direct_open_lepton_ghost_vertex=0,
        zero_vertex_provenance='cbar M_FP[A,H] c has no Psi derivative; zero classical ghost background. Does not remove graded bosonic response or gauge Green dependence.',
        periodic_or_zero_background_ghost_operator_substituted=False,
        Lorentz_Hessian_squared_to_make_positive=False,
        full_one_form_gauge_fixed_inverse_completed=False,
        physical_Wick_relative_BRST_quotient_or_LSZ_completed=False,
        complete_graded_quantum_Sigma_or_Pauli_assigned=False,
        physical_a_mu=None,physical_g_mu=None)

"""Same positive-ADM one-form action, finite Lorenz fixing and ghost images.

The field domain is the complete odd five-component tent domain augmented
by the exact smooth ghost gradients.  No Lorentz Hessian is squared, no
curvature contact is discarded and no negative eigenvalue is shifted.
This is a declared finite coefficient-cell reference, not a Wick or LSZ
identification of the physical graded determinant.
"""
from __future__ import annotations
from functools import lru_cache
from fractions import Fraction
import numpy as np
from scipy.linalg import cholesky,eigh,solve_triangular,cho_solve,solve
from .muon_parent_positive_brst_ghost import (
    actual_positive_parent_reference,ghost_radial_values,_linear_curvature,
    ghost_temporal_moments,_ghost_form_row,
)
from .muon_parent_maxwell_corrected_retarded import _ad,constant_angular_curvatures
from .muon_matched_mechanical_source import epsilon


def _integral_product(a,b,lo,hi):
    c=[Fraction(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return sum(x*(hi**(i+1)-lo**(i+1))/(i+1) for i,x in enumerate(c))


@lru_cache(maxsize=1)
def _unit_temporal_moments():
    g=[Fraction(x) for x in (0,0,1,-2,1)]
    h=[Fraction(x) for x in (0,0,-1,4,-5,2)]
    derivative=lambda p:[(i+1)*p[i+1] for i in range(len(p)-1)]
    left=([Fraction(0),Fraction(2)],[Fraction(2)],g,derivative(g),h,derivative(h))
    right=([Fraction(2),Fraction(-2)],[Fraction(-2)],g,derivative(g),h,derivative(h))
    m=np.array([[float(_integral_product(left[i],left[j],Fraction(0),Fraction(1,2))+
        _integral_product(right[i],right[j],Fraction(1,2),Fraction(1))) for j in range(6)] for i in range(6)])
    return m


def one_form_temporal_moments(length):
    """Exact rational integrals of b,b',g0,g0',g1,g1' before float conversion."""
    L=float(length)
    if not np.isfinite(L) or L<=0:raise ValueError('positive explicit cell interval required')
    orders=np.array([0,1,0,1,0,1])
    return _unit_temporal_moments()*L**(1-orders[:,None]-orders[None,:])


def stored_inverse_neumann_majorant(operator,preconditioner):
    """IEEE guarded Neumann norm for the exact stored normalized matrix.

    The nonnegative product/reduction guard uses gamma_(4n+16), covering
    dot products, absolute residual arithmetic and norm reductions.  It
    excludes production of the stored operator/Gram and upstream fields.
    No matrix is changed.  A bound below1 permits the exact stored inverse
    norm estimate ||M||_inf/(1-rho); otherwise the estimate is absent.
    """
    A,M=(np.asarray(x) for x in (operator,preconditioner))
    if (A.ndim!=2 or A.shape[0]!=A.shape[1] or M.shape!=A.shape or
        any(not np.isrealobj(x) or not np.isfinite(x).all() for x in (A,M))):
        raise ValueError('finite real same square stored matrices required')
    n=len(A);u=np.finfo(float).eps/2;k=4*n+16;gamma=k*u/(1-k*u)
    product=A@M;absolute_product=np.abs(A)@np.abs(M)
    if not np.isfinite(product).all() or not np.isfinite(absolute_product).all():
        raise ArithmeticError('overflowed stored product cannot certify a Neumann bound')
    positive_upper=np.nextafter(absolute_product/(1-gamma),np.inf)
    entry=np.abs(np.eye(n)-product)+gamma*positive_upper+gamma*(np.eye(n)+np.abs(product))
    entry=np.nextafter(entry+np.finfo(float).tiny*n,np.inf)
    rho=float(np.nextafter(np.max(entry.sum(1))/(1-gamma),np.inf))
    norm=float(np.nextafter(np.max(abs(M).sum(1))/(1-gamma),np.inf))
    inverse=None if rho>=1 else float(np.nextafter(norm/(1-rho),np.inf))
    difference=None if rho>=1 else float(np.nextafter(norm*rho/(1-rho),np.inf))
    return dict(defect_infinity_upper=rho,preconditioner_infinity_upper=norm,
        exact_stored_inverse_infinity_upper=inverse,
        exact_stored_inverse_difference_infinity_upper=difference,
        gamma_guard=gamma,operator_or_Gram_production_error_included=False)


def boundary_temporal_product_moments(length):
    """Exact source-product moment and its nonzero intermediate complement.

    External/intermediate fermion tent b and one-form function f give
    projection int b² f / int b².  The residual is the Gram of b f after
    projection onto b.  It is exported rather than declaring the source
    image closed in a single tent.
    """
    L=float(length)
    if not np.isfinite(L) or L<=0:raise ValueError('positive explicit cell interval required')
    g=[Fraction(x) for x in (0,0,1,-2,1)];h=[Fraction(x) for x in (0,0,-1,4,-5,2)]
    derivative=lambda p:[(i+1)*p[i+1] for i in range(len(p)-1)]
    left=([Fraction(0),Fraction(2)],[Fraction(2)],g,derivative(g),h,derivative(h))
    right=([Fraction(2),Fraction(-2)],[Fraction(-2)],g,derivative(g),h,derivative(h))
    multiply=lambda a,b:[sum(a[j]*b[i-j] for j in range(max(0,i-len(b)+1),min(i+1,len(a)))) for i in range(len(a)+len(b)-1)]
    b2=[multiply(a[0],a[0]) for a in (left,right)]
    moment=np.zeros(6);gram=np.zeros((6,6));orders=np.array([0,1,0,1,0,1])
    for i in range(6):
        moment[i]=float(_integral_product(b2[0],left[i],Fraction(0),Fraction(1,2))+
            _integral_product(b2[1],right[i],Fraction(1,2),Fraction(1)))*L**(1-orders[i])
        for j in range(6):
            gram[i,j]=float(_integral_product(multiply(b2[0],left[i]),left[j],Fraction(0),Fraction(1,2))+
                _integral_product(multiply(b2[1],right[i]),right[j],Fraction(1,2),Fraction(1)))*L**(1-orders[i]-orders[j])
    projection=moment/(L/3)
    return dict(vertex_time_projection=projection,source_product_time_Gram=gram,
        source_product_complement_Gram=gram-np.outer(moment,moment)/(L/3),
        fermion_tent_Gram=L/3,temporal_product_image_complete_in_single_tent=False)


def one_form_wall_maps(raw_fields,representation,angular,*,length):
    """Full five-component wall trace maps, including ghost radial traces."""
    from .muon_parent_retarded_hypercharge import WALL
    rep=dict(representation);rep['rho']=np.array([WALL]);rep['radial_quadrature']=np.ones(1)
    rep['gauge_basis']=np.moveaxis(rep['wall_trace_map'],-1,0)[None,:,None]
    rep['gauge_radial_basis']=np.moveaxis(rep['wall_radial_derivative_map'],-1,0)[None,:,None]
    ref=actual_positive_parent_reference(raw_fields,rep);A=ref['background_values'][0]
    E=np.asarray(angular['derivative_matrices']);radial=ghost_radial_values([WALL])[0]
    Efull=np.array([np.kron(np.eye(4),z) for z in E]);D=np.array([np.kron(_ad(a),np.eye(20)) for a in A]);D[2:]+=Efull
    maps=np.zeros((6,400,1120));I=np.eye(400).reshape(5,80,400)
    maps[0,:,:800]=np.concatenate([r[0]*I for r in radial],axis=2).reshape(400,800)
    G=[];R=[]
    for p in radial:
        g=p[0]*D;g[1]+=p[1]*np.eye(80);r=np.zeros_like(g);r[0]=p[0]*np.eye(80)
        G.append(g.reshape(400,80));R.append(r.reshape(400,80))
    G,R=(np.concatenate(a,axis=1) for a in (G,R))
    maps[2,:,800:960]=G;maps[3,:,800:960]=R;maps[4,:,960:]=G;maps[5,:,960:]=R
    temporal=boundary_temporal_product_moments(length)
    projected=np.einsum('t,tij->ij',temporal['vertex_time_projection'],maps)
    return dict(wall_time_profile_value_maps=maps,wall_projected_value_map=projected,
        wall_background_values=A,**temporal)


def positive_curvature_contact_matrix(curvature,densities,harmonic_count):
    """Literal <F,delta²F> on all five real one-form components."""
    e,r,d,k,beta=np.asarray(densities)
    F=curvature;C=np.zeros((20,20));eps=epsilon()
    block=lambda a:-_ad(a)
    C[0:4,4:8]=k*block(F['Ftr'])
    for i in range(3):
        sl=slice(8+4*i,12+4*i)
        electric=block(F['Ft'][i]-beta*F['Fr'][i])
        C[:4,sl]=e*electric
        C[4:8,sl]=-e*beta*electric+r*block(F['Fr'][i])
    C=C+C.T
    for i,j,k0 in np.argwhere(eps):
        C[8+4*j:12+4*j,8+4*k0:12+4*k0]+=d*eps[i,j,k0]*block(F['B'][i])
    return np.kron(C,np.eye(harmonic_count))


def _weighted_curvature_maps(curves,densities):
    e,r,d,k,beta=densities
    X,T,R,B=curves
    return np.concatenate((np.sqrt(k)*X.reshape(-1,X.shape[-1]),
        np.sqrt(e)*(T-beta*R).reshape(-1,X.shape[-1]),
        np.sqrt(r)*R.reshape(-1,X.shape[-1]),
        np.sqrt(d)*B.reshape(-1,X.shape[-1])),axis=0)


def _value_form_blocks(V,G,R,metric,m):
    """All1120 pairings of the same field and DG value maps."""
    ff=V.T@metric@V;fg=V.T@metric@G;fr=V.T@metric@R
    gg=G.T@metric@G;gr=G.T@metric@R;rr=R.T@metric@R
    out=np.zeros((1120,1120));out[:800,:800]=m[0,0]*ff
    for i in range(2):
        a=2+2*i;s=slice(800+160*i,960+160*i)
        out[:800,s]=m[0,a]*fg+m[0,a+1]*fr;out[s,:800]=out[:800,s].T
        for j in range(2):
            b=2+2*j;t=slice(800+160*j,960+160*j)
            out[s,t]=m[a,b]*gg+m[a,b+1]*gr+m[a+1,b]*gr.T+m[a+1,b+1]*rr
    return out


def one_form_cell_row(A,At,Ar,E,radial,metric,densities,moments):
    """Literal one-form Hessian/Gram on one radial node.

    First800 are radial profile2 x field5 x adjoint4 x harmonic20.
    Last320 are temporal parity2 x radial profile2 x adjoint4 x harmonic20.
    The latter are functions D_A eta, not a projection onto the first800.
    Covariant d_A D_A eta=[F,eta] retains all curvature and time/radial jets.
    """
    I=np.eye(400).reshape(5,80,400);Efull=np.array([np.kron(np.eye(4),z) for z in E])
    V=np.concatenate([radial[j,0]*I for j in range(2)],axis=2)
    Vr=np.concatenate([radial[j,1]*I for j in range(2)],axis=2)
    Va=np.einsum('phk,fkA->pfhA',Efull,V)
    C0=_linear_curvature(A,V.reshape(5,4,-1),np.zeros_like(V).reshape(5,4,-1),
        Vr.reshape(5,4,-1),Va.reshape(3,5,4,-1))
    C1=_linear_curvature(A,np.zeros_like(V).reshape(5,4,-1),V.reshape(5,4,-1),
        np.zeros_like(V).reshape(5,4,-1),np.zeros_like(Va).reshape(3,5,4,-1))
    C0,C1=(_weighted_curvature_maps(tuple(z.reshape(z.shape[:-1]+(20,800)) for z in c),densities) for c in (C0,C1))
    F=constant_angular_curvatures(A,At,Ar)
    ad=[np.kron(_ad(a),np.eye(20)) for a in A]
    D=np.array(ad);D[2:]+=Efull
    G=[];R=[];CG=[]
    for j in range(2):
        values=radial[j,0]*D;values[1]+=radial[j,1]*np.eye(80)
        rates=np.zeros_like(values);rates[0]=radial[j,0]*np.eye(80)
        G.append(values.reshape(400,80));R.append(rates.reshape(400,80))
        FC=tuple(radial[j,0]*np.kron(_ad(f),np.eye(20)) for f in (F['Ftr'],*F['Ft'],*F['Fr'],*F['B']))
        curves=(FC[0],np.array(FC[1:4]),np.array(FC[4:7]),np.array(FC[7:10]))
        CG.append(_weighted_curvature_maps(curves,densities))
    G,R,CG=(np.concatenate(a,axis=1) for a in (G,R,CG))
    V=V.reshape(400,800);m=moments
    K=np.zeros((1120,1120));K[:800,:800]=m[0,0]*C0.T@C0+m[1,1]*C1.T@C1
    for i in range(2):
        a=2+2*i;s=slice(800+160*i,960+160*i)
        K[:800,s]=m[0,a]*C0.T@CG+m[1,a]*C1.T@CG;K[s,:800]=K[:800,s].T
        for j in range(2):
            b=2+2*j;t=slice(800+160*j,960+160*j)
            K[s,t]=m[a,b]*CG.T@CG
    contact=_value_form_blocks(V,G,R,positive_curvature_contact_matrix(F,densities,20),m)
    mu,gt,gr,gs,beta,orbit_radius=metric
    gram_blocks=np.diag([gt,gr+beta**2*gt,gs,gs,gs]);gram_blocks[0,1]=gram_blocks[1,0]=-beta*gt
    Gram=_value_form_blocks(V,G,R,np.kron(gram_blocks,np.eye(80)),m)
    return K+contact,Gram,contact


def positive_parent_gauge_application(raw_fields,representation,angular,*,length):
    """Execute full finite one-form/Lorenz form and its inverse if positive.

    F is the actual weak d_A dagger map into the same320 ghost functions:
    B=<D_A eta,a>_1, F=Gram0^-1 B.  Gauge fixing is B^T Gram0^-1 B.
    Exact gradient images are appended, so no fitted BRST image is used.
    Boundary intrinsic-H mass/mixed rows and EC-HS are separate sectors;
    this pure parent one-form inverse is not a total matter inverse.
    """
    ref=actual_positive_parent_reference(raw_fields,representation)
    E=np.asarray(angular['derivative_matrices']);L=float(length)
    if E.shape!=(3,20,20) or not np.isfinite(E).all():raise ValueError('complete actual odd derivative maps required')
    m=one_form_temporal_moments(L);radial=ghost_radial_values(ref['rho'])
    K=np.zeros((1120,1120));G=K.copy();contact=K.copy();ghostGram=np.zeros((320,320));ghostK=ghostGram.copy()
    for j,(A,At,Ar,metric,density,w) in enumerate(zip(ref['background_values'],ref['background_time_derivatives'],
        ref['background_radial_derivatives'],ref['positive_metric_coefficients'],ref['positive_two_form_densities'],ref['radial_weights'])):
        kr,gr,cr=one_form_cell_row(A,At,Ar,E,radial[j],metric,density,m)
        kg,gg=_ghost_form_row(A,E,radial[j],metric,ghost_temporal_moments(L))
        K+=w*kr;G+=w*gr;contact+=w*cr;ghostGram+=w*gg;ghostK+=w*kg
    B=G[800:,:];chol0=cholesky(ghostGram,lower=True)
    F=cho_solve((chol0,True),B);fix=B.T@F;total=K+fix
    chol=cholesky(G,lower=True);P=solve_triangular(chol,total,lower=True)
    P=solve_triangular(chol,P.T,lower=True).T
    values,U=eigh(P)
    positive=bool(values[0]>0)
    inverse=None;inverse_residual=None;normalized_inverse=None;normalized_residual=None;backward_error=None;majorant=None
    if positive:
        # Solve the actual stored normalized matrix, rather than replacing
        # it by an eigenvector reconstruction using only one triangle.
        normalized_inverse=solve(P,np.eye(1120),assume_a='gen')
        normalized_residual=float(np.linalg.norm(P@normalized_inverse-np.eye(1120)))
        inverse=normalized_inverse
        inverse=solve_triangular(chol.T,inverse,lower=False)
        inverse=solve_triangular(chol.T,inverse.T,lower=False).T
        inverse_residual=float(np.linalg.norm(total@inverse-np.eye(1120)))
        backward_error=inverse_residual/(np.linalg.norm(total)*np.linalg.norm(inverse)+np.sqrt(1120))
        majorant=stored_inverse_neumann_majorant(P,normalized_inverse)
    wall=one_form_wall_maps(raw_fields,representation,angular,length=L)
    wall_green=None if inverse is None else wall['wall_projected_value_map']@inverse@wall['wall_projected_value_map'].T
    return dict(ref,**wall,one_form_YM_Hessian=K,one_form_curvature_contact=contact,
        one_form_Gram=G,ghost_Gram=ghostGram,ghost_FP_Hessian=ghostK,
        weak_Lorenz_map=F,weak_gradient_pairing=B,Lorenz_gauge_fixing=fix,
        gauge_fixed_one_form_Hessian=total,normalized_gauge_fixed_operator=P,
        gauge_fixed_eigenvalues=values,gauge_fixed_Green=inverse,
        projected_wall_one_form_Green=wall_green,
        normalized_gauge_fixed_Green=normalized_inverse,
        normalized_inverse_residual=normalized_residual,inverse_relative_backward_error=backward_error,
        stored_normalized_inverse_majorant=majorant,
        ghost_image_FP_relative_error=float(np.linalg.norm(G[800:,800:]-ghostK)/np.linalg.norm(ghostK)),
        inverse_residual=inverse_residual,finite_gauge_fixed_form_positive=positive,
        ghost_gradient_coordinate_injection=np.eye(1120)[:,800:],
        one_form_temporal_moment_matrix=m,radial_profile_value_rate_second=radial,
        field_coordinates='tent x radial2 x field5 x unit-Tr16 adjoint4 x real n1/n3 harmonic20=800',
        augmented_coordinates='320 exact D_A eta images (H2 smooth ghosts); total1120',
        gauge_fixing_scope='finite weak Lorenz projection into exactly the same320 ghost functions; full gradient images retained',
        intrinsic_Higgs_gauge_boundary_mass_and_mixed_rows_included=False,
        physical_Wick_relative_BRST_quotient_or_LSZ_completed=False,
        complete_graded_quantum_Sigma_or_Pauli_assigned=False,
        physical_a_mu=None,physical_g_mu=None)

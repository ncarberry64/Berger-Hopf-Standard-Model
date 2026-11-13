"""Actual magnetic gauge-plus-Higgs source Hessian on the positive cell.

The even Yukawa coefficient is computed as an analytic Cauchy coefficient,
avoiding subtraction of two nearly identical physical-family heat values.
The contour is a coefficient algorithm, not a selected Higgs or Yukawa.
The temporal tent/cutoff remain explicit numerical components.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eig, eigh

from .muon_primal_cell_reached_source_heat import actual_reached_cell_vertices
from .muon_primal_cell_native_heat import _positive_length
from .muon_native_mean_core_heat_target import _unit_lepton_mass6
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def magnetic_source_heat_polynomial(fields, representation, angular, *, length):
    """Build the reached P, P_A and P_AB polynomial coefficients, all images."""
    h=_positive_length(length)
    vertices=actual_reached_cell_vertices(fields,representation);op=vertices['operator']
    ids=np.array([0,1,6,7,12,13])
    alpha=lepton_current_hilbert_representation()['alpha'][:,ids][:,:,ids]
    W=op['W'][np.ix_(ids,ids)].copy();W[:4,4:]=0;W[4:,:4]=0
    A=W+op['Omega_tau'][np.ix_(ids,ids)]
    M=_unit_lepton_mass6(op['H']);temporal=12/(op['N']**2*h*h)
    def pencil(B,U):
        return (temporal*np.eye(len(B))+B.conj().T@B,
                B.conj().T@U+U.conj().T@B,U.conj().T@U)
    P0=pencil(A,M)
    gauge=vertices['gauge_spatial_vertex']+vertices['gauge_temporal_vertex']
    Xg=gauge[:,:,ids][:,:,:,ids]
    Xh=np.array([_unit_lepton_mass6(H) for H in
        vertices['complex_H_response'].reshape(160,2)]).reshape(8,20,6,6)
    shells={};contact=[np.zeros((8,8,6,6),complex) for _ in range(3)]
    E=angular['derivative_matrices']
    for n in (1,3):
        labels=np.array([i for i,l in enumerate(angular['harmonic_labels']) if l[0]==n]);d=len(labels)
        B=-1j*sum(np.kron(E[a][np.ix_(labels,labels)],alpha[a]) for a in range(3))/op['R4']+np.kron(np.eye(d),A)
        U=np.kron(np.eye(d),M)
        G=Xg[:,labels].reshape(8,6*d,6);H=Xh[:,labels].reshape(G.shape)
        Ga=Xg[:,labels].conj().transpose(0,1,3,2).reshape(G.shape)
        Ha=Xh[:,labels].conj().transpose(0,1,3,2).reshape(H.shape)
        # At complex Y, adjoints act on coefficient matrices, never on Y.
        F0=np.einsum('ij,Ajk->Aik',B.conj().T,G)+np.einsum('Aij,jk->Aik',Ga,A)
        F1=(np.einsum('ij,Ajk->Aik',U.conj().T,G)+np.einsum('ij,Ajk->Aik',B.conj().T,H)
            +np.einsum('Aij,jk->Aik',Ga,M)+np.einsum('Aij,jk->Aik',Ha,A))
        F2=np.einsum('ij,Ajk->Aik',U.conj().T,H)+np.einsum('Aij,jk->Aik',Ha,M)
        # For rectangular images, the reverse source block is the adjoint
        # coefficient polynomial.  X itself may include temporal connection.
        C0=np.einsum('Aki,Bkj->ABij',G.conj(),G)
        C1=np.einsum('Aki,Bkj->ABij',G.conj(),H)+np.einsum('Aki,Bkj->ABij',H.conj(),G)
        C2=np.einsum('Aki,Bkj->ABij',H.conj(),H)
        for k,C in enumerate((C0,C1,C2)):
            contact[k]+=C+C.transpose(1,0,2,3)
        shells[str(n)]=dict(pencil=pencil(B,U),first_source=(F0,F1,F2),
            gauge_vertex=G,unit_Y_H_vertex=H,intermediate_mode_count=6*d)
    Gamma=np.diag([1]*4+[-1]*2)
    parity=max(float(np.max(abs(Gamma@p@Gamma-((-1)**k)*p))) for k,p in enumerate(P0))
    parity=max(parity,max(float(np.max(abs(np.einsum('ij,ABjk,kl->ABil',Gamma,C,Gamma)-((-1)**k)*C)))
        for k,C in enumerate(contact)))
    if parity!=0:
        raise ArithmeticError('source polynomial lost the retained exact L/R parity')
    return dict(n0_pencil=P0,contact=tuple(contact),shells=shells,
        vertices=vertices,length=h,temporal_factor_squared=temporal,
        exact_LR_even_sign_parity=True,normalized_Haar_volume_count=1,
        source_statistics_factor_inserted=False,complete_native_or_Pauli=False)


def _evaluate(polynomial, z):
    return polynomial[0]+z*polynomial[1]+z*z*polynomial[2]


def _analytic_lag(a,b,c,order):
    """Analytic lag K=integral dv (1-v)e^-ck(c/k+1/k²)."""
    nodes,weights=np.polynomial.legendre.leggauss(order)
    nodes=(nodes+1)/2;weights=weights/2
    out=np.zeros((len(a),len(b)),complex)
    for v,w in zip(nodes,weights):
        k=(1-v)*a[:,None]+v*b[None,:]
        out+=w*(1-v)*np.exp(-c*k)*(c/k+1/k**2)
    return out


def analytic_magnetic_source_pair(polynomial, Yukawa_parameter, cutoff, *, lag_order=64):
    """Evaluate the holomorphic coefficient family, including both orders."""
    c=_positive_length(cutoff);z=complex(Yukawa_parameter)
    if not np.isfinite([z.real,z.imag]).all() or type(lag_order) is not int or lag_order<8:
        raise ValueError('finite analytic coefficient parameter and resolved lag rule required')
    P=_evaluate(polynomial['n0_pencil'],z)
    lam,V=eig(P);Vi=np.linalg.solve(V,np.eye(6))
    if min(lam.real)<=0:raise ValueError('accretive analytic cell required')
    C=_evaluate(polynomial['contact'],z)
    diagonal=np.einsum('ij,ABjk,ki->ABi',Vi,C,V)
    direct=-np.einsum('i,ABi->AB',np.exp(-c*lam)/lam,diagonal)
    ordered=np.zeros_like(direct)
    for shell in polynomial['shells'].values():
        Pn=_evaluate(shell['pencil'],z);ln,Vn=eig(Pn);Vni=np.linalg.solve(Vn,np.eye(len(ln)))
        if min(ln.real)<=0:raise ValueError('accretive analytic complement required')
        F=_evaluate(shell['first_source'],z)
        reverse=_evaluate(tuple(p.conj().transpose(0,2,1) for p in shell['first_source']),z)
        forward=np.einsum('ij,Ajk,kl->Ail',Vni,F,V)
        backward=np.einsum('ij,Ajk,kl->Ail',Vi,reverse,Vn)
        lag=_analytic_lag(lam,ln,c,lag_order)
        ordered+=np.einsum('Aij,Bji,ij->AB',backward,forward,lag)
    return dict(source_square_contact=direct,ordered_two_insertion=ordered,
        opposite_order_two_insertion=ordered.T.copy(),available_source_pair=direct+ordered+ordered.T)


def magnetic_source_even_y2_coefficient(polynomial, cutoff, *, contour_radius=16384.,
        contour_order=32,lag_order=64):
    """Compute Y² by Cauchy quadrature on an explicitly accretive circle.

    The exact integral coefficient is H_2=average H(r exp(it))exp(-2it)/r².
    The finite trapezoid has analytic higher-coefficient aliasing; the
    returned refinement difference is a numerical diagnostic, not an
    enclosure of eigensolver, upstream assembly or continuum errors.
    """
    c=_positive_length(cutoff);r=_positive_length(contour_radius)
    if type(contour_order) is not int or contour_order<16 or contour_order%2:
        raise ValueError('even analytic contour order>=16 required')
    margins=[]
    for coefficients in [polynomial['n0_pencil']]+[p['pencil'] for p in polynomial['shells'].values()]:
        gap=float(min(eigh(coefficients[0],eigvals_only=True)))
        margins.append(gap-r*np.linalg.norm(coefficients[1],2)-r*r*np.linalg.norm(coefficients[2],2))
    if min(margins)<=0:raise ValueError('the full source-reached circle must remain accretive')
    sums={name:np.zeros((8,8),complex) for name in ('source_square_contact','ordered_two_insertion','opposite_order_two_insertion','available_source_pair')}
    for j in range(contour_order):
        t=2*np.pi*(j+.5)/contour_order;z=r*np.exp(1j*t)
        values=analytic_magnetic_source_pair(polynomial,z,c,lag_order=lag_order)
        weight=np.exp(-2j*t)/(r*r*contour_order)
        for name in sums:sums[name]+=weight*values[name]
    # Keep the reported ledger sum literal, even below rounding of the
    # much larger gauge-only contour values.
    sums['opposite_order_two_insertion']=sums['ordered_two_insertion'].T.copy()
    sums['available_source_pair']=(sums['source_square_contact']+
        sums['ordered_two_insertion']+sums['opposite_order_two_insertion'])
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real;difference=Y[1]**2-Y[2]**2
    paired={name:difference*value for name,value in sums.items()}
    paired['available_source_pair']=(paired['source_square_contact']+
        paired['ordered_two_insertion']+paired['opposite_order_two_insertion'])
    return dict(unit_Y2_source_pair=sums,paired_middle_minus_light_Y2_source_pair=paired,
        fixed_Y_square_difference=float(difference),contour_radius=r,contour_order=contour_order,
        lag_order=lag_order,cutoff_probe=c,numerical_circle_accretivity_margin=float(min(margins)),
        coefficient_imaginary_rounding_norm=float(np.linalg.norm(sums['available_source_pair'].imag)),
        all_n1_n3_complement_modes_retained=True,both_source_orders_retained=True,
        gauge_source_and_solved_H_response_retained=True,
        contour_is_coefficient_algorithm_not_physical_Y_selection=True,
        source_pair_Y4_remainder_outward_certified=False,
        source_statistics_factor_inserted=False,complete_native_or_Pauli=False)


def magnetic_source_analytic_error_estimates(polynomial,cutoff,*,outer_radius=65536.,
        contour_radius=16384.,contour_order=32):
    """Finite analytic tail/alias majorants evaluated in binary64.

    These formulas are conditional on the exact polynomial and its norm
    bounds.  The returned floating evaluations are not outward enclosures
    of upstream assembly, spectral/norm rounding, or temporal projection.
    """
    c=_positive_length(cutoff);R=_positive_length(outer_radius);r=_positive_length(contour_radius)
    if not r<R or type(contour_order) is not int or contour_order<16:
        raise ValueError('outer analytic circle and resolved smaller contour required')
    coefficients=[polynomial['n0_pencil']]+[p['pencil'] for p in polynomial['shells'].values()]
    a=min(float(min(eigh(p[0],eigvals_only=True)))-R*np.linalg.norm(p[1],2)-R*R*np.linalg.norm(p[2],2)
        for p in coefficients)
    if a<=0:raise ValueError('positive accretivity on the bounding circle required')
    contact=sum(R**k*np.array([[np.linalg.norm(m,2) for m in row] for row in p])
        for k,p in enumerate(polynomial['contact']))
    product=np.zeros((8,8))
    for shell in polynomial['shells'].values():
        F=sum(R**k*np.array([np.linalg.norm(m,2) for m in p])
            for k,p in enumerate(shell['first_source']))
        product+=F[:,None]*F[None,:]
    M=6*np.exp(-c*a)*(contact/a+(c/a+1/a**2)*product)
    q=r/R;alias=M/R**2*q**contour_order/(1-q**contour_order)
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real
    # Even action parity makes the difference of the geometric tails valid.
    ratios=(Y[1]/R)**2,(Y[2]/R)**2
    remainder=M*(ratios[0]**2/(1-ratios[0])-ratios[1]**2/(1-ratios[1]))
    return dict(bounding_circle_radius=R,bounding_circle_accretivity_margin=a,
        circle_source_pair_norm_majorant=M,unit_Y2_contour_alias_majorant_estimate=alias,
        paired_even_Y4_remainder_majorant_estimate=remainder,
        analytic_alias_equation='M/R^2*(r/R)^N/(1-(r/R)^N)',
        even_tail_equation='M*((Ymu/R)^4/(1-(Ymu/R)^2)-(Ye/R)^4/(1-(Ye/R)^2))',
        semigroup_source_bound='6 exp(-c a) [norm(P_AB)/a+(c/a+1/a^2) sum_n norm(P_A,n0) norm(P_B,n0)]',
        norm_and_majorant_arithmetic_outward_certified=False,
        upstream_assembly_eigensolver_or_continuum_error_enclosed=False)

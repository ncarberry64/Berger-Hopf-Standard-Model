"""Positive-factor source heat on actual interacting coefficient cells.

The constant-cell coefficient evaluation uses the solved common midpoint
fields and a Dirichlet temporal tent as an explicit numerical form core.
It does not select the complete event domain or a formation cutoff.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eigh
from scipy.special import exp1
from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import (
    retained_eight_q_fermion_source_image,_ordered_cutoff_heat_lag,
)
from .muon_native_mean_core_heat_target import _unit_lepton_mass6
from .muon_current_source_motion_cubic import _real,current_face_source_jets


def _positive_length(value):
    if value is None or not np.isrealobj(value):raise ValueError('explicit real numerical cell length required')
    h=float(value)
    if not np.isfinite(h) or h<=0:raise ValueError('positive finite numerical cell length required')
    return h


def actual_cell_heat_polynomial(raw_fields,representation,*,length):
    """P(Y)=P0+YC+YÃ‚Â²B on the normalized constant-angular six-fiber core.

    For the temporal tent b with b=0 at both faces, int b b'=0,
    int bÃ‚Â²=L/3, int b'Ã‚Â²=4/L.  Thus the exact coefficient-cell
    normalized pencil is 12/(NÃ‚Â²LÃ‚Â²)I+(W+Omega_tau)Ã¢â‚¬Â (W+Omega_tau).
    Differentiating this quotient retains the lapse/Gram contact.
    """
    h=_positive_length(length);op=primal_trace_enriched_lepton_operator(raw_fields,representation)
    ids=np.array([0,1,6,7,12,13]);nr=len(raw_fields)
    W=op['W'][np.ix_(ids,ids)].copy();omega=op['Omega_tau'][np.ix_(ids,ids)].copy()
    dW=op['W_raw_first_jet'][:,ids][:,:,ids].copy();do=op['Omega_tau_raw_first_jet'][:,ids][:,:,ids].copy()
    # Exact action grading: internal gauge/principal is L/R diagonal;
    # full complex weak-frame Higgs is solely the off-diagonal mass.
    W[:4,4:]=0;W[4:,:4]=0;dW[:,:4,4:]=0;dW[:,4:,:4]=0
    M=_unit_lepton_mass6(op['H']);dM=np.zeros_like(dW)
    dM[nr-8:nr-4]=np.array([_unit_lepton_mass6(H) for H in ([1,0],[0,1],[1j,0],[0,1j])])
    A=W+omega;dA=dW+do;temporal=12/(op['N']**2*h*h)
    ratio=op['proper_time_Haar_measure_first_jet']/op['proper_time_Haar_measure']
    spatial=A.conj().T@A;P0=temporal*np.eye(6)+spatial
    C=A.conj().T@M+M.conj().T@A;B=M.conj().T@M
    dSpatial=np.einsum('bij,jk->bik',dA.conj().transpose(0,2,1),A)+np.einsum('ij,bjk->bik',A.conj().T,dA)
    dTemporal=-2*temporal*ratio;dP=dTemporal[:,None,None]*np.eye(6)+dSpatial
    dC=np.einsum('bij,jk->bik',dA.conj().transpose(0,2,1),M)+np.einsum('ij,bjk->bik',A.conj().T,dM)+np.einsum('bij,jk->bik',dM.conj().transpose(0,2,1),A)+np.einsum('ij,bjk->bik',M.conj().T,dA)
    dB=np.einsum('bij,jk->bik',dM.conj().transpose(0,2,1),M)+np.einsum('ij,bjk->bik',M.conj().T,dM)
    Gamma=np.diag([1]*4+[-1]*2)
    if any(np.max(abs(x))!=0 for x in (Gamma@P0@Gamma-P0,Gamma@C@Gamma+C,Gamma@B@Gamma-B)):
        raise RuntimeError('owned cell polynomial lost exact L/R sign grading')
    return dict(P0=P0,P1=C,P2=B,P0_raw_first_jet=dP,P1_raw_first_jet=dC,P2_raw_first_jet=dB,
        normalized_LR_sign_grading=Gamma,operator=op,length=h,
        temporal_factor_squared=temporal,temporal_factor_squared_raw_first_jet=dTemporal,
        zero_Y_spatial_square=spatial,zero_Y_spatial_square_raw_first_jet=dSpatial,FE_Gram_scalar=op['proper_time_Haar_measure']*h/3,
        coefficient_cell_scope='actual solved midpoint coefficients, constant within this numerical action cell; not an interpolated full history',
        domain='Dirichlet temporal tent, normalized Haar constant-angular C6; no arbitrary birth transmission or dual imposed',
        normalized_Gram_contact_included=True,physical_formation_cutoff_selected=False)


def _divided_differences(values,c,order):
    """Stable simplex g[1],g[2] also for nearly equal large poles."""
    if type(order) is not int or order<4:raise ValueError('divided-difference quadrature order>=4 required')
    x,w=np.polynomial.legendre.leggauss(order);x=(x+1)/2;w=w/2
    first=np.zeros((len(values),len(values)));second=np.zeros((len(values),)*3)
    a,b,d=np.broadcast_arrays(values[:,None,None],values[None,:,None],values[None,None,:])
    for t,wt in zip(x,w):
        q=(1-t)*values[:,None]+t*values[None,:]
        first+=wt*np.exp(-c*q)*(c/q+1/q**2)
        for u,wu in zip(x,w):
            q=(1-t)*a+t*(1-u)*b+t*u*d
            second-=wt*wu*t*np.exp(-c*q)*(c*c/q+2*c/q**2+2/q**3)
    return first,second


def actual_cell_even_y_target(polynomial,cutoff,*,divided_difference_order=16):
    """Stable paired YÃ‚Â² value and full raw cotangent, without family subtraction."""
    c=_positive_length(cutoff);P0,C,B=(polynomial[k] for k in ('P0','P1','P2'))
    values=[];V=np.zeros((6,6),complex);offset=0
    for ids in (np.arange(4),np.arange(4,6)):
        v,U=eigh(P0[np.ix_(ids,ids)]);V[np.ix_(ids,np.arange(offset,offset+len(ids)))]=U
        values.extend(v);offset+=len(ids)
    lam=np.array(values)
    if min(lam)<=0:raise ValueError('actual coefficient-cell pencil must be strictly positive')
    C=V.conj().T@C@V;B=V.conj().T@B@V
    first,second=_divided_differences(lam,c,divided_difference_order);g=-np.exp(-c*lam)/lam
    D=first*C;Z=first*B+np.einsum('ijk,ij,jk->ik',second,C,C)
    Z=(Z+Z.conj().T)/2;D=(D+D.conj().T)/2
    coefficient=float((g@np.diag(B).real+.5*np.sum(first*abs(C)**2)).real)
    transformed=[np.einsum('ij,bjk,kl->bil',V.conj().T,polynomial[k],V) for k in ('P0_raw_first_jet','P1_raw_first_jet','P2_raw_first_jet')]
    gradient=(np.einsum('ij,bji->b',Z,transformed[0])+np.einsum('ij,bji->b',D,transformed[1])+np.einsum('i,bii->b',g,transformed[2])).real
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real;difference=Y[1]**2-Y[2]**2
    gap=float(min(lam));cn=float(np.linalg.norm(C,2));bn=float(np.linalg.norm(B,2))
    radius=min(gap/(4*cn) if cn else np.inf,np.sqrt(gap/(4*bn)) if bn else np.inf)
    if not np.isfinite(radius) or radius<=max(abs(Y[1:])):raise ValueError('finite even-Y circle must contain actual fixed Yukawas')
    tailfactor=(Y[1]/radius)**4/(1-(Y[1]/radius)**2)-(Y[2]/radius)**4/(1-(Y[2]/radius)**2)
    return dict(cutoff_probe=c,stable_even_Y_coefficient=coefficient,
        paired_middle_minus_light_Y2_value=difference*coefficient,
        paired_middle_minus_light_raw_cotangent=difference*gradient,
        normalized_P0_eigenvalues=lam,normalized_P1=C,normalized_P2=B,
        normalized_eigenvectors=V,exact_sign_parity_retained=True,
        numerical_P0_gap=gap,numerical_P1_operator_norm=cn,numerical_P2_operator_norm=bn,
        finite_matrix_even_Y_circle_radius=radius,
        value_Y4_tail_analytic_estimate=6*exp1(c*gap/2)*tailfactor,
        analytic_estimate_inputs_outward_certified=False,
        source_statistics_or_relative_supertrace_coefficient_selected=False,
        physical_cutoff_or_completed_Pauli_selected=False,
        divided_difference_order=divided_difference_order)


def actual_cell_eight_q_heat_core(raw_fields,representation,*,length,repository):
    """Both source insertions and XiÃ¢â‚¬Â Xi on the actual interacting coefficient cell."""
    polynomial=actual_cell_heat_polynomial(raw_fields,representation,length=length);op=polynomial['operator']
    image=retained_eight_q_fermion_source_image(repository);labels=image['angular']['harmonic_labels'];E=image['angular']['derivative_matrices'];Xi=image['unit_radius_source_image'].reshape(8,20,18,18)
    frame=lepton_current_hilbert_representation();Y=np.diag(frame['family_Y']).real
    chart=current_face_source_jets(np.asarray(raw_fields)[:100]);scale=chart['T_b'].value/op['R4']
    families={}
    for family in (1,2):
        ids=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
        W=op['W'][np.ix_(ids,ids)];Omega=op['Omega_tau'][np.ix_(ids,ids)];B0=W+Omega
        P0=polynomial['temporal_factor_squared']*np.eye(6)+B0.conj().T@B0
        l0,V0=eigh(P0);contact=np.zeros((8,8,6),complex);shells={}
        alpha=frame['alpha'][:,ids][:,:,ids]
        for n in (1,3):
            hs=np.array([i for i,label in enumerate(labels) if label[0]==n]);count=len(hs)
            principal=-1j*sum(np.kron(E[a][np.ix_(hs,hs)],alpha[a]) for a in range(3))/op['R4']
            Bn=principal+np.kron(np.eye(count),B0)
            Pn=polynomial['temporal_factor_squared']*np.eye(6*count)+Bn.conj().T@Bn
            ln,Vn=eigh(Pn)
            X=scale*Xi[:,hs][:,:,ids][:,:,:,ids].reshape(8,6*count,6)
            F=np.einsum('ij,Ajk->Aik',Bn.conj().T,X)+np.einsum('Aij,jk->Aik',X,B0)
            G=np.einsum('Aki,Bkj->ABij',X.conj(),X);G+=G.transpose(1,0,2,3).copy()
            contact+=np.einsum('ij,ABjk,ki->ABi',V0.conj().T,G,V0)
            first=np.einsum('ij,Ajk,kl->Ail',Vn.conj().T,F,V0)
            shells[str(n)]=dict(eigenvalues=ln,first_jet_n0=first,
                all_intermediate_mode_count=len(ln),principal_hermiticity_residual=float(np.linalg.norm(principal-principal.conj().T)))
        families[str(family)]=dict(inherited_family=('heavy','middle','light')[family],fixed_Y=float(Y[family]),
            n0_eigenvalues=l0,mixed_contact_n0_spectral_diagonal=contact,intermediate_shells=shells)
    return dict(families=families,actual_primal_operator=op,source_normalization_Tb=chart['T_b'].value,
        source_normalization='explicit inherited8Q b directions; beta=Tb(currentR4)b; unit-Haar source pairing; no extra e,QNORM or statistical factor',
        complete_n1_n3_source_image_included=True,higher_shell_zero_scope='n0 two-insertion under this angular-homogeneous coefficient operator only',
        solved_induced_gauge_H_first_or_second_response_included=False,complete_native_or_Pauli=False)


def actual_cell_eight_q_cutoff_application(core,cutoff):
    """Contact minus both ordered cutoff insertions; source8x8 component only."""
    c=_positive_length(cutoff);rows={}
    for family,data in core['families'].items():
        l0=data['n0_eigenvalues'];contact=-np.einsum('i,ABi->AB',np.exp(-c*l0)/l0,data['mixed_contact_n0_spectral_diagonal'])
        ordered=np.zeros((8,8),complex)
        for shell in data['intermediate_shells'].values():
            f=shell['first_jet_n0'];_,weights=_ordered_cutoff_heat_lag(l0,shell['eigenvalues'],c)
            ordered+=np.einsum('Aji,Bji,ji->AB',f.conj(),f,weights)
        opposite=ordered.T.copy();total=contact+ordered+opposite
        rows[family]=dict(source_square_contact=contact,ordered_two_insertion=ordered,
            opposite_order_two_insertion=opposite,available_fixed_field_source_pair=total,
            source_pair_hermiticity_residual=float(np.linalg.norm(total-total.conj().T)),
            available_channel_trace=float(np.trace(total).real))
    return dict(cutoff_probe=c,families=rows,paired_middle_minus_light=None,
        paired_subtraction_scope='no subtraction of two nearby family outputs is claimed as a certified paired component',
        actual_same_background_induced_response_included=False,complete_native_or_Pauli=False)

"""Muon predecessor connection realization and pointwise event weight.

The rank-16 representation is supplied by the retained hybrid-bundle
producer. These functions do not select a quantum state, physical pole,
positive stratified bulk source lift, or full AE4 matching remainder.
"""
from fractions import Fraction
import numpy as np


def rank16_connection_attachment(multiplets):
    """Materialize the inherited unit-quaternion representation, not a fit.

    A doublet realizes e_a by -i*sigma_a; [e_a,e_b]=2 eps_abc e_c.
    The component-to-ordinary-Tr16 index is fixed by these supplied rows.
    The orientation convention is d+rho(omega)=d-i*T_a*W_hat^a,
    W_hat=2*omega. Q=T3+Y is the existing connection-coordinate source.
    """
    pauli=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    blocks=[]
    ys=[]
    labels=[]
    doublets=0
    for row in multiplets:
        dim=int(row['dimension'])
        # Explicit retained representation string, not a phenomenological
        # identification by a field's mass or observed charge.
        weak=int(row['weak_dimension'])
        if weak not in (1,2) or dim % weak:
            raise ValueError('retained weak singlets/doublets required')
        color=dim//weak
        block=np.zeros((3,dim,dim),complex)
        if weak==2:
            block=np.array([np.kron(np.eye(color),s/2) for s in pauli])
            doublets+=color
        blocks.append(block)
        ys.extend([Fraction(row['Y'])]*dim)
        labels.extend([str(row['name'])+':'+str(i) for i in range(dim)])
    if sum(len(b[0]) for b in blocks)!=16 or doublets!=4:
        raise ValueError('the supplied one-family rank16 carrier is required')
    T=np.zeros((3,16,16),complex)
    offset=0
    for block in blocks:
        dim=len(block[0]);T[:,offset:offset+dim,offset:offset+dim]=block
        offset+=dim
    Y=np.diag([float(y) for y in ys]).astype(complex)
    Q=T[2]+Y
    jmath=-2j*T
    t3_exact=[Fraction(float(x.real)) for x in np.diag(T[2])]
    qs=[t+y for t,y in zip(t3_exact,ys)]
    index=Fraction(2*doublets)
    traces=dict(I_jmath=str(index),Tr_T3_squared=str(sum(t*t for t in t3_exact)),
                Tr_Y_squared=str(sum(y*y for y in ys)),
                Tr_T3Y=str(sum(t*y for t,y in zip(t3_exact,ys))),
                Tr_Q_squared=str(sum(q*q for q in qs)))
    ratio=sum(q*q for q in qs)/index
    return dict(T=T,Y=Y,Q=Q,jmath=jmath,component_to_Tr16_index=index,
                K_Q_over_K_component=ratio,exact_traces=traces,labels=labels,
                exact_Q_diagonal=[str(q) for q in qs])


def eta_kinetic_weight(parent_fields):
    """Evaluate the retained f=chi target-map kinetic density on the cache.

    rho=2chi; f_normal=-shift_chi/N=-zeta_rho/(2nu).
    X=1/C_chi²+3cos²chi/A²+3sin²chi/B²-f_normal².
    The pole uses its analytic cancellation, not an artificial boundary.
    This is the v15.73 pointwise coefficient, not min_rho(L_eta).
    """
    rho=np.asarray(parent_fields['rho'],float)
    chi=rho/2
    A,B,C,nu,zeta=[np.asarray(parent_fields[k],float) for k in
                   ('A','B','C_rho','proper_lapse','proper_shift_rho')]
    if A.shape!=B.shape or A.shape[1]!=len(rho) or not np.all(nu>0):
        raise ValueError('matching retained parent fields required')
    plus=A/np.cos(chi)[None]
    sine=np.sin(chi)
    minus=np.empty_like(B)
    np.divide(B,sine[None],out=minus,where=sine[None]!=0)
    pole=sine==0
    # v=sin²(2chi)*v_poly vanishes at the regular pole, so the two
    # canceled angular radii agree there exactly in the retained ansatz.
    minus[:,pole]=plus[:,pole]
    normal=-zeta/(2*nu)
    X=1/(4*C*C)+3/(plus*plus)+3/(minus*minus)-normal*normal
    L=1+X**3
    return dict(X_eta=X,eta_normal_derivative=normal,L_eta=L,
                W_event=parent_fields['Lambda'][None]*L)


def matched_local_electric_density(parent_fields,attachment):
    """Reuse the computed geometric prefix; attach the derived trace once.

    Arrays remain per kappa1. Neither a numerical kappa1 nor an AE4 induced
    matching remainder is supplied. M, stiffness and source coordinates are
    not identified by this function.
    """
    factor=float(attachment['K_Q_over_K_component'])
    e=np.asarray(parent_fields['b_velocity_density_per_kappa1_cQ'])
    radial=np.asarray(parent_fields['b_radial_density_per_kappa1_cQ'])
    gram=np.asarray(parent_fields['actual_angular_Haar_Gram'])
    w=eta_kinetic_weight(parent_fields)
    plain=factor*e
    weighted=plain*w['L_eta']
    return dict(**w,E_b_Lambda_only_per_kappa1=plain,
                E_b_event_weighted_per_kappa1=weighted,
                E_b_event_weighted_matrix_per_kappa1=weighted[:,:,None,None]*gram,
                radial_density_event_weighted_per_kappa1=factor*radial*w['L_eta'],
                source_coordinate='beta along Q: (W3_hat,B_hat)=beta(1,1); A_Q=sqrt(2)*beta')

"""Literal natural-wall gauge/H action on the retained radial coefficient map.

The independent wall one-form values are internal unknowns.  They are not
the eight prescribed magnetic drive columns.  The original Maxwell curvature
contact, intrinsic Higgs first germ and every algebraic At row survive this
angular lift.  Continuation and a declared computational frame are applied
after the signed action is assembled; no positive ADM replacement is used.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve

from .muon_parent_maxwell_corrected_retarded import full_constant_angular_hessian
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_literal_euclidean_higgs_green import literal_proper_euclidean_forms
from .muon_piecewise_euclidean_action import _basis

VOLUME = 2*np.pi**2


def intrinsic_natural_wall_hessian(connection, H, Hdot, derivatives, *,
                                    metric_weights, lambda_H, nu_squared_action):
    """Realified analytic-transpose Hessian in (H, wall A20, Hdot).

    The off-shell DH*T contacts are separate from the two first-image
    products.  In particular the temporal cross depends on the actual Hdot.
    All angular columns use the same unit-Haar derivative matrices.
    """
    A,h,hd,E=[np.asarray(x,complex) for x in (connection,H,Hdot,derivatives)]
    w=np.asarray(metric_weights,complex);lam=float(lambda_H);nu=float(nu_squared_action)
    if (A.shape!=(5,4) or h.shape!=(4,) or hd.shape!=(4,) or E.ndim!=3
        or E.shape[0]!=3 or E.shape[1]!=E.shape[2] or w.shape!=(3,)
        or any(not np.isfinite(x).all() for x in (A,h,hd,E,w))
        or not np.isfinite([lam,nu]).all() or lam<=0 or nu<0):
        raise ValueError('complete intrinsic wall fields, first germ and action parameters required')
    n=E.shape[1];I=np.eye(n);T=higgs_u2_real_representation()['real_generators']
    O=np.einsum('fc,cij->fij',A,T);U=np.einsum('cij,j->ic',T,h)
    z=np.zeros((4*n,28*n),complex);vh=z.copy();vh[:,:4*n]=np.eye(4*n)
    vg=np.zeros((5,4*n,28*n),complex)
    for f in range(5):vg[f,:,4*n+f*4*n:4*n+(f+1)*4*n]=np.eye(4*n)
    vt=z.copy();vt[:,24*n:]=np.eye(4*n)
    cov=[]
    for j,f in enumerate((0,2,3,4)):
        ordinary=vt if f==0 else np.kron(np.eye(4),E[f-2])@vh
        cov.append(ordinary+np.kron(O[f],I)@vh+np.kron(U,I)@vg[f])
    DH=np.r_[ (hd+O[0]@h)[None], np.einsum('fij,j->fi',O[2:],h)]
    result=np.zeros((28*n,28*n),complex);contacts=np.zeros_like(result)
    for j,(f,weight) in enumerate(zip((0,2,3,4),(w[0],-w[1],-w[1],-w[1]))):
        result+=2*weight/VOLUME*cov[j].T@cov[j]
        # The second derivative of D_f H is (delta A_f) T delta H.
        cross=np.einsum('i,cij->jc',DH[j],T)
        X=np.kron(cross,I)
        contact=vh.T@X@vg[f]+vg[f].T@X.T@vh
        contacts+=2*weight/VOLUME*contact
    potential=lam*(8*np.outer(h,h)+4*(h@h-nu)*np.eye(4))
    result-=w[2]/VOLUME*vh.T@np.kron(potential,I)@vh
    return dict(hessian=result+contacts,off_shell_DH_contact=contacts,
        H_value_map=vh,gauge_wall_maps=vg,H_rate_map=vt,
        DH=DH,coordinate_order='Hreal4*nh, wall A20*nh, Hdot4*nh',
        scalar_cap_normalization='physical angular volume V divided by V² once',
        extra_material_Ar_advection_count=0)


def natural_wall_lorentz_forms(background, representation, derivatives, *,
        wall_connection,H,Hdot,metric_weights,lambda_H,nu_squared_action):
    """Full original M/B/K for four radial gauge unknowns and intrinsic H.

    Value order is gauge80*nh then H4*nh, before the explicit At permutation.
    The Maxwell background subtraction has no independent-field Hessian.
    It therefore changes no field row here and adds no reference energy twice.
    """
    E=np.asarray(derivatives,float);rep=representation
    if E.ndim!=3 or E.shape[0]!=3 or E.shape[1]!=E.shape[2] or not np.isfinite(E).all():
        raise ValueError('complete same angular derivative representation required')
    n=E.shape[1];gauge=np.asarray(rep['gauge_basis']);radial=np.asarray(rep['gauge_radial_basis'])
    quad=np.asarray(rep['radial_quadrature']);trace=np.asarray(rep['wall_trace_map'])
    A,At,Ar=[np.asarray(background[k]) for k in
        ('background_values','background_time_derivatives','background_radial_derivatives')]
    density=np.asarray(background['positive_two_form_densities'])
    if (gauge.shape!=(len(quad),80,1,5,4) or radial.shape!=gauge.shape
        or trace.shape!=(5,4,80) or any(a.shape!=(len(quad),5,4) for a in (A,At,Ar))
        or density.shape!=(len(quad),5) or any(not np.isrealobj(a) for a in (A,At,Ar,density))):
        raise ValueError('actual original four-radial gauge map and real action background required')
    ep=np.concatenate((np.eye(n)[None],E))
    # The explicit pair p,q is required: E_p^T E_q, not a sum over p.
    products=np.einsum('pkn,qkm->pqnm',ep,ep)
    size=84*n;M,B,K=[np.zeros((size,size)) for _ in range(3)]
    contacts=np.zeros_like(K)
    for r,w in enumerate(quad):
        row=full_constant_angular_hessian(A[r],At[r],Ar[r],density[r])
        tensor=row['tensor']
        P=np.kron(gauge[r,:,0].reshape(80,20).T,np.eye(n))
        Pr=np.kron(radial[r,:,0].reshape(80,20).T,np.eye(n))
        def block(i,j):
            return np.einsum('pqab,pqnm->anbm',tensor[i,j],products,optimize=True).reshape(20*n,20*n)
        M[:80*n,:80*n]+=w*(P.T@block(1,1)@P)
        B[:80*n,:80*n]+=w*(P.T@block(0,1)@P+Pr.T@block(2,1)@P)
        K[:80*n,:80*n]+=w*(P.T@block(0,0)@P+P.T@block(0,2)@Pr+
                            Pr.T@block(2,0)@P+Pr.T@block(2,2)@Pr)
        contacts[:80*n,:80*n]+=w*(P.T@np.kron(row['curvature_contact'],np.eye(n))@P)
    M*=MAXWELL_TO_CAP;B*=MAXWELL_TO_CAP;K*=MAXWELL_TO_CAP;contacts*=MAXWELL_TO_CAP
    scalar=intrinsic_natural_wall_hessian(wall_connection,H,Hdot,E,
        metric_weights=metric_weights,lambda_H=lambda_H,nu_squared_action=nu_squared_action)
    S=np.zeros((28*n,2*size),complex)
    S[:4*n,80*n:size]=np.eye(4*n)
    S[4*n:24*n,:80*n]=np.kron(trace.reshape(20,80),np.eye(n))
    S[24*n:,size+80*n:]=np.eye(4*n)
    SH=S.T@scalar['hessian']@S
    K=K.astype(complex)+SH[:size,:size];B=B.astype(complex)+SH[:size,size:];M=M.astype(complex)+SH[size:,size:]
    labels=rep['gauge_labels'];at=np.array([j for j,l in enumerate(labels) if l['field']=='A_tau'])
    dyn=np.array([j for j,l in enumerate(labels) if l['field']!='A_tau'])
    if len(at)!=16 or len(dyn)!=64:raise ValueError('the original full80 gauge coefficient map is required')
    ids=np.r_[(at[:,None]*n+np.arange(n)).ravel(),(dyn[:,None]*n+np.arange(n)).ravel(),np.arange(80*n,84*n)]
    frame=np.array([j for j,i in enumerate(dyn) if labels[i]['field']=='A_rho' and labels[i]['internal']==3])
    if len(frame)!=4:raise ValueError('four named original central Ar frame slices required')
    framed=(16*n+frame[:,None]*n+np.arange(n)).ravel()
    T=np.zeros((24*n,size),complex);T[:20*n,:80*n]=np.kron(trace.reshape(20,80),np.eye(n));T[20*n:,80*n:]=np.eye(4*n)
    return dict(forms=tuple(a[np.ix_(ids,ids)] for a in (M,B,K)),
        value_permutation=ids,At_count=16*n,central_radial_frame_indices=framed,
        original_wall_trace_map=T[:,ids],curvature_contact=contacts[np.ix_(ids,ids)],
        scalar_off_shell_DH_contact=S.T@scalar['off_shell_DH_contact']@S,
        scalar_gauge_cross_norm=float(np.linalg.norm(SH[:80*n,80*n:size])),
        natural_gauge_wall_trace_is_internal_unknown=True,
        magnetic_drive_columns_relabelled_internal=False,
        action_pairing='analytic transpose; original real (+---) scalar action',
        gauge_frame_is_complete_BRST_quotient=False)


def natural_wall_weak_inverse(nodes, point_forms, *, temporal_cells,
                              frame_indices, At_count):
    """Solve every action/Gauss row with named coordinate-frame reactions.

    No eigenvector removal or pseudoinverse is performed.  The finite initial
    trace is zero and the final action cotangent is natural; this separate-arm
    computational graph is not a physical birth transmission prescription.
    """
    q=len(nodes['weight']);callback=callable(point_forms)
    p=tuple(np.asarray(a,complex) for a in (point_forms(0)if callback else point_forms))
    if len(p)!=3 or (not callback and any(a.ndim!=3 or a.shape[0]!=q or a.shape[1]!=a.shape[2] for a in p)):
        raise ValueError('complete original continued wall action nodes required')
    d=p[0].shape[-1];n=int(temporal_cells)
    if type(temporal_cells) is not int or n<1 or any(a.shape!=((d,d)if callback else(q,d,d)) for a in p):
        raise ValueError('one explicit same FE domain required')
    f=np.asarray(frame_indices,int)
    if f.ndim!=1 or len(set(f.tolist()))!=len(f) or np.any((f<At_count)|(f>=d)):
        raise ValueError('named dynamic central radial frame indices required')
    K=np.zeros((n*d,n*d),complex)
    for iq,t in enumerate(nodes['proper_time']):
        row=point_forms(iq)if callback else tuple(a[iq] for a in p)
        M,B,C=literal_proper_euclidean_forms(row,nodes['N'][iq],At_count)['forms']
        basis=_basis(t,nodes['total_proper_clock'],n)
        for j,pj,dj in basis:
            for k,pk,dk in basis:
                K[j*d:(j+1)*d,k*d:(k+1)*d]+=float(nodes['weight'][iq])*(dj*dk*M+pj*dk*B+dj*pk*B.T+pj*pk*C)
    fi=(np.arange(n)[:,None]*d+f).ravel();C=np.eye(n*d)[fi]
    saddle=np.block([[K,C.T],[C,np.zeros((len(C),len(C)))]]);rhs=np.r_[np.eye(n*d),np.zeros((len(C),n*d))]
    sol=solve(saddle,rhs,assume_a='gen');X=sol[:n*d];reaction=sol[n*d:]
    original=K@X+C.T@reaction-np.eye(n*d)
    ati=(np.arange(n)[:,None]*d+np.arange(At_count)).ravel()
    return dict(original_Hessian=K,original_action_Green=X,frame_reactions=reaction,
        frame_rows=C,original_all_row_residual=original,original_Gauss_row_residual=original[ati],
        frame_residual=C@X,saddle_condition_number=float(np.linalg.cond(saddle)),
        original_row_residual_max=float(np.max(abs(original))),
        original_Gauss_row_residual_max=float(np.max(abs(original[ati]))),
        frame_residual_max=float(np.max(abs(C@X))),
        physical_BRST_or_birth_graph_or_P_strat_identified=False)


def natural_wall_current_maps(literal_vertices, wall_trace_map, lapse, harmonic_count):
    """Literal independent action currents in the Euclidean field chart.

    At_L=i*N*At_E,proper is applied to the field-coordinate map once.
    The analytic left current uses the same action generator; it is not
    silently replaced by its Hilbert adjoint.  The reflected coefficient
    branch remains the responsibility of the independently bound factor.
    """
    V=np.asarray(literal_vertices,complex);P=np.asarray(wall_trace_map,complex)
    n=int(harmonic_count);N=complex(lapse)
    if (type(harmonic_count)is not int or n<1 or V.shape!=(24,6,6)
        or P.ndim!=2 or P.shape[0]!=24*n or not np.isfinite(V).all()
        or not np.isfinite(P).all() or not np.isfinite(N) or N==0):
        raise ValueError('all24 literal action vertices and complete same wall field map required')
    P=P.copy();P[:4*n]*=1j*N
    right=np.einsum('cfs,chb->fhsb',V,P.reshape(24,n,-1),optimize=True).reshape(6*n,6,-1)
    left=np.einsum('csf,chb->sfhb',V,P.reshape(24,n,-1),optimize=True).reshape(6,6*n,-1)
    return dict(right=right,literal_left=left,Lorentz_field_image=P,
        temporal_connection_chart_count=1,left_generator_is_literal_action=True,
        angular_normalization='fermion phi_h=Y_h/sqrt(V); Haar-orthonormal real field coefficients')


def natural_wall_open_current(nodes, fermion_coefficients, fermion_form,
        field_inverse, trace_map, *, temporal_cells, family):
    """Apply one coupled original field Green across both open vertices."""
    from .muon_euclidean_angular_weak_action import euclidean_open_action_vertices
    n=int(temporal_cells);P=np.asarray(trace_map,complex)
    h=P.shape[0]//24;df=6*h;db=P.shape[1]
    if (type(temporal_cells)is not int or n<1 or P.shape!=(24*h,db)
        or field_inverse['original_action_Green'].shape!=(n*db,n*db)
        or fermion_form['K'].shape!=(n*df,n*df)):
        raise ValueError('same complete fermion/field FE domain and literal wall map required')
    R=np.zeros((n*df,6,n*db),complex);L=np.zeros((6,n*df,n*db),complex)
    for q,t in enumerate(nodes['proper_time']):
        V=euclidean_open_action_vertices(nodes['R'][q],nodes['N'][q],family=family)['vertices']
        maps=natural_wall_current_maps(V,P,nodes['N'][q],int(h))
        for j,pj,dj in _basis(t,nodes['total_proper_clock'],n):
            sf=slice(j*df,(j+1)*df);dual=dj*np.eye(df)+pj*fermion_coefficients['reflected'][q]
            for k,pk,dk in _basis(t,nodes['total_proper_clock'],n):
                sb=slice(k*db,(k+1)*db);w=float(nodes['weight'][q])
                R[sf,:,sb]+=w*pk*np.einsum('fg,gib->fib',dual,maps['right'],optimize=True)
                L[:,sf,sb]+=w*pj*pk*maps['literal_left']
    response=solve(fermion_form['K'],R.reshape(n*df,-1),assume_a='gen').reshape(R.shape)
    current=-np.einsum('ofb,fik,bk->oi',L,response,field_inverse['original_action_Green'],optimize=True)
    return dict(open_Gaussian_current=current,actual_A_sharp_numerator=R,
        literal_left_current=L,full_fermion_response=response,
        original_fermion_source_residual_max=float(np.max(abs(np.einsum('fg,gib->fib',fermion_form['K'],response)-R))),
        scalar_and_gauge_Greens_summed_separately=False,Gaussian_sign=-1,
        finite_c_mixed_P_cycle_or_normalized_soft_Pauli_identified=False)

"""Source-directed Green and radial residue of the original signed action.

The four named inherited radial frame rows are kept as reactions.  This
application does not promote that computational frame to BRST or identify
the frozen-frequency polynomial with the full causal quantum propagator.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eig,lu_factor,lu_solve


def coupled_radial_trace_application(coefficients,quotient_lift,joint_trace_map,
        radial_tangent,frame_rows,*,frequency):
    """Apply all24 joint currents and the correctly dualized radial source.

    deltaH=r*h, r^T r=1/2, so h=d^T deltaH with d=2r.  The
    canonical h propagator is4*r^T K^-1r, not r^T K^-1r.  Its
    inverse-frequency derivative is computed from the same joint solve.
    """
    if any(not np.isrealobj(np.asarray(x)) for x in
           (quotient_lift,joint_trace_map,radial_tangent,frame_rows)):
        raise ValueError('inherited trace, tangent and frame coordinate maps must be real')
    C,Q,T,r,F=(np.asarray(x,complex)for x in
        (coefficients,quotient_lift,joint_trace_map,radial_tangent,frame_rows))
    z=complex(frequency)
    if (C.shape!=(3,84,84)or Q.shape!=(84,80)or T.shape!=(24,84)
        or r.shape!=(84,)or F.shape!=(4,84)or not np.isfinite(z)
        or any(not np.isfinite(x).all()for x in(C,Q,T,r,F))):
        raise ValueError('complete original84 field symbol and inherited80 frame required')
    if (np.max(abs(Q.T@Q-np.eye(80)))>32*np.finfo(float).eps
        or np.max(abs(F@F.T-np.eye(4)))>32*np.finfo(float).eps
        or np.max(abs(F@Q))):
        raise ValueError('literal inherited coordinate restriction required')
    if np.any(r[:64])or np.any(r[68:])or not np.isclose((r.conj()@r).real,.5,rtol=2e-14,atol=0):
        raise ValueError('owned canonical radial tangent H/(sqrt2|H|) required')
    K=sum(C[k]*z**k for k in range(3));Kp=C[1]+2*z*C[2]
    # All traces are literal real-linear coefficient maps; analytic left
    # placement is transpose, not a new frequency-dependent adjoint.
    d=2*r;S=np.column_stack((d,T.T));A=Q.T@K@Q;B=Q.T@S
    fac=lu_factor(A);u=lu_solve(fac,B);full=Q@u
    uprime=lu_solve(fac,-(Q.T@Kp@Q)@u);fullprime=Q@uprime
    usecond=lu_solve(fac,-2*(Q.T@C[2]@Q)@u-2*(Q.T@Kp@Q)@uprime)
    fullsecond=Q@usecond
    contraction=S.T@full;derivative=S.T@fullprime
    second=S.T@fullsecond
    residual=K@full-S;reaction=F@residual
    # Independent field/Higgs Schur solve, with all gauge/At rows kept.
    hi=np.flatnonzero(np.any(Q[64:68]!=0,axis=0));gi=np.setdiff1d(np.arange(80),hi)
    gg=A[np.ix_(gi,gi)];hg=A[np.ix_(hi,gi)];gh=A[np.ix_(gi,hi)];hh=A[np.ix_(hi,hi)]
    gauge=lu_factor(gg);returned_h=hh-hg@lu_solve(gauge,gh)
    h=lu_solve(lu_factor(returned_h),B[hi]-hg@lu_solve(gauge,B[gi]))
    g=lu_solve(gauge,B[gi]-gh@h);schur=np.empty_like(u);schur[hi]=h;schur[gi]=g
    weak_r=.25*contraction[0,0];canonical=contraction[0,0]
    if canonical==0:raise ArithmeticError('canonical radial inverse derivative undefined at this numerical probe')
    return dict(frequency=np.array(z),full_field_response=full,
        full_field_frequency_response=fullprime,joint_source_matrix=S,
        full_field_frequency_second_response=fullsecond,
        radial_canonical_dual=d,canonical_radial_Green=canonical,
        canonical_radial_Green_frequency_derivative=derivative[0,0],
        canonical_radial_Green_frequency_second_derivative=second[0,0],
        canonical_radial_inverse=1/canonical,
        canonical_radial_inverse_frequency_derivative=-derivative[0,0]/canonical**2,
        canonical_radial_inverse_frequency_second_derivative=
            2*derivative[0,0]**2/canonical**3-second[0,0]/canonical**2,
        unnormalized_radial_weak_pairing=weak_r,
        canonical_to_weak_pairing_factor=4.,
        full_joint_source_Green=contraction,full_joint_source_frequency_derivative=derivative,
        full_joint_source_frequency_second_derivative=second,
        joint_wall_Green=contraction[1:,1:],joint_wall_frequency_derivative=derivative[1:,1:],
        radial_to_gauge_wall_Green=contraction[0,1:21],gauge_wall_to_radial_Green=contraction[1:21,0],
        scalar_returned_operator=returned_h,scalar_gauge_block=hg,
        Schur_full_response_difference=Q@(schur-u),
        original_field_equation_residual=residual,original_radial_frame_reactions=reaction,
        quotient_equation_residual=Q.T@residual,
        reaction_resolved_original_residual=residual-F.T@reaction,
        scalar_radial_restricted_quadratic_coefficient=r.T@C[2]@r,
        weak_matrix_condition_number=float(np.linalg.cond(A)),
        physical_frequency_or_pole_selected=False,physical_overlap_subtracted=False,
        exact_matching_role='original full signed field source/trace Green and its analytic frequency derivative in the inherited four-slice radial frame; canonical radial dual2r',
        physical_F2=None)


def coupled_radial_pole_application(coefficients,quotient_lift,joint_trace_map,
        radial_tangent,frame_rows):
    """All finite local poles and source residues of the same signed pencil.

    Generalized companion eigenvalues retain the algebraic A_t rows.
    Only exactly zero homogeneous beta entries are designated infinite;
    no angular, unstable or small-residue mode is removed.
    """
    checked=coupled_radial_trace_application(coefficients,quotient_lift,
        joint_trace_map,radial_tangent,frame_rows,frequency=1j)
    C=np.asarray(coefficients,complex);Q=np.asarray(quotient_lift,float)
    P=np.array([Q.T@c@Q for c in C]);n=P.shape[1]
    A=np.block([[np.zeros((n,n)),np.eye(n)],[-P[0],-P[1]]])
    B=np.block([[np.eye(n),np.zeros((n,n))],[np.zeros((n,n)),P[2]]])
    homogeneous,left,right=eig(A,B,left=True,right=True,homogeneous_eigvals=True)
    ids=np.flatnonzero(homogeneous[1]!=0)
    poles=homogeneous[0,ids]/homogeneous[1,ids]
    order=np.lexsort((poles.imag,poles.real));ids=ids[order];poles=poles[order]
    S=checked['joint_source_matrix'];sources=Q.T@S
    rr=[];lr=[];den=[];residues=[];right_defect=[];left_defect=[]
    scale=np.array([np.linalg.norm(p)for p in P])
    for j,z in zip(ids,poles):
        v=right[:n,j];l=left[n:,j].conj()
        K=sum(P[k]*z**k for k in range(3));kp=P[1]+2*z*P[2]
        derivative=l@kp@v
        if derivative==0:raise ArithmeticError('multiple or singular companion pole requires its complete cluster resolvent')
        rr.append(Q@v);lr.append(l@Q.T);den.append(derivative)
        residues.append(np.outer(sources.T@v,l@sources)/derivative)
        divisor=sum(scale[k]*abs(z)**k for k in range(3))
        right_defect.append(np.linalg.norm(K@v)/(np.linalg.norm(v)*divisor))
        left_defect.append(np.linalg.norm(l@K)/(np.linalg.norm(l)*divisor))
    residues=np.array(residues);radial=residues[:,0,0]
    probes=np.array([0,.5j,1j,2j]);values=[];defects=[]
    for z in probes:
        direct=coupled_radial_trace_application(coefficients,quotient_lift,
            joint_trace_map,radial_tangent,frame_rows,frequency=z)['canonical_radial_Green']
        modal=np.sum(radial/(z-poles));values.append(modal);defects.append(modal-direct)
    separation=np.min(np.where(np.eye(len(poles),dtype=bool),np.inf,
                        abs(poles[:,None]-poles[None,:])),axis=1)
    return dict(local_poles=poles,homogeneous_companion_eigenvalues=homogeneous,
        finite_companion_indices=ids,infinite_companion_indices=np.flatnonzero(homogeneous[1]==0),
        original_field_right_pole_vectors=np.array(rr),original_field_left_pole_rows=np.array(lr),
        pole_derivative_pairings=np.array(den),all_joint_source_pole_residues=residues,
        canonical_radial_frequency_residues=radial,
        canonical_radial_squared_pole_weights=2*poles*radial,
        right_polynomial_relative_residual=np.array(right_defect),
        left_polynomial_relative_residual=np.array(left_defect),
        nearest_pole_separation=separation,
        radial_modal_check_frequencies=probes,radial_modal_values=np.array(values),
        radial_modal_minus_direct=np.array(defects),
        finite_pole_count=len(poles),infinite_pole_count=2*n-len(poles),
        pole_scope='all local original signed-action poles in the inherited four central radial coordinate slices; no unstable mode or small residue deleted',
        physical_Higgs_pole_selected=False,physical_overlap_subtracted=False)


def radial_section_overlap_application(coefficients,radial_tangent,zero_application,probe_application):
    """Exact source-level subtraction of the local radial section reference.

    It exposes the static and kinetic matching contacts before a scalar
    loop.  The calibrated measured-pole reference additionally requires
    the action-to-physical unit map and its matched local counterterms.
    """
    C=np.asarray(coefficients,complex);r=np.asarray(radial_tangent,float)
    local=np.array([r.T@c@r for c in C]);z=complex(probe_application['frequency'])
    reference_inverse=sum(local[k]*z**k for k in range(3))
    if reference_inverse==0:raise ArithmeticError('radial reference is at a pole')
    actual=probe_application['canonical_radial_inverse']
    k0=zero_application['canonical_radial_inverse']
    k1=zero_application['canonical_radial_inverse_frequency_derivative']
    k2=.5*zero_application['canonical_radial_inverse_frequency_second_derivative']
    return dict(radial_section_reference_coefficients=local,
        radial_section_reference_Green=1/reference_inverse,
        full_minus_radial_section_Green=probe_application['canonical_radial_Green']-1/reference_inverse,
        static_inverse_matching_contact=k0-local[0],
        linear_inverse_matching_contact=k1-local[1],
        kinetic_inverse_matching_contact=k2-local[2],
        full_inverse_zero_frequency_coefficients=np.array([k0,k1,k2]),
        surviving_nonquadratic_inverse_response=actual-(k0+k1*z+k2*z*z),
        inverse_difference=actual-reference_inverse,
        matching_identity_residual=actual-reference_inverse-
            ((k0-local[0])+(k1-local[1])*z+(k2-local[2])*z*z+
             actual-(k0+k1*z+k2*z*z)),
        calibrated_reference_subtracted=False,
        calibrated_unit_matching_equation='m_mu_action=m_mu_GeV/E_kappa; M_h_action=M_h_GeV/E_kappa; matched scalar kinetic and pole counterterms fixed on the same current/domain',
        radial_scalar_loop_consumer='a_h[G_h]=-(Y_mu^2/2)/(8*pi^2)*integral_0^1 m_mu_action^2*x^2*(2-x)/(1-x)*G_h(i*m_mu_action*x/sqrt(1-x)) dx, only after the same Lorentz scalar restriction and contour/pole prescription are identified',
        physical_overlap_subtracted=False,physical_F2=None)

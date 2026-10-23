"""Literal zero-Cauchy response and its scalar matching continuation.

The frequency owner uses x(t)=exp(+i*z*t)x. Thus the retarded Laplace
transfer is C(-i*s), not C(+i*s). A unit positive action source produces
-C(-i*s)^-1; the inverse-action Green and that driven response are kept
distinct. Finite canonical endpoints supply an evaluated boundary term.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm,eigvals
from .muon_native_radial_overlap_tail import radial_detoured_soft_covector


def causal_radial_boundary_application(pencil,*,proper_length,laplace_rates):
    """Solve the original frozen action with initial x=p=0 before impulse.

    On the reduced coordinates, C(+i*w)=K+wJ-w²M. Literal Hamilton
    equations give M*x''=K*x-J*x'+S*delta(t) for the positive action
    source +x^T S. Hence v(0+)=M^-1 S and
      C(-i*s) X_T=-S+exp(-s*T)[M*v_T+(s*M+J)*x_T].
    This finite-endpoint identity is evaluated against the actual transfer.
    No finite natural/Dirichlet endpoint is substituted for zero Cauchy.
    """
    K,J,M,S=(np.asarray(pencil[k])for k in('K','J','M','source'))
    T=float(proper_length);rates=np.asarray(laplace_rates,complex);n=len(K)
    if T<=0 or not np.isfinite(T)or rates.ndim!=1 or not np.isfinite(rates).all():
        raise ValueError('positive actual proper interval and finite declared Laplace rates required')
    MK,MJ,MS=(np.linalg.solve(M,a)for a in(K,J,S))
    # Constant similarity only conditions the same canonical differential
    # action; all modes and sources are retained.
    scale=max(1.,np.sqrt(np.linalg.norm(MK,2)))
    F=np.block([[np.zeros((n,n)),scale*np.eye(n)],[MK/scale,-MJ]])
    initial=np.r_[np.zeros_like(S),MS/scale]
    U=expm(T*F);terminal=U@initial;xT=terminal[:n];vT=scale*terminal[n:]
    AtT=-np.linalg.solve(pencil['At_matrix'],pencil['At_constant_right']@xT-pencil['At_linear_right']@vT)
    records=[]
    for s in rates:
        # Integrate the semigroup source as an augmented exponential. This
        # evaluates the actual finite response without subtracting two
        # large inverse/endpoint terms when the interval is short.
        columns=S.shape[1]
        aug=np.zeros((2*n+columns,2*n+columns),complex)
        aug[:2*n,:2*n]=F-s*np.eye(2*n);aug[:2*n,2*n:]=initial
        integral=expm(T*aug)[:n,2*n:]
        D=K-s*J-s*s*M
        inverse=np.linalg.solve(D,S);retarded=-inverse
        boundary=np.exp(-s*T)*(M@vT+(s*M+J)@xT)
        endpoint_correction=np.linalg.solve(D,boundary)
        at=-np.linalg.solve(pencil['At_matrix'],
            (pencil['At_constant_right']-s*pencil['At_linear_right'])@integral-
            np.exp(-s*T)*pencil['At_linear_right']@xT)
        gauss=(pencil['At_matrix']@at+pencil['At_constant_right']@integral-
            pencil['At_linear_right']@(s*integral+np.exp(-s*T)*xT))
        # Negating the driven response converts to the inverse-action
        # Green used in the frozen scalar matching formula.
        records.append(dict(laplace_rate=np.array(s),finite_driven_response=integral,
            infinite_meromorphic_action_response=retarded,inverse_action_Green=inverse,
            finite_canonical_endpoint_source=boundary,finite_canonical_endpoint_response=endpoint_correction,
            finite_minus_meromorphic_action_response=integral-retarded,
            finite_boundary_identity_residual=integral-retarded-endpoint_correction,
            original_dynamic_equation_residual=D@integral+S-boundary,
            finite_At_response=at,original_Gauss_equation_residual=gauss,
            finite_radial_driven_pairing=S.T@integral,
            meromorphic_radial_inverse_action_pairing=S.T@inverse,
            finite_radial_inverse_action_pairing=-S.T@integral,
            radial_endpoint_response=S.T@endpoint_correction))
    growth=eigvals(F)
    return dict(proper_length=T,terminal_dynamic_field=xT,terminal_dynamic_velocity=vT,
        terminal_At_field=AtT,initial_dynamic_velocity_after_positive_action_impulse=MS,
        similarity_velocity_scale=scale,growth_exponents=growth,
        numerical_growth_abscissa=float(np.max(growth.real)),applications=records,
        causal_initial_condition='x=p=0 before source; positive action impulse gives v(0+)=M^-1S; all Gauss equations remain',
        proper_Fourier_owner='chronological_frequency_polynomial: v=+i*z*x',
        retarded_half_plane='Laplace s=i*z; Im(z)<-growth_abscissa for convergence',
        continued_original_frequency='z=-i*s',
        driven_action_source_and_inverse_action_Green_have_opposite_sign=True,
        finite_endpoint_is_actual_canonical_output=True,
        physical_native_quantum_covariance_or_Feynman_loop_identified=False,
        semigroup_and_matrix_production_error_is_not_interval_enclosed=True)


def causal_radial_soft_path_application(pencil,clusters,*,matched_mass_action,
        fixed_Y,kinetic_residue,reference_mass_squared,log_end=32.,order=24):
    """Apply C(-i*s)^-1 and the positive-frequency retarded boundary value.

    For the owner exp(+i*z*t), retarded boundary values are approached
    from Im(z)<0. Continue positive Lorentz frequency clockwise toward
    z=-i*s, staying on Re(z)>0: this is the UPPER s-plane bypass. The
    opposite independent branch is retained as the quantified difference.
    With unstable poles this meromorphic continuation is not an absolutely
    convergent Laplace transform below the growth abscissa, nor is it a
    Feynman covariance. The actual finite causal endpoint application above
    evaluates that distinction rather than assuming it away.
    """
    ret=dict(pencil);ret['J']=-pencil['J']
    app=radial_detoured_soft_covector(ret,clusters,matched_mass_action=matched_mass_action,
        fixed_Y=fixed_Y,kinetic_residue=kinetic_residue,reference_mass_squared=reference_mass_squared,
        log_end=log_end,order=order)
    return dict(application=app,
        applied_retarded_rotation_covector=app['upper_reached_covector'],
        applied_retarded_rotation_same_coordinate_subtraction=app['upper_same_coordinate_subtraction'],
        opposite_continuation_covector=app['lower_reached_covector'],
        causal_rotation_minus_opposite=app['upper_minus_lower'],
        causal_frequency_sign='C(-i*s); owner exp(+i*z*t)',
        applied_bypass='Im(s)>0, Re(z)>0, clockwise continuation of positive Lorentz frequency from retarded lower half-plane',
        adopted_Feynman_quantum_contour_identified=False,
        finite_causal_endpoint_correction_automatically_zero=False,
        physical_Pauli_identified=False)


def finite_causal_radial_covector(pencil,*,proper_length,matched_mass_action,
        fixed_Y,kinetic_residue,quadrature_order=8,log_edges=(0,8,16,24,32,40,48,64)):
    """Apply the same scalar matching functional to the actual finite IVP.

    The inverse-action kernel is minus the positive-source driven response,
    so the frozen local scalar numerator sign is unchanged. Finite causal
    Laplace integrals have no poles at any real positive s; actual final
    canonical contacts are kept inside each transfer. This is a causal
    action application, not a quantum covariance or physical Feynman loop.
    """
    m,Y,Z=map(float,(matched_mass_action,fixed_Y,kinetic_residue))
    edges=np.asarray(log_edges,float)
    if min(m,Y,Z)<=0 or np.any(np.diff(edges)<=0)or edges[0]!=0 or quadrature_order<4:
        raise ValueError('positive matching constants and resolved log partition required')
    gx,gw=np.polynomial.legendre.leggauss(quadrature_order)
    ys=np.concatenate([a+(b-a)*(gx+1)/2 for a,b in zip(edges[:-1],edges[1:])])
    weights=np.concatenate([gw*(b-a)/2 for a,b in zip(edges[:-1],edges[1:])])
    endpoint=np.exp(-ys);x=-np.expm1(-ys);s=m*x/np.sqrt(endpoint)
    a=causal_radial_boundary_application(pencil,proper_length=proper_length,laplace_rates=s)
    green=np.array([r['finite_radial_inverse_action_pairing']for r in a['applications']])
    values=-Y*Y/(16*np.pi**2)*m*m*x*x*(2-x)*Z*np.trace(green,axis1=1,axis2=2)/green.shape[1]
    return dict(log_nodes=ys,quadrature_weights=weights,proper_Laplace_rates=s,
        finite_causal_radial_Green_samples=green,finite_causal_covector_samples=values,
        finite_causal_covector=np.array(weights@values),
        original_dynamic_equation_residual_max=float(max(np.max(abs(r['original_dynamic_equation_residual']))for r in a['applications'])),
        original_Gauss_equation_residual_max=float(max(np.max(abs(r['original_Gauss_equation_residual']))for r in a['applications'])),
        quadrature_order=quadrature_order,log_end=float(edges[-1]),
        finite_canonical_endpoint_automatically_dropped=False,
        quantum_covariance_or_physical_Pauli_identified=False,
        quadrature_semigroup_and_y_gt_end_error_interval_enclosed=False)

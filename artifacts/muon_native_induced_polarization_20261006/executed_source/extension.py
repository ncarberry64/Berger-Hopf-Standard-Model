"""Saved muon source quotient and inherited parent weak-form coefficients.

This realizes a finite core of the existing calculation.  It does not select
an exterior domain, construct a physical parent extension, or replace AE4's
induced form by its local Maxwell expansion.
"""
from __future__ import annotations

import numpy as np


def independent_source_frame(inputs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Factor Phi(tau)=F(tau) C, keeping the f_R profile in F.

    The established angular representation has rank(P1+)=12 and
    W W*=(8/3)P1+.  Projected coordinate vectors choose a reproducible frame;
    no null direction is repaired with a diagonal regularization.
    """
    E = inputs['mixed__external_n0_test_frame_E0']
    W = inputs['mixed__Gamma_s_unit_source_fermion_boson_external'].reshape(20, 32)
    P = inputs['mixed__current_generated_projector_canonical20']
    P1 = P-E@E.conj().T
    columns = []
    pivots = []
    for i in range(20):
        vector = P1[:, i].copy()
        for _ in range(2):
            for old in columns:
                vector -= old*np.vdot(old, vector)
        norm = np.linalg.norm(vector)
        if norm > 1.e-10:
            columns.append(vector/norm)
            pivots.append(i)
    if len(columns) != 12:
        raise ValueError('Saved rank-12 generated angular representation changed.')
    U1 = np.column_stack(columns)
    U = np.column_stack((E, U1))
    C = np.zeros((16, 36), complex)
    C[:4, :4] = E.conj().T@E
    C[4:, 4:] = U1.conj().T@W
    # A right inverse only of the independent, well-conditioned 16-row map.
    J = np.linalg.solve(C@C.conj().T, C).conj().T
    f = inputs['frame__canonical_physical_volume_factor_nodes']
    F = np.broadcast_to(U, (len(f), 20, 16)).copy()
    F[:, :, 4:] *= f[:, None, None]
    return dict(angular_frame=U, generated_angular_frame=U1,
                coefficient_map=C, right_inverse=J,
                coefficient_row_projector=J@C,
                independent_profile_nodes=F,
                projected_coordinate_pivots=np.asarray(pivots),
                profile_power=np.r_[np.zeros(4, int), np.ones(12, int)])


def transport_cached_forms(frame: dict[str, np.ndarray],
                           cached: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Transport every supplied form, including connected contacts, once."""
    J = frame['right_inverse']
    names = {'M': 'child_M_test_Gram',
             'q_A': 'child_q_A_integrated',
             'q_AB': 'child_q_AB_integrated',
             'q_AB_connected': 'child_q_AB_connected_complement',
             'q_A_segments': 'child_q_A_segment_first_forms'}
    return {key: np.einsum('ki,...kl,lj->...ij', J.conj(), cached[name], J)
            for key, name in names.items()}


def transport_cached_source_actions(frame, source, inputs):
    """Apply the already evaluated full source map to independent profiles.

    The output still contains n2.  This operation is no claim about repeated
    source actions, a resolvent complement, or a physical muon state.
    """
    F = frame['independent_profile_nodes']
    f = inputs['frame__canonical_physical_volume_factor_nodes']
    return f[:, None, None, None]*np.einsum('aoi,tic->taoc',
                                            source['Xi_complete'], F)


def inherited_parent_principal_form(parent, weighted):
    """Project the retained Lorentz Maxwell principal form, without Wick rotation.

    e and r already contain K_Q/K_component=2/3 and the full pointwise weight.
    The +/- in M5_plus labels a stratum, not a positive-metric instruction.
    Returned densities are per inherited kappa1, not new Wilson coefficients.
    """
    e = weighted['E_b_event_weighted_per_kappa1']
    r = weighted['radial_density_event_weighted_per_kappa1']
    z = parent['proper_shift_rho']
    H = parent['boundary_H'][:, None]
    S = np.empty((*e.shape, 2, 2))
    S[..., 0, 0] = e
    S[..., 0, 1] = S[..., 1, 0] = -e*z
    S[..., 1, 1] = e*z*z-r
    # Fluxes conjugate to b_tau and b_rho, respectively.  The final column
    # retains the moving b-frame coefficient, D b=b_tau-z b_rho-H b/2.
    flux = np.empty((*e.shape, 2, 3))
    flux[..., :, :2] = S
    flux[..., 0, 2] = -.5*e*H
    flux[..., 1, 2] = .5*z*e*H
    return dict(lorentz_principal_tau_rho_per_kappa1=S,
                temporal_radial_flux_map_per_kappa1=flux,
                e=e, r=r, shift=z, boundary_H=H,
                determinant_exact_expression_samples=-e*r,
                proper_times=parent['proper_times'], rho=parent['rho'],
                angular_haar_Gram=parent['actual_angular_Haar_Gram'])


def weak_extension_contract():
    """Identify the unfilled temporal-face relation in inherited stationarity.

    A positive microscopic P does not prove positivity of the gauge Hessian.
    Therefore no additional positive-Maxwell realization is made a gate for
    the inherited causal stationary source extension.
    """
    return dict(
        prescription='fixed-trace stationary elimination inherited from v15.69/v15.73; no independent connection pullback recovered',
        primitive_equation='B5 A5=a4; q5_L(v,A5)+boundary_exterior_pairing(v,A5)=0 for owned B5 v=0, on the Gauss/BRST quotient',
        local_bilinear='integral e conjugate(D_tau v) D_tau b - r conjugate(v_rho) b_rho + angular/covariant/lower-order terms; D_tau=b_tau-zeta b_rho-H b/2',
        lifting_independence='For two trace liftings L,Lprime with difference in V0, solve q_eff(v,w)=-q_eff(v,L a); uniqueness on the owned gauge quotient gives L a+w=Lprime a+wprime. Coercivity/inf-sup and the full exterior realization must be established for that solve.',
        fixed_internal_trace_child_return='A term acting only on B5 A5=a4 has zero first variation for B5 v=0; it is not an extra free Robin load at the internal material trace.',
        free_interface_equation='H_pp x+H_pc c+B5_dagger lambda=0; H_cp x+H_cc^R c=0; B5 x=a4, with gauge rows and owned interface traces; use coupled solves, not alternating guessed lifts',
        source_differentiation='Differentiate the unreduced fixed-trace functional and this coupled system. Classical stationary extension does not require first knowing its induced boundary Hessian; the native bulk remainder may change the effective interior form.',
        name='weighted parent exterior temporal-face Calderon relation on the forced eight-mode traces',
        equation='q5_L_core(v,A5)+<Gamma_tau v,N_ext,Q^R Gamma_tau A5+j_ext,Q^R[a4 outside core]>=0, B5 A5=a4, B5 v=0; when no DtN graph chart exists use the affine Calderon trace/traction relation itself',
        input_space='tangential parent connection traces on the artificial proper-time faces of the saved 47-segment core, functions of rho and the eight saved angular lifts, plus the same source continuation; Gauss/BRST partners share the owned trace complex',
        output_space='dual exterior-outward temporal conormal traction in the actual Green pairing; core outward traction is Pi_n=n_tau*e(D_tau b) and matches the negative exterior traction, distinct from Pi_rho=-zeta Pi_tau-r b_rho',
        complement_scope='Restriction to forced eight-mode traces is a contracted output requirement, not invariance of that compression. Retain the connected owned exterior complement or its controlled Schur response. The saved n2 one-action contact result does not bound this resolvent/evolution complement.',
        producer='same weighted parent evolution on ae4_future_collapse_relative_boundary_domain.future_collapse_domain_contract; ae4_current_c2_canonical_stop_domain_bridge supplies the retained endpoint class, not the weighted rho-dependent eight-mode core-to-exterior response',
        consumer='zero-trace parent weak solve for E_plus_54_Q; its Xi5 actions and same-owner finite-E1 form jets',
        supplied_value=None,
        classification='unevaluated same-action response on the already owned future-directed domain, not a new free boundary datum; continuation/operator coefficients must produce it, and no physical extension solve with these coefficients has yet run',
        positive_native_matching='Later native promotion must match the action-owned pairing pullback B_owner(Z_alphaA,Z_betaB), Z_alphaA=dx^alpha wedge(T_b Y_A Q), and the bulk/domain/completion remainder. A metric-induced positive representation is conditional. P_strat=D_strat_dagger D_strat proves neither a sign-flipped Maxwell form nor positivity of its induced gauge Hessian. This is not an extra prerequisite for inherited causal stationarity.',
        cache_endpoint_promoted_to_physical_boundary=False,
        parent_extension_evaluated=False,
        interface_reset_Clifford_flux_residuals=None)

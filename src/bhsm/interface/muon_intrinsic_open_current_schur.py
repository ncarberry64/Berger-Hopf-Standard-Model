"""External current application of the reached scalar/fermion Green kernel.

The external domain is the retained tent, with complete constant/n1
angular fibers.  The internal b-squared image has already been integrated.
This applies the actual external positive-factor Green, including neutral
returns.  Its charged fiber is an algebraic current representation, not
an interacting Lorentz pole or a selected spin state.
"""
from __future__ import annotations

import numpy as np

from .muon_magnetic_mixed_green import _finite, family_fiber_indices
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation


def external_current_schur_application(factor, positive_form, charged, neutral):
    """Solve the complete current Green and its exact neutral Schur return.

    G=P^-1 A^dagger.  For a charged source J, the neutral right-hand side
    K^dagger A^dagger J participates before elimination; a charged block
    of A alone does not supply it.  This also returns the whole G, so an
    open insertion need not assume that the charged subspace is invariant.
    """
    A=_finite(factor,'actual external first-order factor')
    P=_finite(positive_form,'actual external positive form')
    J=_finite(charged,'complete charged current injection')
    K=_finite(neutral,'complete neutral current injection')
    if A.ndim!=2 or A.shape[0]!=A.shape[1] or P.shape!=A.shape:
        raise ValueError('same square actual external factor and positive form required')
    n=len(A)
    if J.ndim!=2 or K.ndim!=2 or J.shape[0]!=n or K.shape[0]!=n or J.shape[1]+K.shape[1]!=n:
        raise ValueError('charged and neutral injections must cover the complete external fiber')
    F=np.column_stack((J,K)); gram=F.conj().T@F
    defect=float(np.linalg.norm(gram-np.eye(n)))
    if defect>64*n*np.finfo(float).eps:
        raise ValueError('current injections must be the complete orthonormal fiber convention')
    hermitian_defect=float(np.linalg.norm(P-P.conj().T))
    if hermitian_defect>64*n*np.finfo(float).eps*np.linalg.norm(P):
        raise ValueError('actual external positive form must be Hermitian')
    minimum=float(np.linalg.eigvalsh(P)[0])
    if minimum<=0:raise ValueError('actual external positive form has no positive finite margin')
    G=np.linalg.solve(P,A.conj().T)
    Pcc=J.conj().T@P@J; Pcn=J.conj().T@P@K
    Pnc=K.conj().T@P@J; Pnn=K.conj().T@P@K
    rhs_c=J.conj().T@A.conj().T@J
    rhs_n=K.conj().T@A.conj().T@J
    neutral_coupling=np.linalg.solve(Pnn,Pnc)
    neutral_rhs=np.linalg.solve(Pnn,rhs_n)
    Schur=Pcc-Pcn@neutral_coupling
    charged_response=np.linalg.solve(Schur,rhs_c-Pcn@neutral_rhs)
    neutral_response=neutral_rhs-neutral_coupling@charged_response
    complete_response=J@charged_response+K@neutral_response
    isolated_charged_response=np.linalg.solve(Pcc,rhs_c)
    return dict(Green=G,charged_source_response=complete_response,
        charged_response=charged_response,neutral_response=neutral_response,
        charged_Schur_positive_form=Schur,neutral_right_hand_side=rhs_n,
        neutral_right_hand_side_return=Pcn@neutral_rhs,
        neutral_positive_form=Pnn,
        isolated_charged_response=isolated_charged_response,
        charged_response_difference_from_isolated=charged_response-isolated_charged_response,
        complete_response_difference_from_isolated=complete_response-J@isolated_charged_response,
        source_response_residual=P@complete_response-A.conj().T@J,
        full_Green_residual=P@G-A.conj().T,
        Schur_full_solve_difference=complete_response-G@J,
        current_Gram_defect=defect,positive_form_Hermiticity_defect=hermitian_defect,
        positive_form_minimum_eigenvalue=minimum,
        neutral_factor_source_leakage=K.conj().T@A.conj().T@J,
        interacting_Lorentz_pole_or_LSZ_residue_selected=False)


def _exact_shell_restriction(matrix,count,name):
    x=_finite(matrix,name)
    if x.ndim!=2 or x.shape[0]!=x.shape[1] or len(x)<count:
        raise ValueError('complete inherited angular '+name+' required')
    if np.any(x[:count,count:]) or np.any(x[count:,:count]):
        raise ValueError('actual angular shell is not exactly invariant in '+name)
    return x[:count,:count]


def source_image_external_current_application(data, forward_kernel, reverse_kernel, H, *, family):
    """Carry the actual open image through both complete external Greens.

    The forward image is n0 -> complete scalar n1, with all six Weyl
    components.  D=-G1 Sigma G0 is an explicitly unsigned Green-insertion
    application: it is the derivative for an added positive-factor Dyson
    kernel, without assigning a quantum self-energy sign to Sigma.
    All four charged/neutral internal placements are retained.  Measured
    free-pole masses and a Pauli projector are not inserted in this form.
    """
    ids=family_fiber_indices(family)
    h=_finite(H,'actual background Higgs doublet')
    injection=charged_dirac_injection(h,family=family)
    J0=injection['charged'][ids];K0=injection['neutral'][ids]
    J1=np.kron(np.eye(4),J0);K1=np.kron(np.eye(4),K0)
    A0=_exact_shell_restriction(data.get('A_even'),6,'n0 first-order factor')
    P0=_exact_shell_restriction(data.get('P_even'),6,'n0 positive form')
    A1=_exact_shell_restriction(data.get('A_odd'),24,'n1 first-order factor')
    P1=_exact_shell_restriction(data.get('P_odd'),24,'n1 positive form')
    S=_finite(forward_kernel,'actual enlarged forward open kernel')
    Sr=_finite(reverse_kernel,'actual enlarged reverse open kernel')
    if S.shape!=(3,24,6) or Sr.shape!=(3,6,24):
        raise ValueError('complete three magnetic axes and n1/n0 six-component open placements required')
    g0=external_current_schur_application(A0,P0,J0,K0)
    g1=external_current_schur_application(A1,P1,J1,K1)
    G0,G1=g0['Green'],g1['Green']
    D=-G1@S@G0;Dr=-G0@Sr@G1
    projections0={'charged':J0@J0.conj().T,'neutral':K0@K0.conj().T}
    projections1={'charged':J1@J1.conj().T,'neutral':K1@K1.conj().T}
    placements={};reverse_placements={}
    for left,Q1 in projections1.items():
        for right,Q0 in projections0.items():
            name=left+'_image_'+right+'_source'
            placements[name]=-J1.conj().T@G1@Q1@S@Q0@G0@J0
            reverse_placements[name]=-J0.conj().T@G0@Q0@Sr@Q1@G1@J1
    charged=J1.conj().T@D@J0
    charged_reverse=J0.conj().T@Dr@J1
    direct_charged=S@J0
    current_blocks={}
    for left,L in (('charged',J1),('neutral',K1)):
        for right,R in (('charged',J0),('neutral',K0)):
            current_blocks[left+'_image_'+right+'_source']=L.conj().T@S@R
    # This is the owned canonical/factor coefficient relation, not a Wick
    # continuation of a propagator.  W is Hermitian and Omega_tau is
    # anti-Hermitian.  The actual Lorentz canonical coefficient is
    # Hcan=W-i Omega_tau, while the positive factor coefficient is W+Omega_tau.
    W=(A0+A0.conj().T)/2;Omega_tau=(A0-A0.conj().T)/2
    Hcan=W-1j*Omega_tau
    charged_Hcan=J0.conj().T@Hcan@J0
    neutral_Hcan=K0.conj().T@Hcan@J0
    Y=lepton_current_hilbert_representation()['family_Y'][family,family].real
    mass=float(Y*np.linalg.norm(h))
    beta=retained_higgs_spin_charge_representation()['gamma_Dirac'][0]
    return dict(forward_full_Green_insertion=D,reverse_full_Green_insertion=Dr,
        forward_charged_current_insertion=charged,reverse_charged_current_insertion=charged_reverse,
        forward_charged_neutral_placements=placements,
        reverse_charged_neutral_placements=reverse_placements,
        forward_placement_sum_difference=sum(placements.values())-charged,
        reverse_placement_sum_difference=sum(reverse_placements.values())-charged_reverse,
        forward_open_current_blocks=current_blocks,
        forward_neutral_image_of_charged_source=K1.conj().T@direct_charged,
        external_n0=g0,external_n1=g1,
        charged_injection_n0=J0,neutral_injection_n0=K0,
        charged_injection_n1=J1,neutral_injection_n1=K1,
        actual_n0_canonical_Hamiltonian=Hcan,
        charged_n0_canonical_Hamiltonian=charged_Hcan,
        neutral_n0_canonical_source_leakage=neutral_Hcan,
        fixed_Y_background_mass_action=mass,
        charged_free_rest_symbol_difference=charged_Hcan-mass*beta,
        external_matching_application='complete positive-factor Schur current solve; actual canonical charged/neutral coefficients compared with the fixed-Y free rest symbol without replacing them',
        family=family,external_shell_restrictions_exact_in_stored_operator=True,
        scalar_internal_temporal_image_source_already_enlarged=True,
        all_neutral_returns_and_open_placements_retained=True,
        readout='unit-current charged-fiber Green insertion; no selected external spin state',
        signed_Dyson_identity='delta G=-G1 delta K G0; no quantum identification/sign assigned to the supplied mixed factor kernel',
        statistics_sign_or_Lorentz_self_energy_assigned=False,
        physical_external_pole_or_LSZ_matching_completed=False,
        finite_coercive_P_does_not_define_Lorentz_mass_shell=True,
        Pauli_tensor_or_measured_a_mu_inserted=False,
        physical_a_mu=None,physical_g_mu=None)

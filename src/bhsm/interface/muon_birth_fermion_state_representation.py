"""Fermion-state representation and same-event covariance transport at E1.

No Cauchy state is selected here. Finite matrix routines validate supplied
operands; the report derives covariance identities without choosing a state.
The frozen 57-row geometric reset is read, never recomputed.
"""
from __future__ import annotations

from pathlib import Path
import json
from math import isfinite
import numpy as np
import sympy as sp

from bhsm.interface.ae31_c2_fermion_hadamard_state_class import (
    cauchy_covariance_selection_contract,
    hadamard_class_existence_theorem,
    retained_state_selector_audit,
)
from bhsm.interface.ae31_c2_reset_hadamard_transport import (
    transport_self_dual_covariance,
    reset_hadamard_transport_theorem,
)

ROOT = Path(__file__).resolve().parents[3]
STARTING_HEAD = "1d94ce8ed77f8bfe1f13c729dd3d8885dbee5b69"
SCIENTIFIC_REFERENCE = "524ed90689bd5923c249bba2e699abf627e703cd"
ARTIFACT_DIRECTORY = "artifacts/muon_birth_fermion_state_representation_20261008"
NEXT_OPERAND = "C_C1_E1_MINUS_BHSM"


def _tolerance(value):
    value = float(value)
    if not isfinite(value) or value <= 0:
        raise ValueError("finite positive tolerance required")
    return value


def _matrix(value, name):
    result = np.asarray(value, dtype=complex)
    if (result.ndim != 2 or result.shape[0] == 0
            or result.shape[0] != result.shape[1]
            or not np.isfinite(result).all()):
        raise ValueError(f"{name} must be a finite nonempty square matrix")
    return result


def charge_conjugate_family_projector(particle_projector, *, tolerance=1e-10):
    """Double an already supplied family projector; derive no new family."""
    tol = _tolerance(tolerance)
    p = _matrix(particle_projector, "particle_projector")
    if (np.linalg.norm(p-p.conj().T, 2) > tol
            or np.linalg.norm(p@p-p, 2) > tol):
        raise ValueError("particle_projector must be Hermitian and idempotent")
    zero = np.zeros_like(p)
    return np.block([[p, zero], [zero, p.conj()]])


def transport_muon_covariance(covariance_event, reset_lift,
                              conjugation_event, conjugation_child,
                              family_sector, *, tolerance=1e-10):
    """Transport a supplied CAR covariance and compress its doubled sector.

    Q is Gamma invariant. The compressed self-dual identity is Q on the
    ambient space, or I on Ran(Q). Compression need not preserve purity
    unless the supplied covariance commutes with Q. A finite check cannot
    certify the continuum Hadamard wavefront condition.
    """
    tol = _tolerance(tolerance)
    c = _matrix(covariance_event, "covariance_event")
    u = _matrix(reset_lift, "reset_lift")
    ge = _matrix(conjugation_event, "conjugation_event")
    gc = _matrix(conjugation_child, "conjugation_child")
    q = _matrix(family_sector, "family_sector")
    if any(x.shape != c.shape for x in (u, ge, gc, q)):
        raise ValueError("all covariance transport dimensions must agree")
    if (np.linalg.norm(q-q.conj().T, 2) > tol
            or np.linalg.norm(q@q-q, 2) > tol):
        raise ValueError("family_sector must be a Hermitian projector")
    gamma_residual = max(
        np.linalg.norm(ge@q.conj()@ge.conj().T-q, 2),
        np.linalg.norm(gc@q.conj()@gc.conj().T-q, 2))
    if gamma_residual > tol:
        raise ValueError("family_sector must include its conjugate-charge partner")
    reset_residual = np.linalg.norm(u@q-q@u, 2)
    if reset_residual > tol:
        raise ValueError("reset must preserve the supplied family sector")
    result = transport_self_dual_covariance(c, u, ge, gc, tolerance=tol)
    child = result["covariance_child"]
    ce, cc = q@c@q, q@child@q
    restricted = max(
        np.linalg.norm(ce+ge@ce.conj()@ge.conj().T-q, 2),
        np.linalg.norm(cc+gc@cc.conj()@gc.conj().T-q, 2))
    result.update(
        muon_covariance_event=ce,
        muon_covariance_child=cc,
        family_sector=q.copy(),
        restricted_CAR_identity="Q on ambient space; I on Ran(Q)",
        restricted_CAR_residual=float(restricted),
        family_reset_commutator_residual=float(reset_residual),
        family_conjugation_residual=float(gamma_residual),
        family_covariance_commutator_residual=float(np.linalg.norm(c@q-q@c, 2)),
        family_transport_residual=float(np.linalg.norm(cc-u@ce@u.conj().T, 2)),
        sector_purity_residual=float(np.linalg.norm(cc@cc-cc, 2)),
        hadamard_class_certified_by_finite_matrix=False,
        physical_state_selected=False,
    )
    return result


def covariance_balance_defect(operator_event, oriented_child_operator,
                              reset_lift, *, tolerance=1e-10):
    """Return the pulled-back oriented kernel, without selecting any C.

    The child's normal sign is already included in oriented_child_operator.
    A zero kernel proves cancellation for every state, not just one test
    covariance. Numeric tolerance here is only a supplied-matrix diagnostic.
    """
    from bhsm.interface.action_extension_global_spin_reset_ae2 import validate_unitary
    tol = _tolerance(tolerance)
    a = _matrix(operator_event, "operator_event")
    b = _matrix(oriented_child_operator, "oriented_child_operator")
    u = validate_unitary(_matrix(reset_lift, "reset_lift"), tolerance=tol)
    if a.shape != b.shape or a.shape != u.shape:
        raise ValueError("balance operator dimensions must agree")
    defect = a+u.conj().T@b@u
    norm = float(np.linalg.norm(defect, 2))
    return dict(kernel_defect=defect, defect_norm=norm,
                supplied_matrix_zero_within_tolerance=norm <= tol,
                physical_E1_kernel_evaluated=False,
                condition="A_minus+U_R_dagger*A_plus_outward*U_R=0")


def occupation_difference_contraction(operator, delta_c_plus):
    """Finite ordered chi-dagger A chi STATE DIFFERENCE, not absolute Wick value.

    Retained conventions identify occupation N=I-C_plus, hence
    delta <chi-dagger A chi> = -Tr(A delta C_plus). Continuum local values
    still require their owned point-split distribution and subtraction.
    """
    a = _matrix(operator, "operator")
    dc = _matrix(delta_c_plus, "delta_c_plus")
    if a.shape != dc.shape:
        raise ValueError("contraction dimensions must agree")
    return complex(-np.trace(a@dc))


def symbolic_matched_balance():
    """Prove the pulled-back kernel vanishes for arbitrary matched operators."""
    a = sp.MatrixSymbol("A_minus", 2, 2)
    u = sp.MatrixSymbol("U_R", 2, 2)
    ui = sp.Inverse(u)  # U^-1=U-dagger by the retained unitary reset law.
    child = -u*a*ui
    defect = (a+ui*child*u).doit()
    return dict(
        proof="A_minus+U_R^-1*(-U_R*A_minus*U_R^-1)*U_R=0",
        pulled_back_kernel=str(defect),
        identically_zero=bool(defect == sp.ZeroMatrix(2, 2)),
        dimension_scope="Formal operator identity; displayed size2 is symbolic",
        covariance_chosen=False,
        smooth_covariance_completion_needed_for_matched_zero=False,
        actual_full_E1_stress_Noether_kernel_match_proved=False,
    )


def representation_report(root=ROOT):
    """Adjudicate the inherited quantum contract and preserve frozen values."""
    root = Path(root)
    directory = root/ARTIFACT_DIRECTORY
    owner = json.loads((directory/"owner_state_receipt.json").read_text())
    interface = json.loads((directory/"interface_cancellation_receipt.json").read_text())
    prior_path = root/"artifacts/muon_birth_transfer_value_20261008/run_1/transfer_value.json"
    prior = json.loads(prior_path.read_text())
    norms = prior["reset_residual_norm_or_component_enclosures"]
    if (prior["starting_head"] != "64b51a2cedb7be410251b3fb3c4f942cc148bcc4"
            or norms["l2_norm"] != 7.64107108345298e-15
            or norms["max_abs"] != 5.628594097932515e-15):
        raise ValueError("frozen geometric reset identity changed")
    theorem = reset_hadamard_transport_theorem()
    return dict(
        target="I_PHYS_MUON_BIRTH_TRANSFER_VALUE__FERMION_STATE_REPRESENTATION",
        starting_head=STARTING_HEAD,
        scientific_reference=SCIENTIFIC_REFERENCE,
        classification="CAR_COVARIANCE_REPRESENTATION_AND_STATE_UNIFORM_GREEN_MATCHING_DERIVED__SELECTED_UPSTREAM_COVARIANCE_UNEVALUATED",
        representation="SELF_DUAL_CAR_CAUCHY_COVARIANCE",
        previous_vector_stop_superseded=True,
        previous_vector_stop_scope="A vector API operand was mistakenly promoted to a universal physical state requirement; frozen numerical reset data remain valid.",
        nonzero_one_point_required=False,
        zero_one_point_implies_no_muon=False,
        external_one_particle_ray_selected=False,
        physical_covariance_selected=False,
        numerical_covariance=None,
        state_contract=cauchy_covariance_selection_contract(),
        state_class=hadamard_class_existence_theorem(),
        reset_covariance_transport=theorem,
        family_restriction=dict(
            frozen_projector=prior["muon_projector"],
            doubled_projector="Q_mu=Pi_mu tensor spin/carrier plus its conjugate-charge sector",
            covariance="C_mu=Q_mu*C*Q_mu",
            restricted_CAR="C_mu+Gamma*C_mu*Gamma=Q_mu; identity on Ran(Q_mu)",
            purity_condition="[C,Q_mu]=0 in addition to global purity",
            transport="C_mu,child=U_R*C_mu,event*U_R_dagger",
            localization_warning="T_enc C T_enc_dagger has CAR pairing T_enc T_enc_dagger, not automatic ambient I.",
        ),
        owner_state_receipt=owner,
        interface_cancellation_receipt=interface,
        exact_symbolic_matched_balance=symbolic_matched_balance(),
        owned_internal_EM_normal_flux=dict(
            status="DERIVED_STATE_UNIFORM_ZERO_ON_AE2_INTERNAL_GRAPH",
            charge="Q_l=-I_spin tensor I_family; conjugate charge on the doubled partner",
            derivation="The same Dirac local-phase variation gives a normal-current kernel proportional to J_Green Q_l in its fixed action convention. Both factors transport through U_R, with the opposite outward-normal sign. Thus A_Q,plus=-U_R A_Q,minus U_R_dagger and Delta_A_Q=0.",
            individual_current_magnitude_evaluated=False,
            full_sourced_event_Noether_balance_evaluated=False,
            generic_Green_helper_assigns_physical_current_prefactor=False,
        ),
        fixed_entire_sourced_native_heat=dict(
            status="STATE_INDEPENDENT_AT_FIXED_COMPLETE_SOURCED_FAMILY",
            reason="The retained HeatPencil consumes the supplied K, M, ell and source jets, with no covariance argument. At fixed entire sourced family its covariance variation is zero.",
            unknown_injection_domain_or_relative_completion_fixed=False,
            actual_physical_heat_evaluated=False,
            covariance_needed_for_this_fixed_contraction=False,
        ),
        convention=dict(
            AE31="W_plus=U_t*C_plus*U_s_dagger; W_minus=U_t*(I-C_plus)*U_s_dagger",
            external_body="N_ij=<chi_j_dagger*chi_i>; N=I-C_plus on ordinary particle block",
            ordered_bilinear="chi_dagger*A*chi -> Tr(A*N)",
            finite_relative_state_difference="delta <chi_dagger*A*chi>=-Tr(A*delta C_plus)",
            time_ordered="G_F=-i*U_t*(C_plus-theta(s-t)*I)*U_s_dagger",
            time_ordered_state_difference="delta G_F=-i*U_t*delta C_plus*U_s_dagger",
            retarded="G_R=-i*theta(t-s)*U_t*U_s_dagger; state independent for fixed free Dirac dynamics",
            absolute_local_Wick_prescription_owned=False,
            kinetic_action_half_is_quantum_doubling_half=False,
            blind_Tr_C_A_used=False,
        ),
        surviving_state_consumers=dict(
            two_point_state="W_plus itself changes by U_t delta C_plus U_s_dagger",
            exact_selected_muon_two_point_dependence="For a nonzero admissible smooth X supported in the muon/conjugate sector, delta W_mu=V_C2 U_R X U_R_dagger V_C2_dagger is nonzero by invertibility of the family-preserving Cauchy/reset maps. The retained fixed-history theorem admits distinct covariances within the same family.",
            cancellation_does_not_select_covariance="An oriented zero balance constrains the matched operators, not the choice of C; it vanishes for all these distinct covariances.",
            charged_lepton_mixed_response="M_eHS[C]=Tr(G_e[C]*V_HS*G_e[C]*V_intrinsic)",
            finite_response="Finite chi_f,fin[C] and Pi_fin[C] are not the universal Hadamard pole.",
            blanket_native_KKT_or_Pauli_dependence_claimed=False,
            full_birth_balance_covariance_dependence_proved=False,
            covariance_selection_sufficient_for_all_remaining_values=False,
        ),
        unified_state_operand=dict(
            id=NEXT_OPERAND,
            value_name="C_C1,E1^-^BHSM",
            type="Action-selected self-dual CAR Hadamard Cauchy covariance on the incoming C1 E1^- Hilbert space",
            value=None,
            producer="Retained BHSM physical state selector or equivalent boundary covariance/complex structure; none supplied.",
            consumer="C_E1plus=U_R*C_C1,E1minus*U_R_dagger; C_mu,Sigma=Q_mu*V_C2(Sigma,E1plus)*C_E1plus*V_C2_dagger*Q_mu",
            existing_current_C2_operand="C_mu,Sigma^BHSM=Pi_mu*C_Sigma^BHSM*Pi_mu with conjugate-charge restriction understood",
            independent_state_selection_problems=1,
            causal_reset_transport_selects_state=False,
            qualification="Needed for an actual selected matter covariance/two-point function and its smooth-state response, not for the already proved matched internal-seam zero.",
        ),
        selector_audit=retained_state_selector_audit(),
        frozen_geometric_reset=dict(
            path=str(prior_path.relative_to(root)).replace("\\","/"),
            norms=norms,
            newly_evaluated=False,
            full_physical_birth_claimed=False,
        ),
        physical_I_phys_passed=False,
        downstream={name: None for name in prior["downstream"]},
        claim_statuses=dict(
            DERIVED="CAR representation, unitary reset/restricted-family identities, exact Green and matched-kernel cancellation; upstream/current-C2 state unification",
            EVALUATED="Source/hash/contract audit and symbolic zero identity; no new physical C or field expectation",
            CONTROL_ONLY="Supplied finite matrices in focused API tests only; no control state is the BHSM covariance",
            UNEVALUATED="One selected upstream covariance, unmatched full-event stress/Noether values, full physical transfer and downstream",
            OWNER_DEFINITION_GAP="No action-owned covariance selector supplied; no new support/family/cutoff definition is requested",
        ),
    )

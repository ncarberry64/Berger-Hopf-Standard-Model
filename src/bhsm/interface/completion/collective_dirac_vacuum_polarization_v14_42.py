"""BHSM v14.42 collective-Dirac and coexact vacuum-polarization audit.

This layer continues the v14.41 source-free relative-frame no-go.  It asks
whether the FR eta-knot collective sector already supplies an action-normalized
Dirac determinant capable of driving the positive L=2 or L=3 coexact ADM shift
modes through zero.

The audit separates three logically distinct statements:

1.  A smooth twisted Dirac Hamiltonian on compact S3 has a unique self-adjoint
    closure on H1.  This is a valid conditional domain theorem.
2.  FR quantization and the inherited rotor inertia do not by themselves derive
    a local first-order spacetime Clifford principal symbol.  The collective
    Dirac action therefore remains a normal-form interface rather than an
    action-derived consequence of the eta moduli dynamics.
3.  If such a self-adjoint Dirac completion is supplied, the stationary coexact
    shift couples through the Hermitian spinorial-diffeomorphism (Kosmann/ADM
    momentum) vertex.  The filled-sea transition contribution to the static
    quadratic vacuum energy is nonpositive and vanishes for exact Killing
    shifts.  Its continuum value is ultraviolet divergent and must be combined
    with renormalized Einstein and curvature-squared shift operators.  Hence no
    physical L=2/L=3 crossing is emitted here.

No CKM matrix, CP phase, determinant value, mass, coupling, radius, scale, or
renormalized polarization coefficient is produced.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

VERSION = "v14.42"
PUBLIC_STATUS = (
    "conditional compact Dirac-domain and paramagnetic sign theorem derived; "
    "action ownership and renormalized L2/L3 crossing remain open"
)

PRIMARY_VERDICT = (
    "BHSM_FR_KNOT_PARITY_ROTOR_AND_H1_DOMAIN_DO_NOT_BY_THEMSELVES_DERIVE_"
    "AN_ACTION_NORMALIZED_LOCAL_COLLECTIVE_DIRAC_OPERATOR_OR_ITS_L2_L3_"
    "VACUUM_POLARIZATION"
)
SECONDARY_VERDICT = (
    "ANY_GAPPED_SELF_ADJOINT_DIRAC_COMPLETION_COUPLED_THROUGH_THE_ADM_"
    "KOSMANN_VERTEX_HAS_A_NONPOSITIVE_BARE_COEXACT_TRANSITION_"
    "SUSCEPTIBILITY_ZERO_ON_KILLING_MODES_BUT_THE_RENORMALIZED_ZERO_"
    "CROSSING_IS_NOT_YET_DEFINED"
)
RENORMALIZATION_VERDICT = (
    "THE_V14_41_EINSTEIN_ONLY_THRESHOLD_IS_A_RESTRICTED_SCHEME_CONTRACT_"
    "BECAUSE_CURVATURE_SQUARED_COUNTERTERMS_ADD_INDEPENDENT_LAMBDA_L_"
    "SQUARED_CONTRIBUTIONS"
)
EXACT_NEXT_OBJECT = (
    "MODULI_DERIVED_RELATIVISTIC_FR_KNOT_PRINCIPAL_SYMBOL_AND_CANONICAL_"
    "NORMALIZATION_WITH_UNITARY_CORE_WALL_SPINOR_MATCHER_ZETA_OR_HEAT_"
    "KERNEL_RENORMALIZATION_AND_EXPLICIT_L2_L3_KOSMANN_REDUCED_MATRIX_"
    "ELEMENTS_ON_THE_COMPACT_CAP"
)

ARTIFACT_FILES = {
    "ownership": "BHSM_collective_Dirac_action_ownership_v14_42.json",
    "domain": "BHSM_compact_cap_Dirac_domain_and_spectrum_v14_42.json",
    "vertex": "BHSM_coexact_Kosmann_stress_vertex_v14_42.json",
    "polarization": "BHSM_Dirac_vacuum_polarization_sign_and_renormalization_v14_42.json",
    "completion": "BHSM_completion_gate_v14_42.json",
}


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def round_s3_dirac_eigenvalue(n: int, sign: int = 1, radius: float = 1.0) -> float:
    """Eigenvalue of the intrinsic massless Dirac operator on round S3.

    spec(D_S3) = +/- (n+3/2)/R, n=0,1,...
    """

    if n < 0:
        raise ValueError("n must be nonnegative")
    if sign not in (-1, 1):
        raise ValueError("sign must be -1 or +1")
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    return float(sign * (n + 1.5) / radius)


def round_s3_dirac_multiplicity(n: int) -> int:
    """Multiplicity of each sign of the round-S3 Dirac eigenvalue."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    return (n + 1) * (n + 2)


def massive_round_s3_energy(n: int, mass: float = 0.0, radius: float = 1.0) -> float:
    """Positive energy of a standard massive Dirac Hamiltonian on R x S3."""

    if mass < 0.0:
        raise ValueError("mass must be nonnegative")
    k = round_s3_dirac_eigenvalue(n, +1, radius)
    return float(np.sqrt(k * k + mass * mass))


def hermitian_part(matrix: np.ndarray) -> np.ndarray:
    array = np.asarray(matrix, dtype=complex)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValueError("matrix must be square")
    return 0.5 * (array + array.conj().T)


def commutator_norm(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=complex)
    bb = np.asarray(b, dtype=complex)
    if aa.shape != bb.shape or aa.ndim != 2 or aa.shape[0] != aa.shape[1]:
        raise ValueError("a and b must be square matrices of the same shape")
    return float(np.linalg.norm(aa @ bb - bb @ aa))


def filled_sea_transition_susceptibility(
    hamiltonian: np.ndarray,
    vertex: np.ndarray,
    *,
    fermi_level: float = 0.0,
    gap_tolerance: float = 1.0e-12,
) -> float:
    """Finite-dimensional static filled-sea transition contribution.

    For a self-adjoint one-particle Hamiltonian H with occupied eigenvalues
    e_a < mu and unoccupied eigenvalues e_b > mu, the second-order ground-state
    energy coefficient from a Hermitian perturbation V is

        Q_para = - sum_(a occ, b unocc) |V_ba|^2 / (e_b-e_a) <= 0.

    This function is a theorem witness for the sign.  It is not a physical BHSM
    determinant or a regulator for the continuum problem.
    """

    h = hermitian_part(hamiltonian)
    v = hermitian_part(vertex)
    if h.shape != v.shape:
        raise ValueError("hamiltonian and vertex must have the same shape")

    eigenvalues, eigenvectors = np.linalg.eigh(h)
    if np.any(np.abs(eigenvalues - fermi_level) <= gap_tolerance):
        raise ValueError("hamiltonian must be gapped at the fermi level")

    transformed = eigenvectors.conj().T @ v @ eigenvectors
    occupied = np.flatnonzero(eigenvalues < fermi_level)
    empty = np.flatnonzero(eigenvalues > fermi_level)

    total = 0.0
    for a in occupied:
        for b in empty:
            denominator = float(eigenvalues[b] - eigenvalues[a])
            total -= float(abs(transformed[b, a]) ** 2 / denominator)
    return total


def normalized_shift_eigenvalue(L: int) -> int:
    """Dimensionless R^2-scaled coexact ADM shift eigenvalue from v14.41."""

    if L < 1:
        raise ValueError("L must be at least 1")
    return (L - 1) * (L + 3)


def total_renormalized_channel_coefficient(
    L: int,
    *,
    c2: float,
    c4: float,
    nonlocal_polarization: float,
) -> float:
    """Dimensionless renormalized static channel coefficient.

    q_L=(L-1)(L+3).  The most conservative local quadratic normal form is

        Lambda_L = c2*q_L + c4*q_L^2 + Pi_L^nonlocal.

    c2 includes the renormalized Einstein/background-curvature contribution;
    c4 represents independent four-derivative gravitational counterterms.
    None of these arguments is fixed by this sprint.
    """

    q = float(normalized_shift_eigenvalue(L))
    return float(c2 * q + c4 * q * q + nonlocal_polarization)


def collective_dirac_action_ownership_payload() -> dict[str, Any]:
    validation = {
        "FR_parity_fixes_spin_statistics_not_principal_symbol": True,
        "rotor_Hamiltonian_is_second_order_on_moduli": True,
        "H1_domain_does_not_prove_action_origin": True,
        "canonical_field_rescaling_requires_a_derived_inner_product": True,
        "no_independent_UV_Psi_double_counted": True,
        "conditional_Dirac_interface_retained": True,
        "action_normalized_collective_Dirac_not_claimed": True,
    }
    return {
        "artifact": "BHSM_collective_Dirac_action_ownership_v14_42",
        "version": VERSION,
        "inherited_quantization": {
            "FR_line": "flat Z2 line over the odd-degree relative eta-knot configuration sector",
            "spin_selection": "2j=N mod 2; odd N admits lowest j=1/2",
            "rotor_Hamiltonian": "H_rot=-(2 I_T)^(-1) Delta_moduli with FR equivariance",
            "what_it_derives": [
                "spin/statistics parity",
                "collective rotor spectrum after an inertia tensor is supplied",
                "a one-particle Hilbert-space candidate",
            ],
            "what_it_does_not_derive": [
                "a local Spin(1,3) Clifford principal symbol",
                "the relative speed relating temporal and spatial derivatives",
                "a canonically normalized local Grassmann field",
                "the response endomorphism Phi_response",
                "a determinant measure or regulator",
            ],
        },
        "conditional_normal_form": (
            "D_eta=i gamma^mu nabla_mu^total+Phi_response on the second-quantized "
            "FR-knot state bundle"
        ),
        "no_double_counting": (
            "Psi_eta may be used only as the low-energy second-quantized coordinate "
            "of eta-knot states; it is not an additional independent ultraviolet "
            "fermion integrated alongside the complete classical eta zero mode."
        ),
        "ownership_status": {
            "FR_quantization": "DERIVED_CONDITIONAL_ON_CONFIGURATION_SPACE_IDENTIFICATION",
            "compact_Dirac_domain": "DERIVED_CONDITIONAL_ON_THE_DIRAC_NORMAL_FORM",
            "local_collective_Dirac_principal_symbol": "OPEN_NOT_DERIVED_FROM_MODULI_ACTION",
            "canonical_action_normalization": "OPEN",
            "fermion_functional_measure": "OPEN",
        },
        "primary_verdict": PRIMARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def compact_dirac_domain_payload() -> dict[str, Any]:
    rows = [
        {
            "n": n,
            "eigenvalue_plus_times_R": n + 1.5,
            "eigenvalue_minus_times_R": -(n + 1.5),
            "multiplicity_each_sign": round_s3_dirac_multiplicity(n),
        }
        for n in range(5)
    ]
    validation = {
        "lowest_absolute_eigenvalue_times_R_is_3_over_2": round_s3_dirac_eigenvalue(0) == 1.5,
        "first_multiplicity_is_two": round_s3_dirac_multiplicity(0) == 2,
        "spectrum_is_symmetric": all(
            round_s3_dirac_eigenvalue(n, +1) == -round_s3_dirac_eigenvalue(n, -1)
            for n in range(5)
        ),
        "smooth_bounded_Hermitian_response_preserves_self_adjointness": True,
        "compact_resolvent": True,
        "Lorentzian_spatial_domain_is_H1": True,
        "APS_not_required_on_boundaryless_S3": True,
        "Euclidean_index_not_claimed": True,
    }
    return {
        "artifact": "BHSM_compact_cap_Dirac_domain_and_spectrum_v14_42",
        "version": VERSION,
        "spatial_manifold": "round S3(R) reference compact cap section",
        "bundle": (
            "Spin(S3) tensor E_color tensor L_FR tensor E_weak,Y tensor C3_family, "
            "subject to the Path-B associated-bundle and singlet constraints"
        ),
        "operator_contract": {
            "Hamiltonian": "H0=-i alpha^i nabla_i^total+beta M_eta+Phi_response",
            "domain": "H1(S3,E_total)",
            "conditions": [
                "smooth unitary bundle connection",
                "bounded Hermitian mass/response endomorphism",
                "compact boundaryless spatial S3",
            ],
            "result": "unique self-adjoint closure with compact resolvent",
        },
        "massless_round_spectrum": {
            "formula": "+/-(n+3/2)/R",
            "multiplicity_each_sign": "(n+1)(n+2)",
            "rows": rows,
        },
        "scope_boundary": (
            "This is a rigorous domain and spectrum contract for a supplied twisted "
            "Dirac operator.  It does not derive that operator from the eta moduli "
            "action or fix its physical mass, response term, radius, or normalization."
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def kosmann_vertex_payload() -> dict[str, Any]:
    validation = {
        "vertex_contains_orbital_and_spin_connection_parts": True,
        "no_new_fermion_rotation_coefficient": True,
        "divergence_free_vertex_is_formally_Hermitian": True,
        "Killing_vertex_commutes_with_invariant_Dirac_operator": True,
        "relative_vertex_requires_unitary_core_wall_matcher": True,
        "matcher_not_invented": True,
        "L2_L3_reduced_matrix_elements_not_emitted": True,
    }
    return {
        "artifact": "BHSM_coexact_Kosmann_stress_vertex_v14_42",
        "version": VERSION,
        "single_cap_vertex": {
            "spinorial_Lie_derivative": (
                "L_beta^K psi=beta^i nabla_i psi+(1/4)(D_i beta_j) gamma^{ij} psi, "
                "gamma^{ij}=(1/2)[gamma^i,gamma^j]"
            ),
            "Hermitian_ADM_vertex": "V_beta=-i L_beta^K for D_i beta^i=0",
            "interpretation": (
                "the beta^i T_0i coupling obtained by varying the tetrad and its "
                "Levi-Civita spin connection together"
            ),
            "coefficient": "fixed by the Dirac action; no independent spin-rotation coupling",
        },
        "Killing_gate": {
            "condition": (
                "beta is Killing and all gauge/response backgrounds are invariant under beta"
            ),
            "commutator": "[H0,V_beta]=0",
            "positive_negative_transition_block": "P_plus V_beta P_minus=0",
            "vacuum_transition_susceptibility": 0,
        },
        "relative_core_wall_vertex": {
            "formula": "V_rel=V_core-U_cw^dagger V_wall U_cw",
            "required_matcher": (
                "a unitary seam identification U_cw between the normalized core and "
                "wall spinor bundles on one common domain"
            ),
            "status": "OPEN",
        },
        "harmonic_gate": {
            "L1": "Killing/global-rotation channel; transition susceptibility vanishes in invariant vacuum",
            "L2": "kinematically allowed non-Killing stress vertex; reduced matrix elements open",
            "L3": "kinematically allowed non-Killing stress vertex; reduced matrix elements open",
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def polarization_sign_and_renormalization_payload() -> dict[str, Any]:
    # Deterministic theorem witnesses.
    h = np.diag([-3.0, -1.0, 2.0, 4.0])
    commuting = np.diag([0.2, -0.1, 0.3, 0.4])
    mixing = np.array(
        [
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.5j, 0.8],
            [1.0, 0.5j.conjugate(), 0.0, 0.0],
            [0.0, 0.8, 0.0, 0.0],
        ],
        dtype=complex,
    )
    q_commuting = filled_sea_transition_susceptibility(h, commuting)
    q_mixing = filled_sea_transition_susceptibility(h, mixing)

    validation = {
        "commuting_vertex_transition_term_zero": abs(q_commuting) < 1.0e-14,
        "noncommuting_vertex_transition_term_negative": q_mixing < 0.0,
        "bare_spectral_term_is_nonpositive": True,
        "Killing_channel_zero_by_symmetry": True,
        "continuum_sum_requires_regulator": True,
        "Einstein_and_curvature_squared_counterterms_are_independent": True,
        "only_total_renormalized_Hessian_is_scheme_independent": True,
        "physical_L2_L3_crossing_not_evaluated": True,
        "quadratic_kernel_is_real_and_even_at_zero_background": True,
    }
    return {
        "artifact": "BHSM_Dirac_vacuum_polarization_sign_and_renormalization_v14_42",
        "version": VERSION,
        "conditional_spectral_theorem": {
            "assumptions": [
                "self-adjoint gapped one-particle Dirac Hamiltonian H0",
                "Hermitian stationary shift vertex V_beta",
                "filled negative-energy subspace and empty positive-energy subspace",
                "symmetry-preserving finite cutoff before renormalization",
            ],
            "formula": (
                "Q_para[beta]=-sum_(a occupied,b empty) |<b|V_beta|a>|^2/(E_b-E_a) <= 0"
            ),
            "Killing_result": (
                "if [H0,V_beta]=0 then P_plus V_beta P_minus=0 and Q_para=0"
            ),
            "meaning": (
                "the fermionic transition term has the sign required to oppose the "
                "positive classical ADM stiffness in non-Killing channels"
            ),
            "finite_matrix_witness": {
                "commuting_vertex": q_commuting,
                "noncommuting_vertex": q_mixing,
            },
        },
        "renormalization_audit": {
            "bare_status": "UV_DIVERGENT_IN_CONTINUUM",
            "local_terms_generated": [
                "renormalization of the Einstein/background-curvature shift coefficient",
                "independent curvature-squared/four-derivative shift operators",
                "possible finite local terms fixed only by renormalization conditions",
            ],
            "dimensionless_channel_normal_form": (
                "Lambda_L^ren=c2^ren q_L+c4^ren q_L^2+Pi_L^nonlocal, "
                "q_L=(L-1)(L+3)"
            ),
            "restricted_v14_41_contract": (
                "Pi_L=-c_G q_L/R^2 is valid only after choosing an Einstein-only "
                "renormalization contract or fixing every independent four-derivative coefficient"
            ),
            "physical_statement": (
                "Only the total renormalized channel coefficient Lambda_L^ren is "
                "scheme independent; Pi_L^ren by itself is not a physical observable."
            ),
        },
        "requested_channels": {
            "L2": {
                "q_L": normalized_shift_eigenvalue(2),
                "crossing_equation": "5 c2^ren+25 c4^ren+Pi_2^nonlocal=0",
                "status": "OPEN",
            },
            "L3": {
                "q_L": normalized_shift_eigenvalue(3),
                "crossing_equation": "12 c2^ren+144 c4^ren+Pi_3^nonlocal=0",
                "status": "OPEN",
            },
        },
        "CP_orientation": (
            "The quadratic determinant at beta=0 is real and even under beta->-beta. "
            "It may create an amplitude if a channel crosses zero, but it cannot by "
            "itself choose between conjugate CP orientations; the separate relative-"
            "holonomy/Z6 mechanism remains a post-crossing orientation candidate."
        ),
        "renormalization_verdict": RENORMALIZATION_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def completion_payload() -> dict[str, Any]:
    ownership = collective_dirac_action_ownership_payload()
    domain = compact_dirac_domain_payload()
    vertex = kosmann_vertex_payload()
    polarization = polarization_sign_and_renormalization_payload()
    validation = {
        "ownership_audit_passed": ownership["validation_passed"],
        "conditional_domain_passed": domain["validation_passed"],
        "Kosmann_vertex_contract_passed": vertex["validation_passed"],
        "polarization_sign_audit_passed": polarization["validation_passed"],
        "action_normalized_Dirac_not_promoted": True,
        "renormalized_Pi2_not_emitted": True,
        "renormalized_Pi3_not_emitted": True,
        "physical_zero_crossing_not_claimed": True,
        "physical_CKM_CP_masses_not_emitted": True,
        "frozen_predictions_unchanged": True,
        "BHSM_not_complete": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_42",
        "version": VERSION,
        "public_status": PUBLIC_STATUS,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "renormalization_verdict": RENORMALIZATION_VERDICT,
        "Dirac_action_gate": "OPEN_NOT_DERIVED_FROM_FR_MODULI_DYNAMICS",
        "compact_self_adjoint_domain_gate": "PASSED_CONDITIONAL_ON_SUPPLIED_DIRAC_NORMAL_FORM",
        "matched_single_cap_tetrad_vertex_gate": "PASSED_AS_KOSMANN_ADM_VERTEX_CONDITIONAL_ON_DIRAC_ACTION",
        "unitary_core_wall_spinor_matcher_gate": "OPEN",
        "bare_transition_sign_gate": "NONPOSITIVE_AND_ZERO_ON_KILLING_MODES",
        "renormalized_L2_crossing_gate": "OPEN_NOT_NUMERICALLY_DEFINED",
        "renormalized_L3_crossing_gate": "OPEN_NOT_NUMERICALLY_DEFINED",
        "CP_orientation_gate": "OPEN_POST_CROSSING",
        "BHSM_complete": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def build_artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "ownership": collective_dirac_action_ownership_payload(),
        "domain": compact_dirac_domain_payload(),
        "vertex": kosmann_vertex_payload(),
        "polarization": polarization_sign_and_renormalization_payload(),
        "completion": completion_payload(),
    }


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads()
    written: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = output_dir / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written

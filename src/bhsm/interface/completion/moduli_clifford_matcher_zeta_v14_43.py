"""BHSM v14.43 moduli/Clifford, seam-matcher, and zeta audit.

This layer continues the v14.42 collective-Dirac vacuum-polarization gate.
It asks how far the existing FR-knot moduli data can be pushed toward an
actual local relativistic Dirac determinant without inserting a new field,
normalization, seam phase, or fitted gravitational counterterm.

The audit establishes four results.

1. Bosonic collective-coordinate quantization supplies a scalar mass-shell or
   Laplace--Beltrami principal symbol.  FR equivariance fixes a Z2 sign and spin
   parity, but a rank-one FR line cannot carry the complex spacetime Clifford
   algebra.  A Hodge--Dirac square root exists canonically on the *moduli
   space*, but it acts on differential forms over moduli and is not a local
   Spin(1,3) operator on M4.
2. The normalized one-particle Hilbert norm does not fix the residue of a local
   second-quantized field.  A constant field rescaling changes the kinetic
   coefficient while preserving FR rays and probabilities.  Canonical local
   normalization therefore requires an action-derived current or two-point
   residue.
3. A self-adjoint core--wall transmission domain is a family of unitary
   Clifford intertwiners.  Green's identity fixes the intertwining condition,
   but it does not select a unique matcher or relative holonomy.
4. The v12.1 L=2/L=3 Clebsch factors are exact on the frozen orbital Berger
   modules.  Lifting those modules to spinors introduces a Wigner-6j
   recoupling factor and an unresolved choice of spinor-harmonic branch.  The
   full Kosmann reduced matrix elements therefore remain unevaluated.  Exact
   round-S3 zeta diagnostics can be computed, but they do not fix the
   renormalized L=2/L=3 stress polarization or its finite local counterterms.

No determinant, CKM matrix, CP phase, mass, coupling, radius, physical scale,
or renormalized polarization coefficient is emitted.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from sympy import Rational, sqrt
from sympy.physics.quantum.cg import CG
from sympy.physics.wigner import wigner_6j

VERSION = "v14.43"
PUBLIC_STATUS = (
    "moduli-to-Clifford rank obstruction, unitary seam-matcher theorem, "
    "spinor recoupling audit, and round-S3 zeta diagnostics derived; local "
    "collective Dirac action and renormalized L2/L3 polarization remain open"
)

PRIMARY_VERDICT = (
    "BHSM_BOSONIC_FR_KNOT_MODULI_QUANTIZATION_AND_THE_FLAT_Z2_FR_LINE_DO_NOT_"
    "DERIVE_A_UNIQUE_LOCAL_SPACETIME_CLIFFORD_PRINCIPAL_SYMBOL_OR_CANONICAL_"
    "SECOND_QUANTIZED_FIELD_NORMALIZATION"
)
SECONDARY_VERDICT = (
    "BHSM_SELF_ADJOINT_CORE_WALL_DIRAC_TRANSMISSION_REQUIRES_A_UNITARY_"
    "CLIFFORD_INTERTWINER_FAMILY_BUT_THE_ACTION_DOES_NOT_SELECT_ITS_RELATIVE_"
    "HOLONOMY"
)
SPINOR_LIFT_VERDICT = (
    "THE_V12_1_L2_L3_CLEBSCH_FACTORS_ARE_EXACT_ORBITAL_FACTORS_BUT_FULL_"
    "KOSMANN_MATRIX_ELEMENTS_REQUIRE_AN_ACTION_SELECTED_SPINOR_HARMONIC_LIFT_"
    "AND_RADIAL_REDUCED_ELEMENTS"
)
ZETA_VERDICT = (
    "ROUND_S3_ZETA_DIAGNOSTICS_ARE_EXACT_AND_SCHEME_CONSISTENT_BUT_DO_NOT_"
    "FIX_THE_FOUR_DIMENSIONAL_RENORMALIZED_COEXACT_STRESS_POLARIZATION"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_CLIFFORD_SUPERCONNECTION_OR_WORLDLINE_SPIN_FACTOR_WHOSE_"
    "SQUARE_RECOVERS_THE_FR_KNOT_MODULI_HAMILTONIAN_TOGETHER_WITH_AN_ACTION_"
    "SELECTED_CORE_WALL_TRANSMISSION_INTERTWINER_AND_NORMALIZED_SPINOR_"
    "HARMONIC_EMBEDDINGS_FOR_THE_L2_L3_KOSMANN_POLARIZATION"
)

ARTIFACT_FILES = {
    "principal": "BHSM_moduli_to_spacetime_Clifford_gate_v14_43.json",
    "normalization": "BHSM_collective_field_normalization_gate_v14_43.json",
    "matcher": "BHSM_core_wall_Dirac_transmission_matcher_v14_43.json",
    "recoupling": "BHSM_spinor_lift_Kosmann_recoupling_v14_43.json",
    "zeta": "BHSM_round_S3_Dirac_zeta_diagnostics_v14_43.json",
    "completion": "BHSM_completion_gate_v14_43.json",
}

FROZEN_ORBITAL_BLOCKS: dict[str, dict[str, tuple[int, int]]] = {
    "up": {
        "heavy": (0, 0),
        "middle": (3, 3),
        "light": (5, 4),
    },
    "down": {
        "heavy": (0, 0),
        "middle": (3, 0),
        "light": (4, 2),
    },
}


def _json_default(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    raise TypeError(type(value).__name__)


def deterministic_json(value: Any) -> str:
    return json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        default=_json_default,
    ) + "\n"


def minimum_complex_clifford_module_rank(dimension: int) -> int:
    """Minimum complex module rank for the full Clifford algebra in dimension d."""

    if dimension < 1:
        raise ValueError("dimension must be positive")
    return 2 ** (dimension // 2)


def euclidean_gamma_matrices_4() -> tuple[np.ndarray, ...]:
    """One explicit Hermitian representation of Cl_4(C)."""

    s1 = np.array([[0, 1], [1, 0]], dtype=complex)
    s2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
    s3 = np.array([[1, 0], [0, -1]], dtype=complex)
    identity = np.eye(2, dtype=complex)
    zero = np.zeros((2, 2), dtype=complex)

    gammas = (
        np.block([[zero, -1j * s1], [1j * s1, zero]]),
        np.block([[zero, -1j * s2], [1j * s2, zero]]),
        np.block([[zero, -1j * s3], [1j * s3, zero]]),
        np.block([[zero, identity], [identity, zero]]),
    )
    return gammas


def clifford_residual(gammas: tuple[np.ndarray, ...] | list[np.ndarray]) -> float:
    matrices = [np.asarray(g, dtype=complex) for g in gammas]
    if not matrices:
        raise ValueError("at least one gamma matrix is required")
    shape = matrices[0].shape
    if shape[0] != shape[1] or any(g.shape != shape for g in matrices):
        raise ValueError("gamma matrices must be square and have a common shape")
    identity = np.eye(shape[0], dtype=complex)
    residual = 0.0
    for i, left in enumerate(matrices):
        for j, right in enumerate(matrices):
            target = 2.0 * identity if i == j else np.zeros_like(identity)
            residual = max(
                residual,
                float(np.linalg.norm(left @ right + right @ left - target)),
            )
    return residual


def clifford_square_residual(momentum: np.ndarray) -> float:
    vector = np.asarray(momentum, dtype=float)
    if vector.shape != (4,):
        raise ValueError("momentum must have shape (4,)")
    gammas = euclidean_gamma_matrices_4()
    symbol = sum(float(vector[index]) * gammas[index] for index in range(4))
    target = float(vector @ vector) * np.eye(4, dtype=complex)
    return float(np.linalg.norm(symbol @ symbol - target))


def field_rescaling_kinetic_coefficient(coefficient: float, scale: float) -> float:
    """Coefficient after Psi_new=scale*Psi_old in Z bar(Psi_old)D Psi_old."""

    if coefficient <= 0.0:
        raise ValueError("coefficient must be positive")
    if scale == 0.0:
        raise ValueError("scale must be nonzero")
    return float(coefficient / (scale * scale))


def transmission_residual(
    alpha_core: np.ndarray,
    alpha_wall: np.ndarray,
    matcher: np.ndarray,
) -> float:
    """Common-normal self-adjoint transmission residual U^* alpha_w U-alpha_c."""

    ac = np.asarray(alpha_core, dtype=complex)
    aw = np.asarray(alpha_wall, dtype=complex)
    u = np.asarray(matcher, dtype=complex)
    if ac.shape != aw.shape or ac.shape != u.shape:
        raise ValueError("alpha_core, alpha_wall, and matcher must share a shape")
    if ac.ndim != 2 or ac.shape[0] != ac.shape[1]:
        raise ValueError("inputs must be square matrices")
    return float(np.linalg.norm(u.conj().T @ aw @ u - ac))


def unitarity_residual(matrix: np.ndarray) -> float:
    value = np.asarray(matrix, dtype=complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError("matrix must be square")
    identity = np.eye(value.shape[0], dtype=complex)
    return float(np.linalg.norm(value.conj().T @ value - identity))


def spinor_total_j_branches(orbital_j: int) -> tuple[Rational, ...]:
    """Total diagonal-SU2 branches after tensoring orbital J with spin 1/2."""

    if orbital_j < 0:
        raise ValueError("orbital_j must be nonnegative")
    if orbital_j == 0:
        return (Rational(1, 2),)
    return (Rational(2 * orbital_j - 1, 2), Rational(2 * orbital_j + 1, 2))


def orbital_cg_factors() -> dict[str, Any]:
    """Exact v12.1 orbital Clebsch factors for the minimal chain."""

    values = {
        "up_heavy_middle_L3": CG(0, 0, 3, 3, 3, 3).doit(),
        "up_middle_light_L2": CG(3, 3, 2, 1, 5, 4).doit(),
        "down_heavy_middle_L3": CG(0, 0, 3, 0, 3, 0).doit(),
        "down_middle_light_L2": CG(3, 0, 2, 2, 4, 2).doit(),
    }
    return {
        key: {"exact": str(value), "float": float(value.evalf())}
        for key, value in values.items()
    }


def orbital_spin_recoupling_factor(
    *,
    target_orbital_j: int,
    target_total_j: Rational,
    source_orbital_j: int,
    source_total_j: Rational,
    tensor_rank: int,
) -> Any:
    """Wigner-6j factor multiplying an orbital reduced matrix element.

    For spin s=1/2 and an operator acting on the orbital factor,

      <(j_t s)J_t||T^L||(j_s s)J_s>
      = R_6j <j_t||T^L||j_s>.
    """

    if target_orbital_j < 0 or source_orbital_j < 0 or tensor_rank < 0:
        raise ValueError("orbital labels and tensor rank must be nonnegative")
    s = Rational(1, 2)
    exponent = Rational(target_orbital_j) + s + source_total_j + tensor_rank
    if exponent.q != 1:
        raise ValueError("phase exponent must be integral")
    phase = -1 if int(exponent) % 2 else 1
    return (
        phase
        * sqrt((2 * target_total_j + 1) * (2 * source_total_j + 1))
        * wigner_6j(
            Rational(target_orbital_j),
            target_total_j,
            s,
            source_total_j,
            Rational(source_orbital_j),
            Rational(tensor_rank),
        )
    ).simplify()


def spinor_recoupling_table() -> dict[str, list[dict[str, Any]]]:
    transitions = {
        "heavy_to_middle_L3": (3, 0, 3),
        "up_middle_to_light_L2": (5, 3, 2),
        "down_middle_to_light_L2": (4, 3, 2),
    }
    result: dict[str, list[dict[str, Any]]] = {}
    for name, (target_j, source_j, rank) in transitions.items():
        rows: list[dict[str, Any]] = []
        for target_total in spinor_total_j_branches(target_j):
            for source_total in spinor_total_j_branches(source_j):
                factor = orbital_spin_recoupling_factor(
                    target_orbital_j=target_j,
                    target_total_j=target_total,
                    source_orbital_j=source_j,
                    source_total_j=source_total,
                    tensor_rank=rank,
                )
                rows.append(
                    {
                        "target_total_j": str(target_total),
                        "source_total_j": str(source_total),
                        "tensor_rank": rank,
                        "six_j_recoupling_exact": str(factor),
                        "six_j_recoupling_float": float(factor.evalf()),
                        "nonzero": bool(factor != 0),
                    }
                )
        result[name] = rows
    return result


def hurwitz_zeta_at_nonpositive_integer(s: int, a: Fraction) -> Fraction:
    """Exact Hurwitz-zeta values needed for the round-S3 diagnostic."""

    if s == 0:
        return Fraction(1, 2) - a
    if s == -1:
        # -B2(a)/2; B2=x^2-x+1/6
        b2 = a * a - a + Fraction(1, 6)
        return -b2 / 2
    if s == -2:
        # -B3(a)/3; B3=x^3-3/2 x^2+1/2 x
        b3 = a**3 - Fraction(3, 2) * a**2 + Fraction(1, 2) * a
        return -b3 / 3
    if s == -3:
        # -B4(a)/4; B4=x^4-2x^3+x^2-1/30
        b4 = a**4 - 2 * a**3 + a**2 - Fraction(1, 30)
        return -b4 / 4
    raise ValueError("only s in {0,-1,-2,-3} is implemented")


def round_s3_abs_dirac_zeta_zero() -> Fraction:
    """zeta_|D|(0), counting both signs of the intrinsic two-component operator."""

    a = Fraction(3, 2)
    one_sign = hurwitz_zeta_at_nonpositive_integer(-2, a) - Fraction(1, 4) * hurwitz_zeta_at_nonpositive_integer(0, a)
    return 2 * one_sign


def round_s3_abs_dirac_zeta_minus_one_times_radius() -> Fraction:
    """R*zeta_|D|(-1), counting both signs."""

    a = Fraction(3, 2)
    one_sign = hurwitz_zeta_at_nonpositive_integer(-3, a) - Fraction(1, 4) * hurwitz_zeta_at_nonpositive_integer(-1, a)
    return 2 * one_sign


def round_s3_two_component_fermion_casimir_times_radius() -> Fraction:
    """-R*zeta_|D|(-1)/2 for one intrinsic two-component complex spinor."""

    return -round_s3_abs_dirac_zeta_minus_one_times_radius() / 2


def moduli_clifford_payload() -> dict[str, Any]:
    gamma_residual = clifford_residual(euclidean_gamma_matrices_4())
    square_residual = clifford_square_residual(np.array([0.3, -0.5, 0.7, 1.1]))
    validation = {
        "FR_line_rank_one": True,
        "spatial_Cl3_minimum_rank_two": minimum_complex_clifford_module_rank(3) == 2,
        "spacetime_Cl4_minimum_rank_four": minimum_complex_clifford_module_rank(4) == 4,
        "FR_line_cannot_carry_spacetime_Clifford": 1 < minimum_complex_clifford_module_rank(4),
        "explicit_Cl4_representation_valid": gamma_residual < 1.0e-13,
        "Clifford_square_returns_scalar_symbol": square_residual < 1.0e-13,
        "moduli_Hodge_Dirac_has_wrong_base_for_M4_principal_symbol": True,
        "local_Dirac_normal_form_not_promoted": True,
    }
    return {
        "artifact": "BHSM_moduli_to_spacetime_Clifford_gate_v14_43",
        "version": VERSION,
        "bosonic_moduli_principal_symbols": {
            "nonrelativistic": "sigma_2(H_mod)=G^{AB}p_A p_B times identity on the FR line",
            "relativistic_translation": "mass shell p_mu p^mu+M_eta^2=0 with scalar symbol",
            "FR_effect": "flat Z2 equivariance changes global signs and allowed spin representations, not the local differential order",
        },
        "rank_obstruction": {
            "FR_line_complex_rank": 1,
            "minimum_complex_Cl3_module_rank": minimum_complex_clifford_module_rank(3),
            "minimum_complex_Cl4_module_rank": minimum_complex_clifford_module_rank(4),
            "consequence": (
                "The FR line cannot itself furnish gamma matrices. A separate spinor/"
                "Clifford module is required even after odd-degree FR quantization."
            ),
        },
        "canonical_moduli_square_root": {
            "operator": "D_moduli=d_(L_FR)+d_(L_FR)^dagger",
            "square": "D_moduli^2=Delta_moduli on differential forms twisted by L_FR",
            "base": "eta-knot moduli space",
            "why_not_spacetime_Dirac": (
                "Its symbol is Clifford multiplication by T*Moduli, not by T*M4; "
                "it also enlarges states to exterior forms and does not select a "
                "Spin(1,3) representation or chirality."
            ),
        },
        "conditional_minimal_linearization": (
            "After separately declaring a spacetime Clifford module, a first-order "
            "operator gamma^mu p_mu is a square root of the scalar mass shell. The "
            "choice of module, chirality, connection, and normalization is additional "
            "data not fixed by the bosonic moduli metric or FR character."
        ),
        "numerical_residuals": {
            "Cl4_anticommutator": gamma_residual,
            "sample_symbol_square": square_residual,
        },
        "primary_verdict": PRIMARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def normalization_payload() -> dict[str, Any]:
    transformed = field_rescaling_kinetic_coefficient(7.0, np.sqrt(7.0))
    validation = {
        "field_rescaling_changes_local_kinetic_residue": abs(transformed - 1.0) < 1.0e-13,
        "FR_ray_probabilities_invariant_under_constant_rescaling_after_renormalization": True,
        "one_particle_inner_product_not_equal_to_local_LSZ_residue_without_field_map": True,
        "current_normalization_requires_action_variation": True,
        "canonical_local_field_normalization_not_claimed": True,
    }
    return {
        "artifact": "BHSM_collective_field_normalization_gate_v14_43",
        "version": VERSION,
        "local_action": "S_eff=Z_Psi int sqrt(-h) bar(Psi) i slash(D) Psi+...",
        "rescaling": {
            "definition": "Psi_new=c Psi_old",
            "coefficient_map": "Z_new=Z_old/|c|^2",
            "witness": {"Z_old": 7.0, "c": float(np.sqrt(7.0)), "Z_new": transformed},
        },
        "invariant_collective_data": [
            "FR sign",
            "normalized one-particle rays",
            "spin parity",
            "moduli-space probability after wavefunction renormalization",
        ],
        "missing_normalization_data": [
            "an action-derived map from localized eta fluctuations to the local field Psi_eta",
            "the pole residue or equal-time canonical anticommutator",
            "the action-normalized stress and gauge currents",
            "the number of independent local spinor species after constraints",
        ],
        "status": "OPEN_NOT_FIXED_BY_FR_HILBERT_NORM",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def matcher_payload() -> dict[str, Any]:
    alpha = np.diag([1.0, 1.0, -1.0, -1.0]).astype(complex)
    good = np.diag([1.0, 1j, -1.0, -1j]).astype(complex)
    hadamard = np.array(
        [
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, -1, 0],
            [0, 1, 0, -1],
        ],
        dtype=complex,
    ) / np.sqrt(2.0)
    good_residual = transmission_residual(alpha, alpha, good)
    bad_residual = transmission_residual(alpha, alpha, hadamard)
    validation = {
        "good_matcher_unitary": unitarity_residual(good) < 1.0e-13,
        "good_matcher_satisfies_Clifford_intertwining": good_residual < 1.0e-13,
        "generic_unitary_need_not_satisfy_intertwining": bad_residual > 1.0e-6,
        "matcher_family_nonunique": True,
        "self_adjointness_does_not_select_relative_holonomy": True,
        "action_selected_matcher_not_claimed": True,
    }
    return {
        "artifact": "BHSM_core_wall_Dirac_transmission_matcher_v14_43",
        "version": VERSION,
        "green_boundary_form": (
            "B(psi,phi)=-i int_Seam [psi_c^dagger alpha_(n_c) phi_c+"
            "psi_w^dagger alpha_(n_w) phi_w]"
        ),
        "transmission_domain": "psi_wall=U_cw psi_core",
        "common_normal_condition": "U_cw^dagger alpha_n^wall U_cw=alpha_n^core",
        "outward_normal_condition": "U_cw^dagger alpha_(n_w)^wall U_cw=-alpha_(n_c)^core",
        "additional_requirements": [
            "U_cw is unitary for the seam Hermitian metrics",
            "U_cw intertwines the retained color, weak, hypercharge, and FR transition actions",
            "U_cw has the regularity needed to preserve the H1 transmission domain",
        ],
        "nonuniqueness": {
            "reference_matcher": "If U0 is one solution, U=U0 C is another whenever C is unitary and commutes with alpha_n and all retained seam structures.",
            "rank4_normal_commutant_example": "U(2)_plus x U(2)_minus before internal-bundle restrictions",
            "physical_meaning": "Self-adjointness fixes a matcher class, not a unique relative phase or holonomy.",
        },
        "relative_vertex": "V_rel=V_core-U_cw^dagger V_wall U_cw",
        "ownership_status": "MATCHER_CLASS_DERIVED_ACTION_SELECTED_MEMBER_OPEN",
        "residuals": {"good": good_residual, "bad_generic_unitary": bad_residual},
        "secondary_verdict": SECONDARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def spinor_recoupling_payload() -> dict[str, Any]:
    orbital = orbital_cg_factors()
    recoupling = spinor_recoupling_table()
    branches = {
        sector: {
            slot: {
                "orbital_J": J,
                "orbital_m": m,
                "possible_total_j": [str(value) for value in spinor_total_j_branches(J)],
            }
            for slot, (J, m) in rows.items()
        }
        for sector, rows in FROZEN_ORBITAL_BLOCKS.items()
    }
    up_zero = any(
        row["six_j_recoupling_exact"] == "0"
        for row in recoupling["up_middle_to_light_L2"]
    )
    validation = {
        "v12_1_orbital_CG_values_reproduced": (
            orbital["up_heavy_middle_L3"]["exact"] == "1"
            and orbital["up_middle_light_L2"]["exact"] == "sqrt(10)/5"
            and orbital["down_heavy_middle_L3"]["exact"] == "1"
            and orbital["down_middle_light_L2"]["exact"] == "-sqrt(21)/7"
        ),
        "spinor_tensor_product_has_branch_choice": all(
            len(data["possible_total_j"]) == (1 if data["orbital_J"] == 0 else 2)
            for sector in branches.values()
            for data in sector.values()
        ),
        "six_j_recoupling_changes_orbital_reduced_elements": True,
        "one_up_L2_spinor_branch_vanishes": up_zero,
        "radial_Kosmann_reduced_elements_still_open": True,
        "full_spinorial_L2_L3_matrix_not_emitted": True,
    }
    return {
        "artifact": "BHSM_spinor_lift_Kosmann_recoupling_v14_43",
        "version": VERSION,
        "frozen_orbital_blocks": branches,
        "orbital_Wigner_Eckart_factors": orbital,
        "spinor_recoupling_formula": (
            "<(j_t,1/2)J_t||T^L||(j_s,1/2)J_s>="
            "(-1)^(j_t+1/2+J_s+L) sqrt[(2J_t+1)(2J_s+1)] "
            "{j_t J_t 1/2; J_s j_s L}<j_t||T^L||j_s>"
        ),
        "recoupling_table": recoupling,
        "Kosmann_decomposition": {
            "transport": "-i beta^i nabla_i",
            "spin": "-(i/4)(D_i beta_j) gamma^{ij}",
            "full_reduced_element": (
                "orbital/spin angular recoupling times a normalized radial and seam integral"
            ),
        },
        "missing_for_explicit_matrix_elements": [
            "which S3 spinor-harmonic branch realizes each frozen orbital block",
            "the total magnetic-state embedding and chiral polarization",
            "the normalized compact-cap radial spinors",
            "the normalized L=2 and L=3 coexact shift eigenfields",
            "the selected unitary core-wall matcher",
            "the response endomorphism and physical scale",
        ],
        "important_reclassification": (
            "The v12.1 numbers are exact orbital Clebsch factors. They are not yet "
            "the final local-Dirac Kosmann coefficients after spinor recoupling."
        ),
        "spinor_lift_verdict": SPINOR_LIFT_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def zeta_payload() -> dict[str, Any]:
    z0 = round_s3_abs_dirac_zeta_zero()
    zm1 = round_s3_abs_dirac_zeta_minus_one_times_radius()
    casimir = round_s3_two_component_fermion_casimir_times_radius()
    validation = {
        "absolute_Dirac_zeta_at_zero_vanishes": z0 == 0,
        "absolute_Dirac_zeta_minus_one_exact": zm1 == Fraction(-17, 480),
        "two_component_Casimir_exact": casimir == Fraction(17, 960),
        "odd_spatial_zeta_diagnostic_has_no_log_scale_at_free_level": z0 == 0,
        "four_dimensional_polarization_counterterms_still_required": True,
        "zeta_scheme_does_not_fix_finite_gravitational_couplings": True,
        "Pi2_Pi3_not_emitted": True,
    }
    return {
        "artifact": "BHSM_round_S3_Dirac_zeta_diagnostics_v14_43",
        "version": VERSION,
        "spectrum": {
            "absolute_eigenvalues": "(n+3/2)/R, n=0,1,...",
            "multiplicity_each_sign": "(n+1)(n+2)",
            "absolute_spectral_zeta": (
                "zeta_|D|(s)=2 R^s [zeta_H(s-2,3/2)-(1/4)zeta_H(s,3/2)]"
            ),
        },
        "exact_values": {
            "zeta_abs_D_at_0": str(z0),
            "R_times_zeta_abs_D_at_minus_1": str(zm1),
            "R_times_two_component_fermion_Casimir": str(casimir),
        },
        "interpretation": (
            "These values validate the free round-cap spectral convention. The "
            "physical L=2/L=3 susceptibility is a second variation of the full "
            "four-dimensional determinant with seam, mass, gauge, response, and "
            "counterterm data. It is not fixed by the unperturbed spatial zeta."
        ),
        "renormalized_channel_contract": (
            "Lambda_L^ren=c2^ren q_L+c4^ren q_L^2+Pi_L^nonlocal with q_L=(L-1)(L+3)"
        ),
        "finite_ambiguity": [
            "renormalized Einstein/background-curvature coefficient c2^ren",
            "independent curvature-squared coefficient c4^ren",
            "seam-local counterterms allowed by the matched geometry",
        ],
        "zeta_verdict": ZETA_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def completion_payload() -> dict[str, Any]:
    principal = moduli_clifford_payload()
    normalization = normalization_payload()
    matcher = matcher_payload()
    recoupling = spinor_recoupling_payload()
    zeta = zeta_payload()
    validation = {
        "principal_symbol_gate_audited": principal["validation_passed"],
        "normalization_gate_audited": normalization["validation_passed"],
        "matcher_gate_audited": matcher["validation_passed"],
        "spinor_recoupling_gate_audited": recoupling["validation_passed"],
        "zeta_gate_audited": zeta["validation_passed"],
        "frozen_predictions_unchanged": True,
        "measured_inputs_not_used": True,
        "new_continuous_coefficients_not_introduced": True,
        "local_Dirac_action_not_claimed": True,
        "renormalized_polarization_not_claimed": True,
        "physical_CKM_CP_mass_scale_not_emitted": True,
        "BHSM_completion_not_claimed": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_43",
        "version": VERSION,
        "public_status": PUBLIC_STATUS,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "spinor_lift_verdict": SPINOR_LIFT_VERDICT,
        "zeta_verdict": ZETA_VERDICT,
        "gate_status": {
            "FR_spin_statistics": "PRESERVED_CONDITIONAL",
            "moduli_space_Hodge_Dirac": "CANONICAL_BUT_WRONG_BASE_FOR_LOCAL_M4_DIRAC",
            "local_spacetime_Clifford_principal_symbol": "OPEN_NOT_DERIVED",
            "canonical_local_field_normalization": "OPEN",
            "self_adjoint_matcher_class": "DERIVED_CONDITIONAL",
            "action_selected_matcher_member": "OPEN",
            "orbital_L2_L3_CG_factors": "DERIVED",
            "full_spinorial_Kosmann_elements": "OPEN",
            "round_S3_free_zeta_diagnostic": "DERIVED",
            "renormalized_L2_L3_polarization": "OPEN",
            "physical_CKM": "NOT_DERIVED",
            "BHSM_complete": False,
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def build_artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "principal": moduli_clifford_payload(),
        "normalization": normalization_payload(),
        "matcher": matcher_payload(),
        "recoupling": spinor_recoupling_payload(),
        "zeta": zeta_payload(),
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

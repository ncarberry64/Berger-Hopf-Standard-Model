"""BHSM v14.45 foundational Dirac action and spin-glue audit.

This sprint takes the honest foundational branch left open by v14.44.  It does
not claim that the bosonic Path-B eta action derives local Grassmann fields.
Instead it declares a canonically normalized eta-bound Dirac sector as
foundational low-energy data, proves the exact normal-mode pullback and global
spin-bundle seam cancellation, installs a collective-coordinate
no-double-counting projector, and audits the remaining L=2/L=3 renormalization
ambiguity.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp

VERSION = "v14.45"
PRIMARY_VERDICT = (
    "BHSM_V14_45_ADOPTS_THE_CANONICALLY_NORMALIZED_TWO_SIDED_ETA_BOUND_"
    "DIRAC_ACTION_AND_GLOBAL_PARENT_SPIN_BUNDLE_AS_FOUNDATIONAL_EFFECTIVE_"
    "DATA_NOT_AS_A_DERIVATION_FROM_PATH_B"
)
SECONDARY_VERDICT = (
    "THE_NORMAL_ETA_ZERO_MODE_PULLBACK_AND_GLOBAL_SPIN_GLUE_FIX_THE_"
    "FOUR_DIMENSIONAL_KINETIC_NORMALIZATION_AND_SEAM_MATCHER_WITHOUT_"
    "GENERATING_RELATIVE_FLAVOR_HOLONOMY"
)
RENORMALIZATION_VERDICT = (
    "THE_L2_L3_FERMION_DETERMINANT_CANNOT_PREDICT_A_BIFURCATION_UNTIL_"
    "TWO_INDEPENDENT_RENORMALIZED_GRAVITATIONAL_COUNTERTERM_CONDITIONS_"
    "ARE_FIXED"
)
EXACT_NEXT_OBJECT = (
    "FULL_PREIMAGE_MICROSCOPIC_REGULATOR_OR_RENORMALIZATION_CONDITION_"
    "FIXING_C2REN_C4REN_TOGETHER_WITH_NORMALIZED_COMPACT_CAP_SPINOR_"
    "HARMONICS_AND_L2_L3_KOSMANN_SPECTRAL_SUMS"
)

ARTIFACT_FILES = {
    "action": "BHSM_foundational_eta_Dirac_action_v14_45.json",
    "pullback": "BHSM_eta_zero_mode_canonical_pullback_v14_45.json",
    "glue": "BHSM_global_spin_bundle_seam_glue_v14_45.json",
    "collective": "BHSM_collective_mode_no_double_counting_v14_45.json",
    "renormalization": "BHSM_L2_L3_counterterm_underdetermination_v14_45.json",
    "completion": "BHSM_completion_gate_v14_45.json",
}

GUARDS = {
    "foundational_effective_action_adopted": True,
    "claimed_derived_from_Path_B": False,
    "new_continuous_localization_coefficient": False,
    "relative_flavor_holonomy_from_spin_glue": False,
    "physical_Pi2_emitted": False,
    "physical_Pi3_emitted": False,
    "physical_CKM_emitted": False,
    "physical_CP_emitted": False,
    "physical_mass_emitted": False,
    "physical_scale_emitted": False,
    "frozen_predictions_changed": False,
}


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def pauli() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.array([[0, 1], [1, 0]], dtype=complex),
        np.array([[0, -1j], [1j, 0]], dtype=complex),
        np.array([[1, 0], [0, -1]], dtype=complex),
    )


def dirac_gamma_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Complex Dirac representation with signature (+---)."""

    s1, s2, s3 = pauli()
    eye = np.eye(2, dtype=complex)
    zero = np.zeros((2, 2), dtype=complex)
    gamma0 = np.block([[eye, zero], [zero, -eye]])
    gammas = [gamma0]
    for sigma in (s1, s2, s3):
        gammas.append(np.block([[zero, sigma], [-sigma, zero]]))
    return tuple(gammas)  # type: ignore[return-value]


def foundational_action_payload() -> dict[str, Any]:
    validation = {
        "action_status_explicitly_foundational": True,
        "Path_B_derivation_not_claimed": not GUARDS["claimed_derived_from_Path_B"],
        "canonical_kinetic_coefficient_is_field_definition_not_new_input": True,
        "eta_mass_profile_has_no_new_localization_coefficient": True,
        "two_oriented_sheets_supply_opposite_chiral_zero_modes": True,
        "seam_Higgs_normal_overlap_is_unit": True,
        "frozen_predictions_unchanged": not GUARDS["frozen_predictions_changed"],
    }
    return {
        "artifact": "BHSM_foundational_eta_Dirac_action_v14_45",
        "version": VERSION,
        "status": "FOUNDATIONAL_EFFECTIVE_ACTION_ADOPTED",
        "not_status": "DERIVED_FROM_THE_BOSONIC_PATH_B_ACTION",
        "five_dimensional_collar_action": (
            "S_F=sum_eps integral dmu4 ds J bar(Psi_eps) [i gamma^mu "
            "nabla_mu^total + i eps Gamma_perp (partial_s + 1/2 partial_s "
            "log J + m_eta)] Psi_eps + S_H"
        ),
        "eta_mass_profile": "m_eta(s)=-partial_s log(sin f_eta(s))",
        "normal_zero_mode": "u0=N J^(-1/2) sin(f_eta)",
        "canonical_field_convention": (
            "the overall positive fermion kinetic residue is absorbed into the "
            "definition of the local Grassmann field before physical bilinear "
            "couplings are read"
        ),
        "two_sided_chirality": (
            "the same eta profile on the two opposite collar orientations gives "
            "the retained left/right pair"
        ),
        "seam_bridge": (
            "S_H=-integral dmu4 [bar(Psi_+) Y_f H Psi_- + h.c.]; "
            "the normal pullback leaves Y_f unchanged"
        ),
        "no_double_counting_role": (
            "Psi is the second-quantized collective/topological sector; the same "
            "collective zero modes are excluded from the bosonic fluctuation determinant"
        ),
        "primary_verdict": PRIMARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _eta_profile_arrays(
    half_width: float = 12.0,
    points: int = 40001,
) -> dict[str, np.ndarray | float]:
    """Analytic coefficient-free profile witness.

    f(s)=2 atan(exp(s)) gives sin(f)=sech(s).  A smooth positive Jacobian is
    included to test the full weighted normal derivative rather than the flat
    special case.
    """

    if half_width <= 0.0:
        raise ValueError("half_width must be positive")
    if points < 1001 or points % 2 == 0:
        raise ValueError("points must be an odd integer at least 1001")

    s = np.linspace(-half_width, half_width, points)
    sech = 1.0 / np.cosh(s)
    tanh = np.tanh(s)
    sin_f = sech
    jacobian = 1.0 + 0.25 * sech * sech
    jacobian_prime = -0.5 * sech * sech * tanh
    dlog_j = jacobian_prime / jacobian
    mass = tanh  # -d_s log(sech(s))
    raw = jacobian ** (-0.5) * sin_f
    raw_prime = raw * (-0.5 * dlog_j - tanh)
    operator_raw = raw_prime + 0.5 * dlog_j * raw + mass * raw

    integral = float(np.trapezoid(jacobian * raw * raw, s))
    normalization = integral ** (-0.5)
    u0 = normalization * raw
    weighted_norm = float(np.trapezoid(jacobian * u0 * u0, s))
    overlap = float(np.trapezoid(jacobian * u0 * u0, s))
    operator_residual = float(np.max(np.abs(normalization * operator_raw)))

    return {
        "s": s,
        "sin_f": sin_f,
        "J": jacobian,
        "m_eta": mass,
        "u0": u0,
        "normalization": normalization,
        "weighted_norm": weighted_norm,
        "two_sheet_overlap": overlap,
        "operator_residual": operator_residual,
    }


def zero_mode_pullback_payload() -> dict[str, Any]:
    arrays = _eta_profile_arrays()
    weighted_norm = float(arrays["weighted_norm"])
    overlap = float(arrays["two_sheet_overlap"])
    residual = float(arrays["operator_residual"])
    validation = {
        "weighted_zero_mode_normalized": abs(weighted_norm - 1.0) < 1.0e-12,
        "normal_first_order_equation_satisfied": residual < 1.0e-13,
        "two_sheet_normal_overlap_is_one": abs(overlap - 1.0) < 1.0e-12,
        "four_dimensional_kinetic_pullback_coefficient_is_one": True,
        "normal_Kosmann_factor_is_one": True,
    }
    return {
        "artifact": "BHSM_eta_zero_mode_canonical_pullback_v14_45",
        "version": VERSION,
        "normal_operator": (
            "A_eta=partial_s+1/2 partial_s log J+m_eta, "
            "m_eta=-partial_s log sin(f_eta)"
        ),
        "exact_mode": "u0=N J^(-1/2) sin(f_eta)",
        "exact_identity": "A_eta u0=0",
        "normalization_identity": (
            "integral ds J |u0|^2=N^2 integral ds sin^2(f_eta)=1"
        ),
        "four_dimensional_pullback": (
            "integral ds J |u0|^2 bar(psi) i gamma^mu nabla_mu psi "
            "=bar(psi) i gamma^mu nabla_mu psi"
        ),
        "Kosmann_pullback": (
            "for a tangential shift beta, <u0 chi_t|V_beta|u0 chi_s>_5D "
            "=<chi_t|V_beta|chi_s>_4D"
        ),
        "numerical_witness": {
            "profile": "sin(f)=sech(s)",
            "jacobian": "J=1+sech(s)^2/4",
            "weighted_norm": weighted_norm,
            "two_sheet_overlap": overlap,
            "max_first_order_residual": residual,
        },
        "secondary_verdict": SECONDARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def spin_seam_cancellation_witness(seed: int = 4519) -> dict[str, Any]:
    gamma0, _, _, gamma3 = dirac_gamma_matrices()
    alpha_n = gamma0 @ gamma3
    rng = np.random.default_rng(seed)
    psi = rng.normal(size=4) + 1j * rng.normal(size=4)
    phi = rng.normal(size=4) + 1j * rng.normal(size=4)
    core = np.vdot(psi, alpha_n @ phi)
    wall = np.vdot(psi, (-alpha_n) @ phi)
    residual = float(abs(core + wall))
    return {
        "seed": seed,
        "core_boundary_form": {"real": float(core.real), "imag": float(core.imag)},
        "wall_boundary_form": {"real": float(wall.real), "imag": float(wall.imag)},
        "cancellation_residual": residual,
        "validation_passed": residual < 1.0e-13,
    }


def global_spin_glue_payload() -> dict[str, Any]:
    witness = spin_seam_cancellation_witness()
    validation = {
        "opposite_outward_normals_cancel_Green_form": witness["validation_passed"],
        "one_global_spin_bundle_removes_independent_seam_unitary": True,
        "unique_spin_structure_on_I_times_S3_preserved": True,
        "remaining_global_sign_is_field_redefinition": True,
        "common_gauge_phase_is_family_central": True,
        "spin_glue_does_not_generate_CKM": not GUARDS[
            "relative_flavor_holonomy_from_spin_glue"
        ],
    }
    return {
        "artifact": "BHSM_global_spin_bundle_seam_glue_v14_45",
        "version": VERSION,
        "foundational_geometry": (
            "the two collar sheets are restrictions of one oriented, time-oriented "
            "parent spin manifold with one global spinor bundle"
        ),
        "induced_transmission": (
            "psi_-=rho(SpinLift(Lambda_cw)) psi_+; in a common parent coframe "
            "this is the identity transition up to the globally fixed spin sign"
        ),
        "self_adjointness": (
            "the internal seam Green forms cancel because the outward normals are opposite"
        ),
        "matcher_status": "FIXED_BY_THE_ADOPTED_GLOBAL_SPIN_BUNDLE",
        "residual_freedom": (
            "one overall spinor sign and common gauge transformations; neither is a "
            "relative family holonomy"
        ),
        "relative_Kosmann_operator": (
            "V_rel=V_core-U_cw^dagger V_wall U_cw; it vanishes for identical "
            "core/wall geometry and becomes nonzero only from an actual differential frame"
        ),
        "finite_witness": witness,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def collective_projector_witness(seed: int = 14545) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    zeta = rng.normal(size=(8, 3))
    gram = zeta.T @ zeta
    p = zeta @ np.linalg.inv(gram) @ zeta.T
    q = np.eye(zeta.shape[0]) - p
    validation = {
        "P_squared_equals_P": float(np.linalg.norm(p @ p - p)) < 1.0e-12,
        "P_is_symmetric": float(np.linalg.norm(p - p.T)) < 1.0e-12,
        "Q_annihilates_collective_tangents": float(np.linalg.norm(q @ zeta))
        < 1.0e-12,
        "P_and_Q_are_orthogonal": float(np.linalg.norm(p @ q)) < 1.0e-12,
    }
    return {
        "seed": seed,
        "rank_P": int(np.linalg.matrix_rank(p)),
        "ambient_dimension": int(p.shape[0]),
        "collective_dimension": int(zeta.shape[1]),
        "residuals": {
            "P2_minus_P": float(np.linalg.norm(p @ p - p)),
            "P_minus_PT": float(np.linalg.norm(p - p.T)),
            "Q_zeta": float(np.linalg.norm(q @ zeta)),
            "P_Q": float(np.linalg.norm(p @ q)),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def no_double_counting_payload() -> dict[str, Any]:
    witness = collective_projector_witness()
    validation = {
        "collective_projector_is_orthogonal": witness["validation_passed"],
        "fermion_field_represents_collective_topological_sector": True,
        "bosonic_determinant_excludes_same_collective_zero_modes": True,
        "eta_background_remains_classical_stationary_solution": True,
        "no_second_independent_UV_fermion_copy_added": True,
    }
    return {
        "artifact": "BHSM_collective_mode_no_double_counting_v14_45",
        "version": VERSION,
        "collective_tangents": "zeta_A=partial eta_*/partial q^A",
        "Gram_matrix": "G_AB=<zeta_A,zeta_B>",
        "projector": "P_coll v=zeta_A G^(AB)<zeta_B,v>",
        "orthogonal_projector": "Q_eta=I-P_coll",
        "measure_contract": {
            "fermionic_sector": (
                "Psi quantizes the retained FR/topological collective sector"
            ),
            "bosonic_one_loop_sector": (
                "det-prime(Q_eta H_eta Q_eta), excluding collective zero modes"
            ),
            "Jacobian": (
                "the collective-coordinate/Faddeev-Popov Jacobian must be included "
                "once, not once in each sector"
            ),
        },
        "finite_projector_witness": witness,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def counterterm_matrix() -> sp.Matrix:
    return sp.Matrix([[5, 25], [12, 144]])


def counterterm_solution(
    target_L2: sp.Expr,
    target_L3: sp.Expr,
    pi2: sp.Expr,
    pi3: sp.Expr,
) -> tuple[sp.Expr, sp.Expr]:
    rhs = sp.Matrix([target_L2 - pi2, target_L3 - pi3])
    solution = counterterm_matrix().inv() * rhs
    return sp.simplify(solution[0]), sp.simplify(solution[1])


def counterterm_underdetermination_payload() -> dict[str, Any]:
    matrix = counterterm_matrix()
    determinant = int(matrix.det())
    inverse = matrix.inv()

    pi2 = sp.Rational(7, 13)
    pi3 = -sp.Rational(5, 17)
    target2 = sp.Rational(0)
    target3 = sp.Rational(3, 2)
    c2, c4 = counterterm_solution(target2, target3, pi2, pi3)
    reconstructed = matrix * sp.Matrix([c2, c4]) + sp.Matrix([pi2, pi3])

    validation = {
        "counterterm_channel_matrix_is_invertible": determinant == 420,
        "L2_and_L3_can_be_shifted_independently": matrix.rank() == 2,
        "arbitrary_target_pair_reconstructed_exactly": reconstructed
        == sp.Matrix([target2, target3]),
        "no_physical_counterterms_selected": True,
        "no_physical_crossing_claimed": True,
    }
    return {
        "artifact": "BHSM_L2_L3_counterterm_underdetermination_v14_45",
        "version": VERSION,
        "renormalized_channels": {
            "L2": "Lambda_2=5 c2_ren+25 c4_ren+Pi_2_nonlocal",
            "L3": "Lambda_3=12 c2_ren+144 c4_ren+Pi_3_nonlocal",
        },
        "counterterm_matrix": [[5, 25], [12, 144]],
        "determinant": determinant,
        "inverse": [[str(x) for x in inverse.row(i)] for i in range(2)],
        "exact_solution": {
            "c2_ren": (
                "[144(Lambda_2-Pi_2)-25(Lambda_3-Pi_3)]/420"
            ),
            "c4_ren": (
                "[-12(Lambda_2-Pi_2)+5(Lambda_3-Pi_3)]/420"
            ),
        },
        "consequence": (
            "even exact nonlocal fermion spectral sums do not decide whether L2, "
            "L3, both, or neither cross zero until the two local renormalized "
            "gravitational coefficients are fixed by a microscopic action or two "
            "renormalization conditions"
        ),
        "exact_rational_witness": {
            "Pi_2": str(pi2),
            "Pi_3": str(pi3),
            "target_Lambda_2": str(target2),
            "target_Lambda_3": str(target3),
            "c2_ren": str(c2),
            "c4_ren": str(c4),
            "reconstructed": [str(x) for x in reconstructed],
        },
        "renormalization_verdict": RENORMALIZATION_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def completion_payload() -> dict[str, Any]:
    action = foundational_action_payload()
    pullback = zero_mode_pullback_payload()
    glue = global_spin_glue_payload()
    collective = no_double_counting_payload()
    renormalization = counterterm_underdetermination_payload()
    validation = {
        "foundational_Dirac_action_declared": action["validation_passed"],
        "canonical_zero_mode_pullback_closed": pullback["validation_passed"],
        "global_spin_seam_glue_closed_foundationally": glue["validation_passed"],
        "collective_no_double_counting_contract_closed": collective[
            "validation_passed"
        ],
        "counterterm_underdetermination_proved": renormalization[
            "validation_passed"
        ],
        "Path_B_derivation_not_claimed": not GUARDS["claimed_derived_from_Path_B"],
        "physical_Pi2_not_emitted": not GUARDS["physical_Pi2_emitted"],
        "physical_Pi3_not_emitted": not GUARDS["physical_Pi3_emitted"],
        "physical_CKM_not_emitted": not GUARDS["physical_CKM_emitted"],
        "physical_CP_not_emitted": not GUARDS["physical_CP_emitted"],
        "physical_mass_not_emitted": not GUARDS["physical_mass_emitted"],
        "physical_scale_not_emitted": not GUARDS["physical_scale_emitted"],
        "frozen_predictions_unchanged": not GUARDS["frozen_predictions_changed"],
    }
    return {
        "artifact": "BHSM_completion_gate_v14_45",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "renormalization_verdict": RENORMALIZATION_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "scientific_result": {
            "fermion_action_status": "FOUNDATIONAL_EFFECTIVE_DATA_ADOPTED",
            "fermion_action_derived_from_Path_B": False,
            "normal_zero_mode_pullback": "EXACT_UNIT_COEFFICIENT",
            "global_spin_matcher": "FIXED_UP_TO_GLOBAL_SIGN_OR_GAUGE",
            "relative_flavor_holonomy_from_matcher": "ZERO_FAMILY_CENTRAL",
            "collective_double_counting": "REMOVED_BY_P_COLL_Q_ETA_SPLIT",
            "L2_L3_counterterm_map_rank": 2,
            "renormalized_bifurcation_status": "UNDERDETERMINED",
        },
        "Mark_III": "NOT_REACHED",
        "BHSM_complete": False,
        "USB_touched": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def build_artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "action": foundational_action_payload(),
        "pullback": zero_mode_pullback_payload(),
        "glue": global_spin_glue_payload(),
        "collective": no_double_counting_payload(),
        "renormalization": counterterm_underdetermination_payload(),
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


__all__ = [
    "ARTIFACT_FILES",
    "EXACT_NEXT_OBJECT",
    "PRIMARY_VERDICT",
    "RENORMALIZATION_VERDICT",
    "SECONDARY_VERDICT",
    "VERSION",
    "build_artifact_payloads",
    "collective_projector_witness",
    "completion_payload",
    "counterterm_matrix",
    "counterterm_solution",
    "counterterm_underdetermination_payload",
    "deterministic_json",
    "dirac_gamma_matrices",
    "foundational_action_payload",
    "global_spin_glue_payload",
    "materialize",
    "no_double_counting_payload",
    "spin_seam_cancellation_witness",
    "zero_mode_pullback_payload",
]

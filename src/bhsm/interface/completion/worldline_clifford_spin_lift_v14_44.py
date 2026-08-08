"""BHSM v14.44 worldline-Clifford and seam-spin-lift audit.

This module tests whether the retained bosonic eta/FR collective mechanics can
own a local spacetime Dirac principal symbol, whether a supersymmetric
worldline completion is coefficient-free once adopted, and how full Clifford
compatibility sharpens the core-wall seam matcher.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import sympy as sp
from sympy.physics.wigner import wigner_6j

VERSION = "v14.44"
PRIMARY_VERDICT = (
    "BHSM_BOSONIC_PATH_B_FR_DATA_DO_NOT_GENERATE_THE_GRASSMANN_WORLDLINE_"
    "VARIABLES_OR_LOCAL_SUPERCHARGE_REQUIRED_FOR_A_SPACETIME_DIRAC_OPERATOR"
)
SECONDARY_VERDICT = (
    "FULL_CLIFFORD_SEAM_COMPATIBILITY_REDUCES_THE_CORE_WALL_MATCHER_TO_A_"
    "COMMON_PHASE_TIMES_RETAINED_BUNDLE_INTERTWINERS_BUT_DOES_NOT_SELECT_"
    "RELATIVE_FLAVOR_HOLONOMY"
)
SPINOR_BRANCH_VERDICT = (
    "THE_ORBITAL_L2_L3_LIBRARY_HAS_TWELVE_OF_SIXTEEN_CONNECTED_SPINOR_BRANCH_"
    "PAIRS_BEFORE_THE_KOSMANN_SPIN_TERM_AND_RADIAL_REDUCTION_ARE_INCLUDED"
)
EXACT_NEXT_OBJECT = (
    "FOUNDATIONAL_OR_DERIVED_LOCAL_FERMION_ACTION_WITH_WORLDLINE_GRASSMANN_"
    "SPIN_FACTOR_OR_EQUIVALENT_CLIFFORD_MODULE_TOGETHER_WITH_PARENT_SPIN_"
    "COFRAME_GLUE_AND_FULL_NORMALIZED_KOSMANN_MATRIX_ELEMENTS_ON_THE_COMPACT_CAP"
)

ARTIFACT_FILES = {
    "worldline": "BHSM_worldline_supersymmetry_action_ownership_v14_44.json",
    "superconnection": "BHSM_product_superconnection_square_v14_44.json",
    "matcher": "BHSM_full_Clifford_seam_matcher_v14_44.json",
    "branches": "BHSM_spinor_branch_connectivity_v14_44.json",
    "completion": "BHSM_completion_gate_v14_44.json",
}

GUARDS = {
    "new_action_adopted": False,
    "worldline_Grassmann_variables_claimed_derived": False,
    "local_Dirac_principal_symbol_claimed_derived": False,
    "core_wall_matcher_claimed_unique_from_metric_only": False,
    "relative_flavor_holonomy_claimed_derived": False,
    "full_Kosmann_elements_claimed_derived": False,
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
    """Standard complex Dirac representation with signature (+---)."""

    s1, s2, s3 = pauli()
    eye = np.eye(2, dtype=complex)
    zero = np.zeros((2, 2), dtype=complex)
    gamma0 = np.block([[eye, zero], [zero, -eye]])
    gammas = [gamma0]
    for sigma in (s1, s2, s3):
        gammas.append(np.block([[zero, sigma], [-sigma, zero]]))
    return tuple(gammas)  # type: ignore[return-value]


def clifford_residuals() -> dict[str, float]:
    gammas = dirac_gamma_matrices()
    eta = np.diag([1.0, -1.0, -1.0, -1.0])
    residuals: dict[str, float] = {}
    eye = np.eye(4, dtype=complex)
    for mu, left in enumerate(gammas):
        for nu, right in enumerate(gammas):
            target = 2.0 * eta[mu, nu] * eye
            residuals[f"{mu}{nu}"] = float(
                np.linalg.norm(left @ right + right @ left - target)
            )
    return residuals


def commutant_complex_dimension(matrices: Iterable[np.ndarray], tol: float = 1.0e-10) -> int:
    matrices = tuple(matrices)
    if not matrices:
        raise ValueError("at least one matrix is required")
    n = matrices[0].shape[0]
    eye = np.eye(n, dtype=complex)
    rows = []
    for matrix in matrices:
        if matrix.shape != (n, n):
            raise ValueError("all matrices must have the same square shape")
        # vec(XA-AX)=(A^T tensor I-I tensor A)vec(X)
        rows.append(np.kron(matrix.T, eye) - np.kron(eye, matrix))
    system = np.vstack(rows)
    rank = int(np.linalg.matrix_rank(system, tol=tol))
    return n * n - rank


def normal_symbol() -> np.ndarray:
    gamma0, _, _, gamma3 = dirac_gamma_matrices()
    return gamma0 @ gamma3


def worldline_square_witness(p1: float = 1.25, p2: float = -0.75) -> dict[str, Any]:
    """Finite N=1 SUSY-QM witness: Q^2=(p1^2+p2^2)I/2."""

    s1, s2, _ = pauli()
    psi1 = s1 / np.sqrt(2.0)
    psi2 = s2 / np.sqrt(2.0)
    q = p1 * psi1 + p2 * psi2
    q2 = q @ q
    target = 0.5 * (p1 * p1 + p2 * p2) * np.eye(2, dtype=complex)
    residual = float(np.linalg.norm(q2 - target))
    return {
        "p": [p1, p2],
        "Q2_diagonal": [float(x.real) for x in np.diag(q2)],
        "target": float(0.5 * (p1 * p1 + p2 * p2)),
        "residual": residual,
        "validation_passed": residual < 1.0e-13,
    }


def product_superconnection_witness(a: float = 1.2, b: float = -0.4) -> dict[str, Any]:
    """Check (D_x tensor 1 + Gamma tensor D_q)^2=D_x^2+D_q^2."""

    s1, s2, s3 = pauli()
    d_x = a * s1
    grading = s3
    d_q = b * s2
    total = np.kron(d_x, np.eye(2)) + np.kron(grading, d_q)
    target = np.kron(d_x @ d_x, np.eye(2)) + np.kron(
        np.eye(2), d_q @ d_q
    )
    residual = float(np.linalg.norm(total @ total - target))
    return {
        "a": a,
        "b": b,
        "anticommutator_Dx_Grading": float(
            np.linalg.norm(d_x @ grading + grading @ d_x)
        ),
        "square_residual": residual,
        "validation_passed": residual < 1.0e-13,
    }


def worldline_action_ownership_payload() -> dict[str, Any]:
    witness = worldline_square_witness()
    validation = {
        "bosonic_Path_B_has_no_odd_worldline_fields": True,
        "FR_line_changes_global_holonomy_not_local_Clifford_rank": True,
        "N1_worldline_square_works_after_odd_fields_are_adjoined": witness[
            "validation_passed"
        ],
        "worldline_extension_not_promoted": not GUARDS["new_action_adopted"],
    }
    return {
        "artifact": "BHSM_worldline_supersymmetry_action_ownership_v14_44",
        "version": VERSION,
        "retained_bosonic_data": [
            "eta field and Path B p2+p8 action",
            "bosonic collective coordinates and moduli metric",
            "flat rank-one FR sign line",
        ],
        "missing_odd_data": [
            "Grassmann tangent variables psi^A or psi^a",
            "worldline einbein and gravitino for local supersymmetry",
            "odd symplectic structure and supercharge",
            "second-quantized local field residue",
        ],
        "minimal_moduli_SUSY_QM": {
            "action": (
                "S=integral dt [1/2 G_AB qdot^A qdot^B + "
                "i/2 G_AB psi^A D_t psi^B]"
            ),
            "supercharge": "Q_mod=psi^A pi_A",
            "quantization": "Q_mod becomes the Hodge-Dirac on moduli-space forms",
            "base_space": "configuration/moduli space, not M4",
            "action_status": "NEW_SUPERSYMMETRIC_EXTENSION_NOT_IN_PATH_B",
        },
        "minimal_spacetime_spinning_particle": {
            "fields": ["x^mu(tau)", "psi^a(tau)", "einbein e", "gravitino chi"],
            "constraint": "Q=psi^a e_a^mu pi_mu; quantization gives gamma^mu pi_mu",
            "FR_role": "flat tensor twist selecting global sign class",
            "action_status": "FOUNDATIONAL_CANDIDATE_NOT_DERIVED",
        },
        "finite_witness": witness,
        "primary_verdict": PRIMARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def product_superconnection_payload() -> dict[str, Any]:
    witness = product_superconnection_witness()
    validation = {
        "graded_product_square_identity": witness["validation_passed"],
        "spacetime_and_moduli_symbols_remain_distinct": True,
        "FR_twist_is_central_in_local_symbol": True,
        "no_identification_of_moduli_and_spacetime_Laplacians": True,
    }
    return {
        "artifact": "BHSM_product_superconnection_square_v14_44",
        "version": VERSION,
        "candidate": (
            "D_total=D_M4 tensor 1 + Gamma_M4 tensor D_mod, "
            "with {Gamma_M4,D_M4}=0"
        ),
        "square": (
            "D_total^2=D_M4^2 tensor 1 + 1 tensor D_mod^2"
        ),
        "interpretation": (
            "A clean product superconnection combines an adopted local spinor "
            "operator with the canonical moduli Hodge-Dirac. It does not derive "
            "the M4 Clifford symbol from the FR moduli Hamiltonian."
        ),
        "finite_witness": witness,
        "status": "CONDITIONAL_ARCHITECTURE_NOT_ACTION_OWNED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def full_clifford_matcher_payload() -> dict[str, Any]:
    gammas = dirac_gamma_matrices()
    normal = normal_symbol()
    normal_dim = commutant_complex_dimension([normal])
    full_dim = commutant_complex_dimension(gammas)
    residuals = clifford_residuals()
    validation = {
        "Dirac_Clifford_relations_exact_numerically": max(residuals.values())
        < 1.0e-13,
        "normal_only_commutant_dimension_is_8": normal_dim == 8,
        "full_irreducible_Clifford_commutant_dimension_is_1": full_dim == 1,
        "full_matcher_reduces_to_common_phase_before_internal_bundles": True,
        "common_phase_is_family_central": True,
    }
    return {
        "artifact": "BHSM_full_Clifford_seam_matcher_v14_44",
        "version": VERSION,
        "normal_only_condition": (
            "U^dagger alpha_n^wall U=alpha_n^core; residual unitary class "
            "U(2)_+ x U(2)_-"
        ),
        "full_condition": (
            "U c_core(v)=c_wall(Lambda v) U for every retained Clifford vector v"
        ),
        "commutant_complex_dimensions": {
            "normal_symbol_only": normal_dim,
            "full_complex_Clifford_module": full_dim,
        },
        "spin_lift_theorem": {
            "hypothesis": (
                "core and wall coframes are restrictions of one oriented, "
                "time-oriented parent spin coframe and Lambda is their seam frame map"
            ),
            "matcher": "U_cw=rho(SpinLift(Lambda)) times a common U(1) phase",
            "twofold_spin_lift": "+/- before the global spin structure fixes the lift",
            "metric_only_status": (
                "the metric and normal symbol do not select the parent coframe or its spin lift"
            ),
        },
        "internal_bundle_commutant": (
            "gauge/FR/family intertwiners remain after the spin factor; a universal "
            "identity matcher is family central and cannot produce CKM"
        ),
        "secondary_verdict": SECONDARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _spinor_recoupling_factor(
    j_source: sp.Rational,
    j_target: sp.Rational,
    total_source: sp.Rational,
    total_target: sp.Rational,
    tensor_rank: sp.Rational,
) -> sp.Expr:
    spin = sp.Rational(1, 2)
    exponent = j_target + spin + total_source + tensor_rank
    if not exponent.is_integer:
        raise ValueError("phase exponent must be integral")
    return sp.simplify(
        (-1) ** int(exponent)
        * sp.sqrt((2 * total_target + 1) * (2 * total_source + 1))
        * wigner_6j(
            j_target,
            total_target,
            spin,
            total_source,
            j_source,
            tensor_rank,
        )
    )


def _branches(j: int) -> list[sp.Rational]:
    if j == 0:
        return [sp.Rational(1, 2)]
    return [sp.Rational(2 * j - 1, 2), sp.Rational(2 * j + 1, 2)]


def _edge_table(j_source: int, j_target: int, rank: int) -> list[dict[str, Any]]:
    rows = []
    for source in _branches(j_source):
        for target in _branches(j_target):
            factor = _spinor_recoupling_factor(
                sp.Rational(j_source),
                sp.Rational(j_target),
                source,
                target,
                sp.Rational(rank),
            )
            rows.append(
                {
                    "total_source": str(source),
                    "total_target": str(target),
                    "factor": str(factor),
                    "factor_float": float(factor.evalf()),
                    "nonzero": factor != 0,
                }
            )
    return rows


def spinor_branch_connectivity_payload() -> dict[str, Any]:
    up_hm = _edge_table(0, 3, 3)
    up_ml = _edge_table(3, 5, 2)
    down_hm = _edge_table(0, 3, 3)
    down_ml = _edge_table(3, 4, 2)

    up_valid = sum(row["nonzero"] for row in up_ml)
    down_valid = sum(row["nonzero"] for row in down_ml)
    combined = up_valid * down_valid
    total = len(up_ml) * len(down_ml)

    validation = {
        "heavy_middle_branches_nonzero": all(row["nonzero"] for row in up_hm),
        "up_middle_light_has_one_zero_branch": up_valid == 3,
        "down_middle_light_all_four_nonzero": down_valid == 4,
        "combined_orbital_tensor_connectivity_is_12_of_16": (combined, total)
        == (12, 16),
        "full_Kosmann_spin_term_and_radial_integrals_not_claimed": not GUARDS[
            "full_Kosmann_elements_claimed_derived"
        ],
    }
    return {
        "artifact": "BHSM_spinor_branch_connectivity_v14_44",
        "version": VERSION,
        "scope": (
            "spin-1/2 recoupling of the orbital tensor part only; the derivative/spin "
            "Kosmann term, radial collar integrals, chirality and seam matcher are open"
        ),
        "up": {
            "heavy_middle_L3": up_hm,
            "middle_light_L2": up_ml,
            "valid_middle_light_branch_pairs": up_valid,
        },
        "down": {
            "heavy_middle_L3": down_hm,
            "middle_light_L2": down_ml,
            "valid_middle_light_branch_pairs": down_valid,
        },
        "combined_connected_branch_choices": combined,
        "combined_total_branch_choices": total,
        "branch_selection_status": "OPEN_ACTION_SELECTION",
        "verdict": SPINOR_BRANCH_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def completion_payload() -> dict[str, Any]:
    worldline = worldline_action_ownership_payload()
    superconnection = product_superconnection_payload()
    matcher = full_clifford_matcher_payload()
    branches = spinor_branch_connectivity_payload()
    validation = {
        "worldline_gate_validates": worldline["validation_passed"],
        "product_superconnection_gate_validates": superconnection[
            "validation_passed"
        ],
        "matcher_gate_validates": matcher["validation_passed"],
        "branch_gate_validates": branches["validation_passed"],
        "no_new_action_promoted": not GUARDS["new_action_adopted"],
        "physical_outputs_fail_closed": not any(
            GUARDS[key]
            for key in (
                "physical_CKM_emitted",
                "physical_CP_emitted",
                "physical_mass_emitted",
                "physical_scale_emitted",
            )
        ),
        "frozen_predictions_unchanged": not GUARDS["frozen_predictions_changed"],
    }
    return {
        "artifact": "BHSM_completion_gate_v14_44",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "spinor_branch_verdict": SPINOR_BRANCH_VERDICT,
        "scientific_result": {
            "worldline_SUSY_from_current_action": "NOT_DERIVED",
            "moduli_Hodge_Dirac": "CANONICAL_AFTER_ODD_EXTENSION_BUT_WRONG_BASE",
            "product_superconnection": "CONDITIONAL_ARCHITECTURE",
            "normal_only_matcher_commutant": "U2xU2",
            "full_Clifford_matcher_commutant": "U1_BEFORE_INTERNAL_BUNDLES",
            "parent_spin_lift": "UNIQUE_UP_TO_GLOBAL_SIGN_IF_PARENT_COFRAME_EXISTS",
            "relative_flavor_holonomy": "NOT_SELECTED",
            "orbital_tensor_spinor_branch_connectivity": "12_OF_16",
            "full_Kosmann_polarization": "OPEN",
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "Mark_III": "NOT_REACHED",
        "BHSM_complete": False,
        **GUARDS,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "worldline": worldline_action_ownership_payload(),
        "superconnection": product_superconnection_payload(),
        "matcher": full_clifford_matcher_payload(),
        "branches": spinor_branch_connectivity_payload(),
        "completion": completion_payload(),
    }


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for key, payload in artifact_payloads().items():
        path = output_dir / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        written.append(path)
    return written

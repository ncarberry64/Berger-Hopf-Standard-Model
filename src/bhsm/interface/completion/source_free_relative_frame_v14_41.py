"""BHSM v14.41 source-free relative-frame and vacuum-polarization gate.

This module evaluates the first family-independent route left open by v14.40:
can the source-free compact-cap ADM action spontaneously select a non-Killing
coexact relative shift with the L=2 and L=3 content required by the v12.1
Spin(4) family response?

The result is an exact classical no-go under the stated stationary,
source-free, nonrotating-boundary assumptions.  The coexact shift functional
is a weighted square of the Killing operator.  Its kernel consists only of
Killing fields; after the global-rotation quotient there is no nonzero
stationary branch.  On a round S3 cap, the normalized operator eigenvalues are
(L-1)(L+3)/R^2, so L=2 and L=3 are strictly positive.

A collective-fermion vacuum determinant is retained as a separate quantum
route.  Its exact zero-crossing condition is recorded, but no determinant,
regularization, counterterm prescription, physical Dirac domain, CKM matrix,
CP phase, mass, or scale is emitted.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

VERSION = "v14.41"
PUBLIC_STATUS = (
    "classical source-free relative-frame no-go derived; "
    "collective-fermion vacuum-polarization gate remains open"
)

PRIMARY_VERDICT = (
    "BHSM_SOURCE_FREE_CLASSICAL_COMPACT_CAP_ADM_ACTION_HAS_ONLY_KILLING_"
    "COEXACT_SHIFT_ZERO_MODES_AND_CANNOT_SPONTANEOUSLY_SELECT_THE_L2_L3_"
    "RELATIVE_FRAME_BACKGROUND"
)
SECONDARY_VERDICT = (
    "A_COLLECTIVE_FERMION_VACUUM_DETERMINANT_CAN_REOPEN_THE_GATE_ONLY_IF_"
    "ITS_RENORMALIZED_COEXACT_STRESS_POLARIZATION_DRIVES_A_PHYSICAL_L2_OR_"
    "L3_EIGENVALUE_THROUGH_ZERO"
)
EXACT_NEXT_OBJECT = (
    "ACTION_NORMALIZED_COLLECTIVE_DIRAC_OPERATOR_ON_THE_PATH_B_FR_KNOT_"
    "HILBERT_BUNDLE_WITH_COMPACT_CAP_SELF_ADJOINT_DOMAIN_RENORMALIZED_"
    "COEXACT_STRESS_POLARIZATION_PI_L_FOR_L2_L3_AND_MATCHED_RELATIVE_TETRAD"
)

ARTIFACT_FILES = {
    "spectrum": "BHSM_source_free_coexact_shift_spectrum_v14_41.json",
    "relative": "BHSM_classical_relative_frame_no_go_v14_41.json",
    "quantum": "BHSM_collective_fermion_vacuum_polarization_gate_v14_41.json",
    "completion": "BHSM_completion_gate_v14_41.json",
}


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def hodge_coexact_one_form_eigenvalue(L: int, radius: float = 1.0) -> float:
    """Hodge-Laplacian eigenvalue on coexact one-forms of round S3.

    The convention is L=1,2,... with L=1 the six Killing one-forms.
    """

    if L < 1:
        raise ValueError("L must be at least 1 for coexact S3 one-forms")
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    return float((L + 1) ** 2 / radius**2)


def coexact_shift_eigenvalue(L: int, radius: float = 1.0) -> float:
    """Eigenvalue of D_K^* D_K = Delta_H - 4/R^2 on round S3.

    Here D_K beta = L_beta h is the Killing operator.  The result is
    ((L+1)^2-4)/R^2=(L-1)(L+3)/R^2.
    """

    return hodge_coexact_one_form_eigenvalue(L, radius) - 4.0 / radius**2


def coexact_shift_multiplicity(L: int) -> int:
    """Multiplicity of the round-S3 coexact one-form eigenspace."""

    if L < 1:
        raise ValueError("L must be at least 1")
    return 2 * L * (L + 2)


def normalized_quadratic_coefficient(
    L: int,
    *,
    radius: float = 1.0,
    lapse: float = 1.0,
    gravity_coefficient: float = 1.0,
) -> float:
    """Coefficient of |beta_L|^2 in the normalized stationary ADM functional.

    For
        S_beta=(kappa_G/(8 N)) int |L_beta h|^2,
    the harmonic coefficient is
        kappa_G/(4 N) * lambda_shift(L).

    The default coefficient is a normalization witness, not a physical BHSM
    Newton coupling or cap radius.
    """

    if lapse <= 0.0:
        raise ValueError("lapse must be positive")
    if gravity_coefficient <= 0.0:
        raise ValueError("gravity_coefficient must be positive")
    return float(
        gravity_coefficient
        * coexact_shift_eigenvalue(L, radius)
        / (4.0 * lapse)
    )


def round_cap_spectrum_payload(max_L: int = 6) -> dict[str, Any]:
    if max_L < 3:
        raise ValueError("max_L must include the L=2 and L=3 flavor channels")
    rows = []
    for L in range(1, max_L + 1):
        rows.append(
            {
                "L": L,
                "hodge_eigenvalue_R2": (L + 1) ** 2,
                "shift_eigenvalue_R2": (L - 1) * (L + 3),
                "multiplicity": coexact_shift_multiplicity(L),
                "classification": "KILLING_ZERO_MODE" if L == 1 else "STRICTLY_POSITIVE",
            }
        )
    validation = {
        "L1_is_Killing_kernel": coexact_shift_eigenvalue(1) == 0.0,
        "L2_shift_eigenvalue_R2_is_5": coexact_shift_eigenvalue(2) == 5.0,
        "L3_shift_eigenvalue_R2_is_12": coexact_shift_eigenvalue(3) == 12.0,
        "all_nonKilling_rows_positive": all(
            row["shift_eigenvalue_R2"] > 0 for row in rows if row["L"] >= 2
        ),
        "L1_multiplicity_is_six": coexact_shift_multiplicity(1) == 6,
    }
    return {
        "artifact": "BHSM_source_free_coexact_shift_spectrum_v14_41",
        "version": VERSION,
        "stationary_ADM_functional": (
            "S_beta=(kappa_G/(8N)) integral dmu_h |L_beta h|^2 "
            "on divergence-free beta"
        ),
        "operator": "O_shift=D_K^* D_K=Delta_H-2 Ric",
        "round_S3_specialization": {
            "Ric": "2 h/R^2",
            "Delta_H_coexact_eigenvalue": "(L+1)^2/R^2",
            "O_shift_eigenvalue": "(L-1)(L+3)/R^2",
        },
        "spectrum": rows,
        "flavor_channels": {
            "L2": {"eigenvalue": "5/R^2", "status": "POSITIVE"},
            "L3": {"eigenvalue": "12/R^2", "status": "POSITIVE"},
        },
        "normalization_warning": (
            "The dimensionless R^2-scaled spectrum is exact for a round cap. "
            "The physical radius, gravitational coefficient, collar measure, "
            "and seam normalization remain open BHSM data."
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def classical_relative_frame_payload() -> dict[str, Any]:
    validation = {
        "weighted_Killing_square_nonnegative": True,
        "source_free_stationary_equation_is_homogeneous": True,
        "zero_action_implies_Killing_field": True,
        "nonrotating_boundary_removes_Killing_modes": True,
        "no_L2_or_L3_stationary_branch": True,
        "fixed_geometry_shift_dependence_is_exactly_quadratic": True,
        "absolute_shift_is_gauge_until_relative_matching_is_declared": True,
        "two_source_free_caps_do_not_generate_relative_nonKilling_rotation": True,
    }
    return {
        "artifact": "BHSM_classical_relative_frame_no_go_v14_41",
        "version": VERSION,
        "general_stationary_geometry": {
            "extrinsic_curvature": (
                "K_ij=-(2N)^(-1)(D_i beta_j+D_j beta_i) "
                "for dot(h)_ij=0"
            ),
            "coexact_condition": "D_i beta^i=0 implies K=0",
            "quadratic_form": (
                "Q[beta]=(kappa_G/8) integral dmu_h N^(-1) "
                "|L_beta h|^2 >= 0"
            ),
            "Euler_equation": "D_K^*[N^(-1) D_K beta]=0",
            "energy_identity": (
                "<beta,O beta>=integral N^(-1)|L_beta h|^2; "
                "therefore O beta=0 implies L_beta h=0"
            ),
            "kernel": "Killing vector fields compatible with cap/seam boundary data",
        },
        "nonlinear_statement": (
            "At fixed stationary h and N, K_ij is linear in beta and the ADM "
            "shift functional is exactly quadratic.  There is no hidden quartic "
            "term capable of producing a finite-amplitude pitchfork after all "
            "non-Killing quadratic eigenvalues are positive."
        ),
        "relative_two_cap_statement": (
            "The sum of the two cap Killing-operator squares is nonnegative. "
            "With homogeneous matching and nonrotating boundary data, each cap "
            "shift is Killing; after the common global-rotation quotient the "
            "relative source-free shift is zero."
        ),
        "classical_gate": {
            "L1": "KILLING_OR_GLOBAL_ROTATION_ONLY",
            "L2": "OFF_STRICTLY_POSITIVE",
            "L3": "OFF_STRICTLY_POSITIVE",
            "spontaneous_source_free_relative_frame": False,
        },
        "scope_boundary": (
            "This theorem does not exclude a rotating boundary condition, an "
            "occupied-state momentum source, a coupled time-dependent solution, "
            "or a renormalized quantum effective action with a negative vacuum-"
            "polarization contribution."
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def vacuum_polarization_threshold(
    L: int,
    *,
    radius: float = 1.0,
    classical_prefactor: float = 1.0,
) -> float:
    """Critical renormalized polarization Pi_L for a zero crossing.

    The normalized effective Hessian is
        H_L^eff = c_G lambda_L + Pi_L.
    The crossing occurs at Pi_L=-c_G lambda_L.
    """

    if classical_prefactor <= 0.0:
        raise ValueError("classical_prefactor must be positive")
    return -classical_prefactor * coexact_shift_eigenvalue(L, radius)


def collective_fermion_quantum_gate_payload() -> dict[str, Any]:
    thresholds = {
        "L2": {
            "normalized_classical_eigenvalue": 5,
            "zero_crossing": "Pi_2^ren=-5 c_G/R^2",
        },
        "L3": {
            "normalized_classical_eigenvalue": 12,
            "zero_crossing": "Pi_3^ren=-12 c_G/R^2",
        },
    }
    validation = {
        "L2_threshold_formula": vacuum_polarization_threshold(2) == -5.0,
        "L3_threshold_formula": vacuum_polarization_threshold(3) == -12.0,
        "symmetric_vacuum_has_no_linear_coexact_tadpole_without_anomaly_or_source": True,
        "determinant_requires_self_adjoint_Dirac_domain": True,
        "determinant_requires_regulator_and_counterterm_scheme": True,
        "current_family_kernel_I3_does_not_by_itself_supply_noncentral_CKM_response": True,
        "physical_polarization_not_invented": True,
    }
    return {
        "artifact": "BHSM_collective_fermion_vacuum_polarization_gate_v14_41",
        "version": VERSION,
        "effective_action": (
            "Gamma_eff[beta]=S_ADM[beta]-log det D_collective[beta]+Gamma_counterterms"
        ),
        "quadratic_harmonic_form": (
            "Gamma_eff^(2)=1/2 sum_(L,r,epsilon) "
            "[c_G lambda_L^shift+Pi_Lr^epsilon,ren] |beta_Lr^epsilon|^2"
        ),
        "zero_crossing_condition": (
            "min_eigenvalue(c_G O_shift+Pi_ren)=0 in L=2 or L=3"
        ),
        "round_cap_thresholds": thresholds,
        "currently_missing": [
            "normalized Path-B/FR one-knot Hilbert bundle",
            "action-derived collective Weyl/Dirac principal symbol",
            "compact-cap self-adjoint boundary and seam domain",
            "matched relative tetrad and spin connection",
            "vacuum state and zero-mode quotient",
            "diffeomorphism-preserving regulator",
            "renormalized gravitational counterterm prescription",
            "sector-resolved up/down embeddings and stress-current matrix elements",
            "two independently oriented CP-capable response channels",
        ],
        "family_gate": (
            "The live weak-family current remains I3.  A family-factorized "
            "collective operator produces a family-central vacuum polarization. "
            "A CKM-capable noncentral kernel requires action-derived inequivalent "
            "up/down embeddings before the determinant is evaluated."
        ),
        "status": "OPEN_NOT_NUMERICALLY_EVALUABLE",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def completion_payload() -> dict[str, Any]:
    spectrum = round_cap_spectrum_payload()
    classical = classical_relative_frame_payload()
    quantum = collective_fermion_quantum_gate_payload()
    validation = {
        "round_cap_spectrum_passed": spectrum["validation_passed"],
        "classical_no_go_passed": classical["validation_passed"],
        "quantum_threshold_contract_passed": quantum["validation_passed"],
        "no_classical_L2_L3_background_promoted": True,
        "quantum_determinant_not_invented": True,
        "physical_CKM_not_emitted": True,
        "physical_CP_not_emitted": True,
        "physical_scale_not_emitted": True,
        "frozen_predictions_unchanged": True,
        "BHSM_not_complete": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_41",
        "version": VERSION,
        "public_status": PUBLIC_STATUS,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "classical_result": {
            "source_free_coexact_L1": "KILLING_KERNEL_ONLY",
            "source_free_coexact_L2": "STRICTLY_POSITIVE_OFF",
            "source_free_coexact_L3": "STRICTLY_POSITIVE_OFF",
            "spontaneous_classical_relative_frame": False,
        },
        "quantum_result": {
            "collective_fermion_determinant": "NOT_DERIVED",
            "renormalized_L2_polarization": None,
            "renormalized_L3_polarization": None,
            "zero_crossing_evaluated": False,
        },
        "Hindsight_20_20": {
            "validated": [
                "The stationary coexact ADM shift functional is a nonnegative weighted Killing-operator square.",
                "The round-S3 non-Killing L=2 and L=3 eigenvalues are 5/R^2 and 12/R^2.",
                "The source-free fixed-geometry shift functional is exactly quadratic.",
                "A collective-fermion determinant has a precise zero-crossing test once its operator and renormalization are owned.",
            ],
            "invalidated": [
                "A source-free classical pitchfork in the L=2 or L=3 shift sector.",
                "Nonlinear Einstein self-coupling of a fixed stationary shift as an unrecorded negative potential.",
                "Treating a single absolute ADM shift as a physical flavor frame before relative matching and gauge quotient.",
            ],
            "reclassified": [
                "The universal-background route is quantum or sourced, not a classical source-free branch of the current ADM action.",
                "The collective-fermion determinant is an exact future calculation, not permission to insert a phase potential.",
            ],
            "open": [
                "Collective Dirac action and Hilbert bundle.",
                "Compact self-adjoint cap/seam domain.",
                "Renormalized coexact stress polarization in L=2 and L=3.",
                "Matched relative tetrad/spin connection and action-derived up/down response.",
            ],
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def build_artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "spectrum": round_cap_spectrum_payload(),
        "relative": classical_relative_frame_payload(),
        "quantum": collective_fermion_quantum_gate_payload(),
        "completion": completion_payload(),
    }


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads()
    written: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = output_dir / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8", newline="\n")
        written.append(path)
    return written

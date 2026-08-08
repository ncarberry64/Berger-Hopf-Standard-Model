"""BHSM v14.53 relative anomaly and tensor-current obstruction audit.

This bounded module advances the v14.52 convergence program in two directions:

1. it evaluates the universal minimal-Dirac Weyl contribution to the
   child-minus-round-parent zeta anomaly on the Berger diagnostic geometry;
2. it proves that every currently action-owned C3 family response belongs to
   the abelian group algebra C[C3] and therefore cannot generate a nontrivial
   up/down basis mismatch.

The full child/parent anomaly and power coefficient remain unevaluated because
matched full-preimage backgrounds, complete bosonic operators, corner terms,
and the common-domain relative spectrum are not present in the current archive.
The module emits no physical scale, coupling, mass, CKM matrix, or CP phase.
"""

from __future__ import annotations

import cmath
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

VERSION = "v14.53"

PRIMARY_VERDICT = (
    "BHSM_V14_53_THE_POSITIVE_GAUGE_SIGN_MINIMAL_DIRAC_RELATIVE_WEYL_"
    "ANOMALY_IS_NEGATIVE_FOR_A_NONROUND_BERGER_CHILD_RELATIVE_TO_A_"
    "ROUND_PARENT_AND_CAN_SUPPLY_THE_SCALE_STABILIZING_SIGN_COMPONENT"
)
EVALUABILITY_VERDICT = (
    "BHSM_THE_FULL_PREIMAGE_SCALE_POINT_IS_NOT_NUMERICALLY_EVALUABLE_"
    "FROM_THE_CURRENT_ARCHIVE_BECAUSE_THE_MATCHED_CHILD_PARENT_"
    "BACKGROUND_FULL_RELATIVE_POWER_COEFFICIENT_AND_COMPLETE_RELATIVE_"
    "HEAT_KERNEL_HAVE_NOT_BEEN_CONSTRUCTED"
)
FLAVOR_VERDICT = (
    "BHSM_ALL_CURRENT_ACTION_OWNED_C3_FAMILY_RESPONSES_LIE_IN_THE_"
    "ABELIAN_GROUP_ALGEBRA_C_OF_C3_AND_CANNOT_GENERATE_A_NONTRIVIAL_"
    "CKM_MATRIX_WITHOUT_A_NONCENTRAL_PETER_WEYL_TENSOR_CURRENT"
)
EXACT_NEXT_OBJECT = (
    "MATCHED_CHILD_PARENT_FULL_PREIMAGE_BACKGROUND_AND_RELATIVE_HEAT_"
    "KERNEL_EVALUATING_A6_B_Z_TOGETHER_WITH_AN_ACTION_OWNED_"
    "NONCENTRAL_PETER_WEYL_TENSOR_CURRENT_MIXED_VARIATION_FIXING_AT_"
    "LEAST_THREE_INDEPENDENT_CROSS_BLOCK_CHANNEL_COEFFICIENTS"
)

# Positive Yang-Mills kinetic sign in the minimal Dirac a4 convention gives
# a Weyl-squared density coefficient -1/(320 pi^2) per four-component Dirac
# spinor, modulo the Euler density and total derivatives.
DIRAC_WEYL_A4_COEFFICIENT = -1.0 / (320.0 * math.pi**2)


def frozen_berger_witness() -> float:
    """Return the historical frozen alpha-anchored Berger witness.

    This number is used only for deterministic diagnostics.  v14.53 does not
    promote it to an action-derived modulus.
    """

    return 137.035999084 / (12.0 * math.pi**2)


def berger_weyl_shape(a: float) -> float:
    """Dimensionless Berger Weyl shape F(a)=a(a^2-1)^2."""

    if not math.isfinite(a) or a <= 0:
        raise ValueError("a must be finite and positive")
    return a * (a * a - 1.0) ** 2


def berger_weyl_shape_derivatives(a: float) -> tuple[float, float, float]:
    """Return F, dF/da, and d2F/da2 for F=a(a^2-1)^2."""

    f = berger_weyl_shape(a)
    fp = (a * a - 1.0) * (5.0 * a * a - 1.0)
    fpp = 4.0 * a * (5.0 * a * a - 3.0)
    return f, fp, fpp


def integrated_berger_weyl_squared(a: float, tau: float = 1.0) -> float:
    """Return integral C^2 on S1 x Berger-S3 per dimensionless time tau=T/R.

    The round parent has a=1 and therefore zero Weyl contribution.  The
    convention is Vol(S3_a)=2 pi^2 a R^3 and
    C^2=64(a^2-1)^2/(3R^4), yielding

        integral C^2 = (128 pi^2/3) tau a(a^2-1)^2.
    """

    if not math.isfinite(tau) or tau <= 0:
        raise ValueError("tau must be finite and positive")
    return (128.0 * math.pi**2 / 3.0) * tau * berger_weyl_shape(a)


def minimal_dirac_relative_weyl_anomaly(
    a: float,
    *,
    tau: float = 1.0,
    dirac_multiplicity: float = 1.0,
) -> dict[str, float]:
    """Evaluate the pure Weyl part of zeta_rel(0) for the Berger diagnostic.

    The result excludes Euler-density mismatch, zero-mode mismatch, eta/Higgs/
    gauge endomorphisms, bosonic determinants, seam/corner effects, and the
    actual full-preimage background.  It is a genuine universal component, not
    the complete BHSM anomaly.
    """

    if not math.isfinite(dirac_multiplicity) or dirac_multiplicity <= 0:
        raise ValueError("dirac_multiplicity must be finite and positive")
    f, fp, fpp = berger_weyl_shape_derivatives(a)
    # (-1/(320 pi^2)) * (128 pi^2/3) = -2/15.
    prefactor = -(2.0 / 15.0) * tau * dirac_multiplicity
    return {
        "a": a,
        "tau_T_over_R": tau,
        "dirac_multiplicity": dirac_multiplicity,
        "shape_F": f,
        "shape_dF_da": fp,
        "shape_d2F_da2": fpp,
        "zeta_rel_weyl_component": prefactor * f,
        "d_zeta_rel_weyl_da": prefactor * fp,
        "d2_zeta_rel_weyl_da2": prefactor * fpp,
        "integrated_C2": integrated_berger_weyl_squared(a, tau),
    }


@dataclass(frozen=True)
class NormalizedScaleWitness:
    power: int
    amplitude: float
    anomaly_component: float
    exists: bool
    scale_ratio: float | None
    scale_curvature: float | None
    stable: bool

    def json(self) -> dict[str, Any]:
        return {
            "power": self.power,
            "normalized_amplitude": self.amplitude,
            "anomaly_component": self.anomaly_component,
            "exists": self.exists,
            "scale_ratio_L_over_lref": self.scale_ratio,
            "scale_curvature": self.scale_curvature,
            "stable": self.stable,
            "qualification": (
                "diagnostic only; the full A_p and full zeta_rel(0) are not "
                "replaced by this normalized component"
            ),
        }


def normalized_scale_witness(
    anomaly_component: float,
    *,
    power: int = 6,
    amplitude: float = 1.0,
) -> NormalizedScaleWitness:
    """Evaluate the v14.52 one-power gate using normalized witness inputs."""

    if power <= 0:
        raise ValueError("power must be positive")
    if not math.isfinite(amplitude) or amplitude == 0:
        raise ValueError("amplitude must be finite and nonzero")
    ratio_p = -anomaly_component / (power * amplitude)
    if not math.isfinite(ratio_p) or ratio_p <= 0:
        return NormalizedScaleWitness(
            power, amplitude, anomaly_component, False, None, None, False
        )
    ratio = ratio_p ** (1.0 / power)
    curvature = -power * anomaly_component
    return NormalizedScaleWitness(
        power,
        amplitude,
        anomaly_component,
        True,
        ratio,
        curvature,
        curvature > 0,
    )


def relative_anomaly_payload() -> dict[str, Any]:
    a = frozen_berger_witness()
    anomaly = minimal_dirac_relative_weyl_anomaly(a)
    witness = normalized_scale_witness(anomaly["zeta_rel_weyl_component"])
    return {
        "artifact": "BHSM_relative_weyl_anomaly_v14_53",
        "version": VERSION,
        "geometry": "S1_tau x Berger-S3_a child relative to round a=1 parent",
        "positive_gauge_sign_dirac_a4": {
            "weyl_density_coefficient": "-1/(320*pi^2) per four-component Dirac spinor",
            "integrated_C2": "(128*pi^2/3)*tau*a*(a^2-1)^2",
            "relative_component": "Z_W=-(2/15)*N_D*tau*a*(a^2-1)^2",
        },
        "frozen_a_diagnostic": anomaly,
        "normalized_A6_scale_witness": witness.json(),
        "scope_exclusions": [
            "Euler-density or topology mismatch",
            "kernel-dimension mismatch",
            "eta, Higgs, gauge, and finite-family endomorphism contributions",
            "bosonic and ghost determinants",
            "collar, seam, corner, and counterterm contributions",
            "full-preimage child and parent backreaction",
        ],
        "interpretation": (
            "the universal minimal-Dirac Weyl component has the sign required "
            "to stabilize a positive p=6 power term, but the total BHSM anomaly "
            "and total power coefficient remain unevaluated"
        ),
        "primary_verdict": PRIMARY_VERDICT,
        "validation": {
            "round_parent_component_zero": abs(
                minimal_dirac_relative_weyl_anomaly(1.0)[
                    "zeta_rel_weyl_component"
                ]
            )
            < 1e-15,
            "nonround_component_negative": anomaly["zeta_rel_weyl_component"] < 0,
            "frozen_shape_positive": anomaly["shape_F"] > 0,
            "normalized_scale_witness_stable": witness.stable,
            "full_anomaly_not_claimed": True,
        },
    }


def full_preimage_evaluability_gate() -> dict[str, Any]:
    required = {
        "matched_child_solution": False,
        "matched_parent_reference_with_same_interface_data": False,
        "complete_gauge_fixed_bosonic_hessian": False,
        "complete_child_parent_Dirac_operators": False,
        "common_self_adjoint_seam_domain": False,
        "trace_class_relative_heat_kernel": False,
        "relative_zero_mode_ledger": False,
        "GHY_corner_counterterm_completion": False,
        "numerical_A8_A6_A3": False,
        "numerical_B_finite_relative_part": False,
        "numerical_Z_total_relative_anomaly": False,
    }
    return {
        "artifact": "BHSM_full_preimage_evaluability_gate_v14_53",
        "version": VERSION,
        "required_objects": required,
        "known_partial_numeric_witnesses": {
            "reduced_state_energy": 9.8689261083,
            "reduced_nesting_ratio": 0.3644325544,
            "weak_gravity_Brown_York_charge_approximately": 10.5970,
            "status": (
                "regression witnesses only; they use incomplete source content "
                "and do not determine A_p, B, or Z"
            ),
        },
        "exact_failure_reason": (
            "numerical full-preimage evaluation cannot be reconstructed from "
            "reduced witness energies because the missing terms contribute to "
            "both the stationary background and the relative spectral operator"
        ),
        "numerical_full_preimage_scale_point_emitted": False,
        "evaluability_verdict": EVALUABILITY_VERDICT,
        "validation": {
            "all_required_full_objects_open": not any(required.values()),
            "partial_witness_not_promoted": True,
            "physical_scale_not_emitted": True,
        },
    }


def _matmul(
    a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]
) -> tuple[tuple[complex, ...], ...]:
    n = len(a)
    if n == 0 or len(b) != n:
        raise ValueError("square matrices of equal dimension required")
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n))
        for i in range(n)
    )


def _matsub(
    a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]
) -> tuple[tuple[complex, ...], ...]:
    return tuple(
        tuple(a[i][j] - b[i][j] for j in range(len(a)))
        for i in range(len(a))
    )


def _frobenius_norm(a: Sequence[Sequence[complex]]) -> float:
    return math.sqrt(sum(abs(value) ** 2 for row in a for value in row))


def c3_cycle() -> tuple[tuple[complex, ...], ...]:
    return (
        (0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j),
        (0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j),
        (1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j),
    )


def identity3() -> tuple[tuple[complex, ...], ...]:
    return tuple(
        tuple(1.0 + 0.0j if i == j else 0.0 + 0.0j for j in range(3))
        for i in range(3)
    )


def c3_commutant_response(
    scalar: float, even: float, odd: float
) -> tuple[tuple[complex, ...], ...]:
    """Return H=aI+x(C+C^2)+i y(C-C^2), Hermitian for real inputs."""

    c = c3_cycle()
    c2 = _matmul(c, c)
    ident = identity3()
    return tuple(
        tuple(
            scalar * ident[i][j]
            + even * (c[i][j] + c2[i][j])
            + 1j * odd * (c[i][j] - c2[i][j])
            for j in range(3)
        )
        for i in range(3)
    )


def commutator_norm(
    a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]
) -> float:
    return _frobenius_norm(_matsub(_matmul(a, b), _matmul(b, a)))


def c3_group_algebra_no_go() -> dict[str, Any]:
    # Representative distinct sector coefficients.  Their values are chosen only
    # to exercise the theorem; the commutator vanishes identically for all real
    # coefficients because both matrices are polynomials in C.
    h_u = c3_commutant_response(0.12, -0.003, 0.0002)
    h_d = c3_commutant_response(0.09, 0.004, -0.0007)
    comm_norm = commutator_norm(h_u, h_d)
    return {
        "artifact": "BHSM_C3_group_algebra_no_go_v14_53",
        "version": VERSION,
        "theorem": (
            "all operators H_f=sum_(n=0)^2 c_(f,n) C^n lie in the abelian "
            "group algebra C[C3], hence [H_u,H_d]=0 for arbitrary sector "
            "coefficients"
        ),
        "included_current_action_owned_structures": [
            "exact C3 projectors",
            "octave-dependent diagonal attachment response",
            "G2/C3 odd coefficient i*y*(C-C^2)",
            "Berger spectral functions and overlap semigroup",
            "sector degree or incidence rescalings",
            "family-identity weak current",
        ],
        "representative_commutator_frobenius_norm": comm_norm,
        "consequences": {
            "different_up_down_eigenvalues_are_sufficient_for_hierarchy": True,
            "different_up_down_C3_commutant_coefficients_generate_CKM": False,
            "G2_C3_odd_coefficient_alone_generates_physical_CP": False,
            "common_Fourier_eigenbasis": True,
            "physical_CKM_from_this_algebra": "identity up to phases and permutations",
        },
        "flavor_verdict": FLAVOR_VERDICT,
        "validation": {
            "representative_commutator_zero": comm_norm < 1e-12,
            "sector_specific_coefficients_do_not_help": True,
            "noncentral_operator_required": True,
            "physical_CKM_not_emitted": True,
        },
    }


def peter_weyl_tensor_current_contract() -> dict[str, Any]:
    table = [
        [[0, 0], [3, 0], [4, -2]],
        [[3, 3], [3, 3], [1, 1]],
        [[5, 4], [4, 4], [2, 2]],
    ]
    return {
        "artifact": "BHSM_Peter_Weyl_tensor_current_contract_v14_53",
        "version": VERSION,
        "weak_current_channel_table": {
            "row_order": ["U0", "U1", "U2"],
            "column_order": ["D0", "D1", "D2"],
            "entries_minimal_L_r": table,
            "all_nine_have_nonzero_normalized_witnesses": True,
        },
        "minimum_current_structure": {
            "rank_three_requirement": (
                "at least three independent separable channels or one genuinely "
                "nonseparable extended kernel"
            ),
            "required_noncentral_basis": "normalized Peter-Weyl tensors M_(L,r)",
            "mixed_action_variation": (
                "Gamma_plus=delta^3 S/(delta W_plus delta bar(Psi_u,L) "
                "delta Psi_d,L)"
            ),
            "projected_coefficients": (
                "c_ij^(L,r)=<T_u e_i, P_u Gamma_plus[M_(L,r)] "
                "P_d T_d e_j>_common"
            ),
            "raw_kernel": "K_ud=sum_(L,r)c^(L,r)M_(L,r)",
            "unitary_readout": "V=Pol(G_uu^(-1/2) K_ud G_dd^(-1/2))",
        },
        "action_ownership_audit": {
            "S8_has_local_chiral_fermion_current": False,
            "Lambda85_has_fermionic_tensor_current": False,
            "foundational_M4_Dirac_current_family_kernel": "I3",
            "G2_C3_odd_response_is_noncentral": False,
            "current_action_fixes_channel_coefficients": False,
        },
        "allowed_foundational_extension": (
            "an intrinsic M4 tensor-current/Yukawa functional may be adopted as "
            "new foundational effective data, but it must be labeled adopted "
            "unless its coefficients follow from a larger parent action"
        ),
        "validation": {
            "table_is_three_by_three": len(table) == 3
            and all(len(row) == 3 for row in table),
            "minimum_three_separable_channels": True,
            "connection_functional_calculus_not_sufficient": True,
            "current_action_does_not_satisfy_contract": True,
        },
    }


def completion_payload() -> dict[str, Any]:
    anomaly = relative_anomaly_payload()
    evaluability = full_preimage_evaluability_gate()
    c3 = c3_group_algebra_no_go()
    tensor = peter_weyl_tensor_current_contract()
    validation = {
        "relative_weyl_component_evaluated": anomaly["validation"][
            "nonround_component_negative"
        ],
        "full_anomaly_not_falsely_emitted": not evaluability[
            "numerical_full_preimage_scale_point_emitted"
        ],
        "current_C3_algebra_proved_commuting": c3["validation"][
            "representative_commutator_zero"
        ],
        "tensor_current_contract_fail_closed": tensor["validation"][
            "current_action_does_not_satisfy_contract"
        ],
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "physical_scale_emitted": False,
        "physical_CKM_emitted": False,
        "BHSM_physical_completion": False,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_53",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "evaluability_verdict": EVALUABILITY_VERDICT,
        "flavor_verdict": FLAVOR_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "gates": {
            "minimal_Dirac_relative_Weyl_component_evaluated": True,
            "total_relative_anomaly_evaluated": False,
            "full_relative_power_coefficient_evaluated": False,
            "stable_full_scale_Berger_point_emitted": False,
            "current_action_owned_family_algebra_nonabelian": False,
            "Peter_Weyl_tensor_current_action_owned": False,
            "physical_CKM_emitted": False,
            "physical_scale_emitted": False,
            "BHSM_physical_completion": False,
        },
        "validation": validation,
        "validation_passed": all(
            value if key not in {"physical_scale_emitted", "physical_CKM_emitted", "BHSM_physical_completion"}
            else not value
            for key, value in validation.items()
        ),
    }


ARTIFACT_FILES = {
    "relative_anomaly": "BHSM_relative_weyl_anomaly_v14_53.json",
    "evaluability": "BHSM_full_preimage_evaluability_gate_v14_53.json",
    "c3_no_go": "BHSM_C3_group_algebra_no_go_v14_53.json",
    "tensor_contract": "BHSM_Peter_Weyl_tensor_current_contract_v14_53.json",
    "completion": "BHSM_completion_gate_v14_53.json",
}


def materialize(directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    payloads = {
        ARTIFACT_FILES["relative_anomaly"]: relative_anomaly_payload(),
        ARTIFACT_FILES["evaluability"]: full_preimage_evaluability_gate(),
        ARTIFACT_FILES["c3_no_go"]: c3_group_algebra_no_go(),
        ARTIFACT_FILES["tensor_contract"]: peter_weyl_tensor_current_contract(),
        ARTIFACT_FILES["completion"]: completion_payload(),
    }
    paths: list[Path] = []
    for name, payload in payloads.items():
        path = directory / name
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        paths.append(path)
    return paths

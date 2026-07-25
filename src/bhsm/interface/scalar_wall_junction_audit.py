"""BHSM v6.1.5 scalar-wall junction and coefficient-source audit."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from scipy.integrate import solve_ivp
from scipy.optimize import brentq


VERSION = "v6.1.5"
SPRINT = "bhsm-scalar-wall-junction-audit-v6-1-5"
PRIMARY_RESULT = "BHSM_MINIMAL_P1_SCALAR_WALL_JUNCTION_NOT_FOUND"
COMPLETION_GATE = "V6_1_5_COUPLED_FINITE_AMPLITUDE_WALL_AND_MIXED_STABILITY_OPEN"

ARTIFACT_FILES = {
    "ledger": "BHSM_scalar_wall_action_convention_ledger_v6_1_5.json",
    "vacuum": "BHSM_scalar_vacuum_energy_shift_v6_1_5.json",
    "equations": "BHSM_curved_scalar_wall_equations_v6_1_5.json",
    "reduced": "BHSM_scalar_wall_reduced_action_crosscheck_v6_1_5.json",
    "parity": "BHSM_scalar_wall_parity_regularity_v6_1_5.json",
    "identity": "BHSM_scalar_wall_integral_identity_v6_1_5.json",
    "branch": "BHSM_scalar_wall_branch_audit_v6_1_5.json",
    "thin": "BHSM_scalar_wall_thin_limit_v6_1_5.json",
    "junction": "BHSM_scalar_wall_modified_junction_v6_1_5.json",
    "sources": "BHSM_scalar_wall_boundary_coefficient_source_map_v6_1_5.json",
    "shape": "BHSM_scalar_wall_Berger_shape_source_v6_1_5.json",
    "stability": "BHSM_scalar_wall_constraint_reduced_stability_v6_1_5.json",
    "hidden": "BHSM_scalar_wall_hidden_input_claim_audit_v6_1_5.json",
    "report": "BHSM_scalar_wall_junction_report_v6_1_5.json",
}

GUARDS = {
    "boundary_tension_inserted": False,
    "boundary_vacuum_constant_inserted": False,
    "new_parent_field_added": False,
    "new_scalar_interaction_added": False,
    "P2_or_P3_repair_used": False,
    "measured_input_used": False,
    "hard_coded_wall_thickness_used": False,
    "vacuum_energy_silently_subtracted": False,
    "bending_mode_called_sigma_partial": False,
    "numerical_null_promoted_to_theorem": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def stable_diagnostic(value: float, digits: int = 12) -> float:
    """Quantize solver diagnostics for cross-platform artifact identity."""
    return float(f"{value:.{digits}f}")


def scalar_vacua(A_5: float, G_5: float) -> dict[str, Any]:
    """Classify the stationary points of U=A sigma^2/2+G sigma^4/4."""
    rows: list[dict[str, Any]] = [
        {
            "sigma": 0.0,
            "hessian": A_5,
            "energy": 0.0,
            "local_minimum": A_5 > 0,
        }
    ]
    if G_5 != 0 and -A_5 / G_5 > 0:
        v = math.sqrt(-A_5 / G_5)
        energy = -(A_5**2) / (4 * G_5)
        rows.extend(
            {
                "sigma": sign * v,
                "hessian": -2 * A_5,
                "energy": energy,
                "local_minimum": A_5 < 0 and G_5 > 0,
            }
            for sign in (-1, 1)
        )
    return {
        "stationary_points": rows,
        "stable_double_well": A_5 < 0 and G_5 > 0,
        "signs_selected": False,
    }


def effective_kappa0(kappa_0: float, A_5: float, G_5: float) -> float:
    """Return kappa0+2 U(v), retaining the scalar vacuum energy exactly."""
    if not (A_5 < 0 and G_5 > 0):
        raise ValueError("the nonzero stable vacuum requires A_5<0 and G_5>0")
    return kappa_0 - A_5**2 / (2 * G_5)


def vacuum_sectional_curvature(
    kappa_0: float, kappa_1: float, A_5: float, G_5: float
) -> float:
    if kappa_1 <= 0:
        raise ValueError("kappa_1 must be positive")
    return effective_kappa0(kappa_0, A_5, G_5) / (12 * kappa_1)


def flat_control_wall(A_5: float, G_5: float, Z_5: float) -> dict[str, float]:
    """Controlled no-gravity diagnostic; it is not a curved BHSM solution."""
    if not (A_5 < 0 and G_5 > 0 and Z_5 > 0):
        raise ValueError("flat control wall requires A_5<0, G_5>0, Z_5>0")
    v = math.sqrt(-A_5 / G_5)
    inverse_width = math.sqrt(-A_5 / (2 * Z_5))
    tension = 2 * math.sqrt(2 * Z_5) * (-A_5) ** 1.5 / (3 * G_5)
    return {
        "v": v,
        "inverse_width": inverse_width,
        "width": 1 / inverse_width,
        "excess_tension": tension,
    }


def modified_junction_residual(
    X: float,
    q_vac: float,
    C_partial: float,
    kappa_1: float,
    tension: float,
) -> float:
    """Maximally symmetric thin-wall equation in the v6.1.4 orientation."""
    if kappa_1 <= 0:
        raise ValueError("kappa_1 must be positive")
    k = tension / (6 * kappa_1) - (C_partial / kappa_1) * X
    return X - q_vac - k**2


def _linear_cap_endpoint(mu: float, *, max_step: float, rtol: float) -> float:
    """Endpoint value for the q=1, X=2 critical-cap odd mode."""
    endpoint = math.pi / 4
    epsilon = 1.0e-7
    initial = [1 - mu * epsilon**2 / 10, -mu * epsilon / 5]

    def rhs(rho: float, state: list[float]) -> list[float]:
        phi, derivative = state
        return [derivative, -4 / math.tan(rho) * derivative - mu * phi]

    solution = solve_ivp(
        rhs,
        (epsilon, endpoint),
        initial,
        rtol=rtol,
        atol=rtol * 1.0e-2,
        max_step=max_step,
    )
    return float(solution.y[0, -1])


def lowest_odd_cap_eigenvalue(
    *, max_step: float = 0.005, rtol: float = 1.0e-12
) -> float:
    """Lowest Dirichlet-at-junction, regular-at-cap scalar eigenvalue."""
    return float(
        brentq(
            lambda mu: _linear_cap_endpoint(mu, max_step=max_step, rtol=rtol),
            29.0,
            30.0,
            xtol=1.0e-13,
        )
    )


def _nonlinear_probe_endpoint(
    cap_value: float, A_over_Z: float, G_over_Z: float, *, max_step: float, rtol: float
) -> float:
    endpoint = math.pi / 4
    epsilon = 1.0e-6
    force = A_over_Z * cap_value + G_over_Z * cap_value**3
    initial = [cap_value + force * epsilon**2 / 10, force * epsilon / 5]

    def rhs(rho: float, state: list[float]) -> list[float]:
        sigma, derivative = state
        return [
            derivative,
            A_over_Z * sigma
            + G_over_Z * sigma**3
            - 4 / math.tan(rho) * derivative,
        ]

    solution = solve_ivp(
        rhs,
        (epsilon, endpoint),
        initial,
        rtol=rtol,
        atol=rtol * 1.0e-2,
        max_step=max_step,
    )
    return float(solution.y[0, -1])


def fixed_background_probe_amplitude(
    *, A_over_Z: float = -35.0, G_over_Z: float = 1.0,
    max_step: float = 0.005, rtol: float = 1.0e-10
) -> float:
    """Nonzero fixed-background profile; deliberately excludes backreaction."""
    if not (A_over_Z < -lowest_odd_cap_eigenvalue() and G_over_Z > 0):
        raise ValueError("probe branch requires a supercritical negative quadratic term")
    return float(
        brentq(
            lambda value: _nonlinear_probe_endpoint(
                value, A_over_Z, G_over_Z, max_step=max_step, rtol=rtol
            ),
            4.0,
            4.1,
            xtol=1.0e-12,
        )
    )


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "The frozen scalar polynomial admits a regular odd fixed-background "
            "cap profile beyond a derived spectral threshold, but no finite-amplitude "
            "coupled Einstein-scalar-B1 branch or mixed-stability proof is established."
        ),
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    c = _common
    eigenvalue_rows = [
        {
            "max_step": step,
            "rtol": tolerance,
            "mu1_over_q5": stable_diagnostic(
                lowest_odd_cap_eigenvalue(max_step=step, rtol=tolerance)
            ),
        }
        for step, tolerance in (
            (0.02, 1.0e-8),
            (0.01, 1.0e-10),
            (0.005, 1.0e-12),
        )
    ]
    probe_rows = [
        {
            "max_step": step,
            "rtol": tolerance,
            "cap_amplitude": stable_diagnostic(
                fixed_background_probe_amplitude(max_step=step, rtol=tolerance)
            ),
        }
        for step, tolerance in (
            (0.02, 1.0e-8),
            (0.01, 1.0e-9),
            (0.005, 1.0e-10),
        )
    ]
    mu1 = eigenvalue_rows[-1]["mu1_over_q5"]
    return {
        "ledger": {
            **c("BHSM_scalar_wall_action_convention_ledger_v6_1_5"),
            "status": "BHSM_SCALAR_WALL_ACTION_AND_CONVENTIONS_FROZEN",
            "signature": "(-,+,+,+,+)",
            "metric": "ds5^2=N(rho)^2 d rho^2+a(rho)^2 h_mu_nu dx^mu dx^nu",
            "h_curvature": "R_mu_nu(h)=3X h_mu_nu",
            "normal": "n=N^-1 partial_rho; K_mu_nu=(1/2)L_n h_mu_nu",
            "GHY": "+kappa_1 integral sqrt(-h) K on each oriented cap",
            "bulk_action": "integral sqrt(-g)[kappa_1 R5/2-kappa_0/2-Z5(grad sigma)^2/2-U5(sigma)]",
            "U5": "A5 sigma^2/2+G5 sigma^4/4",
            "B1": "integral sqrt(-h)[C_partial R4-tau_A Tr(F^2)/4-Z_partial(partial sigma_partial)^2/2]",
            "dimensions": {
                "sigma_parent": "L^0",
                "kappa_1_M5": "L^-3",
                "kappa_0_M5": "L^-5",
                "Z5": "L^-3",
                "A5": "L^-5",
                "G5": "L^-5",
                "parent_Zsigma": "L^-6",
                "parent_A0": "L^-8",
                "parent_G0": "L^-8",
            },
            "pushforward": "[Z5,A5,G5]=Vol(S3)[Zsigma,A0,G0] on the frozen internal slice",
            "field_domain": "sigma is the existing neutral bulk singlet; sigma_partial is an independent provisional B1 field",
            "Z2_distinction": "sigma -> -sigma is internal; rho -> -rho exchanges caps",
            "unselected_signs": ["A5", "G5"],
            "positive_principal_coefficients": ["kappa_1", "Z5", "C_partial", "tau_A", "Z_partial"],
        },
        "vacuum": {
            **c("BHSM_scalar_vacuum_energy_shift_v6_1_5"),
            "status": "BHSM_SCALAR_VACUUM_ENERGY_SHIFT_DERIVED",
            "stationary": "sigma=0; sigma=±sqrt(-A5/G5) when -A5/G5>0",
            "stable_double_well": "A5<0 and G5>0",
            "hessians": {"zero": "A5", "nonzero": "-2A5"},
            "U_vac": "-A5^2/(4G5)",
            "kappa0_eff": "kappa_0+2U_vac=kappa_0-A5^2/(2G5)",
            "q5_vac": "kappa0_eff/(12kappa_1)",
            "positive_cap_condition": "kappa_0>A5^2/(2G5)",
            "vacua_gravitationally_degenerate": True,
            "constant_subtracted": False,
        },
        "equations": {
            **c("BHSM_curved_scalar_wall_equations_v6_1_5"),
            "status": "BHSM_CURVED_SCALAR_WALL_EQUATIONS_DERIVED",
            "proper_normal_gauge": "N=1 only after variation; H_rho=a'/a",
            "scalar": "Z5[sigma''+4H_rho sigma']=A5 sigma+G5 sigma^3",
            "normal_constraint": "6kappa_1[H_rho^2-X/a^2]+kappa_0/2=Z5 sigma'^2/2-U5",
            "tangential": "3kappa_1[a''/a+H_rho^2-X/a^2]+kappa_0/2=-Z5 sigma'^2/2-U5",
            "monotonicity": "H_rho'+X/a^2=-Z5 sigma'^2/(3kappa_1)",
            "regular_acceleration": "a''=-a[kappa_0/2+U5+3Z5 sigma'^2/2]/(6kappa_1)",
            "stress": {
                "T_rho_rho": "Z5 sigma'^2/2-U5",
                "T_mu_nu": "-[Z5 sigma'^2/2+U5]g_mu_nu",
            },
            "Bianchi": "the rho derivative of the constraint vanishes after the scalar and tangential equations",
            "junction": "smooth bulk sigma has no delta stress; the B1 metric junction remains kappa_1[Q]+2C_partial G4=T_boundary",
        },
        "reduced": {
            **c("BHSM_scalar_wall_reduced_action_crosscheck_v6_1_5"),
            "status": "BHSM_SCALAR_WALL_REDUCED_ACTION_CROSSCHECK_PASSED",
            "lapse_retained": True,
            "L1D": "6kappa_1[a^2 a'^2/N+N X a^2]-N a^4[kappa_0/2+U5]-a^4 Z5 sigma'^2/(2N)",
            "boundary_terms": "GHY cancels the radial second derivative before the displayed reduction",
            "delta_N": "normal Einstein constraint",
            "delta_sigma": "scalar Euler-Lagrange equation",
            "delta_a": "tangential Einstein equation after using the constraint",
            "independent_route": "direct warped-product Einstein tensor",
            "factor_crosscheck": True,
        },
        "parity": {
            **c("BHSM_scalar_wall_parity_regularity_v6_1_5"),
            "status": "BHSM_COMPACT_DOUBLE_CAP_KINK_REGULARITY_CLASSIFIED",
            "classes": {
                "even": "sigma'(0)=0; same pullback on both caps; no topological sign change",
                "odd": "sigma(0)=0; sigma' continuous in a global normal coordinate; opposite cap signs allowed",
                "same_vacuum_lump": "requires an interior turn and is not selected by parity",
                "opposite_vacuum_kink": "requires cap values ±v in addition to regularity and was not solved",
            },
            "cap_regularity": "a=0, |sigma| finite, sigma'=0 in the regular radial coordinate",
            "central_delta_stress_for_finite_width": False,
            "B1_compatibility": "odd bulk pullback is zero; it does not equal or source sigma_partial without a map",
            "second_junction_required": False,
            "topology_forces_zero_for_odd_class": True,
        },
        "identity": {
            **c("BHSM_scalar_wall_integral_identity_v6_1_5"),
            "status": "BHSM_SCALAR_WALL_NECESSARY_SIGN_IDENTITIES_DERIVED",
            "flux": "[a^4 Z5 sigma']_cap^junction=integral a^4 U5'(sigma)d rho",
            "virial": "integral a^4[Z5 sigma'^2+A5 sigma^2+G5 sigma^4]d rho=0 for odd Dirichlet junction and regular cap",
            "exact_no_go": "for Z5>0, A5>=0, G5>=0 only sigma=0 satisfies the identity",
            "stable_wall_necessary_sign": "A5<0 and G5>0",
            "monotonicity": "H_rho'+X/a^2<=0 for kappa_1,Z5>0",
            "global_exclusion_claimed": False,
        },
        "branch": {
            **c("BHSM_scalar_wall_branch_audit_v6_1_5"),
            "status": PRIMARY_RESULT,
            "vacuum_regression": {
                "q5": 1.0,
                "X": 2.0,
                "C_partial_over_kappa_1": 0.5,
                "cap_warp": "a=sqrt(2) sin(rho)",
                "junction_rho": "pi/4",
                "junction_residual": 0.0,
            },
            "linear_operator": "-a^-4 d_rho(a^4 d_rho), regular at rho=0 and Dirichlet at rho=pi/4",
            "eigenvalue_convergence": eigenvalue_rows,
            "critical_ratio": f"A5/Z5=-{mu1:.12f} q5 on the critical cap",
            "fixed_background_probe": {
                "A5_over_Z5": -35.0,
                "G5_over_Z5": 1.0,
                "convergence": probe_rows,
                "classification": "regular nonlinear scalar profile on the frozen metric only",
            },
            "coupled_backreaction_included": False,
            "finite_amplitude_coupled_branch_found": False,
            "numerical_domain": "critical q5=1,X=2 cap; one supercritical fixed-background point",
            "outcome": "probe branch found; coupled BVP not found/closed",
            "not_a_global_theorem": True,
        },
        "thin": {
            **c("BHSM_scalar_wall_thin_limit_v6_1_5"),
            "status": "BHSM_SCALAR_WALL_THIN_LIMIT_DERIVED_CONDITIONALLY",
            "definition": "integrate T_AB(wall)-T_AB(selected vacuum), never the full vacuum energy",
            "flat_control": {
                "v": "sqrt(-A5/G5)",
                "delta": "sqrt(2Z5/(-A5))",
                "T_excess": "2sqrt(2Z5)(-A5)^(3/2)/(3G5)",
            },
            "curved_BHSM_tension": None,
            "normal_pressure": "vanishes in the exact flat control by the first integral",
            "tangential_surface_stress": "-T_excess h_mu_nu",
            "anisotropic_stress": 0,
            "scope": "diagnostic formula pending a controlled curved, backreacted limit",
        },
        "junction": {
            **c("BHSM_scalar_wall_modified_junction_v6_1_5"),
            "status": "BHSM_SCALAR_WALL_JUNCTION_POLYNOMIAL_DERIVED_CONDITIONALLY",
            "thin_surface_equation": "k=T/(6kappa_1)-(C_partial/kappa_1)X",
            "Gauss": "X=q5_vac+k^2",
            "polynomial": "X=q5_vac+[T/(6kappa_1)-(C_partial/kappa_1)X]^2",
            "zero_tension_regression": "eta^2 X^2-X+q5=0",
            "T_source": "must be the excess stress of a curved solution; no independent tension was inserted",
            "finite_width_wall": "smooth stress modifies cap equations but contributes no junction delta",
        },
        "sources": {
            **c("BHSM_scalar_wall_boundary_coefficient_source_map_v6_1_5"),
            "status": "BHSM_SCALAR_WALL_B1_COEFFICIENT_SOURCE_FAILURE_DERIVED",
            "map": {
                "C_partial": {
                    "parent_term": None,
                    "profile_integral": None,
                    "status": "BHSM_SCALAR_WALL_DOES_NOT_GENERATE_CPARTIAL",
                    "reason": "minimal stress changes background/junction tension but is not an intrinsic R4 kinetic term",
                },
                "tau_A": {
                    "parent_term": None,
                    "profile_integral": None,
                    "status": "BHSM_SCALAR_WALL_DOES_NOT_GENERATE_TAUA",
                    "reason": "the frozen P1 action has no sigma-dependent F^2 coefficient",
                },
                "Z_partial": {
                    "parent_term": "bulk scalar kinetic term",
                    "profile_integral": "T_excess for a normalizable translation collective coordinate",
                    "status": "BHSM_WALL_BENDING_SCALAR_NORMALIZATION_DERIVED_CONDITIONALLY",
                    "reason": "the bending coordinate is an embedding mode, not the declared sigma_partial without an action/domain map",
                },
            },
            "independent_B1_primitives_removed": [],
        },
        "shape": {
            **c("BHSM_scalar_wall_Berger_shape_source_v6_1_5"),
            "status": "BHSM_SINGLET_WALL_BERGER_SOURCE_VANISHES",
            "stress_difference": "p1-p2=0",
            "reason": "a minimally coupled (J,m)=(0,0) scalar has isotropic tangential stress",
            "Berger_split_sourced": False,
            "round_shape_diagonal": "retains the positive v6.1 principal shape terms at zero wall amplitude",
            "wall_shape_mixing": "begins through metric dependence at quadratic order and is not diagonalized",
            "healthy_coexistence_proved": False,
        },
        "stability": {
            **c("BHSM_scalar_wall_constraint_reduced_stability_v6_1_5"),
            "status": "BHSM_SCALAR_WALL_MIXED_STABILITY_OPEN",
            "closed_sector_requested": [
                "wall scalar fluctuation",
                "translation/bending mode",
                "metric scalar",
                "junction displacement",
                "two Berger shape modes",
            ],
            "constraints_to_remove": ["bulk lapse", "bulk shift", "boundary lapse", "normal diffeomorphism"],
            "known_linear_entry": f"lambda_wall,1=mu1 q5+A5/Z5 with mu1={mu1:.12f}",
            "translation_zero_mode": "only exact before compact cap and fixed-junction boundary conditions lift or gauge it",
            "negative_modes": None,
            "full_matrix_constructed": False,
            "stability_claimed": False,
        },
        "hidden": {
            **c("BHSM_scalar_wall_hidden_input_claim_audit_v6_1_5"),
            "status": "BHSM_SCALAR_WALL_HIDDEN_INPUTS_EXPOSED",
            "primitive_inputs": ["kappa_0", "kappa_1", "Z5", "A5", "G5", "C_partial"],
            "signs_not_selected": ["A5", "G5"],
            "not_imported": [
                "measured masses",
                "measured couplings",
                "cosmological parameters",
                "absolute length",
                "fitted wall thickness",
            ],
            "probe_normalization": "q5=1 is dimensionless; all reported thresholds are ratios",
            "remaining_hidden_choices": [
                "scalar sign domain",
                "cap root",
                "finite-amplitude continuation path",
                "mixed fluctuation boundary conditions",
            ],
        },
        "report": {
            **c("BHSM_scalar_wall_junction_report_v6_1_5"),
            "status": PRIMARY_RESULT,
            "central_answer": (
                "The retained scalar vacuum energy shifts kappa_0 exactly. "
                "A regular odd fixed-background cap profile exists beyond a "
                "derived spectral threshold, so the scalar mechanism is not "
                "excluded. A finite-amplitude coupled Einstein-scalar-B1 wall "
                "satisfying the junction and mixed-stability problem was not "
                "constructed. Minimal scalar stress generates neither "
                "C_partial nor tau_A; its possible bending mode is not the "
                "declared B1 scalar without an additional map."
            ),
            "derived": [
                "vacuum-energy shift",
                "Gaussian-normal Einstein-scalar equations",
                "reduced-action crosscheck",
                "parity and regularity conditions",
                "integral identity and A5>=0 no-go domain",
                "critical-cap odd spectral threshold",
                "B1 coefficient-source failures",
                "isotropic Berger shape source",
            ],
            "conditional": [
                "fixed-background nonlinear profile",
                "flat control tension",
                "thin-wall junction polynomial",
                "bending-mode normalization",
            ],
            "invalidated": [
                "silent scalar vacuum-energy subtraction",
                "flat kink treated as a curved solution",
                "minimal wall stress identified with C_partial",
                "minimal wall stress identified with tau_A",
                "bulk wall identified automatically with sigma_partial",
            ],
            "open": [
                "finite-amplitude coupled backreacted BVP",
                "opposite-vacuum cap endpoint solution",
                "controlled curved thin-wall limit",
                "mixed scalar-metric-junction-Berger spectrum",
                "parent source of B1 coefficients",
            ],
            "completion_gate": COMPLETION_GATE,
            "full_bhsm_status": "FULL_BHSM_NOT_COMPLETE",
        },
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    paths: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths


def scalar_wall_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {
        key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()
    }
    return report


def scalar_wall_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# BHSM v6.1.5 Scalar-Wall Junction Audit",
            "",
            f"Primary result: `{report['primary_result']}`.",
            "",
            report["central_answer"],
            "",
            f"Next gate: `{report['completion_gate']}`.",
            "",
            "`FULL_BHSM_NOT_COMPLETE`.",
        ]
    ) + "\n"

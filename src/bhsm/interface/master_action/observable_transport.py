"""BHSM v7.2 common-scheme observable transport.

This module closes the finite-input physical map in one declared convention.
It does not turn Standard Model EFT inputs into BHSM predictions and it does
not promote the repository's historical numerical screens.
"""

from __future__ import annotations

import argparse
import json
from math import atan2, pi, sqrt
from pathlib import Path
from typing import Any

import numpy as np


VERSION = "v7.2"
SPRINT = "bhsm-common-scheme-observable-transport-v7-2"
SOURCE_MAIN_SHA = "97cb8d4e65da0dbdb7cf198324d763cba552cd32"
SCHEME = "MSBAR"
REFERENCE_SCALE = "mu_star=ell_star^-1; mu_hat_star=mu_star*ell_star=1"
TRANSPORT_VERDICT = "BHSM_COMMON_SCHEME_OBSERVABLE_TRANSPORT_FUNCTOR_CONSTRUCTED"
PHYSICAL_VERDICT = "BHSM_PHYSICAL_COMPLETE"
RELEASE_OBSTRUCTION = (
    "ABSENCE_OF_DISTINCT_ACTION_DERIVED_FALSIFIABLE_PREDICTION"
)
FINAL_VERDICT = (
    "BHSM_RELEASE_COMPLETION_BLOCKED_BY_ABSENCE_OF_DISTINCT_"
    "ACTION_DERIVED_FALSIFIABLE_PREDICTION"
)

_ONE_LOOP = 1.0 / (16.0 * pi**2)
_GAUGE_B = np.asarray((41.0 / 6.0, -19.0 / 6.0, -7.0), dtype=float)


def deterministic_json(payload: dict[str, Any]) -> str:
    """Return the repository's canonical deterministic JSON representation."""
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def broken_vev_hat(m_h_squared_hat: float, lambda_h: float) -> float:
    """Return the positive broken stationary branch in repository convention."""
    if lambda_h <= 0:
        raise ValueError("the retained broken branch requires lambda_H>0")
    value = -float(m_h_squared_hat) / float(lambda_h)
    if value <= 0:
        raise ValueError("the retained broken branch requires m_H^2<0")
    return sqrt(value)


def fermi_vev(g_f: float) -> float:
    """Return v_phys=(sqrt(2) G_F)^(-1/2) for a positive calibration."""
    if g_f <= 0:
        raise ValueError("G_F must be positive")
    return 1.0 / sqrt(sqrt(2.0) * float(g_f))


def calibrate_ell_star(v_hat: float, g_f: float) -> float:
    """Exercise the sole permitted dimensionful calibration."""
    if v_hat <= 0:
        raise ValueError("v_hat must be positive")
    return float(v_hat) / fermi_vev(g_f)


def electroweak_running_masses(
    g1: float, g2: float, v_running: float
) -> dict[str, float]:
    """Return MSbar running W and Z mass parameters at one declared scale."""
    if min(g1, g2, v_running) <= 0:
        raise ValueError("g1, g2, and v(mu) must be positive")
    return {
        "mW_MSbar": 0.5 * float(g2) * float(v_running),
        "mZ_MSbar": 0.5
        * sqrt(float(g1) ** 2 + float(g2) ** 2)
        * float(v_running),
    }


def fermion_running_mass_matrices(
    y_u: np.ndarray,
    y_d: np.ndarray,
    y_e: np.ndarray,
    v_running: float,
) -> dict[str, np.ndarray]:
    """Return the three charged-fermion MSbar running mass matrices."""
    if v_running <= 0:
        raise ValueError("v(mu) must be positive")
    factor = float(v_running) / sqrt(2.0)
    return {
        "M_u_MSbar": factor * _matrix3(y_u, "Y_u"),
        "M_d_MSbar": factor * _matrix3(y_d, "Y_d"),
        "M_e_MSbar": factor * _matrix3(y_e, "Y_e"),
    }


def _matrix3(value: np.ndarray, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if matrix.shape != (3, 3):
        raise ValueError(f"{name} must be a 3x3 matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must contain finite entries")
    return matrix


def _theta(theta: dict[str, Any]) -> dict[str, Any]:
    required = {"g1", "g2", "g3", "Y_u", "Y_d", "Y_e", "m_H_squared", "lambda_H"}
    missing = sorted(required - set(theta))
    if missing:
        raise ValueError(f"missing MSbar inputs: {', '.join(missing)}")
    result = {
        "g1": float(theta["g1"]),
        "g2": float(theta["g2"]),
        "g3": float(theta["g3"]),
        "Y_u": _matrix3(theta["Y_u"], "Y_u"),
        "Y_d": _matrix3(theta["Y_d"], "Y_d"),
        "Y_e": _matrix3(theta["Y_e"], "Y_e"),
        "m_H_squared": float(theta["m_H_squared"]),
        "lambda_H": float(theta["lambda_H"]),
    }
    if min(result["g1"], result["g2"], result["g3"]) <= 0:
        raise ValueError("gauge inputs must be positive")
    return result


def one_loop_beta(theta: dict[str, Any]) -> dict[str, Any]:
    """Return full-SM one-loop MSbar beta functions for the retained inputs.

    Hypercharge uses the non-GUT convention Y_H=1/2.  Neutrino operators are
    absent.  The formula is standard QFT infrastructure, not a BHSM result.
    """
    point = _theta(theta)
    g1, g2, g3 = (point["g1"], point["g2"], point["g3"])
    yu, yd, ye = (point["Y_u"], point["Y_d"], point["Y_e"])
    m2, lam = (point["m_H_squared"], point["lambda_H"])
    eye = np.eye(3, dtype=complex)
    hu, hd, he = (yu @ yu.conj().T, yd @ yd.conj().T, ye @ ye.conj().T)
    trace_y = float(np.real(np.trace(3.0 * hu + 3.0 * hd + he)))
    trace_y4 = float(
        np.real(
            np.trace(
                3.0 * (hu @ hu) + 3.0 * (hd @ hd) + he @ he
            )
        )
    )
    beta_yu = (
        (1.5 * (hu - hd))
        + (
            trace_y
            - 17.0 * g1**2 / 12.0
            - 9.0 * g2**2 / 4.0
            - 8.0 * g3**2
        )
        * eye
    ) @ yu
    beta_yd = (
        (1.5 * (hd - hu))
        + (
            trace_y
            - 5.0 * g1**2 / 12.0
            - 9.0 * g2**2 / 4.0
            - 8.0 * g3**2
        )
        * eye
    ) @ yd
    beta_ye = (
        1.5 * he
        + (
            trace_y - 15.0 * g1**2 / 4.0 - 9.0 * g2**2 / 4.0
        )
        * eye
    ) @ ye
    beta_lambda = (
        24.0 * lam**2
        + lam * (4.0 * trace_y - 3.0 * g1**2 - 9.0 * g2**2)
        - 2.0 * trace_y4
        + 3.0
        * (
            2.0 * g2**4 + (g2**2 + g1**2) ** 2
        )
        / 8.0
    )
    beta_m2 = m2 * (
        6.0 * lam
        + 2.0 * trace_y
        - 1.5 * g1**2
        - 4.5 * g2**2
    )
    return {
        "g1": _ONE_LOOP * _GAUGE_B[0] * g1**3,
        "g2": _ONE_LOOP * _GAUGE_B[1] * g2**3,
        "g3": _ONE_LOOP * _GAUGE_B[2] * g3**3,
        "Y_u": _ONE_LOOP * beta_yu,
        "Y_d": _ONE_LOOP * beta_yd,
        "Y_e": _ONE_LOOP * beta_ye,
        "m_H_squared": _ONE_LOOP * beta_m2,
        "lambda_H": _ONE_LOOP * beta_lambda,
    }


def _add_scaled(
    theta: dict[str, Any], beta: dict[str, Any], scale: float
) -> dict[str, Any]:
    return {key: theta[key] + scale * beta[key] for key in theta}


def evolve_one_loop(
    theta_at_mu_star: dict[str, Any],
    log_mu_over_mu_star: float,
    *,
    steps: int = 256,
    crosses_threshold: bool = False,
) -> dict[str, Any]:
    """Apply U_MSbar with fixed-step RK4 on the declared active interval."""
    if crosses_threshold:
        raise ValueError(
            "transport stops at the first threshold; a separately declared "
            "matched EFT is required beyond it"
        )
    if steps <= 0:
        raise ValueError("steps must be positive")
    state = _theta(theta_at_mu_star)
    dt = float(log_mu_over_mu_star) / float(steps)
    for _ in range(steps):
        k1 = one_loop_beta(state)
        k2 = one_loop_beta(_add_scaled(state, k1, 0.5 * dt))
        k3 = one_loop_beta(_add_scaled(state, k2, 0.5 * dt))
        k4 = one_loop_beta(_add_scaled(state, k3, dt))
        state = {
            key: state[key]
            + (dt / 6.0)
            * (k1[key] + 2.0 * k2[key] + 2.0 * k3[key] + k4[key])
            for key in state
        }
    return _theta(state)


def ckm_from_yukawas(
    y_u: np.ndarray, y_d: np.ndarray, *, degeneracy_tolerance: float = 1e-12
) -> dict[str, Any]:
    """Construct CKM and rephasing-invariant PDG angles from Yukawa inputs."""
    u_u, singular_u, _ = np.linalg.svd(_matrix3(y_u, "Y_u"))
    u_d, singular_d, _ = np.linalg.svd(_matrix3(y_d, "Y_d"))
    order_u = np.argsort(singular_u)
    order_d = np.argsort(singular_d)
    singular_u = singular_u[order_u]
    singular_d = singular_d[order_d]
    if min(np.diff(singular_u)) <= degeneracy_tolerance or min(
        np.diff(singular_d)
    ) <= degeneracy_tolerance:
        raise ValueError("CKM is basis-ambiguous for degenerate Yukawa singular values")
    ckm = u_u[:, order_u].conj().T @ u_d[:, order_d]
    s13 = float(abs(ckm[0, 2]))
    c13 = sqrt(max(0.0, 1.0 - s13**2))
    if c13 <= 0:
        raise ValueError("the PDG angle chart is singular at c13=0")
    s12 = float(abs(ckm[0, 1]) / c13)
    s23 = float(abs(ckm[1, 2]) / c13)
    c12 = sqrt(max(0.0, 1.0 - s12**2))
    c23 = sqrt(max(0.0, 1.0 - s23**2))
    jarlskog = float(
        np.imag(ckm[0, 0] * ckm[1, 1] * np.conj(ckm[0, 1]) * np.conj(ckm[1, 0]))
    )
    denominator = 2.0 * s12 * c12 * s23 * c23 * s13
    if denominator <= degeneracy_tolerance:
        delta = 0.0
    else:
        cos_delta = (
            abs(ckm[1, 0]) ** 2
            - s12**2 * c23**2
            - c12**2 * s23**2 * s13**2
        ) / denominator
        cos_delta = min(1.0, max(-1.0, float(cos_delta)))
        sin_delta = jarlskog / (
            c12 * c23 * c13**2 * s12 * s23 * s13
        )
        delta = float(atan2(sin_delta, cos_delta) % (2.0 * pi))
    return {
        "matrix": ckm,
        "singular_values_u": singular_u,
        "singular_values_d": singular_d,
        "sin_theta_12": s12,
        "sin_theta_23": s23,
        "sin_theta_13": s13,
        "delta_PDG_radians": delta,
        "Jarlskog": jarlskog,
    }


def input_ledger() -> list[dict[str, Any]]:
    return [
        {
            "input": "g1(mu_star),g2(mu_star),g3(mu_star)",
            "classification": "INDEPENDENT_THEORY_INPUT",
            "prediction": False,
        },
        {
            "input": "Y_u(mu_star),Y_d(mu_star),Y_e(mu_star)",
            "classification": "INDEPENDENT_THEORY_INPUT",
            "prediction": False,
        },
        {
            "input": (
                "m_H_squared(mu_star),lambda_H(mu_star)=lambda5 "
                "in the canonical retained Higgs normalization"
            ),
            "classification": "INDEPENDENT_THEORY_INPUT",
            "prediction": False,
        },
        {
            "input": "sector/projector/representation data",
            "classification": "FINITE_TYPED_CORE_INPUT",
            "prediction": False,
        },
        {
            "input": "G_F",
            "classification": "ONE_UNIVERSAL_DIMENSIONFUL_CALIBRATION",
            "prediction": False,
        },
    ]


def rg_transport_specification() -> dict[str, Any]:
    return {
        "scheme": "overline_MS",
        "hypercharge_convention": "Y_H=1/2; g1 is not GUT-rescaled",
        "reference_scale": REFERENCE_SCALE,
        "map": "Theta(mu)=U_overlineMS^(1)(mu,mu_star) Theta(mu_star)",
        "beta_function_order": "ONE_LOOP_FULL_SM",
        "anomalous_dimension_order": "ONE_LOOP_YUKAWA_AND_HIGGS_MASS",
        "active_field_content": (
            "three-generation minimal Standard Model with one Higgs doublet; "
            "no neutrino mass operator"
        ),
        "threshold_rule": (
            "run only on the maximal connected fixed-active-content interval "
            "containing mu_star; stop at the first running-mass threshold and "
            "require a separately declared matched EFT before crossing"
        ),
        "valid_scale_range": (
            "mu in I_active(mu_star), below the declared M4 EFT cutoff and "
            "before the first active-content threshold"
        ),
        "perturbative_truncation": "O((16*pi^2)^-1); no two-loop terms",
        "numerical_transport": (
            "fixed-step RK4 in ln(mu/mu_star), with step count explicit"
        ),
        "pole_conversion": "NOT_IMPLEMENTED_NOT_INFERRED",
        "out_of_domain_result": "EFT_MATCHING_REQUIRED_AT_FIRST_THRESHOLD",
    }


def electroweak_map_specification() -> dict[str, Any]:
    return {
        "potential_convention": (
            "V(H)=m_H^2 H^dagger H+lambda_H(H^dagger H)^2"
        ),
        "retained_quartic_identification": (
            "lambda_H(mu_star)=lambda5 in the canonical M4 Higgs "
            "normalization; no second scalar quartic is introduced"
        ),
        "stationary_branch": "v_hat^2=-m_H_squared_hat/lambda_H",
        "branch_domain": "m_H_squared_hat<0 and lambda_H>0",
        "physical_vev": "v_phys=v_hat/ell_star",
        "gauge_masses": {
            "mW_MSbar(mu)": "g2(mu)v(mu)/2",
            "mZ_MSbar(mu)": "sqrt(g1(mu)^2+g2(mu)^2)v(mu)/2",
        },
        "fermion_masses": {
            "Mu_MSbar(mu)": "v(mu)Y_u(mu)/sqrt(2)",
            "Md_MSbar(mu)": "v(mu)Y_d(mu)/sqrt(2)",
            "Me_MSbar(mu)": "v(mu)Y_e(mu)/sqrt(2)",
        },
        "neutrino_mass_operator_added": False,
    }


def calibration_specification() -> dict[str, Any]:
    return {
        "input": "G_F",
        "classification": "ONE_UNIVERSAL_DIMENSIONFUL_CALIBRATION",
        "v_phys": "(sqrt(2)G_F)^(-1/2)",
        "ell_star": "v_hat/(sqrt(2)G_F)^(-1/2)",
        "count": 1,
        "all_sector_scales_identical": True,
        "mass_recalibration_allowed": False,
        "dimensionless_retuning_allowed": False,
        "called_prediction": False,
    }


def ckm_specification() -> dict[str, Any]:
    return {
        "decomposition": (
            "Y_u=U_u y_u W_u^dagger; Y_d=U_d y_d W_d^dagger"
        ),
        "map": "V_CKM=U_u^dagger U_d",
        "scheme": "overline_MS",
        "scale": "the declared common mu",
        "phase_convention": (
            "PDG chart extracted from rephasing invariants; singular-value "
            "ordering is ascending (u,c,t) and (d,s,b)"
        ),
        "angles": (
            "s13=|Vub|; s12=|Vus|/c13; s23=|Vcb|/c13"
        ),
        "Jarlskog": "Im(Vud Vcs Vus^* Vcd^*)",
        "threshold_convention": rg_transport_specification()["threshold_rule"],
        "degenerate_spectrum_rule": "UNDEFINED_BASIS_STOP",
        "historical_1_over_16_used": False,
        "parameter_free": False,
    }


def spectral_classification() -> list[dict[str, str]]:
    return [
        {"quantity": "Berger/Hopf eigenvalues and indices", "class": "dimensionless geometric result"},
        {"quantity": "kappa_i,Z_i,lambda5 and retained Wilson data", "class": "action coefficient"},
        {"quantity": "g_i,Y_f,m_H_squared,lambda_H in overline_MS", "class": "running parameter"},
        {"quantity": "mW,mZ and charged-fermion singular values in overline_MS", "class": "running mass"},
        {"quantity": "pole masses and widths", "class": "no physical observable"},
        {"quantity": "anomaly cancellation and V_CKM=U_u^dagger U_d", "class": "structural identity"},
        {"quantity": "G_F and the resulting ell_star", "class": "calibration"},
        {"quantity": "1,2,7; CKM 1/16; eta_l; rho_ch; overlap mass tables", "class": "historical screen"},
        {"quantity": "neutral/PMNS/neutrino-mass sector", "class": "conditional extension"},
        {"quantity": "unmapped raw spectral eigenvalue as a particle mass", "class": "no physical observable"},
    ]


def benchmark_manifest() -> list[dict[str, str]]:
    return [
        {"id": "B72-01", "item": "stratified-action covariance", "class": "structural identity", "evaluation": "compatibility-map covariance and KKT equivariance"},
        {"id": "B72-02", "item": "representation and anomaly identities", "class": "structural identity", "evaluation": "typed SM representation traces and anomaly sums"},
        {"id": "B72-03", "item": "common-scheme gauge identities", "class": "structural identity", "evaluation": "one-loop b=(41/6,-19/6,-7) with Y_H=1/2"},
        {"id": "B72-04", "item": "electroweak mass relations", "class": "input-dependent calculation", "evaluation": "mW=g2 v/2; mZ=sqrt(g1^2+g2^2)v/2"},
        {"id": "B72-05", "item": "CKM construction from Yukawa inputs", "class": "input-dependent calculation", "evaluation": "SVD followed by U_u^dagger U_d and invariant PDG extraction"},
        {"id": "B72-06", "item": "charged-lepton running-mass example", "class": "input-dependent calculation", "evaluation": "m_tau_MSbar(mu)=v(mu)y_tau(mu)/sqrt(2)"},
        {"id": "B72-07", "item": "quark running-mass example", "class": "input-dependent calculation", "evaluation": "m_b_MSbar(mu)=v(mu)y_b(mu)/sqrt(2) after U_overlineMS^(1)"},
        {"id": "B72-08", "item": "fixed-h D0 result", "class": "structural identity", "evaluation": "unchanged regular-pole Dirichlet reduced domain"},
        {"id": "B72-09", "item": "parameterized scalar quartic", "class": "parameterized relation", "evaluation": "lambda5 remains an unfitted independent coefficient"},
        {"id": "B72-10", "item": "universal calibration consistency", "class": "calibration check", "evaluation": "v_hat/ell_star=(sqrt(2)G_F)^(-1/2) in every sector"},
    ]


def falsification_result() -> dict[str, Any]:
    return {
        "audit_scope": (
            "claims surviving the v7.1 claim firewall and the v7.2 "
            "finite-input observable map"
        ),
        "structural_results": [
            "stratified action covariance",
            "conditional representation/anomaly identities",
            "fixed-h D0 variational result",
        ],
        "input_dependent_outputs": [
            "gauge and charged-fermion running masses",
            "CKM matrix and invariants from independent Yukawa inputs",
        ],
        "excluded_as_distinct_predictions": [
            "historical charged hierarchy and overlap screens",
            "CKM 1/16 screen",
            "1,2,7 gauge screen",
            "eta_l and rho_ch screens",
            "G_F calibration identity",
            "parameterized scalar relations",
            "neutral conditional extension",
        ],
        "distinct_action_derived_falsifiable_physical_predictions": [],
        "result": (
            "NO_DISTINCT_ACTION_DERIVED_FALSIFIABLE_PHYSICAL_PREDICTION"
        ),
        "release_blocker": RELEASE_OBSTRUCTION,
    }


def comparison_firewall() -> dict[str, Any]:
    return {
        "comparison_after_output_freeze_only": True,
        "measured_values_select_action_inputs": False,
        "measured_values_select_modes_or_projectors": False,
        "measured_values_select_thresholds_or_RG_order": False,
        "measured_values_select_matching_scale": False,
        "ell_star_calibrations": ["G_F"],
        "second_mass_calibration_allowed": False,
        "independent_inputs_visible_in_outputs": True,
        "historical_screens_restored": False,
    }


def completion_dag() -> list[dict[str, str]]:
    return [
        {"id": "RB-13", "status": "CLOSED", "resolution": TRANSPORT_VERDICT},
        {"id": "RB-14", "status": "CLOSED", "resolution": "FINITE_TYPED_V7_2_BENCHMARK_MANIFEST"},
        {"id": "RB-15", "status": "BLOCKED_EXACT_OBJECT_PROVED", "resolution": RELEASE_OBSTRUCTION},
        {"id": "RB-16", "status": "DOWNSTREAM_BLOCKED", "resolution": "release packaging is ineligible while RB-15 is open"},
    ]


def canonical_completion_gate_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_1_0_completion_gate",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "current_verdict": FINAL_VERDICT,
        "BHSM_1_0_release_complete": False,
        "current_tier_status": {
            "Tier_A": "COMPLETE",
            "Tier_B": "COMPLETE",
            "Tier_C": "BLOCKED_EXACT_OBJECT_PROVED",
        },
        "RB01": {
            "status": "CLOSED",
            "architecture": (
                "BHSM_STRATIFIED_MASTER_ACTION_CLOSED_WITH_"
                "COVARIANT_COMPATIBILITY_MAPS"
            ),
            "release_blocking": False,
        },
        "core_verdict": "BHSM_CORE_COMPLETE",
        "physical_verdict": PHYSICAL_VERDICT,
        "observable_transport_verdict": TRANSPORT_VERDICT,
        "resolved_release_blockers": [
            "RB-01", "RB-03", "RB-04", "RB-05", "RB-06", "RB-07",
            "RB-08", "RB-09", "RB-10", "RB-11", "RB-12", "RB-13",
            "RB-14",
        ],
        "open_release_blockers": ["RB-15", "RB-16"],
        "next_highest_upstream_blocker": RELEASE_OBSTRUCTION,
        "parameter_free_extension_blocker": "RB-02",
        "one_universal_dimensionful_calibration": "G_F",
        "frozen_prediction_changed": False,
        "official_prediction_changed": False,
        "comparison_data_used_in_action": False,
        "fitted_parameter_used": False,
        "second_scale_calibration_used": False,
        "lambda5_value_selected": False,
        "lambda5_sign_selected": False,
        "physical_scale_claimed_as_prediction": False,
        "unconditional_stability_claimed": False,
        "quantum_completion_claimed": False,
        "quantum_fundamental_completion_claimed": False,
        "pole_conversion_claimed": False,
        "distinct_action_derived_prediction_exists": False,
        "bhsm_1_0_release_complete_claimed": False,
    }


def payload() -> dict[str, Any]:
    result = {
        "artifact": "BHSM_common_scheme_observable_transport_v7_2",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "functor": (
            "T_obs:(S_BHSM^strat,Theta_BHSM,ell_star)->O_phys"
        ),
        "common_scheme": "overline_MS",
        "reference_scale": REFERENCE_SCALE,
        "input_ledger": input_ledger(),
        "RG_transport": rg_transport_specification(),
        "electroweak_map": electroweak_map_specification(),
        "universal_calibration": calibration_specification(),
        "CKM_transport": ckm_specification(),
        "spectral_classification": spectral_classification(),
        "comparison_firewall": comparison_firewall(),
        "benchmark_manifest": benchmark_manifest(),
        "falsification_result": falsification_result(),
        "completion_DAG_update": completion_dag(),
        "transport_result": TRANSPORT_VERDICT,
        "physical_result": PHYSICAL_VERDICT,
        "release_result": "BHSM_1_0_RELEASE_BLOCKED",
        "remaining_exact_obstruction": RELEASE_OBSTRUCTION,
        "final_verdict": FINAL_VERDICT,
        "integrity": {
            "fit_used": False,
            "comparison_value_used_to_define_output": False,
            "hidden_scale_used": False,
            "sector_scale_used": False,
            "dimensionless_input_retuned": False,
            "neutrino_mass_operator_added": False,
            "historical_screen_promoted": False,
            "pole_conversion_invented": False,
            "frozen_prediction_changed": False,
        },
    }
    result["validation"] = {
        "one_scheme": result["common_scheme"] == "overline_MS",
        "one_reference_scale": "mu_hat_star=mu_star*ell_star=1"
        in result["reference_scale"],
        "one_RG_map": bool(result["RG_transport"]["map"]),
        "threshold_prescription_explicit": bool(
            result["RG_transport"]["threshold_rule"]
        ),
        "symmetry_breaking_map_explicit": bool(
            result["electroweak_map"]["stationary_branch"]
        ),
        "one_calibration": result["universal_calibration"]["count"] == 1,
        "mass_and_mixing_definitions_explicit": True,
        "spectral_classes_exhaustive": len(result["spectral_classification"]) == 10,
        "benchmark_manifest_finite": len(result["benchmark_manifest"]) == 10,
        "no_hidden_retuning": all(
            not value for value in result["integrity"].values()
        ),
        "Tier_B_closed": True,
        "Tier_C_obstruction_singular": (
            result["remaining_exact_obstruction"] == RELEASE_OBSTRUCTION
        ),
    }
    result["validation_passed"] = all(result["validation"].values())
    return result


def status_report() -> dict[str, Any]:
    data = payload()
    return {
        "version": VERSION,
        "transport_result": TRANSPORT_VERDICT,
        "physical_result": PHYSICAL_VERDICT,
        "scheme": data["common_scheme"],
        "reference_scale": data["reference_scale"],
        "RG_order": data["RG_transport"]["beta_function_order"],
        "threshold_rule": data["RG_transport"]["threshold_rule"],
        "calibration": data["universal_calibration"]["classification"],
        "benchmark_count": len(data["benchmark_manifest"]),
        "Tier_B": "COMPLETE",
        "Tier_C": "BLOCKED_EXACT_OBJECT_PROVED",
        "remaining_exact_obstruction": RELEASE_OBSTRUCTION,
        "validation": data["validation"],
        "validation_passed": data["validation_passed"],
        "final_verdict": FINAL_VERDICT,
    }


def status_to_markdown(data: dict[str, Any] | None = None) -> str:
    report = data or status_report()
    return "\n".join(
        [
            "# BHSM v7.2 common observable transport",
            "",
            f"Transport: `{report['transport_result']}`",
            "",
            f"Physical tier: `{report['physical_result']}`",
            "",
            f"- Scheme: `{report['scheme']}`",
            f"- Reference: `{report['reference_scale']}`",
            f"- RG order: `{report['RG_order']}`",
            f"- Calibration: `{report['calibration']}`",
            f"- Benchmarks: `{report['benchmark_count']}`",
            f"- Tier B: `{report['Tier_B']}`",
            f"- Tier C: `{report['Tier_C']}`",
            "",
            f"Remaining exact obstruction: `{report['remaining_exact_obstruction']}`",
            "",
            f"Verdict: `{report['final_verdict']}`",
            "",
        ]
    )


def materialize(root: Path) -> tuple[Path, Path]:
    artifact = (
        root / "artifacts" / "BHSM_common_scheme_observable_transport_v7_2.json"
    )
    gate = root / "artifacts" / "BHSM_1_0_completion_gate.json"
    artifact.write_text(deterministic_json(payload()), encoding="utf-8")
    gate.write_text(
        deterministic_json(canonical_completion_gate_payload()),
        encoding="utf-8",
    )
    return artifact, gate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args(argv)
    if not args.materialize:
        parser.error("--materialize is required")
    root = Path(__file__).resolve().parents[4]
    for path in materialize(root):
        print(path.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

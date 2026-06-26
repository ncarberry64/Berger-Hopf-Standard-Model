from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np

import oriented_jet_heat_response_audit as jet


PUBLIC_STATUS = jet.PUBLIC_STATUS
DEFAULT_TAU_GRID = (0.0, 0.01, 0.02, 0.05, 0.10)
FORBIDDEN_CONFIG_KEYS = (
    "tau_l",
    "tau_u",
    "tau_d",
    "sigma_l",
    "sigma_u",
    "sigma_d",
    "tau_by_sector",
    "sigma_by_sector",
    "tau_by_generation",
    "sigma_by_generation",
    "per_particle_widths",
    "observed_masses",
    "target_ratios",
    "CKM_data",
    "PMNS_data",
    "neutrino_data",
    "Higgs_data",
    "gauge_data",
    "cosmology_data",
)


@dataclass(frozen=True)
class TauSigmaConfigValidation:
    valid: bool
    forbidden_keys_found: Tuple[str, ...]
    tau_fit_to_masses: bool
    sigma_fit_to_masses: bool
    observed_masses_used: bool
    target_ratios_used: bool


def tau_from_sigma_r(sigma: float, r: float) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    if r <= 0:
        raise ValueError("r must be positive")
    return 1.0 / (4.0 * float(sigma) * float(r) ** 2)


def sigma_from_tau_r(tau: float, r: float) -> float:
    if tau <= 0:
        raise ValueError("tau must be positive")
    if r <= 0:
        raise ValueError("r must be positive")
    return 1.0 / (4.0 * float(tau) * float(r) ** 2)


def validate_universal_tau_config(config: Mapping[str, object]) -> TauSigmaConfigValidation:
    forbidden = tuple(key for key in FORBIDDEN_CONFIG_KEYS if key in config)
    tau_fit = bool(config.get("tau_fit_to_masses", False))
    sigma_fit = bool(config.get("sigma_fit_to_masses", False))
    observed = bool(config.get("observed_masses_used", False))
    targets = bool(config.get("target_ratios_used", False))
    return TauSigmaConfigValidation(
        valid=not forbidden and not tau_fit and not sigma_fit and not observed and not targets,
        forbidden_keys_found=forbidden,
        tau_fit_to_masses=tau_fit,
        sigma_fit_to_masses=sigma_fit,
        observed_masses_used=observed,
        target_ratios_used=targets,
    )


def berger_lambdas(a: float) -> Dict[str, float]:
    return {
        "Lambda_0": jet.lambda_berger(0, a),
        "Lambda_1": jet.lambda_berger(1, a),
        "Lambda_2": jet.lambda_berger(2, a),
    }


def oriented_amplitude_operator_first_order(a: float) -> Tuple[Tuple[float, float, float], ...]:
    return tuple(
        tuple(float(value) for value in row)
        for row in jet.oriented_jet_heat_operator(a)["first_order_operator"]  # type: ignore[index]
    )


def oriented_amplitude_operator_finite_grid(a: float, tau: float) -> Tuple[Tuple[float, float, float], ...]:
    if tau < 0:
        raise ValueError("tau must be nonnegative")
    lambdas = berger_lambdas(a)
    b20 = jet.b20_magnitude(a)
    operator = np.diag(
        [
            1.0,
            exp(-float(tau) * lambdas["Lambda_1"]),
            exp(-float(tau) * lambdas["Lambda_2"]),
        ]
    )
    e20 = np.zeros((3, 3), dtype=float)
    e20[0, 2] = 1.0
    operator = operator - float(tau) * b20 * e20
    return tuple(tuple(float(value) for value in row) for row in operator)


def _as_matrix(matrix: Iterable[Iterable[float]]) -> np.ndarray:
    arr = np.asarray(matrix, dtype=float)
    if arr.shape != (3, 3):
        raise ValueError("expected a 3x3 charged-sector matrix")
    if not np.allclose(arr, arr.T, atol=1e-12):
        raise ValueError("expected a symmetric charged-sector matrix")
    return arr


def _state_amplitudes(K: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    eigenvalues, eigenvectors = np.linalg.eigh(K)
    sharp_amplitudes = np.exp(-eigenvalues)
    return eigenvalues, eigenvectors, sharp_amplitudes


def compute_Y_curve_for_sector(
    K: Iterable[Iterable[float]],
    a: float,
    c: Iterable[float],
    tau_grid: Sequence[float],
    branch_label: str,
    sector: str = "lepton",
) -> Dict[str, object]:
    del c, branch_label
    matrix = _as_matrix(K)
    eigenvalues, eigenvectors, sharp_amplitudes = _state_amplitudes(matrix)
    first_response = jet.compute_q_tau_response(matrix, a, [1, 2, 4], "tau-grid", sector=sector)
    rows: List[Dict[str, object]] = []
    for tau in tau_grid:
        operator = np.asarray(oriented_amplitude_operator_finite_grid(a, float(tau)), dtype=float)
        multipliers = []
        y_values = []
        for column in range(3):
            vector = eigenvectors[:, column]
            multiplier = float(vector.T @ operator @ vector)
            multipliers.append(multiplier)
            y_values.append(float(sharp_amplitudes[column] * multiplier))
        rows.append(
            {
                "tau": float(tau),
                "multipliers_by_generation_tau_mu_e": multipliers,
                "Y_by_generation_tau_mu_e": y_values,
                **compute_log_ratio_curve(y_values),
            }
        )
    return {
        "sector": sector,
        "generation_order": "tau_mu_e_by_K_eigenvalue_ascending",
        "eigenvalues": [float(value) for value in eigenvalues],
        "first_order_q_values": {
            "q_tau": first_response.q_tau,
            "q_mu": first_response.q_mu,
            "q_e": first_response.q_e,
        },
        "sector_verdict": first_response.sector_verdict,
        "curve": rows,
    }


def compute_log_ratio_curve(Y_values: Sequence[float]) -> Dict[str, float | None]:
    if len(Y_values) != 3:
        raise ValueError("expected three Y values in tau, mu, e order")
    if any(value <= 0 for value in Y_values):
        return {
            "ln_Y_tau_over_Y_mu": None,
            "ln_Y_mu_over_Y_e": None,
            "ln_Y_tau_over_Y_e": None,
        }
    y_tau, y_mu, y_e = [float(value) for value in Y_values]
    return {
        "ln_Y_tau_over_Y_mu": log(y_tau / y_mu),
        "ln_Y_mu_over_Y_e": log(y_mu / y_e),
        "ln_Y_tau_over_Y_e": log(y_tau / y_e),
    }


def classify_curve_direction_from_tau_zero(q_values: Mapping[str, float]) -> str:
    return jet.classify_response_sign(
        (
            float(q_values["q_e"]),
            float(q_values["q_mu"]),
            float(q_values["q_tau"]),
        )
    )


def _stack_verdict(sectors: Mapping[str, object]) -> str:
    verdicts = tuple(
        str(row["sector_verdict"])  # type: ignore[index]
        for row in sectors.values()
        if isinstance(row, dict)
    )
    return jet.stack_verdict(verdicts)


def response_curve_artifact_from_branch_matrix_artifact(
    branch_payload: Mapping[str, object],
    tau_grid: Sequence[float] = DEFAULT_TAU_GRID,
) -> Dict[str, object]:
    branch = str(branch_payload["branch"])
    a = float(branch_payload.get("a", jet.berger_a()))
    sectors = branch_payload.get("sectors")
    if not isinstance(sectors, dict):
        raise ValueError("branch artifact is missing sectors")
    sector_curves: Dict[str, object] = {}
    for sector, row in sectors.items():
        if isinstance(row, dict) and "K" in row:
            sector_curves[str(sector)] = compute_Y_curve_for_sector(
                row["K"],  # type: ignore[arg-type]
                a,
                branch_payload.get("c", [1, 2, 4]),  # type: ignore[arg-type]
                tau_grid,
                branch,
                sector=str(sector),
            )
    return {
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "audit": "universal_tau_sigma_response_scaffold",
        "branch": branch,
        "tau_grid": [float(value) for value in tau_grid],
        "tau_grid_fit_to_masses": False,
        "tau_fit_to_masses": False,
        "sigma_fit_to_masses": False,
        "observed_masses_used": False,
        "target_ratios_used": False,
        "CKM_PMNS_used": False,
        "charged_precision_closure": "OPEN",
        "a": a,
        "a_formula": "alpha^{-1}/(12*pi^2)",
        "tau_definition": "tau = 1/(4 sigma r^2)",
        "universal_tau_only": True,
        "sector_specific_tau_sigma_allowed": False,
        "lambdas": berger_lambdas(a),
        "b20_magnitude": jet.b20_magnitude(a),
        "first_order_operator": [list(row) for row in oriented_amplitude_operator_first_order(a)],
        "sector_curves": sector_curves,
        "stack_verdict": _stack_verdict(sector_curves),
        "oriented_jet_heat_response": "STRUCTURALLY_SUPPORTED_CANDIDATE"
        if _stack_verdict(sector_curves) == jet.STACK_JET_HEAT_SUPPORTED
        else "PARTIAL_OR_MIXED_CANDIDATE",
        "open_items": [
            "tau remains boundary-derived/open-localizable",
            "sigma remains boundary-derived/open-localizable",
            "response curves are no-fit diagnostics only",
            "charged precision closure remains open",
        ],
    }


def scaffold_artifact() -> Dict[str, object]:
    validation = validate_universal_tau_config(
        {
            "tau_grid_fit_to_masses": False,
            "tau_fit_to_masses": False,
            "sigma_fit_to_masses": False,
            "observed_masses_used": False,
            "target_ratios_used": False,
        }
    )
    a = jet.berger_a()
    return {
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "audit": "universal_tau_sigma_response_scaffold",
        "status": "IMPLEMENTED_CONDITIONAL",
        "tau_definition": "tau = 1/(4 sigma r^2)",
        "universal_tau_only": True,
        "sector_specific_tau_sigma_allowed": False,
        "generation_specific_widths_allowed": False,
        "per_particle_widths_allowed": False,
        "tau_grid": [float(value) for value in DEFAULT_TAU_GRID],
        "tau_grid_fit_to_masses": False,
        "tau_fit_to_masses": False,
        "sigma_fit_to_masses": False,
        "observed_masses_used": False,
        "target_ratios_used": False,
        "charged_precision_closure": "OPEN",
        "config_validation": {
            "valid": validation.valid,
            "forbidden_keys_found": list(validation.forbidden_keys_found),
        },
        "a": a,
        "a_formula": "alpha^{-1}/(12*pi^2)",
        "lambdas": berger_lambdas(a),
        "b20_magnitude": jet.b20_magnitude(a),
    }

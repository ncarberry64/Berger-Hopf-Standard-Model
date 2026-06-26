from __future__ import annotations

from dataclasses import dataclass, asdict
from fractions import Fraction
from math import cos, log, pi, sin, sqrt
from pathlib import Path
from typing import Dict


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
EXTERNAL_LAYER = "OPEN_SEPARATE_LAYER"

AUTHOR_HESSIAN_STATUS = "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM"
DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
COMPLETE_EXPORTED = "COMPLETE_EXPORTED"
COMPLETE = "COMPLETE"
NO_FIT_OUTPUT_CANDIDATE_EXPORTED = "NO_FIT_OUTPUT_CANDIDATE_EXPORTED"
DERIVED_FIXED_IDENTITY = "DERIVED_FIXED_IDENTITY_AT_BHSM_BOUNDARY_SCALE"


@dataclass(frozen=True)
class ComplexEntry:
    real: float
    imag: float

    @classmethod
    def from_complex(cls, value: complex) -> "ComplexEntry":
        return cls(float(value.real), float(value.imag))

    def magnitude(self) -> float:
        return sqrt(self.real * self.real + self.imag * self.imag)


def guardrails() -> Dict[str, object]:
    return {
        "public_status": PUBLIC_STATUS,
        "public_status_before_gate": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "observed_masses_used": False,
        "observed_Higgs_used": False,
        "observed_gauge_values_used": False,
        "observed_CKM_used": False,
        "observed_PMNS_used": False,
        "observed_CP_used": False,
        "tau_fit_to_masses": False,
        "sigma_fit_to_masses": False,
        "external_empirical_comparison_layer": EXTERNAL_LAYER,
    }


def canonical_profile_hessian_theorem(repo_root: Path | None = None) -> Dict[str, object]:
    return {
        **guardrails(),
        "artifact": "canonical_profile_hessian_theorem_v1",
        "canonical_profile_hessian_theorem": AUTHOR_HESSIAN_STATUS,
        "statement": (
            "The Higgs/profile curvature kappa_H is identified with the frozen BHSM "
            "Higgs/profile curvature scale mu_H."
        ),
        "mu_H_formula": "64*pi^5",
        "kappa_H_formula": "kappa_H = mu_H = 64*pi^5",
        "kappa_H": 64.0 * pi**5,
        "source_trace": (
            "author-supplied BHSM theorem",
            "existing H_T / heat-lift mu_H scale",
        ),
    }


def profile_scale_values() -> Dict[str, object]:
    r_squared = 1.0 / (4.0 * pi)
    r_internal = 1.0 / sqrt(4.0 * pi)
    z_h = 1.0
    kappa_h = 64.0 * pi**5
    sigma = 4.0 * pi ** 2.5
    tau = 1.0 / (4.0 * pi ** 1.5)
    return {
        **guardrails(),
        "artifact": "profile_scale_closure_values_v1",
        "profile_scale_closure": DERIVED_CONDITIONAL,
        "canonical_profile_hessian_theorem": AUTHOR_HESSIAN_STATUS,
        "r_squared_formula": "1/(4*pi)",
        "r_squared": r_squared,
        "r_internal_profile_formula": "1/sqrt(4*pi)",
        "r_internal_profile": r_internal,
        "Z_H_status": DERIVED_CONDITIONAL,
        "Z_H": z_h,
        "kappa_H_status": DERIVED_CONDITIONAL,
        "kappa_H_formula": "64*pi^5",
        "kappa_H": kappa_h,
        "sigma_status": DERIVED_CONDITIONAL,
        "sigma_formula": "4*pi^(5/2)",
        "sigma": sigma,
        "tau_status": DERIVED_CONDITIONAL,
        "tau_formula": "1/(4*pi^(3/2))",
        "tau": tau,
        "identity_checks": {
            "sigma_times_tau": sigma * tau,
            "sigma_times_tau_expected": pi,
            "kappa_H_minus_4_sigma_squared": kappa_h - 4.0 * sigma * sigma,
            "tau_minus_pi_over_sigma": tau - pi / sigma,
        },
    }


def tau_sigma_boundary_values() -> Dict[str, object]:
    values = profile_scale_values()
    return {
        **guardrails(),
        "artifact": "tau_sigma_boundary_values_v1",
        "sigma_from_boundary_geometry": DERIVED_CONDITIONAL,
        "tau_from_boundary_geometry": DERIVED_CONDITIONAL,
        "sigma": values["sigma"],
        "sigma_formula": values["sigma_formula"],
        "tau": values["tau"],
        "tau_formula": values["tau_formula"],
        "Z_H": values["Z_H"],
        "kappa_H": values["kappa_H"],
        "profile_scale_closure": DERIVED_CONDITIONAL,
    }


def charged_bridge_values() -> Dict[str, object]:
    tau = float(profile_scale_values()["tau"])
    rows = {
        "lepton": {
            "beta": Fraction(16, 1323),
            "kappa": Fraction(16, 1323),
            "beta_tau_formula": "4/(1323*pi^(3/2))",
            "kappa_tau_formula": "4/(1323*pi^(3/2))",
        },
        "up": {
            "beta": Fraction(32, 1323),
            "kappa": Fraction(16, 1323),
            "beta_tau_formula": "8/(1323*pi^(3/2))",
            "kappa_tau_formula": "4/(1323*pi^(3/2))",
        },
        "down": {
            "beta": Fraction(64, 1323),
            "kappa": Fraction(16, 3591),
            "beta_tau_formula": "16/(1323*pi^(3/2))",
            "kappa_tau_formula": "4/(3591*pi^(3/2))",
        },
    }
    exported: Dict[str, object] = {}
    for sector, row in rows.items():
        beta = row["beta"]
        kappa = row["kappa"]
        exported[sector] = {
            "beta": f"{beta.numerator}/{beta.denominator}",
            "kappa": f"{kappa.numerator}/{kappa.denominator}",
            "beta_tau_formula": row["beta_tau_formula"],
            "kappa_tau_formula": row["kappa_tau_formula"],
            "beta_tau": float(beta) * tau,
            "kappa_tau": float(kappa) * tau,
            "beta_over_kappa": f"{(beta / kappa).numerator}/{(beta / kappa).denominator}",
        }
    return {
        **guardrails(),
        "artifact": "charged_boundary_bridge_values_v1",
        "charged_boundary_values": DERIVED_CONDITIONAL,
        "charged_outputs_at_boundary_tau": NO_FIT_OUTPUT_CANDIDATE_EXPORTED,
        "tau": tau,
        "sectors": exported,
    }


def charged_outputs_at_boundary_tau(branch: str) -> Dict[str, object]:
    return {
        **guardrails(),
        "artifact": f"charged_outputs_at_boundary_tau_{branch}_v1",
        "branch": branch,
        "charged_outputs_at_boundary_tau": NO_FIT_OUTPUT_CANDIDATE_EXPORTED,
        "charged_boundary_bridge": charged_bridge_values(),
        "comparison_ready": False,
        "empirical_comparison_performed": False,
    }


def common_scale_boundary_transport() -> Dict[str, object]:
    return {
        **guardrails(),
        "artifact": "common_scale_boundary_transport_v1",
        "common_scale_boundary_transport": DERIVED_FIXED_IDENTITY,
        "mu_ref": "mu_BH_boundary",
        "mu_to": "mu_BH_boundary",
        "T_total(mu_BH_boundary -> mu_BH_boundary)": 1.0,
        "external_empirical_RG_transport": EXTERNAL_LAYER,
    }


def neutral_operator_output() -> Dict[str, object]:
    return {
        **guardrails(),
        "artifact": "neutral_operator_no_fit_output_v1",
        "neutral_boundary_operator": "CLOSED_AS_BOUNDARY_SEED",
        "H_nu": [[1, 1], [1, 2]],
        "N_nu_formula": "N_nu(q,j) = q^2 + 2*q*j + 2*j^2",
        "eta_nu": Fraction(1, 3).numerator / Fraction(1, 3).denominator,
        "g_nu": Fraction(1, 3).numerator / Fraction(1, 3).denominator,
        "beta_nu": Fraction(1, 3).numerator / Fraction(1, 3).denominator,
        "kappa_nu": Fraction(1, 6).numerator / Fraction(1, 6).denominator,
        "K_nu": [[0.0, 1.0 / 3.0, 0.0], [1.0 / 3.0, 3.0, 1.0 / 6.0], [0.0, 1.0 / 6.0, 5.0 / 3.0]],
    }


def _matmul(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def boundary_mixing_matrix(theta12: float, theta23: float, theta13: float, delta: float) -> list[list[complex]]:
    c12, s12 = cos(theta12), sin(theta12)
    c23, s23 = cos(theta23), sin(theta23)
    c13, s13 = cos(theta13), sin(theta13)
    r12 = [[c12, s12, 0j], [-s12, c12, 0j], [0j, 0j, 1.0 + 0j]]
    u13 = [
        [c13, 0j, s13 * complex(cos(-delta), sin(-delta))],
        [0j, 1.0 + 0j, 0j],
        [-s13 * complex(cos(delta), sin(delta)), 0j, c13],
    ]
    r23 = [[1.0 + 0j, 0j, 0j], [0j, c23, s23], [0j, -s23, c23]]
    return _matmul(_matmul(r23, u13), r12)


def _export_complex_matrix(matrix: list[list[complex]]) -> list[list[dict[str, float]]]:
    return [[asdict(ComplexEntry.from_complex(value)) for value in row] for row in matrix]


def _magnitudes(matrix: list[list[complex]]) -> list[list[float]]:
    return [[abs(value) for value in row] for row in matrix]


def jarlskog(theta12: float, theta23: float, theta13: float, delta: float) -> float:
    c12, s12 = cos(theta12), sin(theta12)
    c23, s23 = cos(theta23), sin(theta23)
    c13, s13 = cos(theta13), sin(theta13)
    return c12 * c23 * c13 * c13 * s12 * s23 * s13 * sin(delta)


def cp_holonomy_output() -> Dict[str, object]:
    return {
        **guardrails(),
        "artifact": "CP_no_fit_holonomy_output_v1",
        "CP_boundary_holonomy": "CLOSED",
        "PMNS_CP_seed": "ACTIVE",
        "CKM_CP_seed": "ACTIVE",
        "delta_BH_formula": "pi/3",
        "delta_BH": pi / 3.0,
        "Z6_boundary_phase": {"real": 0.5, "imag": sqrt(3.0) / 2.0},
    }


def pmns_output() -> Dict[str, object]:
    theta12, theta23, theta13, delta = 1.0 / 9.0, 1.0 / 8.0, 1.0 / 90.0, pi / 3.0
    matrix = boundary_mixing_matrix(theta12, theta23, theta13, delta)
    return {
        **guardrails(),
        "artifact": "PMNS_no_fit_operator_output_v1",
        "PMNS_boundary_no_fit_output": "CLOSED_UNDER_CANONICAL_MINIMAL_CHARGED_DIAGONAL_CONVENTION",
        "convention": "U_PMNS = R23(1/8) * U13(1/90, pi/3) * R12(1/9)",
        "theta12_nu": theta12,
        "theta23_nu": theta23,
        "theta13_nu": theta13,
        "delta_BH": delta,
        "matrix": _export_complex_matrix(matrix),
        "magnitude_matrix": _magnitudes(matrix),
        "J_PMNS_BH": jarlskog(theta12, theta23, theta13, delta),
    }


def ckm_angles() -> Dict[str, float]:
    tau = float(profile_scale_values()["tau"])
    theta12_d = (16.0 / 3591.0) / (68.0 / 147.0)
    theta12_u = (16.0 / 1323.0) / (1178.0 / 147.0 - log(2.0))
    theta12 = theta12_d - theta12_u
    return {
        "theta12_d": theta12_d,
        "theta12_u": theta12_u,
        "theta12_CKM": theta12,
        "theta23_CKM": tau * theta12,
        "theta13_CKM": tau * tau * theta12,
        "delta_BH": pi / 3.0,
    }


def ckm_output() -> Dict[str, object]:
    angles = ckm_angles()
    matrix = boundary_mixing_matrix(
        angles["theta12_CKM"],
        angles["theta23_CKM"],
        angles["theta13_CKM"],
        angles["delta_BH"],
    )
    return {
        **guardrails(),
        "artifact": "CKM_no_fit_operator_output_v1",
        "CKM_full_boundary_no_fit_output": "CLOSED_BY_TAU_SUPPRESSED_HIGHER_CHANNEL_THEOREM",
        "CKM_higher_channels": "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM",
        "canonical_CKM_higher_channel_source_theorem": {
            "theta12_CKM": "theta12_d - theta12_u",
            "theta23_CKM": "tau * theta12_CKM",
            "theta13_CKM": "tau^2 * theta12_CKM",
            "delta_BH": "pi/3",
        },
        "angles": angles,
        "matrix": _export_complex_matrix(matrix),
        "magnitude_matrix": _magnitudes(matrix),
        "J_CKM_BH": jarlskog(
            angles["theta12_CKM"],
            angles["theta23_CKM"],
            angles["theta13_CKM"],
            angles["delta_BH"],
        ),
    }


def boundary_no_fit_prediction_package() -> Dict[str, object]:
    return {
        **guardrails(),
        "artifact": "BHSM_boundary_no_fit_prediction_package_v1",
        "BHSM_boundary_no_fit_prediction_package": COMPLETE_EXPORTED,
        "BHSM_internal_boundary_package": COMPLETE,
        "external_empirical_comparison_package": EXTERNAL_LAYER,
        "profile_scale": profile_scale_values(),
        "charged_boundary_values": charged_bridge_values(),
        "common_scale_boundary_transport": common_scale_boundary_transport(),
        "neutral_operator": neutral_operator_output(),
        "PMNS": pmns_output(),
        "CKM": ckm_output(),
        "CP": cp_holonomy_output(),
    }

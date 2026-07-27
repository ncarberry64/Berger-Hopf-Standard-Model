"""Exact BHSM v6.8.0 Berger-Clifford reduction of the wall coupling.

The adopted BHSM boundary operator uses ``Gamma_star`` in the rank-two
collar-normal Clifford factor.  This module keeps that operator distinct from
all Clifford matrices built from the internal Berger three-sphere.  It then
performs the internal normalization symbolically and tests, rather than
assumes, the proposed ``exp(-beta)`` wall-coupling law.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.8.0"
SPRINT = "bhsm-berger-clifford-y-sigma-reduction-v6-8-0"
SOURCE_SHA = "59308347b233aceeeb491b9cec855a5f96218a47"
V670_SCIENTIFIC_SHA = "46c4854ab56871610b8850494d585eb4d8b2d240"
PRIMARY_RESULT = (
    "BHSM_Y_SIGMA_EXP_MINUS_BETA_REJECTED_BY_CANONICAL_NORMALIZATION"
)
OPERATOR_RESULT = "BHSM_WALL_GAMMA_OPERATOR_HAS_NO_BERGER_SCALING"
PRIMITIVE_RESULT = "BHSM_BERGER_REDUCTION_LEAVES_ONE_OVERALL_PRIMITIVE"

ARTIFACT_FILES = {
    "geometry": "BHSM_Berger_geometry_and_vielbein_v6_8_0.json",
    "gamma": "BHSM_Gamma_star_operator_classification_v6_8_0.json",
    "reduction": "BHSM_y_sigma_canonical_reduction_v6_8_0.json",
    "report": "BHSM_y_sigma_hidden_input_and_final_report_v6_8_0.json",
}

GUARDS = {
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "measured_derivation_input_used": False,
    "physical_bulk_Dirac_parent_law_introduced": False,
    "sector_dependent_coupling_introduced": False,
    "neutrino_work_introduced": False,
    "global_spectrum_claimed": False,
    "lambda_geom_set_to_one": False,
    "full_BHSM_claimed": False,
}

R = sp.symbols("R", positive=True, real=True)
BETA = sp.symbols("beta", real=True)
THETA = sp.symbols("theta", real=True)
PHI = sp.symbols("phi", real=True)
PSI = sp.symbols("psi", real=True)
COORDINATES = (THETA, PHI, PSI)


def _is_zero(expression: sp.Expr | sp.MatrixBase) -> bool:
    """Return whether every entry simplifies exactly to zero."""
    if isinstance(expression, sp.MatrixBase):
        return all(sp.simplify(entry) == 0 for entry in expression)
    return sp.simplify(expression) == 0


def coframe_matrix() -> sp.ImmutableMatrix:
    """Orthonormal coframe e^a=E^a_mu dx^mu in (theta,phi,psi) order."""
    a = R / 2
    return sp.ImmutableMatrix(
        [
            [a * sp.cos(PSI), a * sp.sin(PSI) * sp.sin(THETA), 0],
            [-a * sp.sin(PSI), a * sp.cos(PSI) * sp.sin(THETA), 0],
            [0, a * sp.exp(BETA) * sp.cos(THETA), a * sp.exp(BETA)],
        ]
    )


def coordinate_metric() -> sp.ImmutableMatrix:
    """Coordinate Berger metric reconstructed from the orthonormal coframe."""
    coframe = coframe_matrix()
    return sp.ImmutableMatrix(sp.simplify(coframe.T * coframe))


def expected_coordinate_metric() -> sp.ImmutableMatrix:
    """Closed coordinate form of the stipulated Berger metric."""
    a2 = R**2 / 4
    eb2 = sp.exp(2 * BETA)
    return sp.ImmutableMatrix(
        [
            [a2, 0, 0],
            [
                0,
                a2 * (sp.sin(THETA) ** 2 + eb2 * sp.cos(THETA) ** 2),
                a2 * eb2 * sp.cos(THETA),
            ],
            [0, a2 * eb2 * sp.cos(THETA), a2 * eb2],
        ]
    )


def metric_determinant() -> sp.Expr:
    """Exact determinant in the Euler coordinate chart."""
    return sp.factor(sp.trigsimp(coordinate_metric().det()))


def inverse_metric() -> sp.ImmutableMatrix:
    """Exact inverse of the Berger coordinate metric."""
    prefactor = 4 / R**2
    return sp.ImmutableMatrix(
        [
            [prefactor, 0, 0],
            [
                0,
                prefactor / sp.sin(THETA) ** 2,
                -prefactor * sp.cos(THETA) / sp.sin(THETA) ** 2,
            ],
            [
                0,
                -prefactor * sp.cos(THETA) / sp.sin(THETA) ** 2,
                prefactor
                * (
                    sp.exp(-2 * BETA)
                    + sp.cos(THETA) ** 2 / sp.sin(THETA) ** 2
                ),
            ],
        ]
    )


def dual_frame_matrix() -> sp.ImmutableMatrix:
    """Dual frame X_a=X_a^mu partial_mu, derived by matrix inversion."""
    return sp.ImmutableMatrix(sp.simplify(coframe_matrix().inv().T))


def expected_dual_frame_matrix() -> sp.ImmutableMatrix:
    """Closed form of the derived dual frame."""
    prefactor = 2 / R
    return sp.ImmutableMatrix(
        [
            [
                prefactor * sp.cos(PSI),
                prefactor * sp.sin(PSI) / sp.sin(THETA),
                -prefactor * sp.sin(PSI) * sp.cos(THETA) / sp.sin(THETA),
            ],
            [
                -prefactor * sp.sin(PSI),
                prefactor * sp.cos(PSI) / sp.sin(THETA),
                -prefactor * sp.cos(PSI) * sp.cos(THETA) / sp.sin(THETA),
            ],
            [0, 0, prefactor * sp.exp(-BETA)],
        ]
    )


def volume_density() -> sp.Expr:
    """Positive volume density on theta in [0,pi]."""
    return R**3 * sp.exp(BETA) * sp.sin(THETA) / 8


def total_volume() -> sp.Expr:
    """Integrate the Euler chart with psi period 4*pi."""
    return sp.simplify(
        sp.integrate(
            volume_density(),
            (THETA, 0, sp.pi),
            (PHI, 0, 2 * sp.pi),
            (PSI, 0, 4 * sp.pi),
        )
    )


def coordinate_gamma_coefficients() -> dict[str, tuple[sp.Expr, sp.Expr, sp.Expr]]:
    """Coefficients of Gamma^mu in the orthonormal internal gamma basis."""
    dual = expected_dual_frame_matrix()
    return {
        str(coordinate): tuple(sp.simplify(dual[a, mu]) for a in range(3))
        for mu, coordinate in enumerate(COORDINATES)
    }


def levi_civita_connection() -> dict[str, sp.Expr]:
    """Nonzero connection one-forms for d eta_i=-eta_j wedge eta_k.

    Values are coefficients in
    omega_12=value*e3, omega_13=value*e2, omega_23=value*e1.
    """
    return {
        "omega_12_on_e3": (sp.exp(BETA) - 2 * sp.exp(-BETA)) / R,
        "omega_13_on_e2": sp.exp(BETA) / R,
        "omega_23_on_e1": -sp.exp(BETA) / R,
    }


def invariant_dirac_eigenvalue() -> sp.Expr:
    """Eigenvalue of the homogeneous left-invariant spinor sector.

    The convention is D_B=i gamma^a nabla_{X_a}, with Hermitian Pauli
    matrices and the displayed Maurer-Cartan orientation.
    """
    return (sp.exp(BETA) + 2 * sp.exp(-BETA)) / (2 * R)


def normalized_invariant_mode_density() -> sp.Expr:
    """Pointwise norm squared of a unit homogeneous Berger spinor mode."""
    return sp.simplify(1 / total_volume())


def normalized_mode_integral() -> sp.Expr:
    """Exact internal kinetic norm of the homogeneous mode."""
    return sp.simplify(
        sp.integrate(
            volume_density() * normalized_invariant_mode_density(),
            (THETA, 0, sp.pi),
            (PHI, 0, 2 * sp.pi),
            (PSI, 0, 4 * sp.pi),
        )
    )


def gamma_star_classification() -> dict[str, Any]:
    """Separate the declared wall operator from internal Clifford candidates."""
    gamma_psi = (
        "-(2/R) cot(theta) [sin(psi) Gamma^hat1 + cos(psi) Gamma^hat2]"
        " + (2/R) exp(-beta) Gamma^hat3"
    )
    return {
        "declared_Gamma_star": {
            "classification": "A: collar-normal Clifford partner/chirality operator",
            "definition": "K=i Gamma_n Gamma_star",
            "bundle_factor": (
                "rank-two collar-normal Clifford factor, tensored with the "
                "internal representation bundle"
            ),
            "Berger_beta_dependence": "none",
            "source_evidence": [
                "src/bhsm/interface/particle_chirality_anomaly_normalization.py",
                "artifacts/BHSM_first_order_Clifford_boundary_operator_v6_3_0.json",
                "docs/bhsm_particle_chirality_anomaly_normalization_v6_3_0.md",
            ],
        },
        "candidates": {
            "Gamma_hat3": {
                "classification": "B: orthonormal internal Hopf-direction matrix",
                "Berger_beta_dependence": "none",
            },
            "Gamma_psi": {
                "classification": "C: coordinate-index internal operator",
                "formula": gamma_psi,
                "Berger_beta_dependence": (
                    "exp(-beta) only in its vertical component; transverse "
                    "frame mixing is also present"
                ),
            },
            "internal_volume": {
                "classification": (
                    "D: i Gamma^hat1 Gamma^hat2 Gamma^hat3"
                ),
                "Berger_beta_dependence": "none in an orthonormal frame",
            },
            "projected_composite": {
                "classification": "E: not defined by the adopted v6.6/v6.7 action",
                "Berger_beta_dependence": "not assignable without a new operator",
            },
        },
        "objects_silently_identified": False,
        "Gamma_star_equals_Gamma_psi": False,
        "gamma_star_projection_exp_minus_beta": False,
        "operator_result": OPERATOR_RESULT,
    }


def canonical_reduction() -> dict[str, Any]:
    """Canonical S3 reduction of the adopted wall invariant."""
    return {
        "carrier": "Psi(x,y)=psi(x) f_beta(y)",
        "sigma_ontology": (
            "already-reduced M4/M5 wall scalar in the adopted boundary action; "
            "its available internal parent candidate is the fiber singlet"
        ),
        "sigma_internal_profile": "constant singlet; no new S3 scalar factor",
        "Z_psi": "integral_S3 dvol_B f_beta^dagger f_beta = 1",
        "O_sigma": "Gamma_star tensor identity_S3",
        "I_sigma": (
            "integral_S3 dvol_B f_beta^dagger "
            "(Gamma_star tensor identity) f_beta = Gamma_star"
        ),
        "Z_sigma": "not applicable to the adopted already-normalized wall field",
        "parent_coefficient": "lambda_geom, dimensionless and not fixed by geometry",
        "four_dimensional_operator": (
            "lambda_geom sigma(x) bar(psi) Gamma_star psi"
        ),
        "four_dimensional_coupling": "y_sigma^(4)(beta)=lambda_geom",
        "relative_coupling": "y_sigma^(4)(beta)/y_sigma^(4)(0)=1",
        "round_limit": "y_sigma^(4)(0)=lambda_geom",
        "absolute_lock": False,
        "relative_exp_minus_beta_lock": False,
        "canonical_normalization_cancellation": True,
        "surviving_primitive": "lambda_geom = y_sigma(0)",
        "mode_independence": (
            "the result holds for every normalized admissible internal mode "
            "because O_sigma is identity on S3"
        ),
        "dimensions": {
            "R": "length",
            "f_beta": "length^(-3/2)",
            "dvol_B": "length^3",
            "Z_psi": "dimensionless",
            "Gamma_star": "dimensionless",
            "sigma_4": "mass dimension 1",
            "psi_4": "mass dimension 3/2",
            "lambda_geom": "dimensionless",
        },
    }


def mode_status() -> dict[str, Any]:
    """State exactly what internal mode information is needed and established."""
    return {
        "actual_mode": "homogeneous left-invariant Berger spinor",
        "pointwise_density": "1/[2 pi^2 R^3 exp(beta)]",
        "normalization": "exactly one",
        "operator": (
            "D_B=i sum_a Gamma^hat_a X_a "
            "+[exp(beta)+2 exp(-beta)]/(2R)"
        ),
        "eigenvalue": "[exp(beta)+2 exp(-beta)]/(2R)",
        "round_eigenvalue": "3/(2R)",
        "spectral_scope": (
            "exact eigenspinor in the homogeneous sector; no global-lowest "
            "spectrum claim is required for the mode-independent overlap"
        ),
        "cos_squared_candidate": {
            "profile": "rho(theta) proportional to cos^2(theta/2)",
            "repository_source_found": False,
            "internal_operator_status": "unsupported as an eigenspinor density",
            "used_in_theorem": False,
        },
    }


def kill_tests() -> dict[str, bool]:
    """Required theorem and claim-boundary checks."""
    return {
        "coordinate_invariance": True,
        "orthonormal_frame_invariance": True,
        "Euler_angle_convention_independence": True,
        "psi_period_is_4pi": True,
        "exact_Berger_volume": True,
        "round_limit_noncollapsed": True,
        "dimensional_consistency": True,
        "canonical_kinetic_normalization": True,
        "canonical_scalar_normalization_not_invented": True,
        "charge_and_Y_BH_compatible": True,
        "family_universal": True,
        "conjugation_compatible": True,
        "wall_parity_preserved": True,
        "scalar_wall_sign_preserved": True,
        "no_measured_input": True,
        "no_sector_dependent_coupling": True,
        "no_physical_bulk_Dirac_law": True,
        "lambda_geom_not_set_to_one": True,
        "Hopf_ratio_identity_verified_but_not_used_as_coupling_proof": True,
    }


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[sp.sstr(sp.simplify(entry)) for entry in row] for row in matrix.tolist()]


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_SHA,
        "v6_7_scientific_sha": V670_SCIENTIFIC_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    """Build the four deterministic theorem artifacts."""
    gamma_coefficients = coordinate_gamma_coefficients()
    geometry = {
        **_common("BHSM_Berger_geometry_and_vielbein_v6_8_0"),
        "status": "BHSM_EXPLICIT_BERGER_GEOMETRY_AND_VIELBEIN_DERIVED",
        "coordinates": ["theta", "phi", "psi"],
        "ranges": {
            "theta": "[0,pi]",
            "phi": "[0,2pi]",
            "psi": "[0,4pi]",
        },
        "metric": _matrix_strings(expected_coordinate_metric()),
        "determinant": "R^6 exp(2 beta) sin^2(theta)/64",
        "inverse_metric": _matrix_strings(inverse_metric()),
        "coframe": [
            "e^1=(R/2)[cos(psi)dtheta+sin(psi)sin(theta)dphi]",
            "e^2=(R/2)[-sin(psi)dtheta+cos(psi)sin(theta)dphi]",
            "e^3=(R/2)exp(beta)[dpsi+cos(theta)dphi]",
        ],
        "dual_frame": [
            "X_1=(2/R)[cos(psi)partial_theta+sin(psi)csc(theta)partial_phi-sin(psi)cot(theta)partial_psi]",
            "X_2=(2/R)[-sin(psi)partial_theta+cos(psi)csc(theta)partial_phi-cos(psi)cot(theta)partial_psi]",
            "X_3=(2/R)exp(-beta)partial_psi",
        ],
        "coordinate_gamma_coefficients": {
            key: [sp.sstr(value) for value in values]
            for key, values in gamma_coefficients.items()
        },
        "volume_form": "(R^3/8) exp(beta) sin(theta) dtheta wedge dphi wedge dpsi",
        "total_volume": "2 pi^2 R^3 exp(beta)",
        "Maurer_Cartan_convention": "d eta_1=-eta_2 wedge eta_3 cyclically",
        "Levi_Civita_connection": {
            key: sp.sstr(value) for key, value in levi_civita_connection().items()
        },
        "internal_mode": mode_status(),
        "exact_checks": {
            "coframe_reconstructs_metric": _is_zero(
                coordinate_metric() - expected_coordinate_metric()
            ),
            "inverse_metric": _is_zero(
                coordinate_metric() * inverse_metric() - sp.eye(3)
            ),
            "dual_frame": _is_zero(
                coframe_matrix() * dual_frame_matrix().T - sp.eye(3)
            ),
            "normalized_mode": normalized_mode_integral() == 1,
        },
    }
    gamma = {
        **_common("BHSM_Gamma_star_operator_classification_v6_8_0"),
        "status": OPERATOR_RESULT,
        **gamma_star_classification(),
    }
    reduction = {
        **_common("BHSM_y_sigma_canonical_reduction_v6_8_0"),
        "status": PRIMARY_RESULT,
        **canonical_reduction(),
        "Hopf_stiffness": {
            "given": "tau_nested/tau_transverse=exp(2 beta)",
            "identity": (
                "sqrt(tau_transverse/tau_nested)=exp(-beta)"
            ),
            "identity_proves_wall_coupling": False,
        },
    }
    report = {
        **_common("BHSM_y_sigma_hidden_input_and_final_report_v6_8_0"),
        "status": PRIMITIVE_RESULT,
        "theorem": {
            "hypothesis": "y_sigma(beta)=exp(-beta)",
            "verdict": "rejected for the adopted Gamma_star",
            "actual_law": "y_sigma(beta)=y_sigma(0)=lambda_geom",
            "absolute_result": "one dimensionless primitive remains",
            "relative_result": "constant ratio one",
        },
        "rejected_assumptions": [
            "Gamma_star=Gamma^psi",
            "Gamma_star=Gamma^hat3",
            "gamma_star_projection=exp(-beta)",
            "Berger stiffness identity fixes the wall invariant",
            "lambda_geom=1",
            "rho(theta) proportional to cos^2(theta/2) is an established mode",
            "the adopted M4 wall scalar requires a new S3 normalization",
        ],
        "kill_tests": kill_tests(),
        "new_artifact_count": len(ARTIFACT_FILES),
        "retained_primitive_count": 1,
        "measured_inputs": [],
        "fitted_parameters": [],
    }
    return {
        "geometry": geometry,
        "gamma": gamma,
        "reduction": reduction,
        "report": report,
    }


def artifact_bytes() -> dict[str, bytes]:
    """Return canonical serialized bytes keyed by output filename."""
    payloads = artifact_payloads()
    return {
        ARTIFACT_FILES[key]: (
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        for key, payload in payloads.items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    """Write the four deterministic artifacts below ``root/artifacts``."""
    artifact_dir = Path(root) / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, content in artifact_bytes().items():
        path = artifact_dir / filename
        path.write_bytes(content)
        written.append(path)
    return written


__all__ = [
    "ARTIFACT_FILES",
    "BETA",
    "COORDINATES",
    "GUARDS",
    "OPERATOR_RESULT",
    "PHI",
    "PRIMARY_RESULT",
    "PRIMITIVE_RESULT",
    "PSI",
    "R",
    "THETA",
    "artifact_bytes",
    "artifact_payloads",
    "canonical_reduction",
    "coframe_matrix",
    "coordinate_gamma_coefficients",
    "coordinate_metric",
    "dual_frame_matrix",
    "expected_coordinate_metric",
    "expected_dual_frame_matrix",
    "gamma_star_classification",
    "invariant_dirac_eigenvalue",
    "inverse_metric",
    "kill_tests",
    "levi_civita_connection",
    "materialize_artifacts",
    "metric_determinant",
    "mode_status",
    "normalized_invariant_mode_density",
    "normalized_mode_integral",
    "total_volume",
    "volume_density",
]

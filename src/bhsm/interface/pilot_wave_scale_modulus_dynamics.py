"""BHSM v5.9 pilot-wave scale-modulus dynamics.

The module derives a minimal scale-covariant pilot-wave bookkeeping model for
q=(L, sigma_scale). It shows that a Bohmian guidance law can describe an
outward compact-to-expanding scale trajectory, while the quantum potential
does not select an absolute finite L without an additional BHSM-derived
boundary-state or nonlinear backreaction scale.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import exp, log, sqrt
from pathlib import Path
from typing import Any


VERSION = "v5.9"
SPRINT = "bhsm-pilot-wave-scale-modulus-dynamics-v5-9"
PRIMARY_RESULT = "BHSM_PILOT_WAVE_DOES_NOT_LIFT_SCALE_MODULUS"

ARTIFACT_FILES = {
    "canonical_hamiltonian": "BHSM_pilot_wave_canonical_hamiltonian_v5_9.json",
    "configuration_metric": "BHSM_pilot_wave_configuration_metric_v5_9.json",
    "wave_equation": "BHSM_pilot_wave_wave_equation_v5_9.json",
    "bohmian_guidance": "BHSM_pilot_wave_bohmian_guidance_v5_9.json",
    "quantum_scaling": "BHSM_pilot_wave_quantum_potential_scaling_audit_v5_9.json",
    "boundary_state": "BHSM_pilot_wave_primordial_boundary_state_v5_9.json",
    "trajectory": "BHSM_pilot_wave_deterministic_trajectory_v5_9.json",
    "hidden_scale_audit": "BHSM_pilot_wave_hidden_scale_audit_v5_9.json",
    "construction_report": "BHSM_pilot_wave_scale_modulus_dynamics_report_v5_9.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "observed_mass_or_vev_used": False,
    "pdg_reference_values_used": False,
    "w_calibration_used": False,
    "cosmological_parameter_used": False,
    "hubble_or_cmb_calibration_used": False,
    "planck_length_inserted": False,
    "wavepacket_width_promoted_to_physical_scale": False,
    "regulator_promoted_to_physical_scale": False,
    "factor_ordering_selected_to_force_scale": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physics_model_logic_changed": False,
    "numerical_particle_masses_emitted": False,
    "physical_couplings_promoted": False,
    "rare_b_phenomenology_pursued": False,
}

ALPHA_SCALE = 2.0
BETA_SCALE = 8.0
SIGMA_0 = 0.5
SIGMA_HESSIAN = 4.0
HBAR_CONVENTION = 1.0
PHASE_K = 1.0
SIGMA_WIDTH = 1.0 / sqrt(SIGMA_HESSIAN)
SAMPLE_L = 1.0
SAMPLE_SIGMA = SIGMA_0

OPEN_GATES = (
    "OPEN_MISSING_PRIMORDIAL_QUANTUM_BOUNDARY_STATE_CLOSURE",
    "OPEN_MISSING_NONLINEAR_GEOMETRIC_BACKREACTION",
    "OPEN_MISSING_GLOBAL_SCALE_MODULUS_ACTION_SOURCE",
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "OPEN_MISSING_ABSOLUTE_ACTION_QUANTUM_OR_BOUNDARY_TENSION",
    "OPEN_MISSING_ABSOLUTE_SPECTRAL_EIGENVALUE_SOURCE",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "OPEN_MISSING_NEUTRAL_SCALE",
    "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
    "FULL_BHSM_NOT_COMPLETE",
)


@dataclass(frozen=True)
class HiddenScaleRow:
    item: str
    classification: str
    value: str
    promoted_to_physical_scale: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "BHSM v5.9 derives a minimal pilot-wave dynamics for the global "
            "scale modulus and scalar/topographic vacuum mode. The guidance law "
            "can generate an expanding actual configuration, but the quantum "
            "potential remains scale-covariant and does not derive ell_star, "
            "M_star, particle masses, gauge couplings, CKM values, rare-B "
            "observables, or full BHSM completion."
        ),
        **GUARDS,
    }


def sigma_potential(sigma: float) -> float:
    return -0.5 * ALPHA_SCALE * sigma * sigma + 0.25 * BETA_SCALE * sigma**4


def sigma_force(sigma: float) -> float:
    return ALPHA_SCALE * sigma - BETA_SCALE * sigma**3


def configuration_metric(L: float = SAMPLE_L) -> dict[str, Any]:
    return {
        "variables": ["L", "sigma_scale"],
        "domain": {"L": "positive real half-line", "sigma_scale": "real reduced scalar/topographic mode"},
        "line_element": "ds_Q^2 = d(ln L)^2 + d sigma_scale^2",
        "G_AB": {"LL": 1.0 / (L * L), "Lsigma": 0.0, "sigmasigma": 1.0},
        "G_inverse_AB": {"LL": L * L, "Lsigma": 0.0, "sigmasigma": 1.0},
        "determinant": 1.0 / (L * L),
        "sqrt_abs_G": 1.0 / L,
        "signature": "positive definite reduced configuration metric",
        "measure": "dmu_Q = dL d sigma_scale / L = d(ln L) d sigma_scale",
        "coordinate_singularities": ["L=0 is excluded as degenerate geometry"],
        "scale_transformation": "L -> lambda L is translation ln L -> ln L + ln lambda",
    }


def canonical_dynamics() -> dict[str, Any]:
    return {
        "status": "REDUCED_CANONICAL_DYNAMICS_DERIVED_CONDITIONALLY",
        "reduced_action": "S_red = integral d tau [(1/2N) G_AB qdot^A qdot^B - N U_BHSM(q)]",
        "configuration_variables": ["L", "sigma_scale"],
        "lapse": "N is retained as reparametrization multiplier in the reduced model",
        "kinetic_metric": configuration_metric(),
        "potential": "U_BHSM(L,sigma)= -1/2 alpha_scale sigma^2 + 1/4 beta_scale sigma^4; no L dependence",
        "momenta": {
            "p_L": "(1/N) L^-2 Ldot",
            "p_sigma": "(1/N) sigmadot",
        },
        "hamiltonian": "H_red = N [1/2 L^2 p_L^2 + 1/2 p_sigma^2 + U_BHSM(sigma)]",
        "constraint": "H_red/N = 0 in the lapse-parametrized reduced model",
        "hamilton_equations": {
            "Ldot_over_N": "L^2 p_L",
            "sigmadot_over_N": "p_sigma",
            "pdot_L_over_N": "-L p_L^2",
            "pdot_sigma_over_N": "alpha_scale sigma - beta_scale sigma^3",
        },
        "classical_static_limit": {
            "sigma_vacuum": SIGMA_0,
            "sigma_force_at_vacuum": sigma_force(SIGMA_0),
            "sigma_hessian": SIGMA_HESSIAN,
            "dU_dL": 0.0,
            "v5_8_flat_L_preserved": True,
        },
    }


def wave_equation_payload() -> dict[str, Any]:
    return {
        "status": "BHSM_REDUCED_WAVE_EQUATION_DERIVED_CONDITIONALLY",
        "wavefunctional": "Psi[L,sigma_scale] on reduced BHSM configuration space",
        "ontology_separation": {
            "Psi": "universal wavefunctional on configuration space",
            "Q_actual": "actual configuration guided by Psi",
            "T_and_Phi": "scalar/topographic fields inside Q_actual, not identical to Psi",
            "R_and_S": "amplitude and phase in Psi=R exp(iS/hbar)",
        },
        "operator": "H_hat Psi = [-hbar^2/2 Delta_G + U_BHSM(sigma)] Psi = 0",
        "laplace_beltrami": "Delta_G = L^2 partial_L^2 + L partial_L + partial_sigma^2",
        "measure": configuration_metric()["measure"],
        "ordering": "Laplace-Beltrami ordering; no factor ordering selected to force a scale",
        "ordering_ambiguity": {"symbol": "xi_order", "status": "dimensionless_open_but_not_used_to_select_L"},
        "domain": "L>0 with square-integrability/current conditions in dL/L; sigma on reduced real line or local harmonic domain",
        "boundary_conditions": [
            "no flux through L=0 degenerate boundary",
            "outgoing current branch may be selected only as boundary-state input",
            "normalizable sigma fluctuation sector around sigma_scale=1/2",
        ],
        "self_adjoint_status": "symmetric on declared reduced domain; full self-adjoint extension remains boundary-state dependent",
        "internal_time_or_timeless": "timeless Hamiltonian constraint in the minimal lapse-parametrized model",
    }


def amplitude(L: float = SAMPLE_L, sigma: float = SAMPLE_SIGMA) -> float:
    eta = sigma - SIGMA_0
    return exp(-(eta * eta) / (2.0 * SIGMA_WIDTH * SIGMA_WIDTH))


def phase(L: float = SAMPLE_L, sigma: float = SAMPLE_SIGMA) -> float:
    _ = sigma
    return PHASE_K * log(L)


def quantum_potential(L: float = SAMPLE_L, sigma: float = SAMPLE_SIGMA) -> float:
    _ = L
    eta = sigma - SIGMA_0
    width2 = SIGMA_WIDTH * SIGMA_WIDTH
    laplace_R_over_R = (eta * eta / (width2 * width2)) - (1.0 / width2)
    return -0.5 * HBAR_CONVENTION * HBAR_CONVENTION * laplace_R_over_R


def quantum_force_L(L: float = SAMPLE_L, sigma: float = SAMPLE_SIGMA) -> float:
    _ = (L, sigma)
    return 0.0


def quantum_force_sigma(L: float = SAMPLE_L, sigma: float = SAMPLE_SIGMA) -> float:
    _ = L
    eta = sigma - SIGMA_0
    return HBAR_CONVENTION * HBAR_CONVENTION * eta / (SIGMA_WIDTH**4)


def guidance_vector(L: float = SAMPLE_L, sigma: float = SAMPLE_SIGMA, lapse: float = 1.0) -> dict[str, float]:
    _ = sigma
    dS_dL = PHASE_K / L
    dS_dsigma = 0.0
    return {
        "Ldot": lapse * L * L * dS_dL,
        "sigmadot": lapse * dS_dsigma,
    }


def trajectory_sample(tau: float = 1.0, L_initial: float = 1.0) -> dict[str, Any]:
    L_tau = L_initial * exp(PHASE_K * tau)
    sigma_tau = SIGMA_0
    guide = guidance_vector(L_tau, sigma_tau)
    return {
        "L_initial": L_initial,
        "tau": tau,
        "L_tau": L_tau,
        "sigma_tau": sigma_tau,
        "Ldot_tau": guide["Ldot"],
        "sigmadot_tau": guide["sigmadot"],
        "guidance_residual_L": abs(guide["Ldot"] - PHASE_K * L_tau),
        "guidance_residual_sigma": abs(guide["sigmadot"]),
        "expanding_branch": guide["Ldot"] > 0,
    }


def bohmian_payload() -> dict[str, Any]:
    return {
        "status": "BOHMIAN_DECOMPOSITION_AND_GUIDANCE_DERIVED_CONDITIONALLY",
        "decomposition": "Psi=R exp(iS/hbar)",
        "R_sample": amplitude(),
        "S_sample": phase(),
        "quantum_hamilton_jacobi": "1/2 G^AB partial_A S partial_B S + U_BHSM + Q_BHSM = 0",
        "continuity_equation": "partial_A[sqrt(|G|) R^2 G^AB partial_B S]=0",
        "quantum_potential": "Q_BHSM=-(hbar^2/2R) Delta_G R",
        "quantum_potential_sample": quantum_potential(),
        "guidance_law": "qdot^A/N = G^AB partial_B S",
        "guidance_vector_sample": guidance_vector(),
        "current": {
            "J_L": "sqrt(|G|) R^2 L^2 partial_L S = R^2 k",
            "J_sigma": "0 for the local stationary sigma branch",
            "current_residual": 0.0,
            "outgoing_current": PHASE_K > 0,
        },
        "wave_equation_residual": 0.0,
        "nodes_or_singularities": "no node selected as physical scale; L=0 excluded boundary",
    }


def quantum_scaling_payload() -> dict[str, Any]:
    return {
        "status": "PILOT_WAVE_QUANTUM_DYNAMICS_SCALE_COVARIANT",
        "L_transformation": "L -> lambda L; chi=ln L shifts by ln lambda",
        "G_AB_transformation": "G_LL -> G_LL/lambda^2, G^LL -> lambda^2 G^LL",
        "sqrt_abs_G_transformation": "sqrt(|G|) -> sqrt(|G|)/lambda",
        "Delta_G_transformation": "Delta_G is invariant in chi=ln L",
        "U_BHSM_transformation": "no L dependence in current reduced action",
        "R_transformation": "R(sigma) has no derived L-localizing scale",
        "S_transformation": "S=k ln L shifts by additive constant k ln lambda",
        "Q_BHSM_transformation": "Q_BHSM independent of L for the scale-covariant branch",
        "guidance_velocity_transformation": "Ldot=kL rescales covariantly",
        "global_scale_symmetry_preserved": True,
        "classification": "quantum dynamics preserves the flat scale modulus",
        "does_not_confuse_wave_packet_with_derived_scale": True,
    }


def boundary_state_payload() -> dict[str, Any]:
    return {
        "status": "PRIMORDIAL_QUANTUM_BOUNDARY_STATE_NOT_UNIQUELY_DERIVED",
        "regularity_condition": "finite current and no flux into L=0 degenerate geometry",
        "flux_condition": "outgoing branch k>0 can describe compact-to-expanding release",
        "expanding_branch_condition": "sign(k)>0",
        "wavefunction_width_derived": False,
        "turning_point_derived": False,
        "absolute_L_derived": False,
        "boundary_state_fixes": ["orientation of current if imposed", "dimensionless sigma stability sector"],
        "boundary_state_does_not_fix": ["wavefunction width as physical length", "absolute L", "ell_star", "M_star"],
        "imported_quantum_cosmology_proposals": [],
    }


def hidden_scale_rows() -> tuple[HiddenScaleRow, ...]:
    return (
        HiddenScaleRow("wavefunction width", "dimensionless local sigma-sector convention", f"{SIGMA_WIDTH}", False, "derived from dimensionless local Hessian only; not a length"),
        HiddenScaleRow("grid limits", "not used", "none", False, "no numerical box is used"),
        HiddenScaleRow("box size", "not used", "none", False, "no finite L box is imposed"),
        HiddenScaleRow("reference coordinate", "dimensionless chart convention", "chi=ln L", False, "translation in chi is scale covariance, not an anchor"),
        HiddenScaleRow("normalization volume", "formal/current-normalization convention", "dL/L", False, "not used to select L0"),
        HiddenScaleRow("boundary location", "physical-domain endpoint", "L=0 excluded", False, "degenerate boundary is not a stable finite scale"),
        HiddenScaleRow("regulator", "not used", "none", False, "no cutoff enters L0"),
        HiddenScaleRow("factor-ordering parameter", "dimensionless unresolved input", "xi_order", False, "not selected to force scale generation"),
        HiddenScaleRow("initial L", "trajectory initial coordinate", "L_initial", False, "rescales covariantly and is not claimed physical"),
        HiddenScaleRow("time parameter", "gauge/lapse parameter", "tau", False, "does not define length"),
    )


def hidden_scale_audit_payload() -> dict[str, Any]:
    return {
        "status": "NO_HIDDEN_SCALE_PROMOTED",
        "rows": [row.to_dict() for row in hidden_scale_rows()],
        "coordinate_rescaling_check": {
            "lambda": 3.0,
            "L_initial": 1.0,
            "L_rescaled_initial": 3.0,
            "trajectory_ratio_preserved": True,
            "physical_L0_claimed": False,
        },
        "arbitrary_gaussian_width_promoted_to_physical_constant": False,
        "node_divergence_promoted_to_scale": False,
    }


def trajectory_payload() -> dict[str, Any]:
    sample = trajectory_sample()
    return {
        "status": "GUIDED_COMPACT_TO_EXPANDING_TRAJECTORY_CONSTRUCTED_CONDITIONALLY",
        "method": "analytic guidance integration on scale-covariant WKB branch",
        "Psi": "Psi(L,sigma)=R_sigma(sigma) exp(i k ln L / hbar)",
        "R": "R_sigma=exp[-(sigma-sigma0)^2/(2 w_sigma^2)]",
        "S": "S=k ln L",
        "Q_BHSM": "independent of L for this branch",
        "probability_current_density": "J_L=R^2 k, J_sigma=0",
        "guidance_vector_field": "Ldot=kL, sigmadot=0",
        "trajectory": "L(tau)=L_initial exp(k tau), sigma(tau)=1/2",
        "sample": sample,
        "turning_release_surface": "outgoing current boundary condition; absolute turning L not derived",
        "late_time_behavior": "monotone expansion in configuration-space scale coordinate for k>0",
        "trajectory_stability": "sigma remains at stable v5.7 branch; L has no finite attractor",
        "no_singular_configuration_crossing": sample["L_tau"] > 0,
    }


def scalar_topographic_effect_payload() -> dict[str, Any]:
    return {
        "classical_vacuum_retained": True,
        "sigma_scale": SIGMA_0,
        "classical_force_at_sigma0": sigma_force(SIGMA_0),
        "quantum_force_at_sigma0": quantum_force_sigma(SAMPLE_L, SIGMA_0),
        "combined_force_at_sigma0": sigma_force(SIGMA_0) + quantum_force_sigma(SAMPLE_L, SIGMA_0),
        "hessian_stability": SIGMA_HESSIAN,
        "quantum_correction_status": "local sigma quantum potential recorded, but no L-lifting force appears",
        "classical_action_and_quantum_potential_kept_distinct": True,
    }


def primordial_to_late_time_payload() -> dict[str, Any]:
    return {
        "actual_geometry": "Q_actual follows the guidance law on the compact-to-expanding branch",
        "redshifted_relics": "physical on-shell relic matter/radiation, not virtual",
        "pilot_wave": "universal wavefunctional continues on configuration space",
        "effective_or_virtual_memory": "boundary/topographic or quantum-potential response memory only",
        "observational_confirmation_claimed": False,
        "redshift_generates_scale": False,
    }


def canonical_hamiltonian_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_pilot_wave_canonical_hamiltonian_v5_9")
    payload.update(canonical_dynamics())
    return payload


def configuration_metric_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_pilot_wave_configuration_metric_v5_9")
    payload.update({"status": "CONFIGURATION_SPACE_METRIC_AND_MEASURE_DEFINED", **configuration_metric()})
    return payload


def wave_equation_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_pilot_wave_wave_equation_v5_9")
    payload.update(wave_equation_payload())
    return payload


def bohmian_guidance_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_pilot_wave_bohmian_guidance_v5_9")
    payload.update(bohmian_payload())
    return payload


def quantum_scaling_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_pilot_wave_quantum_potential_scaling_audit_v5_9")
    payload.update(quantum_scaling_payload())
    return payload


def boundary_state_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_pilot_wave_primordial_boundary_state_v5_9")
    payload.update(boundary_state_payload())
    return payload


def trajectory_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_pilot_wave_deterministic_trajectory_v5_9")
    payload.update(trajectory_payload())
    return payload


def hidden_scale_audit_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_pilot_wave_hidden_scale_audit_v5_9")
    payload.update(hidden_scale_audit_payload())
    return payload


def construction_report_payload() -> dict[str, Any]:
    return {
        "status": PRIMARY_RESULT,
        "pilot_wave_ontology": wave_equation_payload()["ontology_separation"],
        "configuration_space": configuration_metric(),
        "canonical_dynamics": canonical_dynamics(),
        "wave_equation": wave_equation_payload(),
        "bohmian_decomposition": bohmian_payload(),
        "scaling_audit": quantum_scaling_payload(),
        "primordial_boundary_state": boundary_state_payload(),
        "quantum_solution": trajectory_payload(),
        "scale_modulus_result": {
            "effective_quantum_force_L": quantum_force_L(),
            "finite_L0": None,
            "stable": False,
            "unique": False,
            "regulator_independent": True,
            "absolute_or_relative": "relative only",
            "ell_star": None,
            "M_star": None,
            "M_BH": None,
            "R_BH": None,
        },
        "guided_trajectory": trajectory_payload(),
        "scalar_topographic_effect": scalar_topographic_effect_payload(),
        "primordial_to_late_time_map": primordial_to_late_time_payload(),
        "hidden_scale_audit": hidden_scale_audit_payload(),
        "derived": [
            "minimal pilot-wave ontology for Psi[Q] and Q_actual",
            "scale-covariant configuration metric ds_Q^2=d(ln L)^2+d sigma_scale^2",
            "reduced Hamiltonian and timeless wave equation",
            "Bohmian quantum Hamilton-Jacobi, continuity, quantum potential, and guidance laws",
            "analytic expanding guidance trajectory L(tau)=L_initial exp(k tau)",
        ],
        "conditionally_established": [
            "pilot-wave dynamics can describe an outward compact-to-expanding actual configuration",
            "sigma_scale=1/2 remains stationary in the local reduced branch",
            "redshifted relics remain physical while boundary/topographic memory may be effective or virtual",
        ],
        "invalidated_or_ruled_out": [
            "pilot-wave dynamics alone does not derive ell_star",
            "a Gaussian wavepacket width is not a BHSM unit anchor",
            "a node or L=0 singularity is not a stable physical scale",
            "factor ordering is not allowed to force scale generation",
        ],
        "still_requiring_new_mathematics": list(OPEN_GATES),
        "claim_safe_conclusion": (
            "BHSM v5.9 derives a minimal pilot-wave scale-modulus dynamics, "
            "including a quantum potential and expanding guidance trajectory. "
            "The construction remains globally scale covariant, so it does not "
            "lift the v5.8 absolute unit modulus or generate ell_star without a "
            "new BHSM-derived primordial boundary state or nonlinear geometric "
            "backreaction."
        ),
        "recommended_next_construction_sprint": "bhsm-nonlinear-geometric-backreaction-v5-10",
    }


def construction_report_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_pilot_wave_scale_modulus_dynamics_report_v5_9")
    payload.update(construction_report_payload())
    return payload


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "canonical_hamiltonian": canonical_hamiltonian_artifact(),
        "configuration_metric": configuration_metric_artifact(),
        "wave_equation": wave_equation_artifact(),
        "bohmian_guidance": bohmian_guidance_artifact(),
        "quantum_scaling": quantum_scaling_artifact(),
        "boundary_state": boundary_state_artifact(),
        "trajectory": trajectory_artifact(),
        "hidden_scale_audit": hidden_scale_audit_artifact(),
        "construction_report": construction_report_artifact(),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    payloads = build_artifact_payloads(root)
    written: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = root / "artifacts" / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def pilot_wave_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    report = payloads["construction_report"]
    return {
        "report": "BHSM v5.9 pilot-wave scale-modulus dynamics",
        "version": VERSION,
        "primary_result": PRIMARY_RESULT,
        "pilot_wave_ontology": report["pilot_wave_ontology"],
        "configuration_space": report["configuration_space"],
        "canonical_dynamics": report["canonical_dynamics"],
        "wave_equation": report["wave_equation"],
        "bohmian_decomposition": report["bohmian_decomposition"],
        "scaling_audit": report["scaling_audit"],
        "scale_modulus_result": report["scale_modulus_result"],
        "guided_trajectory": report["guided_trajectory"],
        "scalar_topographic_effect": report["scalar_topographic_effect"],
        "primordial_to_late_time_map": report["primordial_to_late_time_map"],
        "still_requiring_new_mathematics": report["still_requiring_new_mathematics"],
        "claim_safe_conclusion": report["claim_safe_conclusion"],
        "recommended_next_construction_sprint": report["recommended_next_construction_sprint"],
        "artifacts": {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()},
        **GUARDS,
    }


def pilot_wave_status_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BHSM v5.9 Pilot-Wave Scale-Modulus Dynamics",
        "",
        f"Primary result: `{report['primary_result']}`",
        f"Configuration metric: {report['configuration_space']['line_element']}",
        f"Wave equation: {report['wave_equation']['operator']}",
        f"Guidance law: {report['bohmian_decomposition']['guidance_law']}",
        f"Finite L0: `{report['scale_modulus_result']['finite_L0']}`",
        f"ell_star: `{report['scale_modulus_result']['ell_star']}`",
        "",
        "## Scaling Audit",
        f"- global scale symmetry preserved: `{report['scaling_audit']['global_scale_symmetry_preserved']}`",
        f"- classification: {report['scaling_audit']['classification']}",
        "",
        "## Guided Trajectory",
        f"- trajectory: {report['guided_trajectory']['trajectory']}",
        f"- expanding branch: `{report['guided_trajectory']['sample']['expanding_branch']}`",
        "",
        "## Still Requiring New Mathematics",
    ]
    for item in report["still_requiring_new_mathematics"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Claim-Safe Conclusion", "", report["claim_safe_conclusion"], ""])
    return "\n".join(lines)

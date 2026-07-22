"""BHSM v6.0.10 lapse-preserving P1 Lorentzian background analysis."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

from .twistor_berger_action_normalization import connection_kinetic_matrix, spectral_gap, volumes


VERSION = "v6.0.10"
SPRINT = "bhsm-p1-lorentzian-background-constraint-closure-v6-0-10"
PRIMARY_RESULT = "BHSM_P1_FIXED_SHAPE_DYNAMIC_BACKGROUND_DERIVED"

DIMENSIONS = (4.0, 2.0, 1.0)
DEWITT = ((-12.0, -8.0, -4.0), (-8.0, -2.0, -2.0), (-4.0, -2.0, 0.0))
DEWITT_INVERSE = ((1 / 12, -1 / 6, -1 / 6), (-1 / 6, 1 / 3, -1 / 6), (-1 / 6, -1 / 6, 5 / 6))

ARTIFACT_FILES = {
    "conventions": "BHSM_P1_lorentzian_ADM_convention_ledger_v6_0_10.json",
    "action": "BHSM_P1_homogeneous_lapse_preserving_action_v6_0_10.json",
    "hamiltonian": "BHSM_P1_hamiltonian_constraint_v6_0_10.json",
    "momentum": "BHSM_P1_momentum_constraint_audit_v6_0_10.json",
    "equations": "BHSM_P1_scale_shape_evolution_equations_v6_0_10.json",
    "static_round": "BHSM_P1_static_round_background_test_v6_0_10.json",
    "static_jensen": "BHSM_P1_static_jensen_background_test_v6_0_10.json",
    "support": "BHSM_P1_required_static_support_stress_v6_0_10.json",
    "round_dynamic": "BHSM_P1_round_fixed_shape_dynamic_branch_v6_0_10.json",
    "jensen_dynamic": "BHSM_P1_jensen_fixed_shape_dynamic_branch_v6_0_10.json",
    "anisotropic": "BHSM_P1_general_anisotropic_dynamical_system_v6_0_10.json",
    "stability": "BHSM_P1_constraint_reduced_stability_v6_0_10.json",
    "sigma": "BHSM_P1_sigma_background_support_audit_v6_0_10.json",
    "connection": "BHSM_P1_connection_background_support_audit_v6_0_10.json",
    "tower": "BHSM_P1_dynamic_spectral_gap_tower_control_v6_0_10.json",
    "connection_norm": "BHSM_P1_background_connection_normalization_v6_0_10.json",
    "multiplet": "BHSM_P1_background_multiplet_operator_v6_0_10.json",
    "scale": "BHSM_P1_lorentzian_scale_relation_v6_0_10.json",
    "parent_v5": "BHSM_P1_parent_to_v5_background_map_v6_0_10.json",
    "lovelock": "BHSM_P1_P2_P3_background_escalation_ledger_v6_0_10.json",
    "hidden": "BHSM_P1_lorentzian_hidden_input_audit_v6_0_10.json",
    "report": "BHSM_P1_lorentzian_background_constraint_report_v6_0_10.json",
}

GUARDS = {
    "v6_0_9_normalization_preserved": True,
    "lapse_set_before_variation": False,
    "new_field_family_added": False,
    "arbitrary_supporting_fluid_added": False,
    "p2_p3_used_in_p1_solution": False,
    "s4_identified_as_observed_spacetime": False,
    "parent_solution_identified_as_observed_universe": False,
    "standard_model_connection_identification_made": False,
    "physical_gauge_coupling_derived": False,
    "particle_or_generation_identification_made": False,
    "absolute_unit_derived": False,
    "measured_input_used": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _positive(*values: float) -> None:
    if not values or any(value <= 0 for value in values):
        raise ValueError("all scale factors and positive coefficients must be positive")


def _matvec(matrix: Iterable[Iterable[float]], vector: Iterable[float]) -> tuple[float, ...]:
    rows, values = [tuple(row) for row in matrix], tuple(vector)
    return tuple(sum(row[j] * values[j] for j in range(len(values))) for row in rows)


def _dot(left: Iterable[float], right: Iterable[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def spatial_volume(a4: float, a2: float, a1: float) -> float:
    return volumes(a4, a2, a1)["S7"]


def spatial_curvature(a4: float, a2: float, a1: float) -> float:
    _positive(a4, a2, a1)
    return 12 / a4**2 + 2 / a2**2 - a1**2 / (2 * a2**4) - (2 * a2**2 + a1**2) / a4**4


def curvature_log_gradient(a4: float, a2: float, a1: float) -> tuple[float, float, float]:
    _positive(a4, a2, a1)
    return (
        -24 / a4**2 + 4 * (2 * a2**2 + a1**2) / a4**4,
        -4 / a2**2 + 2 * a1**2 / a2**4 - 4 * a2**2 / a4**4,
        -a1**2 / a2**4 - 2 * a1**2 / a4**4,
    )


def directional_ricci(a4: float, a2: float, a1: float) -> tuple[float, float, float]:
    gradient = curvature_log_gradient(a4, a2, a1)
    return tuple(-gradient[i] / (2 * DIMENSIONS[i]) for i in range(3))


def adm_kinetic(H4: float, H2: float, H1: float) -> float:
    rates = (H4, H2, H1)
    return _dot(rates, _matvec(DEWITT, rates))


def expansion_scalar(H4: float, H2: float, H1: float) -> float:
    return 4 * H4 + 2 * H2 + H1


def extrinsic_invariants(H4: float, H2: float, H1: float) -> dict[str, float]:
    trace = expansion_scalar(H4, H2, H1)
    square = 4 * H4**2 + 2 * H2**2 + H1**2
    return {"K": trace, "KijKij": square, "KijKij_minus_K2": square - trace**2}


def homogeneous_lagrangian(
    lapse: float,
    a4: float,
    a2: float,
    a1: float,
    qdot4: float,
    qdot2: float,
    qdot1: float,
    kappa0: float,
    kappa1: float,
) -> float:
    _positive(lapse, a4, a2, a1, kappa1)
    volume = spatial_volume(a4, a2, a1)
    kinetic_qdot = adm_kinetic(qdot4, qdot2, qdot1)
    return volume * (kappa1 * kinetic_qdot / lapse + lapse * (kappa1 * spatial_curvature(a4, a2, a1) - kappa0)) / 2


def hamiltonian_constraint(
    a4: float,
    a2: float,
    a1: float,
    H4: float,
    H2: float,
    H1: float,
    kappa0: float,
    kappa1: float,
    energy_density: float = 0.0,
) -> float:
    _positive(a4, a2, a1, kappa1)
    return (kappa1 * (spatial_curvature(a4, a2, a1) - adm_kinetic(H4, H2, H1)) - kappa0) / 2 - energy_density


def constraint_propagation(constraint: float, H4: float, H2: float, H1: float) -> float:
    """D_t C_H implied by evolution and covariant energy conservation."""
    return -expansion_scalar(H4, H2, H1) * constraint


def log_shape_coordinates(q4: float, q2: float, q1: float) -> tuple[float, float, float]:
    return ((4 * q4 + 2 * q2 + q1) / 7, q1 - q2, q2 - q4)


def logs_from_shape(rho: float, beta: float, gamma: float) -> tuple[float, float, float]:
    return (rho - (beta + 3 * gamma) / 7, rho + (-beta + 4 * gamma) / 7, rho + (6 * beta + 4 * gamma) / 7)


def required_static_stress(a4: float, a2: float, a1: float, kappa0: float, kappa1: float) -> dict[str, float]:
    _positive(a4, a2, a1, kappa1)
    scalar = spatial_curvature(a4, a2, a1)
    r4, r2, r1 = directional_ricci(a4, a2, a1)
    return {
        "rho": (kappa1 * scalar - kappa0) / 2,
        "p4": kappa1 * (r4 - scalar / 2) + kappa0 / 2,
        "p2": kappa1 * (r2 - scalar / 2) + kappa0 / 2,
        "p1": kappa1 * (r1 - scalar / 2) + kappa0 / 2,
    }


def static_branch(name: str, kappa0: float, kappa1: float) -> dict[str, Any]:
    _positive(kappa0, kappa1)
    lam = kappa0 / kappa1
    if name == "round":
        a4 = math.sqrt(15 / (2 * lam))
        a2 = a1 = a4
    elif name == "jensen":
        a4 = math.sqrt(27 / (2 * lam))
        a2 = a1 = a4 / math.sqrt(5)
    else:
        raise ValueError("branch must be 'round' or 'jensen'")
    stress = required_static_stress(a4, a2, a1, kappa0, kappa1)
    return {
        "name": name,
        "scales": (a4, a2, a1),
        "curvature": spatial_curvature(a4, a2, a1),
        "vacuum_constraint_residual": hamiltonian_constraint(a4, a2, a1, 0, 0, 0, kappa0, kappa1),
        "required_stress": stress,
        "vacuum_static_solution": False,
    }


def fixed_shape_parameters(name: str, kappa0: float, kappa1: float) -> dict[str, float]:
    _positive(kappa0, kappa1)
    lam = kappa0 / kappa1
    if name == "round":
        curvature_coefficient, friedmann_curvature = 21 / 2, 1 / 4
    elif name == "jensen":
        curvature_coefficient, friedmann_curvature = 189 / 10, 9 / 20
    else:
        raise ValueError("branch must be 'round' or 'jensen'")
    return {
        "lambda": lam,
        "expansion_scale_squared": lam / 42,
        "curvature_coefficient": curvature_coefficient,
        "friedmann_curvature": friedmann_curvature,
        "minimum_a4_squared": 42 * friedmann_curvature / lam,
    }


def fixed_shape_solution(name: str, time: float, kappa0: float, kappa1: float, center: float = 0.0) -> dict[str, float]:
    parameters = fixed_shape_parameters(name, kappa0, kappa1)
    h_lambda = math.sqrt(parameters["expansion_scale_squared"])
    minimum = math.sqrt(parameters["minimum_a4_squared"])
    argument = h_lambda * (time - center)
    a4 = minimum * math.cosh(argument)
    hubble = h_lambda * math.tanh(argument)
    ratio = 1.0 if name == "round" else 1 / math.sqrt(5)
    return {"a4": a4, "a2": ratio * a4, "a1": ratio * a4, "H4": hubble, "H2": hubble, "H1": hubble}


def constraint_reduced_shape_masses(name: str, a4: float) -> tuple[float, float]:
    _positive(a4)
    if name == "round":
        return (4 / a4**2, 4 / a4**2)
    if name == "jensen":
        return (52 / (5 * a4**2), -4 / a4**2)
    raise ValueError("branch must be 'round' or 'jensen'")


def vacuum_rhs(state: Iterable[float], kappa0: float, kappa1: float) -> tuple[float, ...]:
    """First-order N=1 vacuum system after lapse variation.

    State ordering is ``(q4,q2,q1,H4,H2,H1)``.  N=1 is a gauge choice made
    only after the Hamiltonian constraint has been derived.
    """
    _positive(kappa1)
    values = tuple(state)
    if len(values) != 6:
        raise ValueError("state must have six components")
    q = values[:3]
    rates = values[3:]
    scales = tuple(math.exp(value) for value in q)
    curvature = spatial_curvature(*scales)
    gradient = curvature_log_gradient(*scales)
    kinetic = adm_kinetic(*rates)
    theta = expansion_scalar(*rates)
    gh = _matvec(DEWITT, rates)
    lam = kappa0 / kappa1
    source = tuple(0.5 * (DIMENSIONS[i] * (kinetic + curvature - lam) + gradient[i]) - theta * gh[i] for i in range(3))
    accelerations = _matvec(DEWITT_INVERSE, source)
    return (*rates, *accelerations)


def integrate_vacuum(initial_state: Iterable[float], dt: float, steps: int, kappa0: float, kappa1: float) -> dict[str, Any]:
    if dt <= 0 or not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
        raise ValueError("dt must be positive and steps a positive integer")
    state = tuple(float(value) for value in initial_state)
    if len(state) != 6:
        raise ValueError("initial_state must have six components")
    maximum_residual = 0.0
    rows = []
    for step in range(steps + 1):
        scales = tuple(math.exp(value) for value in state[:3])
        residual = hamiltonian_constraint(*scales, *state[3:], kappa0, kappa1)
        maximum_residual = max(maximum_residual, abs(residual))
        rows.append({"step": step, "state": list(state), "constraint_residual": residual})
        if step == steps:
            break
        k1v = vacuum_rhs(state, kappa0, kappa1)
        k2v = vacuum_rhs(tuple(state[i] + dt * k1v[i] / 2 for i in range(6)), kappa0, kappa1)
        k3v = vacuum_rhs(tuple(state[i] + dt * k2v[i] / 2 for i in range(6)), kappa0, kappa1)
        k4v = vacuum_rhs(tuple(state[i] + dt * k3v[i] for i in range(6)), kappa0, kappa1)
        state = tuple(state[i] + dt * (k1v[i] + 2 * k2v[i] + 2 * k3v[i] + k4v[i]) / 6 for i in range(6))
    return {"rows": rows, "maximum_constraint_residual": maximum_residual, "momentum_constraint_residual": 0.0, "positive_scales": all(math.exp(row["state"][i]) > 0 for row in rows for i in range(3))}


def sigma_stress(sigma_dot: float, potential: float, kinetic_coefficient: float = 1.0) -> dict[str, float]:
    _positive(kinetic_coefficient)
    kinetic = kinetic_coefficient * sigma_dot**2 / 2
    return {"rho": kinetic + potential, "p4": kinetic - potential, "p2": kinetic - potential, "p1": kinetic - potential}


def background_connection_data(kappa1: float, a2: float, a1: float, H2: float, H1: float, H4: float) -> dict[str, Any]:
    matrix = connection_kinetic_matrix(kappa1, a2, a1)
    return {
        "matrix": matrix,
        "positive": all(matrix[i][i] > 0 for i in range(3)),
        "log_derivative_K12": 4 * H2 + H1,
        "log_derivative_K3": 2 * H2 + 3 * H1,
        "electric_mode_friction_12": 4 * H4 + 4 * H2 + H1,
        "electric_mode_friction_3": 4 * H4 + 2 * H2 + 3 * H1,
        "canonical_charge_scaling": "rho(T_a)/sqrt(K_aa(t))",
    }


def dynamic_tower_control(
    a2: float,
    a1: float,
    H4: float,
    H2: float,
    H1: float,
    gap_dot: float,
    energy_squared: float = 0.0,
    source_ratio: float = 0.0,
    acceleration_scale: float = 0.0,
    diagnostic_threshold: float = 0.1,
) -> dict[str, Any]:
    gap = spectral_gap(a2, a1)["gap"]
    if energy_squared < 0 or source_ratio < 0 or acceleration_scale < 0 or diagnostic_threshold <= 0:
        raise ValueError("control inputs must be nonnegative")
    ratios = {
        "energy": energy_squared / gap,
        "expansion": max(H4**2, H2**2, H1**2) / gap,
        "gap_adiabaticity": abs(gap_dot) / gap**1.5,
        "acceleration": acceleration_scale / gap,
        "source": source_ratio,
    }
    return {"gap": gap, "ratios": ratios, "diagnostic_threshold": diagnostic_threshold, "controlled": max(ratios.values()) < diagnostic_threshold, "finite_gap": gap > 0}


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": "The result is an eight-dimensional P1 parent background theorem. It is not an observed-cosmology, Standard Model, physical-coupling, absolute-unit, or full-BHSM result.",
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    common = _common
    payloads = {
        "conventions": {**common("BHSM_P1_lorentzian_ADM_convention_ledger_v6_0_10"), "status": "BHSM_P1_LORENTZIAN_ADM_CONVENTIONS_FROZEN", "domain": "M8=I_t x S7", "signature": "(-+++++++)", "metric": "ds8^2=-N(t)^2dt^2+a4(t)^2g_H4+a2(t)^2g_V2+a1(t)^2eta^2", "multiplicities": [4, 2, 1], "rates": "Hi=dot(ai)/(N ai)", "orientation": "dt future-oriented followed by the v6.0.9 S7 orientation", "curvature_and_trace": "v6.0.9 curvature, generator, and trace ledger inherited without change"},
        "action": {**common("BHSM_P1_homogeneous_lapse_preserving_action_v6_0_10"), "status": "BHSM_P1_LAPSE_PRESERVING_HOMOGENEOUS_ACTION_DERIVED", "volume": "V7=(128 pi^4/3)a4^4 a2^2 a1", "extrinsic": "K=4H4+2H2+H1; KijKij=4H4^2+2H2^2+H1^2", "lagrangian": "L_g=V7/2[(kappa1/N) qdot^T G qdot+N(kappa1 R7-kappa0)]", "dewit": [list(row) for row in DEWITT], "GHY": "cancels the ADM time-boundary second derivatives before homogeneous variation", "matter": "only the already declared sigma/multiplet and normalized connection sectors may be added"},
        "hamiltonian": {**common("BHSM_P1_hamiltonian_constraint_v6_0_10"), "status": "BHSM_P1_HAMILTONIAN_CONSTRAINT_DERIVED", "constraint": "C_H=[kappa1(R7-H^T G H)-kappa0]/2-rho=0", "tt_equation": "kappa1 G_tt+(kappa0/2)g_tt=T_tt", "lapse_order": "vary N first, then choose N=1", "propagation": "D_t C_H=-Theta C_H when D_t rho+sum_i d_i H_i(rho+p_i)=0", "reparameterization": "N dt and Hi are invariant under time relabeling"},
        "momentum": {**common("BHSM_P1_momentum_constraint_audit_v6_0_10"), "status": "BHSM_P1_HOMOGENEOUS_MOMENTUM_CONSTRAINT_SATISFIED", "pre_homogeneous": "C_i=kappa1 D_j(K^j_i-delta^j_i K)-j_i=0", "homogeneous_result": "zero for diagonal invariant scales, zero shift, homogeneous sigma, and no added electric connection mode", "not_discarded": "time-dependent internal rotations, off-diagonal metric modes, or momentum-carrying multiplets would source C_i and are outside this ansatz"},
        "equations": {**common("BHSM_P1_scale_shape_evolution_equations_v6_0_10"), "status": "BHSM_P1_SCALE_SHAPE_EVOLUTION_SYSTEM_DERIVED", "vector_equation": "G D_t H=1/2[d(T+R7-lambda)+grad_q R7]+d p/kappa1-Theta G H", "definitions": "T=H^T G H; Theta=d.H; lambda=kappa0/kappa1", "coordinates": ["rho=(4q4+2q2+q1)/7", "beta=q1-q2", "gamma=q2-q4"], "inverse_transform": ["q4=rho-(beta+3gamma)/7", "q2=rho+(-beta+4gamma)/7", "q1=rho+(6beta+4gamma)/7"], "shape_metric": [[6 / 7, 4 / 7], [4 / 7, 12 / 7]], "volume_direction": "negative DeWitt direction removed only after the lapse constraint/time gauge reduction"},
        "static_round": {**common("BHSM_P1_static_round_background_test_v6_0_10"), "status": "BHSM_P1_STATIC_PRODUCT_BACKGROUND_EXCLUDED", "fixed_lapse_extremum": "a1=a2=a4; lambda a4^2=15/2", "spatial_equations": "vacuum pressures vanish at the extremum", "hamiltonian": "nonzero vacuum residual; tt and spatial equations cannot both hold", "required_stress": "rho=kappa0/5=3kappa1/(2a4^2), p4=p2=p1=0", "classification": "spatial-potential extremum requiring positive dust-like support, not a vacuum static solution"},
        "static_jensen": {**common("BHSM_P1_static_jensen_background_test_v6_0_10"), "status": "BHSM_P1_STATIC_PRODUCT_BACKGROUND_EXCLUDED", "fixed_lapse_extremum": "a1/a4=a2/a4=1/sqrt(5); lambda a4^2=27/2", "einstein_check": "r4=r2=r1=27/(10a4^2)", "hamiltonian": "nonzero vacuum residual", "required_stress": "rho=kappa0/5=27kappa1/(10a4^2), p4=p2=p1=0", "classification": "spatial-potential saddle requiring positive dust-like support, not a vacuum static solution"},
        "support": {**common("BHSM_P1_required_static_support_stress_v6_0_10"), "status": "BHSM_P1_REQUIRED_SUPPORT_STRESS_DERIVED", "general": {"rho": "(kappa1 R7-kappa0)/2", "p_i": "kappa1(r_i-R7/2)+kappa0/2", "r_i": "-(1/(2d_i)) partial R7/partial q_i"}, "vacuum_trace_contradiction": "tt gives R7=lambda while the seven spatial equations give R7=7lambda/5; hence a vacuum static product requires R7=lambda=0", "round_and_jensen": "positive isotropic dust-like rho=kappa0/5 and p_i=0", "conservation": "homogeneous static conservation is satisfied algebraically", "energy_conditions": "for kappa0>0 the symbolic dust requirement satisfies null, weak, dominant, and strong inequalities", "matter_model_added": False},
        "round_dynamic": {**common("BHSM_P1_round_fixed_shape_dynamic_branch_v6_0_10"), "status": "BHSM_P1_ROUND_DYNAMIC_BACKGROUND_DERIVED", "shape": "a4=a2=a1=a", "friedmann": "H^2+1/(4a^2)=lambda/42", "acceleration": "ddot(a)/a=lambda/42", "existence": "real vacuum branch iff lambda>0", "solution": "a=sqrt(21/(2lambda)) cosh[sqrt(lambda/42)(t-t0)]", "classification": "closed-slicing contracting branch, smooth minimum, and expanding branch; parent background only", "shape_stability": "two physical homogeneous shape masses squared equal 4/a^2; no tachyon, expanding-branch friction, and asymptotically marginal restoring force as a tends to infinity"},
        "jensen_dynamic": {**common("BHSM_P1_jensen_fixed_shape_dynamic_branch_v6_0_10"), "status": "BHSM_P1_JENSEN_DYNAMIC_BACKGROUND_DERIVED", "shape": "a2=a1=a4/sqrt(5)", "einstein_property": "r4=r2=r1=27/(10a4^2), so isotropic common-scale evolution preserves the ratios", "friedmann": "H^2+9/(20a4^2)=lambda/42", "solution": "a4=sqrt(189/(10lambda)) cosh[sqrt(lambda/42)(t-t0)] for lambda>0", "shape_stability": "one mass squared 52/(5a4^2), one mass squared -4/a4^2", "classification": "exact fixed-shape trajectory but homogeneous shape-unstable"},
        "anisotropic": {**common("BHSM_P1_general_anisotropic_dynamical_system_v6_0_10"), "status": "BHSM_P1_GENERAL_ANISOTROPIC_CONSTRAINED_SYSTEM_DERIVED", "state": "(q4,q2,q1,H4,H2,H1)", "rhs": "dot q=H and the exact G-inverted scale equations after N=1 gauge fixing", "constraint": "C_H=0 on initial data and dot C_H=-Theta C_H", "invariant_submanifolds": ["round Einstein shape", "Jensen Einstein shape"], "integrator": "deterministic RK4 with Hamiltonian residual, identically zero homogeneous momentum residual, scale positivity, vacuum energy/constraint propagation, and timestep-refinement diagnostics", "prediction_status": "illustrative parent dynamics only"},
        "stability": {**common("BHSM_P1_constraint_reduced_stability_v6_0_10"), "status": "BHSM_P1_CONSTRAINT_REDUCED_SHAPE_STABILITY_DERIVED", "reduction": "lapse is nondynamical; time reparameterization and the Hamiltonian-constrained volume perturbation are removed before shape classification", "round": {"masses_squared": ["4/a^2", "4/a^2"], "result": "no homogeneous shape tachyon; 7H damps on the expanding half, is antifriction on the contracting half, and the restoring masses tend to zero asymptotically"}, "jensen": {"masses_squared": ["52/(5a4^2)", "-4/a4^2"], "result": "one homogeneous tachyonic shape direction"}, "fixed_lapse_hessian_reused_as_final": False, "connection_zero_modes": "require connection gauge fixing and are not counted as physical shape modes"},
        "sigma": {**common("BHSM_P1_sigma_background_support_audit_v6_0_10"), "status": "BHSM_SIGMA_DYNAMIC_BACKGROUND_SUPPORT_DERIVED_CONDITIONALLY", "candidate": "existing normalized (J,m)=(0,0) bulk-sigma singlet only", "stress": "rho_sigma=Z sigma_dot^2/2+U; p4=p2=p1=Z sigma_dot^2/2-U", "equation": "Z(D_t^2 sigma+Theta D_t sigma)+U'(sigma)=0", "static": "a constant stationary sigma has p=-rho and cannot supply the required positive dust-like p=0 stress unless rho=0", "massless": "for U=0 a rolling homogeneous sigma has p=rho, not the required static p=0", "rolling": "the existing polynomial potential does not give an exactly time-independent positive dust stress without a new action condition", "dynamic": "isotropic sigma stress is compatible with either Einstein fixed-shape trajectory but changes the common-scale solution according to existing primitive coefficients and initial data", "v5_value_inserted": False},
        "connection": {**common("BHSM_P1_connection_background_support_audit_v6_0_10"), "status": "BHSM_GEOMETRIC_CONNECTION_BACKGROUND_ALREADY_INCLUDED", "invariant_background": "canonical quaternionic Hopf connection/curvature", "field_equation": "the invariant instanton connection is Yang-Mills-compatible at fixed Einstein shape", "backreaction": "already included in the v6.0.9 connection-metric R7 and K_ab reduction", "additional_support": "none without double counting; A_fluctuation=0 is the retained fluctuation branch", "arbitrary_electric_or_magnetic_field_inserted": False},
        "tower": {**common("BHSM_P1_dynamic_spectral_gap_tower_control_v6_0_10"), "status": "BHSM_DYNAMIC_TOWER_CONTROL_CONDITIONS_DERIVED", "gap": "Delta(t)=min[1/(2a2^2)+1/(4a1^2),2/a2^2]", "conditions": ["E^2/Delta <<1", "max H_i^2/Delta <<1", "|D_t Delta|/Delta^(3/2)<<1", "max |D_t H_i|/Delta <<1", "||J_H||/(Delta ||Phi_ref||)<<1"], "fixed_shape": "Delta proportional to a^-2 and |dot Delta|/Delta^(3/2)=2|H|/sqrt(Delta)", "diagnostic_boolean": "the executable uses an exposed 0.1 ratio threshold for tests; the theorem statement remains the asymptotic <<1 condition", "late_time": "on the lambda>0 cosh branches Delta tends to zero while H tends to sqrt(lambda/42), so the tower EFT is eventually uncontrolled", "gap_crossing": "no finite-time gap closing for positive scales; a level crossing occurs only if the evolving ratio passes (a1/a2)^2=1/6", "through_closing_event_claimed": False},
        "connection_norm": {**common("BHSM_P1_background_connection_normalization_v6_0_10"), "status": "BHSM_BACKGROUND_CONNECTION_NORMALIZATION_DERIVED", "matrix": "K=(kappa1 Vol(F)/2)diag(a2^2,a2^2,a1^2)", "log_rates": ["D_t ln K_11=D_t ln K_22=4H2+H1", "D_t ln K_33=2H2+3H1"], "electric_friction": ["Theta_A12=4H4+4H2+H1", "Theta_A3=4H4+2H2+3H1"], "positivity": "retained for kappa1,a1,a2>0", "charge_map": "rho(T_a)/sqrt(K_aa(t))", "RG_running_interpretation": False},
        "multiplet": {**common("BHSM_P1_background_multiplet_operator_v6_0_10"), "status": "BHSM_BACKGROUND_MULTIPLET_OPERATOR_DERIVED", "equation": "D_t^2 phi+Theta D_t phi+[lambda_(J,m)(a2,a1)+E_(J,m)+M_parent^2]phi+interaction sources=0", "friction": "Theta=4H4+2H2+H1", "connection": "D_t and spatial D_A use the v6.0.9 associated connection and canonical generator map", "mixing": "time-dependent moduli change the instantaneous basis; Berry/mode mixing is absent only in the symmetry-preserving fixed-(J,m) basis", "canonical_volume_variable": "chi=V7^(1/2)phi has pump term -dot(Theta)/2-Theta^2/4", "particle_mass_interpretation": False},
        "scale": {**common("BHSM_P1_lorentzian_scale_relation_v6_0_10"), "status": "BHSM_P1_PARENT_CURVATURE_SCALE_DERIVED_PRIMITIVE_OPEN", "lambda": "kappa0/kappa1", "expansion_scale": "H_lambda^2=lambda/42", "round_minimum": "a_min^2=21/(2lambda)", "jensen_minimum": "a4_min^2=189/(10lambda)", "static_extrema": "remain non-solutions even though their radii are algebraic in lambda", "integration_constant": "t0 selects the time origin; expanding or contracting orientation selects a branch", "absolute_unit": None},
        "parent_v5": {**common("BHSM_P1_parent_to_v5_background_map_v6_0_10"), "status": "BHSM_PARENT_TO_V5_DYNAMIC_BACKGROUND_MAP_ADVANCED", "Berger_metric": "instantaneous spatial operator on the exact fixed-shape parent trajectories", "measure": "time-dependent physical measure derived", "associated_operator": "adiabatic/local only where dynamic tower conditions hold", "sigma": "conditional homogeneous parent singlet, not the v5 identification", "connection": "time-dependent geometric normalization, not a physical gauge coupling", "boundary_collar": "unresolved; I_t endpoints are variational boundaries, not the v5 physical collar", "scale_transport": "parent lambda supplies a curvature/expansion relation but no observed calibration", "frozen_v5_formulas_changed": False},
        "lovelock": {**common("BHSM_P1_P2_P3_background_escalation_ledger_v6_0_10"), "status": "BHSM_P1_BACKGROUND_CLOSES_ROUND_DYNAMIC_P2_P3_NOT_REQUIRED", "P1_limitations": ["no positive-curvature vacuum static product", "Jensen shape instability", "late-time loss of tower separation"], "P2": "Gauss-Bonnet can modify algebraic Friedmann and shape Hessian terms but introduces independent kappa2", "P3": "cubic Lovelock can further modify high-curvature branches but introduces independent kappa3", "necessity": "not necessary for the stable round fixed-shape Lorentzian P1 background; possible later correction only", "coefficient_fit_performed": False},
        "hidden": {**common("BHSM_P1_lorentzian_hidden_input_audit_v6_0_10"), "status": "BHSM_P1_LORENTZIAN_HIDDEN_INPUTS_EXPOSED", "primitive_inputs": ["kappa0", "kappa1", "existing sigma coefficients", "initial data", "time orientation"], "derived_not_input": ["Hamiltonian constraint", "round/Jensen Friedmann equations", "required static stress", "shape eigenvalues", "dynamic gap conditions"], "not_imported": ["Planck length", "Hubble data", "CMB temperature", "cosmological parameters", "measured masses", "PDG values", "gauge couplings", "CKM or PMNS data"], "support_fluid_is_diagnostic_only": True},
        "report": {**common("BHSM_P1_lorentzian_background_constraint_report_v6_0_10"), "status": PRIMARY_RESULT, "central_answer": "The lapse-preserving normalized P1 action has no positive-curvature vacuum static product, but it does admit exact round and Jensen fixed-shape Lorentzian parent trajectories for kappa0/kappa1>0. The round trajectory has no tachyonic homogeneous shape mode and its expanding half is friction-damped; Jensen carries one tachyonic shape mode. Static round and Jensen extrema require the same positive dust-like diagnostic stress, which neither a constant existing sigma nor an additional independent connection source supplies. The round dynamic branch therefore closes the P1 parent-background gate without adding matter, while tower control remains local and is lost asymptotically as the instantaneous gap tends to zero.", "derived": ["lapse-preserving ADM action", "Hamiltonian and momentum constraints", "constraint propagation", "scale/shape system", "static exclusion and required stress", "exact round/Jensen dynamic solutions", "constraint-reduced shape spectrum", "background connection/multiplet equations", "dynamic tower conditions"], "conditional": ["sigma-supported dynamic histories", "adiabatic associated-mode reduction", "parent-to-v5 local operator map"], "constructive_constraints": ["static fixed-lapse extrema are not Lorentzian vacua", "Jensen is shape-unstable", "connection background cannot be counted twice", "late-time decompactification closes the spectral gap"], "completion_gate": "V6_0_10_ROUND_FIXED_SHAPE_P1_BACKGROUND_SELECTED", "recommended_next_branch": "bhsm-round-background-gauge-scalar-sector-v6-1", "full_bhsm_status": "FULL_BHSM_NOT_COMPLETE"},
    }
    return payloads


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    built = build_artifact_payloads(root)
    paths = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(built[key]), encoding="utf-8")
        paths.append(path)
    return paths


def lorentzian_background_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def lorentzian_background_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.0.10 P1 Lorentzian Background Constraint Closure",
        "",
        f"Primary result: `{report['primary_result']}`.",
        "",
        report["central_answer"],
        "",
        f"Next gate: `{report['completion_gate']}`.",
        "",
        "`FULL_BHSM_NOT_COMPLETE`.",
    ]) + "\n"

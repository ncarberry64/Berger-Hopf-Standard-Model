"""BHSM v14.61 full-global-envelopment Euler-Lagrange and Hessian gate.

This module is the fail-closed bridge from the reduced v14.60 global-cap theorem
witness to a physical BHSM parent/child solve.  It assembles the scale-power
structure already established by the BHSM action program,

    Gamma(u,x) = exp(8x) A8(u) + exp(6x) A6(u) + exp(3x) A3(u)
                 + A0(u) + x Z(u),

with x = log(R_child/R_parent), and provides exact residual/Hessian formulas,
a gauge-reduction interface, a deterministic branch-search harness, coefficient
provenance gates, and the zero-retuning neutrino handoff contract.

The numerical model in this module is a synthetic theorem fixture.  It proves
that the full architecture is executable and that an isolated globally varied
parent/child stationary branch can be certified locally by a reduced Hessian.
It is NOT the physical BHSM background.  Physical execution fails closed until
all action coefficients and gauge-fixed parent/child operators are derived.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
import math
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

VERSION = "v14.61"

PRIMARY_VERDICT = (
    "BHSM_V14_61_THE_FULL_GLOBAL_ENVELOPMENT_EULER_LAGRANGE_SCALE_POWER_"
    "STRUCTURE_GAUGE_REDUCED_HESSIAN_INTERFACE_AND_BRANCH_EXHAUSTION_GATE_"
    "ARE_NOW_EXPLICIT_AND_EXECUTABLE_WITHOUT_SEAM_FIRST_CAP_INFERENCE_BUT_"
    "PHYSICAL_EXECUTION_REMAINS_BLOCKED_UNTIL_THE_REMAINING_UNIFIED_ACTION_"
    "COEFFICIENTS_AND_COMPLETE_GAUGE_FIXED_PARENT_CHILD_OPERATORS_ARE_DERIVED"
)

CAP_VERDICT = (
    "BHSM_V14_61_V14_60_GLOBAL_CAP_SELECTION_SURVIVES_AS_THE_CORRECT_"
    "ARCHITECTURE_THE_SEAM_IS_AN_OUTPUT_OF_GLOBAL_STATIONARITY_AND_LOCAL_"
    "HESSIAN_NONDEGENERACY_CERTIFIES_ONLY_AN_ISOLATED_BRANCH_NOT_GLOBAL_"
    "UNIQUENESS_SO_COMPETING_STATIONARY_BRANCHES_MUST_BE_EXHAUSTIVELY_SEARCHED"
)

EXACT_NEXT_OBJECT = (
    "ACTION_DERIVATION_OF_THE_NORMALIZED_M8_VOLUME_AND_TWO_DERIVATIVE_"
    "COEFFICIENTS_COLLAR_GHY_NORMALIZATION_COMPLETE_M4_GAUGE_FERMION_SCALAR_"
    "AND_CURRENT_ATTACHMENTS_AND_FULL_RELATIVE_NONLOCAL_SPECTRAL_COEFFICIENT_"
    "FOLLOWED_BY_THE_COUPLED_GAUGE_FIXED_COSMOLOGICAL_PARENT_REGULAR_CHILD_"
    "GLOBAL_BVP_BRANCH_SEARCH_AND_ZERO_RETUNING_NEUTRINO_EXECUTION"
)


@dataclass(frozen=True)
class ActionSector:
    name: str
    scale_power: int | None
    role: str
    structural_status: str
    coefficient_status: str
    coefficient_symbol: str
    physical_ready: bool
    note: str


def action_sector_ledger() -> tuple[ActionSector, ...]:
    """Return the current fail-closed global-action provenance ledger.

    The statuses intentionally distinguish a structurally identified term from
    a coefficient/operator that is sufficiently derived to run the physical
    parent/child solve.  No measured particle data are used here.
    """
    return (
        ActionSector(
            "M8_volume", 8, "global parent/child volume response",
            "STRUCTURAL_TERM_IDENTIFIED", "NORMALIZATION_OPEN", "A8",
            False, "Scale power L^8 is structural; physical normalized coefficient is not closed.",
        ),
        ActionSector(
            "M8_two_derivative_geometry_eta", 6,
            "Einstein/two-derivative geometry and eta response",
            "STRUCTURAL_TERM_IDENTIFIED", "NORMALIZATION_AND_BACKGROUND_ATTACHMENT_OPEN", "A6",
            False, "Scale power L^6 is structural; full gauge-fixed physical coefficient/background is open.",
        ),
        ActionSector(
            "collar_GHY_interface", 3, "collar/GHY and parent-child seam response",
            "STRUCTURAL_TERM_IDENTIFIED", "PHYSICAL_NORMALIZATION_OPEN", "A3",
            False, "Scale power L^3 is structural; seam must be varied globally rather than prescribed.",
        ),
        ActionSector(
            "M4_local_action", 0,
            "gauge, fermion, scalar/topographic, charged-current and neutral-response local terms",
            "ACTION_SKELETON_CONDITIONAL", "COMPLETE_NORMALIZED_ATTACHMENT_OPEN", "A0",
            False, "Canonical trace structure exists, but complete physical action attachment is not closed.",
        ),
        ActionSector(
            "relative_nonlocal_spectral", None, "relative determinant / heat-kernel / anomaly response",
            "RELATIVE_SPECTRAL_FORMULAS_PARTIAL", "FULL_PARENT_CHILD_COEFFICIENT_OPEN", "Z",
            False, "Minimal local anomaly pieces are known; the complete matched relative spectral coefficient is not.",
        ),
        ActionSector(
            "Berger_connection_curvature_endomorphism", 0,
            "Dirac curvature-endomorphism branch",
            "FOUNDATIONAL_CONNECTION_LOCK", "XI_EQUALS_ZERO", "xi",
            True, "The BHSM connection locks the extra curvature endomorphism branch to xi=0.",
        ),
        ActionSector(
            "three_transverse_shape_channels", 0,
            "noncentral moving-seam wake/flavor response",
            "OPERATOR_BASIS_AVAILABLE", "ACTION_SELECTED_AMPLITUDES_PHASES_OPEN", "q_Lr",
            False, "Three noncentral channels can be represented, but the physical orbit and amplitudes remain unselected.",
        ),
        ActionSector(
            "cosmological_parent_anchor", None,
            "topographic S3(R_H) parent",
            "EFFECTIVE_EXTERNAL_ANCHOR_BRANCH", "COUPLED_ACTION_VALUE_OPEN", "R_H",
            False, "R_H may anchor an effective branch; the coupled action does not yet derive its unique physical value.",
        ),
    )


def coefficient_readiness() -> dict[str, Any]:
    ledger = action_sector_ledger()
    missing = [s.name for s in ledger if not s.physical_ready]
    return {
        "version": VERSION,
        "all_physical_coefficients_and_operators_ready": len(missing) == 0,
        "ready_sectors": [s.name for s in ledger if s.physical_ready],
        "missing_sectors": missing,
        "ledger": [asdict(s) for s in ledger],
        "measured_particle_data_used_to_fill_missing_entries": False,
    }


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


@dataclass(frozen=True)
class QuadraticSector:
    power: int
    K: np.ndarray
    j: np.ndarray
    c: float

    def value(self, u: np.ndarray) -> float:
        return 0.5 * float(u @ self.K @ u) - float(self.j @ u) + float(self.c)

    def grad(self, u: np.ndarray) -> np.ndarray:
        return self.K @ u - self.j


@dataclass(frozen=True)
class DiagnosticGlobalAction:
    sectors: tuple[QuadraticSector, ...]
    K0: np.ndarray
    j0: np.ndarray
    c0: float
    z0: float
    z1: np.ndarray
    target_u: np.ndarray
    target_x: float

    @property
    def dimension(self) -> int:
        return int(self.target_u.size + 1)


def _spd(seed: int, n: int, floor: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    m = rng.normal(size=(n, n))
    return (m.T @ m) / float(n) + floor * np.eye(n)


def synthetic_global_action(n: int = 5) -> DiagnosticGlobalAction:
    """Return a frozen, nonphysical action fixture with a known stationary point.

    The fixture is built algebraically, not fitted to any experimental target.
    It only tests the global Euler-Lagrange/Hessian machinery.
    """
    if not isinstance(n, int) or n < 3:
        raise ValueError("n must be an integer >= 3")
    target_u = np.linspace(-0.18, 0.22, n, dtype=float)
    target_x = -0.58
    sector_specs = [(8, 11, 0.08), (6, 17, 0.11), (3, 23, 0.16)]
    sectors0: list[QuadraticSector] = []
    for power, seed, floor in sector_specs:
        K = _spd(seed, n, floor)
        j = np.zeros(n, dtype=float)
        # Large positive constant keeps the x-x Hessian contribution positive.
        c = 0.75 + 0.07 * power
        sectors0.append(QuadraticSector(power, K, j, c))
    K0 = _spd(31, n, 5.0)
    z1 = np.linspace(-0.025, 0.03, n, dtype=float)

    # Solve the source terms analytically so the target is exactly stationary.
    weighted_grad = np.zeros(n, dtype=float)
    for s in sectors0:
        weighted_grad += math.exp(s.power * target_x) * s.grad(target_u)
    j0 = K0 @ target_u + weighted_grad + target_x * z1

    # Choose c0 independently; it does not enter the field gradient.
    c0 = 0.2
    x_sum = 0.0
    for s in sectors0:
        x_sum += s.power * math.exp(s.power * target_x) * s.value(target_u)
    z0 = -float(z1 @ target_u) - x_sum

    return DiagnosticGlobalAction(tuple(sectors0), K0, j0, c0, z0, z1, target_u, target_x)


def split_state(state: Sequence[float], model: DiagnosticGlobalAction) -> tuple[np.ndarray, float]:
    v = np.asarray(state, dtype=float)
    if v.shape != (model.dimension,):
        raise ValueError("state vector has wrong dimension")
    return v[:-1], float(v[-1])


def global_action_value(state: Sequence[float], model: DiagnosticGlobalAction | None = None) -> float:
    model = model or synthetic_global_action()
    u, x = split_state(state, model)
    total = 0.5 * float(u @ model.K0 @ u) - float(model.j0 @ u) + model.c0
    for s in model.sectors:
        total += math.exp(s.power * x) * s.value(u)
    total += x * (model.z0 + float(model.z1 @ u))
    return float(total)


def global_action_gradient(state: Sequence[float], model: DiagnosticGlobalAction | None = None) -> np.ndarray:
    model = model or synthetic_global_action()
    u, x = split_state(state, model)
    gu = model.K0 @ u - model.j0 + x * model.z1
    gx = model.z0 + float(model.z1 @ u)
    for s in model.sectors:
        ep = math.exp(s.power * x)
        gu = gu + ep * s.grad(u)
        gx += s.power * ep * s.value(u)
    return np.concatenate([gu, np.array([gx])])


def global_action_hessian(state: Sequence[float], model: DiagnosticGlobalAction | None = None) -> np.ndarray:
    model = model or synthetic_global_action()
    u, x = split_state(state, model)
    n = u.size
    Huu = model.K0.copy()
    Hux = model.z1.copy()
    Hxx = 0.0
    for s in model.sectors:
        ep = math.exp(s.power * x)
        Huu += ep * s.K
        Hux += s.power * ep * s.grad(u)
        Hxx += (s.power ** 2) * ep * s.value(u)
    H = np.zeros((n + 1, n + 1), dtype=float)
    H[:-1, :-1] = Huu
    H[:-1, -1] = Hux
    H[-1, :-1] = Hux
    H[-1, -1] = Hxx
    return H


def scale_stationarity_components(state: Sequence[float], model: DiagnosticGlobalAction | None = None) -> dict[str, float]:
    model = model or synthetic_global_action()
    u, x = split_state(state, model)
    rows = {f"p{sector.power}": sector.power * math.exp(sector.power * x) * sector.value(u) for sector in model.sectors}
    rows["Z"] = model.z0 + float(model.z1 @ u)
    rows["sum"] = sum(rows.values())
    return {k: float(v) for k, v in rows.items()}


def newton_solve(initial: Sequence[float], model: DiagnosticGlobalAction | None = None, *, max_iter: int = 80, tol: float = 1e-11) -> dict[str, Any]:
    model = model or synthetic_global_action()
    z = np.asarray(initial, dtype=float).copy()
    if z.shape != (model.dimension,):
        raise ValueError("initial state has wrong dimension")
    for iteration in range(max_iter):
        g = global_action_gradient(z, model)
        gn = float(np.linalg.norm(g))
        if gn < tol:
            return {"converged": True, "iterations": iteration, "state": z, "gradient_norm": gn, "action": global_action_value(z, model)}
        H = global_action_hessian(z, model)
        try:
            step = np.linalg.solve(H, -g)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, -g, rcond=None)[0]
        # Backtracking on gradient norm; avoids pretending Newton is globally convergent.
        alpha = 1.0
        accepted = False
        for _ in range(30):
            cand = z + alpha * step
            if not np.all(np.isfinite(cand)):
                alpha *= 0.5
                continue
            try:
                cand_gn = float(np.linalg.norm(global_action_gradient(cand, model)))
            except OverflowError:
                cand_gn = math.inf
            if cand_gn < gn:
                z = cand
                accepted = True
                break
            alpha *= 0.5
        if not accepted:
            return {"converged": False, "iterations": iteration + 1, "state": z, "gradient_norm": gn, "action": global_action_value(z, model)}
    g = global_action_gradient(z, model)
    return {"converged": float(np.linalg.norm(g)) < tol, "iterations": max_iter, "state": z, "gradient_norm": float(np.linalg.norm(g)), "action": global_action_value(z, model)}


def stationary_fixture_certificate() -> dict[str, Any]:
    model = synthetic_global_action()
    target = np.concatenate([model.target_u, np.array([model.target_x])])
    g = global_action_gradient(target, model)
    H = global_action_hessian(target, model)
    eig = np.linalg.eigvalsh(H)
    scale = scale_stationarity_components(target, model)
    return {
        "version": VERSION,
        "fixture_status": "SYNTHETIC_NONPHYSICAL_THEOREM_WITNESS",
        "state": [float(v) for v in target],
        "log_nesting": float(model.target_x),
        "diagnostic_nesting_ratio": float(math.exp(model.target_x)),
        "gradient_norm": float(np.linalg.norm(g)),
        "scale_stationarity_components": scale,
        "scale_stationarity_residual": abs(scale["sum"]),
        "hessian_min_eigenvalue": float(np.min(eig)),
        "hessian_max_eigenvalue": float(np.max(eig)),
        "hessian_condition_number": float(np.linalg.cond(H)),
        "isolated_local_stationary_branch": bool(np.min(np.abs(eig)) > 1e-9),
        "positive_local_hessian_in_fixture": bool(np.min(eig) > 0.0),
        "global_uniqueness_proved": False,
        "physical_BHSM_solution": False,
    }


def _cluster_states(states: list[np.ndarray], tol: float = 1e-7) -> list[np.ndarray]:
    clusters: list[np.ndarray] = []
    for s in states:
        if not any(float(np.linalg.norm(s - c)) < tol for c in clusters):
            clusters.append(s)
    return clusters


def branch_search_payload() -> dict[str, Any]:
    model = synthetic_global_action()
    base = np.concatenate([model.target_u, np.array([model.target_x])])
    seeds: list[np.ndarray] = []
    # Frozen deterministic seed family; this is a numerical exhaustion harness, not a proof over all field space.
    for dx in (-0.7, -0.3, 0.0, 0.3, 0.65):
        for amp in (-0.18, 0.0, 0.18):
            perturb = np.linspace(-amp, amp, model.target_u.size + 1)
            seed = base + perturb
            seed[-1] = model.target_x + dx
            seeds.append(seed)
    results = [newton_solve(seed, model) for seed in seeds]
    converged_states = [r["state"] for r in results if r["converged"]]
    clusters = _cluster_states(converged_states)
    rows = []
    for c in clusters:
        H = global_action_hessian(c, model)
        rows.append({
            "state": [float(v) for v in c],
            "action": global_action_value(c, model),
            "gradient_norm": float(np.linalg.norm(global_action_gradient(c, model))),
            "hessian_min_eigenvalue": float(np.min(np.linalg.eigvalsh(H))),
        })
    return {
        "version": VERSION,
        "seed_count": len(seeds),
        "converged_seed_count": len(converged_states),
        "distinct_stationary_clusters_in_frozen_search": len(clusters),
        "clusters": rows,
        "all_converged_to_single_fixture_branch": len(clusters) == 1 and len(converged_states) == len(seeds),
        "global_branch_exhaustion_proved": False,
        "physical_branch_search_executed": False,
        "interpretation": "A nondegenerate Hessian proves local isolation only; physical completion requires a dedicated competing-branch search on the full gauge-fixed action.",
    }


def _nullspace_rows(rows: np.ndarray, dimension: int, rtol: float = 1e-12) -> np.ndarray:
    if rows.size == 0:
        return np.eye(dimension)
    A = np.asarray(rows, dtype=float)
    if A.ndim != 2 or A.shape[1] != dimension:
        raise ValueError("row constraints must have shape (m, dimension)")
    _, s, vh = np.linalg.svd(A, full_matrices=True)
    rank = int(np.sum(s > (s[0] * rtol if s.size and s[0] > 0 else rtol)))
    return vh[rank:].T.copy()


def gauge_reduced_hessian(hessian: np.ndarray, gauge_generators: np.ndarray | None = None, constraints: np.ndarray | None = None) -> dict[str, Any]:
    H = np.asarray(hessian, dtype=float)
    if H.ndim != 2 or H.shape[0] != H.shape[1]:
        raise ValueError("hessian must be square")
    n = H.shape[0]
    rows: list[np.ndarray] = []
    if gauge_generators is not None:
        G = np.asarray(gauge_generators, dtype=float)
        if G.ndim == 1: G = G.reshape(1, -1)
        rows.append(G)
    if constraints is not None:
        C = np.asarray(constraints, dtype=float)
        if C.ndim == 1: C = C.reshape(1, -1)
        rows.append(C)
    stacked = np.vstack(rows) if rows else np.zeros((0, n), dtype=float)
    Q = _nullspace_rows(stacked, n)
    Hphys = Q.T @ H @ Q
    eig = np.linalg.eigvalsh(Hphys) if Hphys.size else np.array([], dtype=float)
    return {
        "basis": Q,
        "reduced_hessian": Hphys,
        "physical_dimension": int(Q.shape[1]),
        "eigenvalues": eig,
        "min_abs_eigenvalue": float(np.min(np.abs(eig))) if eig.size else math.inf,
        "nondegenerate": bool(eig.size == 0 or np.min(np.abs(eig)) > 1e-10),
        "positive": bool(eig.size == 0 or np.min(eig) > 0.0),
    }


def gauge_reduction_fixture_payload() -> dict[str, Any]:
    # A synthetic Hessian with one deliberately flat gauge coordinate.  The physical block is positive.
    H = np.diag([0.0, 2.0, 3.5, 5.0, 7.0])
    gauge = np.array([[1.0, 0.0, 0.0, 0.0, 0.0]])
    reduced = gauge_reduced_hessian(H, gauge_generators=gauge)
    return {
        "version": VERSION,
        "raw_hessian_has_zero_mode": True,
        "gauge_generator_count": 1,
        "physical_dimension": reduced["physical_dimension"],
        "reduced_eigenvalues": [float(v) for v in reduced["eigenvalues"]],
        "gauge_reduced_hessian_nondegenerate": reduced["nondegenerate"],
        "gauge_reduced_hessian_positive": reduced["positive"],
        "physical_BHSM_gauge_ghost_operator_inserted": False,
    }


def euler_lagrange_contract_payload() -> dict[str, Any]:
    payload = {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "global_state": [
            "cosmological_parent_fields",
            "regular_child_cap_fields",
            "moving_seam_embedding_X",
            "eta_and_metric",
            "gauge_fields",
            "fermions",
            "scalar_topographic_fields",
            "x=log(R_child/R_parent)",
        ],
        "effective_scale_structure": "Gamma=exp(8x)A8+exp(6x)A6+exp(3x)A3+A0+xZ",
        "scale_equation": "0=8 exp(8x)A8+6 exp(6x)A6+3 exp(3x)A3+Z",
        "field_equation": "0=sum_p exp(px) delta A_p/delta Phi + delta A0/delta Phi + x delta Z/delta Phi",
        "seam_rule": "seam value and traction are outputs of the same global stationarity problem, not cap input data",
        "local_isolation_rule": "after gauge/constraint reduction, det(H_phys)!=0 implies only local branch isolation",
        "global_uniqueness_rule": "physical global uniqueness requires explicit exclusion/classification of competing stationary branches",
        "no_retuning": True,
        "physical_coefficients_inserted": False,
    }
    return {**payload, "payload_sha256": sha256_payload(payload)}


def precomparison_freeze_manifest() -> dict[str, Any]:
    core = {
        "version": VERSION,
        "equations": euler_lagrange_contract_payload(),
        "coefficient_readiness": coefficient_readiness(),
        "experimental_neutrino_targets_present": False,
        "measured_particle_masses_present": False,
        "measured_CKM_PMNS_values_present": False,
        "retuning_after_comparison_allowed": False,
    }
    return {**core, "freeze_sha256": sha256_payload(core)}


def physical_execution_gate() -> dict[str, Any]:
    readiness = coefficient_readiness()
    checks = {
        "global_envelopment_architecture": True,
        "scale_power_EL_structure": True,
        "seam_as_variational_output": True,
        "gauge_reduced_hessian_interface": True,
        "branch_exhaustion_requirement": True,
        "no_retuning_freeze_manifest": True,
        "all_action_coefficients_and_operators_derived": readiness["all_physical_coefficients_and_operators_ready"],
        "stationary_cosmological_parent_solved": False,
        "stationary_regular_child_cap_solved": False,
        "complete_metric_gauge_ghost_projector_inserted": False,
        "all_competing_physical_branches_classified": False,
        "three_transverse_shape_amplitudes_action_selected": False,
        "physical_relative_DtN_heat_kernel_bundle": False,
        "physical_neutrino_kill_screen_executed": False,
    }
    missing = [k for k,v in checks.items() if not v]
    return {
        "version": VERSION,
        "verdict": "PHYSICAL_EXECUTION_BLOCKED" if missing else "PHYSICAL_EXECUTION_READY",
        "checks": checks,
        "missing_checks": missing,
        "missing_action_sectors": readiness["missing_sectors"],
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "usb_touched": False,
    }


def require_physical_execution_ready() -> None:
    gate = physical_execution_gate()
    if gate["verdict"] != "PHYSICAL_EXECUTION_READY":
        raise RuntimeError("BHSM physical execution blocked: " + ", ".join(gate["missing_checks"]))


def neutrino_handoff_payload() -> dict[str, Any]:
    gate = physical_execution_gate()
    return {
        "version": VERSION,
        "fixed_inception_pair_identity": True,
        "three_wake_projection_basis_required": True,
        "matter_common_mode_impulse_and_phase_kick_contract_preserved": True,
        "inputs_required_from_global_background": [
            "action_selected_parent_operator",
            "action_selected_regular_child_operator",
            "derived_seam_DtN_map",
            "relative_heat_kernel_or_zeta_derivatives",
            "three_transverse_shape_derivatives",
            "complete_zero_mode_projector",
        ],
        "physical_inputs_available": gate["verdict"] == "PHYSICAL_EXECUTION_READY",
        "physical_neutrino_execution_performed": False,
        "no_PMNS_or_mass_splitting_emitted": True,
    }


def completion_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "cap_verdict": CAP_VERDICT,
        "v14_59_local_inverse_boundary_obstruction": "ARCHITECTURALLY_BYPASSED_BY_GLOBAL_ENVELOPMENT_VARIATION",
        "v14_60_reduced_global_selection_mechanism": "VALIDATED",
        "full_action_EL_interface": "FORMULATED",
        "physical_full_action_solution": "BLOCKED_BY_PROVENANCE_AND_OPERATOR_GATES",
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "usb_touched": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def artifact_payloads() -> Mapping[str, dict[str, Any]]:
    return {
        "BHSM_action_sector_provenance_v14_61.json": coefficient_readiness(),
        "BHSM_full_global_EL_contract_v14_61.json": euler_lagrange_contract_payload(),
        "BHSM_stationary_fixture_certificate_v14_61.json": stationary_fixture_certificate(),
        "BHSM_global_branch_search_v14_61.json": branch_search_payload(),
        "BHSM_gauge_reduction_fixture_v14_61.json": gauge_reduction_fixture_payload(),
        "BHSM_precomparison_freeze_manifest_v14_61.json": precomparison_freeze_manifest(),
        "BHSM_neutrino_global_background_handoff_v14_61.json": neutrino_handoff_payload(),
        "BHSM_completion_gate_v14_61.json": completion_gate_payload(),
    }


def materialize(directory: str | Any) -> list[Any]:
    from pathlib import Path
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, payload in sorted(artifact_payloads().items()):
        path = root / name
        path.write_bytes(canonical_json_bytes(payload) + b"\n")
        paths.append(path)
    return paths

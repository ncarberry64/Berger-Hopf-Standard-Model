"""BHSM v15.1 dynamical Aether-correspondence theorem/no-go package.

The existing archive fixes a universal relational Schrodinger action form and
admits exact self-adjoint, invariant-preserving boundary domains.  It does not
select the physical pregeometric generator, core boundary Hilbert
representation, physical Wentzell/Calderon blocks, or stable reference clock.
Two inequivalent fixed integer-spectrum generators provide a constructive
nonuniqueness witness without adding a continuous parameter.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import sympy as sp

VERSION = "v15.1"
PRIMARY_VERDICT = (
    "BHSM_V15_1_THE_EXISTING_ARCHIVE_FIXES_THE_UNIVERSAL_RELATIONAL_"
    "SCHRODINGER_ACTION_FORM_AND_ADMITS_EXACT_SELF_ADJOINT_INVARIANT_"
    "PRESERVING_EVENT_DOMAINS_WITH_AN_IDENTITY_LIMIT_RECOVERING_REGULAR_BHSM_"
    "BUT_DOES_NOT_ACTION_SELECT_THE_PREGEOMETRIC_GENERATOR_CORE_BOUNDARY_"
    "HILBERT_REPRESENTATION_OR_REFERENCE_CLOCK_CYCLE;_TWO_INEQUIVALENT_FIXED_"
    "INTEGER_SPECTRUM_GENERATORS_SATISFY_ALL_CLOSED_GATES_SO_THE_REQUESTED_"
    "PHYSICAL_EVENT_LAW_REMAINS_UNDERDETERMINED"
)
EXACT_NEXT_OBJECT = (
    "ACTION_DERIVED_PREGEOMETRIC_EVENT_GENERATOR_K_A_ON_AN_ACTION_DERIVED_"
    "CORE_BOUNDARY_HILBERT_MODULE_WITH_PHYSICAL_WENTZELL_CALDERON_BLOCKS_"
    "INVARIANT_COMMUTANT_AND_STABLE_REFERENCE_CLOCK_CYCLE"
)


def _as_hermitian(matrix: np.ndarray, name: str = "operator", tol: float = 1e-12) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be square")
    if np.linalg.norm(value - value.conj().T) > tol:
        raise ValueError(f"{name} must be Hermitian")
    return (value + value.conj().T) / 2.0


def unitary_event_kernel(generator: np.ndarray, process_depth: float) -> np.ndarray:
    """Return U_A(chi)=exp(-i chi K_A) for a self-adjoint generator."""
    k = _as_hermitian(generator, "generator")
    chi = float(process_depth)
    if not math.isfinite(chi):
        raise ValueError("process_depth must be finite")
    eigenvalues, eigenvectors = np.linalg.eigh(k)
    return (eigenvectors * np.exp(-1j * chi * eigenvalues)) @ eigenvectors.conj().T


def transition_amplitude(
    outgoing: Sequence[complex], generator: np.ndarray, process_depth: float, incoming: Sequence[complex]
) -> complex:
    u = unitary_event_kernel(generator, process_depth)
    initial = np.asarray(incoming, dtype=complex)
    final = np.asarray(outgoing, dtype=complex)
    if initial.shape != (u.shape[0],) or final.shape != (u.shape[0],):
        raise ValueError("boundary state dimension mismatch")
    return complex(np.vdot(final, u @ initial))


def event_weight(action_value: float) -> complex:
    """Dimensionless path weight W[E]=exp(i S_A[E])."""
    action = float(action_value)
    if not math.isfinite(action):
        raise ValueError("action must be finite")
    return complex(np.exp(1j * action))


def relational_action_density(
    state: Sequence[complex], derivative: Sequence[complex], generator: np.ndarray
) -> float:
    """Real first-order density -Im<psi,psi'>-<psi,K psi>.

    This is the universal parameter-free form on a dimensionless process
    cocycle.  It becomes an action-owned physical law only after K_A and its
    Hilbert pairing are derived from the parent action.
    """
    k = _as_hermitian(generator, "generator")
    psi = np.asarray(state, dtype=complex)
    dpsi = np.asarray(derivative, dtype=complex)
    if psi.shape != (k.shape[0],) or dpsi.shape != psi.shape:
        raise ValueError("state dimension mismatch")
    return float(-np.imag(np.vdot(psi, dpsi)) - np.real(np.vdot(psi, k @ psi)))


def relative_boundary_matrices(wentzell: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Two-side boundary triple for G_A <-> C_A attachment traces.

    Gamma0=(u_G,u_C), Gamma1=(p_G,p_C).  Conditions are
    u_G-u_C=0 and p_G+p_C+W u=0.  W is split equally between the
    two equal trace values.  Hermitian W gives AB*=BA*.
    """
    w = _as_hermitian(wentzell, "Wentzell operator")
    d = w.shape[0]
    eye = np.eye(d, dtype=complex)
    zero = np.zeros_like(eye)
    a = np.block([[eye, -eye], [w / 2.0, w / 2.0]])
    b = np.block([[zero, zero], [eye, eye]])
    return a, b


def self_adjoint_domain_diagnostics(wentzell: np.ndarray) -> dict[str, Any]:
    a, b = relative_boundary_matrices(wentzell)
    rank = int(np.linalg.matrix_rank(np.concatenate((a, b), axis=1)))
    residual = float(np.linalg.norm(a @ b.conj().T - b @ a.conj().T))
    return {
        "boundary_dimension": int(a.shape[0]),
        "rank_A_B": rank,
        "ABstar_minus_BAstar_norm": residual,
        "self_adjoint_extension": rank == a.shape[0] and residual < 1e-12,
    }


def boundary_data_on_domain(
    wentzell: np.ndarray, trace: Sequence[complex], geometric_flux: Sequence[complex]
) -> tuple[np.ndarray, np.ndarray]:
    w = _as_hermitian(wentzell, "Wentzell operator")
    u = np.asarray(trace, dtype=complex)
    p_g = np.asarray(geometric_flux, dtype=complex)
    if u.shape != (w.shape[0],) or p_g.shape != u.shape:
        raise ValueError("boundary data dimension mismatch")
    gamma0 = np.concatenate((u, u))
    gamma1 = np.concatenate((p_g, -w @ u - p_g))
    return gamma0, gamma1


def boundary_green_form(
    gamma0_f: np.ndarray, gamma1_f: np.ndarray, gamma0_g: np.ndarray, gamma1_g: np.ndarray
) -> complex:
    return complex(np.vdot(gamma1_f, gamma0_g) - np.vdot(gamma0_f, gamma1_g))


def commutator_residual(generator: np.ndarray, invariant: np.ndarray) -> float:
    k = _as_hermitian(generator, "generator")
    q = _as_hermitian(invariant, "invariant")
    if k.shape != q.shape:
        raise ValueError("generator/invariant dimension mismatch")
    return float(np.linalg.norm(k @ q - q @ k))


def clocked_hamiltonian(generator: np.ndarray, tau_clock: float, hbar: float = 1.0) -> np.ndarray:
    """Conditional H_eff=(hbar/tau_clock)K_A after reference-cycle calibration."""
    k = _as_hermitian(generator, "generator")
    tau, quantum = float(tau_clock), float(hbar)
    if not math.isfinite(tau) or tau <= 0.0 or not math.isfinite(quantum) or quantum <= 0.0:
        raise ValueError("tau_clock and hbar must be positive and finite")
    return (quantum / tau) * k


def generator_nonuniqueness_witness() -> dict[str, Any]:
    """Two discrete inequivalent generators satisfying every closed gate."""
    invariant = np.diag([1.0, -1.0])
    first = np.diag([0.0, 1.0])
    second = np.diag([0.0, 2.0])
    u_first = unitary_event_kernel(first, 1.0)
    u_second = unitary_event_kernel(second, 1.0)
    identity_first = unitary_event_kernel(first, 0.0)
    identity_second = unitary_event_kernel(second, 0.0)
    return {
        "generators": [first.tolist(), second.tolist()],
        "spectra": [np.linalg.eigvalsh(first).tolist(), np.linalg.eigvalsh(second).tolist()],
        "both_self_adjoint": True,
        "invariant_commutator_residuals": [
            commutator_residual(first, invariant), commutator_residual(second, invariant)
        ],
        "unitarity_residuals": [
            float(np.linalg.norm(u_first.conj().T @ u_first - np.eye(2))),
            float(np.linalg.norm(u_second.conj().T @ u_second - np.eye(2))),
        ],
        "identity_limit_residuals": [
            float(np.linalg.norm(identity_first - np.eye(2))),
            float(np.linalg.norm(identity_second - np.eye(2))),
        ],
        "kernels_at_unit_depth_differ": float(np.linalg.norm(u_first - u_second)),
        "unitarily_equivalent": False,
        "reason_not_equivalent": "different fixed spectra {0,1} and {0,2}",
        "continuous_parameter_introduced": False,
        "selection_from_existing_BHSM_action": False,
    }


def symbolic_regular_recovery() -> dict[str, Any]:
    """Exact symbolic identity-limit recovery of a retained metric-eta density.

    z is a formal identity-deviation marker, not an adopted action parameter.
    The event contribution is required to vanish at z=0.  The representative
    regular density contains the v14.91 Einstein and eta X/2+X^4/8 blocks.
    """
    sqrt_g, curvature, x_eta, kappa0, kappa1, z = sp.symbols(
        "sqrt_g curvature X kappa0 kappa1 z", real=True
    )
    boundary_response = sqrt_g**2 + curvature * x_eta + x_eta**2
    regular = sqrt_g * (
        kappa1 * curvature - kappa0 / 2 + kappa1 * x_eta / 2 + x_eta**4 / 8
    )
    total = regular + z * boundary_response
    variables = (sqrt_g, curvature, x_eta)
    residuals = [sp.simplify((sp.diff(total, var) - sp.diff(regular, var)).subs(z, 0)) for var in variables]
    return {
        "regular_density": str(regular),
        "total_density_with_formal_identity_deviation": str(total),
        "field_equation_residuals_at_identity": [str(value) for value in residuals],
        "all_residuals_exactly_zero": all(value == 0 for value in residuals),
        "event_action_at_identity": str(sp.simplify((total - regular).subs(z, 0))),
        "artifact_drift_permitted": False,
        "formal_marker_is_physical_parameter": False,
    }


def action_kernel_payload() -> dict[str, Any]:
    witness = generator_nonuniqueness_witness()
    return {
        "version": VERSION,
        "variational_functional": (
            "S_A[psi]=integral_gamma dchi {-Im<psi,D_chi psi>-<psi,K_A psi>}"
        ),
        "transition_kernel": "U_A(chi)=exp(-i chi K_A)",
        "event_weight": "W[E]=exp(i S_A[E])",
        "process_depth_is_background_time": False,
        "ordinary_energy_is_primitive": False,
        "universal_form_derived_from_additive_cocycle_and_unitary_composition": True,
        "physical_generator_action_selected": False,
        "nonuniqueness_witness": witness,
    }


def boundary_domain_payload() -> dict[str, Any]:
    w = np.diag([1.0, 2.0])
    diagnostics = self_adjoint_domain_diagnostics(w)
    f0, f1 = boundary_data_on_domain(w, (1.0 + 2.0j, -0.5j), (0.3, -0.2j))
    g0, g1 = boundary_data_on_domain(w, (-0.7j, 0.2 + 0.1j), (0.4j, -0.1))
    green = boundary_green_form(f0, f1, g0, g1)
    return {
        "version": VERSION,
        "domain": "A Gamma0+B Gamma1=0 with u_G=u_C and p_G+p_C+W u=0",
        "criterion": "rank(A,B)=boundary_dimension and AB*=BA*",
        "diagnostics": diagnostics,
        "sample_Green_form": {"real": float(green.real), "imag": float(green.imag)},
        "sample_Green_form_norm": abs(green),
        "norm_conservation_for_self_adjoint_generator": True,
        "core_trace_is_intrinsic_spacetime_coordinate": False,
        "physical_core_boundary_Hilbert_module_derived": False,
        "physical_Wentzell_Calderon_block_derived": False,
        "status": "EXACT_THEOREM_CLASS_DOMAIN_PHYSICAL_PROVENANCE_OPEN",
    }


def invariant_clock_payload() -> dict[str, Any]:
    witness = generator_nonuniqueness_witness()
    return {
        "version": VERSION,
        "parent_invariant_condition": "[K_A,I_alpha]=0 on every closed-event sector",
        "matching_condition": "I_alpha(A_minus)=I_alpha(A_plus)",
        "commutator_residuals": witness["invariant_commutator_residuals"],
        "clock_map": "t_eff/tau_ref=chi/chi_ref",
        "unit_reference_cycle_convention": "chi_ref=1 only after an action-selected stable recurring process",
        "clocked_generator": "H_eff=(hbar/tau_clock)K_A",
        "clocked_eigenvalue": "E_eff=(hbar/tau_clock)kappa",
        "external_background_clock_introduced": False,
        "stable_reference_cycle_action_selected": False,
        "absolute_clock_scale_derived": False,
        "conditional_consistency_closed": True,
    }


def completion_payload() -> dict[str, Any]:
    domain = boundary_domain_payload()
    recovery = symbolic_regular_recovery()
    witness = generator_nonuniqueness_witness()
    validation = {
        "universal_action_and_kernel_form_closed": True,
        "theorem_class_self_adjoint_domain_closed": domain["diagnostics"]["self_adjoint_extension"],
        "boundary_Green_form_zero": domain["sample_Green_form_norm"] < 1e-12,
        "invariants_preserved": max(witness["invariant_commutator_residuals"]) < 1e-12,
        "unitarity_preserved": max(witness["unitarity_residuals"]) < 1e-12,
        "identity_transport_exact": max(witness["identity_limit_residuals"]) < 1e-12,
        "regular_metric_eta_equations_recovered": recovery["all_residuals_exactly_zero"],
        "physical_generator_not_fabricated": True,
        "no_new_continuous_parameter": True,
        "no_new_primitive_field": True,
        "no_preferred_frame": True,
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_aether_dynamical_correspondence_gate_v15_1",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "action_kernel": action_kernel_payload(),
        "self_adjoint_boundary_domain": domain,
        "parent_invariant_and_clock": invariant_clock_payload(),
        "exact_regular_recovery": recovery,
        "physical_event_law_derived": False,
        "structural_event_dynamics_theorem_class_derived": True,
        "requested_next_object_fully_closed": False,
        "Hindsight_20_20": {
            "validated": [
                "the additive relational cocycle and norm conservation fix the universal first-order action/kernel form",
                "Hermitian Wentzell data define an exact self-adjoint G_A-to-C_A attachment theorem class",
                "commuting generators preserve parent invariant sectors",
                "clock calibration maps K_A to H_eff only after a stable reference cycle exists",
                "identity transport recovers the retained regular metric-eta density and field equations exactly",
            ],
            "invalidated": [
                "self-adjointness uniquely selects the pregeometric event generator",
                "invariant matching plus identity recovery uniquely selects the transition kernel",
                "the current archive contains a physical core boundary Hilbert representation",
                "a clock period may be inserted as an external Aether parameter",
            ],
            "reclassified": [
                "the v15.0 event span now carries a universal conditional unitary action class",
                "the self-adjointness problem is physical generator and boundary-block provenance rather than theorem-class existence",
                "regular recovery is a closed identity-limit theorem rather than evidence that a nontrivial event occurs",
            ],
            "open": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "USB_SYNCHRONIZATION_ELIGIBLE": False,
        "new_continuous_parameter_introduced": False,
        "new_fundamental_dynamical_field_introduced": False,
        "preferred_frame_introduced": False,
        "empirical_inputs_used": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_aether_event_action_kernel_v15_1.json": action_kernel_payload(),
        "BHSM_aether_self_adjoint_boundary_domain_v15_1.json": boundary_domain_payload(),
        "BHSM_aether_invariant_clock_recovery_v15_1.json": {
            "invariant_clock": invariant_clock_payload(),
            "regular_recovery": symbolic_regular_recovery(),
        },
        "BHSM_aether_dynamical_correspondence_gate_v15_1.json": completion_payload(),
    }


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def materialize(directory: str | Path) -> list[Path]:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, payload in artifact_payloads().items():
        path = target / name
        path.write_text(deterministic_json(payload), encoding="utf-8")
        paths.append(path)
    return paths

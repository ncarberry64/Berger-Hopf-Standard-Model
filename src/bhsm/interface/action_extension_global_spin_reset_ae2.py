"""BHSM-AE-2.0.0 global-spin reset action/domain extension.

The owner-selected extension upgrades the returned event/child SM-bundle
isomorphism class to an actual orientation- and FR-compatible reset lift.  It
does not place fields in the pregeometric core.  The terminal regular event
trace and the first regular child trace instead become restrictions of one
bundle glued by ``U_R``.  There is no independent fermion surface density.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np


ACTION_VERSION = "BHSM-AE-2.0.0"
DECISION_TYPE = "OWNER_AUTHORIZED_THEORY_VERSION_DECISION"
FULL_BHSM_COMPLETE = False


def _vector(value: Sequence[complex], name: str) -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if result.ndim != 1 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite vector")
    return result


def _square(value: Sequence[Sequence[complex]], name: str) -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if result.ndim != 2 or result.shape[0] != result.shape[1]:
        raise ValueError(f"{name} must be square")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite")
    return result


def validate_unitary(
    reset_lift: Sequence[Sequence[complex]], *, tolerance: float = 1.0e-12
) -> np.ndarray:
    """Return a finite unitary reset lift or raise ``ValueError``."""

    lift = _square(reset_lift, "reset_lift")
    residual = np.linalg.norm(np.conjugate(lift.T) @ lift - np.eye(lift.shape[0]))
    if residual > tolerance:
        raise ValueError("reset_lift must be unitary")
    return lift


def transmit_trace(
    event_trace: Sequence[complex], reset_lift: Sequence[Sequence[complex]]
) -> np.ndarray:
    """Apply the reset-owned spin/gauge lift to an event trace."""

    trace = _vector(event_trace, "event_trace")
    lift = validate_unitary(reset_lift)
    if lift.shape[0] != trace.size:
        raise ValueError("reset lift and event trace dimensions must match")
    return lift @ trace


def opposite_normal_green_residual(
    psi_event: Sequence[complex],
    phi_event: Sequence[complex],
    normal_green_form: Sequence[Sequence[complex]],
    reset_lift: Sequence[Sequence[complex]],
) -> float:
    """Return the two-sided Green-form cancellation residual.

    If ``J_e`` is the event outward-normal form, the child form in its own
    frame is ``J_c=-U_R J_e U_R^dagger``.  Traces and admissible variations
    obey the same reset lift, so the internal-seam contribution vanishes.
    """

    psi = _vector(psi_event, "psi_event")
    phi = _vector(phi_event, "phi_event")
    form = _square(normal_green_form, "normal_green_form")
    lift = validate_unitary(reset_lift)
    if psi.shape != phi.shape or form.shape != lift.shape or psi.size != lift.shape[0]:
        raise ValueError("all Green-form dimensions must match")
    child_form = -lift @ form @ np.conjugate(lift.T)
    event_value = np.vdot(psi, form @ phi)
    child_value = np.vdot(lift @ psi, child_form @ (lift @ phi))
    return float(abs(event_value + child_value))


def transmission_graph_certificate(
    normal_green_form: Sequence[Sequence[complex]],
    reset_lift: Sequence[Sequence[complex]],
) -> dict[str, float | int | bool]:
    """Certify that the reset graph is maximal isotropic.

    The graph matrix is ``G=(I,U_R)^T`` in the direct-sum trace space.  Its
    rank is half the ambient dimension and ``G^dagger J_total G=0``.
    """

    form = _square(normal_green_form, "normal_green_form")
    lift = validate_unitary(reset_lift)
    if form.shape != lift.shape:
        raise ValueError("normal form and reset lift dimensions must match")
    size = lift.shape[0]
    graph = np.vstack((np.eye(size), lift))
    child_form = -lift @ form @ np.conjugate(lift.T)
    total_form = np.block(
        [[form, np.zeros_like(form)], [np.zeros_like(form), child_form]]
    )
    isotropy = np.conjugate(graph.T) @ total_form @ graph
    rank = int(np.linalg.matrix_rank(graph))
    residual = float(np.linalg.norm(isotropy))
    return {
        "trace_dimension_per_side": size,
        "ambient_trace_dimension": 2 * size,
        "graph_rank": rank,
        "half_dimensional": rank == size,
        "isotropy_residual": residual,
        "maximal_isotropic": rank == size and residual < 1.0e-12,
    }


def brst_transmission_residual(
    event_trace: Sequence[complex],
    reset_lift: Sequence[Sequence[complex]],
    event_ghost_generator: Sequence[Sequence[complex]],
) -> float:
    """Check covariance of the reset graph under matched BRST generators."""

    trace = _vector(event_trace, "event_trace")
    lift = validate_unitary(reset_lift)
    ghost_event = _square(event_ghost_generator, "event_ghost_generator")
    if lift.shape != ghost_event.shape or trace.size != lift.shape[0]:
        raise ValueError("BRST transmission dimensions must match")
    ghost_child = lift @ ghost_event @ np.conjugate(lift.T)
    child_trace = lift @ trace
    varied_constraint = ghost_child @ child_trace - lift @ (ghost_event @ trace)
    return float(np.linalg.norm(varied_constraint))


def independent_phase_twist_distance(
    reset_lift: Sequence[Sequence[complex]], phase: float
) -> float:
    """Distance from the fixed reset graph after an extra relative phase.

    This is not used to select a phase.  It records that a nontrivial relative
    Cayley twist changes the fixed reset transition, whereas a common gauge
    frame change conjugates all bundle data together.
    """

    lift = validate_unitary(reset_lift)
    angle = float(phase)
    if not math.isfinite(angle):
        raise ValueError("phase must be finite")
    return float(np.linalg.norm(np.exp(1j * angle) * lift - lift))


def action_definition() -> dict[str, Any]:
    """Return the exact coefficient-free AE2 action/domain definition."""

    return {
        "action_version": ACTION_VERSION,
        "decision_type": DECISION_TYPE,
        "configuration_space": (
            "SECTIONS_OF_E_event_GLUED_TO_E_child_BY_THE_RESET_OWNED_"
            "Spin_TIMES_G_SM_LIFT_U_R_ON_THE_LAST_AND_FIRST_REGULAR_TRACES"
        ),
        "pregeometric_core_field_content": "NO_CONTINUOUS_SPINOR_TRACE_OR_FLUX",
        "reset_lift": (
            "U_R=rho(SpinLift(Lambda_R))_tensor_G_R_WITH_G_R_THE_RETURNED_"
            "GAUGE_BUNDLE_ISOMORPHISM"
        ),
        "bulk_action": (
            "S_F_AE2=(1/2)*integral_(M_event_union_R_M_child)[barPsi*iD*Psi-"
            "overline(iD*Psi)*Psi]dmu_WITH_THE_RETAINED_CANONICAL_NORMALIZATION"
        ),
        "independent_normal_matter_boundary_action": "S_Sigma_F_AE2=0",
        "why_zero_is_owned": (
            "THE_RESET_LOCUS_IS_AN_INTERNAL_GLUE_OF_ONE_GLOBAL_FIELD_DOMAIN_"
            "AND_HAS_NO_DELTA_SUPPORTED_MATTER_DENSITY"
        ),
        "trace_graph": "Gamma0_child(Psi)=U_R*Gamma0_event(Psi)",
        "variation_graph": "Gamma0_child(deltaPsi)=U_R*Gamma0_event(deltaPsi)",
        "squared_operator_flux_graph": (
            "Gamma1_child(Psi)=-U_R*Gamma1_event(Psi)_ON_Dom(D_AE2^2)"
        ),
        "squared_operator_domain": (
            "Dom(D_AE2^2)={Psi_in_Dom(D_AE2):D_AE2*Psi_in_Dom(D_AE2)}"
        ),
        "common_reset_frame": "U_R=I_UP_TO_GLOBAL_SPIN_SIGN_AND_GAUGE_FRAME",
        "independent_Cayley_phase": None,
        "new_continuous_coefficient": None,
        "new_physical_scale": None,
        "new_propagating_field": None,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
    }


__all__ = [
    "ACTION_VERSION",
    "DECISION_TYPE",
    "FULL_BHSM_COMPLETE",
    "validate_unitary",
    "transmit_trace",
    "opposite_normal_green_residual",
    "transmission_graph_certificate",
    "brst_transmission_residual",
    "independent_phase_twist_distance",
    "action_definition",
]

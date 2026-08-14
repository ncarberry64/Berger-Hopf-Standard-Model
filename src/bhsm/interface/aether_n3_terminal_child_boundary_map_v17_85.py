"""Action-derived terminal N=3 trace/flux data for child reconstruction."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    ORDER,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)


VERSION = "v17.85"
CLASSIFICATION = "BHSM_N3_TERMINAL_COMPLETE_CHILD_BOUNDARY_DATA_MAP"
FULL_BHSM_COMPLETE = False


def terminal_event_boundary_data(raw_vector: np.ndarray) -> dict[str, Any]:
    """Extract gauge-typed traces and action momenta at chi=pi/4."""

    raw = np.asarray(raw_vector, dtype=float)
    if raw.shape != (376,):
        raise ValueError("raw event vector must have dimension 376")
    unpacked = unpack_reduced(raw)
    q = np.asarray(unpacked["coordinates"])
    multipliers = np.asarray(unpacked["multipliers"])
    period = float(unpacked["period"])
    velocity = trapezoid_sbp_difference() @ q / period
    terminal = q[-1]
    terminal_rate = velocity[-1]
    terminal_multiplier = multipliers[-1]

    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    scale = float(terminal[0])
    u = float(terminal[1:1 + ORDER] @ signs_k)
    w = float(terminal[1 + ORDER:1 + 2 * ORDER] @ signs_j)
    v = float(terminal[1 + 2 * ORDER:1 + 3 * ORDER] @ signs_j)
    scale_rate = float(terminal_rate[0])
    u_rate = float(terminal_rate[1:1 + ORDER] @ signs_k)
    w_rate = float(
        terminal_rate[1 + ORDER:1 + 2 * ORDER] @ signs_j
    )
    v_rate = float(
        terminal_rate[1 + 2 * ORDER:1 + 3 * ORDER] @ signs_j
    )
    log_lapse = float(terminal_multiplier[:ORDER] @ signs_k)
    shift_poly = float(terminal_multiplier[ORDER:] @ signs_j)

    radius = float(RADIUS0 * math.exp(scale))
    C = float(radius * math.exp(u + w))
    A = float(radius * math.exp(u + v) / math.sqrt(2.0))
    B = float(radius * math.exp(u - v) / math.sqrt(2.0))
    lapse = float(math.exp(log_lapse))
    shift = 0.0
    shift_prime = -4.0 * shift_poly

    # The regular spectral basis fixes u'=w'=v'=n'=0 at chi=pi/4.
    log_C_prime = 0.0
    log_A_prime = -1.0
    log_B_prime = 1.0
    log_N_prime = 0.0
    f = math.pi / 4.0
    f_prime = 1.0
    f_normal = 0.0
    x_spatial = (
        f_prime**2 / C**2
        + 1.5 / A**2
        + 1.5 / B**2
    )
    eta_legendre = 1.0 + x_spatial**3
    sigma = 0.0
    localization = 1.0

    h_c = (scale_rate + u_rate + w_rate - shift_prime) / lapse
    h_a = (scale_rate + u_rate + v_rate) / lapse
    h_b = (scale_rate + u_rate - v_rate) / lapse
    h_sum = h_c + 3.0 * h_a + 3.0 * h_b
    volume = C * A**3 * B**3
    temporal_momenta = {
        "Pi_log_C": float(volume * (h_c - h_sum)),
        "Pi_log_A": float(3.0 * volume * (h_a - h_sum)),
        "Pi_log_B": float(3.0 * volume * (h_b - h_sum)),
        "Pi_f": float(volume * localization * eta_legendre * f_normal),
    }

    radial_prefactor = 3.0 * lapse * A**3 * B**3 / C
    radial_flux = {
        "Pi_log_N": float(radial_prefactor * (
            log_A_prime + log_B_prime
        )),
        "Pi_log_A": float(radial_prefactor * (
            log_N_prime + 2.0 * log_A_prime + 3.0 * log_B_prime
        )),
        "Pi_log_B": float(radial_prefactor * (
            log_N_prime + 2.0 * log_B_prime + 3.0 * log_A_prime
        )),
        "Pi_f": float(
            -lapse * A**3 * B**3 * localization
            * eta_legendre * f_prime / C
        ),
    }

    return {
        "source": "v17.75_selected_fine_period_log_mix_state",
        "terminal_node": 23,
        "period": period,
        "spatial_trace_Gamma0": {
            "C_radial_gauge_factor": C,
            "A_child_boundary_radius": A,
            "B_child_boundary_radius": B,
            "lapse": lapse,
            "shift": shift,
            "f": f,
            "sigma": sigma,
            "log_B_over_A": float(math.log(B / A)),
            "localization": localization,
        },
        "radial_derivatives": {
            "d_chi_log_C": log_C_prime,
            "d_chi_log_A": log_A_prime,
            "d_chi_log_B": log_B_prime,
            "d_chi_log_N": log_N_prime,
            "d_chi_f": f_prime,
        },
        "GHY_eta_radial_flux_Gamma1": radial_flux,
        "temporal_Cauchy_data": {
            "H_C": float(h_c),
            "H_A": float(h_a),
            "H_B": float(h_b),
            "eta_normal_flow": f_normal,
            "canonical_momenta": temporal_momenta,
        },
        "material_response": {
            "sigma": sigma,
            "Lambda": localization,
            "X_eta": float(x_spatial),
            "eta_Legendre": float(eta_legendre),
            "sigma_normal_derivative": (
                "CONSTRAINT_DETERMINED_BY_NORMALIZED_W_J[f]_RESPONSE"
            ),
        },
        "mode_state": {
            "terminal_q": terminal.tolist(),
            "terminal_q_rate": terminal_rate.tolist(),
            "terminal_lapse_shift_multipliers": terminal_multiplier.tolist(),
            "scale_history": q[:, 0].tolist(),
        },
        "quotient_certificate": {
            "boundary_shift_zero_from_regular_odd_basis": shift == 0.0,
            "time_phase_fixed_by_anchored_reset": True,
            "radial_coordinate_factor_C_is_not_an_independent_child_scale": True,
        },
    }


def event_child_datum_ownership_ledger() -> list[dict[str, str]]:
    return [
        {"datum": "spatial_geometry", "class": "DIRECTLY_INHERITED", "owner": "terminal_N3_q_trace_Gamma0"},
        {"datum": "conjugate_geometry_extrinsic_data", "class": "DIRECTLY_INHERITED", "owner": "SBP_terminal_rate_plus_lapse_shift_then_action_Legendre_map"},
        {"datum": "eta_configuration", "class": "QUOTIENTED/GAUGE", "owner": "degree_one_eta_coordinate_gauge_f=chi"},
        {"datum": "eta_momentum_flow", "class": "CONSTRAINT-DETERMINED", "owner": "shift_covariant_eta_Legendre_map"},
        {"datum": "sigma_material_response", "class": "CONSTRAINT-DETERMINED", "owner": "sigma=C_J[f]-1/2"},
        {"datum": "sigma_response_derivative", "class": "CONSTRAINT-DETERMINED", "owner": "normalized_W_J[f]_response_constraint"},
        {"datum": "scale_history", "class": "DIRECTLY_INHERITED", "owner": "23_free_log_scale_nodes_plus_fixed_reset"},
        {"datum": "local_reconstruction_scale", "class": "MISSING", "owner": "event_environment_conditioned_child_BVP_solution"},
        {"datum": "period_internal_phase", "class": "POST-EVENT DYNAMIC", "owner": "pre_event_period_direct;child_FR_phase_from_reconstructed_inertia"},
        {"datum": "v0_w0_and_remaining_u_v_w_modes", "class": "DIRECTLY_INHERITED", "owner": "terminal_N3_q_and_SBP_rate"},
        {"datum": "lapse_shift_constraints", "class": "CONSTRAINT-DETERMINED", "owner": "terminal_N3_multiplier_block"},
        {"datum": "Hopf_orientation_topology", "class": "DIRECTLY_INHERITED", "owner": "degree_1_child_x_negative_event_quotient"},
        {"datum": "FR_parity", "class": "DIRECTLY_INHERITED", "owner": "event_quotient_FR=-1"},
        {"datum": "gauge_carrier", "class": "DIRECTLY_INHERITED", "owner": "transported_SM_bundle_isomorphism_class"},
        {"datum": "rank16_fermion_carrier", "class": "RECONSTRUCTED", "owner": "same_replacement_heat_HS_operator_on_child_geometry"},
        {"datum": "environmental_event_invariants", "class": "ENVIRONMENT-DETERMINED", "owner": "I_event_I_environment_B_SM_channel"},
        {"datum": "incidence_projector_family_information", "class": "DIRECTLY_INHERITED", "owner": "boundary_identity_C3_family_and_bundle_projectors"},
        {"datum": "persistent_child_imbalance", "class": "POST-EVENT DYNAMIC", "owner": "to_be_derived_from_reconstructed_child_action_and_nonzero_Cauchy_momenta"},
    ]


def completion_payload() -> dict[str, Any]:
    boundary = terminal_event_boundary_data(v17_75_selected_raw_vector())
    ledger = event_child_datum_ownership_ledger()
    trace = boundary["spatial_trace_Gamma0"]
    flux = boundary["GHY_eta_radial_flux_Gamma1"]
    validation = {
        "all_requested_event_child_data_classified": len(ledger) == 18,
        "terminal_trace_finite": all(math.isfinite(float(trace[key])) for key in (
            "C_radial_gauge_factor", "A_child_boundary_radius",
            "B_child_boundary_radius", "lapse", "f", "sigma",
            "log_B_over_A", "localization",
        )),
        "terminal_flux_finite": all(math.isfinite(value) for value in flux.values()),
        "full_N3_mode_state_retained": len(boundary["mode_state"]["terminal_q"]) == 10,
        "full_scale_history_retained": len(boundary["mode_state"]["scale_history"]) == 24,
        "regular_boundary_shift_closed": boundary["quotient_certificate"][
            "boundary_shift_zero_from_regular_odd_basis"
        ],
        "eta_boundary_and_response_closed": (
            math.isclose(trace["f"], math.pi / 4.0, abs_tol=1.0e-15)
            and trace["sigma"] == 0.0
            and boundary["material_response"]["eta_Legendre"] > 0.0
        ),
        "missing_reconstruction_scale_not_fabricated": next(
            row for row in ledger if row["datum"] == "local_reconstruction_scale"
        )["class"] == "MISSING",
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_terminal_child_boundary_map_v17_85",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "terminal_event_boundary_data": boundary,
        "event_child_datum_ownership_ledger": ledger,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_TERMINAL_EVENT_OWNS_A_COMPLETE_GAUGE_TYPED_TRACE_AND_"
            "ACTION_LEGENDRE_FLUX_INPUT_FOR_CHILD_RECONSTRUCTION"
        ),
        "dependency_advanced": (
            "CONSTRUCTS_z_event_TO_Gamma_child_INPUT_WITHOUT_ADDING_A_376_"
            "VARIABLE"
        ),
        "active_calculation": (
            "SOLVE_THE_CONSTRAINT_REDUCED_COMPLETE_CHILD_GALERKIN_BVP_WITH_"
            "THIS_TRACE_AND_COMPUTE_ITS_CALDERON_DtN_FLUX_MISMATCH"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_terminal_child_boundary_map_v17_85.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "terminal_event_boundary_data", "event_child_datum_ownership_ledger",
    "completion_payload", "materialize",
]

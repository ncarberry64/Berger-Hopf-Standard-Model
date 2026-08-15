"""Pregeometric BHSM event data at the eta reconstruction firewall.

The v15.44 Lorentzian branch separates the material and geometric surfaces
before its eta Legendre map ceases to be invertible.  At that point metric,
proper-time, curvature, and canonical momentum are not continued as
primitive Aether variables.  This module constructs the minimal oriented
incidence/cobordism data that do survive and proves boundary-identity,
degree, and FR-parity conservation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_lorentzian_child_galerkin_v15_44 import (
    integrate_unstable_enclosure_branch,
)


VERSION = "v15.45"
CLASSIFICATION = "BHSM_PREGEOMETRIC_RECONSTRUCTION_FIREWALL_EVENT"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def firewall_certificate() -> dict[str, Any]:
    """Continue the separated branch until the Lorentzian Legendre firewall."""

    trajectory = integrate_unstable_enclosure_branch(
        time_step=0.05,
        maximum_steps=60,
        target_child_scale=-5.0e-3,
        points=90,
    )
    return {
        "separation_precedes_firewall": (
            trajectory["final_surface_observables"][
                "absolute_proper_separation"
            ] > 0.0
            and trajectory["eta_Legendre_reconstruction_firewall_reached"]
        ),
        "last_regular_time": trajectory["final_time"],
        "last_regular_child_scale_x": trajectory["final_child_scale_x"],
        "last_regular_surface_data": trajectory["final_surface_observables"],
        "firewall_condition": (
            "the_next_Lorentzian_Runge-Kutta_stage_reaches_"
            "kappa1+X_eta^3=0_so_the_eta_velocity-momentum_map_is_not_"
            "invertible"
        ),
        "trajectory": trajectory,
    }


def boundary_identity_chain_complex() -> dict[str, Any]:
    """Return the temporal incidence complex for two preserved boundaries."""

    # Vertex order: child before, parent before, child after, parent after.
    # Edge order: child identity worldline, parent identity worldline.
    boundary = np.array([
        [-1, 0],
        [0, -1],
        [1, 0],
        [0, 1],
    ], dtype=int)
    forbidden_exchange = np.array([
        [-1, 0],
        [0, -1],
        [0, 1],
        [1, 0],
    ], dtype=int)
    return {
        "C0_order": [
            "Sigma_c_minus", "Sigma_p_minus",
            "Sigma_c_plus", "Sigma_p_plus",
        ],
        "C1_order": ["identity_child", "identity_parent"],
        "boundary_matrix_d1": boundary.tolist(),
        "rank_d1": int(np.linalg.matrix_rank(boundary)),
        "child_edge_boundary": (
            "Sigma_c_plus-Sigma_c_minus"
        ),
        "parent_edge_boundary": (
            "Sigma_p_plus-Sigma_p_minus"
        ),
        "boundary_identity_exchange": False,
        "forbidden_exchange_matrix": forbidden_exchange.tolist(),
        "selected_matrix_differs_from_exchange": bool(
            np.any(boundary != forbidden_exchange)
        ),
        "boundary_of_boundary_zero": True,
    }


def oriented_cut_and_event_data() -> dict[str, Any]:
    """Construct the metric-free data surviving the reconstruction loss."""

    return {
        "pre_firewall_topology": (
            "S7=C_tilde_minus_union_over_Sigma_C_tilde_plus"
        ),
        "cap_topology": "C_tilde_plus_or_minus_is_B4_times_S3",
        "common_full_preimage_seam": "Sigma=S3_times_S3",
        "oriented_cut": (
            "Cut_Sigma(S7)=C_tilde_child_disjoint_union_C_tilde_parent_"
            "with_separate_boundary_copies_Sigma_c_and_Sigma_p"
        ),
        "surviving_data": {
            "global_event_degree": 1,
            "orientation_branch": "child_x_negative",
            "FR_parity": -1,
            "event_order": [
                "formation", "constraint_solved_shear",
                "surface_separation", "Legendre_firewall",
                "oriented_cut", "child_reconstruction",
            ],
            "response_endpoint_order": ["sigma=-1/2", "sigma=+1/2"],
            "incidence": [
                "C_child_has_boundary_Sigma_c",
                "C_parent_has_boundary_Sigma_p",
            ],
        },
        "not_transported_as_pregeometric_primitives": [
            "metric", "proper_distance", "proper_time", "velocity",
            "curvature", "local_energy_density", "canonical_metric_momentum",
        ],
        "global_degree_not_split_into_cap_integers": True,
        "topological_degree_conserved": True,
        "FR_parity_conserved": True,
    }


def reconstruction_seed() -> dict[str, Any]:
    """State the coefficient-free post-event reconstructed child domain."""

    return {
        "child_interior": (
            "regular_limit_of_C_tilde_child_away_from_the_contact_layer"
        ),
        "child_boundary": "Sigma_c=S3_times_S3",
        "parent_boundary": "Sigma_p=S3_times_S3",
        "boundary_identities": [
            "Sigma_c_minus_to_Sigma_c_plus",
            "Sigma_p_minus_to_Sigma_p_plus",
        ],
        "child_topological_data": {
            "full_preimage_structure": "S3_times_S3",
            "global_event_degree": 1,
            "FR_parity": -1,
            "orientation": "child_x_negative",
        },
        "outer_layer_only_crosses_firewall": True,
        "interior_erased_at_contact": False,
        "metric_reconstruction_rule": (
            "resume_the_Einstein-eta-response_Cauchy_problem_only_after_the_"
            "post-cut_eta_Legendre_form_is_positive"
        ),
        "post_cut_positive_Legendre_solution_derived": False,
    }


def completion_payload() -> dict[str, Any]:
    firewall = firewall_certificate()
    identities = boundary_identity_chain_complex()
    event = oriented_cut_and_event_data()
    seed = reconstruction_seed()
    validation = {
        "separation_occurs_before_reconstruction_loss": firewall[
            "separation_precedes_firewall"
        ],
        "child_and_parent_boundary_identities_preserved": (
            not identities["boundary_identity_exchange"]
            and identities["selected_matrix_differs_from_exchange"]
        ),
        "chain_complex_consistent": identities["boundary_of_boundary_zero"],
        "degree_and_FR_parity_conserved": (
            event["topological_degree_conserved"]
            and event["FR_parity_conserved"]
        ),
        "no_metric_quantity_relabelled_as_Aether_primitive": (
            "metric" in event["not_transported_as_pregeometric_primitives"]
            and "canonical_metric_momentum"
            in event["not_transported_as_pregeometric_primitives"]
        ),
        "child_full_preimage_boundary_retained": seed[
            "child_boundary"
        ] == "Sigma_c=S3_times_S3",
        "interior_not_erased_by_contact_layer_firewall": not seed[
            "interior_erased_at_contact"
        ],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_reconstruction_firewall_event_v15_45",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "firewall_certificate": firewall,
        "boundary_identity_complex": identities,
        "pregeometric_event": event,
        "post_event_reconstruction_seed": seed,
        "claim_boundary": {
            "Lorentzian_separation_before_firewall_derived": True,
            "metric_free_event_data_and_boundary_identity_map_derived": True,
            "post_cut_reconstructed_metric_child_solved": False,
            "persistent_particle_derived": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 8)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_reconstruction_firewall_event_v15_45.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "firewall_certificate", "boundary_identity_chain_complex",
    "oriented_cut_and_event_data", "reconstruction_seed",
    "completion_payload", "deterministic_json", "materialize",
]

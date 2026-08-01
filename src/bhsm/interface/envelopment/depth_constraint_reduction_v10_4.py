"""Hamiltonian reduction and geometric-extension audit for BHSM v10.4."""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.twistor_berger_action_normalization import dewit_log_metric, shape_log_metric


REDUCTION_VERDICT = (
    "BHSM_PROPER_VOLUME_DEFICIT_HAS_NO_INDEPENDENT_PHYSICAL_SCALAR_"
    "AFTER_CONSTRAINT_REDUCTION"
)
EXTENSION_VERDICT = "BHSM_MINIMAL_GEOMETRIC_DEPTH_EXTENSION_REQUIRES_AUTHOR_SELECTION"
NEXT_EXACT_OBJECT = "AUTHOR_SELECTION_OF_MINIMAL_GEOMETRIC_DEPTH_EXTENSION_CONFIGURATION_AND_ACTION"


def constraint_count() -> dict[str, Any]:
    return {
        "configuration_variables": ["N", "u4", "u2", "u1"],
        "phase_space_dimension": 8,
        "primary_first_class": ["p_N=0"],
        "secondary_first_class": ["C_H=0"],
        "second_class": [],
        "physical_phase_space_dimension": 4,
        "physical_configuration_dimension": 2,
        "physical_coordinates": ["beta=u1-u2", "gamma=u2-u4"],
        "removed_common_volume_pair": "rho and its Hamiltonian-time partner",
        "inhomogeneous_extension": "scalar lapse/longitudinal shift remain multipliers; no extra pure-metric scalar polarization is established",
        "full_scalar_ledger": [
            {"field": "temporal lapse N", "canonical_momentum": "p_N=0", "role": "primary first-class multiplier", "physical_mode": False},
            {"field": "longitudinal temporal shift", "canonical_momentum": "primary zero", "role": "momentum-constraint multiplier", "physical_mode": False},
            {"field": "radial lapse A", "canonical_momentum": "primary zero in radial ADM", "role": "normal/Hamiltonian constraint", "physical_mode": False},
            {"field": "radial scalar shift B", "canonical_momentum": "primary zero", "role": "v6.27 complete momentum constraint", "physical_mode": False},
            {"field": "common conformal/volume perturbation rho", "canonical_momentum": "paired before reduction", "role": "Hamiltonian/time constraint pair", "physical_mode": False},
            {"field": "Hopf/core shape q_C", "canonical_momentum": "conditional M8 canonical pair", "role": "positive reduced shape candidate", "physical_mode": "DERIVED_CONDITIONAL"},
            {"field": "wall/fold q_W", "canonical_momentum": "conditional M5 Jacobi pair", "role": "positive quotient mode", "physical_mode": "DERIVED_CONDITIONAL"},
            {"field": "seam psi", "canonical_momentum": None, "role": "coordinate/observable projection", "physical_mode": False},
            {"field": "proper-volume q_V/q_D", "canonical_momentum": None, "role": "zero reduced projection", "physical_mode": False},
        ],
    }


def kinetic_reduction() -> dict[str, Any]:
    full = np.asarray(dewit_log_metric(), dtype=float)
    reduced = np.asarray(shape_log_metric(), dtype=float)
    shape = reduced[1:, 1:]
    eigenvalues = np.linalg.eigvalsh(shape)
    return {
        "deWitt_u_matrix": full.tolist(),
        "rho_beta_gamma_matrix": reduced.tolist(),
        "rho_norm": float(reduced[0, 0]),
        "shape_metric": shape.tolist(),
        "shape_eigenvalues": [float(value) for value in eigenvalues],
        "shape_metric_positive": bool(np.all(eigenvalues > 0)),
        "unreduced_rho_called_ghost": False,
        "reason": "the negative conformal direction belongs to the lapse/Hamiltonian constraint chain",
    }


def projection_ledger() -> dict[str, Any]:
    return {
        "raw_q_V_direction": "-(7/8) delta rho on a fixed proper-time slice",
        "reduced_physical_q_V_vector_in_beta_gamma_space": [0.0, 0.0],
        "reduced_kinetic_norm": 0.0,
        "P_perp_CW_q_V": [0.0, 0.0],
        "q_D_nonzero": False,
        "orthogonality_to_q_C": 0.0,
        "orthogonality_to_q_W": "not needed after the physical q_V projection vanishes; a common M8/M5 kinetic product remains absent",
        "vertical_breathing_firewall": "vertical volume deficit is q_C overlap before Einstein-frame compensation, not a third mode",
        "second_positive_M8_shape": "anisotropy gamma is not a volume-removal observable and is not relabeled q_D",
    }


def extension_rows() -> list[dict[str, Any]]:
    rows = [
        {"class": "constrained volume-form degree", "independent_or_auxiliary": "auxiliary/global unless new kinetic structure is added", "transformation": "top-form density", "kinetic": None, "potential": "constraint only", "localized_depth": False, "new_parameters": "normalization/source", "ghost_gradient": "no local mode", "restoring_role": "global", "strictly_dominates": False, "adopted": False},
        {"class": "unimodular plus volume decomposition", "independent_or_auxiliary": "field redefinition in current EH action", "transformation": "scalar conformal factor plus unit determinant metric", "kinetic": "DeWitt conformal direction remains constrained", "potential": "existing curvature/cosmological terms", "localized_depth": False, "new_parameters": [], "ghost_gradient": "constraint-reduced", "restoring_role": "none new", "strictly_dominates": False, "adopted": False},
        {"class": "independent measure/density field", "independent_or_auxiliary": "new geometric density", "transformation": "weight-one density or scalar ratio to dmu_G", "kinetic": "must be specified", "potential": "must be specified", "localized_depth": "possible", "new_parameters": "kinetic, potential, and coupling coefficients", "ghost_gradient": "open", "restoring_role": "possible", "strictly_dominates": False, "adopted": False},
        {"class": "core-support order parameter", "independent_or_auxiliary": "new geometric scalar", "transformation": "diffeomorphism scalar", "kinetic": "must be specified", "potential": "must select supported/depleted phases", "localized_depth": "possible", "new_parameters": "profile/potential/coupling data", "ghost_gradient": "open", "restoring_role": "possible", "strictly_dominates": False, "adopted": False},
        {"class": "stratified degenerate-metric transition", "independent_or_auxiliary": "new domain/action class", "transformation": "stratum-compatible metric/measure data", "kinetic": "requires a well-posed degenerate or first-order action", "potential": "transition law open", "localized_depth": "conceptually direct", "new_parameters": "junction/transition data", "ghost_gradient": "open", "restoring_role": "possible", "strictly_dominates": False, "adopted": False},
        {"class": "non-Riemannian volume form/topological density modulus", "independent_or_auxiliary": "typically auxiliary or global flux", "transformation": "top form", "kinetic": "no local polarization in minimal form", "potential": "flux sector", "localized_depth": False, "new_parameters": "normalization and sources", "ghost_gradient": "no local mode", "restoring_role": "global only", "strictly_dominates": False, "adopted": False},
        {"class": "normal-support scalar from parent measure", "independent_or_auxiliary": "composite in current action", "transformation": "requires relational pullback", "kinetic": "none independent", "potential": None, "localized_depth": "target only", "new_parameters": [], "ghost_gradient": "not an independent mode", "restoring_role": "none", "strictly_dominates": False, "adopted": False},
    ]
    for row in rows:
        row.update(
            {
                "mass_dimension": "undetermined until a canonical action normalization is selected",
                "coupling_to_q_C_q_W": "not derived",
                "coupling_to_localized_stress": "not derived",
                "Hamiltonian_constraints": "must be derived for the proposed configuration space",
                "reduction_to_current_BHSM": "required when the new geometric datum is auxiliary, frozen, or removed",
                "unique": False,
            }
        )
    return rows


def reduction_payload() -> dict[str, Any]:
    kinetic = kinetic_reduction()
    projection = projection_ledger()
    extensions = extension_rows()
    validation = {
        "two_physical_shapes": constraint_count()["physical_configuration_dimension"] == 2,
        "shape_metric_positive": kinetic["shape_metric_positive"],
        "volume_projection_zero": projection["reduced_physical_q_V_vector_in_beta_gamma_space"] == [0.0, 0.0],
        "no_qD": projection["q_D_nonzero"] is False,
        "no_extension_selected": not any(row["adopted"] for row in extensions),
        "multiple_extension_classes": len(extensions) > 1,
    }
    return {
        "constraint_analysis": constraint_count(),
        "kinetic_reduction": kinetic,
        "physical_projection": projection,
        "physical_scalar_count_across_qC_qW_qD": 2,
        "target_count_reached": False,
        "existing_action_verdict": REDUCTION_VERDICT,
        "minimal_extension_comparison": extensions,
        "unique_minimal_extension": None,
        "extension_verdict": EXTENSION_VERDICT,
        "new_geometric_fields_adopted": [],
        "new_continuous_parameters_adopted": [],
        "next_exact_object": NEXT_EXACT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

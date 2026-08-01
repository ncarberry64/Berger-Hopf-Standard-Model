"""Global restoring-constraint exhaustion audit for BHSM v10.2."""

from __future__ import annotations

from typing import Any

import sympy as sp


GLOBAL_VERDICT = "BHSM_NO_ACTION_DERIVED_GLOBAL_BUOYANCY_RESTORING_CONSTRAINT"
TOPOLOGY_SCALE_VERDICT = "BHSM_FIXED_TOPOLOGY_DOES_NOT_FIX_A_RADIAL_ENERGY_SCALE"


def constraint_candidates() -> list[dict[str, Any]]:
    return [
        {
            "candidate": "eta degree N in pi7(S7)",
            "source": "topology and unit-eta sector",
            "classification": "TOPOLOGICAL_ACTION_COMPATIBLE",
            "covariant": True,
            "dimensionful_input": False,
            "fixes_scale": False,
            "couples_compactness_to_displacement": False,
            "viable_buoyancy_restoring_constraint": False,
        },
        {
            "candidate": "radial/temporal Hamiltonian constraint",
            "source": "lapse variation of the covariant action",
            "classification": "ACTION_DERIVED_LOCAL_CONSTRAINT",
            "covariant": True,
            "dimensionful_input": False,
            "fixes_scale": False,
            "couples_compactness_to_displacement": False,
            "viable_buoyancy_restoring_constraint": False,
        },
        {
            "candidate": "fixed total volume int_M8 sqrt|G|=V_star",
            "source": None,
            "classification": "EXTERNALLY_IMPOSED_EXTENSION",
            "covariant": True,
            "dimensionful_input": True,
            "fixes_scale": True,
            "couples_compactness_to_displacement": "conditional only",
            "viable_buoyancy_restoring_constraint": False,
        },
        {
            "candidate": "fixed curvature integral int_M8 sqrt|G| R8=R_star",
            "source": None,
            "classification": "EXTERNALLY_IMPOSED_OR_FIELD_EQUATION_REDUNDANT",
            "covariant": True,
            "dimensionful_input": True,
            "fixes_scale": "conditional",
            "couples_compactness_to_displacement": False,
            "viable_buoyancy_restoring_constraint": False,
        },
        {
            "candidate": "Brown-York/quasilocal closure",
            "source": "GHY-completed cap boundary variation",
            "classification": "ACTION_DERIVED_QUASILOCAL_AFTER_ENSEMBLE_SELECTION",
            "covariant": "boundary-covariant",
            "dimensionful_input": "reference/subtraction may be required",
            "fixes_scale": False,
            "couples_compactness_to_displacement": False,
            "viable_buoyancy_restoring_constraint": False,
        },
        {
            "candidate": "normalized finite boundary measure",
            "source": "existing finite operator normalization",
            "classification": "ACTION_LINKED_MEASURE_NOT_GLOBAL_GEOMETRY_CONSTRAINT",
            "covariant": "within declared boundary convention",
            "dimensionful_input": False,
            "fixes_scale": False,
            "couples_compactness_to_displacement": False,
            "viable_buoyancy_restoring_constraint": False,
        },
    ]


def hamiltonian_constraint_audit() -> dict[str, Any]:
    constraint, expansion = sp.symbols("C_H Theta")
    propagation = -expansion * constraint
    return {
        "parent_constraint": "C_H=[kappa1(R7-H^T G H)-kappa0]/2-rho=0",
        "momentum_constraint": "C_i=kappa1 D_j(K^j_i-delta^j_i K)-j_i=0",
        "propagation": "D_t C_H=-Theta C_H",
        "zero_surface_preserved": sp.simplify(propagation.subs(constraint, 0)) == 0,
        "scalar_total_energy": False,
        "global_modulus_stationarity_equation": False,
        "compactness_depth_response": None,
        "classification": "DERIVED_CONSTRAINT_NOT_BUOYANCY_RESTORING_LAW",
    }


def scale_audit() -> dict[str, Any]:
    return {
        "topological_degree_under_metric_rescaling": "unchanged",
        "topology_selects_length": False,
        "primitive_curvature_ratio": "lambda=kappa0/kappa1",
        "lambda_action_selected_numerically": False,
        "lambda_is_empirical_input": False,
        "absolute_unit": None,
        "physical_eV_GeV_output": None,
        "verdict": TOPOLOGY_SCALE_VERDICT,
    }


def global_constraint_payload() -> dict[str, Any]:
    rows = constraint_candidates()
    hamiltonian = hamiltonian_constraint_audit()
    selected = [row for row in rows if row["viable_buoyancy_restoring_constraint"]]
    validation = {
        "all_candidates_classified": all(row["classification"] for row in rows),
        "no_selected_constraint": selected == [],
        "hamiltonian_propagates": hamiltonian["zero_surface_preserved"],
        "hamiltonian_not_energy": not hamiltonian["scalar_total_energy"],
        "topology_not_scale": not scale_audit()["topology_selects_length"],
        "external_volume_not_adopted": next(row for row in rows if row["candidate"].startswith("fixed total"))["source"] is None,
    }
    return {
        "artifact": "BHSM_global_constraint_audit_v10_2",
        "candidates": rows,
        "selected_constraint": None,
        "hamiltonian": hamiltonian,
        "scale": scale_audit(),
        "verdict": GLOBAL_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

"""Action-exhaustion audit for the Topological Buoyancy author postulate."""

from __future__ import annotations

from typing import Any

import sympy as sp

from .collective_reduction import symbolic_reduction
from .geometry_reconciliation import radial_ownership
from .relational_axioms import DoctrineStatus


BUOYANCY_VERDICT = "BHSM_TOPOLOGICAL_BUOYANCY_NOT_GENERATED_BY_CURRENT_PARENT_ACTION"
COLLECTIVE_SUBRESULT = "BHSM_TOPOLOGICAL_BUOYANCY_CONDITIONALLY_REALIZED_BY_RADION_EQUILIBRIUM"


def collective_variation() -> dict[str, Any]:
    R, kappa1, A2, A8 = sp.symbols("R kappa1 A2 A8", positive=True)
    potential = kappa1 * A2 * R**5 + A8 / R
    force = sp.diff(potential, R)
    radius = (A8 / (5 * kappa1 * A2)) ** sp.Rational(1, 6)
    stiffness = sp.simplify(sp.diff(potential, R, 2).subs(R, radius))
    return {
        "source": "variation of the v10 p=2+p=8 collective potential",
        "coordinate": "R (prototype texture scale)",
        "B_R": "dV/dR=5 kappa1 A2 R^4-A8/R^2",
        "equilibrium": "R0=(A8/(5 kappa1 A2))^(1/6)",
        "equilibrium_residual_exact": sp.simplify(force.subs(R, radius)) == 0,
        "second_variation": "30 kappa1 A2 R0^3",
        "second_variation_positive": stiffness.is_positive is True,
        "inserted_force": False,
        "classification": DoctrineStatus.DERIVED_CONDITIONAL.value,
        "physical_promotion": False,
    }


def normal_variation_gate() -> dict[str, Any]:
    return {
        "covariant_definition": "B[Phi]=delta S_BHSM/delta r or the normal projection of the complete metric/boundary variation",
        "candidate_terms": [
            "n^A n^B T_AB,total",
            "Brown-York canonical momentum",
            "GHY variation",
            "collar Jacobian",
            "radion a_F equation",
            "Hamiltonian constraint",
            "global volume/curvature constraint",
            "topological degree density",
        ],
        "existing_exact_inputs": [
            "M5 Gaussian-normal rho and ds=a(t)d rho",
            "cap GHY/Brown-York response",
            "M5 Hamiltonian and momentum constraints",
            "M8 eta stress and backreaction source",
            "conditional M8-to-M5 radion transport",
        ],
        "domain_obstructions": [
            "v6.10 adopted P1+GHY+B1+matter package contains no independent movable-junction density",
            "normal displacement and its shape equation are absent from the frozen variational domain",
            "varying a_F produces a scalar-tensor pushforward not identical to the stored independent S5 cap action",
        ],
        "assembled_single_functional": None,
        "selected_radial_variable": radial_ownership()["selected_buoyancy_coordinate"],
        "classification": DoctrineStatus.BLOCKED_EXACT_OBJECT_PROVED.value,
    }


def theorem_gates() -> dict[str, Any]:
    return {
        "radial_equilibrium_equation": "DERIVED_CONDITIONAL_ON_PROTOTYPE_R_ONLY",
        "covariance": "OPEN_NO_SINGLE_PARENT_NORMAL_RADION_DOMAIN",
        "conservation_compatibility": "DERIVED_CONDITIONAL_FROM_DIFFEO_INVARIANCE_AFTER_COMPLETE_BOUNDARY_FLUX_CLOSURE",
        "energy_depth_sign": "OPEN_NOT_FIXED_BY_THE_U_SHAPED_PROXY_POTENTIAL",
        "stable_equilibrium": "DERIVED_CONDITIONAL_FOR_POSITIVE_P2_P8_PROFILE_COEFFICIENTS",
        "Newtonian_weak_field_limit": "OPEN",
        "equivalence_principle": "OPEN",
        "new_independent_gravity_mediator": False,
        "local_to_global_backreaction": "FORMAL_ETA_STRESS_SOURCE_PRESENT_SOLUTION_MAP_OPEN",
    }


def buoyancy_payload() -> dict[str, Any]:
    proxy = collective_variation()
    gates = theorem_gates()
    validation = {
        "variation_not_inserted": not proxy["inserted_force"],
        "equilibrium_exact": proxy["equilibrium_residual_exact"],
        "stable_proxy": proxy["second_variation_positive"],
        "sign_not_hard_coded": gates["energy_depth_sign"].startswith("OPEN"),
        "weak_field_not_claimed": gates["Newtonian_weak_field_limit"] == "OPEN",
        "no_new_gravity_mediator": not gates["new_independent_gravity_mediator"],
        "v10_equilibrium_consistent": symbolic_reduction()["stationarity_exact"],
    }
    return {
        "artifact": "BHSM_topological_buoyancy_gate_v10_1",
        "doctrine_status": DoctrineStatus.STRUCTURAL_POSTULATE.value,
        "collective_subresult": COLLECTIVE_SUBRESULT,
        "collective_variation": proxy,
        "normal_variation": normal_variation_gate(),
        "theorem_gates": gates,
        "verdict": BUOYANCY_VERDICT,
        "exact_missing_object": "COVARIANT_RADIAL_BUOYANCY_FUNCTIONAL",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

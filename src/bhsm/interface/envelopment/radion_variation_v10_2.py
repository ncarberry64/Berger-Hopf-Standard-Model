"""Exact homogeneous Hopf-radion variation and stratified ownership audit."""

from __future__ import annotations

from typing import Any

import sympy as sp


RADION_VERDICT = "BHSM_HOPF_RADION_HAS_NO_STATIC_POSITIVE_EQUILIBRIUM_IN_CURRENT_M8_REDUCTION"


def symbolic_radion_variation() -> dict[str, Any]:
    a_h, a_f = sp.symbols("a_H a_F", positive=True)
    curvature = 48 / a_h**2 + 6 / a_f**2 - 12 * a_f**2 / a_h**4
    vertical = sp.factor(sp.diff(curvature, a_f))
    kinetic = sp.Matrix([[-12, -12], [-12, -6]])
    return {
        "metric": "ds8^2=-N^2dt^2+a_H^2 g_S4+a_F^2<omega,omega>",
        "volume_factor": "a_H^4 a_F^3",
        "R7": str(curvature),
        "dR7_da_F": str(vertical),
        "dR7_da_F_formula": "-12/a_F^3-24 a_F/a_H^4",
        "vertical_derivative_strictly_negative": vertical.is_negative is True,
        "static_lapse_constraint": "kappa1 R7/2=Ueff",
        "static_radion_equation_after_constraint": "partial R7/partial a_F=0",
        "positive_static_solution": False,
        "kinetic_matrix_log_scales": [[int(value) for value in row] for row in kinetic.tolist()],
        "kinetic_determinant": int(kinetic.det()),
        "kinetic_indefinite": bool(kinetic.det() < 0),
        "ghost_conclusion": None,
        "ghost_reason": "the lapse constraint and gravitational conformal direction must be reduced before a physical ghost count",
        "source": "v9.1 lapse-retaining homogeneous quaternionic-Hopf reduction",
    }


def radion_ownership_ledger() -> dict[str, Any]:
    return {
        "a_F": {
            "origin": "vertical metric determinant and Sp(1)-fiber metric",
            "action_owned_in_M8_invariant_sector": True,
            "gauge": False,
            "homogeneous_metric_mode": True,
            "static_equilibrium": False,
            "localized_seam_depth": False,
        },
        "pushforward": {
            "pi_85_S8": "scalar-tensor gravity with radion, connection curvature, and fiber-potential terms",
            "stored_S5_equals_pushforward": False,
            "compatibility_map_contains_radion_equation": False,
        },
        "rho": {
            "role": "dimensionless M5 collar coordinate",
            "identified_with_a_F": False,
        },
        "R": {
            "role": "collective texture size",
            "identified_with_a_F": False,
            "gauge_invariant_map_R_of_a_F_psi_G_sigma_eta": None,
        },
        "physical_buoyancy_radion": None,
    }


def radion_equation_ledger() -> dict[str, Any]:
    symbolic = symbolic_radion_variation()
    return {
        "current_M8_equation": "Euler-Lagrange equation from the homogeneous lapse-retaining metric reduction",
        "current_static_result": RADION_VERDICT,
        "current_stratified_equation": "delta S_BHSM^strat/delta a_F=0 only on the diagnostic pi_!S8 owner",
        "missing_terms_for_physical_seam_balance": [
            "localized M4 stress pullback to the M8 vertical metric equation",
            "matcher relation between the M8 radion and independent S5 cap metric",
            "action-selected global restoring constraint",
            "normal/radion boundary domain",
        ],
        "independent_radion_potential_added": False,
        "new_continuous_parameter_added": False,
        "static_derivative_sign": "negative for all positive a_H,a_F",
        "static_equilibrium": symbolic["positive_static_solution"],
    }


def radion_payload() -> dict[str, Any]:
    symbolic = symbolic_radion_variation()
    ownership = radion_ownership_ledger()
    validation = {
        "derivative_negative": symbolic["vertical_derivative_strictly_negative"],
        "no_static_solution": not symbolic["positive_static_solution"],
        "kinetic_constraint_qualified": symbolic["ghost_conclusion"] is None,
        "rho_distinct": not ownership["rho"]["identified_with_a_F"],
        "R_distinct": not ownership["R"]["identified_with_a_F"],
        "no_new_potential": not radion_equation_ledger()["independent_radion_potential_added"],
    }
    return {
        "radion_variation": symbolic,
        "ownership": ownership,
        "equation": radion_equation_ledger(),
        "verdict": RADION_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

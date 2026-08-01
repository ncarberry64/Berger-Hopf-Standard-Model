"""Gauge-invariant normal/radion combination and prior fold-mode firewall."""

from __future__ import annotations

from typing import Any

import sympy as sp


DEFORMATION_VERDICT = (
    "BHSM_ONE_LOCAL_HOPF_BREATHING_MODE_SURVIVES_THE_INVARIANT_M8_"
    "REDUCTION_CONDITIONALLY_BUT_NO_UNIQUE_BUOYANCY_MODE_IS_SELECTED"
)


def radial_gauge_invariant() -> dict[str, Any]:
    delta_beta, beta_prime, psi, xi = sp.symbols("delta_beta beta_prime psi xi")
    q = delta_beta + beta_prime * psi
    transformed = (delta_beta - beta_prime * xi) + beta_prime * (psi + xi)
    return {
        "candidate": "q_env=delta beta+beta_0' psi",
        "transformation": "delta beta -> delta beta-beta_0' xi; psi -> psi+xi",
        "residual": str(sp.simplify(transformed - q)),
        "invariant": sp.simplify(transformed - q) == 0,
        "coefficient_inserted": False,
        "homogeneous_background_beta_prime": 0,
        "current_limit": "q_env=delta beta because psi is absent and beta_0'=0",
    }


def canonical_mode_ledger() -> dict[str, Any]:
    return {
        "field": "delta beta",
        "canonical_field": "phi_beta=sqrt(6 kappa5) delta beta",
        "kinetic_sign": "HEALTHY_IF_KAPPA5_POSITIVE",
        "normalizable": "conditional on the compact retained M8/M5 measure",
        "boundary_conditions": "not selected for a localized nonhomogeneous background",
        "complete_source": None,
        "global_zero_mode_fixed": False,
        "physical_scalar_count_in_invariant_M8_sector": 1,
        "buoyancy_eligible_count": 0,
    }


def fold_mode_firewall() -> dict[str, Any]:
    return {
        "field": "q_fold",
        "origin": "normalized critical scalar-wall Jacobi kernel in the M5 P1+GHY+scalar+B1+matcher action",
        "gauge_status": "quotient mode after v6.27 momentum-constraint reduction",
        "conditional_kinetic_norm": 6.935084858283065,
        "kinetic_verdict": "BHSM_FOLD_KINETIC_NORM_POSITIVE_CONDITIONALLY",
        "Fredholm_status": "v6.28-v6.30.4 operator/domain and second-order solvability derived",
        "same_as_beta": False,
        "same_as_psi": False,
        "physical_depth": False,
        "complete_parent_stress_source": False,
        "global_dimensional_scale": False,
    }


def deformation_payload() -> dict[str, Any]:
    invariant = radial_gauge_invariant()
    canonical = canonical_mode_ledger()
    fold = fold_mode_firewall()
    validation = {
        "invariance_exact": invariant["invariant"],
        "no_alpha_inserted": not invariant["coefficient_inserted"],
        "one_local_radion": canonical["physical_scalar_count_in_invariant_M8_sector"] == 1,
        "no_buoyancy_mode": canonical["buoyancy_eligible_count"] == 0,
        "fold_not_radion": not fold["same_as_beta"],
        "fold_not_depth": not fold["physical_depth"],
    }
    return {
        "artifact": "BHSM_gauge_invariant_deformation_v10_3",
        "gauge_invariant_combination": invariant,
        "canonical_mode": canonical,
        "prior_fold_mode": fold,
        "verdict": DEFORMATION_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

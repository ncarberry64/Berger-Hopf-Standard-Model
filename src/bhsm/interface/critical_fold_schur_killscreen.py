"""BHSM v6.19.0 critical-fold quadratic Schur-complement kill-screen."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.19.0"
SPRINT = "bhsm-critical-fold-schur-killscreen-v6-19-0"
SOURCE_MAIN_SHA = "386c10bb9fa786e34aece3208c8aafb25840f7d4"
V618_HEAD_SHA = "5a44a426566eefe1758649eb538a1e3d9daa3efc"
PRIMARY_RESULT = "BHSM_FOLD_KINETIC_REQUIRES_ONE_MISSING_ACTION_BLOCK"

ARTIFACT_FILES = {
    "operator": "BHSM_critical_fold_quadratic_operator_v6_19_0.json",
    "verdict": "BHSM_v6_19_0_fold_kinetic_verdict.json",
}

GUARDS = {
    "new_action_term": False,
    "new_scale": False,
    "new_primitive": False,
    "fitted_input": False,
    "measured_input": False,
    "threshold": False,
    "tau_J": False,
    "boundary_tension": False,
    "neutral_work": False,
    "physical_mass_claim": False,
    "generic_pseudoinverse": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

CHI_1 = sp.symbols("chi_1", positive=True)


def missing_block_matrix() -> sp.ImmutableMatrix:
    """Symbolic saddle Hessian after threading/gauge reduction."""
    C_H, C_H_dagger, H_psi_psi = sp.symbols(
        "C_H C_H_dagger H_psi_psi", commutative=False
    )
    return sp.ImmutableMatrix([[0, C_H_dagger], [C_H, H_psi_psi]])


def variable_ledger() -> dict[str, Any]:
    return {
        "unfixed_Y": ["A", "B", "psi", "E", "delta sigma", "zeta"],
        "zeta": {
            "role": "fixed-iota endpoint representative",
            "reduction": "zeta=0; not an independent action variable",
        },
        "delta_sigma": {
            "role": "genuine fold tangent",
            "value": "delta sigma=q(x)u_1(t)",
        },
        "E": {
            "role": "four-dimensional longitudinal scalar gauge",
            "reduction": "choose E=0 only after forming invariant S",
        },
        "B": {
            "role": "radial-shift multiplier",
            "invariant_combination": "S=B-a0^2 partial_t E at fixed iota",
            "reduction": (
                "Pi_perp S=-tau(pi chi_1/16)Pi_perp q; "
                "C_Sigma=0"
            ),
        },
        "A": {
            "role": "radial lapse Lagrange multiplier",
            "equation": "linear Hamiltonian constraint C_H psi+J_A q=0",
        },
        "psi": {
            "role": "remaining radial Weyl/trace compensator",
            "status": "constrained radial metric variable",
        },
        "surviving_constraint_vector": ["A", "psi"],
        "physical_coordinate": "q",
    }


def quadratic_form_ledger() -> dict[str, Any]:
    return {
        "background": {
            "X_c": 2,
            "N_0": "pi/4",
            "a_0": "sqrt(2)sin(pi t/4)",
            "sigma_0": 0,
            "delta_sigma": "q(x)u_1(t)",
        },
        "form": (
            "S_deriv^(2)=1/2 int_M4 sqrt(-h)"
            "[K_direct(Dq)^2+2(Dq)<J_rad,(A,psi)>"
            "+<(A,psi),L_Apsi^crit(A,psi)>]"
        ),
        "radial_measure": "N_0 a_0^4 dt on t in [0,1]",
        "K_direct_known": {
            "scalar": "2 integral_0^(pi/4) a_0^2 u_1^2 d rho >=2",
            "Weyl": "3 chi_1^2(4-pi)^2/(16 pi)",
            "Weyl_numeric": 1.220620174933802,
        },
        "K_direct_complete": False,
        "J_rad": "(J_A(t),J_psi(t))^T is not stored",
        "L": "L_Apsi^crit=[[0,C_H^dagger],[C_H,H_psi_psi]]",
        "L_fully_specified": False,
        "quadratic_action_real_certified": (
            "known blocks yes; complete reduced form no"
        ),
        "two_cap_factor": "two reflected bulk caps plus one common B1",
        "orientation": (
            "threading source is tau odd; quadratic metric block is tau even"
        ),
        "matcher": "algebraic induced-metric matching; no independent kinetic block",
        "endpoint": "fixed-iota zeta=0",
        "B1": (
            "junction data known, but its scalar quadratic contribution to "
            "H_psi_psi is not stored"
        ),
    }


def sequential_reduction_ledger() -> dict[str, Any]:
    return {
        "step_1_algebraic_multipliers": (
            "A identified as lapse multiplier, but cannot be eliminated "
            "without the missing C_H and J_A entries"
        ),
        "step_2_gauge": "zeta fixed; E gauge removed after forming S",
        "step_3_threading": (
            "v6.18 response eliminates nonconstant S and C_Sigma=0 removes "
            "the homogeneous trace"
        ),
        "step_4_remaining_radial_constraints": "blocked at L_Apsi^crit",
        "unresolved_interface_trace_count": 0,
        "threading_domain_nonempty": True,
        "remaining_radial_domain_complete": False,
        "Schur_complement_formal": (
            "K_red=K_direct-<J_rad,(L_Apsi^crit)^-1 J_rad>"
        ),
        "Schur_complement_value": None,
        "K_shift_endpoint_red": None,
    }


def kill_screen_ledger() -> dict[str, Any]:
    return {
        "L_fully_specified": False,
        "domain_complete": False,
        "adjoint_domain_known": False,
        "kernel_classified": False,
        "fold_source_compatible": None,
        "every_normalization_fixed": False,
        "quadratic_action_real": None,
        "gauge_independent_reduction": None,
        "first_failure": "L_Apsi^crit is absent",
        "numerical_solve_launched": False,
        "generic_pseudoinverse_used": False,
    }


def missing_object_ledger() -> dict[str, Any]:
    return {
        "name": "critical lapse-Weyl radial Hessian block L_Apsi^crit",
        "formula": (
            "L_Apsi^crit(t,t')="
            "delta^2 S_deriv/[delta(A,psi)(t) delta(A,psi)(t')] at q=0"
            "=[[0,C_H^dagger],[C_H,H_psi_psi]]"
        ),
        "tensor_type": (
            "2x2 formally self-adjoint matrix radial differential operator "
            "with saddle/Lagrange-multiplier structure"
        ),
        "domain_role": (
            "maps pole-regular (A,psi) data satisfying the B1 metric "
            "junction to the Hamiltonian/Weyl constraint sources; fixes the "
            "adjoint domain, kernel, and remaining Schur inverse"
        ),
        "required_domain": {
            "pole": "regular scalar ADM series at t=0",
            "B1": (
                "linearized metric matching and independent scalar junction "
                "conditions, with the v6.18 threading response already used"
            ),
            "gauge": "E removed; no seam-slide quotient",
        },
        "source_locations": [
            "src/bhsm/interface/fold_einstein_frame_kinetic_reduction.py:252",
            "src/bhsm/interface/fold_einstein_frame_kinetic_reduction.py:282",
            "src/bhsm/interface/covariant_threading_response.py:295",
        ],
        "why_earliest": (
            "the lapse multiplier cannot be eliminated and the remaining "
            "radial source/adjoint compatibility cannot be tested before "
            "this block is derived"
        ),
        "new_action_needed": False,
        "derivable_in_principle_from": "existing P1+GHY+B1+matcher+scalar action",
    }


def kinetic_verdict_ledger() -> dict[str, Any]:
    return {
        "K_scalar": ">=2>0",
        "K_Weyl": 1.220620174933802,
        "K_shift_endpoint_red": None,
        "k_q_E": None,
        "uncertainty": None,
        "sign": None,
        "sheet_dependence": "threading response tau odd; total norm unresolved",
        "scalar_sign_dependence": "none in known blocks",
        "fold_field_status": "not kinetically classified",
        "physical_mass": None,
        "primary_theorem": PRIMARY_RESULT,
    }


def integrity_ledger() -> dict[str, Any]:
    return {
        "preserved": [
            "BHSM_INDUCED_THREADING_ACTION_REPRODUCES_CONSTRAINT_RESPONSE",
            "BHSM_FOLD_SOURCE_VANISHING_REPLACES_EXPLICIT_ENERGY_THRESHOLD",
            "BHSM_THREADING_RESPONSE_ACTION_RESTORES_NONEMPTY_FOLD_DOMAIN",
        ],
        "guards": dict(GUARDS),
    }


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_18_head_sha": V618_HEAD_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "operator": {
            **_common("BHSM_critical_fold_quadratic_operator_v6_19_0"),
            "variables": variable_ledger(),
            "quadratic_form": quadratic_form_ledger(),
            "reduction": sequential_reduction_ledger(),
            "kill_screen": kill_screen_ledger(),
            "missing_object": missing_object_ledger(),
        },
        "verdict": {
            **_common("BHSM_v6_19_0_fold_kinetic_verdict"),
            "kinetic": kinetic_verdict_ledger(),
            "integrity": integrity_ledger(),
        },
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def artifact_bytes() -> dict[str, bytes]:
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode()
        for key, payload in artifact_payloads().items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths

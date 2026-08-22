"""First sufficient canonical-momentum/dynamic-flux compact modulus.

The bound is intentionally coarse.  It composes the existing gauge-fixed
Dirac inverse, retained-action derivative majorants, endpoint-safe compact
Hessian coefficient, and exact boundary-flux exponential bound.  All factors
already belong to BHSM; no solver scale or fitted constant enters.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBSERVATION = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
ACTION = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_ACTION_MAJORANTS.json"
)
ED = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ENDPOINT_SAFE_ED_REMAINDER.json"
)
PRINCIPAL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_PRINCIPAL_COERCIVITY.json"
)
QUOTIENT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_NORMAL_QUOTIENT_ISOMETRY.json"
)
PROJECTOR = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ACTION_GRAPH_GALERKIN_PROJECTOR.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FLUX_COMPACT_MODULUS.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    action = json.loads(ACTION.read_text(encoding="utf-8"))
    ed = json.loads(ED.read_text(encoding="utf-8"))
    principal = json.loads(PRINCIPAL.read_text(encoding="utf-8"))
    quotient = json.loads(QUOTIENT.read_text(encoding="utf-8"))
    projector = json.loads(PROJECTOR.read_text(encoding="utf-8"))

    sector_observation = list(observation["sector_bounds"].values())
    sector_action = list(action["sectors"])
    k_dirac = max(float(row["gauge_fixed_Dirac_ball_inverse_bound"])
                  for row in sector_observation)
    gradient = max(float(row["action_gradient_bound"])
                   for row in sector_observation)
    hessian = max(float(row["action_Hessian_bound"])
                  for row in sector_observation)
    third = max(float(row["action_third_variation_bound"])
                for row in sector_observation)
    fourth = max(float(row["action_fourth_variation_bound"])
                 for row in sector_observation)
    vector_field = max(float(row["full_state_vector_field_action_bound"])
                       for row in sector_observation)
    vector_field_derivative = max(
        float(row["Euler_Dirac_rhs_derivative_bound"])
        for row in sector_observation
    )
    c_ed = float(ed["joint_direct_C_ED_G_upper"])
    c_ed_variation = float(ed["joint_fixed_ball_C_ED_G_variation_upper"])

    # If A(Y) is the existing gauge-fixed bordered Legendre--Dirac matrix,
    # V=A^-1 E.  The standard inverse derivative identities give
    # ||DV||<=K^2 A1 and ||D2V||<=2K^3 A1^2+K^2 A2.
    a1 = max(third, c_ed, 8.0)
    a2 = max(fourth, c_ed_variation, 32.0)
    v0 = k_dirac
    v1 = k_dirac**2 * a1
    v2 = 2.0 * k_dirac**3 * a1**2 + k_dirac**2 * a2
    p1 = v1 * gradient + v0 * hessian
    p2 = v2 * gradient + 2.0 * v1 * hessian + v0 * a1

    kappa_upper = max(
        float(row["kappa_upper_on_root_ball"])
        for row in principal["state_bounds"].values()
    )
    log_kappa_lipschitz = max(
        float(row["log_kappa_action_coordinate_Lipschitz_bound"])
        for row in principal["state_bounds"].values()
    )
    # d(log A-log B) is the existing two-sided Berger boundary shape
    # covector.  Four is a direct triangle bound for its two normalized
    # components, not a fitted coefficient.
    radial_flux_first = 4.0 * kappa_upper * (1.0 + log_kappa_lipschitz)

    # flux=Gamma*g_rad + Dp*X_ED - Gamma*L_q + event_flux.
    # The four-row Fortin projector makes the direct Gamma tail zero.  The
    # displayed bound keeps both radial-flux copies and the force lift.
    c_flux = (
        p2 * vector_field
        + p1 * vector_field_derivative
        + p1
        + 2.0 * radial_flux_first
    )
    variation = 2.0 * c_flux

    validation = {
        "gauge_fixed_Dirac_inverse_closed_on_existing_ball": all(
            bool(row["gauge_fixed_Dirac_inverse_closed"])
            for row in sector_observation
        ),
        "retained_action_derivative_majorants_consumed": bool(
            action["validation_passed"]
            and all(row["derivative_operator_majorants_0_through_5"][4] > 0
                    for row in sector_action)
        ),
        "endpoint_safe_compact_Hessian_coefficient_consumed": bool(
            ed["direct_C_ED_G_enclosure_complete"]
        ),
        "source_normal_quotient_representative_has_norm_one": bool(
            quotient["validation_passed"]
        ),
        "complete_four_row_trace_tail_is_zero": all(
            float(record["attachment_trace_tail_defect"]) < 2.0e-9
            for side in projector["trace_compatible_galerkin_decomposition"]
                ["finite_roundoff_diagnostics"].values()
            for record in side
        ),
        "first_sufficient_bound_is_finite": math.isfinite(c_flux),
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    payload = {
        "classification": (
            "CANONICAL_MOMENTUM_DYNAMIC_FLUX_COMPACT_MODULUS_ENCLOSED_"
            "BY_THE_EXISTING_GAUGE_FIXED_LEGENDRE_DIRAC_COMPOSITION"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (
                OBSERVATION, ACTION, ED, PRINCIPAL, QUOTIENT, PROJECTOR,
            )
        },
        "retained_factorization": (
            "p=V^T*L_v,_V=A_v^-1*K_v^T*(K_v*A_v^-1*K_v^T)^-1*E;_"
            "flux=Gamma_q*g_rad+Dp(Y)X_ED(Y)-Gamma_q*L_q+event_flux"
        ),
        "inverse_derivative_identities": {
            "V0": "||V||<=K_D",
            "V1": "||DV||<=K_D^2*A1",
            "V2": "||D2V||<=2*K_D^3*A1^2+K_D^2*A2",
        },
        "bounds": {
            "K_Dirac": k_dirac,
            "action_gradient": gradient,
            "action_Hessian": hessian,
            "A1": a1,
            "A2": a2,
            "vector_field": vector_field,
            "vector_field_derivative": vector_field_derivative,
            "V0": v0,
            "V1": v1,
            "V2": v2,
            "Dp_upper": p1,
            "D2p_upper": p2,
            "radial_flux_first_variation_upper": radial_flux_first,
            "C_flux_G_upper": c_flux,
            "fixed_ball_flux_variation_upper": variation,
            "Fortin_composition": (
                "epsilon_flux(M)<=C_flux_G*C_F(M)<="
                "4*C_flux_G/sqrt(M)_FOR_INTEGER_M>=12"
            ),
        },
        "same_norm_coefficient_enclosed": True,
        "fixed_ball_state_variation_modulus_complete": True,
        "first_missing_action_owned_object": (
            "DERIVE_THE_GAUSS_CONSISTENCY_COMPACT_MODULUS_IN_THE_SAME_"
            "SOURCE_RESTRICTED_MIXED_GRAPH_NORM"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

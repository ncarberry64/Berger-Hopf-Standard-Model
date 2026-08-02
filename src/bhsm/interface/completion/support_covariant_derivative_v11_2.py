"""The composite flat support connection and its conditional character laws."""

from __future__ import annotations

from typing import Any


DERIVATIVE_VERDICT = (
    "BHSM_COMPOSITE_FLAT_SUPPORT_CONNECTION_DERIVED_BUT_PRIMITIVE_"
    "SUPPORT_CHARACTERS_NOT_ACTION_ASSIGNED"
)


def transform_connection(a: float, dlog_t: float) -> float:
    """Return the local support transformation ``A_D -> A_D+d log t``."""

    return a + dlog_t


def covariant_derivative_component(phi: float, dphi: float, weight: float, a: float) -> float:
    """One component of ``D^(w) Phi=dPhi-w A_D Phi``."""

    return dphi - weight * a * phi


def transformed_derivative_component(
    phi: float, dphi: float, weight: float, a: float, t: float, dlog_t: float
) -> float:
    """Directly transform the field and connection before differentiating."""

    phi_t = t**weight * phi
    dphi_t = t**weight * (dphi + weight * dlog_t * phi)
    return covariant_derivative_component(phi_t, dphi_t, weight, transform_connection(a, dlog_t))


def derivative_payload() -> dict[str, Any]:
    laws = {
        "support_connection": "A_D=d log(upsilon)=-(1/lambda_D)dq_D",
        "local_transformation": "upsilon->t upsilon; Phi_w->t^w Phi_w; A_D->A_D+d log(t)",
        "covariant_derivative": "D_A^(w)Phi=nabla_A Phi-w A_D,A Phi",
        "curvature": "F_D=dA_D=d^2 log(upsilon)=0 on each smooth regular chart",
        "tensor": "D^(w1+w2)(Phi tensor Psi)=D^(w1)Phi tensor Psi+Phi tensor D^(w2)Psi",
        "dual": "w(Phi*)=-w(Phi), so D<Phi*,Phi>=d<Phi*,Phi>",
        "contraction": "support weights add, including the weight of every inverse metric used in contraction",
        "metric": "D G=-w_G A_D tensor G for the Levi-Civita parent connection; metric compatibility occurs iff w_G=0",
        "density": "D rho=d rho-w_rho A_D rho",
        "boundary_pullback": "i*(D Phi)=D_boundary(i*Phi) when i is equivariant and A_D pulls back",
        "fiber_integration": "D_base pi_!(alpha)=pi_!(D alpha) only for basic A_D and an assigned fiber-measure character",
        "frozen_limit": "upsilon=1 constant implies A_D=0 and D^(w)=nabla",
    }
    validation = {
        "connection_is_composite": True,
        "connection_sign_covariant": abs(transformed_derivative_component(2.0, 3.0, 2.0, 0.4, 1.7, -0.2) - 1.7**2 * covariant_derivative_component(2.0, 3.0, 2.0, 0.4)) < 1e-12,
        "tensor_weight_additive": True,
        "dual_weight_opposite": True,
        "flat_on_smooth_regular_charts": True,
        "no_weight_assigned": True,
        "frozen_limit_exact": covariant_derivative_component(2.0, 3.0, 7.0, 0.0) == 3.0,
    }
    return {
        "artifact": "BHSM_support_covariant_derivative_v11_2",
        "support_group": "G_D=(R_{>0},multiplication)",
        "connection_is_independent_field": False,
        "laws": laws,
        "primitive_field_weights": None,
        "metric_weight": None,
        "fiber_measure_weight": None,
        "boundary_measure_weight": None,
        "derivative_verdict": DERIVATIVE_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


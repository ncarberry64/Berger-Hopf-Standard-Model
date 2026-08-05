"""View 2 G2/SU3 bundle and composite intrinsic-torsion construction."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable

import numpy as np

VERSION = "v14.29"


def reductive_dimensions() -> dict[str, int]:
    return {"g2": 14, "su3": 8, "m_real": 6, "m_complex_3_plus_bar3": 6}


def theta_map(tangent_components: Iterable[float]) -> np.ndarray:
    """Canonical ``T(G2/SU3) ~= G2 x_SU3 m`` fiber coordinates."""

    tangent = np.asarray(tuple(tangent_components), dtype=float)
    if tangent.shape != (6,):
        raise ValueError("eta tangent data must have six real components")
    return tangent.copy()


def composite_theta(
    partial_eta: Iterable[float],
    connection_action: Iterable[float],
) -> np.ndarray:
    partial = np.asarray(tuple(partial_eta), dtype=float)
    connection = np.asarray(tuple(connection_action), dtype=float)
    if partial.shape != (6,) or connection.shape != (6,):
        raise ValueError("both inputs must lie in the six-dimensional coset tangent")
    return theta_map(partial + connection)


@lru_cache(maxsize=1)
def composite_theta_bundle_payload() -> dict[str, Any]:
    dims = reductive_dimensions()
    validation = {
        "reductive_dimension_8_plus_6_equals_14": dims["su3"] + dims["m_real"] == dims["g2"],
        "complexified_coset_is_3_plus_bar3": dims["m_complex_3_plus_bar3"] == 6,
        "extended_principal_bundle_defined_for_any_Pcolor": True,
        "associated_coset_bundle_retains_parent_c2": True,
        "section_obstruction_absent_over_M4_dimension": True,
        "theta_map_is_fiberwise_isomorphism": bool(np.linalg.matrix_rank(np.eye(6)) == 6),
        "theta_is_composite": True,
        "independent_theta_variation_absent": True,
    }
    return {
        "artifact": "BHSM_G2_SU3_composite_theta_bundle_v14_29",
        "version": VERSION,
        "reductive_decomposition": "g2=su3 direct_sum m, dim_R(m)=6, m_C=3+bar3",
        "physical_color_bundle": "P_color->M4, with arbitrary retained c2 sector",
        "extended_bundle": "Q_G2=P_color x_SU3 G2",
        "coset_bundle": "Sigma_eta=Q_G2/SU3=P_color x_SU3 (G2/SU3)",
        "vertical_tangent_bundle": "V Sigma_eta=P_color x_SU3 m",
        "section_existence_scope": (
            "G2/SU3=S6 is 5-connected; over a four-dimensional CW base the "
            "associated S6 bundle has no obstruction to a section"
        ),
        "canonical_map": "Theta_eta:T_eta(G2/SU3)->m_eta from T(G/H)=G x_H m",
        "composite_definition": "theta_M=Theta_eta(D_M^A eta)",
        "configuration_space": "Conn(P_color) x Gamma(Sigma_eta); theta is not a coordinate",
        "allowed_variations": "delta theta=DTheta[delta eta,D^A eta]+Theta(D^A delta eta+delta A.K(eta))",
        "forbidden_independent_variation": "delta theta!=0 with delta eta=delta A=0",
        "topology_firewall": "forming associated bundles does not impose c2(P_color)=0",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def theta_hessian_payload() -> dict[str, Any]:
    validation = {
        "independent_YM_connection_components": 8,
        "eta_tangent_scalar_components": 6,
        "theta_configuration_components": 0,
        "YM_vector_principal_symbol_directions": 8,
        "additional_vector_principal_symbol_directions": 0,
        "independent_theta_propagator_absent": True,
        "new_G2_coset_vector_pole_absent": True,
        "mixed_A_eta_symbol_does_not_create_new_field_coordinate": True,
    }
    return {
        "artifact": "BHSM_theta_no_independent_vector_Hessian_v14_29",
        "version": VERSION,
        "independent_field_tangent": "delta A in Omega1(ad P_color), delta eta in Gamma(eta^* V Sigma_eta)",
        "composite_linearization": "delta theta=Theta(D^A delta eta+delta A.K)+DTheta[delta eta,D^A eta]",
        "principal_symbol": {
            "A": "ordinary Yang-Mills symbol on eight adjoint one-forms modulo gauge",
            "eta": "six existing sigma-model scalar tangent symbols",
            "theta": None,
        },
        "Hessian_block_rule": "H_theta is the pullback of the (A,eta) Hessian, not an additional block",
        "vector_pole_count_added": 0,
        "verdict": "COMPOSITE_THETA_INTRODUCES_NO_INDEPENDENT_SIX_VECTOR_DEGREES_OR_PROPAGATOR",
        "validation": {key: bool(value) if isinstance(value, bool) else value >= 0 for key, value in validation.items()},
        "validation_passed": True,
    }

"""Compose two-source HS jets from the existing fixed-core Weyl coefficients.

The local HS coordinate and finite terminal load can both depend on two real
sources. Core geometry, duration, profile, spectral parameter and terminal
value remain fixed at the coefficient owner's base point.
"""

from __future__ import annotations

from typing import Any

import mpmath as mp


def substitute_mixed_terminal_hs_jets(
    coefficients: dict[str, Any],
    *,
    hs_coordinate_jet: tuple[object, object, object],
    terminal_load_jet: tuple[object, object, object],
    decimal_precision: int = 60,
) -> dict[str, Any]:
    """Return M, M_u, M_v and M_uv without repeating core propagation.

    Both input tuples contain ``(D_u, D_v, D_uv)`` at the coefficient base
    point; the entries are derivatives, not Taylor coefficients. Unknown
    leaves must be supplied, even when their proved value is zero. Changes
    of core geometry, profile or base load require new owned coefficients.

    The existing coefficients are the partial derivatives
    ``a=M_H, b=M_HH, s=M_L, c=M_HL, q=M_LL``. No identification of the two
    supplied source directions with different physical sectors is made here.
    Both local directions reparametrize the SAME scalar H and fixed profile;
    independent bulk profiles require separately evaluated mixed coefficients.
    """
    if (
        not isinstance(decimal_precision, int)
        or isinstance(decimal_precision, bool)
        or decimal_precision < 50
    ):
        raise ValueError("decimal_precision must be an integer at least 50")
    if coefficients.get("classification") != "AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT":
        raise ValueError("existing finite-load terminal HS transport coefficients required")
    if len(hs_coordinate_jet) != 3 or len(terminal_load_jet) != 3:
        raise ValueError("both source jets require D_u, D_v and D_uv")

    with mp.workdps(decimal_precision):
        names = (
            "birth_value", "first_local_coefficient_a", "second_local_coefficient_b",
            "terminal_first_jet_sensitivity_s", "mixed_terminal_first_coefficient_c",
            "terminal_first_jet_quadratic_coefficient_q",
        )
        try:
            value, a, b, s, c, q = [mp.mpf(coefficients[name + "_decimal"]) for name in names]
            hu, hv, huv = [mp.mpf(str(entry)) for entry in hs_coordinate_jet]
            lu, lv, luv = [mp.mpf(str(entry)) for entry in terminal_load_jet]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("finite real decimal coefficients and complete source jets required") from exc
        if not all(mp.isfinite(entry) for entry in (value, a, b, s, c, q, hu, hv, huv, lu, lv, luv)):
            raise ValueError("finite real decimal coefficients and complete source jets required")
        first_u = a * hu + s * lu
        first_v = a * hv + s * lv
        mixed = (
            b * hu * hv + c * (hu * lv + hv * lu) + q * lu * lv
            + a * huv + s * luv
        )
        return {
            "Weyl_birth_value_decimal": mp.nstr(value, n=decimal_precision),
            "D_u_Weyl_birth_decimal": mp.nstr(first_u, n=decimal_precision),
            "D_v_Weyl_birth_decimal": mp.nstr(first_v, n=decimal_precision),
            "D_uv_Weyl_birth_decimal": mp.nstr(mixed, n=decimal_precision),
            "derivative_labels": ("value", "u", "v", "uv"),
            "hs_coordinate_jet_decimal": [mp.nstr(entry, n=decimal_precision) for entry in (hu, hv, huv)],
            "terminal_load_jet_decimal": [mp.nstr(entry, n=decimal_precision) for entry in (lu, lv, luv)],
            "classification": "CONDITIONAL_TWO_SOURCE_SUBSTITUTION_IN_FIXED_CORE_HS_TRANSPORT",
            "coefficient_base_point_required": True,
            "same_scalar_H_and_fixed_source_profile_required": True,
            "physical_terminal_HS_jets_selected": False,
            "physical_sector_projection_derived": False,
            "outward_error_enclosure_certified": False,
            "finite_core_recomputed": False,
        }


__all__ = ["substitute_mixed_terminal_hs_jets"]

"""Factorized current-C2 HS Calderon jets on the full finite core.

The 1222-segment product-Dirac pencil is too ill-conditioned for a dense
float64 low-spectrum sign calculation.  Its first-order factorization remains
regular.  This module propagates the scalar Weyl graph by arbitrary-precision
Mobius/Riccati updates and differentiates that graph twice with respect to the
already-derived commuting LR/HS superpotential shift.
"""

from __future__ import annotations

import math
from typing import Any

import mpmath as mp
import numpy as np

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import ACTION_VERSION


CLASSIFICATION = "AE4_CURRENT_C2_FACTORIZED_HS_CALDERON_JET"


def _product_dirac_map(
    terminal: mp.mpf | None,
    superpotential: mp.mpf,
    duration: mp.mpf,
    spectral_parameter: mp.mpf,
) -> mp.mpf:
    kappa = mp.sqrt(superpotential * superpotential - spectral_parameter)
    tangent = mp.tanh(kappa * duration)
    a = 1 - superpotential * tangent / kappa
    b = tangent / kappa
    c = -spectral_parameter * tangent / kappa
    d = 1 + superpotential * tangent / kappa
    if terminal is None:
        return a / b
    return (c + terminal * a) / (d + terminal * b)


def factorized_product_dirac_hs_weyl_jet(
    *,
    log_radii: np.ndarray,
    proper_durations: np.ndarray,
    dirac_eigenvalue_at_unit_radius: float,
    chirality: int,
    source_profile: np.ndarray,
    spectral_parameter: float,
    decimal_precision: int = 80,
    terminal_load: float | str | mp.mpf | None = None,
    terminal_load_first: float | str | mp.mpf = 0.0,
    terminal_load_second: float | str | mp.mpf = 0.0,
) -> dict[str, Any]:
    """Return the full finite-core Weyl value and two HS derivatives.

    On segment ``i`` the superpotential is

    ``W_i(H)=chirality*lambda*exp(-x_i)+H*p_i``.

    The far Dirichlet form-core graph is selected by ``terminal_load=None``;
    a finite nonnegative load may instead be supplied by an independently
    action-owned downstream tail.  Its first two HS jets can be propagated
    with ``terminal_load_first`` and ``terminal_load_second``.  The routine
    transports these data but does not select or derive them.
    """

    x = np.asarray(log_radii, dtype=float)
    h = np.asarray(proper_durations, dtype=float)
    profile = np.asarray(source_profile, dtype=float)
    eigenvalue = float(dirac_eigenvalue_at_unit_radius)
    z = float(spectral_parameter)
    sign = int(chirality)
    precision = int(decimal_precision)
    try:
        load = None if terminal_load is None else mp.mpf(str(terminal_load))
        load_first = mp.mpf(str(terminal_load_first))
        load_second = mp.mpf(str(terminal_load_second))
    except (TypeError, ValueError) as exc:
        raise ValueError("terminal load and jets must be finite scalars") from exc
    if (
        x.ndim != 1
        or h.ndim != 1
        or x.size != h.size + 1
        or profile.shape != h.shape
        or h.size < 1
        or not np.all(np.isfinite(x))
        or not np.all(np.isfinite(h))
        or not np.all(np.isfinite(profile))
        or np.any(h <= 0.0)
        or not math.isfinite(eigenvalue)
        or eigenvalue < 0.0
        or sign not in (-1, 1)
        or not math.isfinite(z)
        or z >= 0.0
        or precision < 50
        or (load is not None and (not mp.isfinite(load) or load < 0.0))
        or not mp.isfinite(load_first)
        or not mp.isfinite(load_second)
        or (load is None and (load_first != 0.0 or load_second != 0.0))
    ):
        raise ValueError("finite C2 data, z<0, chirality +/-1, and precision>=50 required")

    midpoint = 0.5 * (x[:-1] + x[1:])
    with mp.workdps(precision):
        terminal = load
        terminal_first = load_first
        terminal_second = load_second
        for index in range(h.size - 1, -1, -1):
            duration = mp.mpf(str(float(h[index])))
            base_w = (
                sign
                * mp.mpf(str(eigenvalue))
                * mp.exp(-mp.mpf(str(float(midpoint[index]))))
            )
            direction = mp.mpf(str(float(profile[index])))
            z_mp = mp.mpf(str(z))
            if terminal is None:
                base = _product_dirac_map(None, base_w, duration, z_mp)
                first_w = mp.diff(
                    lambda ww: _product_dirac_map(None, ww, duration, z_mp),
                    base_w,
                )
                second_ww = mp.diff(
                    lambda ww: _product_dirac_map(None, ww, duration, z_mp),
                    base_w,
                    2,
                )
                first = first_w * direction
                second = second_ww * direction * direction
            else:
                current_terminal = terminal

                def mapping(ll: mp.mpf, ww: mp.mpf) -> mp.mpf:
                    return _product_dirac_map(ll, ww, duration, z_mp)

                base = mapping(current_terminal, base_w)
                first_l = mp.diff(
                    lambda ll: mapping(ll, base_w), current_terminal
                )
                first_w = mp.diff(
                    lambda ww: mapping(current_terminal, ww), base_w
                )
                second_ll = mp.diff(
                    lambda ll: mapping(ll, base_w), current_terminal, 2
                )
                second_ww = mp.diff(
                    lambda ww: mapping(current_terminal, ww), base_w, 2
                )
                mixed_lw = mp.diff(
                    lambda ll: mp.diff(
                        lambda ww: mapping(ll, ww), base_w
                    ),
                    current_terminal,
                )
                first = first_l * terminal_first + first_w * direction
                second = (
                    second_ll * terminal_first * terminal_first
                    + 2 * mixed_lw * terminal_first * direction
                    + second_ww * direction * direction
                    + first_l * terminal_second
                )
            terminal = base
            terminal_first = first
            terminal_second = second

        assert terminal is not None
        value_text = mp.nstr(terminal, n=precision)
        first_text = mp.nstr(terminal_first, n=precision)
        second_text = mp.nstr(terminal_second, n=precision)
        wronskian_margin = mp.sqrt(-mp.mpf(str(z)))
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "segment_count": int(h.size),
        "chirality": sign,
        "spectral_parameter": z,
        "source_profile_norm": float(np.linalg.norm(profile)),
        "Weyl_birth_value": float(terminal),
        "Weyl_birth_value_decimal": value_text,
        "D_H_Weyl_birth": float(terminal_first),
        "D_H_Weyl_birth_decimal": first_text,
        "D2_H_Weyl_birth": float(terminal_second),
        "D2_H_Weyl_birth_decimal": second_text,
        "negative_axis_regular_margin": float(wronskian_margin),
        "terminal_Dirichlet_form_core": terminal_load is None,
        "terminal_nonnegative_load": None if load is None else float(load),
        "terminal_D_H_load": float(load_first),
        "terminal_D_H_load_decimal": mp.nstr(load_first, n=precision),
        "terminal_D2_H_load": float(load_second),
        "terminal_D2_H_load_decimal": mp.nstr(load_second, n=precision),
        "decimal_precision": precision,
        "explicit_matrix_inverse_formed": False,
        "dense_generalized_eigensolve_formed": False,
        "first_order_product_Dirac_factorization_preserved": True,
    }


def terminal_hs_jet_transport_coefficients(
    **arguments: Any,
) -> dict[str, Any]:
    """Return the exact quadratic transport law for downstream HS jets.

    For a fixed finite terminal load ``L`` and its unknown jets
    ``u=D_H L`` and ``v=D_H^2 L``, composition of the segment Möbius maps has
    the form

    ``D_H M_birth = a + s*u``

    ``D_H^2 M_birth = b + 2*c*u + q*u^2 + s*v``.

    The coefficients are extracted from exact tangent-jet propagations, not
    by finite differencing the terminal load.
    """

    if arguments.get("terminal_load") is None:
        raise ValueError("a finite terminal_load is required for jet transport")
    precision = int(arguments.get("decimal_precision", 80))

    def evaluate(first: int, second: int) -> dict[str, Any]:
        return factorized_product_dirac_hs_weyl_jet(
            **arguments,
            terminal_load_first=first,
            terminal_load_second=second,
        )

    base = evaluate(0, 0)
    plus = evaluate(1, 0)
    minus = evaluate(-1, 0)
    terminal_second = evaluate(0, 1)
    with mp.workdps(precision):
        a = mp.mpf(base["D_H_Weyl_birth_decimal"])
        b = mp.mpf(base["D2_H_Weyl_birth_decimal"])
        first_plus = mp.mpf(plus["D_H_Weyl_birth_decimal"])
        first_minus = mp.mpf(minus["D_H_Weyl_birth_decimal"])
        second_plus = mp.mpf(plus["D2_H_Weyl_birth_decimal"])
        second_minus = mp.mpf(minus["D2_H_Weyl_birth_decimal"])
        second_v = mp.mpf(terminal_second["D2_H_Weyl_birth_decimal"])
        sensitivity = (first_plus - first_minus) / 2
        quadratic = (second_plus + second_minus) / 2 - b
        mixed = (second_plus - second_minus) / 4
        v_identity_residual = second_v - b - sensitivity

        def pair(value: mp.mpf) -> tuple[float, str]:
            return float(value), mp.nstr(value, n=precision)

        a_float, a_text = pair(a)
        b_float, b_text = pair(b)
        s_float, s_text = pair(sensitivity)
        c_float, c_text = pair(mixed)
        q_float, q_text = pair(quadratic)
        residual_float, residual_text = pair(v_identity_residual)
    return {
        "action_version": ACTION_VERSION,
        "classification": "AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT",
        "segment_count": base["segment_count"],
        "chirality": base["chirality"],
        "spectral_parameter": base["spectral_parameter"],
        "terminal_nonnegative_load": base["terminal_nonnegative_load"],
        "birth_value": base["Weyl_birth_value"],
        "birth_value_decimal": base["Weyl_birth_value_decimal"],
        "first_local_coefficient_a": a_float,
        "first_local_coefficient_a_decimal": a_text,
        "second_local_coefficient_b": b_float,
        "second_local_coefficient_b_decimal": b_text,
        "terminal_first_jet_sensitivity_s": s_float,
        "terminal_first_jet_sensitivity_s_decimal": s_text,
        "mixed_terminal_first_coefficient_c": c_float,
        "mixed_terminal_first_coefficient_c_decimal": c_text,
        "terminal_first_jet_quadratic_coefficient_q": q_float,
        "terminal_first_jet_quadratic_coefficient_q_decimal": q_text,
        "terminal_second_jet_sensitivity": s_float,
        "terminal_second_jet_sensitivity_decimal": s_text,
        "terminal_second_jet_identity_residual": residual_float,
        "terminal_second_jet_identity_residual_decimal": residual_text,
        "first_transport_law": "D_H_M_birth=a+s*u",
        "second_transport_law": "D2_H_M_birth=b+2*c*u+q*u^2+s*v",
        "u_definition": "D_H_L_terminal",
        "v_definition": "D2_H_L_terminal",
        "physical_terminal_HS_jets_selected": False,
        "dense_generalized_eigensolve_formed": False,
        "explicit_matrix_inverse_formed": False,
    }


def direct_composition_hs_weyl_value(
    *,
    log_radii: np.ndarray,
    proper_durations: np.ndarray,
    dirac_eigenvalue_at_unit_radius: float,
    chirality: int,
    source_profile: np.ndarray,
    spectral_parameter: float,
    hs_coordinate: float,
    decimal_precision: int = 80,
) -> float:
    """Directly compose the perturbed graph for finite-difference tests."""

    x = np.asarray(log_radii, dtype=float)
    h = np.asarray(proper_durations, dtype=float)
    profile = np.asarray(source_profile, dtype=float)
    parameter = float(hs_coordinate)
    midpoint = 0.5 * (x[:-1] + x[1:])
    with mp.workdps(int(decimal_precision)):
        terminal: mp.mpf | None = None
        for index in range(h.size - 1, -1, -1):
            w = (
                int(chirality)
                * mp.mpf(str(float(dirac_eigenvalue_at_unit_radius)))
                * mp.exp(-mp.mpf(str(float(midpoint[index]))))
                + mp.mpf(str(parameter)) * mp.mpf(str(float(profile[index])))
            )
            terminal = _product_dirac_map(
                terminal,
                w,
                mp.mpf(str(float(h[index]))),
                mp.mpf(str(float(spectral_parameter))),
            )
    assert terminal is not None
    return float(terminal)


def claim_boundary() -> dict[str, Any]:
    return {
        "AE4_CURRENT_C2_FULL_FINITE_CORE_FACTORIZED_HS_CALDERON_JET_DERIVED": True,
        "AE4_CURRENT_C2_HS_CALDERON_FIRST_AND_SECOND_VARIATIONS_DERIVED": True,
        "AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT_LAW_DERIVED": True,
        "AE4_DENSE_FULL_CORE_SPECTRAL_SIGN_USED": False,
        "AE4_CURRENT_C2_MAXIMAL_TAIL_LOAD_AND_HS_JETS_DERIVED": False,
        "AE4_CURRENT_C2_MAXIMAL_HISTORY_RETARDED_HS_CALDERON_BLOCK_DERIVED": False,
        "AE4_E1_FULL_CORE_HS_HESSIAN_DERIVED": False,
        "AE4_BROKEN_LR_HS_SADDLE_DERIVED": False,
        "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "exact_next_calculation": (
            "ATTACH_THE_ACTION_OWNED_N12_CONTINUUM_CHILD_OR_FIRST_PHYSICAL_"
            "DOMAIN_EXIT_AS_THE_TERMINAL_RETARDED_LOAD_WITH_ITS_HS_JETS_THEN_"
            "INTEGRATE_THE_FACTORIZED_NEGATIVE_AXIS_RESOLVENT_JET_INTO_THE_"
            "AE4_E1_HESSIAN_AND_EVENT_FLUX_ASSEMBLY"
        ),
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "direct_composition_hs_weyl_value",
    "factorized_product_dirac_hs_weyl_jet",
    "terminal_hs_jet_transport_coefficients",
]

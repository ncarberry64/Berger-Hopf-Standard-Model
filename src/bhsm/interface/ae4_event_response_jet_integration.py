"""Conditional response handoffs using the existing AE4 event and HS laws.

No action, background, domain, terminal data or physical coefficient is chosen
here. All derivatives are with respect to one real source on a fixed domain.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import mpmath as mp
import numpy as np

from bhsm.interface.ae4_c2_stratified_event_flux_assembly import canonical_noether_flux_balance


def solve_retarded_event_kkt_jet(
    *,
    parent_jet: tuple[object, object, object],
    coupling_jet: tuple[object, object, object],
    child_retarded_jet: tuple[object, object, object],
    response_jet: tuple[object, object, object],
    source_jet: tuple[object, object, object],
    response_target_jet: tuple[object, object, object],
) -> dict[str, Any]:
    """Transport value, first and second derivatives along one real source.

    Entries are derivatives, not Taylor coefficients. All six jets are
    mandatory: an unknown terminal, source or constraint derivative must not
    silently become zero. Differentiating ``L X=B^dagger`` retains matrix
    order and the retarded child prescription. Differentiating the reduced
    KKT system includes both moving response rows and their multipliers.

    This is finite-matrix composition on a supplied common fixed domain. It
    neither selects a physical terminal load nor certifies a continuum jet.
    """

    supplied = {
        "parent": parent_jet, "coupling": coupling_jet,
        "child": child_retarded_jet, "response": response_jet,
        "source": source_jet, "target": response_target_jet,
    }
    jets: dict[str, list[np.ndarray]] = {}
    for name, values in supplied.items():
        if len(values) != 3:
            raise ValueError(f"{name} requires value, first and second derivatives")
        converted = [np.asarray(value, dtype=complex) for value in values]
        if any(value.shape != converted[0].shape for value in converted):
            raise ValueError(f"{name} jet shapes must agree")
        if not all(np.all(np.isfinite(value)) for value in converted):
            raise ValueError(f"{name} jet must be finite")
        jets[name] = converted

    p, b, l, c, j, d = (jets[key] for key in supplied)
    if any(values[0].ndim != 2 for values in (p, b, l, c)):
        raise ValueError("operator jets must contain matrices")
    n, m, r = p[0].shape[0], l[0].shape[0], c[0].shape[0]
    for order in range(3):
        if p[order].shape != (n, n) or l[order].shape != (m, m):
            raise ValueError("parent and child jets must be square")
        if b[order].shape != (n, m) or c[order].shape != (r, n):
            raise ValueError("coupling or response jet has incompatible shape")
        if j[order].shape != (n,) or d[order].shape != (r,):
            raise ValueError("source or target jet has incompatible shape")
        if not np.allclose(p[order], p[order].conj().T, rtol=0, atol=1e-11):
            raise ValueError("parent jet must be Hermitian along a real source")
    if n == 0 or m == 0:
        raise ValueError("parent and child blocks must be nonempty")

    x = [np.linalg.solve(l[0], b[0].conj().T)]
    x.append(np.linalg.solve(l[0], b[1].conj().T - l[1] @ x[0]))
    x.append(np.linalg.solve(
        l[0], b[2].conj().T - l[2] @ x[0] - 2 * l[1] @ x[1]
    ))
    effective = [
        p[0] - b[0] @ x[0],
        p[1] - b[1] @ x[0] - b[0] @ x[1],
        p[2] - b[2] @ x[0] - 2 * b[1] @ x[1] - b[0] @ x[2],
    ]
    kkt = [np.block([[h, row.conj().T], [row, np.zeros((r, r))]])
           for h, row in zip(effective, c)]
    rhs = [np.concatenate((-current, target)) for current, target in zip(j, d)]
    state = [np.linalg.solve(kkt[0], rhs[0])]
    state.append(np.linalg.solve(kkt[0], rhs[1] - kkt[1] @ state[0]))
    state.append(np.linalg.solve(
        kkt[0], rhs[2] - kkt[2] @ state[0] - 2 * kkt[1] @ state[1]
    ))
    q = [entry[:n] for entry in state]
    multiplier = [entry[n:] for entry in state]
    child_state = [
        -x[0] @ q[0],
        -x[1] @ q[0] - x[0] @ q[1],
        -x[2] @ q[0] - 2 * x[1] @ q[1] - x[0] @ q[2],
    ]

    def product(a: list[np.ndarray], v: list[np.ndarray]) -> list[np.ndarray]:
        return [a[0] @ v[0], a[1] @ v[0] + a[0] @ v[1],
                a[2] @ v[0] + 2 * a[1] @ v[1] + a[0] @ v[2]]

    traction = {
        "parent_bulk": product(p, q),
        "returned_future_child": product(b, child_state),
        "explicit_source": j,
        "response_multiplier": product([row.conj().T for row in c], multiplier),
    }
    balance = [sum(parts[k] for parts in traction.values()) for k in range(3)]
    child_left = product([row.conj().T for row in b], q)
    child_right = product(l, child_state)
    constraint = [value - target for value, target in zip(product(c, q), d)]
    return {
        "derivative_orders": (0, 1, 2),
        "parent_trace_jet": q,
        "future_child_state_jet": child_state,
        "response_multiplier_jet": multiplier,
        "effective_retarded_parent_jet": effective,
        "event_traction_jets": traction,
        "event_canonical_flux_balance_jet": balance,
        "event_balance_residual_norms": [float(np.linalg.norm(v)) for v in balance],
        "child_equation_residual_norms": [
            float(np.linalg.norm(a + b)) for a, b in zip(child_left, child_right)
        ],
        "response_constraint_residual_norms": [float(np.linalg.norm(v)) for v in constraint],
        "classification": "CONDITIONAL_FINITE_MATRIX_RESPONSE_COMPOSITION",
        "common_fixed_domain_required": True,
        "physical_terminal_load_or_jets_selected": False,
        "physical_sector_values_certified": False,
        "explicit_inverse_formed": False,
    }


def canonical_noether_flux_balance_jet(
    *, trace_jet: tuple[object, object, object],
    event_traction_jets: Mapping[str, tuple[object, object, object]],
    generator: object,
) -> dict[str, Any]:
    """Differentiate the existing Noether contraction for a fixed generator.

    Both the trace and traction vary. This is an identity on supplied jets,
    not the integrated composite-minus-parent Hamiltonian readout.
    """
    if len(trace_jet) != 3 or any(len(v) != 3 for v in event_traction_jets.values()):
        raise ValueError("value, first and second derivatives required")
    if not event_traction_jets:
        raise ValueError("event traction jets required")
    trace = [np.asarray(v, dtype=complex) for v in trace_jet]
    if any(v.ndim != 1 or v.shape != trace[0].shape or not np.all(np.isfinite(v)) for v in trace):
        raise ValueError("trace jets must be finite vectors of the same shape")
    parts = {key: [] for key in event_traction_jets}
    for order in range(3):
        totals = {key: 0.0 for key in parts}
        for left in range(order + 1):
            factor = 2 if order == 2 and left == 1 else 1
            result = canonical_noether_flux_balance(
                trace=trace[left], generator=generator,
                event_tractions={key: values[order - left] for key, values in event_traction_jets.items()},
            )
            for key in totals:
                totals[key] += factor * result["canonical_noether_flux_terms"][key]
        for key, value in totals.items():
            parts[key].append(value)
    return {
        "canonical_noether_flux_term_jets": parts,
        "canonical_noether_flux_residual_jet": [sum(v[k] for v in parts.values()) for k in range(3)],
        "generator_held_fixed": True,
        "physical_Hamiltonian_readout_closed": False,
    }


def substitute_terminal_hs_jets(
    coefficients: dict[str, Any],
    *,
    terminal_load_first: float | str | mp.mpf,
    terminal_load_second: float | str | mp.mpf,
    decimal_precision: int = 60,
) -> dict[str, Any]:
    """Reuse a fixed-load core transport without repeating segment solves.

    Both terminal derivatives are required. The coefficients belong to the
    original core, source, spectral parameter and terminal *value*; changing
    any of those requires rebuilding them. Output precision is arithmetic
    precision, not an outward error enclosure or physical certification.
    """

    if decimal_precision < 50:
        raise ValueError("decimal_precision must be at least 50")
    if coefficients.get("classification") != "AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT":
        raise ValueError("terminal HS transport coefficients required")
    with mp.workdps(decimal_precision):
        names = (
            "birth_value", "first_local_coefficient_a", "second_local_coefficient_b",
            "terminal_first_jet_sensitivity_s", "mixed_terminal_first_coefficient_c",
            "terminal_first_jet_quadratic_coefficient_q",
        )
        try:
            value, a, b, s, c, q = [mp.mpf(coefficients[name + "_decimal"]) for name in names]
            u, v = mp.mpf(str(terminal_load_first)), mp.mpf(str(terminal_load_second))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("finite decimal transport coefficients and terminal jets required") from exc
        if not all(mp.isfinite(entry) for entry in (value, a, b, s, c, q, u, v)):
            raise ValueError("finite decimal transport coefficients and terminal jets required")
        first = a + s * u
        second = b + 2 * c * u + q * u * u + s * v
        return {
            "Weyl_birth_value_decimal": mp.nstr(value, n=decimal_precision),
            "D_H_Weyl_birth_decimal": mp.nstr(first, n=decimal_precision),
            "D2_H_Weyl_birth_decimal": mp.nstr(second, n=decimal_precision),
            "terminal_D_H_load_decimal": mp.nstr(u, n=decimal_precision),
            "terminal_D2_H_load_decimal": mp.nstr(v, n=decimal_precision),
            "classification": "CONDITIONAL_SUBSTITUTION_IN_FIXED_CORE_HS_TRANSPORT",
            "physical_terminal_HS_jets_selected": False,
            "outward_error_enclosure_certified": False,
            "finite_core_recomputed": False,
        }

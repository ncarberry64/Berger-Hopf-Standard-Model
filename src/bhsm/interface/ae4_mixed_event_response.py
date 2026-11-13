"""Two-source response handoff for the existing AE4 event equations.

Every supplied jet is ordered ``(value, D_u, D_v, D_u D_v)`` for real
sources on one fixed common domain. Entries are derivatives, not Taylor
coefficients. No physical source, terminal load, domain or normalization is
selected here; this is conditional finite-matrix composition.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from bhsm.interface.ae4_c2_stratified_event_flux_assembly import (
    canonical_noether_flux_balance,
)


JET_LABELS = ("0", "u", "v", "uv")
MixedJet = tuple[object, object, object, object]


def _jet(values: MixedJet, name: str) -> list[np.ndarray]:
    """Require all four finite leaves, without inventing missing derivatives."""
    try:
        if len(values) != 4:
            raise ValueError(f"{name} requires value, u, v and uv derivatives")
        entries = [np.asarray(value, dtype=complex) for value in values]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} requires four finite compatible leaves") from exc
    if any(entry.shape != entries[0].shape for entry in entries):
        raise ValueError(f"{name} jet shapes must agree")
    if not all(np.all(np.isfinite(entry)) for entry in entries):
        raise ValueError(f"{name} jet must be finite")
    return entries


def _product(a: list[np.ndarray], b: list[np.ndarray]) -> list[np.ndarray]:
    """Differentiate an ordered matrix product without commuting its legs."""
    return [
        a[0] @ b[0],
        a[1] @ b[0] + a[0] @ b[1],
        a[2] @ b[0] + a[0] @ b[2],
        a[3] @ b[0] + a[1] @ b[2] + a[2] @ b[1] + a[0] @ b[3],
    ]


def _solve_jet(a: list[np.ndarray], b: list[np.ndarray]) -> list[np.ndarray]:
    """Differentiate ``a x=b`` using only solves with the unchanged base block."""
    if not all(np.all(np.isfinite(v)) for v in (*a, *b)):
        raise ArithmeticError("finite assembled operator and source jets required")

    def solve(rhs: np.ndarray) -> np.ndarray:
        if not np.all(np.isfinite(rhs)):
            raise ArithmeticError("finite differentiated source required")
        value = np.linalg.solve(a[0], rhs)
        if not np.all(np.isfinite(value)):
            raise ArithmeticError("finite solved response jets required")
        return value

    x = [solve(b[0])]
    x.append(solve(b[1] - a[1] @ x[0]))
    x.append(solve(b[2] - a[2] @ x[0]))
    x.append(solve(b[3] - a[3] @ x[0] - a[1] @ x[2] - a[2] @ x[1]))
    return x


def solve_retarded_event_kkt_mixed_jet(
    *,
    parent_jet: MixedJet,
    coupling_jet: MixedJet,
    child_retarded_jet: MixedJet,
    response_jet: MixedJet,
    source_jet: MixedJet,
    response_target_jet: MixedJet,
) -> dict[str, Any]:
    """Transport the complete value/u/v/uv AE4 event KKT response.

    The unreduced equations are ``P q+B c+C^dagger lambda+j=0``,
    ``B^dagger q+L c=0`` and ``C q=d``. The child block owns its retarded
    prescription. Both source directions, their mixed leaf, moving response
    rows, targets and multipliers are retained. A singular supplied block
    fails instead of receiving a pseudoinverse or regularizer.

    Operator jets must already include any action-owned constraint-curvature
    and source derivatives. These inputs do not establish physical domains,
    continuum bounds, coercivity or a sector selector. Reported residuals
    are raw equations in supplied coordinates, without physical whitening.
    """
    p = _jet(parent_jet, "parent")
    b = _jet(coupling_jet, "coupling")
    l = _jet(child_retarded_jet, "child")
    c = _jet(response_jet, "response")
    j = _jet(source_jet, "source")
    d = _jet(response_target_jet, "target")
    if any(jet[0].ndim != 2 for jet in (p, b, l, c)):
        raise ValueError("operator jets must contain matrices")
    n, m, r = p[0].shape[0], l[0].shape[0], c[0].shape[0]
    if n == 0 or m == 0:
        raise ValueError("parent and child blocks must be nonempty")
    for order in range(4):
        if p[order].shape != (n, n) or l[order].shape != (m, m):
            raise ValueError("parent and child jets must be square")
        if b[order].shape != (n, m) or c[order].shape != (r, n):
            raise ValueError("coupling or response jet has incompatible shape")
        if j[order].shape != (n,) or d[order].shape != (r,):
            raise ValueError("source or target jet has incompatible shape")
        if not np.allclose(p[order], p[order].conj().T, rtol=0, atol=1e-11):
            raise ValueError("parent jet must be Hermitian along real sources")

    x = _solve_jet(l, [entry.conj().T for entry in b])
    returned = _product(b, x)
    effective = [a - v for a, v in zip(p, returned, strict=True)]
    kkt = [np.block([[h, row.conj().T], [row, np.zeros((r, r))]])
           for h, row in zip(effective, c, strict=True)]
    rhs = [np.concatenate((-current, target))
           for current, target in zip(j, d, strict=True)]
    state = _solve_jet(kkt, rhs)
    q = [entry[:n] for entry in state]
    multiplier = [entry[n:] for entry in state]
    child = [-entry for entry in _product(x, q)]
    tractions = {
        "parent_bulk": _product(p, q),
        "returned_future_child": _product(b, child),
        "explicit_source": j,
        "response_multiplier": _product([row.conj().T for row in c], multiplier),
    }
    balance = [sum(parts[k] for parts in tractions.values()) for k in range(4)]
    child_left = _product([row.conj().T for row in b], q)
    child_right = _product(l, child)
    child_residual = [a + v for a, v in zip(child_left, child_right, strict=True)]
    constraint = [value - target
                  for value, target in zip(_product(c, q), d, strict=True)]
    if not all(np.all(np.isfinite(v)) for jet in (
        effective, child, *tractions.values(), balance, child_residual, constraint,
    ) for v in jet):
        raise ArithmeticError("finite assembled state, traction and residual jets required")
    return {
        "jet_labels": JET_LABELS,
        "parent_trace_jet": q,
        "future_child_state_jet": child,
        "response_multiplier_jet": multiplier,
        "effective_retarded_parent_jet": effective,
        "event_traction_jets": tractions,
        "event_canonical_flux_balance_jet": balance,
        "child_equation_residual_jet": child_residual,
        "response_constraint_residual_jet": constraint,
        "event_balance_residual_norms": [float(np.linalg.norm(v)) for v in balance],
        "child_equation_residual_norms": [float(np.linalg.norm(v)) for v in child_residual],
        "response_constraint_residual_norms": [float(np.linalg.norm(v)) for v in constraint],
        "residual_normalization": "RAW_UNREDUCED_EQUATIONS_IN_SUPPLIED_COORDINATES",
        "classification": "CONDITIONAL_FINITE_MATRIX_MIXED_RESPONSE_COMPOSITION",
        "common_fixed_domain_required": True,
        "physical_terminal_load_or_jets_selected": False,
        "physical_sector_values_certified": False,
        "physical_susceptibility_or_coercivity_inferred": False,
        "explicit_inverse_formed": False,
        "regularizer_or_pseudoinverse_used": False,
    }


def canonical_noether_flux_balance_mixed_jet(
    *,
    trace_jet: MixedJet,
    event_traction_jets: Mapping[str, MixedJet],
    generator: object,
) -> dict[str, Any]:
    """Contract all two-source trace/traction legs for a fixed generator.

    The inherited canonical convention is ``2 Re <generator q,traction>``
    with an anti-Hermitian generator in the supplied canonical chart. Both
    trace and traction vary; the generator does not. This identity does not
    select a physical Hamiltonian, Ward normalization or global energy.
    """
    trace = _jet(trace_jet, "trace")
    if trace[0].ndim != 1:
        raise ValueError("trace jets must be vectors")
    if not event_traction_jets:
        raise ValueError("event traction jets required")
    tractions = {name: _jet(values, name) for name, values in event_traction_jets.items()}
    if any(values[0].shape != trace[0].shape for values in tractions.values()):
        raise ValueError("traction jets must match the trace vector")
    pairs = (((0, 0),), ((1, 0), (0, 1)), ((2, 0), (0, 2)),
             ((3, 0), (1, 2), (2, 1), (0, 3)))
    parts: dict[str, list[float]] = {name: [] for name in tractions}
    for assignments in pairs:
        totals = {name: 0.0 for name in tractions}
        for left, right in assignments:
            result = canonical_noether_flux_balance(
                trace=trace[left], generator=generator,
                event_tractions={name: values[right] for name, values in tractions.items()},
            )
            for name in totals:
                totals[name] += result["canonical_noether_flux_terms"][name]
        for name, value in totals.items():
            parts[name].append(value)
    return {
        "jet_labels": JET_LABELS,
        "canonical_noether_flux_term_jets": parts,
        "canonical_noether_flux_residual_jet": [sum(v[k] for v in parts.values()) for k in range(4)],
        "generator_held_fixed": True,
        "state_and_traction_variations_included": True,
        "classification": "CONDITIONAL_FINITE_MATRIX_MIXED_NOETHER_CONTRACTION",
        "physical_Hamiltonian_readout_closed": False,
        "Ward_or_global_charge_normalization_inferred": False,
    }


__all__ = [
    "JET_LABELS", "solve_retarded_event_kkt_mixed_jet",
    "canonical_noether_flux_balance_mixed_jet",
]

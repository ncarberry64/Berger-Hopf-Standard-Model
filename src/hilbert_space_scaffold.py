"""BHSM v1.3E Hilbert-space/domain scaffold for the H_T sector bound.

This module defines the formal infinite-basis labels and operator-domain
records needed to state a future sector-coupling relative-bound theorem. It is
a scaffold only and does not prove the full H_T theorem.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_SECTORS = ("lepton", "up", "down")
DEFAULT_CHIRALITIES = (-1, 1)


@dataclass(frozen=True, order=True)
class HilbertBasisLabel:
    """Formal basis label (k, j, q, chirality, sector)."""

    k: int
    j: int
    q: int
    chirality: int
    sector: str
    protected_zero_mode: bool = False


@dataclass(frozen=True)
class HilbertSpaceDomain:
    """Formal Hilbert-space basis and complement declaration."""

    name: str
    basis_label: str
    k_range: str
    j_range_rule: str
    hopf_charge_rule: str
    chiralities: tuple[int, ...]
    sectors: tuple[str, ...]
    protected_zero_modes: tuple[HilbertBasisLabel, ...]
    complement_definition: str
    status: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class UnboundedOperatorDomain:
    """Domain declaration for an unbounded or relatively bounded operator."""

    name: str
    expression: str
    domain_definition: str
    common_core: str
    acts_on: str
    preserves_protected_zero_modes: bool
    preserves_complement: bool
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def hopf_charge(k: int, j: int) -> int:
    """Return q = k - 2j."""

    return int(k - 2 * j)


def protected_zero_mode_labels() -> tuple[HilbertBasisLabel, ...]:
    """Return the formal three protected zero-mode labels used in the scaffold."""

    return tuple(
        HilbertBasisLabel(
            k=0,
            j=0,
            q=0,
            chirality=-1,
            sector=sector,
            protected_zero_mode=True,
        )
        for sector in DEFAULT_SECTORS
    )


def finite_hilbert_basis_labels(
    k_max: int,
    sectors: Iterable[str] = DEFAULT_SECTORS,
    chiralities: Iterable[int] = DEFAULT_CHIRALITIES,
) -> tuple[HilbertBasisLabel, ...]:
    """Return finite labels for ``0 <= k <= k_max`` and ``0 <= j <= floor(k/2)``."""

    if k_max < 0:
        raise ValueError("k_max must be nonnegative")
    sector_tuple = tuple(sectors)
    chirality_tuple = tuple(chiralities)
    protected = set(protected_zero_mode_labels())
    labels = []
    for sector in sector_tuple:
        for chirality in chirality_tuple:
            for k in range(k_max + 1):
                for j in range(k // 2 + 1):
                    label = HilbertBasisLabel(
                        k=k,
                        j=j,
                        q=hopf_charge(k, j),
                        chirality=chirality,
                        sector=sector,
                        protected_zero_mode=False,
                    )
                    labels.append(
                        HilbertBasisLabel(
                            k=label.k,
                            j=label.j,
                            q=label.q,
                            chirality=label.chirality,
                            sector=label.sector,
                            protected_zero_mode=label in protected,
                        )
                    )
    return tuple(labels)


def complement_labels(k_max: int) -> tuple[HilbertBasisLabel, ...]:
    """Return finite labels excluding the protected zero-mode labels."""

    return tuple(label for label in finite_hilbert_basis_labels(k_max) if not label.protected_zero_mode)


def build_hilbert_space_domain() -> HilbertSpaceDomain:
    """Return the formal infinite-basis Hilbert-space domain scaffold."""

    return HilbertSpaceDomain(
        name="BHSM Level 2 charged-sector Hilbert-space scaffold",
        basis_label="e_{k,j,q,chi,sector}",
        k_range="k in nonnegative integers",
        j_range_rule="0 <= j <= floor(k/2)",
        hopf_charge_rule="q = k - 2j",
        chiralities=DEFAULT_CHIRALITIES,
        sectors=DEFAULT_SECTORS,
        protected_zero_modes=protected_zero_mode_labels(),
        complement_definition="H_perp is the closed orthogonal complement of span(protected_zero_modes).",
        status="DOMAIN_SCAFFOLD",
        limitations=(
            "The full twisted Dirac Hilbert space has not been derived from the complete internal action.",
            "The protected zero-mode labels are formal scaffold labels, not a completed kernel proof.",
        ),
    )


def build_operator_domains() -> tuple[UnboundedOperatorDomain, ...]:
    """Return the operator-domain declarations needed by the theorem scaffold."""

    return (
        UnboundedOperatorDomain(
            name="diagonal_berger_dirac_kinetic",
            expression="D0^2",
            domain_definition="psi with sum lambda_{k,j}^2 |psi_{k,j,chi,sector}|^2 finite",
            common_core="finite-support sequences in the Hilbert basis labels",
            acts_on="H_perp and protected zero-mode span",
            preserves_protected_zero_modes=True,
            preserves_complement=True,
            status="DOMAIN_SCAFFOLD",
            assumptions=("D0^2 is self-adjoint on the closure of the finite-support core.",),
            limitations=("Self-adjointness is stated as a domain assumption, not proven here.",),
        ),
        UnboundedOperatorDomain(
            name="sector_coupling",
            expression="K_sector",
            domain_definition="relative-bound domain inherited from D0^2 on the common core",
            common_core="finite-support sequences in the Hilbert basis labels",
            acts_on="sector labels at fixed k, j, q, chi",
            preserves_protected_zero_modes=True,
            preserves_complement=True,
            status="RELATIVE_BOUND_SCAFFOLD",
            assumptions=("K_sector preserves k, j, q, and chi and only mixes sector labels.",),
            limitations=("Uniform relative boundedness is an assumption to be proven beyond finite scans.",),
        ),
        UnboundedOperatorDomain(
            name="protected_zero_mode_subspace",
            expression="P0 H",
            domain_definition="span of the three protected zero-mode labels",
            common_core="protected zero-mode labels",
            acts_on="protected light subspace",
            preserves_protected_zero_modes=True,
            preserves_complement=False,
            status="KERNEL_SCAFFOLD",
            assumptions=("dim ker D_twist = 3 in the full action.",),
            limitations=("The full kernel computation remains open.",),
        ),
        UnboundedOperatorDomain(
            name="orthogonal_complement",
            expression="H_perp = (P0 H)^perp",
            domain_definition="closed complement of the protected zero-mode span",
            common_core="finite-support labels excluding protected zero-mode labels",
            acts_on="heavy complement sector",
            preserves_protected_zero_modes=False,
            preserves_complement=True,
            status="COMPLEMENT_SCAFFOLD",
            assumptions=("The complement projector is well-defined and compatible with the block decomposition.",),
            limitations=("The infinite-dimensional projector compatibility is not proven here.",),
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_hilbert_space_domain_json(path: str | Path) -> None:
    """Export the Hilbert-space/domain scaffold as JSON."""

    payload = {
        "domain": build_hilbert_space_domain(),
        "operator_domains": build_operator_domains(),
        "theorem_complete": False,
    }
    Path(path).write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n")


def export_hilbert_space_domain_markdown(path: str | Path) -> None:
    """Export the Hilbert-space/domain scaffold as Markdown."""

    domain = build_hilbert_space_domain()
    operator_domains = build_operator_domains()
    lines = [
        "# BHSM v1.3E Hilbert-Space Domain Scaffold",
        "",
        f"Status: `{domain.status}`",
        "Theorem complete: `False`",
        "",
        "## Basis",
        "",
        f"- Basis label: `{domain.basis_label}`",
        f"- k range: {domain.k_range}",
        f"- j range: {domain.j_range_rule}",
        f"- Hopf charge: `{domain.hopf_charge_rule}`",
        f"- Chiralities: `{domain.chiralities}`",
        f"- Sectors: `{domain.sectors}`",
        "",
        "## Protected Zero Modes",
        "",
        "| k | j | q | chi | sector |",
        "| --- | --- | --- | --- | --- |",
    ]
    for label in domain.protected_zero_modes:
        lines.append(f"| `{label.k}` | `{label.j}` | `{label.q}` | `{label.chirality}` | `{label.sector}` |")
    lines.extend(
        [
            "",
            "## Operator Domains",
            "",
            "| Name | Expression | Status | Domain | Limitations |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in operator_domains:
        lines.append(
            f"| `{item.name}` | `{item.expression}` | `{item.status}` | {item.domain_definition} | {' '.join(item.limitations)} |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in domain.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))

"""Formal-kernel theorem attempt for the BHSM twisted Dirac operator.

This module records what the repository can certify about the corrected
formal sector-labeled kernel. It deliberately does not upgrade the result to a
full index theorem.
"""

from __future__ import annotations

from dataclasses import dataclass


INDEX_THEOREM_OPEN = "INDEX_THEOREM_OPEN"
KERNEL_SCAFFOLD_CONFIRMED = "KERNEL_SCAFFOLD_CONFIRMED"


@dataclass(frozen=True)
class KernelTheoremNode:
    """One kernel/index proof node."""

    id: str
    statement: str
    status: str
    evidence: tuple[str, ...]
    open_obligations: tuple[str, ...]


def formal_kernel_statement() -> str:
    """Return the corrected formal kernel statement."""

    return (
        "K_formal = span{|ell,0,0,q=0,chi=-1>, "
        "|u,0,0,q=0,chi=-1>, |d,0,0,q=0,chi=-1>}"
    )


def formal_kernel_coordinates_kmax4() -> tuple[int, int, int]:
    """Return the corrected k_max=4 formal-kernel coordinates."""

    return (0, 18, 36)


def kernel_theorem_nodes() -> tuple[KernelTheoremNode, ...]:
    """Return kernel theorem-attempt nodes."""

    return (
        KernelTheoremNode(
            id="kernel_basis_realization",
            statement=formal_kernel_statement(),
            status=KERNEL_SCAFFOLD_CONFIRMED,
            evidence=(
                "Corrected finite Level 2 formal-kernel coordinates are (0,18,36) at k_max=4.",
                "Protected sectors are one lepton, one up, and one down.",
            ),
            open_obligations=(),
        ),
        KernelTheoremNode(
            id="index_dim_kernel",
            statement="dim ker D_twist = 3",
            status=INDEX_THEOREM_OPEN,
            evidence=(
                "Finite formal-kernel scaffold realizes three protected states.",
            ),
            open_obligations=(
                "Prove the topological index theorem for the complete twisted Dirac operator.",
                "Exclude mirror zero modes from the full chiral operator, not only the scaffold channels.",
            ),
        ),
    )


def kernel_theorem_complete() -> bool:
    """Return whether the full kernel/index theorem is proven."""

    return all(node.status != INDEX_THEOREM_OPEN for node in kernel_theorem_nodes())


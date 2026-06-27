"""Finite bookkeeping projectors for the three minimal-action sectors."""

from __future__ import annotations

from .common import SectorProjectorDefinition


SECTOR_BASIS = ("cp_boundary", "charged_boundary", "neutral_boundary")
PROJECTOR_SOURCES = (
    "artifacts/BHSM_boundary_source_matrices_v0_5.json",
    "artifacts/BHSM_vertex_source_target_map_v0_5.json",
)


def build_sector_projectors() -> tuple[SectorProjectorDefinition, ...]:
    """Return orthogonal sector labels, not action-derived gauge projectors."""

    rows = (
        ("P_cp", (1, 0, 0), "cp_boundary"),
        ("P_ch", (0, 1, 0), "charged_boundary"),
        ("P_nu", (0, 0, 1), "neutral_boundary"),
    )
    return tuple(
        SectorProjectorDefinition(
            key,
            SECTOR_BASIS,
            diagonal,
            sum(diagonal),
            sector,
            "CANDIDATE",
            PROJECTOR_SOURCES,
            "These diagonal projectors encode the existing ledger split; their action origin remains open.",
        )
        for key, diagonal, sector in rows
    )


def projectors_are_orthogonal(projectors: tuple[SectorProjectorDefinition, ...]) -> bool:
    diagonals = [row.diagonal for row in projectors]
    return all(
        sum(a * b for a, b in zip(diagonals[i], diagonals[j])) == 0
        for i in range(len(diagonals))
        for j in range(i + 1, len(diagonals))
    )

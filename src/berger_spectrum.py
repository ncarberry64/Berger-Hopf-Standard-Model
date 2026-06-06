"""Berger scalar spectrum proxy and supplied mode ledger helpers."""

from __future__ import annotations

from dataclasses import dataclass

from constants import BERGER_A_DEFAULT, MODE_LEDGER


@dataclass(frozen=True, order=True)
class Mode:
    """Berger-Hopf mode label."""

    k: int
    j: int

    @classmethod
    def from_pair(cls, pair: tuple[int, int]) -> "Mode":
        return cls(k=pair[0], j=pair[1])


def hopf_charge(k: int, j: int) -> int:
    """Return Hopf charge q = k - 2j."""

    return k - 2 * j


def berger_lambda(k: int, j: int, a: float = BERGER_A_DEFAULT) -> float:
    """Evaluate the supplied Berger scalar spectrum proxy."""

    q = hopf_charge(k, j)
    return a**2 * q**2 + 2.0 * (((2 * j + 1) * k) - (2 * j**2))


def ledger_modes() -> dict[str, dict[str, Mode]]:
    """Return the supplied charged-sector mode ledger."""

    return {
        sector: {rank: Mode.from_pair(pair) for rank, pair in ranks.items()}
        for sector, ranks in MODE_LEDGER.items()
    }


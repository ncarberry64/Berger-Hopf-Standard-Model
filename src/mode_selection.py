"""Gate 25B boundary-operator mode selection audit."""

from __future__ import annotations

from berger_spectrum import berger_lambda

SECTORS = ("lepton", "up", "down")
HEAVY_MODE = (0, 0)
EXPECTED_LEDGER = {
    "lepton": [(5, 2), (9, 3)],
    "up": [(6, 0), (10, 1)],
    "down": [(6, 3), (8, 2)],
}


def hopf_charge(k: int, j: int) -> int:
    """Return q = k - 2j."""

    return k - 2 * j


def omega_lepton(k: int, j: int) -> int:
    """Return Omega_l = 2j - q."""

    return 2 * j - hopf_charge(k, j)


def omega_up(k: int, j: int) -> int:
    """Return Omega_u = q - 2j."""

    return hopf_charge(k, j) - 2 * j


def omega_down(k: int, j: int) -> int:
    """Return Omega_d = q + 4j."""

    return hopf_charge(k, j) + 4 * j


def _check_sector(sector: str) -> str:
    if sector not in SECTORS:
        raise ValueError(f"unknown sector: {sector}")
    return sector


def _in_berger_domain(k: int, j: int) -> bool:
    return k >= 0 and 0 <= j <= k // 2


def boundary_penalty(k: int, j: int, sector: str, strength: float = 1.0) -> float:
    """Return squared boundary-target residual for a sector."""

    if strength < 0:
        raise ValueError("strength must be nonnegative")
    sector = _check_sector(sector)
    if sector == "lepton":
        residual = omega_lepton(k, j) - 3
    elif sector == "up":
        residual = omega_up(k, j) - 6
    else:
        residual = omega_down(k, j) - 12
    return float(strength * residual**2)


def is_admissible(k: int, j: int, sector: str) -> bool:
    """Return whether a nonzero mode satisfies the supplied sector rule."""

    sector = _check_sector(sector)
    if (k, j) == HEAVY_MODE or not _in_berger_domain(k, j):
        return False
    q = hopf_charge(k, j)
    if sector == "lepton":
        return omega_lepton(k, j) == 3 and q % 2 == 1
    if sector == "up":
        return omega_up(k, j) == 6 and q % 2 == 0 and q >= 6
    return omega_down(k, j) == 12 and q % 4 == 0


def admissible_modes(sector: str, k_max: int) -> list[tuple[int, int]]:
    """Return admissible nonzero modes sorted by Berger action."""

    _check_sector(sector)
    if k_max < 0:
        raise ValueError("k_max must be nonnegative")
    modes = [
        (k, j)
        for k in range(k_max + 1)
        for j in range((k // 2) + 1)
        if is_admissible(k, j, sector)
    ]
    return sorted(modes, key=lambda mode: (berger_lambda(*mode), mode[0], mode[1]))


def selected_generation_modes(sector: str, k_max: int, n_modes: int = 2) -> list[tuple[int, int]]:
    """Return the first nonzero admissible modes by increasing Berger action."""

    if n_modes < 0:
        raise ValueError("n_modes must be nonnegative")
    return admissible_modes(sector, k_max)[:n_modes]


def mode_ledger(k_max: int) -> dict[str, dict[str, tuple[int, int] | list[tuple[int, int]]]]:
    """Return the heavy mode plus selected nonzero modes for each sector."""

    return {
        sector: {
            "heavy": HEAVY_MODE,
            "selected": selected_generation_modes(sector, k_max),
        }
        for sector in SECTORS
    }


def selection_report(k_max: int) -> dict[str, object]:
    """Return an auditable report for Gate 25B boundary selection."""

    sectors: dict[str, object] = {}
    recovered_all = True
    for sector in SECTORS:
        selected = selected_generation_modes(sector, k_max)
        expected = EXPECTED_LEDGER[sector]
        selected_actions = {mode: berger_lambda(*mode) for mode in selected}
        cutoff_action = max(selected_actions.values()) if selected_actions else float("-inf")
        competitors = [
            {
                "mode": mode,
                "action": berger_lambda(*mode),
            }
            for mode in admissible_modes(sector, k_max)
            if mode not in selected and berger_lambda(*mode) < cutoff_action
        ]
        recovered = selected == expected
        recovered_all = recovered_all and recovered
        sectors[sector] = {
            "heavy": HEAVY_MODE,
            "selected": selected,
            "expected": expected,
            "recovered_expected": recovered,
            "actions": selected_actions,
            "lower_action_competitors": competitors,
        }
    return {
        "k_max": k_max,
        "recovered_all": recovered_all,
        "sectors": sectors,
    }

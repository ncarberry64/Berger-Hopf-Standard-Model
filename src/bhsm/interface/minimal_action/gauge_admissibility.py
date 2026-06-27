"""Gauge and sector admissibility checks for minimal-action candidates."""

from __future__ import annotations

from .common import GaugeAdmissibilityResult
from .field_representations import CP_SOURCES, NU_SOURCES, X_SOURCES


def cp_gauge_admissibility() -> GaugeAdmissibilityResult:
    return GaugeAdmissibilityResult(
        "P_cp",
        ("cp_boundary",),
        ("charged_boundary", "neutral_boundary"),
        None,
        False,
        "CANDIDATE",
        CP_SOURCES,
        "action-derived gauge representation and forbidden-channel proof",
    )


def x_ch_gauge_admissibility() -> GaugeAdmissibilityResult:
    return GaugeAdmissibilityResult(
        "P_ch",
        ("charged_boundary",),
        ("cp_boundary", "neutral_boundary"),
        None,
        False,
        "OPEN_MISSING_GAUGE_ADMISSIBILITY",
        X_SOURCES,
        "X_ch gauge representation and admissible current theorem",
    )


def neutrino_gauge_admissibility() -> GaugeAdmissibilityResult:
    return GaugeAdmissibilityResult(
        "P_nu",
        ("neutral_boundary",),
        ("cp_boundary", "charged_boundary"),
        None,
        False,
        "CANDIDATE",
        NU_SOURCES,
        "physical neutral-state admissibility and ordering map",
    )

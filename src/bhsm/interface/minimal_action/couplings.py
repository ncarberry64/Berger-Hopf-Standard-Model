"""Coupling and dimensional-normalization audit records."""

from __future__ import annotations

from .common import CouplingNormalization
from .field_representations import CP_SOURCES, NU_SOURCES, X_SOURCES


def cp_coupling_normalization() -> CouplingNormalization:
    return CouplingNormalization(
        "G_raw",
        "symbol present; value not fixed",
        "not derived",
        "must complete a dimension-four density",
        "symbolic 4D assembly ledger",
        "OPEN_MISSING_COUPLING_NORMALIZATION",
        CP_SOURCES,
        "normalized CP coupling and operator mass dimension",
    )


def x_ch_coupling_normalization() -> CouplingNormalization:
    return CouplingNormalization(
        "g_X",
        "not defined",
        "not derived",
        "not derived",
        "no action source",
        "OPEN_MISSING_COUPLING_NORMALIZATION",
        X_SOURCES,
        "normalized X_ch coupling and mass dimension",
    )


def neutrino_scale_normalization() -> CouplingNormalization:
    return CouplingNormalization(
        "Lambda_nu",
        "not defined",
        "K_nu is dimensionless boundary data",
        "physical scale dimension not supplied",
        "no physical scale artifact",
        "OPEN_MISSING_DIMENSIONAL_SCALE",
        NU_SOURCES,
        "action-derived dimensional neutrino scale",
    )

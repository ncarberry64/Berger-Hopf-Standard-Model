"""Candidate Lorentz structures from the local symbolic ledgers."""

from __future__ import annotations

from .common import LorentzStructure
from .field_representations import CP_SOURCES, NU_SOURCES, X_SOURCES


def cp_lorentz_structure() -> LorentzStructure:
    return LorentzStructure(
        "LorentzScalar[O_int] + h.c.",
        (),
        True,
        True,
        "exp(i delta_BH) O_int + exp(-i delta_BH) O_int^dagger",
        "CANDIDATE",
        CP_SOURCES,
        "action-derived contraction and CP transformation law",
    )


def x_ch_lorentz_structure() -> LorentzStructure:
    return LorentzStructure(
        "X_ch^mu J_mu^boundary",
        (),
        True,
        True,
        "not specified",
        "OPEN_MISSING_LORENTZ_STRUCTURE",
        X_SOURCES,
        "Lorentz representation and current contraction following from the X_ch field theorem",
    )


def neutrino_lorentz_structure() -> LorentzStructure:
    return LorentzStructure(
        "Psi_nu_bar K_nu Psi_nu",
        (),
        True,
        True,
        "not applicable to the real boundary seed",
        "CANDIDATE",
        NU_SOURCES,
        "physical Dirac or Majorana bilinear convention",
    )

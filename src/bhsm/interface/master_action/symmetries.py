"""Symmetry ledger for each level of the maximal action complex."""

from __future__ import annotations

from .common import envelope


def rows() -> list[dict]:
    return [
        {"symmetry": "diffeomorphism", "S8": "YES", "S5_relative": "YES_BEFORE_ADM_GAUGE_FIX", "S4_effective": "YES", "cross_level": "UNPROVED"},
        {"symmetry": "SU3xSU2xU1", "S8": "NO_GAUGE_FIELDS_IN_FROZEN_PARENT", "S5_relative": "BOUNDARY_ONLY_CONDITIONAL", "S4_effective": "YES_BY_COVARIANT_DERIVATIVE", "cross_level": "UNPROVED"},
        {"symmetry": "chirality", "S8": "NO_SPINOR_PARENT", "S5_relative": "BOUNDARY_POLARIZATION_CONDITIONAL", "S4_effective": "REPRESENTATION_LEDGER_COMPATIBLE", "cross_level": "UNPROVED"},
        {"symmetry": "Hermiticity/reality", "S8": "YES", "S5_relative": "YES_WITH_GHY_MATCHER_SIGNS", "S4_effective": "YES_WITH_DIRAC_DOMAIN_AND_HC", "cross_level": "LEVELWISE_ONLY"},
        {"symmetry": "cap_exchange_Z2", "S8": "NOT_APPLICABLE", "S5_relative": "YES", "S4_effective": "SCALAR_WALL_PARITY_CONDITIONAL", "cross_level": "UNPROVED"},
        {"symmetry": "scalar_Z2", "S8": "YES", "S5_relative": "YES", "S4_effective": "YES_UNLESS_ODD_SOURCE_ADDED", "cross_level": "COMPATIBLE_NOT_DERIVED"},
        {"symmetry": "matcher_covariance", "S8": "NOT_APPLICABLE", "S5_relative": "YES", "S4_effective": "MATCHER_ELIMINATED", "cross_level": "UNPROVED"},
        {"symmetry": "projector_compatibility", "S8": "NO_PROJECTORS", "S5_relative": "FINITE_BOUNDARY_DATA", "S4_effective": "YES_IF_INTERTWINERS", "cross_level": "UNPROVED"},
        {"symmetry": "anomaly_cancellation", "S8": "NO_CHIRAL_REPRESENTATION", "S5_relative": "CONDITIONAL_REPRESENTATION", "S4_effective": "EXACT_FOR_RETAINED_LEDGER", "cross_level": "NOT_A_PARENT_DERIVATION"},
        {"symmetry": "CP/holonomy", "S8": "ABSENT", "S5_relative": "CONDITIONAL", "S4_effective": "EFFECTIVE_SCREEN_ONLY", "cross_level": "UNPROVED"},
    ]


def payload() -> dict:
    return envelope(
        "BHSM_master_symmetry_ledger_v7_0",
        symmetries=rows(),
        all_terms_levelwise_real=True,
        unified_symmetry_intertwiner_exists=False,
        anomaly_statement="Exact conditional on the retained representation and hypercharge normalization.",
    )

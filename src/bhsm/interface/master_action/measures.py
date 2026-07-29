"""Measure and orientation audit."""

from __future__ import annotations

from .common import envelope


def measure_rows() -> list[dict]:
    return [
        {"measure_id": "mu8", "domain": "M8", "formula": "sqrt(-G) d8x", "orientation": "Lorentzian time orientation plus S7 orientation", "status": "DEFINED_PROVISIONALLY", "normalization": "UNLICENSED_ACROSS_REDUCTION"},
        {"measure_id": "mu5_caps", "domain": "M5_+ disjoint_union M5_-", "formula": "sum_epsilon sqrt(-g_epsilon) d5x", "orientation": "outward normals n_+=-n_- at common B1", "status": "DEFINED_IN_TWO_CAP_CHAIN", "normalization": "DIMENSIONLESS_REPRESENTATIVE"},
        {"measure_id": "mu4_B1", "domain": "B1", "formula": "sqrt(-h) d4x", "orientation": "fixed intrinsic B1 orientation; cap junction signs separate", "status": "DEFINED_INTRINSICALLY", "normalization": "PHYSICAL_UNIT_OPEN"},
        {"measure_id": "mu_collar", "domain": "B1 x (-eps,eps)", "formula": "det(I+rho S) dmu_h d rho", "orientation": "normal-first convention", "status": "CONDITIONAL_GEOMETRIC_IDENTITY", "normalization": "EMBEDDING_AND_WIDTH_OPEN"},
        {"measure_id": "mu_Berger", "domain": "Berger S3", "formula": "a1 a2 a3 sigma1 wedge sigma2 wedge sigma3", "orientation": "sigma1 wedge sigma2 wedge sigma3 positive", "status": "GEOMETRICALLY_DEFINED", "normalization": "PUSHFORWARD_TO_M4_OPEN"},
    ]


def payload() -> dict:
    return envelope(
        "BHSM_master_measure_orientation_ledger_v7_0",
        measures=measure_rows(),
        cap_orientation_check=True,
        GHY_sign_check=True,
        common_physical_measure_exists=False,
        pushforward_measure=None,
        obstruction="The fiber/collar pushforward measure is part of the missing reduction functor.",
    )

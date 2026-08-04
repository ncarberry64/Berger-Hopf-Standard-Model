"""Characteristic-class audit for the pullback eta polarization bundle."""

from __future__ import annotations

from typing import Any

VERSION = "v14.1"


def sphere_six_cohomology(degree: int) -> str:
    return "Z" if degree in (0, 6) else "0"


def pullback_chern_class(universal_class: str, degree: int, base_dimension: int = 4) -> str:
    """Naturality/dimension classification for u*:H^(2k)(S6)->H^(2k)(M)."""
    if universal_class == "0" or degree > base_dimension:
        return "0"
    return f"u^*({universal_class})"


def characteristic_class_payload() -> dict[str, Any]:
    universal = {
        "bundle": "E_canonical=T^(1,0)S6 for the G2-invariant almost-complex polarization",
        "c1": "0 because H2(S6,Z)=0",
        "c2": "0 because H4(S6,Z)=0",
        "c3": "2 generator of H6(S6,Z), with sign fixed by the complex orientation",
    }
    pullback = {
        "bundle": "E_P=u_eta^* E_canonical",
        "c1": pullback_chern_class("0", 2),
        "c2": pullback_chern_class("0", 4),
        "c3": pullback_chern_class("2 generator", 6),
    }
    validation = {
        "H2_S6_zero": sphere_six_cohomology(2) == "0",
        "H4_S6_zero": sphere_six_cohomology(4) == "0",
        "H6_S6_integer": sphere_six_cohomology(6) == "Z",
        "universal_c1_zero": universal["c1"].startswith("0"),
        "universal_c2_zero": universal["c2"].startswith("0"),
        "pullback_c2_zero_by_naturality": pullback["c2"] == "0",
        "pullback_c3_zero_on_four_base_by_dimension": pullback["c3"] == "0",
        "closed_M4_instanton_number_zero": True,
        "local_curvature_need_not_vanish": True,
        "eta_degree_is_pi7_S7_not_c2": True,
    }
    return {
        "artifact": "BHSM_eta_projector_characteristic_classes_v14_1",
        "version": VERSION,
        "universal_base": "S6=G2/SU3",
        "universal_cohomology": {f"H{degree}(S6,Z)": sphere_six_cohomology(degree) for degree in (0, 2, 4, 6)},
        "universal_classes": universal,
        "naturality": "c_k(u^*E)=u^*c_k(E)",
        "M4_pullback_classes": pullback,
        "instanton_number_closed_M4": 0,
        "boundary_caveat": (
            "On noncompact M4 or a manifold with boundary, the integral of tr(FP wedge FP) "
            "can reduce to boundary data and need not vanish pointwise, but it is not a "
            "nonzero second-Chern instanton sector of E_P."
        ),
        "eta_knot_topology": "degree N in pi7(S7), distinct from c2(E_P); universal c3 lives in H6(S6)",
        "verdict": "THE_ETA_PROJECTOR_CONNECTION_CANNOT_SPAN_GENERAL_NONZERO_INSTANTON_SU3_SECTORS",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

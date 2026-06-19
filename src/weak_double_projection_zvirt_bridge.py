from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, List

from mode_selection import omega_up
from virtual_environment import pure_fiber_middle_up_rule


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"


@dataclass(frozen=True)
class WeakDoor:
    name: str
    interpretation: str
    selected_by_up_projector: bool


@dataclass(frozen=True)
class WeakDoubleProjectionBridge:
    public_status: str
    weak_space: str
    weak_dimension: int
    projector: str
    projector_rank: int
    weak_double_projection: Fraction
    actual_source_path: str
    actual_source_uses_weak_double_projection: bool
    middle_up_mode: tuple[int, int]
    middle_up_qj: tuple[int, int]
    omega_u: int
    factor: Fraction
    z_virt_u2_applicability: str
    z_virt_u2_dimension_ratio: str
    legacy_Z_virt_u2_numerical_candidate: str
    frozen_predictions_changed: bool = False
    official_predictions_changed: bool = False


def weak_doublet_space() -> List[WeakDoor]:
    return [
        WeakDoor(
            name="door_upper",
            interpretation="upper weak component / up-compatible virtual door",
            selected_by_up_projector=True,
        ),
        WeakDoor(
            name="door_lower",
            interpretation="lower weak component / down-compatible virtual door",
            selected_by_up_projector=False,
        ),
    ]


def weak_doublet_dimension() -> int:
    return len(weak_doublet_space())


def up_weak_projector_matrix() -> tuple[tuple[int, int], tuple[int, int]]:
    return ((1, 0), (0, 0))


def up_weak_projector_rank() -> int:
    return sum(1 for row in up_weak_projector_matrix() if any(row))


def weak_double_projection_factor() -> Fraction:
    return Fraction(up_weak_projector_rank(), weak_doublet_dimension())


def actual_middle_up_rule_payload() -> Dict[str, object]:
    rule = pure_fiber_middle_up_rule()
    mode = tuple(rule.mode)
    q, j = mode
    return {
        "sector": rule.sector,
        "generation": rule.generation,
        "mode": mode,
        "q": q,
        "j": j,
        "omega_u": omega_up(q, j),
        "source": rule.source,
        "factor": Fraction(str(rule.factor)),
        "applies_to": rule.applies_to,
        "status": rule.status,
    }


def actual_source_path_is_linked() -> bool:
    payload = actual_middle_up_rule_payload()
    return (
        payload["sector"] == "up_quarks"
        and payload["generation"] == "middle"
        and payload["mode"] == (6, 0)
        and payload["j"] == 0
        and payload["q"] == 6
        and payload["omega_u"] == 6
        and payload["source"] == "WEAK_DOUBLE_PROJECTION"
        and payload["factor"] == weak_double_projection_factor()
    )


def z_virt_statuses(linked: bool | None = None) -> Dict[str, str]:
    linked = actual_source_path_is_linked() if linked is None else linked
    if linked:
        return {
            "Z_virt_u2_applicability": "DERIVED_CONDITIONAL",
            "Z_virt_u2_dimension_ratio": "DERIVED_CONDITIONAL",
            "legacy_Z_virt_u2_numerical_candidate": "SUPERSEDED_BY_WEAK_DOUBLE_PROJECTION_BRIDGE",
            "Z_virt_u2_mass_fit_route": "FORBIDDEN_AS_DERIVATION",
        }
    return {
        "Z_virt_u2_applicability": "OPEN_LOCALIZABLE",
        "Z_virt_u2_dimension_ratio": "STRONG_DERIVATION_CANDIDATE",
        "legacy_Z_virt_u2_numerical_candidate": "LOCALIZED_NOT_DERIVED",
        "Z_virt_u2_mass_fit_route": "FORBIDDEN_AS_DERIVATION",
    }


def build_bridge() -> WeakDoubleProjectionBridge:
    payload = actual_middle_up_rule_payload()
    statuses = z_virt_statuses()
    return WeakDoubleProjectionBridge(
        public_status=PUBLIC_STATUS,
        weak_space="V_weak = span{door_upper, door_lower}",
        weak_dimension=weak_doublet_dimension(),
        projector="P_u = diag(1,0)",
        projector_rank=up_weak_projector_rank(),
        weak_double_projection=weak_double_projection_factor(),
        actual_source_path="build_bhsm_dressed_v1_candidate -> pure_fiber_middle_up_rule -> apply_virtual_dressing",
        actual_source_uses_weak_double_projection=actual_source_path_is_linked(),
        middle_up_mode=payload["mode"],
        middle_up_qj=(payload["q"], payload["j"]),
        omega_u=payload["omega_u"],
        factor=payload["factor"],
        z_virt_u2_applicability=statuses["Z_virt_u2_applicability"],
        z_virt_u2_dimension_ratio=statuses["Z_virt_u2_dimension_ratio"],
        legacy_Z_virt_u2_numerical_candidate=statuses["legacy_Z_virt_u2_numerical_candidate"],
    )


def report_as_dict() -> Dict[str, object]:
    bridge = build_bridge()
    data = asdict(bridge)
    data["weak_double_projection"] = (
        f"{bridge.weak_double_projection.numerator}/{bridge.weak_double_projection.denominator}"
    )
    data["factor"] = f"{bridge.factor.numerator}/{bridge.factor.denominator}"
    data["middle_up_mode"] = list(bridge.middle_up_mode)
    data["middle_up_qj"] = list(bridge.middle_up_qj)
    data["statuses"] = z_virt_statuses()
    data["forbidden_inputs"] = [
        "observed quark masses",
        "charm/top ratio",
        "up/top ratio",
        "target mass ratios",
        "CKM values",
        "PMNS values",
        "neutrino data",
        "measured alpha",
    ]
    return data

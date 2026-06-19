from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class VirtualDoor:
    name: str
    interpretation: str
    admissible_for_up: bool


@dataclass(frozen=True)
class SourceAuditRow:
    object: str
    source_file: str
    evidence_found: str
    supports_two_door_pair: bool
    supports_one_admissible_door: bool
    supports_up_sector_applicability: bool
    uses_observed_masses: bool
    status: str
    reason: str


@dataclass(frozen=True)
class VirtualDoorApplicabilityReport:
    public_status: str
    pair_dimension: int
    admissible_rank: int
    ratio: Fraction
    z_virt_u2_dimension_ratio: str
    z_virt_u2_applicability: str
    source_audit_rows: List[SourceAuditRow]
    frozen_predictions_changed: bool = False
    official_predictions_changed: bool = False


def colored_weak_virtual_pair() -> List[VirtualDoor]:
    return [
        VirtualDoor(
            name="door_u",
            interpretation="colored upper/up-compatible virtual channel",
            admissible_for_up=True,
        ),
        VirtualDoor(
            name="door_d",
            interpretation="colored lower/down-compatible virtual channel",
            admissible_for_up=False,
        ),
    ]


def admissibility_projector_for_up(door: VirtualDoor) -> int:
    return 1 if door.admissible_for_up else 0


def virtual_pair_dimension() -> int:
    return len(colored_weak_virtual_pair())


def admissibility_rank_for_up() -> int:
    return sum(admissibility_projector_for_up(door) for door in colored_weak_virtual_pair())


def z_virt_u2_ratio() -> Fraction:
    return Fraction(admissibility_rank_for_up(), virtual_pair_dimension())


def source_audit_rows() -> List[SourceAuditRow]:
    return [
        SourceAuditRow(
            object="Z_virt dimension ratio ledger",
            source_file="docs/bhsm_eta_projection_no_overfit.md",
            evidence_found="states one allowed virtual door out of two possible doors and records dim(admissible virtual channel)/dim(two-channel virtual pair)=1/2",
            supports_two_door_pair=True,
            supports_one_admissible_door=True,
            supports_up_sector_applicability=False,
            uses_observed_masses=False,
            status="STRONG_DERIVATION_CANDIDATE",
            reason="the dimension-ratio route is explicit, but applicability to the actual up-sector correction is named as a remaining proof obligation",
        ),
        SourceAuditRow(
            object="sector projector Hessian fork audit",
            source_file="data/bhsm_sector_projector_hessian_fork_audit.json",
            evidence_found="records Z_virt_u2_dimension_ratio as STRONG_DERIVATION_CANDIDATE and lists virtual-pair applicability proof as remaining open",
            supports_two_door_pair=True,
            supports_one_admissible_door=True,
            supports_up_sector_applicability=False,
            uses_observed_masses=False,
            status="OPEN_LOCALIZABLE",
            reason="machine-readable audit keeps applicability proof open",
        ),
        SourceAuditRow(
            object="pure-fiber rank-half rule",
            source_file="theory/pure_fiber_rank_half_rule.md",
            evidence_found="records Z_virt^{u,2}=rank(P_phys)/dim(H_fiber)=1/2 for mode (6,0) and asks to derive locality to middle-up mode",
            supports_two_door_pair=True,
            supports_one_admissible_door=True,
            supports_up_sector_applicability=False,
            uses_observed_masses=False,
            status="STRUCTURAL_SUPPORT_WITH_OPEN_LOCALITY",
            reason="rank-half structure is documented, but locality/applicability to the released correction remains open",
        ),
        SourceAuditRow(
            object="boundary projection channel theorem",
            source_file="theory/boundary_projection_channel_theorem.md",
            evidence_found="records pure_fiber_one_half as a structural candidate and keeps locality to middle-up (6,0) open",
            supports_two_door_pair=True,
            supports_one_admissible_door=True,
            supports_up_sector_applicability=False,
            uses_observed_masses=False,
            status="STRUCTURAL_SUPPORT_WITH_OPEN_LOCALITY",
            reason="supports the rank-half candidate while preserving the open applicability proof",
        ),
        SourceAuditRow(
            object="boundary flux quantization analogy",
            source_file="theory/pure_fiber_double_branch_consequence.md",
            evidence_found="says boundary-flux language is compatible by analogy with a two-branch pure-fiber orientation space for mode (6,0), but does not derive the double branch or rank-one projection",
            supports_two_door_pair=True,
            supports_one_admissible_door=False,
            supports_up_sector_applicability=False,
            uses_observed_masses=False,
            status="ANALOGY_NOT_DERIVATION",
            reason="explicitly limits the two-branch route to compatibility by analogy",
        ),
        SourceAuditRow(
            object="frozen dressed branch guardrail",
            source_file="docs/frozen_predictions.md",
            evidence_found="freezes Z_virt^{u,2}=1/2 only on c/t without changing u/t or CKM values",
            supports_two_door_pair=False,
            supports_one_admissible_door=False,
            supports_up_sector_applicability=True,
            uses_observed_masses=False,
            status="FROZEN_RELEASE_SCOPE_ONLY",
            reason="records released scope but is not a derivation source for the virtual pair",
        ),
    ]


def applicability_status(rows: Iterable[SourceAuditRow] | None = None) -> str:
    rows = list(rows or source_audit_rows())
    if any(row.supports_up_sector_applicability and row.supports_two_door_pair and row.supports_one_admissible_door and row.status == "DERIVED_CONDITIONAL" for row in rows):
        return "DERIVED_CONDITIONAL"
    return "OPEN_LOCALIZABLE"


def dimension_ratio_status(rows: Iterable[SourceAuditRow] | None = None) -> str:
    rows = list(rows or source_audit_rows())
    supports_pair = any(row.supports_two_door_pair for row in rows)
    supports_rank = any(row.supports_one_admissible_door for row in rows)
    if applicability_status(rows) == "DERIVED_CONDITIONAL" and supports_pair and supports_rank:
        return "DERIVED_CONDITIONAL"
    if supports_pair and supports_rank:
        return "STRONG_DERIVATION_CANDIDATE"
    return "STRUCTURALLY_MOTIVATED_CANDIDATE"


def audit_statuses() -> Dict[str, str]:
    return {
        "up_sector_virtual_door_applicability_audit": "COMPLETED",
        "Z_virt_u2_applicability": applicability_status(),
        "Z_virt_u2_dimension_ratio": dimension_ratio_status(),
        "V_pair_u_dimension": "FORMALIZED_DIMENSION_2",
        "A_virt_u_rank": "FORMALIZED_RANK_1",
        "Z_virt_u2_mass_fit": "FORBIDDEN_AS_DERIVATION",
    }


def build_report() -> VirtualDoorApplicabilityReport:
    rows = source_audit_rows()
    return VirtualDoorApplicabilityReport(
        public_status=PUBLIC_STATUS,
        pair_dimension=virtual_pair_dimension(),
        admissible_rank=admissibility_rank_for_up(),
        ratio=z_virt_u2_ratio(),
        z_virt_u2_dimension_ratio=dimension_ratio_status(rows),
        z_virt_u2_applicability=applicability_status(rows),
        source_audit_rows=rows,
    )


def report_as_dict() -> Dict[str, object]:
    report = build_report()
    return {
        "public_status": report.public_status,
        "pair_dimension": report.pair_dimension,
        "admissible_rank": report.admissible_rank,
        "ratio": f"{report.ratio.numerator}/{report.ratio.denominator}",
        "Z_virt_u2_dimension_ratio": report.z_virt_u2_dimension_ratio,
        "Z_virt_u2_applicability": report.z_virt_u2_applicability,
        "frozen_predictions_changed": report.frozen_predictions_changed,
        "official_predictions_changed": report.official_predictions_changed,
        "source_audit_rows": [asdict(row) for row in report.source_audit_rows],
    }

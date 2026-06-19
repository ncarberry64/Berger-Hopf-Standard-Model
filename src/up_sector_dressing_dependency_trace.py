from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

STRUCTURAL_SOURCE = "STRUCTURAL_SOURCE"
LEGACY_NUMERICAL_CANDIDATE = "LEGACY_NUMERICAL_CANDIDATE"
FROZEN_PREDICTION_REFERENCE = "FROZEN_PREDICTION_REFERENCE"
COMPARISON_ONLY = "COMPARISON_ONLY"
UNKNOWN_OR_AMBIGUOUS = "UNKNOWN_OR_AMBIGUOUS"


@dataclass(frozen=True)
class DressingDependencyRow:
    object: str
    source_file: str
    source_line_or_key: str
    depends_on: str
    feeds_into: str
    uses_observed_data: bool
    links_to_two_door_pair: bool
    status: str
    reason: str


@dataclass(frozen=True)
class DressingDependencyReport:
    public_status: str
    dependency_trace: List[DressingDependencyRow]
    applicability_status: str
    dimension_ratio_status: str
    legacy_Z_virt_u2_numerical_candidate: str
    Z_virt_u2_mass_fit_route: str
    frozen_predictions_changed: bool = False
    official_predictions_changed: bool = False


def dependency_trace_rows() -> List[DressingDependencyRow]:
    return [
        DressingDependencyRow(
            object="frozen dressed branch builder",
            source_file="src/bhsm_v1.py",
            source_line_or_key="build_bhsm_dressed_v1_candidate",
            depends_on="pure_fiber_middle_up_rule(); apply_virtual_dressing(model, (rule,))",
            feeds_into="BHSM_DRESSED_V1_CANDIDATE frozen c/t dressing",
            uses_observed_data=False,
            links_to_two_door_pair=False,
            status=FROZEN_PREDICTION_REFERENCE,
            reason="the frozen branch applies the existing rule but is not a derivation source",
        ),
        DressingDependencyRow(
            object="dressed branch freeze guard",
            source_file="src/bhsm_v1.py",
            source_line_or_key="BHSMVersion.__post_init__",
            depends_on="sector=up_quarks; generation=middle; mode=(6,0); factor=0.5",
            feeds_into="rejects non-frozen dressed-branch metadata",
            uses_observed_data=False,
            links_to_two_door_pair=False,
            status=FROZEN_PREDICTION_REFERENCE,
            reason="guards the released value and scope without deriving the virtual pair",
        ),
        DressingDependencyRow(
            object="pure-fiber middle-up rule",
            source_file="src/virtual_environment.py",
            source_line_or_key="pure_fiber_middle_up_rule",
            depends_on="j=0; q=6; Omega_u=6; WEAK_DOUBLE_PROJECTION; factor=0.5",
            feeds_into="apply_virtual_dressing and BHSM_DRESSED_V1_CANDIDATE",
            uses_observed_data=False,
            links_to_two_door_pair=False,
            status=STRUCTURAL_SOURCE,
            reason="uses internal mode and boundary data, but not the explicit PO-BH-66 two-door pair",
        ),
        DressingDependencyRow(
            object="virtual dressing application",
            source_file="src/virtual_environment.py",
            source_line_or_key="apply_virtual_dressing/_rule_applies",
            depends_on="MODE_SPECIFIC scope and model generation mode (6,0)",
            feeds_into="dressed ratio copy used by frozen branch and diagnostics",
            uses_observed_data=False,
            links_to_two_door_pair=False,
            status=STRUCTURAL_SOURCE,
            reason="applies the rule locally by sector/generation/mode, but does not prove two-door sampling",
        ),
        DressingDependencyRow(
            object="virtual dressing adoption audit",
            source_file="theory/virtual_dressing_adoption_audit.md",
            source_line_or_key="C1-C6 criteria",
            depends_on="sector=up_quarks; mode=(6,0); q=6; j=0; Omega_u=6; weak-doublet projection",
            feeds_into="ADOPTION_CANDIDATE status language",
            uses_observed_data=False,
            links_to_two_door_pair=False,
            status=LEGACY_NUMERICAL_CANDIDATE,
            reason="records representation-data linkage and output preservation, but says full loop derivation remains open",
        ),
        DressingDependencyRow(
            object="dimension-ratio route",
            source_file="docs/bhsm_up_sector_virtual_door_applicability.md",
            source_line_or_key="Candidate Virtual Pair",
            depends_on="V_pair^u=span{door_u,door_d}; rank(A_virt^u)=1; dim(V_pair^u)=2",
            feeds_into="Z_virt_u2_dimension_ratio",
            uses_observed_data=False,
            links_to_two_door_pair=True,
            status=STRUCTURAL_SOURCE,
            reason="formalizes the two-door ratio but keeps applicability open",
        ),
        DressingDependencyRow(
            object="frozen prediction reference",
            source_file="docs/frozen_predictions.md",
            source_line_or_key="BHSM_DRESSED_V1_CANDIDATE row",
            depends_on="released Z_virt^{u,2}=1/2 applied only to c/t",
            feeds_into="public frozen prediction package",
            uses_observed_data=False,
            links_to_two_door_pair=False,
            status=FROZEN_PREDICTION_REFERENCE,
            reason="preserves the release; it cannot be used as a derivation",
        ),
        DressingDependencyRow(
            object="bare vs dressed manuscript comparison",
            source_file="manuscript/bare_vs_dressed_branches.md",
            source_line_or_key="bare/dressed branch table",
            depends_on="released bare and dressed values",
            feeds_into="human-readable release comparison",
            uses_observed_data=False,
            links_to_two_door_pair=False,
            status=FROZEN_PREDICTION_REFERENCE,
            reason="documents branch difference without proving the source of the factor",
        ),
        DressingDependencyRow(
            object="threshold/common-scale comparison rows",
            source_file="src/virtual_environment.py",
            source_line_or_key="_comparison_rows and adoption_report",
            depends_on="compare_bhsm_to_threshold_common_scale after dressed ratios are computed",
            feeds_into="diagnostic residual tables",
            uses_observed_data=True,
            links_to_two_door_pair=False,
            status=COMPARISON_ONLY,
            reason="comparison occurs after the rule is defined and cannot justify the factor",
        ),
        DressingDependencyRow(
            object="CKM virtual mixing candidate",
            source_file="src/bhsm_virtual_mixing_solution.py",
            source_line_or_key="s23_candidate = s23_frozen * (Z_virt^{u,2})^(1/16)",
            depends_on="released Z_virt factor and exploratory 1/16 exponent",
            feeds_into="non-official CKM 2-3 mixing diagnostic",
            uses_observed_data=True,
            links_to_two_door_pair=False,
            status=COMPARISON_ONLY,
            reason="exploratory mixing candidate cannot derive the mass dressing factor",
        ),
    ]


def rows_by_status() -> Dict[str, List[DressingDependencyRow]]:
    out: Dict[str, List[DressingDependencyRow]] = {}
    for row in dependency_trace_rows():
        out.setdefault(row.status, []).append(row)
    return out


def all_sources_classified(rows: Iterable[DressingDependencyRow] | None = None) -> bool:
    allowed = {
        STRUCTURAL_SOURCE,
        LEGACY_NUMERICAL_CANDIDATE,
        FROZEN_PREDICTION_REFERENCE,
        COMPARISON_ONLY,
        UNKNOWN_OR_AMBIGUOUS,
    }
    return all(row.status in allowed for row in (rows or dependency_trace_rows()))


def actual_dressing_source_links_to_two_door_pair(rows: Iterable[DressingDependencyRow] | None = None) -> bool:
    relevant = [
        row for row in (rows or dependency_trace_rows())
        if row.object in {"frozen dressed branch builder", "pure-fiber middle-up rule", "virtual dressing application"}
    ]
    return any(row.links_to_two_door_pair for row in relevant)


def any_derivation_uses_observed_data(rows: Iterable[DressingDependencyRow] | None = None) -> bool:
    return any(
        row.uses_observed_data and row.status in {STRUCTURAL_SOURCE, LEGACY_NUMERICAL_CANDIDATE}
        for row in (rows or dependency_trace_rows())
    )


def applicability_status(rows: Iterable[DressingDependencyRow] | None = None) -> str:
    rows = list(rows or dependency_trace_rows())
    if actual_dressing_source_links_to_two_door_pair(rows) and not any_derivation_uses_observed_data(rows):
        return "DERIVED_CONDITIONAL"
    return "OPEN_LOCALIZABLE"


def dimension_ratio_status(rows: Iterable[DressingDependencyRow] | None = None) -> str:
    if applicability_status(rows) == "DERIVED_CONDITIONAL":
        return "DERIVED_CONDITIONAL"
    return "STRONG_DERIVATION_CANDIDATE"


def audit_statuses() -> Dict[str, str]:
    return {
        "up_sector_dressing_dependency_trace": "COMPLETED",
        "Z_virt_u2_applicability": applicability_status(),
        "Z_virt_u2_dimension_ratio": dimension_ratio_status(),
        "legacy_Z_virt_u2_numerical_candidate": "LOCALIZED_NOT_DERIVED",
        "Z_virt_u2_mass_fit_route": "FORBIDDEN_AS_DERIVATION",
    }


def build_report() -> DressingDependencyReport:
    return DressingDependencyReport(
        public_status=PUBLIC_STATUS,
        dependency_trace=dependency_trace_rows(),
        applicability_status=applicability_status(),
        dimension_ratio_status=dimension_ratio_status(),
        legacy_Z_virt_u2_numerical_candidate="LOCALIZED_NOT_DERIVED",
        Z_virt_u2_mass_fit_route="FORBIDDEN_AS_DERIVATION",
    )


def report_as_dict() -> Dict[str, object]:
    report = build_report()
    return {
        "public_status": report.public_status,
        "applicability_status": report.applicability_status,
        "dimension_ratio_status": report.dimension_ratio_status,
        "legacy_Z_virt_u2_numerical_candidate": report.legacy_Z_virt_u2_numerical_candidate,
        "Z_virt_u2_mass_fit_route": report.Z_virt_u2_mass_fit_route,
        "frozen_predictions_changed": report.frozen_predictions_changed,
        "official_predictions_changed": report.official_predictions_changed,
        "dependency_trace": [asdict(row) for row in report.dependency_trace],
        "uses_observed_data_flags": {
            row.object: row.uses_observed_data for row in report.dependency_trace
        },
        "two_door_pair_link_flags": {
            row.object: row.links_to_two_door_pair for row in report.dependency_trace
        },
        "remaining_proof_obligations": [
            "prove actual middle-up virtual correction samples V_pair^u",
            "derive full virtual loop/threshold source",
            "keep frozen prediction references out of derivations",
            "keep comparison-only residual rows out of derivations",
        ],
    }

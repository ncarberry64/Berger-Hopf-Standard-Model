"""No-churn BHSM theorem-closure sprint aggregator."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from full_bhsm_theorem_final_decision import FULL_BHSM_THEOREM_PACKAGE_COMPLETE, build_full_bhsm_theorem_final_decision
from full_ht_theorem_final import BHSM_THEOREM_FAILURE, STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP, build_full_ht_theorem_final_report
from ht_lower_bound_transfer import build_ht_lower_bound_transfer_sprint_report
from index_theorem_hardening import build_index_theorem_hardening_report
from mirror_exclusion_hardening import build_mirror_exclusion_hardening_report


@dataclass(frozen=True)
class FullBHSMSprintStatus:
    final_result: str
    exact_blocker: str
    final_paper_allowed: bool
    ht_lower_bound_transfer_status: str
    index_status: str
    mirror_status: str
    full_ht_status: str
    full_bhsm_status: str
    tests_expected: str
    frozen_outputs_changed: bool
    limitations: tuple[str, ...]


def build_full_bhsm_sprint_status() -> FullBHSMSprintStatus:
    lower = build_ht_lower_bound_transfer_sprint_report()
    index = build_index_theorem_hardening_report()
    mirror = build_mirror_exclusion_hardening_report()
    ht = build_full_ht_theorem_final_report()
    bhsm = build_full_bhsm_theorem_final_decision()
    if bhsm.final_result == FULL_BHSM_THEOREM_PACKAGE_COMPLETE:
        final = FULL_BHSM_THEOREM_PACKAGE_COMPLETE
    elif bhsm.final_result == BHSM_THEOREM_FAILURE:
        final = BHSM_THEOREM_FAILURE
    else:
        final = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    return FullBHSMSprintStatus(
        final_result=final,
        exact_blocker=bhsm.exact_blocker,
        final_paper_allowed=bhsm.final_paper_allowed,
        ht_lower_bound_transfer_status=lower.status,
        index_status=index.status,
        mirror_status=mirror.status,
        full_ht_status=ht.final_result,
        full_bhsm_status=bhsm.final_result,
        tests_expected="python -m pytest -q",
        frozen_outputs_changed=False,
        limitations=(
            "No public-facing docs, notebooks, manuscript notes, README, release notes, CITATION, or Zenodo metadata are updated in this sprint.",
            "The sprint stops at the first exact remaining theorem gap rather than upgrading conditional proofs.",
        ),
    )


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_full_bhsm_sprint_status_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_full_bhsm_sprint_status()), indent=2, sort_keys=True) + "\n")


def export_full_bhsm_sprint_result_json(path: str | Path) -> None:
    export_full_bhsm_sprint_status_json(path)


def export_full_bhsm_sprint_result_markdown(path: str | Path) -> None:
    status = build_full_bhsm_sprint_status()
    lines = [
        "# BHSM No-Churn Theorem Sprint Result",
        "",
        f"Final result: `{status.final_result}`",
        f"Exact blocker: `{status.exact_blocker}`",
        f"Final paper allowed: `{status.final_paper_allowed}`",
        f"Frozen outputs changed: `{status.frozen_outputs_changed}`",
        "",
        "| Node | Status |",
        "| --- | --- |",
        f"| H_T lower-bound transfer | `{status.ht_lower_bound_transfer_status}` |",
        f"| index theorem | `{status.index_status}` |",
        f"| mirror exclusion | `{status.mirror_status}` |",
        f"| full H_T theorem | `{status.full_ht_status}` |",
        f"| full BHSM theorem package | `{status.full_bhsm_status}` |",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in status.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

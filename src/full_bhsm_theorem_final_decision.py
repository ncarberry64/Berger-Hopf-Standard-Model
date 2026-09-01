"""No-churn sprint final BHSM theorem-package decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from full_ht_theorem_final import BHSM_THEOREM_FAILURE, FULL_HT_THEOREM_PROVEN, STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP, build_full_ht_theorem_final_report


FULL_BHSM_THEOREM_PACKAGE_COMPLETE = "FULL_BHSM_THEOREM_PACKAGE_COMPLETE"


@dataclass(frozen=True)
class FullBHSMTheoremFinalDecision:
    final_result: str
    theorem_complete: bool
    full_ht_result: str
    exact_blocker: str
    open_or_conditional_nodes: tuple[str, ...]
    final_paper_allowed: bool
    limitations: tuple[str, ...]


def build_full_bhsm_theorem_final_decision() -> FullBHSMTheoremFinalDecision:
    ht = build_full_ht_theorem_final_report()
    if ht.final_result == FULL_HT_THEOREM_PROVEN and not ht.open_or_conditional_nodes:
        result = FULL_BHSM_THEOREM_PACKAGE_COMPLETE
    elif ht.final_result == BHSM_THEOREM_FAILURE:
        result = BHSM_THEOREM_FAILURE
    else:
        result = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    return FullBHSMTheoremFinalDecision(
        final_result=result,
        theorem_complete=result == FULL_BHSM_THEOREM_PACKAGE_COMPLETE,
        full_ht_result=ht.final_result,
        exact_blocker=ht.exact_blocker,
        open_or_conditional_nodes=ht.open_or_conditional_nodes,
        final_paper_allowed=result == FULL_BHSM_THEOREM_PACKAGE_COMPLETE,
        limitations=(
            "This no-churn sprint does not prepare final paper files.",
            "The BHSM theorem package is not complete while any required H_T node remains conditional or blocked.",
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


def export_full_bhsm_theorem_final_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_full_bhsm_theorem_final_decision()), indent=2, sort_keys=True) + "\n")

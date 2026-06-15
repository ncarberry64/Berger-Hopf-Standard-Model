from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_ASSERTIONS = [
    "BHSM proves the Standard Model",
    "BHSM has replaced the Standard Model",
    "BHSM fully derives the Standard Model",
    "BHSM solves dark matter",
    "BHSM disproves particle dark matter",
    "The BHSM mass engine is closed",
    "The heat-kernel spectral action is the official mass engine",
    "All Standard Model constants are derived",
    "The full gauge group is derived",
]

SCAN_PATHS = [
    "README.md",
    "docs/current_bhsm_status.md",
    "docs/github_landing_status.md",
    "docs/github_claim_summary.md",
    "docs/github_quickstart.md",
    "docs/github_release_checklist_full_bhsm_v1.md",
    "theory/full_bhsm_completion_v1_candidate.md",
    "theory/full_bhsm_claim_status_matrix.md",
    "theory/full_bhsm_candidate_release_notes.md",
]

ALLOWED_EXAMPLE_PATHS = {
    "docs/forbidden_claims.md",
}


def _is_negated_context(text: str, start: int) -> bool:
    prefix = text[max(0, start - 80) : start].lower()
    return any(
        marker in prefix
        for marker in (
            "not ",
            "no ",
            "does not ",
            "do not ",
            "forbidden",
            "not claimed",
            "without ",
        )
    )


def audit() -> dict:
    findings = []
    for relative in SCAN_PATHS:
        path = ROOT / relative
        if not path.exists() or relative in ALLOWED_EXAMPLE_PATHS:
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in FORBIDDEN_ASSERTIONS:
            needle = phrase.lower()
            start = lowered.find(needle)
            while start != -1:
                if not _is_negated_context(text, start):
                    findings.append(
                        {
                            "path": relative,
                            "phrase": phrase,
                            "classification": "needs_user_review",
                        }
                    )
                start = lowered.find(needle, start + 1)
    return {
        "audit": "forbidden_claims",
        "passed": not findings,
        "findings": findings,
        "allowed_example_paths": sorted(ALLOWED_EXAMPLE_PATHS),
        "verdict_labels": ["FORBIDDEN_CLAIM_GUARDRAILS_ADDED"],
    }


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "A413C72F731A15B5AF0ED4DDDC3A58D428A60BA3367676FFCDA03FF546593439",
    "docs/frozen_predictions.json": "A9735A4A17934B524C4DE317254AE40838078FBA99274C95C0DBAE11A43C6C17",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def audit() -> dict:
    files = []
    passed = True
    for relative, expected in EXPECTED_HASHES.items():
        actual = sha256(ROOT / relative)
        ok = actual == expected
        passed = passed and ok
        files.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "unchanged": ok,
            }
        )
    return {
        "audit": "frozen_prediction_integrity",
        "passed": passed,
        "frozen_predictions_changed": not passed,
        "files": files,
    }


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)

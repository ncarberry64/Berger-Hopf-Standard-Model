"""Materialize deterministic BHSM v6.30.8 audit artifacts."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import claim_input_completion_consistency as audit

if __name__ == "__main__":
    checks = audit.validate(ROOT)
    if not all(checks.values()):
        raise SystemExit(f"invalid v6.30.8 audit: {checks}")
    if not audit.frozen_hashes_match(ROOT):
        raise SystemExit("frozen hash mismatch")
    for path in audit.materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())

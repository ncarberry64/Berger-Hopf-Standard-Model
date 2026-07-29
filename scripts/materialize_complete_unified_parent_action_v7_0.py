"""Materialize the deterministic BHSM v7.0 master-action audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import master_action


if __name__ == "__main__":
    checks = master_action.validate_model()
    if not all(checks.values()):
        raise SystemExit(f"invalid master-action model: {checks}")
    if not master_action.frozen_hashes_match(ROOT):
        raise SystemExit("frozen prediction hash mismatch")
    for path in master_action.materialize(ROOT):
        print(path.relative_to(ROOT).as_posix())

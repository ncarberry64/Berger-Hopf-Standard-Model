"""Materialize deterministic BHSM v11.5 completion artifacts."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.completion_gate_v11_5 import materialize


if __name__ == "__main__":
    for path in materialize():
        print(path.relative_to(ROOT))

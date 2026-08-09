from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.eta_relative_periodic_legendre_current_gate_v14_87 import materialize


if __name__ == "__main__":
    print(materialize(ROOT))

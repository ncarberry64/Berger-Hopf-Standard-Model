from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.driver_bhsm_exchange_traction_no_go_v14_89 import materialize


if __name__ == "__main__":
    print(materialize(ROOT))

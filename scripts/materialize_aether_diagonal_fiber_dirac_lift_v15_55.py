from pathlib import Path

from bhsm.interface.aether_diagonal_fiber_dirac_lift_v15_55 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

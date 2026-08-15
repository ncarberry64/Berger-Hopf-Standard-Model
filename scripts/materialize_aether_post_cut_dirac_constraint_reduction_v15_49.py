from pathlib import Path

from bhsm.interface.aether_post_cut_dirac_constraint_reduction_v15_49 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))


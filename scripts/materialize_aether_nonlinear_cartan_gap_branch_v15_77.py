from pathlib import Path

from bhsm.interface.aether_nonlinear_cartan_gap_branch_v15_77 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

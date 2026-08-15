from pathlib import Path

from bhsm.interface.aether_reset_hessian_matter_cones_v15_93 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

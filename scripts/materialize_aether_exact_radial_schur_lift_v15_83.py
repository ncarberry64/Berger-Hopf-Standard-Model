from pathlib import Path

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

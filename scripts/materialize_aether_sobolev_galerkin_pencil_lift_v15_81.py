from pathlib import Path

from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

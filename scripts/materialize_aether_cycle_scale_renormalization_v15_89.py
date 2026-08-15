from pathlib import Path

from bhsm.interface.aether_cycle_scale_renormalization_v15_89 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

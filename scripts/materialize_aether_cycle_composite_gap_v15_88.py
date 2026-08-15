from pathlib import Path

from bhsm.interface.aether_cycle_composite_gap_v15_88 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

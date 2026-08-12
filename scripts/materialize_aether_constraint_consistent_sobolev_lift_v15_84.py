from pathlib import Path

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

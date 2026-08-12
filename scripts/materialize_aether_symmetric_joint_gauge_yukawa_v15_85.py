from pathlib import Path

from bhsm.interface.aether_symmetric_joint_gauge_yukawa_v15_85 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

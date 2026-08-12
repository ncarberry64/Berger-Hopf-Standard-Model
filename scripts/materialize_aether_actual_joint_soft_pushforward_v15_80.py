from pathlib import Path

from bhsm.interface.aether_actual_joint_soft_pushforward_v15_80 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

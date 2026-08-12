from pathlib import Path

from bhsm.interface.aether_proper_time_joint_pushforward_v15_91 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

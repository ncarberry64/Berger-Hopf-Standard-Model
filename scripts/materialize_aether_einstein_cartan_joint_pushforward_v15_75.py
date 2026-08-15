from pathlib import Path

from bhsm.interface.aether_einstein_cartan_joint_pushforward_v15_75 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

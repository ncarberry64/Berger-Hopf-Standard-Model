from pathlib import Path

from bhsm.interface.aether_cartan_shell_crossing_v15_76 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

from pathlib import Path

from bhsm.interface.aether_actual_dirac_event_pencil_v15_79 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

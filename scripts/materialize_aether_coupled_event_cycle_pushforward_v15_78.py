from pathlib import Path

from bhsm.interface.aether_coupled_event_cycle_pushforward_v15_78 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

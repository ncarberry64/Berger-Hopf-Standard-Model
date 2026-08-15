from pathlib import Path

from bhsm.interface.aether_cycle_family_centrality_v15_87 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

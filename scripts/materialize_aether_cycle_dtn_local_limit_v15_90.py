from pathlib import Path

from bhsm.interface.aether_cycle_dtn_local_limit_v15_90 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

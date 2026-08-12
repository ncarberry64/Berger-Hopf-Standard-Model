from pathlib import Path

from bhsm.interface.aether_adm_dtn_proper_gap_v15_92 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

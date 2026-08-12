from pathlib import Path

from bhsm.interface.aether_m5_m4_gauge_higgs_ownership_v15_60 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

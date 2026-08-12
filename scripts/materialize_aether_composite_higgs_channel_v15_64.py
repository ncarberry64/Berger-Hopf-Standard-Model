from pathlib import Path

from bhsm.interface.aether_composite_higgs_channel_v15_64 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

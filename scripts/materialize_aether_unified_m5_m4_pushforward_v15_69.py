from pathlib import Path

from bhsm.interface.aether_unified_m5_m4_pushforward_v15_69 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

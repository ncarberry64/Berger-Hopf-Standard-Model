from pathlib import Path

from bhsm.interface.aether_unified_heat_pushforward_gap_v15_70 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

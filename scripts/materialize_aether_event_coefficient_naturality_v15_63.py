from pathlib import Path

from bhsm.interface.aether_event_coefficient_naturality_v15_63 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

from pathlib import Path

from bhsm.interface.aether_sm_gauge_color_completion_v15_58 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

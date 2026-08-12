from pathlib import Path

from bhsm.interface.aether_m4_completion_nonuniqueness_v15_62 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

from pathlib import Path

from bhsm.interface.aether_round_cap_maxwell_dtn_v15_65 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

from pathlib import Path

from bhsm.interface.aether_round_cap_coulomb_dtn_v15_68 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

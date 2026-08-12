from pathlib import Path

from bhsm.interface.aether_zeta_rg_microscopic_completion_v15_61 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

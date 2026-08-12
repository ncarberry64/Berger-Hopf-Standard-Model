from pathlib import Path

from bhsm.interface.aether_lr_susceptibility_zeta_v15_67 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

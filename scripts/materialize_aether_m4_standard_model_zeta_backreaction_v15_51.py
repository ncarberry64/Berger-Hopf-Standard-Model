from pathlib import Path

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

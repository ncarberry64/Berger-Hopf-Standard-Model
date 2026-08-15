from pathlib import Path

from bhsm.interface.aether_lorentzian_child_galerkin_v15_44 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

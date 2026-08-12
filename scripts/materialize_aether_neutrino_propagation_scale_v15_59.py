from pathlib import Path

from bhsm.interface.aether_neutrino_propagation_scale_v15_59 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

from pathlib import Path

from bhsm.interface.aether_hybrid_flavor_spectrum_v15_54 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

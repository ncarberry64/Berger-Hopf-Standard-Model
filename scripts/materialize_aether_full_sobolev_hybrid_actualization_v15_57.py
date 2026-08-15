from pathlib import Path

from bhsm.interface.aether_full_sobolev_hybrid_actualization_v15_57 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

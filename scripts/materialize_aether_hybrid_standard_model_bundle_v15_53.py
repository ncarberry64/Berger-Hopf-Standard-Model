from pathlib import Path

from bhsm.interface.aether_hybrid_standard_model_bundle_v15_53 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

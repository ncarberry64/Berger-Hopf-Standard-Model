from pathlib import Path

from bhsm.interface.aether_full_gauge_dtn_lr_kernel_v15_66 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

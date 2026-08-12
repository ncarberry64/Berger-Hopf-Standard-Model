from pathlib import Path

from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))


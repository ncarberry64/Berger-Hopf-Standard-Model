from pathlib import Path

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

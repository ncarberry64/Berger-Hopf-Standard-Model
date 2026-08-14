"""Materialize the v18.12 square-KKT complete-child promotion."""
from pathlib import Path
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

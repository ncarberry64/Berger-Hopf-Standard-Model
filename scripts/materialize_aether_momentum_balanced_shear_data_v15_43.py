from pathlib import Path

from bhsm.interface.aether_momentum_balanced_shear_data_v15_43 import (
    materialize,
)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

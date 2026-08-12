from pathlib import Path

from bhsm.interface.aether_response_constrained_child_galerkin_v15_41 import (
    materialize,
)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

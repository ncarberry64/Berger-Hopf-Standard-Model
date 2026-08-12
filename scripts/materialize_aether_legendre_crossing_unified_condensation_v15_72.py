from pathlib import Path

from bhsm.interface.aether_legendre_crossing_unified_condensation_v15_72 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

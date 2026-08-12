from pathlib import Path

from bhsm.interface.aether_quadratic_backreaction_closure_v15_94 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

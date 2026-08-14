"""Materialize the v18.10 direct exact projected merit gradient."""
from pathlib import Path
from bhsm.interface.aether_n3_exact_projected_merit_gradient_v18_10 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

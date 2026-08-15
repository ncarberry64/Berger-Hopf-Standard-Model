"""Materialize the v18.07 exact projected residual Jacobian."""
from pathlib import Path
from bhsm.interface.aether_n3_exact_projected_residual_jacobian_v18_07 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

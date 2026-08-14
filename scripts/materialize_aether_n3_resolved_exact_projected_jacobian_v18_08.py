"""Materialize the v18.08 resolved exact projected Jacobian."""
from pathlib import Path
from bhsm.interface.aether_n3_resolved_exact_projected_jacobian_v18_08 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

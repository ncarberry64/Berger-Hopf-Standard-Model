"""Materialize the v18.09 complete-child-gated resolved trial."""
from pathlib import Path
from bhsm.interface.aether_n3_resolved_trial_complete_child_promotion_v18_09 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

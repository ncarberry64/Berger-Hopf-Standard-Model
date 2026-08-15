"""Materialize the v18.06 physically accepted chain-rule trial."""
from pathlib import Path
from bhsm.interface.aether_n3_chain_trial_complete_child_promotion_v18_06 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

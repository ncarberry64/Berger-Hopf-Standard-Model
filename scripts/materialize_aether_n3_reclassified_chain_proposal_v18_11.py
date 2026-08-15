"""Materialize the v18.11 reclassified N=3 proposal continuation."""
from pathlib import Path
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

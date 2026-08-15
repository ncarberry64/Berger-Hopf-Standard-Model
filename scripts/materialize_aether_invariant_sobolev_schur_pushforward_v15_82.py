from pathlib import Path

from bhsm.interface.aether_invariant_sobolev_schur_pushforward_v15_82 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

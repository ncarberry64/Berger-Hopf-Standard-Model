from pathlib import Path

from bhsm.interface.aether_post_cut_self_similar_persistence_v15_47 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))


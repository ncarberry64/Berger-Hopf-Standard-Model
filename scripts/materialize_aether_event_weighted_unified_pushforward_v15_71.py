from pathlib import Path

from bhsm.interface.aether_event_weighted_unified_pushforward_v15_71 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))

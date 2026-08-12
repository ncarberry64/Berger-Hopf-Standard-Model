from pathlib import Path

from bhsm.interface.aether_reconstruction_firewall_event_v15_45 import (
    materialize,
)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

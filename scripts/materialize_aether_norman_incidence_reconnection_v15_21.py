"""Materialize the BHSM NormanWorks incidence reconnection theorem."""

from pathlib import Path

from bhsm.interface.aether_norman_incidence_reconnection_v15_21 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

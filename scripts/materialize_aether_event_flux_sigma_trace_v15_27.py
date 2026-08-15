"""Materialize the BHSM v15.27 event-flux sigma-trace theorem."""

from pathlib import Path

from bhsm.interface.aether_event_flux_sigma_trace_v15_27 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

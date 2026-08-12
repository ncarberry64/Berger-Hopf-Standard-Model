"""Materialize the BHSM v15.11 core--surface trace theorem."""

from pathlib import Path

from bhsm.interface.aether_core_surface_trace_v15_11 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))

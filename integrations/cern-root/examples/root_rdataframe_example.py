"""Minimal PyROOT RDataFrame example for the BHSM coordinate adapter."""

from __future__ import annotations

import sys
from pathlib import Path

import ROOT  # type: ignore[import-not-found]


INTEGRATION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(INTEGRATION / "python"))
from bhsm_root import add_boundary_columns, install  # noqa: E402


install(ROOT)
frame = ROOT.RDataFrame("Events", "events.root")

# Drop-in line: add the BHSM-inspired coordinate columns to an existing frame.
frame = add_boundary_columns(frame, t="t", x="x", y="y", z="z")

frame.Snapshot(
    "Events",
    "events_with_bhsm.root",
    ["bhsm_radius", "bhsm_ux", "bhsm_uy", "bhsm_uz", "bhsm_minkowski_interval"],
)

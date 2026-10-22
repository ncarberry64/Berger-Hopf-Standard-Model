"""Restricted membrane variation and immutable source reconciliation checks."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "norman_consequences", ROOT / "tools/check_norman_core_surface_consequences.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_restricted_symbolic_consequences_and_materialized_ledger_agree():
    result = MODULE.payload()
    assert all(result["exact_symbolic_checks"].values())
    committed = json.loads((ROOT / MODULE.OUTPUT).read_text(encoding="utf-8"))
    assert result == committed


def test_original_versions_are_distinct_and_checked_in_raw_bytes(tmp_path, monkeypatch):
    # Exercise rejection of source mutation without touching the checkout.
    for name in MODULE.RECOVERED_SOURCES:
        path = Path(MODULE.RECOVERY) / "originals" / name
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())
    damaged = tmp_path / MODULE.RECOVERY / "originals" / next(iter(MODULE.RECOVERED_SOURCES))
    damaged.write_bytes(damaged.read_bytes() + b"\n")
    monkeypatch.setattr(MODULE, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="Recovered source bytes differ"):
        MODULE.payload()

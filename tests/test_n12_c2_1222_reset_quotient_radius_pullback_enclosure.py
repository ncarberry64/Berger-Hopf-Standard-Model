from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_c2_1222_reset_quotient_radius_pullback_enclosure.py"
ARTIFACT = ROOT / "artifacts" / "flagship_integration" / "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE.json"
DATA = ARTIFACT.with_suffix(".npz")


def test_1222_radius_pullback_artifact_rebuilds_byte_identically() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = ARTIFACT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    assert ARTIFACT.read_bytes() == first


def test_1222_radius_pullback_scope_and_dimensions() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["fixed_node_radius_pullback"] == "CERTIFIED"
    assert payload["claim_boundary"]["moving_duration_pullback"] == "OPEN"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
    assert sum(payload["Jacobi_provenance"]["block_segment_counts"].values()) == 1222
    with np.load(DATA) as data:
        assert data["local_state_Jacobi_growth_upper"].shape == (1222,)
        assert data["node_log_state_Jacobi_growth_upper"].shape == (1223,)
        assert data["node_log_R4_action_dual_upper"].shape == (1223,)
        assert np.all(data["local_state_Jacobi_growth_upper"] >= 1.0)


def test_nonzero_duration_cotangent_is_not_dropped() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for row in payload["fixed_node_radius_pullback"].values():
        assert row["moving_proper_duration_cotangent_l1_norm"] > 0.0
        assert row["moving_duration_reset_pullback_included"] is False

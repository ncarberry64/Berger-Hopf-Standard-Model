from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface.event_normal_weyl_riccati import (
    scalar_constant_weyl,
    weyl_geometry_jet_rhs,
    weyl_riccati_rhs,
)
from scripts.derive_n12_event_normal_weyl_riccati import (
    build_payload,
    geometry_jet_witness,
    scalar_orientation_witness,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_event_normal_weyl_riccati.py"
TARGET = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json"
)


def test_event_normal_orientation_matches_closed_scalar_solution() -> None:
    assert scalar_orientation_witness()["integration_residual"] < 1.0e-11


def test_linearized_geometry_jet_matches_finite_difference() -> None:
    assert geometry_jet_witness()["absolute_residual"] < 1.0e-9


def test_matrix_rhs_and_input_guards() -> None:
    m = np.diag([0.4, 0.7])
    potential = np.diag([1.3, 2.2])
    rhs = weyl_riccati_rhs(m, potential, -0.2)
    assert np.allclose(rhs, potential + 0.2 * np.eye(2) - m @ m)
    jet = weyl_geometry_jet_rhs(m, np.eye(2), 0.3 * np.eye(2))
    assert np.allclose(jet, 0.3 * np.eye(2) - 2.0 * m)
    with pytest.raises(ValueError, match="Hermitian"):
        weyl_riccati_rhs(np.asarray([[1.0, 1.0], [0.0, 1.0]]), potential, -0.2)
    with pytest.raises(ValueError, match="length"):
        scalar_constant_weyl(-0.1, 2.0, -1.0, 0.5)


def test_event_normal_artifact_is_deterministic() -> None:
    payload = build_payload()
    assert payload["claim_boundary"]["event_normal_Weyl_initial_condition"] == "DERIVED"
    assert payload["claim_boundary"]["actual_N12_exterior_Weyl_value_and_jet"] == "OPEN"
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
    assert json.loads(TARGET.read_text(encoding="utf-8"))["validation_passed"] is True

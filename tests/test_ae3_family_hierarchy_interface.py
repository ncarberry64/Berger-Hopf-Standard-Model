from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface.ae3_family_hierarchy_interface import (
    family_blind_composition,
    family_blind_composition_certificate,
    family_hierarchy_puzzle_ledger,
    hierarchy_interface_decision_surface,
)
from scripts.materialize_ae3_family_hierarchy_interface import TARGET, build_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_ae3_family_hierarchy_interface.py"


def test_family_blind_composition_is_closed_under_noncommuting_spatial_maps() -> None:
    a = np.asarray(((0.0, 1.0), (-1.0, 0.0)))
    b = np.asarray(((2.0, 0.3), (0.3, 1.0)))
    assert np.linalg.norm(a @ b - b @ a) > 0.0
    composed = family_blind_composition((a, b))
    assert np.array_equal(composed, np.kron(b @ a, np.eye(3)))


def test_family_blind_composition_rejects_incompatible_domains() -> None:
    with pytest.raises(ValueError):
        family_blind_composition((np.eye(2), np.eye(3)))


def test_present_ae3_attachment_is_exactly_family_central() -> None:
    certificate = family_blind_composition_certificate()
    assert certificate["certificate_passed"] is True
    assert certificate["factorization_residual"] == 0.0
    assert certificate["C3_shift_commutator_residual"] == 0.0
    assert certificate["family_projector_commutator_residuals"] == [0.0, 0.0, 0.0]
    assert certificate["three_distinct_family_singular_values_possible"] is False


def test_decision_surface_has_two_noncentral_structural_routes() -> None:
    decision = hierarchy_interface_decision_surface()
    route_a = decision["route_A_action_selected_C3_breaking"]
    route_b = decision["route_B_triality_changing_intertwiner"]
    assert route_a["three_distinct_singular_values"] is True
    assert route_a["C3_commutator_norm"] > 0.0
    assert route_a["maximum_projector_commutator_norm"] == 0.0
    assert route_b["three_distinct_singular_values"] is True
    assert route_b["C3_commutator_norm"] < 1.0e-12
    assert route_b["maximum_projector_commutator_norm"] > 0.0
    assert decision["route_selected_by_current_evidence"] is None
    assert decision["continuous_family_coefficients_may_be_inserted"] is False


def test_family_modes_remain_particle_candidates_but_hierarchy_is_open() -> None:
    ledger = family_hierarchy_puzzle_ledger()
    assert ledger["family_modes_can_manifest_as_SM_particles"] is True
    assert ledger["family_mass_hierarchy_derived"] is False
    assert ledger["CKM_PMNS_derived"] is False
    assert ledger["particle_spectrum_rebuilt"] is False
    assert ledger["FULL_BHSM_COMPLETE"] is False


def test_materialized_family_interface_is_deterministic() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert stored["validation_passed"] is True

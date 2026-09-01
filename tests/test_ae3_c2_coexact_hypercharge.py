from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from bhsm.interface.ae3_c2_coexact_hypercharge import (
    assemble_block_element_forms,
    coexact_hypercharge_puzzle_ledger,
    lowest_weyl_coexact_hypercharge_source_jet,
)
from scripts.materialize_ae3_c2_coexact_hypercharge import TARGET, build_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_ae3_c2_coexact_hypercharge.py"


def _elements(
    h: np.ndarray,
    inverse_radii: np.ndarray,
    profile: np.ndarray,
    chirality: int,
    epsilon: float,
) -> np.ndarray:
    S = np.asarray(((1.0, -1.0), (-1.0, 1.0)), dtype=complex)
    A = np.asarray(((2.0, 1.0), (1.0, 2.0)), dtype=complex)
    C = np.asarray(((-1.0, 0.0), (0.0, 1.0)), dtype=complex)
    I = np.eye(2, dtype=complex)
    G = np.diag((1.0, -1.0)).astype(complex)
    rows = []
    for he, inverse, source in zip(h, inverse_radii, profile, strict=True):
        mass = he * A / 6.0
        W = chirality * (1.5 * inverse * I + epsilon * source * G)
        rows.append(np.kron(S / he, I) + np.kron(mass, W @ W) + np.kron(C, W))
    return np.asarray(rows)


def test_matrix_source_jet_is_exact_finite_element_derivative() -> None:
    h = np.asarray((0.17, 0.29, 0.31))
    inverse = np.asarray((1.1, 0.9, 1.3))
    profile = np.asarray((0.4, -0.2, 0.7))
    for chirality in (-1, 1):
        jet = lowest_weyl_coexact_hypercharge_source_jet(
            proper_durations=h,
            inverse_radii=inverse,
            source_profile=profile,
            chirality=chirality,
        )
        epsilon = 1.0e-3
        zero = _elements(h, inverse, profile, chirality, 0.0)
        plus = _elements(h, inverse, profile, chirality, epsilon)
        minus = _elements(h, inverse, profile, chirality, -epsilon)
        first = (plus - minus) / (2.0 * epsilon)
        second = (plus - 2.0 * zero + minus) / epsilon**2
        assert np.allclose(first, jet["vertex_elements"], atol=2.0e-10, rtol=2.0e-10)
        assert np.allclose(second, jet["contact_elements"], atol=3.0e-9, rtol=3.0e-9)


def test_block_assembly_retains_birth_and_eliminates_far_node() -> None:
    local = np.zeros((2, 4, 4), dtype=complex)
    local[0] = np.diag((1.0, 2.0, 3.0, 4.0))
    local[1] = np.diag((5.0, 6.0, 7.0, 8.0))
    assembled = assemble_block_element_forms(local)
    assert np.array_equal(assembled["diagonal_blocks"][0], np.diag((1.0, 2.0)))
    assert np.array_equal(assembled["diagonal_blocks"][1], np.diag((8.0, 10.0)))


def test_source_is_hypercharge_precursor_not_physical_photon() -> None:
    ledger = coexact_hypercharge_puzzle_ledger()
    assert ledger["U1Y_source_jet_derived"] is True
    assert ledger["physical_electromagnetic_vertex_derived"] is False
    assert ledger["muon_magnetic_moment_derived"] is False
    assert "broken_SU2L_x_U1Y_saddle_and_neutral_mixing_map" in ledger[
        "unfitted_interfaces"
    ]["full_field_action"]


def test_actual_c2_hypercharge_artifact_closes_only_the_source_jet() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["CURRENT_C2_COEXACT_U1Y_SOURCE_JET_DERIVED"] is True
    assert payload["CURRENT_C2_PHYSICAL_PHOTON_VERTEX_DERIVED"] is False
    assert payload["MUON_MAGNETIC_MOMENT_DERIVED"] is False
    assert all(
        row["background_diagonal_is_exact_I2_lift"]
        and row["background_off_diagonal_is_exact_I2_lift"]
        for row in payload["chiral_rows"].values()
    )


def test_materialized_hypercharge_source_artifact_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert stored["validation_passed"] is True

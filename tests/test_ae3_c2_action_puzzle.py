from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from bhsm.interface.ae3_c2_action_puzzle import (
    assemble_element_forms,
    assemble_tridiagonal,
    reduced_product_dirac_hs_source_jet,
    section_fit_ledger,
)
from scripts.materialize_ae3_c2_action_puzzle import TARGET, build_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_ae3_c2_action_puzzle.py"


def _local_dirac_form(h: np.ndarray, W: np.ndarray) -> np.ndarray:
    S = np.asarray(((1.0, -1.0), (-1.0, 1.0)))
    A = np.asarray(((2.0, 1.0), (1.0, 2.0)))
    C = np.asarray(((-1.0, 0.0), (0.0, 1.0)))
    return np.asarray(
        [S / he + we**2 * he * A / 6.0 + we * C for he, we in zip(h, W)]
    )


def test_reduced_source_jet_is_exact_dirac_square_derivative() -> None:
    h = np.asarray((0.17, 0.23, 0.31))
    W = np.asarray((1.1, 1.3, 1.7))
    p = np.asarray((0.4, -0.2, 0.8))
    q = -0.7
    jet = reduced_product_dirac_hs_source_jet(
        proper_durations=h,
        base_W=W,
        source_profile=p,
        generator_eigenvalue=q,
    )
    eps = 1.0e-3
    zero = _local_dirac_form(h, W)
    plus = _local_dirac_form(h, W + eps * q * p)
    minus = _local_dirac_form(h, W - eps * q * p)
    first = (plus - minus) / (2.0 * eps)
    second = (plus - 2.0 * zero + minus) / eps**2
    assert np.allclose(first, jet["vertex_elements"], atol=2.0e-11, rtol=2.0e-11)
    assert np.allclose(second, jet["contact_elements"], atol=2.0e-9, rtol=2.0e-9)
    assert jet["electromagnetic_vertex_claimed"] is False
    assert jet["explicit_inverse_formed"] is False


def test_element_assembly_retains_birth_and_eliminates_far_node() -> None:
    elements = np.asarray(
        (
            ((2.0, -1.0), (-1.0, 3.0)),
            ((5.0, 0.5), (0.5, 7.0)),
        )
    )
    assembled = assemble_element_forms(elements)
    matrix = assemble_tridiagonal(
        assembled["diagonal"], assembled["off_diagonal"]
    )
    assert np.array_equal(matrix, np.asarray(((2.0, -1.0), (-1.0, 8.0))))


def test_puzzle_sections_advance_without_overpromoting_observables() -> None:
    ledger = section_fit_ledger()
    assert ledger["method"] == "NON_SERIAL_PUZZLE_SECTION_ASSEMBLY"
    assert "current_full_field_action" in ledger["advanced_sections"]
    assert "muon_magnetic_moment" in ledger["advanced_sections"]
    assert ledger["prediction_emitted"] is False
    assert ledger["full_field_action_complete"] is False
    assert "transverse_photon_vertex" in ledger["unfitted_interfaces"][
        "muon_magnetic_moment"
    ]


def test_actual_c2_piece_reassembles_both_chiralities_without_spectrum_rebuild() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["CURRENT_C2_PRODUCT_DIRAC_QUADRATIC_PIECE_ATTACHED"] is True
    assert payload["CURRENT_C2_REDUCED_HS_SOURCE_JET_DERIVED"] is True
    assert payload["CURRENT_C2_TRANSVERSE_ELECTROMAGNETIC_VERTEX_DERIVED"] is False
    assert payload["MUON_MAGNETIC_MOMENT_DERIVED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert all(
        row["descriptor_exactly_reassembled"]
        for row in payload["operator_piece"]["channels"].values()
    )


def test_materialized_c2_puzzle_artifact_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True

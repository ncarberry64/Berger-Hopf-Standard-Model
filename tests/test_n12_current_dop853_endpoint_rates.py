"""Verify gap enclosures include the error of a nonorthogonal full basis."""
from pathlib import Path
import sys

from flint import arb, ctx
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import certify_n12_current_dop853_endpoint_rates as point


def test_exact_diagonal_gap_is_outward():
    with ctx.workprec(256):
        values = np.arange(61, dtype=float) - 30
        H = np.diag(values)
        packet, _, _ = point.spectrum_gap(H, H)
        assert 0.999999999 < packet["selected_gap_lower"]["lower"] <= 1
        assert packet["all_eigenvalue_error_upper"]["upper"] < 1e-60


def test_imported_basis_orthogonality_error_is_included(monkeypatch):
    values = np.arange(61, dtype=float) - 30
    H = np.diag(values)
    Q = np.eye(61) * (1 + 2.0**-30)
    monkeypatch.setattr(point.np.linalg, "eigh", lambda _: (values, Q))
    with ctx.workprec(256):
        packet, _, _ = point.spectrum_gap(H, H)
        eta = packet["full_basis_orthogonality_norm_upper"]["upper"]
        epsilon = packet["all_eigenvalue_error_upper"]["upper"]
        assert eta > 0
        assert epsilon > packet["full_basis_residual_norm_upper"]["upper"]
        assert 0 < packet["selected_gap_lower"]["lower"] < 1


def test_nonisolated_selected_branch_is_rejected():
    values = np.arange(61, dtype=float) - 30
    values[25] = values[24]
    H = np.diag(values)
    with ctx.workprec(256), pytest.raises(ArithmeticError, match="gap"):
        point.spectrum_gap(H, H)

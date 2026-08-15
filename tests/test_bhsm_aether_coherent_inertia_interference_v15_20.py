from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_coherent_inertia_interference_v15_20 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    attachment_interference_audit_payload,
    coherent_fixed_incidence_quartic,
    completion_payload,
    deterministic_json,
    exact_inertial_sigma_branch,
    fixed_momentum_sigma_energy,
    materialize,
    matrix_fixed_momentum_expansion,
)


ROOT = Path(__file__).resolve().parents[1]


def test_fixed_momentum_expansion_has_positive_inertial_quartic() -> None:
    result = fixed_momentum_sigma_energy(
        0.0,
        momentum=1.7,
        q_inertia=2.3,
        g=0.8,
        static_curvature=0.4,
    )
    assert result["tangent_curvature_at_zero"] == pytest.approx(
        0.4 - 1.7**2 * 0.8 / 2.3
    )
    assert result["induced_Landau_quartic"] == pytest.approx(
        2 * 1.7**2 * 0.8**2 / 2.3
    )
    assert result["induced_Landau_quartic"] > 0.0


def test_exact_nonzero_branch_is_bounded_and_stable() -> None:
    branch = exact_inertial_sigma_branch(
        momentum=2.0, q_inertia=2.0, g=0.8, static_curvature=1.0
    )
    assert branch["activation"] is True
    assert branch["sigma_plus"] == pytest.approx(-branch["sigma_minus"])
    assert branch["branch_curvature"] > 0.0
    assert branch["bounded_without_direct_quartic"] is True
    energy = fixed_momentum_sigma_energy(
        branch["sigma_plus"],
        momentum=2.0,
        q_inertia=2.0,
        g=0.8,
        static_curvature=1.0,
    )
    assert energy["sigma_derivative"] == pytest.approx(0.0, abs=1e-14)


def test_matrix_inverse_inertia_quartic_is_positive_norm() -> None:
    result = matrix_fixed_momentum_expansion(
        [[2.0, 0.3], [0.3, 1.4]],
        [[0.8, 0.2], [0.2, 0.5]],
        [1.1 + 0.2j, -0.4 + 0.3j],
    )
    assert result["induced_quartic_nonnegative"] is True
    assert result["induced_quartic_positive"] is True
    assert result["induced_Landau_quartic"] == pytest.approx(
        2 * result["quartic_as_norm_squared"]
    )


def test_fixed_nonlinear_incidence_norm_is_positive_for_any_phase() -> None:
    gram = [[2.0, 1.0], [1.0, 2.0]]
    aligned = coherent_fixed_incidence_quartic([1.0, 1.0], gram)
    opposed = coherent_fixed_incidence_quartic([1.0, -1.0], gram)
    quadrature = coherent_fixed_incidence_quartic([1.0, 1.0j], gram)
    assert aligned["direct_Landau_quartic"] > opposed["direct_Landau_quartic"] > 0.0
    assert quadrature["direct_Landau_quartic"] > 0.0
    assert aligned["phase_locking_needed_for_nonnegative_sign"] is False
    assert aligned["phase_and_incidence_needed_for_magnitude"] is True


def test_recovered_attachment_gram_has_overlap_but_missing_physical_maps() -> None:
    payload = attachment_interference_audit_payload()
    assert payload["recovered_attachment_tangent_kinetic_Gram"] == [[2.0, 1.0], [1.0, 2.0]]
    assert payload["kinetic_Gram_eigenvalues"] == pytest.approx([1.0, 3.0])
    assert payload["off_diagonal_overlap"] == 1.0
    assert payload["canonical_incidence_isometry_residual"] < 1e-12
    assert payload["canonical_whitened_tangent_channels_are_orthogonal"] is True
    assert payload["second_sigma_nonlinear_incidence_c_sigma2"] is None
    assert payload["formation_q_differential_incidence"] is None
    assert payload["separation_d_differential_incidence"] is None
    assert payload["physical_phase_locking_and_magnitude_derived"] is False


def test_fixed_momentum_and_schur_ensembles_are_not_conflated() -> None:
    branch = exact_inertial_sigma_branch(
        momentum=2.0, q_inertia=2.0, g=0.8, static_curvature=1.0
    )
    assert branch["activation"] is True
    payload = completion_payload()
    assert payload["validation"]["v15_19_Schur_softening_not_contradicted"] is True
    assert "not_interchangeable" in payload["fixed_momentum_saturation"]["ensemble_firewall"]


def test_completion_advances_saturation_but_not_provenance_or_ejection() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    assert payload["fixed_momentum_saturation"]["active_control"]["activation"] is True
    assert payload["G0_provenance"]["inertial_quartic_can_replace_G0_by_current_theorem"] is False
    assert payload["q_to_d_cross_inertia"]["physical_I_qd"] is None
    assert payload["q_to_d_cross_inertia"]["ejection_momentum"] is None
    assert EXACT_NEXT_OBJECT.startswith("ACTION_OWNED_SECOND_SIGMA_AND_Q_D_DIFFERENTIAL_INCIDENCE_MAP")


def test_deterministic_materialization_and_repository_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.20"
    first = materialize(tmp_path / "first")
    second = materialize(tmp_path / "second")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    assert first.read_bytes() == (ROOT / "artifacts" / first.name).read_bytes()

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import scalar_wall_puiseux_fold as fold


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_scalar_wall_puiseux_fold_v6_1_7.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / fold.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def test_sixteen_artifacts_are_deterministic_and_guarded():
    assert len(fold.ARTIFACT_FILES) == 16
    built = fold.build_artifact_payloads(ROOT)
    for key, filename in fold.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == fold.PRIMARY_RESULT
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == fold.deterministic_json(built[key])
        assert all(payload[name] is False for name in fold.GUARDS)


def test_critical_regressions_are_recomputed():
    data = fold.regression_data()
    assert data["mu1_over_q5"] == pytest.approx(29.430918352947, rel=2e-12)
    assert data["cap_value"] == pytest.approx(8.923902707116, rel=2e-11)
    assert data["junction_derivative"] == pytest.approx(-9.124976903426, rel=2e-11)
    assert data["quartic_moment"] == pytest.approx(21.690130229412, rel=2e-11)
    assert data["chi_abs"] == pytest.approx(5.268307871542, rel=2e-11)


def test_double_root_and_two_sheets():
    data = fold.regression_data()
    for sheet in (-1, 1):
        r = 1e-4
        X = 2 + sheet * data["chi_abs"] * r
        sigma_prime = r * data["junction_derivative"]
        assert fold.normal_form(X, sigma_prime) == pytest.approx(0, abs=2e-16)
    h = 1e-6
    assert (fold.normal_form(2 + h, 0) - fold.normal_form(2 - h, 0)) / (2 * h) == pytest.approx(0, abs=1e-15)


def test_order_r_tangent_is_regular_nongauge_and_matches_endpoint():
    for sheet in (-1, 1):
        pole = fold.vacuum_cap_tangent(0, sheet)
        wall = fold.vacuum_cap_tangent(1, sheet)
        assert pole["a0"] == 0
        assert pole["a1"] == 0
        assert wall["a0"] == pytest.approx(1)
        assert wall["a1"] == pytest.approx(0, abs=2e-15)
        assert wall["N1"] == wall["ell1"]
        assert wall["chi1"] != 0


def test_fredholm_shape_derivative_orients_sheets():
    result = load("order_r2_scalar")
    assert result["nu1_upper"] > 0
    assert result["nu1_lower"] < 0
    assert result["direct_quartic_used_here"] is False
    assert abs(result["nu1_upper"] + result["nu1_lower"]) < 1e-12


def test_both_sheets_and_scalar_signs_converge():
    for key, direction in (("lower", -1), ("upper", 1)):
        points = load(key)["points"]
        assert {p["scalar_sign"] for p in points} == {-1, 1}
        assert all(p["converged"] for p in points)
        assert all((p["X"] - 2) * direction > 0 for p in points)
        assert max(p["Hamiltonian_residual"] for p in points) < 2e-8
        assert max(p["junction_residual"] for p in points) < 2e-8
        assert max(p["normal_form_residual"] for p in points) < 2e-8
        by_r = {}
        for point in points:
            by_r.setdefault(point["r"], []).append(point)
        for pair in by_r.values():
            assert pair[0]["X"] == pair[1]["X"]
            assert pair[0]["mu"] == pair[1]["mu"]
            assert pair[0]["sigma_J_prime"] == -pair[1]["sigma_J_prime"]


def test_mesh_convergence_and_no_unconstrained_shooting():
    rows = load("residuals")["mesh_rows"]
    assert len(rows) == 6
    assert all(row["converged"] for row in rows)
    assert load("residuals")["unconstrained_shooting"] is False


def test_action_and_stability_claims_stop_at_available_normalization():
    assert load("action")["leading_power"] is None
    assert load("stability")["action_indication"] is None
    assert load("stability")["full_mixed_operator_constructed"] is False
    assert load("order_r3")["decomposition"]["C_total"] is None


def test_ensemble_and_B1_source_ledgers():
    interpretation = load("interpretation")
    sources = load("sources")
    assert "neighboring provisional B1 theories" in interpretation["varying_C_partial"]
    assert interpretation["dynamical_C_partial"].startswith("unavailable")
    assert sources["removed_primitives"] == []
    assert sources["parent_source_theorem"] is None


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "scalar-wall-puiseux-fold-status"]
    out = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(out.stdout)["primary_result"] == fold.PRIMARY_RESULT
    out = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.1.7 Scalar-Wall Puiseux Fold" in out.stdout


def test_public_status_and_claim_boundary():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert fold.PRIMARY_RESULT in text
    assert fold.COMPLETION_GATE in text
    assert "FULL_BHSM_NOT_COMPLETE" in text


def test_frozen_predictions_and_official_logic_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_invalid_domains_are_rejected():
    with pytest.raises(ValueError):
        fold.normal_form(2, 0, q5=0)
    with pytest.raises(ValueError):
        fold.vacuum_cap_tangent(0.5, 0)
    with pytest.raises(ValueError):
        fold.continuation_point(0, 1)

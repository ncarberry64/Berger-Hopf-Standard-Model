import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import scalar_wall_backreacted_bifurcation as bif


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_scalar_wall_backreacted_bifurcation_v6_1_6.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / bif.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def test_sixteen_artifacts_are_deterministic_and_guarded():
    assert len(bif.ARTIFACT_FILES) == 16
    built = bif.build_artifact_payloads(ROOT)
    for key, filename in bif.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == bif.PRIMARY_RESULT, key
        for guard in bif.GUARDS:
            assert payload[guard] is False, (key, guard)
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == bif.deterministic_json(built[key])


def test_mu1_is_recomputed_by_two_routes_and_converges():
    critical = load("critical")
    rows = critical["shooting_convergence"]
    assert rows[-1]["mu1_over_q5"] == pytest.approx(29.430918352948, rel=2e-12)
    assert abs(rows[-1]["mu1_over_q5"] - rows[-2]["mu1_over_q5"]) < 2e-9
    assert critical["independent_hypergeometric_mu1_over_q5"] == pytest.approx(
        rows[-1]["mu1_over_q5"], rel=2e-12
    )
    assert critical["regression_target_used_as_answer"] is False


def test_weighted_mode_normalization_and_moments():
    mode = bif.critical_mode_diagnostics()
    assert mode["weighted_norm"] == 1
    assert mode["gradient_moment"] == pytest.approx(mode["mu1_over_q5"], rel=2e-12)
    assert mode["junction_derivative"] == pytest.approx(-9.124976903426, rel=2e-11)
    assert mode["quartic_moment"] == pytest.approx(21.690130229412, rel=2e-11)


def test_analytic_second_order_constraint_is_exactly_obstructed():
    second = load("second")
    assert second["status"] == "BHSM_SCALAR_WALL_ANALYTIC_SECOND_ORDER_JUNCTION_OBSTRUCTION_DERIVED"
    assert second["positive_obstruction_coefficient_for_Z5_over_kappa1_1"] == pytest.approx(
        6.938766957338, rel=2e-11
    )
    amplitude = 1.0e-4
    sigma_prime = amplitude * load("critical")["normalized"]["junction_derivative"]
    assert bif.junction_constraint_residual(2.0, sigma_prime) < 0


def test_fold_splits_satisfy_the_nonlinear_junction_constraint():
    amplitude = 1.0e-4
    derivative = load("critical")["normalized"]["junction_derivative"]
    roots = bif.fold_curvature_splits(amplitude, derivative)
    for root in roots:
        assert bif.junction_constraint_residual(
            root, amplitude * derivative
        ) == pytest.approx(0.0, abs=2e-15)
    assert roots[0] < 2 < roots[1]


def test_ensemble_dependence_is_not_promoted_to_branch_or_fredholm_sign():
    branch = load("branch")
    fredholm = load("fredholm")
    continuation = load("continuation")
    assert branch["status"] == bif.PRIMARY_RESULT
    assert branch["fixed_C_partial_analytic"] == "locally obstructed at O(epsilon^2)"
    assert branch["fixed_C_partial_Puiseux"]["full_bulk_solution_found"] is False
    assert branch["supercritical_or_subcritical"] is None
    assert fredholm["decomposition"]["C_total"] is None
    assert fredholm["sign_certified"] is False
    assert continuation["continuation_points"] == []
    assert continuation["unconstrained_shooting_used"] is False


def test_domain_lapse_and_moving_boundary_terms_are_preserved():
    domain = load("domain")
    assert domain["lapse_retained_before_variation"] is True
    assert domain["lapse_and_physical_length_fixed_together"] is False
    assert "endpoint displacement" in domain["boundary_form_map"]
    assert load("expansion")["no_O_epsilon_metric_term_proved"] is False


def test_vacuum_energy_B1_and_Berger_firewalls_are_preserved():
    onshell = load("onshell")
    sources = load("sources")
    mixed = load("mixed")
    assert onshell["scalar_vacuum_energy_retained"] is True
    assert onshell["flat_wall_tension_used"] is False
    assert sources["independent_B1_primitives_removed"] == []
    assert "not generated" in sources["tau_A"]
    assert mixed["p1_minus_p2"] == 0
    assert mixed["direct_singlet_Berger_source"] == 0


def test_continuation_failure_is_not_a_theorem_or_full_stability_claim():
    continuation = load("continuation")
    amplitude = load("amplitude")
    assert continuation["status"] == "BHSM_SCALAR_WALL_BACKREACTED_BRANCH_NOT_FOUND"
    assert continuation["reason"]
    assert amplitude["new_branch_eigenvalue"] is None
    assert amplitude["full_mixed_stability_claimed"] is False


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "scalar-wall-bifurcation-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == bif.PRIMARY_RESULT
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.1.6 Scalar-Wall Backreacted Bifurcation" in markdown.stdout


def test_public_claims_and_required_status_are_explicit():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / name for name in bif.ARTIFACT_FILES.values())
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert bif.PRIMARY_RESULT in text
    assert bif.COMPLETION_GATE in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    assert "total cubic Fredholm coefficient is derived" not in text
    assert "full mixed stability is proved" not in text


def test_frozen_predictions_and_official_logic_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_invalid_fold_domain_is_rejected():
    with pytest.raises(ValueError):
        bif.fold_curvature_splits(0.1, 1.0, q5=0)
    with pytest.raises(ValueError):
        bif.fold_curvature_splits(0.1, 1.0, Z_over_kappa=-1)

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import twistor_berger_associated_bundle as tb


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_twistor_berger_associated_bundle_v6_0_8.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / tb.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / name for name in tb.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_package_has_fifteen_nonduplicative_v608_artifacts_and_guards():
    assert len(tb.ARTIFACT_FILES) == 15
    assert len(set(tb.ARTIFACT_FILES.values())) == 15
    for key in tb.ARTIFACT_FILES:
        payload = load(key)
        assert payload["primary_result"] == "BHSM_BERGER_COVARIANT_MULTIPLET_ARCHITECTURE_DERIVED", key
        assert payload["v6_0_7_topology_theorem_preserved"] is True, key
        assert payload["section_of_cp3_to_s4_assumed"] is False, key
        assert payload["u1_bundle_over_cp3_confused_with_reduction_over_s4"] is False, key
        assert payload["measured_input_used"] is False, key
        assert payload["frozen_predictions_changed"] is False, key
        assert payload["official_prediction_logic_changed"] is False, key


def test_materialization_is_deterministic():
    built = tb.build_artifact_payloads(ROOT)
    for key, filename in tb.ARTIFACT_FILES.items():
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == tb.deterministic_json(built[key])


def test_global_nested_distributions_split_without_double_counting():
    assert tb.nested_dimensions() == (4, 2, 1)
    assert sum(tb.nested_dimensions()) == 7
    payload = load("distributions")
    assert payload["splitting"] == "TS7=H4 direct-sum V2 direct-sum V1"
    assert payload["orthogonal"] is True
    assert payload["double_counted_direction"] is False
    assert payload["global_section_required"] is False


def test_integrability_and_curvature_are_not_silently_flattened():
    payload = load("distributions")
    assert payload["integrability"]["V1"] == "integrable circle orbits"
    assert "not integrable" in payload["integrability"]["V2"]
    assert "S3 fibers" in payload["integrability"]["V2_plus_V1"]
    assert "nonzero c2" in payload["connection_curvature"]


def test_twistor_preimage_reconstructs_the_complete_hopf_s3_fiber():
    payload = load("reconstruction")
    assert payload["identity"] == "F_x=p_C^-1(tau^-1(x))=(tau o p_C)^-1(x)=p_H^-1(x)"
    assert payload["diffeomorphism_type"] == "F_x isomorphic to Sp(1) isomorphic to S3"
    assert payload["restricted_fibration"] == "S1=U(1)->F_x=S3->S2_x=Sp(1)/U(1)"
    assert payload["section_of_twistor_bundle_used"] is False


def test_global_metric_uses_total_space_u1_without_a_reduction_over_s4():
    payload = load("metric")
    assert payload["metric"] == "g7=L4^2 g_H4+L2^2 g_V2+L1^2 eta^2"
    assert payload["generic_invariance"] == "Sp(2)xU(1)_R"
    assert "not a U(1) reduction over S4" in payload["cp3_role"]
    assert payload["no_twistor_section"] is True


def test_berger_metric_coefficients_and_invalid_scales():
    assert tb.berger_metric_coefficients(2.0, 3.0) == (4.0, 4.0, 9.0)
    with pytest.raises(ValueError):
        tb.berger_metric_coefficients(0, 1)
    with pytest.raises(ValueError):
        tb.berger_metric_coefficients(1, -1)


def test_exact_berger_scalar_spectrum_and_round_limit():
    assert tb.berger_eigenvalue(0, 0, 1, 1) == 0
    assert tb.berger_eigenvalue(1, -1, 1, 1) == pytest.approx(3 / 4)
    assert tb.berger_eigenvalue(1, 1, 1, 1) == pytest.approx(3 / 4)
    assert tb.berger_eigenvalue(2, 0, 1, 1) == pytest.approx(2)
    assert tb.berger_eigenvalue(2, 2, 2, 1) == pytest.approx(0.5 + 0.75)
    for two_j in range(8):
        for weight in range(-two_j, two_j + 1, 2):
            j = two_j / 2
            assert tb.berger_eigenvalue(two_j, weight, 2.5, 2.5) == pytest.approx(j * (j + 1) / 2.5**2)


@pytest.mark.parametrize("args", [(-1, 0, 1, 1), (1, 0, 1, 1), (2, 3, 1, 1), (2, 0, 0, 1)])
def test_invalid_berger_quantum_numbers_or_scales_are_rejected(args):
    with pytest.raises(ValueError):
        tb.berger_eigenvalue(*args)


def test_fiberwise_eigenspaces_are_associated_multiplets_not_scalars():
    payload = load("hilbert")
    assert payload["global_bundle"] == "mathcal H_(J,m)=S7 times_(rho_J) V_J -> S4"
    assert "not an ordinary scalar unless J=0" in payload["coefficient_type"]
    assert payload["no_global_basis_required"] is True
    assert tb.mode_bundle_rank(0) == 1
    assert tb.mode_bundle_rank(5) == 6


def test_transition_connection_and_u1_weight_transport_are_covariant():
    payload = load("connection")
    assert "h_ab^-1 A_a h_ab" in payload["connection_transition"]
    assert payload["covariant_derivative"] == "D_A phi=d phi+rho_J*(A) phi"
    assert "rho_J*(Omega" in payload["curvature"]
    assert "commutes" in payload["u1_weight_transport"]
    assert payload["twistor_section_used"] is False


def test_minimal_scalar_operator_is_exactly_covariant_and_multiplet_valued():
    payload = load("operator")
    assert payload["operator"] == "O_(J,m)=-D_A^*D_A+lambda_(J,m)(L1,L2)+E_(J,m)"
    assert payload["minimal_scalar_endomorphism"].startswith("E_(J,m)=0")
    assert payload["uncoupled_scalar_required"] is False
    assert "not a U(1) reduction over S4" in payload["u1_role"]


def test_general_sp2_dimension_formula_known_small_representations():
    assert tb.sp2_dimension(0, 0) == 1
    assert tb.sp2_dimension(1, 0) == 4
    assert tb.sp2_dimension(0, 1) == 5
    assert tb.sp2_dimension(2, 0) == 10
    assert tb.sp2_dimension(1, 1) == 16
    with pytest.raises(ValueError):
        tb.sp2_dimension(-1, 0)


@pytest.mark.parametrize("ell,dimension", [(0, 1), (1, 8), (2, 35), (3, 112), (4, 294), (8, 4719)])
def test_general_so8_to_sp2_sp1_branching_matches_s7_harmonic_dimension(ell, dimension):
    row = tb.branching_row(ell)
    assert row["so8_harmonic_dimension"] == dimension
    assert row["branch_dimension_sum"] == dimension


def test_branching_extends_v607_and_tracks_all_u1_weights():
    row = tb.branching_row(4)
    assert [(s["sp2_dynkin"], s["sp1_highest_weight"]) for s in row["summands"]] == [([4, 0], 4), ([2, 1], 2), ([0, 2], 0)]
    assert row["summands"][0]["u1_weights"] == [-4, -2, 0, 2, 4]
    payload = load("branching")
    assert payload["all_dimension_checks_pass"] is True
    assert payload["physical_particle_map"] is None
    assert payload["legacy_k_j_map"] is None


def test_linear_multiplets_close_while_generic_nonlinear_products_route_to_tower():
    assert tb.nonlinear_closure_test([1], 1)["generic_exact_closure"] is True
    result = tb.nonlinear_closure_test([0, 1], 2)
    assert result["generic_exact_closure"] is False
    assert result["generated_maximum_two_j"] == 2
    payload = load("closure")
    assert payload["generic_finite_nontrivial_polynomial_closure"] is False
    assert payload["generic_requirement"] == "infinite harmonic tower"
    assert "spectral-gap controlled effective truncation" in payload["constructive_routes"]
    assert payload["standalone_scalar_failure_generalized_to_multiplets"] is False


def test_parent_action_reduction_is_structural_not_physical_parent_promotion():
    payload = load("action")
    assert payload["status"] == "BHSM_TWISTOR_MEDIATED_REDUCTION_REQUIRES_ACTION_NORMALIZATION"
    assert payload["parent_family_physically_selected"] is False
    assert payload["v5_values_inserted"] is False
    assert "internal Hopf fibers are not boundaries" in payload["boundary_completion"]


def test_existing_v5_engine_is_preserved_and_globally_reinterpreted():
    payload = load("v5")
    assert payload["status"] == "BHSM_V5_BERGER_ENGINE_FIBERWISE_ASSOCIATED_BUNDLE_REINTERPRETED"
    assert payload["mode_ledgers_changed"] is False
    assert payload["particle_interpretation_promoted"] is False
    assert "intertwiner" in load("berger")["legacy_k_j_identification"]


def test_gauge_forward_link_is_geometric_readiness_not_sm_derivation():
    payload = load("gauge")
    assert payload["base_transport_group"] == "Sp(1)"
    assert payload["standard_model_group_identification"] is None
    assert payload["physical_coupling"] is None
    assert "parent kappa1" in payload["kinetic_normalization_source"]


def test_scalar_singlet_moduli_and_v5_target_are_kept_distinct():
    payload = load("scalar")
    assert payload["trivial_mode"].startswith("(J,m)=(0,0)")
    assert payload["existing_sigma_classification"].startswith("unresolved")
    assert payload["v_red_recovered_without_fit"] is False
    assert payload["sigma_vacuum_derived"] is False


def test_dimensionless_ratios_do_not_generate_absolute_scale():
    payload = load("scale")
    assert "b=L1/L2" in payload["dimensionless_ratios"]
    assert payload["eigenvalue_scaling"] == "lambda_(J,m)->alpha^-2 lambda_(J,m)"
    assert payload["v5_numbers_on_parent_side"] is False
    assert payload["absolute_unit_anchor"] is None


def test_report_leads_with_constructed_architecture_and_routes_forward():
    payload = load("report")
    assert payload["status"] == "BHSM_BERGER_COVARIANT_MULTIPLET_ARCHITECTURE_DERIVED"
    assert "construct a global" in payload["central_answer"]
    assert payload["completion_gate"] == "V6_0_8_CONTINUE_TO_TWISTOR_BERGER_ACTION_NORMALIZATION"
    assert payload["recommended_next_branch"] == "bhsm-twistor-berger-action-normalization-v6-0-9"


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "twistor-berger-associated-bundle-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == "BHSM_BERGER_COVARIANT_MULTIPLET_ARCHITECTURE_DERIVED"
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.0.8 Twistor-Mediated Berger" in markdown.stdout


def test_public_claim_language_preserves_exact_constraint_and_constructive_route():
    text = public_text()
    required = [
        "BHSM_BERGER_COVARIANT_MULTIPLET_ARCHITECTURE_DERIVED",
        "BHSM_TWISTOR_MEDIATED_BERGER_METRIC_DERIVED",
        "BHSM_SP1_TO_U1_REDUCTION_TOPOLOGICALLY_OBSTRUCTED",
        "BHSM_GENERIC_NONLINEAR_FINITE_MULTIPLET_REQUIRES_TOWER",
        "FULL_BHSM_NOT_COMPLETE",
    ]
    assert all(label in text for label in required)
    forbidden = ["Standard Model gauge group is derived", "particle generations are derived", "absolute scale is generated", "full BHSM completion is achieved"]
    assert not any(claim in text for claim in forbidden)


def test_frozen_predictions_and_official_model_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest

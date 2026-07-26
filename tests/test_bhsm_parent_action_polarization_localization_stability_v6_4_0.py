import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface import parent_action_polarization_localization_stability as arch


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_parent_action_polarization_localization_stability_v6_4_0.md"
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md":
        "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    ROOT / "docs" / "frozen_predictions.json":
        "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def load(key):
    return json.loads(
        (ARTIFACTS / arch.ARTIFACT_FILES[key]).read_text(encoding="utf-8")
    )


def test_registry_has_exactly_twenty_six_artifacts_and_preserves_source():
    payloads = arch.build_artifact_payloads(ROOT)
    assert len(payloads) == 26
    assert set(payloads) == set(arch.ARTIFACT_FILES)
    assert all(row["version"] == "v6.4.0" for row in payloads.values())
    assert payloads["handoff"]["source_sha"] == arch.SOURCE_SHA
    assert payloads["handoff"]["source_results_changed"] is False


def test_g2_cross_product_complex_structure_for_basis_and_generic_unit_vectors():
    for u in (
        np.eye(7)[0],
        np.eye(7)[6],
        np.array([1, 2, 3, 4, 5, 6, 7], dtype=float),
    ):
        u = u / np.linalg.norm(u)
        J = arch.cross_product_matrix(u)
        Q = np.eye(7) - np.outer(u, u)
        assert np.allclose(J @ u, 0)
        assert np.allclose(J @ J, -Q)
        assert np.allclose(J.T, -J)


def test_complex_polarization_projectors_are_rank_three_and_conjugate():
    plus, minus, Q = arch.polarization_projectors(np.eye(7)[6])
    assert np.allclose(plus @ plus, plus)
    assert np.allclose(minus @ minus, minus)
    assert np.allclose(plus @ minus, 0)
    assert np.allclose(plus + minus, Q)
    assert np.allclose(plus.conj(), minus)
    assert np.linalg.matrix_rank(plus) == 3
    assert np.linalg.matrix_rank(minus) == 3


def test_globalization_states_exact_obstruction_and_dynamic_selection_boundary():
    ledger = arch.topology_globalization_ledger()
    assert ledger["base_dimension"] == 4
    assert ledger["bundle_rank"] == 7
    assert "H^7(M4)=0" in ledger["obstruction_on_M4"]
    assert "nowhere-zero section exists" in ledger["existence"]
    assert "does not dynamically choose" in ledger["selection"]
    assert "SU3" in ledger["transition_functions"]


def test_triality_compatibility_preserves_three_not_nine_families():
    result = arch.triality_polarization_checks()
    assert all(result["triality_algebra"].values())
    assert result["fourier_intertwiner"]["inverse_exact"] is True
    assert result["fourier_intertwiner"]["intertwines_projectors"] is True
    assert result["family_count"] == 3
    assert result["nine_generation_product_rejected"] is True
    assert result["complex_conjugation_is_antiparticle_map"] is True


def test_first_order_action_classifies_missing_parent_source_and_allowed_terms():
    action = load("matter_action")
    assert action["frozen_parent_contains_matter_action"] is False
    assert action["parent_action_derivation_claimed"] is False
    terms = {row["term"]: row for row in arch.allowed_first_order_terms()}
    assert terms["y_sigma sigma Gamma_star"]["localizes"] is True
    assert terms["y_beta beta Gamma_star"]["localizes"] is False
    assert terms["linear n^a without a covariant contraction"]["source"] == (
        "rejected by covariance"
    )
    assert action["new_independent_primitives_if_adopted"] == ["y_sigma"]


def test_odd_wall_coupling_kill_test_and_firewall():
    coupling = load("odd_coupling")
    checks = coupling["kill_test"]
    assert checks["covariant"] is True
    assert checks["Hermitian_for_real_y_sigma"] is True
    assert checks["family_universal"] is True
    assert checks["commutes_with_Y_BH"] is True
    assert checks["already_in_frozen_parent_action"] is False
    assert coupling["measured_Yukawa_used"] is False
    assert coupling["physical_bulk_Dirac_parent_law_introduced"] is False
    assert coupling["monopole_structure_introduced"] is False


@pytest.mark.parametrize("nu", [0.5, 1.0, 2.0])
def test_normal_mode_is_normalized_and_has_one_sided_index(nu):
    x = np.linspace(-20, 20, 300_001)
    profile = arch.normal_mode_profile(x, nu)
    assert abs(np.trapezoid(profile * profile, x) - 1) < 2e-8
    diagnostic = arch.normal_mode_diagnostic(nu)
    assert diagnostic["K_plus_zero_modes"] == 1
    assert diagnostic["K_minus_zero_modes"] == 0
    assert diagnostic["full_line_index"] == 1


def test_representative_profile_integrals_are_exact_regressions():
    result = arch.normal_mode_diagnostic()
    assert abs(result["numerical_norm"] - 1) < 1e-12
    assert abs(result["sigma_overlap"]) < 1e-14
    assert abs(result["sigma_squared_overlap"] - 1 / 3) < 1e-12


def test_vectorlike_doubling_is_removed_only_conditionally_by_domain():
    result = load("doubling")
    assert result["K_plus"] == "one normalizable profile"
    assert "nonnormalizable" in result["K_minus"]
    assert "not a second vectorlike field" in result["antiparticle"]
    assert result["global_no_extra_family_theorem"] is False


def test_exact_connection_traces_and_rejected_incidence_are_preserved():
    source = load("connection_source")
    assert source["trace_indices"] == {
        "I1_normalized": "2",
        "I1_raw": "10/3",
        "I2": "2",
        "I3": "2",
        "eta_Y": "3/5",
    }
    assert source["candidate_1_2_7_restored"] is False
    assert source["measured_couplings_used"] is False


@pytest.mark.parametrize("L2,L1", [(1.0, 1.0), (1.0, 2.0), (2.5, 0.7)])
def test_hopf_connection_transfer_is_positive_and_berger_split_exact(L2, L1):
    result = arch.hopf_connection_transfer(1.3, L2, L1)
    assert result["positive"] is True
    assert result["ratio_nested_to_transverse"] == pytest.approx((L1 / L2) ** 2)
    assert result["ratio_nested_to_transverse"] == pytest.approx(
        math.exp(2 * result["beta"])
    )
    assert result["matrix"][0][0] == result["matrix"][1][1]


def test_connection_transfer_keeps_missing_color_and_boundary_factors_explicit():
    su3 = load("su3_transfer")
    sp1 = load("sp1_transfer")
    u1 = load("u1_transfer")
    assert su3["tau_3"] == "underdetermined"
    assert su3["localization_function_invented"] is False
    assert "8 pi^2 kappa1" in sp1["exact_parent_matrix"]
    assert u1["relative_geometric_split"] == "exp(2 beta)"
    assert u1["candidate_1_2_7_restored"] is False


def test_gravity_and_connection_normalizations_are_not_silently_locked():
    gravity = load("gravity")
    assert gravity["same_invariant_as_connections"] is False
    assert gravity["Z_g_equals_Z_A_assumed"] is False
    assert gravity["C_partial_source"] == "independent provisional B1 primitive"


def test_berger_higgs_kinetic_metric_is_symmetric_positive_and_separates_sigma():
    metric = arch.scalar_field_metric(2.0, 3.0)
    assert np.allclose(metric, metric.T)
    assert np.all(np.linalg.eigvalsh(metric) > 0)
    assert metric[0, 1] == 0
    assert metric[1, 1] == pytest.approx(18 / 7)
    assert arch.orientation_stiffness(0.0) == 0
    assert arch.orientation_stiffness(0.4) > 0


def test_scalar_mass_matrix_generalized_eigenvalues_and_open_mixing():
    values = arch.scalar_mass_eigenvalues(2, 3, 0)
    assert np.all(values > 0)
    mixed = arch.scalar_mass_eigenvalues(2, 3, 0.5)
    assert len(mixed) == 2
    payload = load("scalar_mass")
    assert payload["retained_H_sigma_beta"] == 0
    assert payload["Higgs_like_eigenmode_derived"] is False
    assert payload["higher_order_mixing"] == "open"


def test_conditional_electroweak_mass_matrix_has_exactly_one_null_direction():
    matrix = arch.electroweak_mass_matrix(1.0, 0.6, 2.0)
    assert np.linalg.matrix_rank(matrix) == 3
    assert np.allclose(matrix @ np.array([0, 0, 0.6, 1.0]), 0)
    values = np.linalg.eigvalsh(matrix)
    assert np.count_nonzero(np.isclose(values, 0)) == 1
    payload = load("gauge_mass")
    assert payload["vacuum_Q_em_neutral"] is True
    assert payload["extra_massless_electroweak_direction"] is False
    assert payload["measured_W_Z_Higgs_inputs"] is False


def test_schur_complement_matches_direct_formula_and_rejects_gauge_zero_mode():
    pp = np.diag([3.0, 2.0])
    pc = np.array([[0.5], [0.25]])
    cc = np.array([[2.0]])
    expected = pp - pc @ np.linalg.inv(cc) @ pc.T
    assert np.allclose(arch.schur_complement(pp, pc, cc), expected)
    with pytest.raises(ValueError):
        arch.schur_complement(pp, np.zeros((2, 1)), np.zeros((1, 1)))


def test_constraint_reduced_sectors_classify_only_supported_signs():
    tensor = load("tensor")
    vector = load("vector")
    scalar = load("scalar")
    matter = load("matter_spectrum")
    assert "kappa1>0 and C_partial>0" in tensor["principal_kinetic"]
    assert tensor["tachyon_free"] is None
    assert "tau_i I_i>0" in vector["principal_kinetic"]
    assert "depend on" in scalar["mass_signs"]
    assert matter["physical_bulk_Dirac_parent_law_introduced"] is False
    assert "absolute eigenvalues not derived" in matter["mass_spectrum"]


def test_local_principal_symbols_do_not_manufacture_sheet_selection():
    result = load("spacetime")
    assert result["unique_upper_selection_derived"] is False
    assert result["status"] == "BHSM_LOCAL_PRINCIPAL_SYMBOLS_SHEET_SYMMETRIC"
    assert result["global_continuation_test"] == "open"


def test_absolute_scale_and_r4_remain_symbolic_with_preserved_cusp():
    scale = load("scale")
    assert scale["numerical_absolute_scale"] is None
    assert "SU3 transfer" in scale["independent"]
    r4 = load("r4")
    assert r4["nu1_over_12"] == 9.138890145035
    assert all(value is None for value in r4["B_components"].values())
    assert r4["flat_kink_27_35_revived"] is False


def test_integration_ledger_uses_only_permitted_statuses_and_no_counting_claim():
    result = load("integration")
    permitted = {
        "Adopted input",
        "Derived",
        "Numerically validated",
        "Needs empirical test",
        "Rejected",
        "Active construction target",
    }
    assert len(result["rows"]) == 16
    assert {row["status"] for row in result["rows"]} <= permitted
    assert result["counting_rows_implies_completion"] is False
    assert result["integrated_action_generated_spectrum_exists"] is False


def test_hidden_input_and_global_safeguards():
    hidden = load("hidden")
    assert hidden["measured_inputs"] == []
    assert hidden["fits"] == []
    assert hidden["new_primitives_derived"] == []
    assert "y_sigma" in hidden["independent_primitives_exposed"][0]
    assert all(value is False for value in arch.GUARDS.values())


def test_frozen_prediction_files_are_byte_identical():
    for path, expected in FROZEN_HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_materialized_artifacts_match_deterministic_payloads():
    payloads = arch.build_artifact_payloads(ROOT)
    for key, payload in payloads.items():
        path = ARTIFACTS / arch.ARTIFACT_FILES[key]
        assert path.read_text(encoding="utf-8") == arch.deterministic_json(payload)


def test_cli_json_and_markdown():
    env = {"PYTHONPATH": str(ROOT / "src")}
    command = [
        sys.executable,
        "-m",
        "bhsm.interface",
        "parent-action-polarization-stability-status",
    ]
    json_run = subprocess.run(
        command + ["--format", "json"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=True,
    )
    assert json.loads(json_run.stdout)["primary_result"] == arch.PRIMARY_RESULT
    md_run = subprocess.run(
        command + ["--format", "markdown"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=True,
    )
    assert "v6.4.0 parent-action polarization" in md_run.stdout


def test_doctrine_and_report_share_primary_status_and_concrete_gate():
    text = DOC.read_text(encoding="utf-8")
    report = load("report")
    assert arch.PRIMARY_RESULT in text
    assert arch.COMPLETION_GATE in text
    assert report["status"] == arch.PRIMARY_RESULT
    assert report["completion_gate"] == arch.COMPLETION_GATE

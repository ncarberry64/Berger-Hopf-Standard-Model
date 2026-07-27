import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface import boundary_matter_dynamics_neutral_response as arch


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_boundary_matter_dynamics_neutral_response_v6_7_0.md"
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


def test_registry_has_exactly_twenty_eight_payloads():
    payloads = arch.build_artifact_payloads(ROOT)
    assert len(payloads) == 28
    assert set(payloads) == set(arch.ARTIFACT_FILES)
    assert all(row["version"] == "v6.7.0" for row in payloads.values())


def test_pr166_history_preserving_handoff():
    merge = load("merge")
    handoff = load("handoff")
    assert merge["pr"] == 166
    assert merge["merge_method"] == "merge commit"
    assert all(merge["checks"][key] == "pass" for key in ("pytest", "native", "ROOT"))
    assert merge["remote_branch_retained"]
    assert not merge["force_push"] and not merge["rebase"] and not merge["squash"]
    assert handoff["v6_6_sha_is_ancestor"]


def test_combined_action_keeps_adopted_status_and_one_primitive():
    row = arch.complete_action_ledger()
    assert row["action"] == "S_v6.7=S_P1+S_GHY+S_B1+S_F,partial"
    assert row["matter_action_status"] == "Adopted action invariant; not parent-derived"
    assert row["normalization"] == "canonical coefficient of C_BHSM fixed to one"
    assert not row["new_dimensional_scale"]


def test_matter_and_adjoint_variations_are_independent():
    row = arch.variation_ledger()
    assert row["variations_independent"]
    assert "C_BHSM+y_sigma sigma Gamma_star" in row["delta_bar_Psi"]
    assert "C_BHSM^adj" in row["delta_Psi"]
    assert row["coefficient_normalization"].endswith("y_sigma")


def test_y_sigma_cannot_be_removed_after_canonical_normalization():
    row = arch.variation_ledger()
    assert not row["y_sigma_removable"]
    assert "currents" in row["field_rescaling"]
    assert "inner product" in row["field_rescaling"]


def test_scalar_source_is_exact_and_family_universal():
    row = arch.source_ledgers()["scalar"]
    assert row["derived_from_action"]
    assert row["source"].startswith("J_sigma=y_sigma")
    assert row["wall_parity"].startswith("odd")
    assert "three" in row["family_factor"]
    assert row["order_r4"].startswith("not fixed")


def test_berger_source_does_not_invent_beta_dependence():
    row = arch.source_ledgers()["berger"]
    assert row["explicit_wall_mass_derivative"] == 0
    assert row["derived_functionally"]
    assert not row["numerically_closed"]
    assert not row["Berger_vacuum_shift_derived"]


def test_gauge_currents_preserve_charge_and_anomaly_ledgers():
    row = arch.source_ledgers()["currents"]
    assert "Y_BH" in row["U1"]
    assert "T_n+Y_BH" in row["Q_em"]
    assert row["on_shell_covariant_conservation"]
    assert row["family_universal"]
    assert row["anomaly_ledger_preserved"]
    assert not row["full_low_energy_G2_current_introduced"]


def test_minimal_stress_includes_measure_connection_and_wall():
    row = arch.source_ledgers()["stress"]
    assert row["wall_term_included"]
    assert row["measure_included"]
    assert row["spin_connection_included"]
    assert "junction" in row["junction_source"]
    assert row["numerical_sheet_shift"].startswith("not closed")


def test_boundary_form_has_balanced_signature():
    form = arch.boundary_form_matrix()
    assert np.allclose(form, form.conj().T)
    assert np.allclose(np.linalg.eigvalsh(form), [-1, 1])


@pytest.mark.parametrize("theta", [0, np.pi / 7, np.pi / 2, np.pi])
def test_u1_graph_domains_are_maximal_isotropic(theta):
    vector = arch.maximal_isotropic_vector(theta)
    form = arch.boundary_form_matrix()
    assert np.linalg.norm(vector) == pytest.approx(1)
    assert vector.conj() @ form @ vector == pytest.approx(0, abs=1e-13)


def test_action_does_not_select_unique_domain():
    row = arch.boundary_domain_audit()
    assert not row["unique_domain_selected"]
    assert row["result"] == arch.DOMAIN_RESULT
    assert "U(1)" in row["self_adjoint_domains"]
    assert "no junction projector" in row["reason"]


def test_domain_compatibility_and_flux_ledger_is_complete():
    row = arch.boundary_domain_audit()
    assert "Y_BH" in row["charge_and_family_compatibility"]
    assert "Q_em" in row["charge_and_family_compatibility"]
    assert "family projectors" in row["charge_and_family_compatibility"]
    assert "Pi_10/Pi_01" in row["polarization_compatibility"]
    assert "conjugate-domain" in row["charge_conjugation"]
    assert all(sample["rank"] == 1 for sample in row["samples"])
    assert all(sample["isotropic_residual"] == 0 for sample in row["samples"])
    assert all(
        sample["projector_idempotence_residual"] == 0
        for sample in row["samples"]
    )


@pytest.mark.parametrize("sheet", [-1, 1])
def test_actual_b1_cap_profile_is_regular_and_reaches_junction(sheet):
    profile = arch.cap_profile(sheet=sheet, points=81)
    assert abs(profile["a"][0]) < 1e-5
    assert profile["a"][-1] == pytest.approx(1, abs=2e-8)
    assert profile["sigma"][-1] == pytest.approx(0, abs=2e-8)
    assert profile["ell"] > 0


@pytest.mark.parametrize("sheet", [-1, 1])
@pytest.mark.parametrize("scalar_sign", [-1, 1])
@pytest.mark.parametrize("orientation", [-1, 1])
def test_actual_cap_first_order_spectrum_has_index_one(sheet, scalar_sign, orientation):
    row = arch.first_order_cap_spectrum(
        sheet=sheet,
        scalar_sign=scalar_sign,
        wall_orientation=orientation,
        points=81,
    )
    assert row["actual_B1_profile"]
    assert row["index"] == 1
    assert row["selected_zero_modes"] == 1
    assert row["opposite_zero_modes"] == 0
    assert row["zero_mode_residual"] < 1e-9
    assert row["first_gap"] > 0
    assert row["cap_regularity"]
    assert not row["action_selected_domain"]


@pytest.mark.parametrize("sheet", [-1, 1])
def test_scalar_sign_and_wall_orientation_combination_is_spectrum_invariant(sheet):
    positive = arch.first_order_cap_spectrum(
        sheet=sheet, scalar_sign=1, wall_orientation=1, points=81
    )
    paired = arch.first_order_cap_spectrum(
        sheet=sheet, scalar_sign=-1, wall_orientation=-1, points=81
    )
    assert positive["massive_levels"] == pytest.approx(paired["massive_levels"], abs=1e-9)
    assert positive["localization_width"] == pytest.approx(
        paired["localization_width"], abs=1e-9
    )


def test_y_sigma_dependency_is_exposed_without_fit():
    weak = arch.first_order_cap_spectrum(y_sigma=0.5, points=81)
    strong = arch.first_order_cap_spectrum(y_sigma=2.0, points=81)
    assert weak["y_sigma"] == 0.5
    assert strong["y_sigma"] == 2.0
    assert weak["localization_mean"] != strong["localization_mean"]


def test_beta_dependency_is_kept_open_until_full_operator_is_available():
    source = arch.source_ledgers()["berger"]
    spectrum = load("spectrum")
    assert "beta dependence of C_BHSM" in source["missing"]
    assert "polarization and Berger correction" in spectrum["missing_terms"]
    assert not source["numerically_closed"]


def test_mesh_convergence_improves_by_refinement():
    rows = arch.convergence_table()
    for sheet in ("lower", "upper"):
        selected = [row for row in rows if row["sheet"] == sheet]
        gap_deltas = [
            abs(selected[index + 1]["first_gap"] - selected[index]["first_gap"])
            for index in range(2)
        ]
        assert gap_deltas[1] < gap_deltas[0]
        assert selected[-1]["zero_mode_residual"] < 1e-9


def test_shooting_crosscheck_agrees_with_first_order_discretization():
    for row in arch.method_crosscheck():
        assert row["first_level_relative_difference"] < 0.004
        assert len(row["finite_difference"]) == len(row["shooting_AA_dagger"]) == 3


def test_spectrum_artifact_keeps_missing_full_operator_terms_open():
    row = load("spectrum")
    assert row["profile_source"].startswith("nonlinear v6.1.7")
    assert not row["full_C_BHSM_terms_included"]
    assert not row["complete_physical_B1_spectrum"]
    assert "junction-domain term" in row["missing_terms"]


def test_vectorlike_result_is_domain_conditional():
    row = load("vectorlike")
    assert row["selected_zero_modes"] == 1
    assert row["opposite_zero_modes"] == 0
    assert not row["near_zero_partner"]
    assert not row["action_selected_domain"]
    assert not row["global_no_doubling_theorem"]


def test_three_selected_family_copies_do_not_become_no_extra_family_theorem():
    row = load("families")
    assert row["triality_projectors"] == row["spectrum_copy_count"] == 3
    assert row["family_universal"]
    assert not row["FR_topology_used_as_no_extra_family_theorem"]
    assert not row["global_no_additional_family_theorem"]


def test_schur_complement_is_hermitian_for_declared_blocks():
    ll = np.diag([0.0, 0.1])
    lh = np.array([[0.2], [0.3]])
    hh = np.array([[3.0]])
    result = arch.schur_complement(ll, lh, hh, 0.5)
    assert np.allclose(result, result.conj().T)


def test_schur_complement_rejects_nonhermitian_blocks():
    with pytest.raises(ValueError, match="Hermitian"):
        arch.schur_complement([[0, 1], [0, 0]], [[1], [1]], [[2]], 0.1)


def test_minimal_light_sector_generates_no_nontrivial_kprop():
    row = arch.neutral_reduction_ledger()
    assert np.allclose(row["K_prop_light"], np.zeros((3, 3)))
    assert np.allclose(row["Schur_correction"], np.zeros((3, 3)))
    assert not row["nontrivial_L_over_E_generated"]
    assert row["result"] == arch.NEUTRAL_RESULT


def test_heavy_compact_levels_are_not_relabelled_propagation_response():
    row = load("k_prop")
    assert row["energy_scaling"]["direct_transverse_heavy_mode"].endswith(
        "operational mass-squared"
    )
    assert row["energy_scaling"]["minimal_light_Schur_term"] == "zero"
    assert row["energy_scaling"]["propagation_supported_nonlocal_term"] == "not generated"


def test_neutral_phase_is_absent_without_arbitrary_pmns():
    phase = load("phase")
    pmns = load("pmns")
    assert phase["law"].startswith("Delta phi_ij=0")
    assert phase["measured_oscillation_inputs"] == []
    assert not phase["arbitrary_PMNS_inserted"]
    assert not pmns["eigenbasis_unique"]
    assert not pmns["fitted_matrix"]


def test_neutral_transport_invariants_and_energy_scaling_are_classified():
    phase = load("phase")
    source = load("k_prop")
    assert phase["unitarity"]
    assert phase["common_phase_removed"]
    assert phase["path_reversal"] == "adjoint evolution"
    assert phase["static_A0"].endswith("L E^0")
    assert "L/(2E)" in phase["heavy_mode"]
    assert source["energy_scaling"]["light_kinetic"] == "E"
    assert source["energy_scaling"]["static_connection"] == "E^0"
    assert not source["nontrivial_L_over_E_generated"]


def test_zero_rest_mass_classification_is_operationally_honest():
    row = load("zero_rest")
    assert row["minimal_zero_mode"].endswith("no rest pole")
    assert row["heavy_compact_eigenvalues"].endswith("mass-squared")
    assert not row["environment_or_path_dependence_derived"]
    assert row["classification"] == "action remains insufficient to decide"


def test_finite_polarization_diagnostic_remains_flat():
    row = arch.polarization_diagnostic()
    assert not row["fully_renormalized_determinant"]
    assert not row["u_dependence_of_available_normal_operator"]
    assert np.allclose(row["tangent_Hessian"], np.zeros((6, 6)))
    assert row["u_to_minus_u"] == "degenerate"
    assert row["full_C_BHSM_polarization_dependence_open"]


def test_polarization_diagnostic_preserves_covariance_and_anomaly_data():
    row = arch.polarization_diagnostic()
    assert row["SU3_covariant"]
    assert row["triality_universal"]
    assert not row["anomaly_ledger_changed"]
    assert not row["extra_gauge_mode_generated"]
    assert row["constrained_gradient"] == [0.0] * 6


def test_sheet_spectrum_does_not_manufacture_branch_selection():
    row = load("sheets")
    assert not row["negative_modes_found"]
    assert row["both_diagnostic_sheets_admissible"]
    assert row["branch_selection"] == "remains adopted global envelopment axiom"
    assert row["gap_ratio_upper_over_lower"] > 1


def test_connection_overlap_does_not_restore_1_2_7():
    row = arch.connection_overlap()
    assert row["normalized_constant_profile_overlap"] == pytest.approx(1)
    assert not row["tree_level_nonuniversal_correction_derived"]
    assert not row["representation_trace_ratio_1_2_7_restored"]


def test_scalar_berger_hessian_keeps_physical_entries_open():
    row = arch.scalar_berger_hessian_ledger()
    assert row["Hessian_symmetric"]
    assert min(row["kinetic_eigenvalues"]) > 0
    assert not row["physical_Schur_complement_closed"]
    assert row["Q_em_null_direction_preserved"]
    assert not row["Z_g_equals_Z_A_assumed"]


def test_gauge_rank_boundary_is_preserved_without_extra_massless_claim():
    row = arch.scalar_berger_hessian_ledger()
    polarization = arch.polarization_diagnostic()
    assert row["Q_em_null_direction_preserved"]
    assert not polarization["extra_gauge_mode_generated"]
    assert row["matter_induced_beta_shift"] == "not derived"


def test_scalar_wall_cusp_preserved_without_total_r4_claim():
    row = load("wall")
    assert row["A"] == pytest.approx(9.138890145035)
    assert row["total_r4_coefficient"] is None
    assert "regularization/domain dependent" in row["determinant_or_occupation_contribution"]


def test_forward_observable_is_preregistered_not_physical_prediction():
    row = arch.forward_observable()
    assert row["value"] == pytest.approx(1.03426465747)
    assert row["measured_inputs"] == []
    assert not row["fitted"]
    assert not row["physical_prediction"]
    assert "5e-4" in row["falsification"]


def test_integration_ledger_uses_only_allowed_statuses():
    allowed = {
        "Adopted input", "Adopted action invariant", "Derived",
        "Numerically validated", "Needs empirical test", "Rejected",
        "Active construction target",
    }
    rows = load("integration")["rows"]
    assert len(rows) == 27
    assert all(row["status"] in allowed for row in rows)


def test_hidden_input_and_claim_guards():
    row = load("hidden")
    assert row["new_primitives"] == []
    assert row["retained_primitive"] == "y_sigma"
    assert row["measured_inputs"] == []
    assert row["fitted_matrices"] == []
    assert not row["domain_called_action_selected"]
    assert not row["K_prop_inserted"]
    for key, value in arch.GUARDS.items():
        assert value is False, key


def test_new_outputs_do_not_append_retired_generic_slogan():
    texts = [DOC.read_text(encoding="utf-8")]
    texts.extend(
        (ARTIFACTS / filename).read_text(encoding="utf-8")
        for filename in arch.ARTIFACT_FILES.values()
    )
    assert all("FULL_BHSM_NOT_COMPLETE" not in text for text in texts)


def test_frozen_prediction_files_are_byte_identical():
    for path, expected in FROZEN_HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_materialized_artifacts_match_payloads():
    payloads = arch.build_artifact_payloads(ROOT)
    for key, filename in arch.ARTIFACT_FILES.items():
        assert (
            ARTIFACTS / filename
        ).read_text(encoding="utf-8") == arch.deterministic_json(payloads[key])


def test_cli_json_and_markdown():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    command = [
        sys.executable, "-m", "bhsm.interface",
        "boundary-matter-neutral-response-status",
    ]
    json_run = subprocess.run(
        command + ["--format", "json"], cwd=ROOT, env=env, text=True,
        capture_output=True, check=True,
    )
    markdown_run = subprocess.run(
        command + ["--format", "markdown"], cwd=ROOT, env=env, text=True,
        capture_output=True, check=True,
    )
    assert json.loads(json_run.stdout)["primary_result"] == arch.PRIMARY_RESULT
    assert arch.PRIMARY_RESULT in markdown_run.stdout
    assert arch.NEXT_GATE in markdown_run.stdout


def test_doctrine_and_report_share_primary_result_and_next_gate():
    doctrine = DOC.read_text(encoding="utf-8")
    report = load("report")
    assert arch.PRIMARY_RESULT in doctrine
    assert arch.NEXT_GATE in doctrine
    assert report["status"] == arch.PRIMARY_RESULT
    assert report["active_next"] == arch.NEXT_GATE

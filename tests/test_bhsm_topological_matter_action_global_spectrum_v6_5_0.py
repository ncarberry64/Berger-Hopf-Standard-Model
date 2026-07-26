import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface import topological_matter_action_global_spectrum as arch


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_topological_matter_action_global_spectrum_v6_5_0.md"
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


def test_registry_has_exactly_twenty_six_artifacts_and_merged_source():
    payloads = arch.build_artifact_payloads(ROOT)
    assert len(payloads) == 26
    assert set(payloads) == set(arch.ARTIFACT_FILES)
    assert all(row["version"] == "v6.5.0" for row in payloads.values())
    assert payloads["handoff"]["source_main_sha"] == arch.SOURCE_SHA
    assert payloads["handoff"]["source_results_changed"] is False


def test_stack_merge_ledger_preserves_all_scientific_shas_and_branches():
    merge = load("merge")
    assert set(merge["stack"]) == {"v6.2.0", "v6.3.0", "v6.4.0"}
    assert [merge["stack"][key]["pr"] for key in merge["stack"]] == [162, 163, 164]
    assert merge["remote_branches_retained"] is True
    assert "no squash" in merge["merge_method"]
    assert merge["branch_protection"]["force_pushes_allowed"] is False


def test_cleanup_classifies_non_scientific_conditions_without_weakening_guards():
    cleanup = load("cleanup")
    classes = {row["class"] for row in cleanup["errors"]}
    assert "stale stacked base" in classes
    assert "connector permission" in classes
    assert cleanup["generated_rewrites"] == []
    assert cleanup["untracked_scientific_source"] == []
    assert cleanup["guards_weakened"] is False


def test_configuration_space_template_exposes_missing_ontology():
    ledger = arch.configuration_space_ledger()
    assert ledger["formal_definition"].startswith("Q_N")
    assert "ker(linearized constraints)" in ledger["tangent_space"]
    assert ledger["fundamental_group_computed"] is False
    assert ledger["local_M4_field_map_derived"] is False
    assert load("configuration")["status"].endswith("NOT_FIXED_BY_FROZEN_ACTION")


def test_fr_sign_character_is_an_exact_z2_homomorphism_template_only():
    result = arch.fr_template_checks()
    assert arch.fr_character(0) == 1
    assert arch.fr_character(1) == -1
    assert arch.fr_character(2) == 1
    assert result["homomorphism_exact"] is True
    assert result["representative_symplectic_antisymmetric"] is True
    assert result["representative_symplectic_nondegenerate"] is True
    assert result["BHSM_pi1_equals_Z2_derived"] is False
    assert result["BHSM_local_first_order_M4_action_derived"] is False


def test_first_order_source_audit_rejects_circular_and_ad_hoc_routes():
    rows = {row["candidate"]: row for row in arch.first_order_source_candidates()}
    assert rows["P1 Einstein-Hilbert plus GHY transgression"]["verdict"] == (
        "rejected as the matter source"
    )
    assert rows["boundary eta invariant"]["verdict"] == "rejected as circular source"
    assert rows["torsion-induced Clifford coupling"]["present"] is False
    source = load("source")
    assert source["existing_invariant_suffices"] is False
    assert source["configuration_space_route_excluded"] is False


def test_minimal_extension_has_one_ratio_and_no_bulk_dirac_ontology():
    extension = arch.minimal_extension_ledger()
    assert extension["new_invariant_count"] == 1
    assert extension["independent_ratio_count_after_canonical_normalization"] == 1
    assert "collective-coordinate" in extension["field_ontology"]
    assert extension["kill_test"]["Hermitian"] is True
    assert extension["kill_test"]["monopole_free"] is True
    assert extension["kill_test"]["bulk_Dirac_parent_free"] is True
    assert extension["kill_test"]["parent_derived"] is False


def test_y_sigma_is_not_fixed_by_normalization_index_or_topology():
    theorem = arch.y_sigma_dependency_theorem()
    assert "not the invariant ratio" in theorem["canonical_field_normalization"]
    assert "sign" in theorem["index"]
    assert theorem["quantized"] is False
    assert theorem["action_derived"] is False
    assert theorem["independent_new_ratio_count"] == 1


@pytest.mark.parametrize(
    "u",
    [np.eye(7)[0], np.eye(7)[6], np.arange(1, 8, dtype=float)],
)
def test_g2_invariant_u_only_potential_is_exactly_flat(u):
    assert arch.polarization_potential(u) == 0


def test_conditional_composite_potential_has_expected_stationary_hessian():
    v = np.eye(7)[6]
    assert arch.polarization_potential(v, v, 2.0) == pytest.approx(0)
    assert arch.polarization_potential(-v, v, 2.0) == pytest.approx(0)
    assert arch.polarization_potential(np.eye(7)[0], v, 2.0) == pytest.approx(2)
    assert np.allclose(arch.polarization_hessian(2.0), 4.0 * np.eye(6))
    payload = load("polarization")
    assert payload["action_supplies_v"] is False
    assert payload["dynamic_selection"] is False


def test_direct_berger_g2_locking_is_rejected_only_in_declared_bundle_data():
    source = arch.polarization_source_map()
    assert source["canonical_identification_present"] is False
    assert source["equivariant_map_derived"] is False
    assert source["new_spurion_required"] is True
    assert source["result"].endswith("BUNDLE_MISMATCH")


@pytest.mark.parametrize("points", [81, 161, 321])
def test_compact_rectangular_supercharge_has_index_one(points):
    result = arch.compact_supercharge_diagnostic(points=points)
    assert result["rank_A"] == points - 1
    assert result["K_plus_zero_modes"] == 1
    assert result["K_minus_zero_modes"] == 0
    assert result["discrete_index"] == 1
    assert result["zero_mode_norm"] == pytest.approx(1, abs=2e-12)
    assert result["zero_mode_residual"] < 5e-12
    assert result["first_massive_level"] > 0
    assert result["boundary_flux"] == 0


def test_compact_mesh_gap_converges_and_is_not_hard_coded():
    rows = arch.compact_mesh_convergence()
    assert [row["points"] for row in rows] == [81, 161, 321]
    assert abs(rows[-1]["first_massive_level"] - rows[-2]["first_massive_level"]) < 5e-4
    assert all(row["zero_mode_norm"] == 1 for row in rows)
    assert max(row["zero_mode_residual"] for row in rows) < 5e-12


def test_compact_mass_reversal_exposes_boundary_domain_problem():
    result = arch.compact_orientation_audit()
    assert result["selected_is_center_localized"] is True
    assert result["reversed_is_center_localized"] is False
    assert result["action_selects_domain"] is False
    assert "both signs are L2" in result["interpretation"]
    payload = load("doubling")
    assert payload["complete_line_index_one_preserved_as_compact_theorem"] is False


def test_compact_artifact_does_not_claim_actual_b1_global_spectrum():
    payload = load("compact")
    assert payload["actual_B1_domain_selected"] is False
    assert payload["actual_v6_1_7_profile_exported_to_operator"] is False
    assert payload["complete_compact_spectrum_claimed"] is False


def test_global_sector_ledger_does_not_manufacture_sheet_selection():
    sectors = arch.global_sector_ledger()
    assert len(sectors) == 7
    assert all(row["complete_normal_operator"] is False for row in sectors)
    sheets = load("sheets")
    assert sheets["upper_selected_globally"] is False
    assert sheets["lower_excluded"] is False
    assert sheets["adopted_upper_axiom_preserved"] is True


def test_connection_transfer_preserves_exact_traces_and_berger_ratio():
    result = arch.connection_transfer_ledger(beta=0.4)
    assert result["trace_indices"] == {
        "I1_normalized": "2",
        "I1_raw": "10/3",
        "I2": "2",
        "I3": "2",
        "eta_Y": "3/5",
    }
    assert result["exact_Berger_ratio"] == pytest.approx(math.exp(0.8))
    assert result["candidate_1_2_7_restored"] is False
    assert result["Z_g_equals_Z_A_assumed"] is False
    assert result["measured_couplings_used"] is False


def test_su3_transfer_remains_independent_while_hopf_intrinsic_terms_survive():
    su3 = load("su3")
    sp1 = load("sp1")
    u1 = load("u1")
    assert "independent" in su3["tau_intrinsic"]
    assert "8 pi^2 kappa1" in sp1["tau_intrinsic"]
    assert "8 pi^2 kappa1" in u1["tau_intrinsic"]
    assert u1["exact_ratio_to_transverse"] > 1


def test_scalar_berger_generalized_mass_problem_is_positive_representative_only():
    diagnostic = arch.scalar_berger_diagnostic()
    assert np.all(np.asarray(diagnostic["kinetic_eigenvalues"]) > 0)
    assert np.all(np.asarray(diagnostic["representative_mixed_eigenvalues"]) > 0)
    assert diagnostic["representative_only"] is True
    assert diagnostic["physical_Hessian_coefficients_derived"] is False
    assert diagnostic["Higgs_like_mode"] == "not determined"


def test_gauge_mass_rank_preserves_one_qem_null_direction():
    payload = load("gauge")
    assert payload["charged_degeneracy"] is True
    assert payload["one_massive_neutral"] is True
    assert payload["exactly_one_Q_em_null"] is True
    assert payload["additional_accidental_null"] is False
    assert payload["global_profile_normalization_derived"] is False


def test_constraint_reduced_hessian_keeps_negative_mode_count_open():
    payload = load("hessian")
    assert payload["local_principal_health_preserved"] is True
    assert payload["global_negative_mode_count"] is None
    assert payload["junction_bending_operator"] is None
    assert payload["complete_mixed_stability_claimed"] is False


def test_neutral_transport_is_unitary_reversible_and_energy_classified():
    result = arch.neutral_transport((0.0, 0.2, 0.5), 3.0, 2.0)
    assert result["unitary"] is True
    assert result["path_reversal_is_adjoint"] is True
    assert result["path_length_scaling"] == "L"
    assert result["energy_scaling"] == "E^0"
    assert result["measured_Delta_m_squared_used"] is False
    payload = load("neutrino")
    assert payload["L_over_E_reproduced"] is False
    assert payload["CKM_PMNS_conflated"] is False


def test_absolute_scale_and_r4_remain_open_without_reviving_retired_target():
    scale = load("scale")
    r4 = load("r4")
    assert scale["dimensionless_transfer_closed"] is False
    assert scale["Z_g_equals_Z_A_assumed"] is False
    assert scale["numerical_absolute_scale"] is None
    assert r4["new_r4_components_derived"] == []
    assert r4["flat_kink_27_35_revived"] is False


def test_integration_ledger_uses_only_declared_statuses_and_no_counting_claim():
    payload = load("integration")
    allowed = set(payload["allowed_statuses"])
    assert len(payload["rows"]) == 20
    assert {row["status"] for row in payload["rows"]} <= allowed
    assert payload["counting_rows_implies_completion"] is False
    assert payload["full_BHSM_complete"] is False


def test_hidden_input_and_global_safeguards():
    hidden = load("hidden")
    assert hidden["measured_inputs"] == []
    assert hidden["fits"] == []
    assert hidden["new_derived_primitives"] == []
    assert hidden["representative_numerics_are_proof_of_physical_spectrum"] is False
    assert all(value is False for value in arch.GUARDS.values())


def test_frozen_prediction_files_are_byte_identical():
    for path, expected in FROZEN_HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_materialized_artifacts_match_deterministic_payloads():
    payloads = arch.build_artifact_payloads(ROOT)
    for key, filename in arch.ARTIFACT_FILES.items():
        path = ARTIFACTS / filename
        assert path.read_text(encoding="utf-8") == arch.deterministic_json(payloads[key])


def test_cli_json_and_markdown():
    env = dict(**__import__("os").environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    command = [
        sys.executable,
        "-m",
        "bhsm.interface",
        "topological-matter-global-spectrum-status",
    ]
    json_run = subprocess.run(
        command + ["--format", "json"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(json_run.stdout)["primary_result"] == arch.PRIMARY_RESULT
    markdown_run = subprocess.run(
        command + ["--format", "markdown"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    assert arch.PRIMARY_RESULT in markdown_run.stdout
    assert arch.COMPLETION_GATE in markdown_run.stdout


def test_doctrine_and_report_share_primary_status_and_concrete_gate():
    doctrine = DOC.read_text(encoding="utf-8")
    report = load("report")
    assert arch.PRIMARY_RESULT in doctrine
    assert arch.COMPLETION_GATE in doctrine
    assert report["status"] == arch.PRIMARY_RESULT
    assert report["completion_gate"] == arch.COMPLETION_GATE
    assert "FULL_BHSM_NOT_COMPLETE" in doctrine

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface import topological_fr_neutral_dispersion as arch


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_topological_fr_neutral_dispersion_v6_6_0.md"
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


def test_registry_has_exactly_twenty_six_payloads():
    payloads = arch.build_artifact_payloads(ROOT)
    assert len(payloads) == 26
    assert set(payloads) == set(arch.ARTIFACT_FILES)
    assert all(row["version"] == "v6.6.0" for row in payloads.values())


def test_pr165_history_preserving_handoff():
    row = load("merge")
    assert row["pr"] == 165
    assert row["merge_method"] == "merge commit"
    assert all(row["checks"][key] == "pass" for key in ("pytest", "native", "ROOT"))
    assert row["remote_branch_retained"]
    assert not row["force_push"] and not row["rebase"] and not row["squash"]


def test_selected_configuration_space_is_explicit():
    row = arch.mapping_space_identification()
    assert row["component"] == "degree N in Z"
    assert row["target"].endswith("SU2")
    assert row["gauge_quotient"] == "none beyond the based condition"
    assert row["identification_status"] == "Adopted BHSM identification"


def test_mapping_space_adjunction_derives_z2_route():
    row = arch.mapping_space_pi1()
    assert row["group"] == "Z2"
    assert row["order"] == 2
    assert any("smash" in step for step in row["route"])
    assert any("pi4(S3)" in step for step in row["route"])
    assert row["derived_from_adjunction_plus_established_pi4"]
    assert not row["hard_coded_as_assumption"]


@pytest.mark.parametrize("a,b", [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_nontrivial_fr_character_is_homomorphism(a, b):
    assert arch.fr_character(a + b) == arch.fr_character(a) * arch.fr_character(b)


@pytest.mark.parametrize("charge,sign", [(0, 1), (1, -1), (2, 1), (-1, -1), (-2, 1)])
def test_fr_rotation_exchange_parity(charge, sign):
    row = arch.loop_classification(charge)
    assert row["two_pi_spatial_rotation"]["sign"] == sign
    assert row["identical_soliton_exchange"]["sign"] == sign
    assert row["two_pi_internal_target_rotation"]["sign"] == sign


def test_unrelated_discrete_actions_are_not_identified_with_fr_loop():
    row = arch.loop_classification(1)
    assert row["triality_cycle"]["class"] != 1
    assert row["wall_orientation_reversal"]["class"] != 1
    assert not row["exactly_one_representation_per_particle_slot"]
    assert not row["additional_family_sectors_excluded"]


def test_conjugation_preserves_fr_parity():
    for charge in range(1, 5):
        assert (
            arch.loop_classification(charge)["two_pi_spatial_rotation"]["sign"]
            == arch.loop_classification(-charge)["two_pi_spatial_rotation"]["sign"]
        )


def test_fr_bundle_is_global_and_local_berry_curvature_is_zero():
    row = arch.collective_coordinate_audit()
    omega = np.asarray(row["local_curvature_omega"])
    assert row["metric_positive"]
    assert row["FR_holonomy"] == -1
    assert np.array_equal(omega, np.zeros((6, 6)))
    assert not row["continuous_Berry_term_derived"]


def test_architecture_b_is_decisive_and_names_obstruction():
    row = arch.architecture_decision()
    assert row["decision"] == "Architecture B"
    assert not row["architecture_A"]["local_frame_and_transition_functions_derived"]
    assert "transgression" in row["architecture_A"]["verdict"]
    assert row["architecture_B"]["new_dimensionless_primitives"] == 1


def test_minimal_invariant_is_adopted_not_parent_derived():
    row = arch.minimal_invariant()
    assert "not parent-derived" in row["status"]
    assert row["family_universal"]
    assert row["preserves_Y_BH"] and row["preserves_Q_em"]
    assert row["sigma_wall_odd"]
    assert not row["beta_can_replace_sigma"]
    assert not row["new_dimensional_scale"]
    assert not row["physical_bulk_Dirac_parent"]


def test_y_sigma_is_exactly_one_exposed_primitive():
    row = arch.y_sigma_theorem()
    assert row["classification"] == "independent dimensionless primitive"
    assert row["primitive_count"] == 1
    assert row["sector_dependent_Yukawa_coefficients"] == 0
    assert row["Z_sigma_relation"] == "not derived"


def test_compact_sweep_preserves_index_and_positive_gap():
    rows = arch.compact_sweep()
    assert len(rows) == 3
    assert all(row["index"] == 1 and row["zero_modes"] == 1 for row in rows)
    assert all(row["first_massive_level"] > 0 for row in rows)
    assert all(row["zero_mode_residual"] < 1e-10 for row in rows)


def test_compact_claim_boundary_preserves_full_b1_gate():
    row = load("compact")
    assert not row["actual_full_B1_cap_spectrum"]
    assert not row["domain_action_selected"]
    assert "not available" in row["upper_lower_sheet_dependence"]


def test_common_phase_removal_is_traceless_and_shift_invariant():
    k_value = arch.representative_response()
    shifted = k_value + 7.0 * np.eye(3)
    assert np.allclose(np.trace(arch.remove_common_phase(k_value)), 0)
    assert np.allclose(
        arch.remove_common_phase(k_value),
        arch.remove_common_phase(shifted),
    )


def test_neutral_hamiltonian_rejects_nonhermitian_input():
    with pytest.raises(ValueError, match="Hermitian"):
        arch.neutral_hamiltonian(2.0, [[0, 1], [0, 0]])


def test_neutral_hamiltonian_rejects_nonpositive_energy():
    with pytest.raises(ValueError, match="positive"):
        arch.neutral_hamiltonian(0.0, np.eye(2))


def test_neutral_transport_is_unitary_and_reversible():
    k_value = arch.representative_response()
    U = arch.unitary_segment(4.0, 3.0, k_value)
    reverse = arch.unitary_segment(4.0, -3.0, k_value)
    assert np.allclose(U.conj().T @ U, np.eye(3))
    assert np.allclose(reverse, U.conj().T)


def test_path_refinement_is_reparameterization_invariant():
    k_value = arch.representative_response()
    whole = arch.path_transport(5.0, [(3.0, k_value)])
    split = arch.path_transport(5.0, [(1.0, k_value), (2.0, k_value)])
    assert np.allclose(whole, split)


def test_kprop_phase_halves_when_energy_doubles():
    row = arch.propagation_diagnostic()
    assert row["phase_halving_at_double_energy"]
    assert row["leading_energy_scaling"] == "E^-1 when flavor-dependent A0 is absent"
    assert row["static_A0_scaling"].startswith("L E^0")


def test_static_a0_does_not_masquerade_as_l_over_e():
    row = load("phase")
    assert row["condition"].startswith("flavor-dependent A0 absent")
    assert not row["prediction"]
    assert not row["measured_oscillation_inputs"]


def test_zero_rest_mass_audit_does_not_relabel_vacuum_mass():
    row = arch.zero_rest_mass_audit()
    assert "mass-squared" in row["constant_Lorentz_invariant_vacuum_K"]
    assert not row["current_action_derives_path_dependent_K_prop"]
    assert "cannot decide" in row["result"]


def test_profile_overlap_is_normalized_but_diagnostic():
    row = arch.profile_overlap()
    assert row["normalization"] == pytest.approx(1.0, abs=1e-12)
    assert 0 < row["overlap"] < 1
    assert not row["action_derived_B1_profile"]
    assert not row["physical_transfer_coefficient_derived"]


def test_dynamic_polarization_not_manufactured():
    row = load("polarization")
    assert not row["equivariant_map_supplied"]
    assert row["induced_potential"] == 0
    assert row["result"] == "polarization remains a flat adopted background"


def test_pmns_ckm_remain_structural_and_unfitted():
    pmns = load("pmns")
    separate = load("separation")
    assert not pmns["arbitrary_free_matrix_inserted"]
    assert not pmns["measured_PMNS_used"]
    assert pmns["formula"] != separate["CKM"]


def test_integrated_ledger_keeps_full_bhsm_open():
    row = load("integration")
    assert row["status"] == "FULL_BHSM_NOT_COMPLETE"
    assert len(row["rows"]) == 23
    assert not any(item["status"] == "Full BHSM complete" for item in row["rows"])


def test_hidden_input_and_claim_guards():
    row = load("hidden")
    assert row["new_primitives"] == [{"count": 1, "dimension": 0, "name": "y_sigma"}]
    assert row["measured_inputs"] == []
    assert row["fitted_matrices"] == []
    for key, value in arch.GUARDS.items():
        assert value is False, key


def test_frozen_prediction_files_are_byte_identical():
    for path, expected in FROZEN_HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_materialized_artifacts_match_payloads():
    payloads = arch.build_artifact_payloads(ROOT)
    for key, filename in arch.ARTIFACT_FILES.items():
        expected = arch.deterministic_json(payloads[key])
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == expected


def test_cli_json_and_markdown():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    command = [sys.executable, "-m", "bhsm.interface",
               "topological-fr-neutral-dispersion-status"]
    json_run = subprocess.run(
        command + ["--format", "json"], cwd=ROOT, text=True,
        env=env, capture_output=True, check=True,
    )
    markdown_run = subprocess.run(
        command + ["--format", "markdown"], cwd=ROOT, text=True,
        env=env, capture_output=True, check=True,
    )
    assert json.loads(json_run.stdout)["primary_result"] == arch.PRIMARY_RESULT
    assert arch.PRIMARY_RESULT in markdown_run.stdout
    assert "FULL_BHSM_NOT_COMPLETE" in markdown_run.stdout


def test_doctrine_and_report_share_primary_status():
    doctrine = DOC.read_text(encoding="utf-8")
    report = load("report")
    assert arch.PRIMARY_RESULT in doctrine
    assert report["status"] == arch.PRIMARY_RESULT
    assert report["architecture"] == "B"
    assert "FULL_BHSM_NOT_COMPLETE" in doctrine

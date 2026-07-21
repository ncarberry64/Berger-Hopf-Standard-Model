import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import energy_geometry_confinement_invariant as eg


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_energy_geometry_confinement_invariant_v6_0_3.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / eg.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths += [ARTIFACTS / name for name in eg.ARTIFACT_FILES.values()]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_artifact_package_is_complete_and_guarded():
    assert len(eg.ARTIFACT_FILES) == 16
    for key in eg.ARTIFACT_FILES:
        payload = load(key)
        assert payload["version"] == "v6.0.3", key
        assert payload["primary_result"] == "BHSM_ENERGY_GEOMETRY_FINITE_INVARIANT_FAMILY_IDENTIFIED"
        assert payload["threshold_result"] == "BHSM_PHYSICALITY_THRESHOLD_ARCHITECTURE_IDENTIFIED"
        assert payload["preserved_results"] == [
            "BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED",
            "BHSM_ENERGY_GEOMETRY_PHYSICALITY_SOURCE_NOT_DERIVED",
        ]
        assert payload["empirical_inputs_used"] is False
        assert payload["physical_spacetime_formation_claimed"] is False
        assert payload["absolute_unit_generated"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialization_round_trip_is_deterministic():
    built = eg.build_artifact_payloads(ROOT)
    for key, name in eg.ARTIFACT_FILES.items():
        assert (ARTIFACTS / name).read_text(encoding="utf-8") == eg.deterministic_json(built[key])


def test_sigma_domain_is_explicit_and_bulk_is_strongest_audit_domain():
    payload = load("sigma_domain")
    rows = {row["id"]: row for row in payload["rows"]}
    assert set(rows) == {"A", "B", "C", "D", "E"}
    assert rows["A"]["status"] == "STRONGEST_ADMISSIBLE_DOMAIN"
    assert rows["B"]["status"] == "CANNOT_GENERATE_ITS_OWN_BOUNDARY"
    assert rows["D"]["status"] == "SPECTRAL_SUBBRANCH_OF_A_NOT_INDEPENDENT_DOMAIN"
    assert payload["physical_domain_selected_by_BHSM"] is False


def test_every_candidate_coupling_declares_action_hessian_parity_and_source():
    rows = load("couplings")["rows"]
    assert len(rows) == 9
    for row in rows:
        assert row["domain"] and row["scalar_status"] and row["coefficient_dimension"]
        assert row["family"] and row["action_term"] and row["hessian"]
        assert row["classification"] and row["parity"] and row["source_status"]
    assert load("couplings")["selected_family"] is None


@pytest.mark.parametrize("source_power,coefficient_power", [(-2, -6), (-4, -4), (-6, -2), (-8, 0)])
def test_curvature_and_density_coefficient_dimensions_close(source_power, coefficient_power):
    assert eg.interaction_coefficient_length_power(source_power) == coefficient_power
    assert coefficient_power + source_power == -8


def test_complete_operator_has_second_order_principal_symbol_and_all_sources():
    payload = load("operator")
    assert payload["euclidean_operator"].startswith("H_sigma^(0)=-nabla_A(Z_0 nabla^A)")
    assert payload["principal_symbol"] == "Z_0 G^AB k_A k_B"
    assert set(payload["components"]) == {"baseline", "geometric", "matter", "boundary", "collar", "flux", "other"}
    assert payload["pointwise_threshold_sufficient"] is False


def test_hessian_eigenvalue_combines_gradient_and_source_terms():
    assert eg.hessian_eigenvalue(2.0, 3.0, 5.0, -1.0, 0.5) == pytest.approx(10.5)
    with pytest.raises(ValueError):
        eg.hessian_eigenvalue(0.0, 1.0, 0.0)
    with pytest.raises(ValueError):
        eg.hessian_eigenvalue(1.0, -1.0, 0.0)


def test_quadratic_operator_is_the_second_action_variation():
    eigenvalue = -3.25
    step = 1.0e-4
    second_difference = (
        eg.quadratic_mode_action(step, eigenvalue)
        - 2.0 * eg.quadratic_mode_action(0.0, eigenvalue)
        + eg.quadratic_mode_action(-step, eigenvalue)
    ) / step**2
    assert second_difference == pytest.approx(eigenvalue)


def test_self_adjointness_and_boundary_form_are_explicit():
    payload = load("operator")
    assert "boundary_form" in payload
    assert "Robin" in payload["self_adjointness"]
    assert "interface transmission" in payload["self_adjointness"]
    assert "H^2(M8)" in payload["domain"]


def test_trace_source_follows_even_conformal_metric_and_vanishes_for_radiation():
    assert eg.conformal_trace_hessian(2.5, 0.0) == 0.0
    assert eg.conformal_trace_hessian(2.5, -4.0) == -10.0
    row = next(row for row in load("admissibility")["rows"] if row["candidate"] == "T")
    assert row["radiation_sensitive"] == "no when T=0"


def test_matter_lagrangian_shift_candidate_is_rejected():
    row = next(row for row in load("admissibility")["rows"] if row["candidate"] == "L_m")
    assert row["verdict"] == "REJECTED_WITHOUT_SHIFT_REDEFINITION_THEOREM"


def test_energy_density_does_not_introduce_an_undeclared_time_direction():
    row = next(row for row in load("admissibility")["rows"] if "J_AJ" in row["candidate"])
    assert row["verdict"] == "BLOCKED_UNDECLARED_TIMELIKE_STRUCTURE"


def test_lorentzian_stress_square_sign_is_not_called_positive():
    row = next(row for row in load("admissibility")["rows"] if row["candidate"].startswith("T_AB T^AB"))
    assert "indefinite" in row["radiation_sensitive"]


def test_interface_pressure_requires_dynamic_interface_normal_and_junction():
    row = next(row for row in load("admissibility")["rows"] if row["candidate"] == "Delta p_n")
    assert row["verdict"] == "BLOCKED_INTERFACE_NOT_DERIVED"
    assert "junction" in row["action_native"]


def test_fixed_flux_and_fixed_charge_hessians_remain_opposite():
    fixed_f = eg.top_form_hessian(3.0, 4.0, 2, "fixed_f")
    fixed_q = eg.top_form_hessian(3.0, 4.0, 2, "fixed_Q")
    assert fixed_f == pytest.approx(-fixed_q)
    with pytest.raises(ValueError):
        eg.top_form_hessian(1.0, 1.0, 2, "unknown")


def test_variational_completions_are_not_free_tension():
    row = next(row for row in load("couplings")["rows"] if row["family"] == "extrinsic_collar")
    assert "not free tension" in row["source_status"]


def test_local_interface_quasilocal_and_global_classes_do_not_mix():
    payload = load("locality")
    assert "R" in payload["local"]
    assert "Delta p_n" in payload["interface"]
    assert "enclosed energy" in payload["quasilocal"]
    assert "total top-form flux Q" in payload["global"]
    assert "cannot be summed" in payload["illegal_mixing_rule"]


def test_no_single_confinement_scalar_is_forced():
    payload = load("admissibility")
    assert payload["selected_C_EG"] is None
    assert payload["single_scalar_reduction_proved"] is False
    assert payload["status"] == "MULTIPLE_INDEPENDENT_INVARIANTS_SURVIVE_CONDITIONALLY"


def test_harmonic_constructive_interference_is_a_precise_unproved_selection_test():
    spectral = load("spectrum")["harmonic_selection_test"]
    assert "C_mn" in spectral["matrix"]
    assert "off-diagonal" in spectral["coherence"]
    assert "2^p" in spectral["octave"]
    assert spectral["verdict"] == "CANDIDATE_SELECTION_THEOREM_NOT_DERIVED"
    assert "not an action selection law" in spectral["order_of_magnitude"]


def test_two_mode_constructive_coherence_lowers_the_lowest_channel():
    low, high = eg.symmetric_two_mode_eigenvalues(3.0, 5.0, 2.0)
    assert low < 3.0
    assert high > 5.0
    assert low + high == pytest.approx(8.0)


def test_reduced_operator_diagnostics_cover_required_source_branches():
    rows = load("operator")["reduced_diagnostics"]
    assert set(rows) == {
        "homogeneous_bulk", "finite_region", "collar_mode", "curvature_branch",
        "trace_branch", "top_form_fixed_f", "top_form_fixed_Q", "harmonic_two_mode",
    }
    assert "trace-free" in rows["trace_branch"]
    assert "opposite" in rows["top_form_fixed_Q"]


def test_spectral_problem_uses_lowest_physical_not_pointwise_mode():
    payload = load("spectrum")
    assert payload["lambda_phys"].startswith("lowest non-gauge normalizable")
    assert payload["marginal"] == "lambda_phys=0"
    assert payload["control_variable"] is None
    assert payload["threshold_derived"] is False


def test_finite_enclosure_gradient_term_changes_threshold():
    assert eg.finite_radius_threshold(2.0, 3.0, -12.0) == pytest.approx(1.0)
    assert eg.finite_radius_threshold(2.0, 3.0, 1.0) is None
    assert eg.finite_radius_threshold(0.0, 3.0, -1.0) is None
    with pytest.raises(ValueError):
        eg.finite_radius_threshold(-1.0, 1.0, -1.0)
    payload = load("finite")
    assert "q_0^2/L^2" in payload["formula"]
    assert payload["absolute_unit"] is None


def test_negative_mode_is_stabilized_only_conditionally_by_positive_quartic():
    branch = eg.quartic_mode_branch(-2.0, 8.0)
    assert branch["amplitudes"] == pytest.approx([-0.5, 0.5])
    assert branch["energy_shift"] == pytest.approx(-0.125)
    assert branch["formed_mode_hessian"] == pytest.approx(4.0)
    assert eg.quartic_mode_branch(1.0, 8.0)["amplitudes"] == []
    with pytest.raises(ValueError):
        eg.quartic_mode_branch(-1.0, 0.0)


def test_planar_domain_wall_thickness_and_tension_follow_from_action():
    wall = eg.planar_wall_diagnostics(1.0, -2.0, 8.0)
    assert wall["vacuum"] == pytest.approx(0.5)
    assert wall["thickness"] == pytest.approx(1.0)
    assert wall["tension"] == pytest.approx(1.0 / 3.0)
    with pytest.raises(ValueError):
        eg.planar_wall_diagnostics(1.0, 1.0, 8.0)
    assert load("wall")["envelope_solution_derived"] is False


def test_imposed_boundary_is_not_called_emergent():
    payload = load("emergent")
    assert payload["status"] == "EMERGENT_BOUNDARY_NOT_DERIVED"
    assert payload["requirements_closed"] is False
    assert payload["imposed_S7_relabelled_emergent"] is False


def test_coupled_solution_and_negative_modes_remain_open():
    payload = load("coupled")
    assert set(payload["families"]) == {"P1", "P2", "P3"}
    assert payload["stationary_solution"] is None
    assert payload["negative_modes"] is None
    assert payload["physical_branch"] is None
    assert payload["P_family_selected_for_threshold"] is False


def test_parent_matter_action_is_exact_next_dependency_for_energy_trigger():
    payload = load("matter")
    assert payload["status"] == "PARENT_MATTER_ACTION_INDISPENSABLE_FOR_ENERGY_TRIGGER_SELECTION"
    assert "covariant conserved parent matter action" in payload["minimal_next_action"]
    assert payload["fabricated_source_used"] is False


def test_parent_to_v5_map_is_not_reverse_engineered():
    payload = load("v5_map")
    assert payload["A_ST_minus_2"] == "not parent-derived"
    assert payload["G_ST_8"] == "not parent-derived"
    assert payload["sigma_half"] == "not parent-derived"
    assert payload["reverse_engineering_used"] is False


def test_formation_release_and_de_enveloping_remain_distinct():
    payload = load("thresholds")
    assert [row["name"] for row in payload["rows"]] == [
        "physicality formation",
        "primordial release",
        "black-hole de-enveloping",
    ]
    assert len({row["background"] for row in payload["rows"]}) == 3
    assert payload["one_eigenvalue_reused"] is False


def test_scale_and_hidden_inputs_are_explicit():
    payload = load("scale")
    assert len(payload["rows"]) == 7
    assert "Z_0" in payload["hidden_inputs"]
    assert "mode normalization and q_0" in payload["hidden_inputs"]
    assert payload["one_common_parent_scale_proved"] is False
    assert payload["absolute_unit"] is None


def test_v602_artifacts_are_not_rewritten_by_builder():
    paths = list(ARTIFACTS.glob("*v6_0_2.json"))
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    eg.build_artifact_payloads(ROOT)
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    assert paths and before == after


def test_report_stops_at_finite_family_and_routes_to_selection_theorem():
    report = load("report")
    assert report["status"] == "BHSM_ENERGY_GEOMETRY_FINITE_INVARIANT_FAMILY_IDENTIFIED"
    assert report["selected_C_EG"] is None
    assert report["completion_gate_status"] == "V6_0_3_STOP_FINITE_INVARIANT_FAMILY_THRESHOLD_ARCHITECTURE_ONLY"
    assert report["recommended_next_branch"] == "bhsm-physicality-coupling-selection-theorem-v6-0-4"


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "energy-geometry-confinement-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == "BHSM_ENERGY_GEOMETRY_FINITE_INVARIANT_FAMILY_IDENTIFIED"
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "BHSM v6.0.3 Energy--Geometry" in markdown.stdout


def test_public_ledgers_preserve_claim_boundary_and_command():
    text = focused_text()
    assert "BHSM_ENERGY_GEOMETRY_FINITE_INVARIANT_FAMILY_IDENTIFIED" in text
    assert "BHSM_PHYSICALITY_THRESHOLD_ARCHITECTURE_IDENTIFIED" in text
    assert "energy-geometry-confinement-status" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    forbidden = [
        "v6.0.3 derives physical spacetime",
        "unique C_EG is derived",
        "Lorentzian signature emerged",
        "primordial release is derived",
        "full BHSM completion is achieved",
    ]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest

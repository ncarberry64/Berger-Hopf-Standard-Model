import hashlib
import json
import math
from pathlib import Path

import pytest

from bhsm.interface import primordial_boundary_tension_action_source_closure as bt


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key: str):
    return json.loads((ARTIFACTS / bt.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text() -> str:
    paths = [ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "CLI_REFERENCE.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "docs" / "bhsm_primordial_boundary_tension_action_source_closure_v5_12.md"]
    paths.extend(ARTIFACTS / name for name in bt.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_original_result_is_preserved_and_recycling_result_is_candidate_level():
    report = load("construction_report")
    assert report["primary_result"] == "BHSM_PRIMORDIAL_BOUNDARY_SOURCE_NOT_CLOSED"
    assert report["recycling_result"] == "BHSM_SPACETIME_RECYCLING_CONSTRAINT_ARCHITECTURE_IDENTIFIED"
    assert report["black_hole_spacetime_recycling_candidate"]["core_source"] is None


@pytest.mark.parametrize("d_bulk", [2, 3, 4, 7])
def test_top_form_degree_matches_declared_bulk_dimension(d_bulk):
    assert bt.top_form_degrees(d_bulk) == (d_bulk - 1, d_bulk)
    assert bt.top_form_local_degrees_of_freedom(d_bulk) == 0
    with pytest.raises(ValueError):
        bt.top_form_degrees(1)


def test_four_dimensional_specialization_is_not_promoted_to_physical_domain():
    payload = load("top_form_dimension")
    assert payload["d_B"] is None
    assert payload["candidate_d_B_4"] == {"potential": "C_3", "field_strength": "F_4", "adopted_as_physical_dimension": False}
    assert payload["natural_units_close_missing_dimensions"] is False


def test_top_form_coefficient_dimensions_follow_the_action_measure():
    dims = load("top_form_dimension")["dimensions"]
    assert dims["F"] == "[C] L^-1"
    assert dims["Z_F"] == "[A] L^(2-d_B) [C]^-2"
    assert dims["rho_rec"] == "[A] L^-d_B for a spacetime action density"
    assert dims["integrated_flux_Q"] == "[C] L^(d_B-1)"


def test_homogeneous_top_form_solution_follows_source_free_equation():
    action = load("recycling_action")
    assert action["field_equation"].startswith("d(Z_F star F")
    assert action["source_free_solution"] == "F_[d_B]=f vol_B and d(Z_F f)=0"
    assert "globally constant" in action["connected_region_result"]
    assert action["candidate_not_adopted_as_established_action"] is True


def test_recycling_stress_is_the_candidate_action_metric_variation():
    data = bt.top_form_lorentzian_stress_data(3.0, 2.0)
    assert data == {"metric_coefficient": -6.0, "energy_density": 6.0, "pressure": -6.0}
    stress = load("recycling_stress")
    assert stress["stress_tensor"].startswith("T_AB=Z_F/(d_B-1)!")
    assert stress["lorentzian_top_form_identity"]["T_AB"] == "-(Z_F f^2/2)G_AB"
    assert stress["outward_pressure_proved"] is False


def test_fixed_f_energy_variation_gives_negative_mechanical_pressure():
    L, Z, f, v, nu = 1.7, 2.0, 0.8, 1.3, 3.0
    pressure = bt.top_form_pressure(L, Z, f, v, nu, "fixed_f")
    volume = v * L**nu
    eps = volume * 1e-6
    energy_plus = 0.5 * Z * f**2 * (volume + eps)
    energy_minus = 0.5 * Z * f**2 * (volume - eps)
    assert pressure == pytest.approx(-(energy_plus - energy_minus) / (2 * eps))


def test_fixed_Q_energy_variation_gives_positive_pressure():
    L, Z, Q, v, nu = 1.4, 1.5, 0.9, 1.2, 3.0
    volume = v * L**nu
    eps = volume * 1e-6
    numeric = -(0.5 * Z * Q**2 / (volume + eps) - 0.5 * Z * Q**2 / (volume - eps)) / (2 * eps)
    assert bt.top_form_pressure(L, Z, Q, v, nu, "fixed_Q") == pytest.approx(numeric)


@pytest.mark.parametrize("ensemble", ["fixed_f", "fixed_Q"])
def test_radial_force_and_stiffness_are_energy_derivatives(ensemble):
    L, Z, amplitude, v, nu = 1.6, 1.4, 0.7, 1.1, 2.5
    eps = 1e-4
    energy = lambda radius: bt.top_form_energy(radius, Z, amplitude, v, nu, ensemble)
    numeric_force = -(energy(L + eps) - energy(L - eps)) / (2 * eps)
    numeric_stiffness = (energy(L + eps) - 2 * energy(L) + energy(L - eps)) / eps**2
    force, stiffness = bt.top_form_radial_force_and_stiffness(L, Z, amplitude, v, nu, ensemble)
    assert force == pytest.approx(numeric_force, rel=1e-7)
    assert stiffness == pytest.approx(numeric_stiffness, rel=1e-6)


def test_ensemble_is_not_silently_selected():
    stress = load("recycling_stress")["boundary_ensemble"]
    assert stress["BHSM_choice"] is None
    assert stress["fixed_local_f"]["direct_delta_p"] == 0.0
    assert "rank-one" in stress["fixed_integrated_flux_Q"]["response"]


def test_core_current_conservation_is_required_but_not_derived():
    source = load("core_source")
    assert source["current_conservation"].startswith("dJ_core=0")
    assert source["source_conservation_derived_for_BHSM_core"] is False
    assert all(value is False for value in source["BHSM_support"].values())


def test_core_worldline_does_not_match_top_form_electric_source():
    dims = load("top_form_dimension")
    assert dims["black_hole_worldline_matches_source"] is False
    assert "spatial (d_B-2)-brane" in dims["source_worldvolume"]


def test_flux_jump_follows_conditional_source_equation():
    assert bt.conditional_flux_jump(0.2, 0.6, 3.0) == pytest.approx(0.4)
    assert bt.conditional_flux_jump(0.2, 0.6, 3.0, -1.0) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        bt.conditional_flux_jump(0.0, 1.0, 0.0)
    source = load("core_source")
    assert source["q_rec"]["classification"] == "UNSUPPORTED"
    assert source["quantization"]["automatic"] is False


def test_constraint_has_no_local_wave_and_no_superluminal_signal_claim():
    causal = load("causal_constraint")
    canonical = causal["canonical_decomposition"]
    assert canonical["local_degrees_of_freedom"] == 0
    assert "global" in canonical["global_degree_of_freedom"]
    assert causal["superluminal_signal"] is False
    assert causal["no_signal_test"]["local_observable_transmits_message_outside_causal_domain"] is False
    assert causal["nonlocal_action_required"] is False


def test_conserved_charges_and_information_are_not_erased():
    doctrine = load("core_source")["information_doctrine"]
    assert "gauge charge" in doctrine["preserved"]
    assert doctrine["fundamental_information_destroyed"] is False
    assert doctrine["unitarity_status"].startswith("open")


def test_recycling_pressure_enters_shape_equation_through_delta_p_sign():
    shape = load("shape_equation")
    assert shape["recycling_addition"] == "-Delta p_rec; not +p_rec by hand"
    term = next(row for row in shape["terms"] if row["name"] == "recycling_pressure")
    assert term["formula"].startswith("-Delta p_rec")
    assert term["status"].endswith("PROJECTION_OPEN")


def test_fixed_Q_surface_response_is_rank_one_and_not_mode_universal():
    overlaps = [2.0, 0.0, -0.5]
    matrix = bt.homogeneous_pressure_hessian(overlaps, -0.25)
    assert matrix[1] == [0.0, 0.0, 0.0]
    assert matrix[0][2] == pytest.approx(0.25)
    hessian = load("surface_hessian")["recycling_terms"]
    assert hessian["mode_independent_shift"] is False
    assert hessian["higher_zero_mean_modes"].startswith("zero direct")


def test_surface_hessian_pressure_response_equals_pressure_derivative():
    L, Z, Q, v, nu = 1.8, 1.2, 0.7, 1.1, 3.0
    volume = v * L**nu
    eps = volume * 1e-6
    pressure_at_volume = lambda V: 0.5 * Z * Q**2 / V**2
    numeric = (pressure_at_volume(volume + eps) - pressure_at_volume(volume - eps)) / (2 * eps)
    analytic = -Z * Q**2 / volume**3
    assert numeric == pytest.approx(analytic, rel=1e-9)
    assert bt.homogeneous_pressure_hessian([1.0], analytic) == [[analytic]]


def test_recycling_L_scaling_is_derived_from_symbolic_volume_measure():
    crossing = load("release_threshold")["recycling_competing_scaling"]
    assert crossing["volume_law"] == "V(L,a)=v(a)L^nu with nu not fixed until the physical canonical domain closes"
    assert "L^(nu-2)" in crossing["fixed_f_radial_stiffness"]
    assert "L^(-nu-2)" in crossing["fixed_Q_radial_stiffness"]
    assert crossing["candidate_root_formula"] is None


def test_primordial_and_late_time_regimes_are_not_identified():
    regimes = load("recycling_regimes")
    assert regimes["primordial"]["surface_crossing"] is None
    assert regimes["late_time"]["incremental_flux_jump"] is None
    assert regimes["regimes_identified"] is False
    assert regimes["same_candidate_action_different_initial_data_possible"] is True


def test_positive_flux_energy_is_not_the_zero_point_floor():
    zero = load("zero_point_flux")
    assert zero["continuous_positive_Z_model"]["minimum_flux"] == 0.0
    assert "above the minimum" in zero["continuous_positive_Z_model"]["nonzero_f"]
    assert zero["energy_returned_to_exact_floor_while_stored_as_positive_pressure"] is False
    assert zero["zpv_reset_established"] is False


def test_closed_energy_ledger_conserves_without_inventing_transfer_fraction():
    assert bt.closed_energy_balance(-10.0, 4.0, 3.0, 2.0, 1.0) == pytest.approx(0.0)
    ledger = load("energy_conversion")
    assert ledger["recycling_global_ledger"]["action_derived_transfer"] is False
    assert ledger["core_event_ledger"]["epsilon_rec"] is None
    assert ledger["core_event_ledger"]["epsilon_rec_status"] == "UNRESOLVED_NOT_FITTED"


def test_entropy_and_unitarity_are_not_overclaimed():
    info = load("energy_conversion")["charge_information_entropy"]
    assert info["exact_charges_erased"] is False
    assert info["complete_state_unitarity"] is None
    assert info["entropy_destroyed"] is False


def test_expansion_equation_is_only_formal_without_collective_kinetic_source():
    expansion = load("reduced_model")["expansion_equation"]
    assert expansion["M_L_action_derived"] is False
    assert expansion["actual_BHSM_evolution_equation_derived"] is False
    assert expansion["static_branch"] is None
    assert expansion["acceleration"] is None
    assert expansion["Hubble_law_postulated"] is False


def test_no_flux_or_black_hole_input_becomes_absolute_unit():
    absolute = load("absolute_one_scale")
    assert absolute["absolute_test"]["arbitrary_initial_flux"] is False
    assert absolute["absolute_test"]["black_hole_mass_input"] is False
    assert all(value is False for value in absolute["recycling_sources"].values())
    assert absolute["outputs"] == {"ell_star": None, "M_star": None, "M_BH": None, "R_BH": None}


def test_public_claims_do_not_promote_recycling_cosmology():
    text = public_text().lower()
    forbidden = [
        "black holes are proven to cause cosmic expansion",
        "dark energy has been replaced",
        "inflation is unnecessary",
        "horizon problem is solved",
        "information is fundamentally erased",
        "signals propagate instantaneously",
        "zpv reset is established",
        "recycling flux derives an absolute unit",
    ]
    assert not any(phrase in text for phrase in forbidden)
    assert "bhsm_spacetime_recycling_constraint_architecture_identified" in text


def test_original_v512_tests_and_integrity_contract_remain_applicable():
    for relative, digest in FROZEN_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    report = load("construction_report")
    assert report["frozen_predictions_changed"] is False
    assert report["official_prediction_logic_changed"] is False
    assert report["recommended_next_construction_sprint"] == "bhsm-scalar-topographic-physical-localization-v5-13"

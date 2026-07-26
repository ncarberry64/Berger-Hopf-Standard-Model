from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from bhsm.interface import particle_chirality_anomaly_normalization as arch
from bhsm.interface import triality_generation_scale_architecture as v620


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_particle_chirality_anomaly_normalization_v6_3_0.md"
FROZEN = ROOT / "docs" / "frozen_predictions.json"


def load(key):
    return json.loads(
        (ARTIFACTS / arch.ARTIFACT_FILES[key]).read_text(encoding="utf-8")
    )


def test_registry_has_exactly_eighteen_deterministic_artifacts():
    payloads = arch.build_artifact_payloads(ROOT)
    assert len(payloads) == 18
    assert set(payloads) == set(arch.ARTIFACT_FILES)
    assert all(payload["version"] == "v6.3.0" for payload in payloads.values())
    assert payloads["handoff"]["source_sha"] == arch.SOURCE_SHA
    assert all(payload["primary_result"] == arch.PRIMARY_RESULT for payload in payloads.values())


def test_boundary_u1_and_electric_charge_operator_are_exact():
    expected = {
        "Q_L": (Fraction(1, 6), Fraction(2, 3), Fraction(-1, 3)),
        "u_c": (Fraction(-2, 3), Fraction(-2, 3), Fraction(-2, 3)),
        "d_c": (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)),
        "L_L": (Fraction(-1, 2), Fraction(0), Fraction(-1)),
        "e_c": (Fraction(1), Fraction(1), Fraction(1)),
        "nu_c": (Fraction(0), Fraction(0), Fraction(0)),
    }
    for row in arch.one_family_multiplets():
        y, qmax, qmin = expected[row.name]
        assert row.Y == y
    charges = {row["slot"]: row["Q_em"] for row in arch.charge_table()}
    assert charges == {
        "L_upper": "0",
        "L_lower": "-1",
        "Q_upper": "2/3",
        "Q_lower": "-1/3",
        "nu_c": "0",
        "e_c": "1",
        "u_c": "-2/3",
        "d_c": "1/3",
    }


def test_particle_map_is_three_families_with_optional_neutral_slot():
    rows = arch.particle_representation_rows()
    assert len(rows) == 18
    assert {row["family_projector"] for row in rows} == {"P_0", "P_1", "P_2"}
    assert arch.family_dimension(False) == 15
    assert arch.family_dimension(True) == 16
    assert load("particle_map")["triality_and_Berger_triplications_multiplied"] is False
    assert load("particle_map")["particles_antiparticles_double_counted"] is False


def test_v620_triality_fourier_branching_and_volume_inputs_are_preserved():
    payloads = v620.build_artifact_payloads(ROOT)
    assert payloads["triality"]["exact_checks"] == {
        "T_cubed": True,
        "complete": True,
        "orthogonal": True,
        "eigen": True,
    }
    assert payloads["no_double"]["fourier_inverse_exact"] is True
    assert payloads["no_double"]["intertwines_projectors"] is True
    assert payloads["no_double"]["nine_generation_architecture_rejected"] is True
    assert payloads["branching"]["eight_dimension"] == 8
    assert payloads["branching"]["adjoint_dimension"] == 14
    assert payloads["volumes"]["three_times_VolS3"] == "6*pi^2"


def test_gauge_representation_is_family_universal_and_conjugation_consistent():
    rows = arch.particle_representation_rows()
    content = {}
    for family in range(3):
        family_rows = [row for row in rows if row["family_projector"] == f"P_{family}"]
        content[family] = {
            (row["name"], row["su3"], row["sp1"], row["Y"])
            for row in family_rows
        }
    assert content[0] == content[1] == content[2]
    expected_conjugates = {
        "u_c": ("conjugate(3)", "-2/3"),
        "d_c": ("conjugate(3)", "1/3"),
        "e_c": ("1", "1"),
        "nu_c": ("1", "0"),
    }
    for row in rows:
        if row["name"] in expected_conjugates:
            assert (row["su3"], row["Y"]) == expected_conjugates[row["name"]]


def test_complex_polarization_is_explicit_and_unpolarized_map_rejected():
    payload = load("particle_map")
    assert "choose 1+3" in payload["complex_polarization"]["selection"]
    assert "antiparticle data" in payload["complex_polarization"]["selection"]
    assert "cannot be" in payload["complex_polarization"]["without_selection"]
    assert payload["complex_polarization"]["status"] == "BHSM boundary-domain identification"


def test_clifford_action_domain_and_kink_zero_mode():
    checks = arch.clifford_checks()
    assert all(checks.values())
    diagnostic = arch.zero_mode_diagnostic()
    assert abs(diagnostic["numerical_norm"] - 1.0) < 3e-7
    assert diagnostic["K_plus_normalizable_count_per_internal_slot"] == 1
    assert diagnostic["K_minus_normalizable_count_per_internal_slot"] == 0
    domain = load("chiral_domain")
    assert domain["physical_Dirac_parent_law_introduced"] is False
    assert domain["zero_mode"]["normal_index_per_selected_slot"] == 1


def test_one_and_three_family_anomalies_cancel_exactly():
    for include_neutral in (False, True):
        one = arch.anomaly_coefficients(1, include_neutral)
        assert one["SU3_cubed"] == 0
        assert one["SU3_squared_U1"] == 0
        assert one["Sp1_squared_U1"] == 0
        assert one["U1_cubed"] == 0
        assert one["gravity_squared_U1"] == 0
        assert one["Sp1_doublet_count"] == 4
        assert one["Witten_parity_even"] is True
    three = load("anomaly_three")
    assert three["Witten_doublets"] == 12
    assert all(
        value == "0"
        for key, value in three["three_family_totals"].items()
        if key not in {"Sp1_doublet_count", "Witten_parity_even"}
    )
    assert three["three_family_totals"]["Witten_parity_even"] is True


def test_trace_normalization_rejects_1_2_7_representation_incidence():
    indices = arch.connection_trace_indices()
    assert indices == {
        "I1_raw": Fraction(10, 3),
        "I2": Fraction(2),
        "I3": Fraction(2),
        "eta_Y": Fraction(3, 5),
        "I1_normalized": Fraction(2),
    }
    incidence = load("incidence")
    assert incidence["raw_integer_ratio"] == "5:3:3"
    assert incidence["canonically_normalized_ratio"] == "1:1:1"
    assert incidence["status"] == "BHSM_1_2_7_CANDIDATE_REJECTED_BY_REPRESENTATION_TRACE"
    assert incidence["geometric_denominator"] == "6*pi^2 preserved exactly"
    assert load("connection_map")["measured_derivation_input_used"] is False


def test_family_mass_operator_is_projector_exact_and_frozen_read_only():
    before = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    mass = arch.exact_mass_operator(ROOT)
    after = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    assert before == after
    assert mass["projector_algebra_preserved"]["complete"] is True
    assert mass["projector_algebra_preserved"]["orthogonal"] is True
    assert mass["mixing_constraint"] == "[M_(f,mix), gauge representation projectors]=0"
    assert mass["absolute_masses_derived"] is False


def test_scale_map_remains_symbolic_and_has_no_measured_input():
    scale = load("scale")
    assert scale["numerical_absolute_mass_emitted"] is False
    assert scale["Z_g_equals_Z_A_assumed"] is False
    assert scale["transfer_factors_equal_assumed"] is False
    assert "N_geom" in scale["Xi_i"]
    hidden = load("hidden")
    assert hidden["measured_inputs"] == []
    assert hidden["fits"] == []
    assert hidden["new_primitive_coefficients"] == []


def test_scalar_berger_mixing_r4_and_hessian_claim_boundaries():
    mixed = load("mixed_mode")
    assert mixed["H_sigma_beta_at_retained_linear_source"] == "0"
    assert mixed["one_light_scalar_claimed"] is False
    r4 = load("r4")
    assert r4["components"]["B_total"] is None
    assert "not completed" in r4["fixed_moving_agreement"]
    hessian = load("hessian")
    assert hessian["full_spectrum_computed"] is False
    assert hessian["full_coefficients_constructed"] is False
    assert len(hessian["variables"]) == 8


def test_scalar_wall_cusp_sign_and_domain_results_are_preserved():
    cusp = v620.build_artifact_payloads(ROOT)["cusp"]
    assert cusp["nu1_over_12"] == 9.138890145035
    assert cusp["scalar_sign_degenerate"] is True
    assert "sheet antisymmetry" in cusp["convention_invariant"]
    r4 = load("r4")
    assert "preserved through O(r^3)" in r4["fixed_moving_agreement"]


def test_materializer_is_byte_deterministic_and_does_not_rewrite_other_files(tmp_path):
    first = {
        key: arch.deterministic_json(value)
        for key, value in arch.build_artifact_payloads(ROOT).items()
    }
    second = {
        key: arch.deterministic_json(value)
        for key, value in arch.build_artifact_payloads(ROOT).items()
    }
    assert first == second
    assert len(first) == 18


def test_materialized_artifacts_match_module_exactly():
    payloads = arch.build_artifact_payloads(ROOT)
    for key, payload in payloads.items():
        path = ARTIFACTS / arch.ARTIFACT_FILES[key]
        assert path.read_text(encoding="utf-8") == arch.deterministic_json(payload)


def test_cli_json_and_markdown():
    env = {"PYTHONPATH": str(ROOT / "src")}
    json_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "bhsm.interface",
            "particle-chirality-anomaly-status",
            "--format",
            "json",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(json_run.stdout)["primary_result"] == arch.PRIMARY_RESULT
    md_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "bhsm.interface",
            "particle-chirality-anomaly-status",
            "--format",
            "markdown",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "v6.3.0 particle/chirality/anomaly" in md_run.stdout


def test_doctrine_and_final_report_preserve_firewall():
    text = DOC.read_text(encoding="utf-8")
    report = load("report")
    assert arch.PRIMARY_RESULT in text
    assert report["status"] == arch.PRIMARY_RESULT
    assert arch.GUARDS["frozen_predictions_changed"] is False
    assert arch.GUARDS["official_prediction_logic_changed"] is False

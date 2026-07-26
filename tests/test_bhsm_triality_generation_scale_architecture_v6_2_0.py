import ast
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import triality_generation_scale_architecture as arch


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_triality_generation_scale_architecture_v6_2_0.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads(
        (ARTIFACTS / arch.ARTIFACT_FILES[key]).read_text(encoding="utf-8")
    )


def test_exact_eisenstein_field_and_triality_order():
    assert arch.OMEGA**2 + arch.OMEGA + 1 == arch.ZERO
    assert arch.OMEGA**3 == arch.ONE
    assert arch.matrix_power(arch.triality_matrix(), 3) == arch.identity_matrix(3)


def test_exact_projector_completeness_orthogonality_and_eigenvalues():
    checks = arch.triality_algebra_check()
    assert checks == {
        "T_cubed": True,
        "complete": True,
        "orthogonal": True,
        "eigen": True,
    }
    for k in range(3):
        projector = arch.triality_projector(k)
        assert arch.matrix_multiply(projector, projector) == projector
        assert arch.matrix_multiply(arch.triality_matrix(), projector) == arch.matrix_scale(
            arch.OMEGA**k, projector
        )


def test_fourier_intertwiner_prevents_nine_generation_double_counting():
    result = arch.no_double_counting_check()
    assert result["fourier_inverse_exact"] is True
    assert result["intertwines_projectors"] is True
    assert result["family_dimension"] == 3
    assert result["internal_rank_per_family"] == 8
    assert result["triality_sum_dimension"] == 24
    assert result["generation_count"] == 3
    assert result["product_generation_count"] is None
    assert result["nine_generation_architecture_rejected"] is True


def test_exact_g2_su3_branching_weights_and_dimensions():
    branching = arch.g2_su3_branching()
    assert branching["eight_dimension"] == 8
    assert branching["adjoint_dimension"] == 14
    assert {(tuple(row["SU3_highest_weight"]), row["dimension"]) for row in branching["eight_weights"]} == {
        ((0, 0), 1),
        ((1, 0), 3),
        ((0, 1), 3),
    }
    assert {(tuple(row["SU3_highest_weight"]), row["dimension"]) for row in branching["adjoint_weights"]} == {
        ((1, 1), 8),
        ((1, 0), 3),
        ((0, 1), 3),
    }


def test_color_projector_retains_eight_and_constrains_coset_six():
    color = arch.color_constraint_projector()
    assert color["P_color_rank"] == 8
    assert color["P_coset_rank"] == 6
    assert color["idempotent"] is True
    assert color["orthogonal"] is True
    assert color["mass_generation_for_coset_claimed"] is False


def test_particle_slots_are_three_families_not_observed_assignments():
    rows = arch.particle_slot_map()
    assert len(rows) == 12
    assert {row["family_projector"] for row in rows} == {"P_0", "P_1", "P_2"}
    assert all("candidate" in row["candidate_role"] for row in rows)
    assert {tuple(row["existing_BHSM_mode"].values()) for row in rows}
    assert load("slots")["observed_particle_names_assigned"] is False


def test_exact_sphere_volumes_ratio_and_denominator():
    assert arch.sphere_volume_exact(7) == (Fraction(1, 3), 4)
    assert arch.sphere_volume_exact(4) == (Fraction(8, 3), 2)
    assert arch.sphere_volume_exact(3) == (Fraction(2), 2)
    volumes = arch.sphere_volume_coefficients()
    assert volumes["VolS4_times_VolS3_over_VolS7"] == 16
    assert volumes["three_times_VolS3"] == "6*pi^2"


def test_exact_cusp_coefficient_and_sheet_sign():
    data = arch.regression_data()
    assert data["chi_abs"] ** 3 / 16 == pytest.approx(
        data["nu1_abs"] / 12, rel=2e-12
    )
    cusp = load("cusp")
    assert cusp["nu1_over_12"] == pytest.approx(9.138890145035, rel=2e-12)
    assert "d^3/16" in cusp["exact_series"]
    assert cusp["scalar_sign_degenerate"] is True


def test_numerical_cusp_convergence_on_both_sheets_and_meshes():
    rows = load("cusp")["numerical_convergence"]
    assert load("cusp")["diagnostic_ratio_decimal_places"] == 3
    for sheet in (-1, 1):
        selected = [row for row in rows if row["sheet"] == sheet]
        assert len(selected) == 4
        errors = [
            abs(row["delta_Gamma_over_r3"] - row["target"]) for row in selected
        ]
        assert errors[-1] < errors[0]
        assert errors[-1] < 0.005
        assert all(row["delta_Gamma_over_r3"] * sheet > 0 for row in selected)
    mesh = load("cusp")["mesh_convergence"]
    assert len(mesh) == 6
    for sheet in (-1, 1):
        selected = [row for row in mesh if row["sheet"] == sheet]
        assert max(row["delta_Gamma_over_r3"] for row in selected) - min(
            row["delta_Gamma_over_r3"] for row in selected
        ) < 0.01


def test_flat_kink_target_is_retired_without_erasing_direct_moment():
    retired = load("retirement")
    assert retired["status"] == "BHSM_FLAT_KINK_QUARTIC_COMPLETION_TARGET_REJECTED_FOR_COMPACT_CAP"
    assert retired["retained_role"] == "uncompactified flat-kink diagnostic only"
    assert "21.690130229412" in retired["compact_direct_moment"]
    assert retired["historical_record_deleted"] is False


def test_adopted_axioms_are_distinguished_from_derived_results():
    spacetime = load("spacetime")
    berger = load("berger_higgs")
    assert spacetime["status"] == "BHSM_SPACETIME_ADMISSIBILITY_SHEET_SELECTION_ADOPTED"
    assert spacetime["local_equations_prove_global_selection"] is False
    assert "same healthy principal signs" in spacetime["principal_symbol_test"]
    assert berger["status"] == "BHSM_BERGER_HIGGS_GEOMETRIC_TRANSLATION_ADOPTED"
    assert "separate linear coordinates" in berger["sigma_vs_Berger"]
    assert berger["independent_arbitrary_scalar_added"] is False


def test_transport_coupling_and_scale_claim_boundaries():
    transport = load("transport")
    couplings = load("couplings")
    scale = load("scale")
    assert transport["matrices_numerically_fit"] is False
    assert transport["existing_frozen_status_preserved"] is True
    assert couplings["alpha_i_physical_derived"] is False
    assert couplings["registered_weights"] == [1, 2, 7]
    assert scale["Z_g_equals_Z_A_assumed"] is False
    assert scale["measured_value_inserted"] is False
    assert scale["numerical_absolute_unit_emitted"] is False


def test_sixteen_artifacts_are_deterministic_and_hidden_inputs_are_clean():
    assert len(arch.ARTIFACT_FILES) == 16
    built = arch.build_artifact_payloads(ROOT)
    for key, filename in arch.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == arch.PRIMARY_RESULT
        assert all(payload[guard] is False for guard in arch.GUARDS)
        assert (ARTIFACTS / filename).read_text(
            encoding="utf-8"
        ) == arch.deterministic_json(built[key])
    hidden = load("hidden")
    assert hidden["measured_inputs"] == []
    assert hidden["fits"] == []


def test_module_imports_no_physical_dirac_or_monopole_packages():
    source = (
        ROOT
        / "src"
        / "bhsm"
        / "interface"
        / "triality_generation_scale_architecture.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = [
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom)) and node.names
    ]
    lowered = " ".join(imports).lower()
    assert "dirac" not in lowered
    assert "monopole" not in lowered


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [
        sys.executable,
        "-m",
        "bhsm.interface",
        "triality-generation-scale-status",
    ]
    result = subprocess.run(
        command + ["--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout)["primary_result"] == arch.PRIMARY_RESULT
    result = subprocess.run(
        command + ["--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "v6.2.0 Triality" in result.stdout


def test_public_status_and_frozen_integrity():
    paths = [
        DOC,
        ROOT / "STATUS.md",
        ROOT / "CLAIMS.md",
        ROOT / "ARTIFACT_INDEX.md",
        ROOT / "CLI_REFERENCE.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert arch.PRIMARY_RESULT in text
    assert "BHSM_SCALAR_WALL_LEADING_CUSP_ACTION_REPRODUCED" in text
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_invalid_domains_rejected():
    with pytest.raises(ValueError):
        arch.triality_projector(3)
    with pytest.raises(ValueError):
        arch.sphere_volume_exact(-1)
    with pytest.raises(ValueError):
        arch.vacuum_action_density(1)
    with pytest.raises(ValueError):
        arch.cusp_action_point(0, 1)

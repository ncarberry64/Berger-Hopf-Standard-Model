from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from bundle_boundary_conditions import (
    CoefficientDerivationStatus,
    default_sector_boundary_functionals,
)
from constants import S_OVERLAP
from mode_selection import EXPECTED_LEDGER
from omega_derivation import (
    build_omega_action_origin_report,
    coefficient_rows,
    export_omega_action_origin_json,
    export_omega_action_origin_markdown,
    omega_equation_from_functional,
    omega_value_from_functional,
    recovered_mode_ledger,
    selected_modes_from_functional,
)


def test_boundary_functionals_reproduce_omega_coefficients():
    functionals = default_sector_boundary_functionals()

    assert functionals["lepton"].fiber_coefficient == -1
    assert functionals["lepton"].base_coefficient == 2
    assert functionals["up"].fiber_coefficient == 1
    assert functionals["up"].base_coefficient == -2
    assert functionals["down"].fiber_coefficient == 1
    assert functionals["down"].base_coefficient == 4


def test_boundary_functionals_reproduce_targets():
    functionals = default_sector_boundary_functionals()

    assert functionals["lepton"].target == 3
    assert functionals["up"].target == 6
    assert functionals["down"].target == 12


def test_equations_and_expected_modes_are_recovered():
    functionals = default_sector_boundary_functionals()

    assert omega_equation_from_functional(functionals["lepton"]) == "Omega_ell = -q+2j = 3"
    assert omega_equation_from_functional(functionals["up"]) == "Omega_u = q-2j = 6"
    assert omega_equation_from_functional(functionals["down"]) == "Omega_d = q+4j = 12"

    assert selected_modes_from_functional(functionals["lepton"], k_max=12) == EXPECTED_LEDGER["lepton"]
    assert selected_modes_from_functional(functionals["up"], k_max=12) == EXPECTED_LEDGER["up"]
    assert selected_modes_from_functional(functionals["down"], k_max=12) == EXPECTED_LEDGER["down"]
    assert recovered_mode_ledger(k_max=12)["recovered_all"] is True


def test_omega_values_match_current_operator_targets_on_ledger_modes():
    functionals = default_sector_boundary_functionals()

    for sector, modes in EXPECTED_LEDGER.items():
        functional = functionals[sector]
        for mode in modes:
            assert omega_value_from_functional(*mode, functional) == functional.target


def test_coefficients_report_statuses_explicitly():
    rows = coefficient_rows()

    assert len(rows) == 9
    assert all(row["status"] for row in rows)
    assert {
        (row["sector"], row["coefficient"]): row["status"] for row in rows
    } == {
        ("lepton", "fiber_q"): "DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        ("lepton", "base_j"): "DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        ("lepton", "target"): "DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        ("up", "fiber_q"): "DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        ("up", "base_j"): "DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        ("up", "target"): "DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        ("down", "fiber_q"): "DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        ("down", "base_j"): "DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        ("down", "target"): "DERIVED_FROM_BOUNDARY_FUNCTIONAL",
    }
    assert [row for row in rows if row["status"] == "ASSUMED"] == []


def test_report_preserves_claim_discipline():
    report = build_omega_action_origin_report()

    assert report.theorem_complete is False
    assert any("not yet derived" in item for item in report.limitations)
    assert all(step.status != CoefficientDerivationStatus.OPEN for step in report.steps)
    assert any("No empirical masses" in item for item in report.assumptions)


def test_no_empirical_masses_or_ckm_are_used_in_omega_modules():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("internal_action.py", "bundle_boundary_conditions.py", "omega_derivation.py")
    )
    forbidden = ("EMPIRICAL_MASS_RATIOS", "from ckm", "compute_ckm", "ckm_reference", "mass_ratio(")

    assert all(token not in source for token in forbidden)


def test_frozen_v1_outputs_are_unchanged_by_action_origin_report():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_omega_action_origin_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert [row for row in comparison["rows"] if row["changed"]] == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "omega.md"
    json_path = tmp_path / "omega.json"

    export_omega_action_origin_markdown(md_path)
    export_omega_action_origin_json(json_path)

    assert "BHSM v1.2 Omega Action-Origin Scaffold" in md_path.read_text()
    assert "DERIVED_FROM_BOUNDARY_FUNCTIONAL" in md_path.read_text()
    assert '"theorem_complete": false' in json_path.read_text()

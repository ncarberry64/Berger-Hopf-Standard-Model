from math import isclose
from pathlib import Path

from action_reduction import reduce_parent_action_to_boundary_functional, reduced_coefficients
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from boundary_functional_derivation import (
    build_parent_action_derivation_report,
    export_parent_action_derivation_json,
    export_parent_action_derivation_markdown,
)
from bundle_boundary_conditions import CoefficientDerivationStatus
from constants import S_OVERLAP
from parent_internal_action import ParentReductionStatus, parent_action_terms


def _without(*term_ids: str):
    return tuple(term for term in parent_action_terms() if term.id not in set(term_ids))


def test_parent_action_reduction_reproduces_sector_boundary_functional():
    expected = {
        "lepton": (-1, 2, 3),
        "up": (1, -2, 6),
        "down": (1, 4, 12),
    }

    for sector, coefficients in expected.items():
        reduction = reduce_parent_action_to_boundary_functional(sector)
        fiber, base, target = coefficients

        assert reduction.parent_action_status == ParentReductionStatus.REDUCED_FROM_PARENT_ACTION
        assert reduction.theorem_complete is False
        assert reduction.functional.fiber_coefficient == fiber
        assert reduction.functional.base_coefficient == base
        assert reduction.functional.target == target


def test_removing_hopf_or_higgs_prevents_fiber_derivation():
    for removed in ("I_HOPF", "I_U1"):
        reduction = reduce_parent_action_to_boundary_functional("up", _without(removed))
        coefficients = reduced_coefficients(reduction)

        assert reduction.parent_action_status == ParentReductionStatus.OPEN
        assert coefficients["fiber_q"].value is None
        assert coefficients["fiber_q"].status == CoefficientDerivationStatus.OPEN
        assert removed in coefficients["fiber_q"].open_reason


def test_removing_base_weak_or_coframe_prevents_base_derivation():
    for removed in ("I_BASE", "I_WEAK", "I_COF"):
        reduction = reduce_parent_action_to_boundary_functional("down", _without(removed))
        coefficients = reduced_coefficients(reduction)

        assert reduction.parent_action_status == ParentReductionStatus.OPEN
        assert coefficients["base_j"].value is None
        assert coefficients["base_j"].status == CoefficientDerivationStatus.OPEN
        assert removed in coefficients["base_j"].open_reason


def test_removing_boundary_index_prevents_target_derivation():
    reduction = reduce_parent_action_to_boundary_functional("lepton", _without("I_BDY"))
    coefficients = reduced_coefficients(reduction)

    assert reduction.parent_action_status == ParentReductionStatus.OPEN
    assert coefficients["target"].value is None
    assert coefficients["target"].status == CoefficientDerivationStatus.OPEN
    assert "I_BDY" in coefficients["target"].open_reason


def test_parent_report_status_and_necessary_terms_are_explicit():
    report = build_parent_action_derivation_report()

    assert report.status == ParentReductionStatus.REDUCED_FROM_PARENT_ACTION
    assert report.theorem_complete is False
    assert report.necessary_terms["fiber_q"] == ("I_HOPF", "I_U1")
    assert report.necessary_terms["base_j"] == ("I_BASE", "I_WEAK", "I_COF")
    assert report.necessary_terms["target"] == ("I_BDY",)
    assert all(row["parent_action_status"] == "REDUCED_FROM_PARENT_ACTION" for row in report.coefficient_table)


def test_no_empirical_flavor_modules_are_imported_by_parent_action_scaffold():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("parent_internal_action.py", "action_reduction.py", "boundary_functional_derivation.py")
    )
    forbidden = (
        "EMPIRICAL_MASS_RATIOS",
        "from ckm",
        "compute_ckm",
        "from pmns",
        "compute_pmns",
        "mass_ratio(",
        "build_prediction_ledger",
        "build_residual_audit",
    )

    assert all(token not in source for token in forbidden)


def test_parent_action_scaffold_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_parent_action_derivation_report()

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


def test_parent_action_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "parent.md"
    json_path = tmp_path / "parent.json"

    export_parent_action_derivation_markdown(md_path)
    export_parent_action_derivation_json(json_path)

    assert "Parent Internal-Action Boundary Derivation" in md_path.read_text()
    assert "REDUCED_FROM_PARENT_ACTION" in md_path.read_text()
    assert '"theorem_complete": false' in json_path.read_text()

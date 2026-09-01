import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from ht_bound_classification import (
    build_ht_inventory_report,
    export_ht_bound_classification_json,
    export_ht_bound_classification_markdown,
)
from ht_term_inventory import (
    HTTermClassification,
    build_ht_bound_inventory,
    export_ht_term_inventory_json,
    export_ht_term_inventory_markdown,
)


EXPECTED_LEVEL2_TERMS = {
    "berger_dirac_kinetic",
    "hopf_twist",
    "boundary_term",
    "chirality_term",
    "sector_coupling",
    "heat_lift",
    "psd_profile",
    "zero_complement_projector",
}


def test_every_level2_term_is_inventoried():
    inventory = build_ht_bound_inventory()

    assert {term.id for term in inventory.terms} == EXPECTED_LEVEL2_TERMS
    assert {item.term_id for item in inventory.classifications} == EXPECTED_LEVEL2_TERMS
    assert inventory.theorem_complete is False


def test_every_term_has_explicit_classification_and_bound_method():
    inventory = build_ht_bound_inventory()
    allowed = set(HTTermClassification)

    for term in inventory.terms:
        assert term.classification in allowed
        assert term.lower_bound_method
        assert term.assumptions
        assert term.limitations
        assert type(term.preserves_zero_modes) is bool
        assert type(term.can_lower_complement_gap) is bool


def test_psd_terms_cannot_reduce_lower_bound():
    inventory = build_ht_bound_inventory()
    psd_terms = [term for term in inventory.terms if term.classification == HTTermClassification.PSD_EXACT]

    assert {term.id for term in psd_terms} == {"heat_lift", "psd_profile"}
    assert all(term.can_lower_complement_gap is False for term in psd_terms)
    assert all("PSD" in term.classification.value for term in psd_terms)


def test_indefinite_and_off_diagonal_terms_are_bounded_or_open():
    inventory = build_ht_bound_inventory()

    for term in inventory.terms:
        if term.can_lower_complement_gap:
            assert term.classification in {
                HTTermClassification.SIGN_INDEFINITE_BOUNDED,
                HTTermClassification.OFF_DIAGONAL_BOUNDED,
                HTTermClassification.OPEN,
            }
            assert "bound" in term.lower_bound_method.lower()


def test_zero_mode_preservation_is_reported_for_all_terms():
    inventory = build_ht_bound_inventory()

    assert all(term.preserves_zero_modes is True for term in inventory.terms)
    projector = next(term for term in inventory.terms if term.id == "zero_complement_projector")
    assert projector.classification == HTTermClassification.FINITE_BASIS_ONLY
    assert "dim ker" in " ".join(projector.limitations)


def test_bound_report_identifies_chain_and_weakest_terms():
    report = build_ht_inventory_report()

    assert report.theorem_complete is False
    assert report.weakest_term == "zero_complement_projector"
    assert report.weakest_matrix_term == "sector_coupling"
    assert any("heat-lift" in step for step in report.combined_bound_chain)
    assert "dim ker D_twist = 3" in report.next_upgrade_target


def test_no_forbidden_empirical_modules_are_imported_by_ht_inventory():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("ht_term_inventory.py", "ht_bound_classification.py")
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


def test_ht_inventory_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_ht_bound_inventory()
    build_ht_inventory_report()

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


def test_ht_inventory_exports_generate_cleanly(tmp_path):
    inventory_md = tmp_path / "inventory.md"
    inventory_json = tmp_path / "inventory.json"
    report_md = tmp_path / "report.md"
    report_json = tmp_path / "report.json"

    export_ht_term_inventory_markdown(inventory_md)
    export_ht_term_inventory_json(inventory_json)
    export_ht_bound_classification_markdown(report_md)
    export_ht_bound_classification_json(report_json)

    assert "Level 2 H_T Term Inventory" in inventory_md.read_text()
    assert json.loads(inventory_json.read_text())["theorem_complete"] is False
    assert "Analytic-Bound Classification Report" in report_md.read_text()
    assert json.loads(report_json.read_text())["weakest_term"] == "zero_complement_projector"

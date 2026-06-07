import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from domain_assumptions import build_infinite_basis_assumptions, candidate_structured_margin
from hilbert_space_scaffold import (
    build_hilbert_space_domain,
    build_operator_domains,
    complement_labels,
    export_hilbert_space_domain_json,
    export_hilbert_space_domain_markdown,
    finite_hilbert_basis_labels,
    hopf_charge,
    protected_zero_mode_labels,
)
from infinite_basis_bounds import (
    build_infinite_bound_report,
    export_infinite_sector_bound_json,
    export_infinite_sector_bound_markdown,
)


def test_hilbert_space_labels_are_generated_consistently():
    labels = finite_hilbert_basis_labels(k_max=4)

    assert labels
    assert all(label.q == hopf_charge(label.k, label.j) for label in labels)
    assert all(0 <= label.j <= label.k // 2 for label in labels)
    assert {label.sector for label in labels} == {"lepton", "up", "down"}
    assert {label.chirality for label in labels} == {-1, 1}


def test_protected_zero_modes_are_separated_from_complement_labels():
    protected = set(protected_zero_mode_labels())
    complement = set(complement_labels(k_max=4))

    assert len(protected) == 3
    assert protected.isdisjoint(complement)
    assert all(label.protected_zero_mode for label in protected)
    assert all(not label.protected_zero_mode for label in complement)


def test_operator_domains_are_explicit_and_conservative():
    domain = build_hilbert_space_domain()
    operators = build_operator_domains()

    assert domain.status == "DOMAIN_SCAFFOLD"
    assert len(domain.protected_zero_modes) == 3
    assert {operator.name for operator in operators} == {
        "diagonal_berger_dirac_kinetic",
        "sector_coupling",
        "protected_zero_mode_subspace",
        "orthogonal_complement",
    }
    assert all(operator.limitations for operator in operators)


def test_assumptions_a1_to_a6_are_present_and_explicit():
    assumptions = build_infinite_basis_assumptions()

    assert {assumption.id for assumption in assumptions} == {f"A{idx}" for idx in range(1, 7)}
    assert all(assumption.statement for assumption in assumptions)
    assert all(assumption.status for assumption in assumptions)
    assert all(assumption.limitations for assumption in assumptions)
    assert any("a_K <= 0.04" in assumption.statement for assumption in assumptions)


def test_conservative_candidate_margin_clears_required_bound():
    margin = candidate_structured_margin()

    assert margin["a_k_max"] == 0.04
    assert margin["b_k"] == 0.0
    assert margin["passes"] is True
    assert margin["candidate_structured_lower_bound"] > margin["required_dirac_lower_bound"]
    assert isclose(margin["margin"], 0.6017295838650562, rel_tol=0.0, abs_tol=1e-12)


def test_infinite_theorem_status_is_scaffold_not_proven():
    report = build_infinite_bound_report()

    assert report.theorem.status == "THEOREM_SCAFFOLD"
    assert report.theorem.status != "THEOREM_PROVEN"
    assert report.theorem_complete is False
    assert report.theorem.theorem_complete is False
    assert report.finite_evidence_bridge["theorem_complete"] is False
    assert "UNIFORM_BOUND_CANDIDATE" == report.finite_evidence_bridge["classification"]


def test_no_forbidden_empirical_modules_are_imported_by_hilbert_scaffold():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("hilbert_space_scaffold.py", "domain_assumptions.py", "infinite_basis_bounds.py")
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


def test_hilbert_scaffold_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_infinite_bound_report()

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


def test_hilbert_and_infinite_bound_exports_generate_cleanly(tmp_path):
    domain_md = tmp_path / "domain.md"
    domain_json = tmp_path / "domain.json"
    theorem_md = tmp_path / "theorem.md"
    theorem_json = tmp_path / "theorem.json"

    export_hilbert_space_domain_markdown(domain_md)
    export_hilbert_space_domain_json(domain_json)
    export_infinite_sector_bound_markdown(theorem_md)
    export_infinite_sector_bound_json(theorem_json)

    assert "Hilbert-Space Domain Scaffold" in domain_md.read_text()
    assert json.loads(domain_json.read_text())["theorem_complete"] is False
    assert "THEOREM_SCAFFOLD" in theorem_md.read_text()
    assert json.loads(theorem_json.read_text())["theorem"]["status"] == "THEOREM_SCAFFOLD"

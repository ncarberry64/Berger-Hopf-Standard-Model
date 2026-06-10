import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from essential_self_adjointness import DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN
from ht_domain_bridge import HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY, build_ht_domain_bridge_report
from kato_rellich_closure import (
    KATO_RELLICH_CLOSURE_CONDITIONAL,
    build_kato_rellich_closure_report,
    export_kato_rellich_closure_json,
    export_kato_rellich_closure_markdown,
)
from lower_bound_preservation import (
    LOWER_BOUND_CONDITIONAL,
    build_lower_bound_preservation_report,
    export_lower_bound_preservation_json,
    export_lower_bound_preservation_markdown,
)
from perturbation_domain_inclusion import (
    PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL,
    build_perturbation_domain_inclusion_report,
    export_perturbation_domain_inclusion_json,
    export_perturbation_domain_inclusion_markdown,
)
from perturbation_operator import (
    PERTURBATION_INVENTORIED,
    build_perturbation_operator_report,
    export_perturbation_operator_json,
    export_perturbation_operator_markdown,
)
from perturbation_symmetry import (
    PERTURBATION_SYMMETRY_CONDITIONAL,
    build_perturbation_symmetry_report,
    export_perturbation_symmetry_json,
    export_perturbation_symmetry_markdown,
)
from relative_bound_closure import (
    RELATIVE_BOUND_CONDITIONAL,
    build_relative_bound_closure_report,
    export_relative_bound_closure_json,
    export_relative_bound_closure_markdown,
)


def test_perturbation_terms_are_inventoried():
    report = build_perturbation_operator_report()
    ids = {term.term_id for term in report.terms}

    assert report.status == PERTURBATION_INVENTORIED
    assert {"V_Hopf", "V_boundary", "V_chi", "K_sector", "P_perp_lift", "PSD_profile"} <= ids
    assert report.total_relative_a == 0.015621013485509948
    assert any(term.term_id == "K_sector" and term.finite_scan_evidence_used for term in report.terms)


def test_perturbation_symmetry_and_domain_are_conditional():
    symmetry = build_perturbation_symmetry_report()
    domain = build_perturbation_domain_inclusion_report()

    assert symmetry.status == PERTURBATION_SYMMETRY_CONDITIONAL
    assert symmetry.theorem_complete is False
    assert symmetry.all_symmetric_on_core is True
    assert symmetry.all_extend_to_domain is False
    assert domain.status == PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL
    assert domain.theorem_complete is False
    assert domain.all_terms_include_DA0 is False


def test_relative_bound_closure_is_not_proven_from_finite_scan():
    report = build_relative_bound_closure_report()

    assert report.status == RELATIVE_BOUND_CONDITIONAL
    assert report.theorem_complete is False
    assert report.a_less_than_one is True
    assert report.all_infinite_bounds_proven is False
    assert report.total_a == 0.015621013485509948


def test_kato_rellich_closure_remains_conditional():
    report = build_kato_rellich_closure_report()

    assert report.reference_self_adjoint_status == DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN
    assert report.status == KATO_RELLICH_CLOSURE_CONDITIONAL
    assert report.theorem_complete is False
    assert report.can_apply_kato_rellich is False
    assert "perturbation domain inclusion" in " ".join(report.open_obligations)


def test_lower_bound_preservation_is_conditional():
    report = build_lower_bound_preservation_report()

    assert report.status == LOWER_BOUND_CONDITIONAL
    assert report.theorem_complete is False
    assert report.clears_required_threshold is True
    assert report.applies_to_formal_complement is False
    assert report.resulting_lower_bound > report.required_dirac_lower_bound


def test_ht_bridge_blocks_on_perturbation_not_full_theorem():
    report = build_ht_domain_bridge_report()

    assert report.domain_bridge_status == HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY
    assert report.kato_rellich_closure_status == KATO_RELLICH_CLOSURE_CONDITIONAL
    assert report.lower_bound_preservation_status == "LOWER_BOUND_BLOCKED_BY_COMPLEMENT"
    assert report.theorem_complete is False


def test_v20_exports_generate(tmp_path):
    outputs = {
        "operator_md": tmp_path / "operator.md",
        "operator_json": tmp_path / "operator.json",
        "sym_md": tmp_path / "sym.md",
        "sym_json": tmp_path / "sym.json",
        "domain_md": tmp_path / "domain.md",
        "domain_json": tmp_path / "domain.json",
        "rel_md": tmp_path / "rel.md",
        "rel_json": tmp_path / "rel.json",
        "kato_md": tmp_path / "kato.md",
        "kato_json": tmp_path / "kato.json",
        "lower_md": tmp_path / "lower.md",
        "lower_json": tmp_path / "lower.json",
    }
    export_perturbation_operator_markdown(outputs["operator_md"])
    export_perturbation_operator_json(outputs["operator_json"])
    export_perturbation_symmetry_markdown(outputs["sym_md"])
    export_perturbation_symmetry_json(outputs["sym_json"])
    export_perturbation_domain_inclusion_markdown(outputs["domain_md"])
    export_perturbation_domain_inclusion_json(outputs["domain_json"])
    export_relative_bound_closure_markdown(outputs["rel_md"])
    export_relative_bound_closure_json(outputs["rel_json"])
    export_kato_rellich_closure_markdown(outputs["kato_md"])
    export_kato_rellich_closure_json(outputs["kato_json"])
    export_lower_bound_preservation_markdown(outputs["lower_md"])
    export_lower_bound_preservation_json(outputs["lower_json"])

    assert json.loads(outputs["operator_json"].read_text())["status"] == PERTURBATION_INVENTORIED
    assert json.loads(outputs["sym_json"].read_text())["status"] == PERTURBATION_SYMMETRY_CONDITIONAL
    assert json.loads(outputs["domain_json"].read_text())["status"] == PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL
    assert json.loads(outputs["rel_json"].read_text())["status"] == RELATIVE_BOUND_CONDITIONAL
    assert json.loads(outputs["kato_json"].read_text())["status"] == KATO_RELLICH_CLOSURE_CONDITIONAL
    assert json.loads(outputs["lower_json"].read_text())["status"] == LOWER_BOUND_CONDITIONAL


def test_v20_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "perturbation_operator.py",
            "perturbation_symmetry.py",
            "perturbation_domain_inclusion.py",
            "relative_bound_closure.py",
            "lower_bound_preservation.py",
            "kato_rellich_closure.py",
        )
    )
    forbidden = (
        "from prediction_ledger",
        "import prediction_ledger",
        "from residual_audit",
        "import residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "compute_ckm",
        "compute_pmns",
    )
    assert all(token not in sources for token in forbidden)


def test_v20_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_kato_rellich_closure_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]


def test_generated_v20_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "perturbation_operator_report.md",
        root / "theory" / "perturbation_symmetry_report.md",
        root / "theory" / "perturbation_domain_inclusion_report.md",
        root / "theory" / "relative_bound_closure_report.md",
        root / "theory" / "kato_rellich_closure_report.md",
        root / "theory" / "lower_bound_preservation_report.md",
        root / "manuscript" / "BHSM_v2_0_kato_rellich_closure_note.md",
        root / "notebooks" / "50_kato_rellich_perturbation_closure.ipynb",
    )
    for path in paths:
        assert path.exists(), path
    text = "\n".join(path.read_text() for path in paths if path.suffix == ".md")
    assert "KATO_RELLICH_CLOSURE_CONDITIONAL" in text
    assert "FULL_HT_THEOREM_PROVEN" not in text

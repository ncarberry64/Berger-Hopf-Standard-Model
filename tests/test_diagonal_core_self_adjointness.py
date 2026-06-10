import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from diagonal_reference_operator import (
    DIAGONAL_REFERENCE_OPERATOR_PROVEN,
    build_diagonal_reference_operator_report,
    diagonal_eigenvalue,
    export_diagonal_reference_operator_json,
    export_diagonal_reference_operator_markdown,
    sample_growth_values,
)
from essential_self_adjointness import (
    DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN,
    build_essential_self_adjointness_report,
    export_essential_self_adjointness_json,
    export_essential_self_adjointness_markdown,
)
from finite_core_domain import (
    FINITE_CORE_DENSE,
    build_finite_core_domain_report,
    export_finite_core_domain_json,
    export_finite_core_domain_markdown,
)
from graph_norm_domain import (
    GRAPH_NORM_DOMAIN_PROVEN,
    build_graph_norm_domain_report,
    export_graph_norm_domain_json,
    export_graph_norm_domain_markdown,
)
from ht_domain_bridge import HT_THEOREM_BLOCKED_BY_PERTURBATION, build_ht_domain_bridge_report
from kato_rellich_preconditions import (
    KATO_RELLICH_PRECONDITIONS_CONDITIONAL,
    build_kato_rellich_precondition_report,
    export_kato_rellich_preconditions_json,
    export_kato_rellich_preconditions_markdown,
)


def test_finite_core_is_dense_and_uses_formal_kernel():
    report = build_finite_core_domain_report()

    assert report.status == FINITE_CORE_DENSE
    assert report.dense_in_l2 is True
    assert report.dense_in_graph_norm_for_diagonal_operator is True
    assert report.coordinate_first_kernel_used is False
    assert report.formal_kernel == (
        "|ell,0,0,q=0,chi=-1>",
        "|u,0,0,q=0,chi=-1>",
        "|d,0,0,q=0,chi=-1>",
    )


def test_diagonal_reference_operator_is_real_symmetric_and_grows():
    report = build_diagonal_reference_operator_report()

    assert report.status == DIAGONAL_REFERENCE_OPERATOR_PROVEN
    assert report.symmetric_on_finite_core is True
    assert report.eigenvalue_law.real_valued is True
    assert report.eigenvalue_law.tends_to_infinity is True
    assert diagonal_eigenvalue(0, 0) == 0.0
    assert diagonal_eigenvalue(4, 2) > 0.0
    values = sample_growth_values()
    assert values[0] == 0.0
    assert values[-1] > values[1]


def test_essential_self_adjointness_route_passes_for_diagonal_operator():
    report = build_essential_self_adjointness_report()

    assert report.status == DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN
    assert report.theorem_complete is True
    assert report.deficiency_indices == (0, 0)
    assert all(route.passes for route in report.proof_routes)
    assert "diagonal reference operator" in " ".join(report.limitations)


def test_graph_norm_domain_is_proven_for_reference_operator():
    report = build_graph_norm_domain_report()

    assert report.status == GRAPH_NORM_DOMAIN_PROVEN
    assert report.finite_core_dense_in_graph_norm is True
    assert report.reference_domain_for_relative_bound_bridge is True
    assert report.perturbation_compatibility_status == "PERTURBATION_COMPATIBILITY_OPEN"


def test_kato_rellich_preconditions_remain_conditional():
    report = build_kato_rellich_precondition_report()

    assert report.status == KATO_RELLICH_PRECONDITIONS_CONDITIONAL
    assert report.theorem_complete is False
    assert report.relative_bound_below_one is True
    rows = {row.id: row for row in report.preconditions}
    assert rows["reference_self_adjointness"].passes is True
    assert rows["graph_domain"].passes is True
    assert rows["domain_inclusion"].passes is False


def test_ht_bridge_records_reference_operator_closed_not_full_proof():
    report = build_ht_domain_bridge_report()

    assert report.domain_bridge_status == HT_THEOREM_BLOCKED_BY_PERTURBATION
    assert report.diagonal_reference_status == DIAGONAL_REFERENCE_OPERATOR_PROVEN
    assert report.graph_norm_domain_status == GRAPH_NORM_DOMAIN_PROVEN
    assert report.kato_rellich_precondition_status == KATO_RELLICH_PRECONDITIONS_CONDITIONAL
    assert report.theorem_complete is False


def test_v19_exports_generate(tmp_path):
    outputs = {
        "core_md": tmp_path / "core.md",
        "core_json": tmp_path / "core.json",
        "diag_md": tmp_path / "diag.md",
        "diag_json": tmp_path / "diag.json",
        "esa_md": tmp_path / "esa.md",
        "esa_json": tmp_path / "esa.json",
        "graph_md": tmp_path / "graph.md",
        "graph_json": tmp_path / "graph.json",
        "kato_md": tmp_path / "kato.md",
        "kato_json": tmp_path / "kato.json",
    }
    export_finite_core_domain_markdown(outputs["core_md"])
    export_finite_core_domain_json(outputs["core_json"])
    export_diagonal_reference_operator_markdown(outputs["diag_md"])
    export_diagonal_reference_operator_json(outputs["diag_json"])
    export_essential_self_adjointness_markdown(outputs["esa_md"])
    export_essential_self_adjointness_json(outputs["esa_json"])
    export_graph_norm_domain_markdown(outputs["graph_md"])
    export_graph_norm_domain_json(outputs["graph_json"])
    export_kato_rellich_preconditions_markdown(outputs["kato_md"])
    export_kato_rellich_preconditions_json(outputs["kato_json"])

    assert json.loads(outputs["core_json"].read_text())["status"] == FINITE_CORE_DENSE
    assert json.loads(outputs["diag_json"].read_text())["status"] == DIAGONAL_REFERENCE_OPERATOR_PROVEN
    assert json.loads(outputs["esa_json"].read_text())["status"] == DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN
    assert json.loads(outputs["graph_json"].read_text())["status"] == GRAPH_NORM_DOMAIN_PROVEN
    assert json.loads(outputs["kato_json"].read_text())["status"] == KATO_RELLICH_PRECONDITIONS_CONDITIONAL


def test_v19_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "diagonal_reference_operator.py",
            "finite_core_domain.py",
            "essential_self_adjointness.py",
            "graph_norm_domain.py",
            "kato_rellich_preconditions.py",
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


def test_v19_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_essential_self_adjointness_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]


def test_generated_v19_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "diagonal_reference_operator_report.md",
        root / "theory" / "finite_core_domain_report.md",
        root / "theory" / "essential_self_adjointness_report.md",
        root / "theory" / "graph_norm_domain_report.md",
        root / "theory" / "kato_rellich_preconditions_report.md",
        root / "manuscript" / "BHSM_v1_9_diagonal_core_self_adjointness_note.md",
        root / "notebooks" / "49_diagonal_core_self_adjointness.ipynb",
    )
    for path in paths:
        assert path.exists(), path
    text = "\n".join(path.read_text() for path in paths if path.suffix == ".md")
    assert "DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN" in text
    assert "This is not `FULL_HT_THEOREM_PROVEN`" in text

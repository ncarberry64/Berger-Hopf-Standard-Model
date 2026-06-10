import json

from full_operator_domain import (
    FORMAL_KERNEL_STATES,
    build_full_operator_domain_report,
    export_full_operator_domain_json,
    export_full_operator_domain_markdown,
)
from self_adjoint_domain import SELF_ADJOINT_DOMAIN_OPEN


def test_full_operator_domain_defines_formal_kernel_and_complement():
    report = build_full_operator_domain_report()

    assert report.formal_kernel == FORMAL_KERNEL_STATES
    assert len(report.formal_kernel) == 3
    assert "ell" in report.formal_kernel[0]
    assert "u" in report.formal_kernel[1]
    assert "d" in report.formal_kernel[2]
    assert report.complement == "H_perp = K_formal^perp"


def test_full_operator_terms_are_inventory_complete():
    report = build_full_operator_domain_report()
    term_ids = {term.id for term in report.terms}

    assert term_ids == {
        "D_diag_squared",
        "V_Hopf",
        "V_boundary",
        "V_chi",
        "K_sector",
        "P_perp_lift",
    }
    assert "D_FK^2" in report.operator_expression


def test_self_adjoint_domain_remains_open_not_overclaimed():
    report = build_full_operator_domain_report()

    assert report.status == SELF_ADJOINT_DOMAIN_OPEN
    assert report.theorem_complete is False
    assert report.self_adjoint_report.finite_matrix_hermitian is True
    assert any("self-adjoint" in item for item in report.open_obligations)
    assert any("Do not promote finite-matrix" in item for item in report.forbidden_claims)


def test_full_operator_domain_exports(tmp_path):
    md = tmp_path / "domain.md"
    js = tmp_path / "domain.json"

    export_full_operator_domain_markdown(md)
    export_full_operator_domain_json(js)

    data = json.loads(js.read_text())
    assert data["status"] == SELF_ADJOINT_DOMAIN_OPEN
    assert data["theorem_complete"] is False
    assert "Full Operator" in md.read_text()

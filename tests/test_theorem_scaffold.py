import json

from claims import ClaimStatus, claims_by_status, build_claims_ledger
from theorem_scaffold import (
    AssumptionStatus,
    build_ht_no_extra_light_theorem_scaffold,
    export_theorem_scaffold_json,
    export_theorem_scaffold_markdown,
    validate_theorem_scaffold,
)


def test_all_assumptions_a1_to_a7_are_present():
    scaffold = build_ht_no_extra_light_theorem_scaffold()

    assert {assumption.id for assumption in scaffold.assumptions} == {
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
    }
    assert validate_theorem_scaffold(scaffold) is True


def test_theorem_complete_is_false():
    scaffold = build_ht_no_extra_light_theorem_scaffold()

    assert scaffold.theorem_complete is False


def test_proxy_assumptions_are_not_marked_proven():
    scaffold = build_ht_no_extra_light_theorem_scaffold()

    for assumption in scaffold.assumptions:
        evidence = " ".join(assumption.evidence).lower()
        if "proxy" in evidence:
            assert assumption.status != AssumptionStatus.PROVEN_CONDITIONAL


def test_scaffold_contains_required_steps_and_conclusion():
    scaffold = build_ht_no_extra_light_theorem_scaffold()

    assert {step.id for step in scaffold.steps} == {"S1", "S2", "S3", "S4", "S5"}
    assert "If A1-A7 are proven" in scaffold.conclusion
    assert scaffold.theorem_complete is False


def test_exports_to_markdown_and_json_with_required_equations(tmp_path):
    md_path = tmp_path / "theorem.md"
    json_path = tmp_path / "theorem.json"

    export_theorem_scaffold_markdown(md_path)
    export_theorem_scaffold_json(json_path)

    markdown = md_path.read_text()
    data = json.loads(json_path.read_text())
    assert "d + mu_H(1 - exp(-d/Lambda^2)) + V_min >= mu_H" in markdown
    assert "H_T|H_perp >= mu_H" in markdown
    assert data["theorem_complete"] is False
    assert len(data["assumptions"]) == 7


def test_ht_claim_remains_proxy_audit_after_scaffold():
    claim = next(claim for claim in build_claims_ledger() if claim.id == "ht_proxy_spectral_gap")

    assert claim.status == ClaimStatus.PROXY_AUDIT


def test_forbidden_claims_remain_forbidden_after_scaffold():
    forbidden = claims_by_status(ClaimStatus.FORBIDDEN)

    assert len(forbidden) == 5
    assert all(claim.status == ClaimStatus.FORBIDDEN for claim in forbidden)

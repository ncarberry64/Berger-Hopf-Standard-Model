import json

from claims import (
    ClaimStatus,
    build_claims_ledger,
    claims_by_status,
    export_claims_json,
    export_claims_markdown,
)


def test_all_claims_have_nonempty_limitations():
    claims = build_claims_ledger()

    assert claims
    assert all(claim.limitations for claim in claims)
    assert all(all(item.strip() for item in claim.limitations) for claim in claims)


def test_forbidden_claims_remain_forbidden():
    forbidden = claims_by_status(ClaimStatus.FORBIDDEN)

    assert forbidden
    assert all(claim.status == ClaimStatus.FORBIDDEN for claim in forbidden)
    assert {claim.id for claim in forbidden} == {
        "forbidden_pure_geometry_derivation",
        "forbidden_confinement_proof",
        "forbidden_completed_no_extra_light_theorem",
        "forbidden_neutrino_minimal_sm",
        "forbidden_numerical_predictions",
    }


def test_no_verified_claim_has_unresolved_open_dependencies():
    open_ids = {claim.id for claim in claims_by_status(ClaimStatus.OPEN)}
    verified = claims_by_status(ClaimStatus.VERIFIED_TEST)

    assert verified
    for claim in verified:
        assert not (set(claim.dependencies) & open_ids)


def test_no_proxy_result_is_marked_completed_theorem():
    proxy_claims = claims_by_status(ClaimStatus.PROXY_AUDIT)

    assert proxy_claims
    assert all("theorem remains conditional" in " ".join(claim.limitations).lower() or "proxy" in " ".join(claim.limitations).lower() for claim in proxy_claims)
    assert all(claim.status == ClaimStatus.PROXY_AUDIT for claim in proxy_claims)


def test_exports_to_markdown_and_json(tmp_path):
    md_path = tmp_path / "claims.md"
    json_path = tmp_path / "claims.json"

    export_claims_markdown(md_path)
    export_claims_json(json_path)

    markdown = md_path.read_text()
    data = json.loads(json_path.read_text())
    assert "# Claims Ledger" in markdown
    assert "| ID | Title | Status | Tests | Limitations |" in markdown
    assert data
    assert all("id" in item and "status" in item for item in data)


def test_claim_counts_by_status_are_nonzero_for_control_categories():
    assert len(claims_by_status(ClaimStatus.VERIFIED_TEST)) >= 1
    assert len(claims_by_status(ClaimStatus.PROXY_AUDIT)) >= 1
    assert len(claims_by_status(ClaimStatus.OPEN)) >= 1
    assert len(claims_by_status(ClaimStatus.FORBIDDEN)) >= 1

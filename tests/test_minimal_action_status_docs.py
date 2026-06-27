from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_status_and_docs_use_the_author_ontology_classifications() -> None:
    status = read("STATUS.md")
    assert "ARTIFACT_BACKED" in status
    assert "RETIRED_TARGET" in status
    assert "CONDITIONAL_ACTION_THEOREM" in status
    assert "CONDITIONAL_PROPAGATION_THEOREM" in status
    assert "Numerical `X_ch` response normalization" not in status
    assert "Numerical normalization" in status
    assert "Numerical curvature response" in status

    for path in (
        "docs/minimal_action_closure.md",
        "docs/cp_o_int_minimal_action_closure.md",
        "docs/x_ch_minimal_action_closure.md",
        "docs/neutrino_basis_scale_minimal_action_closure.md",
        "docs/author_ontology_v0_8.md",
    ):
        assert (ROOT / path).is_file()


def test_claims_and_runtime_boundaries_remain_visible() -> None:
    claims = read("CLAIMS.md")
    assert "## Not Supported" in claims
    assert "validated FeynRules/UFO/MadGraph readiness" in claims
    assert "minimal-action audit" in claims
    assert "static rest-mass" in claims

    combined = "\n".join(read(path) for path in (
        "docs/minimal_action_closure.md",
        "docs/cp_o_int_minimal_action_closure.md",
        "docs/x_ch_minimal_action_closure.md",
        "docs/neutrino_basis_scale_minimal_action_closure.md",
    )).lower()
    assert "bhsm is empirically validated" not in combined
    assert "official cern integration" not in combined
    assert "production-ready" not in combined

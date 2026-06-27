from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_status_and_docs_name_each_first_missing_object() -> None:
    status = read("STATUS.md")
    assert "OPEN_MISSING_ACTION_SOURCE" in status
    assert "OPEN_MISSING_FIELD_REPRESENTATION" in status
    assert "OPEN_MISSING_PHYSICAL_BASIS" in status
    assert "Action-derived `X_ch` field representation" in status
    assert "Map from neutral boundary channels to physical neutrino states" in status

    for path in (
        "docs/minimal_action_closure.md",
        "docs/cp_o_int_minimal_action_closure.md",
        "docs/x_ch_minimal_action_closure.md",
        "docs/neutrino_basis_scale_minimal_action_closure.md",
    ):
        assert (ROOT / path).is_file()


def test_claims_and_runtime_boundaries_remain_visible() -> None:
    claims = read("CLAIMS.md")
    assert "## Not Supported" in claims
    assert "validated FeynRules/UFO/MadGraph readiness" in claims
    assert "minimal-action audit" in claims

    combined = "\n".join(read(path) for path in (
        "docs/minimal_action_closure.md",
        "docs/cp_o_int_minimal_action_closure.md",
        "docs/x_ch_minimal_action_closure.md",
        "docs/neutrino_basis_scale_minimal_action_closure.md",
    )).lower()
    assert "bhsm is empirically validated" not in combined
    assert "official cern integration" not in combined
    assert "production-ready" not in combined

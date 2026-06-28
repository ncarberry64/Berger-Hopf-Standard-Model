from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_docs_keep_completion_and_unit_map_open() -> None:
    text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ("README.md", "STATUS.md", "docs/common_16_closure_report.md")
    )
    assert "OPEN_MISSING_CKM_EXPONENT_DERIVATION" in text
    assert "physical eV/GeV neutrino mass" in text
    assert "empirically validated" not in (ROOT / "docs/common_16_closure_report.md").read_text(encoding="utf-8")

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUSEUM = ROOT / "museum"


def test_museum_has_eight_functional_motion_exhibits_and_static_fallbacks() -> None:
    exhibits = (MUSEUM / "app" / "exhibits.ts").read_text(encoding="utf-8")
    assert exhibits.count("_animated.gif'") == 8
    assert exhibits.count("still: 'bhsm_") == 8
    for phrase in (
        "S², S³, and S⁴",
        "inverse-free LSZ",
        "admissible bands",
        "F₂(0)",
        "Two incoming particles",
        "Allowed decay branches",
        "no-fit firewall",
        "family or mode",
        "local enclosure",
    ):
        assert phrase in exhibits


def test_museum_separates_claim_classes_and_creator_record() -> None:
    page = (MUSEUM / "app" / "page.tsx").read_text(encoding="utf-8")
    page = " ".join(page.split())
    for phrase in (
        "Implemented machinery",
        "Numerically demonstrated",
        "Physical prediction",
        "physical enclosure bridge remains open",
        "FULL_BHSM_COMPLETE = FALSE",
        "Norman P. Carberry",
        "0009-0000-6650-3485",
        "No CERN, Fermilab, or institutional endorsement is implied",
    ):
        assert phrase in page


def test_museum_assets_are_local_and_provenance_documented() -> None:
    provenance = (MUSEUM / "ASSET_PROVENANCE.md").read_text(encoding="utf-8")
    assert "Bubo Research Node" in provenance
    assert "MIT License" in provenance
    assert "No stock imagery" in provenance
    assert (MUSEUM / "public" / "bhsm-symbol.svg").is_file()

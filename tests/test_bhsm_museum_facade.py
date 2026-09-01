from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUSEUM = ROOT / "museum"


def test_museum_has_nine_functional_motion_exhibits_and_static_fallbacks() -> None:
    exhibits = (MUSEUM / "app" / "exhibits.ts").read_text(encoding="utf-8")
    assert exhibits.count("animated: '") == 9
    assert exhibits.count("still: '") == 9
    assert "pr98_cms_engine_validation_continuous.gif" in exhibits
    assert "CMS Open Data Record 303" in exhibits
    for phrase in (
        "100,000 dimuon events",
        "3.225×",
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
        "CMS detector photograph: Simon Waldherr",
        "17,630",
    ):
        assert phrase in page
    assert "guided tour" not in page.lower()
    assert "No invented biography" not in page


def test_museum_assets_are_local_and_provenance_documented() -> None:
    provenance = (MUSEUM / "ASSET_PROVENANCE.md").read_text(encoding="utf-8")
    assert "Bubo Research Node" in provenance
    assert "MIT License" in provenance
    assert "Simon Waldherr" in provenance
    assert "CC BY-SA 4.0" in provenance
    assert (MUSEUM / "public" / "bhsm-symbol.svg").is_file()
    assert (MUSEUM / "public" / "cms-detector-simon-waldherr.jpg").is_file()

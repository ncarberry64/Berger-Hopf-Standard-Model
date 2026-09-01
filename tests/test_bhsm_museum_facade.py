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
        "Simulated particle spectrum",
        "uncertainty envelopes",
        "F₂(q²)",
        "Two incoming states",
        "Allowed branches",
        "no-fit firewall",
        "family or mode",
        "local enclosure",
        "Real CMS Open Data · BHSM Engine",
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
        "17,630",
        "Frozen preprint PDF",
        "Inspect 64 dimuon events",
        "Scientific caption",
        "eventIndices[selected]",
    ):
        assert phrase in page
    assert "guided tour" not in page.lower()
    assert "semantics" not in page.lower()
    assert "Norman P. Carberry · Research archive" not in page
    assert "Norman P. Carberry · Berger–Hopf Standard Model" not in page
    assert "No invented biography" not in page


def test_museum_assets_are_local_and_provenance_documented() -> None:
    provenance = (MUSEUM / "ASSET_PROVENANCE.md").read_text(encoding="utf-8")
    assert "Bubo Research Node" in provenance
    assert "MIT License" in provenance
    assert "SIMULATED" not in provenance
    assert "simulated museum data" in provenance
    assert (MUSEUM / "public" / "bhsm-symbol.svg").is_file()
    assert (MUSEUM / "public" / "data" / "cms-four-vector-sample.json").is_file()

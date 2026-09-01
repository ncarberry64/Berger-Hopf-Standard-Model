from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUSEUM = ROOT / "museum"


def test_museum_has_seven_functional_motion_exhibits_and_static_fallbacks() -> None:
    exhibits = (MUSEUM / "app" / "exhibits.ts").read_text(encoding="utf-8")
    assert exhibits.count("_animated.gif'") == 7
    assert exhibits.count("still: 'bhsm_") == 7
    for phrase in (
        "S², S³, and S⁴",
        "inverse-free LSZ",
        "admissible bands",
        "F₂(0)",
        "Two incoming particles",
        "Allowed decay branches",
        "no-fit firewall",
    ):
        assert phrase in exhibits


def test_museum_separates_claim_classes_and_creator_record() -> None:
    page = (MUSEUM / "app" / "page.tsx").read_text(encoding="utf-8")
    page = " ".join(page.split())
    for phrase in (
        "Implemented machinery",
        "Numerically demonstrated",
        "Physical prediction",
        "Gate 7 remains OPEN",
        "FULL_BHSM_COMPLETE = FALSE",
        "PHYSICAL_ENCAPSULATION_IDENTIFIED = FALSE",
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


def test_cms_gallery_is_distinct_qualified_and_provenanced() -> None:
    exhibits = (MUSEUM / "app" / "exhibits.ts").read_text(encoding="utf-8")
    page = (MUSEUM / "app" / "page.tsx").read_text(encoding="utf-8")
    combined = " ".join((exhibits + page).split())
    for phrase in (
        "Coordinate-engine validation—not a BHSM physics test",
        "No detector reconstruction",
        "no BHSM empirical validation",
        "no CERN/CMS endorsement",
        "https://opendata.cern.ch/record/303",
        "pr98_cms_sample_manifest.json",
        "artifacts/cern_open_data_benchmark/results.json",
        "tests/test_cern_open_data_benchmark.py",
        "100,000 events",
        "200,000 unique muon",
    ):
        assert phrase.casefold() in combined.casefold()

    sync = (MUSEUM / "scripts" / "sync-assets.mjs").read_text(encoding="utf-8")
    assert "pr98_cms_engine_validation_continuous.gif" in sync
    assert "pr98_cms_engine_validation.svg" in sync


def test_museum_has_keyboard_and_reduced_motion_contracts() -> None:
    page = (MUSEUM / "app" / "page.tsx").read_text(encoding="utf-8")
    css = (MUSEUM / "app" / "globals.css").read_text(encoding="utf-8")
    assert 'className="skip-link"' in page
    assert "prefers-reduced-motion: reduce" in page
    assert "aria-pressed={!motion}" in page
    assert "animated={cmsValidation.animated}" in page
    assert "still={cmsValidation.still}" in page
    assert "onError={() => setFailedSource(desired)}" in page
    assert ":focus-visible" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "min-height: 44px" in css

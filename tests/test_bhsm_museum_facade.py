"""Public science order, data authority and retained local asset contracts."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUSEUM = ROOT / "museum"


def test_public_order_leads_with_potential_then_science_details_author_cosmology():
    page = (MUSEUM / "app/page.tsx").read_text(encoding="utf-8")
    positions = [page.index(token) for token in ('id="potential"', '<PrototypeScience motion={motion} setMotion={setMotion} />', '<ScienceGallery />', 'id="research-exhibit"', 'id="details"', 'id="creator"', 'id="other-work"', '<footer>')]
    assert positions == sorted(positions)
    assert "historic stakes" in page
    assert "If established and tested" in page
    assert "FULL_BHSM_COMPLETE = FALSE" in page
    assert page.count('id="research-exhibit"') == 1
    assert "Norman P. Carberry" in page
    assert "0009-0000-6650-3485" in page


def test_science_panels_show_values_and_qualifications_without_hidden_details():
    gallery = " ".join((MUSEUM / "app/science-gallery.tsx").read_text(encoding="utf-8").split())
    assert "In plain language" in gallery
    assert "Sandbox reference · unverified" in gallery
    assert "COMPARISON ONLY" in gallery
    assert "not independently verified experimental data" in gallery
    assert "not a statistical significance" in json.loads((ROOT / "data/museum/bhsm_sandbox_comparison_20260902.json").read_text(encoding="utf-8"))["difference_definition"]
    assert "<details" not in gallery
    assert "comparison-table" in gallery
    assert "<select" in gallery
    assert "θ23 tension" in gallery
    for group in ("families", "forces", "quarks", "neutrinos", "higgs"):
        assert f"id: '{group}'" in gallery


def test_sandbox_pairs_are_complete_source_bound_and_comparison_only():
    path = ROOT / "data/museum/bhsm_sandbox_comparison_20260902.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["classification"] == "COMPARISON_ONLY"
    assert data["physical_prediction"] is False
    assert data["reference_is_independently_verified_measurement"] is False
    source = ROOT / data["source"]["path"]
    assert hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == data["source"]["sha256"]
    assert len(data["rows"]) == 10
    assert len(data["qualitative_sentinels"]) == 4
    rows = {row["id"]: row for row in data["rows"]}
    assert rows["atmospheric-angle"]["bhsm"] == 0.543784
    assert rows["atmospheric-angle"]["reference"] == 0.470
    assert rows["higgs"]["bhsm"] == 123.085
    assert rows["higgs"]["reference"] == 125.20
    for row in data["rows"]:
        assert abs(100*(row["bhsm"]-row["reference"])/row["reference"]) < 20
    assert json.loads((MUSEUM / "public/data/sandbox-comparison.json").read_text(encoding="utf-8")) == data
    assert json.loads((MUSEUM / "app/sandbox-comparison.json").read_text(encoding="utf-8")) == data
    gallery = (MUSEUM / "app/science-gallery.tsx").read_text(encoding="utf-8")
    assert "from './sandbox-comparison.json'" in gallery
    assert "from '../public/" not in gallery


def test_comparison_snapshot_is_not_an_upstream_scientific_dependency():
    forbidden = ("bhsm_sandbox_comparison_20260902", "sandbox-comparison.json", "sandbox_comparison_source_2026-09-02")
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden), path


def test_research_and_cosmology_labels_and_motion_fallbacks_are_explicit():
    page = (MUSEUM / "app/page.tsx").read_text(encoding="utf-8")
    exhibits = (MUSEUM / "app/exhibits.ts").read_text(encoding="utf-8")
    assert "Real experimental data · CMS Open Data" in page
    assert "Simulated schematic · not observational data" in page
    assert "Independent preprint · not peer reviewed" in page
    assert "not a sky map" in page
    assert "cosmologyExhibit.lay" in page
    assert "prefers-reduced-motion" in page
    assert "onError={() => setFailedSource(desired)}" in page
    assert "ASSET_REVISION" in page
    assert "Simulated particle spectrum" not in exhibits
    assert "CMS Open Data Record 303" in exhibits
    assert "10.20944/preprints202601.1427.v1" in exhibits
    assert (MUSEUM / "public/bhsm-symbol.svg").is_file()
    assert (MUSEUM / "public/data/cms-four-vector-sample.json").is_file()
    assert "sandbox-comparison.json" in (MUSEUM / "scripts/sync-assets.mjs").read_text(encoding="utf-8")

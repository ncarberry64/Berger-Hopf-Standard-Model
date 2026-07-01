from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_leads_with_pr98_real_data_animation_and_retains_synthetic_demo():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    real_asset = "docs/assets/pr98_cms_open_data_animation/pr98_cms_engine_validation.gif"
    synthetic_asset = "docs/assets/bhsm_boundary_mapping_explainer.gif"
    assert real_asset in readme
    assert synthetic_asset in readme
    assert readme.index(real_asset) < readme.index(synthetic_asset)
    assert "CERN Open Data Record 303" in readme
    assert "10.7483/OPENDATA.CMS.4M97.3SQ9" in readme
    assert "Engine coordinate-transformation validation only" in readme
    assert len(readme.splitlines()) < 180

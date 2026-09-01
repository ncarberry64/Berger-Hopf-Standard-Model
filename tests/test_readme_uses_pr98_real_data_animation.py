from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_keeps_pr98_claim_boundary_without_embedding_animations():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    real_asset = "docs/assets/pr98_cms_open_data_animation/pr98_cms_engine_validation_continuous.gif"
    synthetic_asset = "docs/assets/bhsm_boundary_mapping_explainer.gif"
    assert real_asset not in readme
    assert synthetic_asset not in readme
    assert "https://ncarberry64.github.io/Berger-Hopf-Standard-Model/" in readme
    assert not any(
        line.startswith("![") and ".gif)" in line
        for line in readme.splitlines()
    )
    assert "CERN Open Data Record 303" in readme
    assert "10.7483/OPENDATA.CMS.4M97.3SQ9" in readme
    assert "Engine coordinate-transformation validation only" in readme

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
NAMES = (
    "bhsm_geometry_to_prediction",
    "bhsm_universal_predictive_engine",
    "bhsm_spectral_forecast",
    "bhsm_muon_g2_pipeline",
    "bhsm_collision_predictor",
    "bhsm_decay_stability_engine",
    "bhsm_no_fit_firewall",
)


def test_visual_manifest_preserves_claim_boundaries() -> None:
    payload = json.loads((ASSETS / "bhsm_readme_visual_status.json").read_text(encoding="utf-8"))
    assert payload["promotion"]["gate7_closed"] is False
    assert payload["capabilities"]["complete_physical_predictions"] is False
    assert payload["spectral_visualization"]["physical_mass_scale_available"] is False
    assert payload["spectral_visualization"]["particle_assignments_available"] is False


def test_visual_suite_and_readme_references_exist() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in NAMES:
        for suffix in (".svg", ".png", "_animated.gif"):
            assert (ASSETS / f"{name}{suffix}").is_file()
        assert f"docs/assets/{name}_animated.gif" in readme


def test_svg_has_no_external_dependencies() -> None:
    for name in NAMES:
        svg = (ASSETS / f"{name}.svg").read_text(encoding="utf-8")
        assert "http://" not in svg.replace("http://www.w3.org/2000/svg", "")
        assert "https://" not in svg
        assert "<animateMotion" in svg

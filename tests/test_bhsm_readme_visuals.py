import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
NAMES = (
    "bhsm_geometry_to_prediction",
    "bhsm_simulated_particle_spectrum",
    "bhsm_spectral_forecast",
    "bhsm_muon_g2_pipeline",
    "bhsm_collision_predictor",
    "bhsm_decay_stability_engine",
    "bhsm_no_fit_firewall",
    "bhsm_physical_identification_bridge",
)


def test_visual_manifest_preserves_claim_boundaries() -> None:
    payload = json.loads((ASSETS / "bhsm_readme_visual_status.json").read_text(encoding="utf-8"))
    assert payload["promotion"]["gate7_closed"] is False
    assert payload["capabilities"]["complete_physical_predictions"] is False
    assert payload["spectral_visualization"]["physical_mass_scale_available"] is False
    assert payload["spectral_visualization"]["particle_assignments_available"] is True
    assert payload["spectral_visualization"]["new_particle_assignments_derived_here"] is False
    assert payload["identification_bridge"]["frozen_particle_registry_reused"] is True
    assert payload["identification_bridge"]["local_enclosure_proved"] is False
    assert payload["identification_bridge"]["carrier_kill_screen_complete"] is True
    assert payload["identification_bridge"]["carrier_candidates_audited"] == 6
    assert payload["identification_bridge"]["qualifying_carriers"] == 0
    assert len(payload["identification_bridge"]["four_kernel_reduction"]) == 4
    assert payload["simulated_particle_spectrum"]["installed_for_museum"] is True
    assert payload["simulated_particle_spectrum"]["physical_mass_scale"] is False
    assert payload["simulated_particle_spectrum"]["new_particle_prediction"] is False
    assert payload["visual_mode"] == "DETERMINISTIC_EXPLANATORY_SIMULATION_ENGINES"
    assert "no measured output" in payload["visual_scope"]


def test_visual_suite_is_presented_outside_the_scientific_readme() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    museum = (ROOT / "museum" / "app" / "exhibits.ts").read_text(encoding="utf-8")
    for name in NAMES:
        for suffix in (".svg", ".png", "_animated.gif"):
            assert (ASSETS / f"{name}{suffix}").is_file()
        assert f"{name}_animated.gif" in museum
        assert f"docs/assets/{name}_animated.gif" not in readme
    assert "https://ncarberry64.github.io/Berger-Hopf-Standard-Model/" in readme
    assert "animations live outside it" in readme


def test_svg_has_no_external_dependencies() -> None:
    for name in NAMES:
        svg = (ASSETS / f"{name}.svg").read_text(encoding="utf-8")
        assert "http://" not in svg.replace("http://www.w3.org/2000/svg", "")
        assert "https://" not in svg
        assert "<animateMotion" in svg or "<animate " in svg

        if name not in {
            "bhsm_simulated_particle_spectrum",
            "bhsm_physical_identification_bridge",
        }:
            assert 'data-visual-kind="simulation-engine"' in svg


def test_simulated_spectrum_is_machine_readable_and_claim_safe() -> None:
    path = ROOT / "data" / "museum" / "bhsm_simulated_particle_spectrum_v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["display_status"] == "SIMULATED_MUSEUM_DATASET"
    assert "not BHSM mass predictions" in payload["claim_boundary"]
    assert len(payload["modes"]) == 9
    assert {mode["family"] for mode in payload["modes"]} == {"lepton", "gauge", "quark"}
